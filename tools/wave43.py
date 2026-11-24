"""Wave 43 home, hobby and learning tools for everyday Nolane users.

All dates, care intervals, prices, room sizes and event constraints are
provided by the user. These utilities are deterministic and do not fetch live
weather, plant, veterinary or market recommendations.
"""
from __future__ import annotations

import calendar
import json
import math
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

MAX_JSON_BYTES = 1 * 1024 * 1024
MAX_ITEMS = 300


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key.")
        result[key] = value
    return result


def _read(path: Path) -> dict:
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            raise RuntimeError("Request exceeds the 1 MiB JSON limit.")
        value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_pairs)
    except RuntimeError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError("Upload a valid UTF-8 JSON object.") from exc
    if not isinstance(value, dict):
        raise RuntimeError("Request must be one JSON object.")
    return value


def _text(value, label: str, maximum: int = 120) -> str:
    if not isinstance(value, str):
        raise RuntimeError(f"{label} must be text.")
    result = " ".join(value.split()).strip()
    if not result or len(result) > maximum:
        raise RuntimeError(f"{label} must contain 1 to {maximum} characters.")
    return result


def _number(value, label: str, minimum=0, maximum=1_000_000_000) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise RuntimeError(f"{label} must be a number.")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        raise RuntimeError(f"{label} must be a number.") from None
    if not result.is_finite() or result < Decimal(str(minimum)) or result > Decimal(str(maximum)):
        raise RuntimeError(f"{label} must be finite and between {minimum} and {maximum}.")
    return result


def _integer(value, label: str, minimum: int, maximum: int) -> int:
    result = _number(value, label, minimum, maximum)
    if result != result.to_integral_value():
        raise RuntimeError(f"{label} must be a whole number.")
    return int(result)


def _date(value, label: str) -> date:
    raw = _text(value, label, 10)
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        raise RuntimeError(f"{label} must use YYYY-MM-DD.") from None
    if parsed.isoformat() != raw:
        raise RuntimeError(f"{label} must use YYYY-MM-DD.")
    return parsed


def _currency(value, default="VND") -> str:
    result = str(value or default).strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", result):
        raise RuntimeError("currency must be a three-letter code such as VND, USD or EUR.")
    return result


def _minor_units(currency: str) -> int:
    if currency in {"BIF", "CLP", "DJF", "GNF", "ISK", "JPY", "KMF", "KRW", "PYG", "RWF", "UGX", "UYI", "VND", "VUV", "XAF", "XOF", "XPF"}:
        return 0
    if currency in {"BHD", "IQD", "JOD", "KWD", "LYD", "OMR", "TND"}:
        return 3
    return 2


def _money(value: Decimal, currency: str) -> Decimal:
    places = _minor_units(currency)
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def _money_text(value: Decimal, currency: str) -> str:
    places = _minor_units(currency)
    return f"{_money(value, currency):.{places}f}"


def _month_add(value: date, months: int) -> date:
    absolute = value.year * 12 + (value.month - 1) + months
    year, month_zero = divmod(absolute, 12)
    month = month_zero + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _write(path: Path, suffix: str, body: str, summary: str) -> dict:
    output = path.with_name((path.stem[:64] or "nolane") + "-" + suffix + ".txt")
    output.write_text(body.rstrip() + "\n", encoding="utf-8")
    return {"summary": summary[:500], "output_path": str(output)}


def habit_history_analyzer(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    window = _integer(data.get("window_days", 30), "window_days", 7, 365)
    habits = data.get("habits")
    if not isinstance(habits, list) or not 1 <= len(habits) <= 100:
        raise RuntimeError("habits must contain 1 to 100 habit objects.")
    start = as_of - timedelta(days=window - 1)
    lines = ["Habit history report", f"As of: {as_of.isoformat()}", f"Review window: {window} days", ""]
    for item in habits:
        if not isinstance(item, dict):
            raise RuntimeError("Each habit must be an object.")
        name = _text(item.get("name"), "habit name", 100)
        target = _integer(item.get("target_days_per_week", 7), "target_days_per_week", 1, 7)
        raw_dates = item.get("check_ins")
        if not isinstance(raw_dates, list) or len(raw_dates) > 2000:
            raise RuntimeError(f"{name}: check_ins must be a list of up to 2,000 dates.")
        dates = {_date(value, f"{name} check-in date") for value in raw_dates}
        if any(value > as_of for value in dates):
            raise RuntimeError(f"{name}: check-in dates cannot be after as_of_date.")
        recent = sorted(value for value in dates if start <= value <= as_of)
        required = math.ceil(Decimal(window) * Decimal(target) / Decimal(7))
        completion = min(100, int((Decimal(len(recent)) / Decimal(required) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
        longest = current = 0
        previous = None
        for value in sorted(dates):
            current = current + 1 if previous and value == previous + timedelta(days=1) else 1
            longest = max(longest, current)
            previous = value
        cursor = as_of if as_of in dates else as_of - timedelta(days=1)
        current_streak = 0
        while cursor in dates:
            current_streak += 1
            cursor -= timedelta(days=1)
        last = max(dates) if dates else None
        lines.extend([
            name,
            f"- Target: {target} check-in day(s) per week",
            f"- Check-ins in window: {len(recent)} / {required} target",
            f"- Target completion: {completion}%",
            f"- Current streak: {current_streak} day(s)",
            f"- Longest recorded streak: {longest} day(s)",
            f"- Last check-in: {last.isoformat() if last else 'none recorded'}",
            "",
        ])
    lines.append("Check-ins are user supplied. The report does not infer missed days before the recorded history.")
    return _write(path, "habit-history", "\n".join(lines), f"Analysed {len(habits)} habits over {window} days.")


def plant_care_scheduler(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    window = _integer(data.get("window_days", 30), "window_days", 1, 180)
    plants = data.get("plants")
    if not isinstance(plants, list) or not 1 <= len(plants) <= 100:
        raise RuntimeError("plants must contain 1 to 100 plant objects.")
    due_rows = []
    task_count = 0
    for plant in plants:
        if not isinstance(plant, dict):
            raise RuntimeError("Each plant must be an object.")
        plant_name = _text(plant.get("name"), "plant name", 100)
        tasks = plant.get("care_tasks")
        if not isinstance(tasks, list) or not 1 <= len(tasks) <= 20:
            raise RuntimeError(f"{plant_name}: care_tasks must contain 1 to 20 tasks.")
        for task in tasks:
            task_count += 1
            if task_count > MAX_ITEMS:
                raise RuntimeError("Combined care-task count exceeds 300.")
            if not isinstance(task, dict):
                raise RuntimeError("Each care task must be an object.")
            task_name = _text(task.get("task"), "care task", 60)
            last_done = _date(task.get("last_done"), "last_done")
            interval = _integer(task.get("every_days"), "every_days", 1, 3650)
            due = last_done + timedelta(days=interval)
            overdue_days = max(0, (as_of - due).days)
            due_rows.append((due, plant_name, task_name, interval, overdue_days, last_done))
    due_rows.sort(key=lambda x: (x[0], x[1].casefold(), x[2].casefold()))
    end = as_of + timedelta(days=window)
    lines = ["Plant care schedule", f"As of: {as_of.isoformat()}", f"Planning window: {window} days",
             "Intervals are entered by the user; no species or weather recommendations are implied.", ""]
    for due, plant, task, interval, overdue, last_done in due_rows:
        status = f"OVERDUE by {overdue} day(s)" if due < as_of else ("Due today" if due == as_of else "Upcoming")
        if due <= end:
            lines.append(f"- {due.isoformat()} | {plant} | {task} | every {interval} day(s) | {status}")
        else:
            lines.append(f"- {plant} | {task} | next due {due.isoformat()} (outside this window)")
    if not due_rows:
        lines.append("No care tasks were supplied.")
    return _write(path, "plant-care-schedule", "\n".join(lines),
                  f"Scheduled {len(due_rows)} plant-care reminders.")


def garden_bed_capacity_calculator(path: Path) -> dict:
    data = _read(path)
    beds = data.get("beds")
    if not isinstance(beds, list) or not 1 <= len(beds) <= 50:
        raise RuntimeError("beds must contain 1 to 50 garden beds.")
    lines = ["Garden bed planting capacity", "Estimates use rectangular beds and even row/plant spacing.", ""]
    total_plants = 0
    total_area = Decimal("0")
    for bed in beds:
        if not isinstance(bed, dict):
            raise RuntimeError("Each bed must be an object.")
        name = _text(bed.get("name"), "bed name", 80)
        length = _number(bed.get("length_m"), "length_m", "0.05", 1000)
        width = _number(bed.get("width_m"), "width_m", "0.05", 1000)
        plant_spacing = _number(bed.get("plant_spacing_cm"), "plant_spacing_cm", "1", 5000)
        row_spacing = _number(bed.get("row_spacing_cm"), "row_spacing_cm", "1", 5000)
        margin = _number(bed.get("edge_margin_cm", 0), "edge_margin_cm", 0, 500)
        usable_length = length * 100 - margin * 2
        usable_width = width * 100 - margin * 2
        if usable_length <= 0 or usable_width <= 0:
            raise RuntimeError(f"{name}: edge margin leaves no usable planting area.")
        plants_per_row = max(0, int(usable_length // plant_spacing))
        rows = max(0, int(usable_width // row_spacing))
        count = plants_per_row * rows
        area = length * width
        total_plants += count
        total_area += area
        lines.extend([
            f"{name}",
            f"- Bed size: {_money(length * width, 'XXX')} m²",
            f"- Rows: {rows}",
            f"- Plants per row: {plants_per_row}",
            f"- Estimated capacity: {count} plant(s)",
            "",
        ])
    lines.append(f"Total garden area: {total_area.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} m²")
    lines.append(f"Estimated total planting capacity: {total_plants} plant(s)")
    lines.append("Actual capacity varies with access paths, plant shape, growth habit and local growing guidance.")
    return _write(path, "garden-bed-capacity", "\n".join(lines),
                  f"Estimated planting capacity: {total_plants} plants across {len(beds)} bed(s).")


def home_inventory_report(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        raise RuntimeError("items must contain 1 to 300 inventory items.")
    totals = defaultdict(lambda: Decimal("0"))
    category_totals = defaultdict(lambda: Decimal("0"))
    lines = ["Home inventory report", f"As of: {as_of.isoformat()}", f"Items: {len(items)}", ""]
    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError("Each inventory item must be an object.")
        name = _text(item.get("name"), "item name", 100)
        category = _text(item.get("category", "Other"), "category", 50)
        quantity = _integer(item.get("quantity", 1), "quantity", 1, 1_000_000)
        unit_price = _number(item.get("purchase_price_per_item", 0), "purchase_price_per_item", 0, "1000000000000")
        currency = _currency(item.get("currency"), str(data.get("currency", "VND")))
        subtotal = (unit_price * quantity).quantize(Decimal(1).scaleb(-_minor_units(currency)), rounding=ROUND_HALF_UP)
        totals[currency] += subtotal
        category_totals[(currency, category)] += subtotal
        purchase_date = _date(item.get("purchase_date"), "purchase_date")
        if purchase_date > as_of:
            raise RuntimeError(f"{name}: purchase_date cannot be after as_of_date.")
        lines.append(f"- {name} ({category}) × {quantity}: {currency} {_money_text(subtotal, currency)}")
        warranty_months = item.get("warranty_months")
        if warranty_months is not None:
            warranty = _month_add(purchase_date, _integer(warranty_months, "warranty_months", 0, 600))
            state = "active" if warranty >= as_of else "expired"
            lines.append(f"  Warranty: {state}; through {warranty.isoformat()}")
        life_months = item.get("expected_life_months")
        if life_months is not None:
            end_of_life = _month_add(purchase_date, _integer(life_months, "expected_life_months", 1, 1200))
            lines.append(f"  Expected service-life date entered by user: {end_of_life.isoformat()}")
        if item.get("location") is not None:
            lines.append("  Location: " + _text(item.get("location"), "location", 80))
    lines.extend(["", "Value by currency"])
    for currency in sorted(totals):
        lines.append(f"- {currency}: {currency} {_money_text(totals[currency], currency)}")
    lines.append("")
    for (currency, category), amount in sorted(category_totals.items()):
        lines.append(f"- {category} ({currency}): {currency} {_money_text(amount, currency)}")
    lines.append("Purchase values are historical user-entered amounts, not current resale values or insurance valuations.")
    return _write(path, "home-inventory", "\n".join(lines),
                  f"Summarised {len(items)} home inventory item(s) across {len(totals)} currency group(s).")


def home_maintenance_scheduler(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    window = _integer(data.get("window_days", 90), "window_days", 1, 730)
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 200:
        raise RuntimeError("tasks must contain 1 to 200 maintenance tasks.")
    rows = []
    for task in tasks:
        if not isinstance(task, dict):
            raise RuntimeError("Each maintenance task must be an object.")
        name = _text(task.get("name"), "task name", 100)
        last_done = _date(task.get("last_completed"), "last_completed")
        if last_done > as_of:
            raise RuntimeError(f"{name}: last_completed cannot be after as_of_date.")
        interval = _integer(task.get("every_days"), "every_days", 1, 3650)
        minutes = _integer(task.get("estimated_minutes", 30), "estimated_minutes", 1, 1440)
        priority = _integer(task.get("priority", 3), "priority", 1, 5)
        due = last_done + timedelta(days=interval)
        overdue = (as_of - due).days if due < as_of else 0
        next_occurrence = due
        while next_occurrence < as_of:
            next_occurrence += timedelta(days=interval)
        rows.append((due, next_occurrence, name, interval, minutes, priority, overdue))
    rows.sort(key=lambda x: (x[0], -x[5], x[2].casefold()))
    end = as_of + timedelta(days=window)
    lines = ["Home maintenance schedule", f"As of: {as_of.isoformat()}",
             f"Planning window: {window} days", "Intervals and estimated times are supplied by the user.", ""]
    for due, next_occurrence, name, interval, minutes, priority, overdue in rows:
        if due <= as_of:
            lines.append(f"- {name}: OVERDUE since {due.isoformat()} by {overdue} day(s); next cycle {next_occurrence.isoformat()} | priority {priority} | {minutes} min")
        elif due <= end:
            lines.append(f"- {due.isoformat()} | {name} | every {interval} day(s) | priority {priority} | {minutes} min")
        else:
            lines.append(f"- {name}: next due {due.isoformat()} (outside this window)")
    due_soon = [row for row in rows if as_of <= row[0] <= end]
    lines.extend(["", f"Tasks due in this window: {len(due_soon)}",
                  f"Estimated minutes for non-overdue tasks due in this window: {sum(row[4] for row in due_soon)}"])
    return _write(path, "home-maintenance", "\n".join(lines),
                  f"Prepared {len(rows)} home maintenance tasks.")


def pet_routine_planner(path: Path) -> dict:
    data = _read(path)
    start = _date(data.get("start_date"), "start_date")
    days = _integer(data.get("days", 7), "days", 1, 31)
    pets = data.get("pets")
    if not isinstance(pets, list) or not 1 <= len(pets) <= 30:
        raise RuntimeError("pets must contain 1 to 30 pets.")
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    schedule = defaultdict(list)
    task_count = 0
    for pet in pets:
        if not isinstance(pet, dict):
            raise RuntimeError("Each pet must be an object.")
        pet_name = _text(pet.get("name"), "pet name", 80)
        routines = pet.get("routines")
        if not isinstance(routines, list) or not 1 <= len(routines) <= 30:
            raise RuntimeError(f"{pet_name}: routines must contain 1 to 30 entries.")
        for routine in routines:
            task_count += 1
            if task_count > MAX_ITEMS:
                raise RuntimeError("Total pet routines exceed 300.")
            if not isinstance(routine, dict):
                raise RuntimeError("Each pet routine must be an object.")
            task = _text(routine.get("task"), "routine task", 80)
            time_text = _text(routine.get("time", "09:00"), "routine time", 5)
            try:
                datetime.strptime(time_text, "%H:%M")
            except ValueError:
                raise RuntimeError("routine time must use HH:MM.") from None
            selected = routine.get("days_of_week", day_names)
            if not isinstance(selected, list) or not 1 <= len(selected) <= 7:
                raise RuntimeError("days_of_week must contain 1 to 7 weekday names.")
            try:
                weekdays = {day_names.index(str(value).strip()[:3].title()) for value in selected}
            except ValueError:
                raise RuntimeError("days_of_week must use Mon, Tue, Wed, Thu, Fri, Sat or Sun.") from None
            note = routine.get("note")
            note_text = _text(note, "routine note", 120) if note is not None else ""
            for offset in range(days):
                current = start + timedelta(days=offset)
                if current.weekday() in weekdays:
                    schedule[current].append((time_text, pet_name, task, note_text))
    lines = ["Pet routine checklist", f"Start date: {start.isoformat()}", f"Planning horizon: {days} days",
             "Only non-medical daily care routines are included. Follow veterinary instructions for medical care.", ""]
    for current in sorted(schedule):
        lines.append(f"{current.isoformat()} ({day_names[current.weekday()]})")
        for time_text, pet, task, note in sorted(schedule[current]):
            row = f"- [ ] {time_text} | {pet} | {task}"
            if note:
                row += " — " + note
            lines.append(row)
        lines.append("")
    if not schedule:
        lines.append("No routine occurrences fall within this planning window.")
    return _write(path, "pet-routines", "\n".join(lines),
                  f"Generated {sum(len(rows) for rows in schedule.values())} pet-care checklist item(s).")


def event_seating_planner(path: Path) -> dict:
    data = _read(path)
    tables = data.get("tables")
    groups = data.get("guest_groups")
    avoid_pairs = data.get("avoid_pairs", [])
    if not isinstance(tables, list) or not 1 <= len(tables) <= 100:
        raise RuntimeError("tables must contain 1 to 100 tables.")
    if not isinstance(groups, list) or not 1 <= len(groups) <= 300:
        raise RuntimeError("guest_groups must contain 1 to 300 groups.")
    if not isinstance(avoid_pairs, list) or len(avoid_pairs) > 500:
        raise RuntimeError("avoid_pairs must be a list of up to 500 pairs.")
    parsed_tables = []
    table_names = set()
    for table in tables:
        if not isinstance(table, dict):
            raise RuntimeError("Each table must be an object.")
        name = _text(table.get("name"), "table name", 80)
        if name.casefold() in table_names:
            raise RuntimeError("Table names must be unique.")
        table_names.add(name.casefold())
        capacity = _integer(table.get("seats"), "table seats", 1, 100)
        parsed_tables.append({"name": name, "capacity": capacity, "guests": []})
    parsed_groups = []
    all_guests = set()
    for group in groups:
        if not isinstance(group, dict):
            raise RuntimeError("Each guest group must be an object.")
        name = _text(group.get("name"), "guest group name", 80)
        guests = group.get("guests")
        if not isinstance(guests, list) or not 1 <= len(guests) <= 100:
            raise RuntimeError(f"{name}: guests must contain 1 to 100 names.")
        clean = [_text(guest, "guest name", 80) for guest in guests]
        if len({guest.casefold() for guest in clean}) != len(clean):
            raise RuntimeError(f"{name}: guest names must be unique inside the group.")
        for guest in clean:
            key = guest.casefold()
            if key in all_guests:
                raise RuntimeError(f"Guest appears more than once: {guest}.")
            all_guests.add(key)
        parsed_groups.append({"name": name, "guests": clean})
    blocked = set()
    for pair in avoid_pairs:
        if not isinstance(pair, list) or len(pair) != 2:
            raise RuntimeError("Each avoid_pairs entry must contain exactly two guest names.")
        a = _text(pair[0], "avoid guest name", 80).casefold()
        b = _text(pair[1], "avoid guest name", 80).casefold()
        if a == b or a not in all_guests or b not in all_guests:
            raise RuntimeError("Avoid pairs must name two different guests in the guest list.")
        blocked.add(frozenset((a, b)))
    parsed_groups.sort(key=lambda group: (-len(group["guests"]), group["name"].casefold()))
    unassigned = []
    for group in parsed_groups:
        group_keys = {guest.casefold() for guest in group["guests"]}
        options = []
        for index, table in enumerate(parsed_tables):
            remaining = table["capacity"] - len(table["guests"])
            if remaining < len(group["guests"]):
                continue
            seated = {guest.casefold() for guest in table["guests"]}
            conflict = any(frozenset((guest, other)) in blocked for guest in group_keys for other in seated)
            if not conflict:
                options.append((remaining - len(group["guests"]), index))
        if not options:
            unassigned.append(group)
            continue
        _, selected = min(options)
        parsed_tables[selected]["guests"].extend(group["guests"])
    lines = ["Event seating plan", f"Guests: {len(all_guests)}",
             f"Tables: {len(parsed_tables)}", "Each guest group is kept together; avoid pairs are never assigned to the same table.", ""]
    assigned = 0
    for table in parsed_tables:
        guests = table["guests"]
        assigned += len(guests)
        lines.append(f"{table['name']} — {len(guests)}/{table['capacity']} seats")
        for guest in guests:
            lines.append("- " + guest)
        lines.append("")
    lines.extend([f"Assigned guests: {assigned}/{len(all_guests)}",
                  f"Unassigned guests: {sum(len(group['guests']) for group in unassigned)}"])
    if unassigned:
        lines.append("Groups needing another table or relaxed constraints:")
        for group in unassigned:
            lines.append(f"- {group['name']}: {', '.join(group['guests'])}")
    return _write(path, "event-seating", "\n".join(lines),
                  f"Seated {assigned} of {len(all_guests)} guests across {len(parsed_tables)} tables.")


def spaced_review_scheduler(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    window = _integer(data.get("planning_days", 14), "planning_days", 1, 90)
    topics = data.get("topics")
    if not isinstance(topics, list) or not 1 <= len(topics) <= MAX_ITEMS:
        raise RuntimeError("topics must contain 1 to 300 study topics.")
    intervals = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}
    rows = []
    for topic in topics:
        if not isinstance(topic, dict):
            raise RuntimeError("Each topic must be an object.")
        name = _text(topic.get("name"), "topic name", 100)
        last = _date(topic.get("last_reviewed"), "last_reviewed")
        if last > as_of:
            raise RuntimeError(f"{name}: last_reviewed cannot be after as_of_date.")
        confidence = _integer(topic.get("confidence"), "confidence", 1, 5)
        interval = _integer(topic.get("interval_days", intervals[confidence]), "interval_days", 1, 365)
        due = last + timedelta(days=interval)
        effective_due = max(due, as_of)
        rows.append((effective_due, due, name, confidence, interval, (as_of - due).days if due < as_of else 0))
    rows.sort(key=lambda x: (x[0], -x[3], x[2].casefold()))
    end = as_of + timedelta(days=window)
    lines = ["Spaced review plan", f"As of: {as_of.isoformat()}", f"Planning window: {window} days",
             "Confidence-based interval heuristic: 1→1 day, 2→2, 3→4, 4→7, 5→14. A custom interval_days overrides it.",
             "This is a simple planner, not the FSRS algorithm or a claim of scientifically optimised intervals.", ""]
    for effective_due, due, name, confidence, interval, overdue in rows:
        if effective_due <= end:
            state = f"OVERDUE by {overdue} day(s)" if overdue else ("Review today" if due == as_of else "Upcoming")
            lines.append(f"- {effective_due.isoformat()} | {name} | confidence {confidence}/5 | interval {interval} day(s) | {state}")
        else:
            lines.append(f"- {name}: next review {effective_due.isoformat()} (outside this window)")
    return _write(path, "spaced-review", "\n".join(lines),
                  f"Prepared review dates for {len(topics)} topic(s) over {window} days.")
