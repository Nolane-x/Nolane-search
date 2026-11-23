"""Everyday calculators for Nolane Wave 39.

These processors are deterministic, offline and intentionally accept a small JSON
request document. They do not call payment, banking, mapping or external services.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import re
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP, localcontext
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MAX_JSON_BYTES = 1 * 1024 * 1024
MAX_ITEMS = 200
ZERO = Decimal("0")
ONE = Decimal("1")


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contains a duplicate object key.")
        result[key] = value
    return result


def _load_request(path: Path) -> dict:
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            raise RuntimeError("Calculator request exceeds the 1 MiB input limit.")
        raw = path.read_text(encoding="utf-8-sig")
        value = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        if isinstance(exc, RuntimeError):
            raise
        raise RuntimeError("Upload a valid UTF-8 JSON calculator request.") from exc
    if not isinstance(value, dict):
        raise RuntimeError("Calculator request must be one JSON object.")
    return value


def _decimal(value, label: str, minimum=None, maximum=None) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise RuntimeError(f"{label} must be a number.")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        raise RuntimeError(f"{label} must be a number.") from None
    if not result.is_finite():
        raise RuntimeError(f"{label} must be finite.")
    if minimum is not None and result < Decimal(str(minimum)):
        raise RuntimeError(f"{label} must be at least {minimum}.")
    if maximum is not None and result > Decimal(str(maximum)):
        raise RuntimeError(f"{label} must not exceed {maximum}.")
    return result


def _integer(value, label: str, minimum: int, maximum: int) -> int:
    number = _decimal(value, label, minimum, maximum)
    if number != number.to_integral_value():
        raise RuntimeError(f"{label} must be a whole number.")
    return int(number)


def _currency(value) -> str:
    code = str(value or "USD").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", code):
        raise RuntimeError("currency must be a three-letter currency code such as VND, USD or EUR.")
    return code


def _minor_units(currency: str) -> int:
    if currency in {"BIF", "CLP", "DJF", "GNF", "ISK", "JPY", "KMF", "KRW", "PYG", "RWF", "UGX", "UYI", "VND", "VUV", "XAF", "XOF", "XPF"}:
        return 0
    if currency in {"BHD", "IQD", "JOD", "KWD", "LYD", "OMR", "TND"}:
        return 3
    return 2


def _money(value: Decimal, currency: str) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-_minor_units(currency)), rounding=ROUND_HALF_UP)


def _fmt(value: Decimal, places: int | None = None) -> str:
    if places is not None:
        value = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def _write(path: Path, suffix: str, body: str, summary: str | None = None) -> dict:
    output = path.with_name((path.stem[:64] or "nolane") + "-" + suffix + ".txt")
    output.write_text(body.rstrip() + "\n", encoding="utf-8")
    return {
        "summary": summary or body.splitlines()[0][:500],
        "output_path": str(output),
    }


def bill_split_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    subtotal = _money(_decimal(data.get("bill_amount"), "bill_amount", "0.01", "1000000000000000"), currency)
    tip_percent = _decimal(data.get("tip_percent", 0), "tip_percent", 0, 100)
    tax_percent = _decimal(data.get("tax_percent", 0), "tax_percent", 0, 100)
    people = _integer(data.get("people"), "people", 1, 1000)
    tip = _money(subtotal * tip_percent / Decimal(100), currency)
    tax = _money(subtotal * tax_percent / Decimal(100), currency)
    total = _money(subtotal + tip + tax, currency)
    equal_share = _money(total / people, currency)
    final_share = total - equal_share * (people - 1)
    lines = [
        "Bill split calculator",
        f"Currency: {currency}",
        f"Subtotal: { _fmt(subtotal, places) }",
        f"Tax ({_fmt(tax_percent)}% of subtotal): {_fmt(tax, places)}",
        f"Tip ({_fmt(tip_percent)}% of subtotal): {_fmt(tip, places)}",
        f"Total bill: {_fmt(total, places)}",
        f"People: {people}",
        f"Per person (first {people - 1}): {_fmt(equal_share, places)}",
        f"Final person's adjusted share: {_fmt(final_share, places)}",
        "Rounding note: the final share absorbs any currency-rounding remainder so all shares add up exactly to the total.",
    ]
    return _write(path, "bill-split", "\n".join(lines),
                  f"Total {currency} {_fmt(total, places)}; {people} people; about {currency} {_fmt(equal_share, places)} each.")


def loan_payment_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    principal = _money(_decimal(data.get("principal"), "principal", "0.01", "1000000000000000"), currency)
    annual_percent = _decimal(data.get("annual_rate_percent"), "annual_rate_percent", 0, 500)
    months = _integer(data.get("term_months"), "term_months", 1, 600)
    extra = _money(_decimal(data.get("extra_monthly_payment", 0), "extra_monthly_payment", 0, "1000000000000000"), currency)
    with localcontext() as ctx:
        ctx.prec = 32
        monthly_rate = annual_percent / Decimal(1200)
        if monthly_rate == 0:
            scheduled = principal / months
        else:
            scheduled = principal * monthly_rate / (ONE - (ONE + monthly_rate) ** (-months))
        scheduled = _money(scheduled, currency)
        balance = principal
        interest_total = ZERO
        rows = []
        month = 0
        while balance > ZERO and month < months:
            month += 1
            opening = balance
            interest = _money(opening * monthly_rate, currency)
            due = _money(scheduled + extra, currency)
            if due <= interest and opening > ZERO:
                raise RuntimeError("Monthly payment does not reduce the balance; increase the payment or shorten the term.")
            actual = min(due, _money(opening + interest, currency))
            principal_paid = _money(actual - interest, currency)
            if principal_paid > opening:
                principal_paid = opening
                actual = _money(principal_paid + interest, currency)
            balance = _money(opening - principal_paid, currency)
            interest_total += interest
            rows.append((month, opening, actual, interest, principal_paid, balance))
        if balance > ZERO:
            raise RuntimeError("Loan schedule did not reach zero within the requested term.")
        total_paid = _money(sum((row[2] for row in rows), ZERO), currency)
    output = path.with_name((path.stem[:64] or "nolane") + "-amortization.csv")
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["month", "opening_balance", "payment", "interest", "principal_paid", "closing_balance", "currency"])
        for month, opening, payment, interest, paid, closing in rows:
            writer.writerow([month, _fmt(opening, places), _fmt(payment, places), _fmt(interest, places),
                             _fmt(paid, places), _fmt(closing, places), currency])
    summary = (
        f"Loan payment: {currency} {_fmt(scheduled, places)} per month before extras; "
        f"{month} months to repay; total interest {currency} {_fmt(interest_total, places)}."
    )
    return {"summary": summary, "output_path": str(output)}


def date_calculator(path: Path) -> dict:
    data = _load_request(path)
    try:
        start = dt.date.fromisoformat(str(data.get("start_date", "")))
    except ValueError:
        raise RuntimeError("start_date must use YYYY-MM-DD.") from None
    if data.get("end_date") is None:
        offset = _integer(data.get("offset_days"), "offset_days", -365000, 365000)
        target = start + dt.timedelta(days=offset)
        lines = [
            "Date calculator",
            f"Start date: {start.isoformat()} ({start.strftime('%A')})",
            f"Offset: {offset:+,} days",
            f"Result: {target.isoformat()} ({target.strftime('%A')})",
        ]
        summary = f"{offset:+,} days from {start.isoformat()} is {target.isoformat()}."
    else:
        try:
            end = dt.date.fromisoformat(str(data.get("end_date")))
        except ValueError:
            raise RuntimeError("end_date must use YYYY-MM-DD.") from None
        include_end = data.get("include_end_date", True)
        if not isinstance(include_end, bool):
            raise RuntimeError("include_end_date must be true or false.")
        signed_days = (end - start).days
        first, last = sorted((start, end))
        inclusive_days = (last - first).days + (1 if include_end else 0)
        business_days = 0
        cursor = first
        while cursor <= last:
            if cursor.weekday() < 5 and (include_end or cursor != last):
                business_days += 1
            cursor += dt.timedelta(days=1)
        lines = [
            "Date calculator",
            f"Start: {start.isoformat()} ({start.strftime('%A')})",
            f"End: {end.isoformat()} ({end.strftime('%A')})",
            f"Elapsed days (end minus start): {signed_days:,}",
            f"Calendar days in range ({'including' if include_end else 'excluding'} end date): {inclusive_days:,}",
            f"Weeks and remaining days: {abs(signed_days) // 7} weeks, {abs(signed_days) % 7} days",
            f"Weekdays in range: {business_days:,}",
        ]
        summary = f"{abs(signed_days):,} elapsed days; {business_days:,} weekdays between {start.isoformat()} and {end.isoformat()}."
    return _write(path, "date-calculation", "\n".join(lines), summary)


def _valid_local_times(naive: dt.datetime, zone: ZoneInfo) -> list[dt.datetime]:
    candidates = []
    seen = set()
    for fold in (0, 1):
        aware = naive.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(dt.timezone.utc)
        round_trip = utc.astimezone(zone)
        if round_trip.replace(tzinfo=None) == naive and utc not in seen:
            candidates.append(aware)
            seen.add(utc)
    return candidates


def timezone_converter(path: Path) -> dict:
    data = _load_request(path)
    try:
        local = dt.datetime.fromisoformat(str(data.get("local_datetime", "")))
    except ValueError:
        raise RuntimeError("local_datetime must use YYYY-MM-DDTHH:MM[:SS].") from None
    if local.tzinfo is not None:
        raise RuntimeError("local_datetime must be local clock time without a UTC offset; specify from_timezone separately.")
    source_name = str(data.get("from_timezone", "")).strip()
    target_name = str(data.get("to_timezone", "")).strip()
    if len(source_name) > 80 or len(target_name) > 80:
        raise RuntimeError("Timezone names must be valid IANA names.")
    try:
        source = ZoneInfo(source_name)
        target = ZoneInfo(target_name)
    except (ZoneInfoNotFoundError, ValueError):
        raise RuntimeError("Use valid IANA timezone names such as Asia/Ho_Chi_Minh or America/New_York.") from None
    candidates = _valid_local_times(local, source)
    if not candidates:
        raise RuntimeError("That local clock time does not exist because the timezone changes its clocks at that time.")
    requested_fold = data.get("fold")
    if requested_fold is not None:
        fold = _integer(requested_fold, "fold", 0, 1)
        candidates = [candidate for candidate in candidates if candidate.fold == fold]
        if not candidates:
            raise RuntimeError("The selected fold is not valid for this local time.")
    lines = [
        "Timezone converter",
        f"From: {source_name}",
        f"To: {target_name}",
    ]
    for index, candidate in enumerate(candidates, 1):
        utc = candidate.astimezone(dt.timezone.utc)
        converted = utc.astimezone(target)
        label = f"Possible interpretation {index}: " if len(candidates) > 1 else "Local time: "
        lines.extend([
            f"{label}{candidate.isoformat()}",
            f"UTC: {utc.isoformat()}",
            f"Converted: {converted.isoformat()} ({target_name})",
        ])
    if len(candidates) > 1:
        lines.append("The source clock time occurs twice during a daylight-saving transition. Both valid interpretations are shown; choose fold 0 or 1 to select one.")
    return _write(path, "timezone-conversion", "\n".join(lines),
                  f"Converted {local.isoformat()} from {source_name} to {target_name}; {len(candidates)} valid interpretation(s).")


def _format_quantity(value: Decimal) -> str:
    return _fmt(value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def recipe_scaler(path: Path) -> dict:
    data = _load_request(path)
    original = _decimal(data.get("original_servings"), "original_servings", "0.01", 100000)
    target = _decimal(data.get("target_servings"), "target_servings", "0.01", 100000)
    ingredients = data.get("ingredients")
    if not isinstance(ingredients, list) or not 1 <= len(ingredients) <= MAX_ITEMS:
        raise RuntimeError("ingredients must be a list containing 1–200 items.")
    factor = target / original
    lines = [
        "Recipe scaler",
        f"Original servings: {_fmt(original)}",
        f"Target servings: {_fmt(target)}",
        f"Scale factor: ×{_format_quantity(factor)}",
        "",
        "Ingredients:",
    ]
    for index, item in enumerate(ingredients, 1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Ingredient {index} must be an object.")
        name = str(item.get("name", "")).strip()
        unit = str(item.get("unit", "")).strip()
        if not name or len(name) > 120 or len(unit) > 32:
            raise RuntimeError(f"Ingredient {index} needs a name (max 120 chars) and a short unit (max 32 chars).")
        raw_amount = item.get("amount")
        if isinstance(raw_amount, (int, float, Decimal)) and not isinstance(raw_amount, bool):
            amount = _decimal(raw_amount, f"ingredient {index} amount", 0, 1000000000) * factor
            lines.append(f"{index}. {_format_quantity(amount)} {unit} {name}".strip())
        elif isinstance(raw_amount, str) and 0 < len(raw_amount.strip()) <= 80:
            lines.append(f"{index}. {raw_amount.strip()} {unit} {name} (unchanged; non-numeric amount)".strip())
        else:
            raise RuntimeError(f"Ingredient {index} amount must be a non-negative number or short text such as 'to taste'.")
    return _write(path, "scaled-recipe", "\n".join(lines),
                  f"Scaled {len(ingredients)} ingredients from {_fmt(original)} to {_fmt(target)} servings (×{_format_quantity(factor)}).")


def grade_calculator(path: Path) -> dict:
    data = _load_request(path)
    components = data.get("components")
    if not isinstance(components, list) or not 1 <= len(components) <= MAX_ITEMS:
        raise RuntimeError("components must contain 1–200 graded components.")
    graded_weight = ZERO
    earned_weight = ZERO
    details = []
    for index, item in enumerate(components, 1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Component {index} must be an object.")
        name = str(item.get("name") or f"Component {index}").strip()[:100]
        score = _decimal(item.get("score"), f"{name} score", 0, 1000000)
        maximum = _decimal(item.get("max_score", 100), f"{name} max_score", "0.000001", 1000000)
        weight = _decimal(item.get("weight_percent"), f"{name} weight_percent", "0.000001", 100)
        if score > maximum:
            raise RuntimeError(f"{name} score cannot exceed max_score.")
        graded_weight += weight
        earned_weight += (score / maximum * Decimal(100)) * weight / Decimal(100)
        details.append((name, score, maximum, weight, score / maximum * Decimal(100)))
    if graded_weight > Decimal(100):
        raise RuntimeError("The sum of graded weight_percent values cannot exceed 100.")
    current_average = earned_weight / graded_weight * Decimal(100) if graded_weight else ZERO
    remaining = Decimal(100) - graded_weight
    lines = [
        "Grade calculator",
        f"Graded weight: {_fmt(graded_weight)}%",
        f"Remaining weight: {_fmt(remaining)}%",
        f"Weighted points already earned: {_fmt(earned_weight)} / 100",
        f"Average across graded components: {_fmt(current_average, 2)}%",
        "",
        "Components:",
    ]
    for name, score, maximum, weight, percent in details:
        lines.append(f"- {name}: {_fmt(score)} / {_fmt(maximum)} = {_fmt(percent, 2)}%; weight {_fmt(weight)}%")
    target_raw = data.get("target_overall_percent")
    summary = f"Current weighted contribution: {_fmt(earned_weight, 2)} points; average on graded work: {_fmt(current_average, 2)}%."
    if target_raw is not None:
        target = _decimal(target_raw, "target_overall_percent", 0, 100)
        lines.extend(["", f"Target overall result: {_fmt(target)}%"])
        if remaining == ZERO:
            lines.append("No ungraded weight remains; the final weighted result is already determined.")
            if earned_weight >= target:
                lines.append("The target has been reached.")
            else:
                lines.append("The target cannot be reached from the currently entered completed components.")
        else:
            needed = (target - earned_weight) / remaining * Decimal(100)
            lines.append(f"Required average across the remaining {_fmt(remaining)}%: {_fmt(needed, 2)}%")
            if needed <= ZERO:
                lines.append("The target is already secured, even with zero points on the remaining work.")
            elif needed > Decimal(100):
                lines.append("The target is not reachable with the remaining weight under a 100% score cap.")
        summary += f" Required average on remaining work for {_fmt(target)}% overall: {_fmt(needed, 2) if remaining else 'not applicable'}%."
    return _write(path, "grade-calculation", "\n".join(lines), summary)


def paint_calculator(path: Path) -> dict:
    data = _load_request(path)
    length = _decimal(data.get("length_m"), "length_m", "0.1", 1000)
    width = _decimal(data.get("width_m"), "width_m", "0.1", 1000)
    height = _decimal(data.get("height_m"), "height_m", "0.1", 100)
    coats = _integer(data.get("coats", 2), "coats", 1, 5)
    coverage = _decimal(data.get("coverage_m2_per_liter", 10), "coverage_m2_per_liter", "0.1", 1000)
    doors = _integer(data.get("doors_count", 0), "doors_count", 0, 100)
    door_area = _decimal(data.get("door_area_m2", 2), "door_area_m2", 0, 20)
    windows = _integer(data.get("windows_count", 0), "windows_count", 0, 100)
    window_area = _decimal(data.get("window_area_m2", 1.5), "window_area_m2", 0, 20)
    waste = _decimal(data.get("waste_percent", 10), "waste_percent", 0, 50)
    include_ceiling = data.get("include_ceiling", False)
    if not isinstance(include_ceiling, bool):
        raise RuntimeError("include_ceiling must be true or false.")
    walls = Decimal(2) * (length + width) * height
    openings = doors * door_area + windows * window_area
    if openings >= walls:
        raise RuntimeError("Door and window area must be smaller than the total wall area.")
    paint_area = walls - openings + (length * width if include_ceiling else ZERO)
    required = paint_area * coats / coverage * (ONE + waste / Decimal(100))
    recommended = required.quantize(Decimal("0.5"), rounding=ROUND_CEILING) / Decimal(1)
    lines = [
        "Paint coverage calculator",
        f"Room: {_fmt(length)} m × {_fmt(width)} m × {_fmt(height)} m",
        f"Gross wall area: {_fmt(walls, 2)} m²",
        f"Door/window area deducted: {_fmt(openings, 2)} m²",
        f"Paintable area: {_fmt(paint_area, 2)} m²",
        f"Coats: {coats}",
        f"Coverage assumption: {_fmt(coverage)} m² per litre",
        f"Allowance for waste: {_fmt(waste)}%",
        f"Estimated paint: {_fmt(required, 2)} litres",
        f"Practical purchase estimate: about {_fmt(recommended, 1)} litres (rounded up to 0.5 L)",
        "Estimate only: surface texture, primer, color changes and actual product coverage can change the amount required.",
    ]
    return _write(path, "paint-estimate", "\n".join(lines),
                  f"Estimated paint: {_fmt(required, 2)} L; plan to buy about {_fmt(recommended, 1)} L.")


def fuel_trip_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency", "VND"))
    places = _minor_units(currency)
    distance = _decimal(data.get("distance_km"), "distance_km", "0.01", 10000000)
    round_trip = data.get("round_trip", False)
    if not isinstance(round_trip, bool):
        raise RuntimeError("round_trip must be true or false.")
    trips = _integer(data.get("trips", 1), "trips", 1, 1000)
    passengers = _integer(data.get("passengers", 1), "passengers", 1, 1000)
    consumption = _decimal(data.get("consumption_l_per_100km"), "consumption_l_per_100km", "0.01", 200)
    price = _money(_decimal(data.get("fuel_price_per_liter"), "fuel_price_per_liter", "0.0001", "1000000000"), currency)
    total_distance = distance * (2 if round_trip else 1) * trips
    liters = total_distance * consumption / Decimal(100)
    total_cost = _money(liters * price, currency)
    per_person = _money(total_cost / passengers, currency)
    return _write(path, "fuel-trip-estimate", "\n".join([
        "Fuel trip calculator",
        f"One-way distance: {_fmt(distance)} km",
        f"Round trip: {'yes' if round_trip else 'no'}",
        f"Trip count: {trips}",
        f"Total distance: {_fmt(total_distance, 2)} km",
        f"Fuel consumption assumption: {_fmt(consumption)} L / 100 km",
        f"Estimated fuel: {_fmt(liters, 2)} L",
        f"Fuel price: {currency} {_fmt(price, places)} / L",
        f"Estimated fuel cost: {currency} {_fmt(total_cost, places)}",
        f"Passengers sharing the cost: {passengers}",
        f"Estimated cost per passenger: {currency} {_fmt(per_person, places)}",
        "Fuel-only estimate; excludes tolls, parking, maintenance, traffic, air-conditioning and price changes.",
    ]), f"Estimated fuel cost {currency} {_fmt(total_cost, places)} for {_fmt(total_distance, 2)} km.")


def discount_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency", "USD"))
    places = _minor_units(currency)
    price = _money(_decimal(data.get("original_price"), "original_price", "0.01", "1000000000000000"), currency)
    discount = _decimal(data.get("discount_percent"), "discount_percent", 0, 100)
    extra = _decimal(data.get("extra_discount_percent", 0), "extra_discount_percent", 0, 100)
    tax = _decimal(data.get("tax_percent", 0), "tax_percent", 0, 100)
    quantity = _integer(data.get("quantity", 1), "quantity", 1, 100000)
    after_first = price * (ONE - discount / Decimal(100))
    after_second = after_first * (ONE - extra / Decimal(100))
    tax_amount = _money(after_second * tax / Decimal(100), currency)
    final_unit = _money(after_second + tax_amount, currency)
    savings = _money(price - after_second, currency)
    total = _money(final_unit * quantity, currency)
    lines = [
        "Discount calculator",
        f"Original unit price: {currency} {_fmt(price, places)}",
        f"First discount: {_fmt(discount)}%",
        f"Additional discount: {_fmt(extra)}% (applied after the first discount)",
        f"Price after discounts: {currency} {_fmt(_money(after_second, currency), places)}",
        f"Tax: {_fmt(tax)}% ({currency} {_fmt(tax_amount, places)} per item)",
        f"Final unit price including tax: {currency} {_fmt(final_unit, places)}",
        f"Savings per item before tax: {currency} {_fmt(savings, places)}",
        f"Quantity: {quantity}",
        f"Total for quantity: {currency} {_fmt(total, places)}",
    ]
    return _write(path, "discount-estimate", "\n".join(lines),
                  f"Final price {currency} {_fmt(final_unit, places)} each; {quantity} item(s) total {currency} {_fmt(total, places)}.")


_UNIT_MAP = {
    "mg": ("mass", "g", Decimal("0.001")), "milligram": ("mass", "g", Decimal("0.001")), "milligrams": ("mass", "g", Decimal("0.001")),
    "g": ("mass", "g", ONE), "gram": ("mass", "g", ONE), "grams": ("mass", "g", ONE),
    "kg": ("mass", "g", Decimal(1000)), "kilogram": ("mass", "g", Decimal(1000)), "kilograms": ("mass", "g", Decimal(1000)),
    "ml": ("volume", "mL", ONE), "milliliter": ("volume", "mL", ONE), "milliliters": ("volume", "mL", ONE), "millilitre": ("volume", "mL", ONE), "millilitres": ("volume", "mL", ONE),
    "l": ("volume", "mL", Decimal(1000)), "liter": ("volume", "mL", Decimal(1000)), "liters": ("volume", "mL", Decimal(1000)), "litre": ("volume", "mL", Decimal(1000)), "litres": ("volume", "mL", Decimal(1000)),
    "cm": ("length", "cm", ONE), "centimeter": ("length", "cm", ONE), "centimeters": ("length", "cm", ONE), "centimetre": ("length", "cm", ONE), "centimetres": ("length", "cm", ONE),
    "m": ("length", "cm", Decimal(100)), "meter": ("length", "cm", Decimal(100)), "meters": ("length", "cm", Decimal(100)), "metre": ("length", "cm", Decimal(100)), "metres": ("length", "cm", Decimal(100)),
    "each": ("count", "each", ONE), "unit": ("count", "each", ONE), "units": ("count", "each", ONE), "pc": ("count", "each", ONE), "pcs": ("count", "each", ONE), "piece": ("count", "each", ONE), "pieces": ("count", "each", ONE),
}


def unit_price_comparator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency", "USD"))
    places = _minor_units(currency)
    items = data.get("items")
    if not isinstance(items, list) or not 2 <= len(items) <= 100:
        raise RuntimeError("items must contain 2–100 packages.")
    normalized = []
    dimension = None
    base_unit = None
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Item {index} must be an object.")
        name = str(item.get("name") or f"Package {index}").strip()[:100]
        price = _money(_decimal(item.get("price"), f"item {index} price", "0.0001", "1000000000000000"), currency)
        quantity = _decimal(item.get("quantity"), f"item {index} quantity", "0.000001", "1000000000")
        unit = str(item.get("unit", "")).strip().casefold()
        info = _UNIT_MAP.get(unit)
        if not info:
            raise RuntimeError(f"Item {index} uses an unsupported unit. Use g, kg, mg, mL, L, cm, m or each.")
        current_dimension, current_base, factor = info
        if dimension is None:
            dimension, base_unit = current_dimension, current_base
        elif current_dimension != dimension:
            raise RuntimeError("All packages must use comparable units from the same dimension (mass, volume, length or count).")
        base_quantity = quantity * factor
        normalized.append((name, price, quantity, unit, base_quantity, price / base_quantity))
    normalized.sort(key=lambda row: row[5])
    lines = [
        "Unit price comparator",
        f"Currency: {currency}",
        f"Comparable dimension: {dimension} (normalized to {base_unit})",
        "",
        "Packages, cheapest unit price first:",
    ]
    for rank, (name, price, quantity, unit, base_quantity, unit_price) in enumerate(normalized, 1):
        lines.append(
            f"{rank}. {name}: {currency} {_fmt(price, places)} for {_fmt(quantity)} {unit}; "
            f"{currency} {_fmt(_money(unit_price, currency), places)} per {base_unit}"
        )
    lines.extend(["", f"Best unit price: {normalized[0][0]}."])
    return _write(path, "unit-price-comparison", "\n".join(lines),
                  f"Lowest unit price: {normalized[0][0]} at {currency} {_fmt(_money(normalized[0][5], currency), places)} per {base_unit}.")
