"""Wave 46 home, vehicle and rental decision-support processors.

All observations, quotes, intervals, amounts, condition labels and contract
terms are user supplied. The reports organize facts and compute arithmetic;
they do not diagnose equipment, value property, rate contractors or interpret law.
"""
from __future__ import annotations

import calendar
import json
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

MAX_JSON_BYTES = 2 * 1024 * 1024
CENT = Decimal("0.01")
CONDITIONS = {"good", "worn", "damaged", "missing", "not_tested"}


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key.")
        result[key] = value
    return result


def _read(path: Path) -> dict:
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            raise RuntimeError("Request exceeds the 2 MiB JSON limit.")
        value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_pairs)
    except RuntimeError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError("Upload a valid UTF-8 JSON object.") from exc
    if not isinstance(value, dict):
        raise RuntimeError("Request must be one JSON object.")
    return value


def _row(value, label):
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be an object.")
    return value


def _list(value, label, minimum=1, maximum=300):
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise RuntimeError(f"{label} must contain {minimum} to {maximum} items.")
    return value


def _text(value, label, maximum=120):
    if not isinstance(value, str):
        raise RuntimeError(f"{label} must be text.")
    result = " ".join(value.split()).strip()
    if not result or len(result) > maximum:
        raise RuntimeError(f"{label} must contain 1 to {maximum} characters.")
    return result


def _number(value, label, minimum=None, maximum=Decimal("1000000000000")):
    if isinstance(value, bool) or value is None:
        raise RuntimeError(f"{label} must be a number.")
    try:
        result = Decimal(str(value).strip().replace(",", ""))
    except (InvalidOperation, ValueError, AttributeError):
        raise RuntimeError(f"{label} must be a number.") from None
    if not result.is_finite() or (minimum is not None and result < Decimal(str(minimum))) or result > Decimal(str(maximum)):
        raise RuntimeError(f"{label} is outside the permitted range.")
    return result


def _money(value, label):
    raw = _number(value, label, 0)
    rounded = raw.quantize(CENT, rounding=ROUND_HALF_UP)
    if abs(raw - rounded) > Decimal("0.0000001"):
        raise RuntimeError(f"{label} must have no more than two decimal places.")
    return rounded


def _integer(value, label, minimum=0, maximum=1_000_000):
    number = _number(value, label, minimum, maximum)
    if number != number.to_integral_value():
        raise RuntimeError(f"{label} must be a whole number.")
    return int(number)


def _date(value, label):
    raw = _text(value, label, 10)
    try:
        result = date.fromisoformat(raw)
    except ValueError:
        raise RuntimeError(f"{label} must use YYYY-MM-DD.") from None
    if result.isoformat() != raw:
        raise RuntimeError(f"{label} must use YYYY-MM-DD.")
    return result


def _currency(value):
    code = _text(value, "currency", 8).upper()
    if not code.isalnum() or not 3 <= len(code) <= 8:
        raise RuntimeError("currency must be a 3–8 character code such as VND, USD or EUR.")
    return code


def _fmt(value, places=2):
    rounded = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    result = format(rounded, "f")
    return result.rstrip("0").rstrip(".") if "." in result else result


def _month_add(value: date, months: int) -> date:
    total = value.year * 12 + value.month - 1 + months
    year, month_zero = divmod(total, 12)
    month = month_zero + 1
    return date(year, month, min(value.day, calendar.monthrange(year, month)[1]))


def _write(path: Path, suffix: str, body: str, summary: str) -> dict:
    output = path.with_name((path.stem[:64] or "nolane") + "-" + suffix + ".txt")
    output.write_text(body.rstrip() + "\n", encoding="utf-8")
    return {"summary": summary[:500], "output_path": str(output)}


def vehicle_fuel_log_analyzer(path: Path) -> dict:
    data = _read(path)
    currency = _currency(data.get("currency"))
    entries = _list(data.get("entries"), "entries", 2, 2000)
    parsed = []
    for i, raw in enumerate(entries, 1):
        item = _row(raw, f"fuel entry {i}")
        day = _date(item.get("date"), f"fuel entry {i} date")
        odo = _number(item.get("odometer_km"), f"fuel entry {i} odometer_km", 0, 10_000_000)
        litres = _number(item.get("litres"), f"fuel entry {i} litres", "0.001", 1000)
        price = _money(item.get("price_per_litre"), f"fuel entry {i} price_per_litre")
        full = item.get("full_tank")
        if not isinstance(full, bool):
            raise RuntimeError(f"fuel entry {i}: full_tank must be true or false.")
        parsed.append((day, odo, litres, price, full, i))
    parsed.sort(key=lambda row: (row[0], row[1], row[5]))
    for previous, current in zip(parsed, parsed[1:]):
        if current[1] <= previous[1]:
            raise RuntimeError("Odometer readings must strictly increase in chronological order.")
    totals_by_month = defaultdict(lambda: {"litres": Decimal("0"), "cost": Decimal("0"), "count": 0})
    total_litres = Decimal("0")
    total_cost = Decimal("0")
    intervals = []
    last_full_index = None
    for i, (day, odo, litres, price, full, original_index) in enumerate(parsed):
        cost = litres * price
        total_litres += litres
        total_cost += cost
        month = totals_by_month[day.strftime("%Y-%m")]
        month["litres"] += litres
        month["cost"] += cost
        month["count"] += 1
        if full:
            if last_full_index is not None:
                previous = parsed[last_full_index]
                distance = odo - previous[1]
                interval_litres = sum((row[2] for row in parsed[last_full_index + 1:i + 1]), Decimal("0"))
                interval_cost = sum((row[2] * row[3] for row in parsed[last_full_index + 1:i + 1]), Decimal("0"))
                if interval_litres > 0 and distance > 0:
                    intervals.append((previous[0], day, distance, interval_litres, interval_cost))
            last_full_index = i
    lines = [
        "Vehicle fuel log summary", f"Currency: {currency}",
        f"Fuel entries: {len(parsed)}", f"Total fuel: {_fmt(total_litres, 3)} L",
        f"Total fuel spend: {_fmt(total_cost)} {currency}",
        "Consumption is calculated only between consecutive full-tank entries. Partial-fill intervals are not compared in isolation.",
        "",
        "FULL-TANK CONSUMPTION INTERVALS",
    ]
    if not intervals:
        lines.append("- At least two full-tank entries are needed for a consumption interval.")
    for start, end, distance, litres, cost in intervals:
        l100 = litres / Decimal(distance) * 100
        kpl = Decimal(distance) / litres
        lines.append(f"- {start.isoformat()} to {end.isoformat()} | {distance:,} km | { _fmt(litres, 3)} L | {_fmt(l100, 2)} L/100 km | {_fmt(kpl, 2)} km/L | fuel cost {_fmt(cost)} {currency}")
    lines.extend(["", "MONTHLY FUEL SPEND"])
    for month, row in sorted(totals_by_month.items()):
        lines.append(f"- {month}: {_fmt(row['cost'])} {currency} | {_fmt(row['litres'], 3)} L | {row['count']} fill(s)")
    return _write(path, "vehicle-fuel-log", "\n".join(lines), f"Analysed {len(parsed)} fuel entries and {len(intervals)} full-tank consumption interval(s).")


def vehicle_ownership_cost_report(path: Path) -> dict:
    data = _read(path)
    currency = _currency(data.get("currency"))
    distance = _number(data.get("distance_km"), "distance_km", "0.001", 100_000_000)
    expenses = _list(data.get("expenses"), "expenses", 1, 5000)
    totals = defaultdict(lambda: {"amount": Decimal("0"), "count": 0})
    months = defaultdict(lambda: Decimal("0"))
    sum_total = Decimal("0")
    for i, raw in enumerate(expenses, 1):
        item = _row(raw, f"expense {i}")
        day = _date(item.get("date"), f"expense {i} date")
        name = _text(item.get("name"), f"expense {i} name", 120)
        category = _text(item.get("category"), f"{name} category", 80)
        amount = _money(item.get("amount"), f"{name} amount")
        totals[category]["amount"] += amount
        totals[category]["count"] += 1
        months[day.strftime("%Y-%m")] += amount
        sum_total += amount
    lines = [
        "Vehicle ownership cost report", f"Currency: {currency}",
        f"Distance covered in the reporting period: {_fmt(distance, 1)} km",
        f"Recorded expenses: {len(expenses)}",
        f"Total recorded running cost: {_fmt(sum_total)} {currency}",
        f"Recorded cost per kilometre: {_fmt(sum_total / distance, 4)} {currency}/km",
        "Only expenses entered in this file are included. Depreciation, finance, resale value and unlisted costs are not inferred.",
        "",
        "COST BY CATEGORY",
    ]
    for category, row in sorted(totals.items(), key=lambda p: (-p[1]["amount"], p[0].casefold())):
        lines.append(f"- {category}: {_fmt(row['amount'])} {currency} | {row['count']} record(s)")
    lines.extend(["", "MONTHLY COST"])
    for month, amount in sorted(months.items()):
        lines.append(f"- {month}: {_fmt(amount)} {currency}")
    return _write(path, "vehicle-ownership-cost", "\n".join(lines), f"Summarised {_fmt(sum_total)} {currency} over {_fmt(distance, 1)} km.")


def appliance_repair_replace_comparator(path: Path) -> dict:
    data = _read(path)
    name = _text(data.get("appliance_name"), "appliance_name", 120)
    currency = _currency(data.get("currency"))
    repair_cost = _money(data.get("repair_cost"), "repair_cost")
    remaining_years = _number(data.get("expected_years_after_repair"), "expected_years_after_repair", "0.1", 100)
    old_energy = _money(data.get("annual_energy_cost_after_repair"), "annual_energy_cost_after_repair")
    replacement_cost = _money(data.get("replacement_cost"), "replacement_cost")
    new_life = _number(data.get("replacement_expected_life_years"), "replacement_expected_life_years", "0.1", 100)
    new_energy = _money(data.get("replacement_annual_energy_cost"), "replacement_annual_energy_cost")
    repair_warranty = _integer(data.get("repair_warranty_months", 0), "repair_warranty_months", 0, 120)
    new_warranty = _integer(data.get("replacement_warranty_months", 0), "replacement_warranty_months", 0, 240)
    repair_annual = repair_cost / remaining_years + old_energy
    replace_annual = replacement_cost / new_life + new_energy
    delta = replace_annual - repair_annual
    energy_saving = old_energy - new_energy
    payback = None
    if energy_saving > 0 and replacement_cost > repair_cost:
        payback = (replacement_cost - repair_cost) / energy_saving
    lines = [
        "Appliance repair-versus-replace comparison", f"Appliance: {name}", f"Currency: {currency}",
        "",
        "REPAIR OPTION",
        f"- Repair cost now: {_fmt(repair_cost)} {currency}",
        f"- Expected years after repair (user estimate): {_fmt(remaining_years, 1)}",
        f"- Estimated annual energy cost: {_fmt(old_energy)} {currency}",
        f"- Repair warranty: {repair_warranty} month(s)",
        f"- Annualised cost proxy: {_fmt(repair_annual)} {currency}/year",
        "",
        "REPLACEMENT OPTION",
        f"- Replacement cost now: {_fmt(replacement_cost)} {currency}",
        f"- Expected product life (user estimate): {_fmt(new_life, 1)} years",
        f"- Estimated annual energy cost: {_fmt(new_energy)} {currency}",
        f"- Replacement warranty: {new_warranty} month(s)",
        f"- Annualised cost proxy: {_fmt(replace_annual)} {currency}/year",
        "",
        "COMPARISON",
    ]
    if delta < 0:
        lines.append(f"- Replacement has the lower annualised cost proxy by {_fmt(abs(delta))} {currency}/year under the entered assumptions.")
    elif delta > 0:
        lines.append(f"- Repair has the lower annualised cost proxy by {_fmt(delta)} {currency}/year under the entered assumptions.")
    else:
        lines.append("- The annualised cost proxies are equal under the entered assumptions.")
    if payback is not None:
        lines.append(f"- Estimated simple payback for the extra replacement purchase cost from energy savings alone: {_fmt(payback, 2)} years.")
    else:
        lines.append("- No positive energy-savings payback period can be calculated from the supplied values.")
    lines.extend(["", "This arithmetic comparison does not inspect appliance safety, reliability, repair quality, environmental impact, product features or actual lifespan. Confirm repair advice and warranty conditions with a qualified provider/manufacturer."])
    return _write(path, "appliance-repair-replace", "\n".join(lines), f"Compared annualised cost proxies for {name} under user-entered assumptions.")


def home_repair_quote_comparator(path: Path) -> dict:
    data = _read(path)
    project = _text(data.get("project_name"), "project_name", 120)
    currency = _currency(data.get("currency"))
    required = _list(data.get("required_work"), "required_work", 1, 100)
    requirements = {}
    for i, raw in enumerate(required, 1):
        item = _row(raw, f"required work {i}")
        work_id = _text(item.get("id"), f"required work {i} id", 40)
        if work_id in requirements:
            raise RuntimeError("Required work IDs must be unique.")
        requirements[work_id] = _text(item.get("description"), f"required work {i} description", 160)
    quotes = _list(data.get("quotes"), "quotes", 1, 30)
    results = []
    for i, raw in enumerate(quotes, 1):
        item = _row(raw, f"quote {i}")
        provider = _text(item.get("provider"), f"quote {i} provider", 120)
        labour = _money(item.get("labour_cost", 0), f"{provider} labour_cost")
        materials = _money(item.get("materials_cost", 0), f"{provider} materials_cost")
        fees = _money(item.get("other_fees", 0), f"{provider} other_fees")
        tax_percent = _number(item.get("tax_percent", 0), f"{provider} tax_percent", 0, 100)
        subtotal = labour + materials + fees
        tax = (subtotal * tax_percent / 100).quantize(CENT, rounding=ROUND_HALF_UP)
        total = subtotal + tax
        included = item.get("included_work_ids", [])
        excluded = item.get("excluded_work", [])
        if not isinstance(included, list) or any(not isinstance(v, str) for v in included):
            raise RuntimeError(f"{provider}: included_work_ids must be a list of IDs.")
        if len(set(included)) != len(included) or any(v not in requirements for v in included):
            raise RuntimeError(f"{provider}: included_work_ids contains duplicate or unknown IDs.")
        if not isinstance(excluded, list) or len(excluded) > 100:
            raise RuntimeError(f"{provider}: excluded_work must be a list of up to 100 items.")
        excluded = [_text(v, f"{provider} exclusion", 160) for v in excluded]
        warranty = _integer(item.get("workmanship_warranty_months", 0), f"{provider} workmanship_warranty_months", 0, 120)
        days = _integer(item.get("estimated_days", 0), f"{provider} estimated_days", 0, 730)
        results.append({
            "provider": provider, "labour": labour, "materials": materials, "fees": fees, "tax": tax,
            "total": total, "included": set(included), "missing": sorted(set(requirements) - set(included)),
            "excluded": excluded, "warranty": warranty, "days": days,
        })
    results.sort(key=lambda row: (-len(row["included"]), row["total"], row["provider"].casefold()))
    lines = [
        "Home repair quote comparison", f"Project: {project}", f"Currency: {currency}",
        f"Required scope items: {len(requirements)}",
        "Quotes are compared using only the amounts and scope details supplied. A lower price does not establish better workmanship or suitability.",
        "",
    ]
    for idx, quote in enumerate(results, 1):
        lines.extend([
            f"{idx}. {quote['provider']} — {_fmt(quote['total'])} {currency}",
            f"- Labour: {_fmt(quote['labour'])}; materials: {_fmt(quote['materials'])}; other fees: {_fmt(quote['fees'])}; entered tax: {_fmt(quote['tax'])}",
            f"- Scope included: {len(quote['included'])}/{len(requirements)}",
            f"- Workmanship warranty entered: {quote['warranty']} month(s); estimated duration: {quote['days']} day(s)",
        ])
        if quote["missing"]:
            lines.append("- Required items not marked included: " + ", ".join(f"{key} ({requirements[key]})" for key in quote["missing"]))
        if quote["excluded"]:
            lines.append("- Explicit exclusions: " + "; ".join(quote["excluded"]))
        lines.append("")
    lines.append("Ask each provider to clarify missing scope, materials/brands, permits, cleanup, payment milestones, change orders and warranty terms before deciding.")
    return _write(path, "home-repair-quotes", "\n".join(lines), f"Compared {len(results)} quotes for {project}.")


def _condition(value, label):
    result = str(value).strip().lower()
    if result not in CONDITIONS:
        raise RuntimeError(f"{label} must be one of: {', '.join(sorted(CONDITIONS))}.")
    return result


def rental_move_in_inspection_report(path: Path) -> dict:
    data = _read(path)
    property_name = _text(data.get("property"), "property", 160)
    tenant = _text(data.get("tenant"), "tenant", 120)
    landlord = _text(data.get("landlord_or_agent"), "landlord_or_agent", 120)
    day = _date(data.get("inspection_date"), "inspection_date")
    checks = _list(data.get("checks"), "checks", 1, 500)
    parsed = []
    for i, raw in enumerate(checks, 1):
        item = _row(raw, f"check {i}")
        area = _text(item.get("area"), f"check {i} area", 80)
        name = _text(item.get("item"), f"check {i} item", 120)
        condition = _condition(item.get("condition"), f"{area}/{name} condition")
        note = " ".join(str(item.get("note", "")).split()).strip()[:400]
        evidence = item.get("evidence_refs", [])
        if not isinstance(evidence, list) or len(evidence) > 20:
            raise RuntimeError(f"{area}/{name}: evidence_refs must be a list of up to 20 labels.")
        evidence = [_text(v, "evidence reference", 120) for v in evidence]
        parsed.append((area, name, condition, note, evidence))
    meters = data.get("meter_readings", [])
    if not isinstance(meters, list) or len(meters) > 50:
        raise RuntimeError("meter_readings must be a list of up to 50 readings.")
    meter_rows = []
    for i, raw in enumerate(meters, 1):
        item = _row(raw, f"meter reading {i}")
        meter_rows.append((_text(item.get("utility"), "meter utility", 60),
                           _text(item.get("reading"), "meter reading", 80),
                           _text(item.get("unit"), "meter unit", 30)))
    parsed.sort(key=lambda row: (row[0].casefold(), row[1].casefold()))
    counts = defaultdict(int)
    lines = [
        "Rental move-in condition report", f"Property: {property_name}",
        f"Tenant: {tenant} | Landlord/agent: {landlord}", f"Inspection date: {day.isoformat()}",
        "This report records observations entered by the user at inspection time. Attach and retain the original evidence separately.",
        "",
        "ROOM-BY-ROOM CHECKS",
    ]
    for area, name, condition, note, evidence in parsed:
        counts[condition] += 1
        lines.append(f"- {area} | {name} | {condition}")
        if note:
            lines.append("  Note: " + note)
        if evidence:
            lines.append("  Evidence references: " + ", ".join(evidence))
    lines.extend(["", "METER READINGS"])
    if meter_rows:
        lines.extend(f"- {utility}: {reading} {unit}" for utility, reading, unit in meter_rows)
    else:
        lines.append("- None recorded.")
    lines.extend(["", "CONDITION SUMMARY"])
    for condition in sorted(CONDITIONS):
        lines.append(f"- {condition}: {counts[condition]}")
    lines.extend(["", "Review this record together, note any disagreement and keep dated photographs/videos and signed copies with the tenancy documents. This report does not determine responsibility for damage or deposit rights."])
    return _write(path, "rental-move-in-inspection", "\n".join(lines), f"Recorded {len(parsed)} condition checks for {property_name}.")


def rental_move_out_condition_report(path: Path) -> dict:
    data = _read(path)
    property_name = _text(data.get("property"), "property", 160)
    tenant = _text(data.get("tenant"), "tenant", 120)
    move_in_date = _date(data.get("move_in_date"), "move_in_date")
    move_out_date = _date(data.get("move_out_date"), "move_out_date")
    if move_out_date < move_in_date:
        raise RuntimeError("move_out_date cannot be before move_in_date.")
    baseline = _list(data.get("move_in_checks"), "move_in_checks", 1, 500)
    exit_checks = _list(data.get("move_out_checks"), "move_out_checks", 1, 500)
    def index(items, label):
        result = {}
        for i, raw in enumerate(items, 1):
            item = _row(raw, f"{label} {i}")
            key = _text(item.get("id"), f"{label} {i} id", 60)
            if key in result:
                raise RuntimeError(f"{label} contains duplicate item IDs.")
            result[key] = (
                _text(item.get("area"), f"{label} area", 80),
                _text(item.get("item"), f"{label} item", 120),
                _condition(item.get("condition"), f"{label} condition"),
                " ".join(str(item.get("note", "")).split()).strip()[:400],
            )
        return result
    before = index(baseline, "move_in_check")
    after = index(exit_checks, "move_out_check")
    proposed = data.get("proposed_deductions", [])
    if not isinstance(proposed, list) or len(proposed) > 200:
        raise RuntimeError("proposed_deductions must be a list of up to 200 entries.")
    currency = _currency(data.get("currency", "VND"))
    deposit = _money(data.get("deposit_amount", 0), "deposit_amount")
    deduction_total = Decimal("0")
    deduction_rows = []
    for i, raw in enumerate(proposed, 1):
        item = _row(raw, f"deduction {i}")
        desc = _text(item.get("description"), f"deduction {i} description", 160)
        amount = _money(item.get("amount"), f"deduction {i} amount")
        deduction_total += amount
        deduction_rows.append((desc, amount))
    changes = []
    for key in sorted(set(before) | set(after)):
        old = before.get(key)
        new = after.get(key)
        if old is None:
            changes.append((key, "Added at move-out", None, new))
        elif new is None:
            changes.append((key, "Not inspected at move-out", old, None))
        elif old[2] == new[2]:
            changes.append((key, "Same recorded condition", old, new))
        else:
            changes.append((key, "Condition label changed", old, new))
    lines = [
        "Rental move-out condition comparison", f"Property: {property_name}",
        f"Tenant: {tenant}", f"Move-in inspection: {move_in_date.isoformat()}",
        f"Move-out inspection: {move_out_date.isoformat()}",
        "This is a comparison of user-entered labels, not a finding about cause, fair wear and tear or legal responsibility.",
        "",
        "ITEM-BY-ITEM COMPARISON",
    ]
    for key, status, old, new in changes:
        if old is None:
            lines.append(f"- {key} | {status} | move-out: {new[0]} / {new[1]} / {new[2]} — {new[3]}")
        elif new is None:
            lines.append(f"- {key} | {status} | move-in: {old[0]} / {old[1]} / {old[2]} — {old[3]}")
        else:
            lines.append(f"- {key} | {status} | move-in {old[2]} → move-out {new[2]}")
            if old[3] or new[3]:
                lines.append(f"  Move-in note: {old[3] or '(none)'} | Move-out note: {new[3] or '(none)'}")
    lines.extend(["", "USER-ENTERED DEPOSIT FIGURES"])
    lines.append(f"- Deposit amount: {_fmt(deposit)} {currency}")
    lines.append(f"- Proposed deductions: {_fmt(deduction_total)} {currency}")
    lines.append(f"- Arithmetic remainder: {_fmt(deposit - deduction_total)} {currency}")
    for desc, amount in deduction_rows:
        lines.append(f"  - {desc}: {_fmt(amount)} {currency}")
    lines.extend(["", "Request itemised explanations and supporting evidence for any proposed deductions. Check the signed agreement and local rules; this arithmetic report does not decide lawful deposit deductions."])
    return _write(path, "rental-move-out-comparison", "\n".join(lines), f"Compared {len(changes)} inventory item(s) for {property_name}.")


def rental_offer_cost_comparator(path: Path) -> dict:
    data = _read(path)
    currency = _currency(data.get("currency"))
    months = _integer(data.get("lease_months"), "lease_months", 1, 120)
    offers = _list(data.get("offers"), "offers", 1, 50)
    results = []
    for i, raw in enumerate(offers, 1):
        item = _row(raw, f"offer {i}")
        name = _text(item.get("name"), f"offer {i} name", 120)
        rent = _money(item.get("monthly_rent"), f"{name} monthly_rent")
        utilities = _money(item.get("monthly_utilities", 0), f"{name} monthly_utilities")
        recurring_fees = _money(item.get("monthly_fees", 0), f"{name} monthly_fees")
        deposit = _money(item.get("refundable_deposit", 0), f"{name} refundable_deposit")
        nonrefundable = _money(item.get("one_time_nonrefundable_fees", 0), f"{name} one_time_nonrefundable_fees")
        move_cost = _money(item.get("move_in_costs", 0), f"{name} move_in_costs")
        monthly = rent + utilities + recurring_fees
        lease_cost = monthly * months + nonrefundable + move_cost
        cash_needed = monthly + deposit + nonrefundable + move_cost
        results.append((name, rent, utilities, recurring_fees, monthly, deposit, nonrefundable, move_cost, lease_cost, cash_needed))
    results.sort(key=lambda row: (row[8], row[0].casefold()))
    lines = [
        "Rental offer cost comparison", f"Currency: {currency}",
        f"Comparison period: {months} month(s)",
        "Recurring costs and one-off costs are compared separately. Refundable deposits count as cash required up front, not as a lease expense in the total-cost comparison.",
        "",
    ]
    for i, row in enumerate(results, 1):
        name, rent, utilities, fees, monthly, deposit, nonrefundable, move_cost, lease_cost, cash_needed = row
        lines.extend([
            f"{i}. {name}",
            f"- Monthly rent: {_fmt(rent)} | utilities: {_fmt(utilities)} | recurring fees: {_fmt(fees)}",
            f"- Estimated recurring monthly total: {_fmt(monthly)} {currency}",
            f"- Refundable deposit: {_fmt(deposit)} {currency}",
            f"- Non-refundable one-time fees: {_fmt(nonrefundable)} {currency} | move-in costs: {_fmt(move_cost)} {currency}",
            f"- Cash required at start (one month + deposit + one-off costs): {_fmt(cash_needed)} {currency}",
            f"- Estimated {months}-month cost excluding refundable deposit: {_fmt(lease_cost)} {currency}",
            "",
        ])
    if len(results) > 1:
        lines.append(f"Lowest entered {months}-month cost: {results[0][0]} ({_fmt(results[0][8])} {currency}); this does not assess location, property condition, landlord, lease clauses or suitability.")
    return _write(path, "rental-offer-costs", "\n".join(lines), f"Compared {len(results)} rental offers over {months} month(s).")


def appliance_service_history_report(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    appliances = _list(data.get("appliances"), "appliances", 1, 200)
    rows = []
    for i, raw in enumerate(appliances, 1):
        item = _row(raw, f"appliance {i}")
        name = _text(item.get("name"), f"appliance {i} name", 120)
        category = " ".join(str(item.get("category", "General")).split()).strip()[:80] or "General"
        currency = _currency(item.get("currency", "VND"))
        purchase_date = _date(item.get("purchase_date"), f"{name} purchase_date")
        warranty_months = _integer(item.get("warranty_months", 0), f"{name} warranty_months", 0, 120)
        warranty_end = _month_add(purchase_date, warranty_months)
        service = item.get("service_entries", [])
        if not isinstance(service, list) or len(service) > 100:
            raise RuntimeError(f"{name}: service_entries must contain up to 100 entries.")
        total = Decimal("0")
        downtime = 0
        latest = None
        types = defaultdict(int)
        for j, entry_raw in enumerate(service, 1):
            entry = _row(entry_raw, f"{name} service entry {j}")
            day = _date(entry.get("date"), f"{name} service entry {j} date")
            if day > as_of:
                raise RuntimeError(f"{name}: a service entry cannot be after as_of_date.")
            event = _text(entry.get("event"), f"{name} service event", 120)
            cost = _money(entry.get("cost", 0), f"{name} service cost")
            days = _integer(entry.get("downtime_days", 0), f"{name} downtime_days", 0, 3650)
            total += cost
            downtime += days
            types[event] += 1
            latest = day if latest is None or day > latest else latest
        next_due = _date(item["next_service_due"], f"{name} next_service_due") if item.get("next_service_due") else None
        rows.append((name, category, currency, purchase_date, warranty_end, total, downtime, len(service), latest, dict(types), next_due))
    rows.sort(key=lambda row: (row[1].casefold(), row[0].casefold()))
    lines = [
        "Appliance service history report", f"As of: {as_of.isoformat()}",
        "Service costs, events and warranty durations are user-entered. Estimated warranty end dates do not establish coverage.",
        "",
    ]
    for name, category, currency, purchase, warranty_end, total, downtime, count, latest, types, next_due in rows:
        warranty_status = "within entered warranty dates" if as_of <= warranty_end else "entered warranty end date passed"
        lines.extend([
            f"{name} | {category}",
            f"- Purchased: {purchase.isoformat()} | estimated warranty end: {warranty_end.isoformat()} ({warranty_status})",
            f"- Service records: {count} | recorded service spend: {_fmt(total)} {currency} | recorded downtime: {downtime} day(s)",
            f"- Latest service entry: {latest.isoformat() if latest else 'none recorded'}",
        ])
        if types:
            lines.append("- Event types: " + ", ".join(f"{key} ({value})" for key, value in sorted(types.items())))
        if next_due:
            lines.append(f"- Next service date entered: {next_due.isoformat()} ({'due/overdue' if next_due <= as_of else 'upcoming'})")
        lines.append("")
    return _write(path, "appliance-service-history", "\n".join(lines), f"Summarised service history for {len(rows)} appliance(s).")
