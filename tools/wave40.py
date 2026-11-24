"""Everyday household, travel and device calculators for Nolane Wave 40.

All calculations are deterministic and offline. They use user-supplied prices,
rates and measurements; no tariff, market or service data is fetched.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP, localcontext
from pathlib import Path

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
        value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_reject_duplicate_keys)
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


def _integer(value, label: str, minimum: int, maximum: int, default=None) -> int:
    if value is None and default is not None:
        value = default
    number = _decimal(value, label, minimum, maximum)
    if number != number.to_integral_value():
        raise RuntimeError(f"{label} must be a whole number.")
    return int(number)


def _currency(value) -> str:
    code = str(value or "VND").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", code):
        raise RuntimeError("currency must be a three-letter code such as VND, USD or EUR.")
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
    return {"summary": summary or body.splitlines()[0][:500], "output_path": str(output)}


def _items(value, label: str, minimum=1, maximum=MAX_ITEMS) -> list:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise RuntimeError(f"{label} must be a list containing {minimum}–{maximum} items.")
    if any(not isinstance(item, dict) for item in value):
        raise RuntimeError(f"Every {label} item must be an object.")
    return value


def appliance_energy_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    tariff = _money(_decimal(data.get("price_per_kwh"), "price_per_kwh", 0, "1000000000"), currency)
    appliances = _items(data.get("appliances"), "appliances")
    total_kwh = ZERO
    total_cost = ZERO
    rows = []
    for index, item in enumerate(appliances, 1):
        name = str(item.get("name") or f"Appliance {index}").strip()[:100]
        watts = _decimal(item.get("watts"), f"{name} watts", "0.01", "1000000")
        hours = _decimal(item.get("hours_per_day"), f"{name} hours_per_day", 0, 24)
        days = _decimal(item.get("days_per_month", 30), f"{name} days_per_month", 0, 31)
        quantity = _integer(item.get("quantity", 1), f"{name} quantity", 1, 1000)
        kwh = watts * hours * days * quantity / Decimal(1000)
        cost = _money(kwh * tariff, currency)
        total_kwh += kwh
        total_cost += cost
        rows.append((name, quantity, watts, hours, days, kwh, cost))
    total_cost = _money(total_cost, currency)
    lines = [
        "Home electricity-use estimate",
        f"Price assumption: {currency} {_fmt(tariff, places)} per kWh",
        "",
        "Appliances:",
    ]
    for name, quantity, watts, hours, days, kwh, cost in rows:
        lines.append(
            f"- {name} ×{quantity}: {_fmt(watts)} W × {_fmt(hours)} h/day × {_fmt(days)} days "
            f"= {_fmt(kwh, 3)} kWh; estimated cost {currency} {_fmt(cost, places)}"
        )
    lines.extend([
        "",
        f"Total monthly energy: {_fmt(total_kwh, 3)} kWh",
        f"Estimated monthly cost: {currency} {_fmt(total_cost, places)}",
        "Estimate only: actual meter readings, standby use, tiered tariffs, taxes and fixed charges may differ.",
    ])
    return _write(path, "electricity-estimate", "\n".join(lines),
                  f"Estimated monthly use {_fmt(total_kwh, 2)} kWh; cost {currency} {_fmt(total_cost, places)}.")


def floor_tile_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    length = _decimal(data.get("room_length_m"), "room_length_m", "0.1", 1000)
    width = _decimal(data.get("room_width_m"), "room_width_m", "0.1", 1000)
    tile_length = _decimal(data.get("tile_length_cm"), "tile_length_cm", "1", 300)
    tile_width = _decimal(data.get("tile_width_cm"), "tile_width_cm", "1", 300)
    waste = _decimal(data.get("waste_percent", 10), "waste_percent", 0, 50)
    per_box = _integer(data.get("tiles_per_box"), "tiles_per_box", 1, 1000)
    price = _money(_decimal(data.get("price_per_box", 0), "price_per_box", 0, "1000000000000"), currency)
    room_area = length * width
    tile_area = tile_length * tile_width / Decimal(10000)
    tile_count = int((room_area / tile_area * (ONE + waste / 100)).to_integral_value(rounding=ROUND_CEILING))
    boxes = (tile_count + per_box - 1) // per_box
    purchased = boxes * per_box
    cost = _money(Decimal(boxes) * price, currency)
    lines = [
        "Floor tile estimator",
        f"Room: {_fmt(length)} m × {_fmt(width)} m = {_fmt(room_area, 2)} m²",
        f"Tile: {_fmt(tile_length)} cm × {_fmt(tile_width)} cm = {_fmt(tile_area, 4)} m² each",
        f"Waste allowance: {_fmt(waste)}%",
        f"Tiles required including waste: {tile_count}",
        f"Tiles per box: {per_box}",
        f"Boxes to buy: {boxes} ({purchased} tiles)",
        f"Estimated material cost: {currency} {_fmt(cost, places)}",
        "Estimate excludes grout, adhesive, trims, breakage beyond the selected waste allowance and installation.",
    ]
    return _write(path, "floor-tile-estimate", "\n".join(lines),
                  f"Allow about {tile_count} tiles; buy {boxes} boxes ({currency} {_fmt(cost, places)}).")


def concrete_volume_calculator(path: Path) -> dict:
    data = _load_request(path)
    length = _decimal(data.get("length_m"), "length_m", "0.01", 1000)
    width = _decimal(data.get("width_m"), "width_m", "0.01", 1000)
    depth = _decimal(data.get("depth_m"), "depth_m", "0.001", 100)
    waste = _decimal(data.get("waste_percent", 10), "waste_percent", 0, 50)
    volume = length * width * depth
    adjusted = volume * (ONE + waste / 100)
    lines = [
        "Concrete volume estimate",
        f"Dimensions: {_fmt(length)} m × {_fmt(width)} m × {_fmt(depth)} m",
        f"Base volume: {_fmt(volume, 4)} m³ ({_fmt(volume * 1000, 1)} litres)",
        f"Waste allowance: {_fmt(waste)}%",
        f"Order estimate: {_fmt(adjusted, 4)} m³ ({_fmt(adjusted * 1000, 1)} litres)",
    ]
    bags_raw = data.get("bag_yield_l")
    summary = f"Order estimate {_fmt(adjusted, 3)} m³ ({_fmt(adjusted * 1000, 0)} L)."
    if bags_raw is not None:
        yield_l = _decimal(bags_raw, "bag_yield_l", "0.1", 1000)
        bags = int((adjusted * 1000 / yield_l).to_integral_value(rounding=ROUND_CEILING))
        lines.extend([f"Yield per bag: {_fmt(yield_l)} litres", f"Bags required: {bags}"])
        if data.get("price_per_bag") is not None:
            currency = _currency(data.get("currency"))
            places = _minor_units(currency)
            price = _money(_decimal(data.get("price_per_bag"), "price_per_bag", 0, "1000000000000"), currency)
            total = _money(price * bags, currency)
            lines.append(f"Estimated bag cost: {currency} {_fmt(total, places)}")
            summary += f" Approximately {bags} bags, estimated {currency} {_fmt(total, places)}."
    lines.append("Estimate only; finished volume varies by mix, aggregate, compaction, ground conditions and supplier yield.")
    return _write(path, "concrete-volume-estimate", "\n".join(lines), summary)


def soil_mulch_calculator(path: Path) -> dict:
    data = _load_request(path)
    area = _decimal(data.get("area_m2"), "area_m2", "0.01", 1000000)
    depth = _decimal(data.get("depth_cm"), "depth_cm", "0.1", 500)
    waste = _decimal(data.get("waste_percent", 10), "waste_percent", 0, 50)
    base_l = area * depth * 10
    required_l = base_l * (ONE + waste / 100)
    lines = [
        "Soil and mulch volume estimate",
        f"Area: {_fmt(area)} m²",
        f"Depth: {_fmt(depth)} cm",
        f"Base volume: {_fmt(base_l, 1)} litres ({_fmt(base_l / 1000, 3)} m³)",
        f"Waste allowance: {_fmt(waste)}%",
        f"Order estimate: {_fmt(required_l, 1)} litres ({_fmt(required_l / 1000, 3)} m³)",
    ]
    summary = f"Order approximately {_fmt(required_l, 0)} litres ({_fmt(required_l / 1000, 3)} m³)."
    if data.get("bag_volume_l") is not None:
        bag_l = _decimal(data.get("bag_volume_l"), "bag_volume_l", "0.1", 1000)
        bags = int((required_l / bag_l).to_integral_value(rounding=ROUND_CEILING))
        lines.extend([f"Bag size: {_fmt(bag_l)} litres", f"Bags required: {bags}"])
        if data.get("price_per_bag") is not None:
            currency = _currency(data.get("currency"))
            places = _minor_units(currency)
            price = _money(_decimal(data.get("price_per_bag"), "price_per_bag", 0, "1000000000000"), currency)
            cost = _money(price * bags, currency)
            lines.append(f"Estimated bag cost: {currency} {_fmt(cost, places)}")
            summary += f" Buy about {bags} bags, estimated {currency} {_fmt(cost, places)}."
    return _write(path, "soil-mulch-estimate", "\n".join(lines), summary)


def household_budget_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    income = _money(_decimal(data.get("monthly_income"), "monthly_income", 0, "1000000000000000"), currency)
    expenses = _items(data.get("expenses"), "expenses", minimum=0)
    totals: dict[str, Decimal] = {}
    overall = ZERO
    for index, item in enumerate(expenses, 1):
        name = str(item.get("name") or f"Expense {index}").strip()[:100]
        category = str(item.get("category") or "Other").strip()[:60] or "Other"
        amount = _money(_decimal(item.get("monthly_amount"), f"{name} monthly_amount", 0, "1000000000000000"), currency)
        totals[category] = totals.get(category, ZERO) + amount
        overall += amount
    remaining = income - overall
    lines = [
        "Monthly household budget",
        f"Monthly income: {currency} {_fmt(income, places)}",
        f"Planned expenses: {currency} {_fmt(overall, places)}",
        "",
        "Expenses by category:",
    ]
    for category, amount in sorted(totals.items(), key=lambda row: row[1], reverse=True):
        share = (amount / income * 100) if income else ZERO
        lines.append(f"- {category}: {currency} {_fmt(amount, places)} ({_fmt(share, 1)}% of income)")
    lines.extend([
        "",
        f"Money remaining: {currency} {_fmt(remaining, places)}",
        f"Remaining share of income: {_fmt(remaining / income * 100, 1) if income else 'n/a'}%",
        "This is a cash-flow summary from the amounts you entered, not a financial recommendation. It excludes unlisted and irregular costs.",
    ])
    return _write(path, "monthly-budget", "\n".join(lines),
                  f"Income {currency} {_fmt(income, places)}; expenses {currency} {_fmt(overall, places)}; remaining {currency} {_fmt(remaining, places)}.")


def savings_goal_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    target = _money(_decimal(data.get("target_amount"), "target_amount", "0.01", "1000000000000000"), currency)
    current = _money(_decimal(data.get("current_savings", 0), "current_savings", 0, "1000000000000000"), currency)
    monthly = _money(_decimal(data.get("monthly_contribution"), "monthly_contribution", 0, "1000000000000000"), currency)
    annual = _decimal(data.get("annual_interest_rate_percent", 0), "annual_interest_rate_percent", 0, 100)
    if current >= target:
        months = 0
        balance = current
    elif monthly == ZERO and annual == ZERO:
        raise RuntimeError("The goal cannot be reached with zero monthly contributions and zero interest.")
    else:
        with localcontext() as ctx:
            ctx.prec = 32
            rate = annual / Decimal(1200)
            balance = current
            months = 0
            while balance < target and months < 1200:
                balance = _money(balance * (ONE + rate) + monthly, currency)
                months += 1
            if balance < target:
                raise RuntimeError("The target was not reached within 100 years; increase the contribution or adjust the assumptions.")
    total_contributed = _money(current + monthly * months, currency)
    interest = _money(balance - total_contributed, currency)
    years, remaining_months = divmod(months, 12)
    lines = [
        "Savings goal estimate",
        f"Target: {currency} {_fmt(target, places)}",
        f"Starting savings: {currency} {_fmt(current, places)}",
        f"Monthly contribution: {currency} {_fmt(monthly, places)}",
        f"Annual interest assumption: {_fmt(annual)}% (compounded monthly)",
        f"Estimated time: {months} months ({years} years and {remaining_months} months)",
        f"Estimated balance at that point: {currency} {_fmt(balance, places)}",
        f"Total starting savings plus contributions: {currency} {_fmt(total_contributed, places)}",
        f"Estimated interest: {currency} {_fmt(interest, places)}",
        "Illustration only: actual rates, taxes, fees, inflation and deposit timing can change the outcome. Interest is assumed constant.",
    ]
    return _write(path, "savings-goal", "\n".join(lines),
                  f"Estimated time to reach the goal: {months} months at {currency} {_fmt(monthly, places)} per month.")


def travel_budget_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    people = _integer(data.get("travelers"), "travelers", 1, 1000)
    days = _integer(data.get("days"), "days", 1, 365)
    buffer = _decimal(data.get("buffer_percent", 10), "buffer_percent", 0, 100)
    items = _items(data.get("expenses"), "expenses", minimum=0)
    total = ZERO
    by_category: dict[str, Decimal] = {}
    for index, item in enumerate(items, 1):
        category = str(item.get("category") or f"Expense {index}").strip()[:80]
        amount = _money(_decimal(item.get("total_cost"), f"{category} total_cost", 0, "1000000000000000"), currency)
        by_category[category] = by_category.get(category, ZERO) + amount
        total += amount
    buffered = _money(total * (ONE + buffer / 100), currency)
    per_person = _money(buffered / people, currency)
    per_person_day = _money(buffered / people / days, currency)
    lines = [
        "Travel budget estimate",
        f"Travelers: {people}",
        f"Trip length: {days} days",
        "",
        "Budget by category:",
    ]
    for category, amount in sorted(by_category.items(), key=lambda row: row[1], reverse=True):
        lines.append(f"- {category}: {currency} {_fmt(amount, places)}")
    lines.extend([
        "",
        f"Base trip budget: {currency} {_fmt(total, places)}",
        f"Buffer: {_fmt(buffer)}%",
        f"Budget including buffer: {currency} {_fmt(buffered, places)}",
        f"Per person: {currency} {_fmt(per_person, places)}",
        f"Per person per day: {currency} {_fmt(per_person_day, places)}",
        "Estimate excludes costs not entered, exchange-rate changes and unexpected disruptions.",
    ])
    return _write(path, "travel-budget", "\n".join(lines),
                  f"Trip estimate {currency} {_fmt(buffered, places)} including buffer; {currency} {_fmt(per_person, places)} per person.")


_SIZE_BYTES = {
    "B": Decimal(1), "KB": Decimal(1000), "MB": Decimal(1000000), "GB": Decimal(1000000000), "TB": Decimal(1000000000000),
    "KIB": Decimal(1024), "MIB": Decimal(1048576), "GIB": Decimal(1073741824), "TIB": Decimal(1099511627776),
}
_SPEED_BPS = {
    "BPS": Decimal(1), "KBPS": Decimal(1000), "MBPS": Decimal(1000000), "GBPS": Decimal(1000000000),
    "B/S": Decimal(8), "KB/S": Decimal(8000), "MB/S": Decimal(8000000), "GB/S": Decimal(8000000000),
    "KIB/S": Decimal(8192), "MIB/S": Decimal(8388608), "GIB/S": Decimal(8589934592),
}


def download_time_calculator(path: Path) -> dict:
    data = _load_request(path)
    size_value = _decimal(data.get("file_size"), "file_size", "0.000001", "1000000000000000")
    size_unit = str(data.get("file_size_unit", "GB")).strip().upper()
    if size_unit not in _SIZE_BYTES:
        raise RuntimeError("file_size_unit must be B, KB, MB, GB, TB, KiB, MiB, GiB or TiB.")
    speed_value = _decimal(data.get("speed"), "speed", "0.000001", "1000000000000000")
    speed_unit = str(data.get("speed_unit", "Mbps")).strip().upper()
    if speed_unit not in _SPEED_BPS:
        raise RuntimeError("speed_unit must be bps, Kbps, Mbps, Gbps, B/s, KB/s, MB/s, GB/s, KiB/s, MiB/s or GiB/s.")
    overhead = _decimal(data.get("overhead_percent", 0), "overhead_percent", 0, 100)
    bits = size_value * _SIZE_BYTES[size_unit] * 8
    bits *= ONE + overhead / 100
    rate = speed_value * _SPEED_BPS[speed_unit]
    seconds = bits / rate
    minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)
    remaining_seconds = seconds - Decimal(int(seconds // 60) * 60)
    lines = [
        "Download time estimate",
        f"File size: {_fmt(size_value)} {size_unit}",
        f"Connection speed: {_fmt(speed_value)} {speed_unit}",
        f"Overhead allowance: {_fmt(overhead)}%",
        f"Estimated time: {hours} h {minutes} min {_fmt(remaining_seconds, 1)} sec",
        f"Seconds: {_fmt(seconds, 1)}",
        "Theoretical estimate assumes the stated speed is sustained; Wi-Fi, server limits, congestion and protocol overhead can lengthen the transfer.",
    ]
    return _write(path, "download-time", "\n".join(lines),
                  f"Estimated download time: {hours} h {minutes} min {_fmt(remaining_seconds, 0)} sec.")


def work_hours_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    rate = _money(_decimal(data.get("hourly_rate", 0), "hourly_rate", 0, "1000000000000"), currency)
    shifts = _items(data.get("shifts"), "shifts")
    total_hours = ZERO
    total_pay = ZERO
    rows = []
    for index, item in enumerate(shifts, 1):
        label = str(item.get("label") or f"Shift {index}").strip()[:80]
        start = str(item.get("start", "")).strip()
        end = str(item.get("end", "")).strip()
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", start) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", end):
            raise RuntimeError(f"{label} start/end must use HH:MM (24-hour time).")
        start_minutes = int(start[:2]) * 60 + int(start[3:])
        end_minutes = int(end[:2]) * 60 + int(end[3:])
        duration = end_minutes - start_minutes
        if duration <= 0:
            duration += 24 * 60
        if duration >= 24 * 60:
            raise RuntimeError(f"{label} duration must be less than 24 hours.")
        break_minutes = _integer(item.get("break_minutes", 0), f"{label} break_minutes", 0, duration - 1)
        paid_hours = Decimal(duration - break_minutes) / 60
        pay = _money(paid_hours * rate, currency)
        total_hours += paid_hours
        total_pay += pay
        rows.append((label, start, end, break_minutes, paid_hours, pay))
    total_pay = _money(total_pay, currency)
    lines = ["Work hours summary", f"Hourly rate assumption: {currency} {_fmt(rate, places)}", "", "Shifts:"]
    for label, start, end, break_minutes, hours, pay in rows:
        lines.append(f"- {label}: {start}–{end}; break {_fmt(Decimal(break_minutes))} min; paid {_fmt(hours, 2)} h; pay {currency} {_fmt(pay, places)}")
    lines.extend([
        "",
        f"Total paid hours: {_fmt(total_hours, 2)}",
        f"Estimated gross pay: {currency} {_fmt(total_pay, places)}",
        "This is a time-and-pay arithmetic estimate; it does not apply local overtime, tax, holiday or employment rules.",
    ])
    return _write(path, "work-hours", "\n".join(lines),
                  f"{_fmt(total_hours, 2)} paid hours; estimated gross pay {currency} {_fmt(total_pay, places)}.")


def battery_runtime_calculator(path: Path) -> dict:
    data = _load_request(path)
    power = _decimal(data.get("device_power_w"), "device_power_w", "0.001", 100000)
    efficiency = _decimal(data.get("efficiency_percent", 85), "efficiency_percent", "0.1", 100)
    reserve = _decimal(data.get("reserve_percent", 0), "reserve_percent", 0, 90)
    if data.get("battery_wh") is not None:
        capacity = _decimal(data.get("battery_wh"), "battery_wh", "0.001", 100000000)
        source = "Wh"
    else:
        mah = _decimal(data.get("capacity_mah"), "capacity_mah", "0.001", 1000000000)
        voltage = _decimal(data.get("voltage_v"), "voltage_v", "0.001", 1000)
        capacity = mah * voltage / 1000
        source = f"{_fmt(mah)} mAh × {_fmt(voltage)} V"
    usable = capacity * (ONE - reserve / 100) * efficiency / 100
    hours = usable / power
    whole_minutes = int((hours * 60).to_integral_value(rounding=ROUND_HALF_UP))
    h, m = divmod(whole_minutes, 60)
    lines = [
        "Battery runtime estimate",
        f"Battery capacity input: {source}",
        f"Nominal energy: {_fmt(capacity, 3)} Wh",
        f"Efficiency assumption: {_fmt(efficiency)}%",
        f"Reserved capacity: {_fmt(reserve)}%",
        f"Usable energy estimate: {_fmt(usable, 3)} Wh",
        f"Device power draw: {_fmt(power)} W",
        f"Estimated runtime: {h} h {m} min",
        "Estimate assumes constant power draw; battery age, temperature, peak loads and device power-management behaviour can change runtime.",
    ]
    return _write(path, "battery-runtime", "\n".join(lines),
                  f"Estimated runtime about {h} h {m} min at {_fmt(power)} W.")


def water_tank_volume_calculator(path: Path) -> dict:
    data = _load_request(path)
    shape = str(data.get("shape", "rectangular")).strip().lower()
    if shape == "rectangular":
        length = _decimal(data.get("length_m"), "length_m", "0.01", 1000)
        width = _decimal(data.get("width_m"), "width_m", "0.01", 1000)
        height = _decimal(data.get("height_m"), "height_m", "0.01", 100)
        capacity = length * width * height * 1000
        dimensions = f"{_fmt(length)} m × {_fmt(width)} m × {_fmt(height)} m"
    elif shape == "cylinder":
        radius = _decimal(data.get("radius_m"), "radius_m", "0.01", 100)
        height = _decimal(data.get("height_m"), "height_m", "0.01", 1000)
        # π is kept to 12 significant decimal places for a stable estimate.
        capacity = Decimal("3.141592653589793238462643383") * radius * radius * height * 1000
        dimensions = f"radius {_fmt(radius)} m × height {_fmt(height)} m"
    else:
        raise RuntimeError("shape must be rectangular or cylinder.")
    fill = _decimal(data.get("fill_percent", 100), "fill_percent", 0, 100)
    current = capacity * fill / 100
    lines = [
        "Water tank capacity",
        f"Shape: {shape}",
        f"Dimensions: {dimensions}",
        f"Full capacity: {_fmt(capacity, 1)} litres ({_fmt(capacity / 1000, 3)} m³)",
        f"Fill level: {_fmt(fill)}%",
        f"Water at this fill level: {_fmt(current, 1)} litres",
        "Geometric estimate; actual usable capacity is lower when fittings, rounded corners, freeboard or internal equipment take up space.",
    ]
    return _write(path, "water-tank-capacity", "\n".join(lines),
                  f"Tank capacity {_fmt(capacity, 0)} L; current fill estimate {_fmt(current, 0)} L.")
