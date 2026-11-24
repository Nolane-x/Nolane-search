"""Wave 44 everyday life-administration planners.

All dates, inventory, recipe ingredients, travel durations, vehicle service
intervals and warranty terms are user-supplied. The processors are deterministic,
offline and intentionally avoid making food-safety, legal or mechanical claims.
"""
from __future__ import annotations

import calendar
import json
import re
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

MAX_JSON_BYTES = 1 * 1024 * 1024
MAX_ITEMS = 300


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
            raise RuntimeError("Request exceeds the 1 MiB JSON limit.")
        value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_pairs)
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


def _integer(value, label: str, minimum: int, maximum: int, default=None) -> int:
    if value is None and default is not None:
        value = default
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


def _time(value, label: str) -> int:
    raw = _text(value, label, 5)
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", raw):
        raise RuntimeError(f"{label} must use HH:MM (24-hour time).")
    return int(raw[:2]) * 60 + int(raw[3:])


def _time_text(minutes: int) -> str:
    if not 0 <= minutes < 24 * 60:
        raise RuntimeError("A planned activity would extend beyond midnight.")
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _fmt(value: Decimal, places=3) -> str:
    rounded = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    rendered = format(rounded, "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def _month_add(value: date, months: int) -> date:
    absolute = value.year * 12 + value.month - 1 + months
    year, month_zero = divmod(absolute, 12)
    month = month_zero + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _write(path: Path, suffix: str, body: str, summary: str) -> dict:
    output = path.with_name((path.stem[:64] or "nolane") + "-" + suffix + ".txt")
    output.write_text(body.rstrip() + "\n", encoding="utf-8")
    return {"summary": summary[:500], "output_path": str(output)}


def pantry_use_first_planner(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    window = _integer(data.get("window_days", 14), "window_days", 1, 365)
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        raise RuntimeError("items must contain 1 to 300 pantry items.")
    rows = []
    kinds = {"use_by": "Use-by date", "best_before": "Best-before date", "expiry": "Expiry date"}
    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError("Each pantry item must be an object.")
        name = _text(item.get("name"), "item name", 100)
        day = _date(item.get("date"), f"{name} date")
        kind = str(item.get("date_type", "best_before")).strip().lower()
        if kind not in kinds:
            raise RuntimeError(f"{name}: date_type must be use_by, best_before or expiry.")
        location = " ".join(str(item.get("location", "")).split()).strip()[:60]
        quantity = item.get("quantity")
        unit = ""
        quantity_text = ""
        if quantity is not None:
            quantity_value = _number(quantity, f"{name} quantity", "0.000001", 1_000_000)
            unit = _text(item.get("unit"), f"{name} unit", 24)
            quantity_text = f" | {_fmt(quantity_value)} {unit}"
        days = (day - as_of).days
        status = "PAST DATE" if days < 0 else ("DATE IS TODAY" if days == 0 else ("Within planning window" if days <= window else "Later"))
        rows.append((day, name.casefold(), name, kind, location, quantity_text, days, status))
    rows.sort(key=lambda row: (row[0], row[1]))
    lines = [
        "Pantry use-first list", f"As of: {as_of.isoformat()}", f"Planning window: {window} days",
        "Items are sorted by the date supplied by the user. This report does not determine whether food is safe to eat.",
        "",
    ]
    for day, _, name, kind, location, quantity, days, status in rows:
        delta = f"{abs(days)} day(s) ago" if days < 0 else (f"in {days} day(s)" if days > 0 else "today")
        parts = [day.isoformat(), name, kinds[kind], status, delta]
        if quantity:
            parts.append(quantity.strip(" |"))
        if location:
            parts.append("location: " + location)
        lines.append("- " + " | ".join(parts))
    lines.extend(["", "Check the package instructions and local food-safety guidance; a date alone is not a safety assessment."])
    return _write(path, "pantry-use-first", "\n".join(lines), f"Prioritised {len(rows)} pantry items by their supplied dates.")


def pantry_recipe_matcher(path: Path) -> dict:
    data = _read(path)
    available = data.get("available_ingredients")
    recipes = data.get("recipes")
    staples = data.get("pantry_staples", [])
    if not isinstance(available, list) or not 1 <= len(available) <= MAX_ITEMS:
        raise RuntimeError("available_ingredients must contain 1 to 300 ingredient names.")
    if not isinstance(staples, list) or len(staples) > 100:
        raise RuntimeError("pantry_staples must be a list of up to 100 names.")
    if not isinstance(recipes, list) or not 1 <= len(recipes) <= 100:
        raise RuntimeError("recipes must contain 1 to 100 recipe objects.")
    normalise = lambda value: " ".join(_text(value, "ingredient", 100).casefold().split())
    stock = {normalise(value) for value in available + staples}
    max_missing = _integer(data.get("max_missing", 5), "max_missing", 0, 30)
    results = []
    total = 0
    for recipe in recipes:
        if not isinstance(recipe, dict):
            raise RuntimeError("Each recipe must be an object.")
        name = _text(recipe.get("name"), "recipe name", 100)
        ingredients = recipe.get("ingredients")
        optional = recipe.get("optional_ingredients", [])
        if not isinstance(ingredients, list) or not 1 <= len(ingredients) <= 100:
            raise RuntimeError(f"{name}: ingredients must contain 1 to 100 required items.")
        if not isinstance(optional, list) or len(optional) > 50:
            raise RuntimeError(f"{name}: optional_ingredients must contain up to 50 items.")
        required = list(dict.fromkeys(normalise(value) for value in ingredients))
        total += len(required)
        if total > MAX_ITEMS:
            raise RuntimeError("Combined required recipe ingredient count exceeds 300.")
        missing = [value for value in required if value not in stock]
        present = len(required) - len(missing)
        optional_missing = [normalise(value) for value in optional if normalise(value) not in stock]
        results.append((len(missing), -present / len(required), name.casefold(), name, present, len(required), missing, optional_missing))
    results.sort(key=lambda row: (row[0], row[1], row[2]))
    lines = [
        "Recipes matched against your ingredients",
        f"Available ingredients: {len(stock)} (including user-listed staples)",
        "Matching is exact after case/space normalisation; aliases and substitutions are not guessed.",
        "",
    ]
    for missing_count, neg_score, _, name, present, required_count, missing, optional in results:
        score = int(round(-neg_score * 100))
        state = "Ready from listed ingredients" if not missing else ("Close match" if missing_count <= max_missing else "Needs more ingredients")
        lines.extend([f"{name} — {score}% ingredient match — {state}", f"- Required items present: {present}/{required_count}"])
        if missing:
            lines.append("- Missing: " + ", ".join(missing))
        if optional:
            lines.append("- Optional items not listed: " + ", ".join(optional))
        lines.append("")
    return _write(path, "pantry-recipe-match", "\n".join(lines), f"Compared {len(recipes)} recipes against {len(stock)} available ingredients.")


def meal_prep_timeline_planner(path: Path) -> dict:
    data = _read(path)
    start = _time(data.get("start_time"), "start_time")
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 100:
        raise RuntimeError("tasks must contain 1 to 100 meal-preparation steps.")
    parsed = []
    identifiers = set()
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise RuntimeError("Each meal-preparation task must be an object.")
        identifier = _text(task.get("id", f"task-{index + 1}"), "task id", 50)
        if identifier in identifiers:
            raise RuntimeError("Meal-preparation task IDs must be unique.")
        identifiers.add(identifier)
        name = _text(task.get("name"), "task name", 100)
        duration = _integer(task.get("duration_minutes"), f"{name} duration_minutes", 1, 480)
        resource = _text(task.get("resource", "hands"), f"{name} resource", 40).casefold()
        deps = task.get("depends_on", [])
        attention = task.get("attention_required", True)
        if not isinstance(deps, list) or len(deps) > 100 or any(not isinstance(dep, str) for dep in deps):
            raise RuntimeError(f"{name}: depends_on must be a list of task IDs.")
        if not isinstance(attention, bool):
            raise RuntimeError(f"{name}: attention_required must be true or false.")
        parsed.append({"id": identifier, "name": name, "duration": duration, "resource": resource,
                       "deps": deps, "attention": attention, "order": index})
    by_id = {task["id"]: task for task in parsed}
    for task in parsed:
        if task["id"] in task["deps"] or any(dep not in by_id for dep in task["deps"]):
            raise RuntimeError(f"{task['name']}: depends_on contains an unknown or self-referencing task ID.")
    reserved = defaultdict(list)
    scheduled = {}
    pending = list(parsed)
    while pending:
        ready = [task for task in pending if all(dep in scheduled for dep in task["deps"])]
        if not ready:
            raise RuntimeError("Meal-preparation dependencies contain a cycle.")
        for task in sorted(ready, key=lambda row: row["order"]):
            earliest = max([start] + [scheduled[dep]["end"] for dep in task["deps"]])
            resources = []
            if task["resource"] != "none":
                resources.append(task["resource"])
            if task["attention"] and "hands" not in resources:
                resources.append("hands")
            candidate = earliest
            while True:
                conflict_end = None
                for resource in resources:
                    for occupied_start, occupied_end, _ in sorted(reserved[resource]):
                        if candidate < occupied_end and candidate + task["duration"] > occupied_start:
                            conflict_end = max(conflict_end or 0, occupied_end)
                if conflict_end is None:
                    break
                candidate = conflict_end
            end = candidate + task["duration"]
            if end >= 24 * 60:
                raise RuntimeError(f"{task['name']}: schedule extends beyond midnight.")
            for resource in resources:
                reserved[resource].append((candidate, end, task["name"]))
            scheduled[task["id"]] = {"start": candidate, "end": end, "task": task}
        pending = [task for task in pending if task["id"] not in scheduled]
    timeline = sorted(scheduled.values(), key=lambda row: (row["start"], row["end"], row["task"]["order"]))
    finish = max(row["end"] for row in timeline)
    lines = [
        "Meal-preparation timeline", f"Start time: {_time_text(start)}",
        f"Estimated finish: {_time_text(finish)}", f"Elapsed time: {finish - start} minutes",
        "Tasks using attention and the same appliance are scheduled without overlap. Passive steps can run while another task is active when resources differ.",
        "",
    ]
    for row in timeline:
        task = row["task"]
        deps = ", ".join(task["deps"]) if task["deps"] else "none"
        lines.append(f"- {_time_text(row['start'])}–{_time_text(row['end'])} | {task['name']} | {task['duration']} min | resource: {task['resource']} | after: {deps}")
    return _write(path, "meal-prep-timeline", "\n".join(lines), f"Scheduled {len(timeline)} cooking steps; finish at {_time_text(finish)}.")


def laundry_load_organizer(path: Path) -> dict:
    data = _read(path)
    capacity = _number(data.get("machine_capacity_kg"), "machine_capacity_kg", "0.1", 30)
    target_temp = _integer(data.get("target_temp_c", 30), "target_temp_c", 20, 90)
    if target_temp % 10:
        raise RuntimeError("target_temp_c must be in 10-degree steps.")
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        raise RuntimeError("items must contain 1 to 300 clothing items.")
    allowed_colors = {"white", "light", "bright", "dark"}
    allowed_fabrics = {"normal", "delicate", "wool", "silk", "denim", "towel"}
    allowed_drying = {"air", "flat", "tumble"}
    groups = defaultdict(list)
    oversized = []
    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError("Each laundry item must be an object.")
        name = _text(item.get("name"), "laundry item name", 100)
        weight = _number(item.get("weight_kg"), f"{name} weight_kg", "0.01", 30)
        color = str(item.get("color_group", "dark")).strip().lower()
        fabric = str(item.get("fabric_group", "normal")).strip().lower()
        drying = str(item.get("drying", "air")).strip().lower()
        max_temp = _integer(item.get("max_temp_c", 30), f"{name} max_temp_c", 20, 90)
        if max_temp % 10:
            raise RuntimeError(f"{name}: max_temp_c must be in 10-degree steps.")
        if color not in allowed_colors or fabric not in allowed_fabrics or drying not in allowed_drying:
            raise RuntimeError(f"{name}: unsupported colour, fabric or drying group.")
        if weight > capacity:
            oversized.append((name, weight))
        else:
            groups[(color, fabric, drying)].append((name, weight, max_temp))
    loads = []
    for (color, fabric, drying), group in sorted(groups.items()):
        bins = []
        for name, weight, max_temp in sorted(group, key=lambda row: (-row[1], row[0].casefold())):
            target = next((bucket for bucket in bins if bucket["weight"] + weight <= capacity), None)
            if target is None:
                target = {"items": [], "weight": Decimal("0"), "max_temp": target_temp}
                bins.append(target)
            target["items"].append((name, weight))
            target["weight"] += weight
            target["max_temp"] = min(target["max_temp"], max_temp)
        for bucket in bins:
            loads.append({"color": color, "fabric": fabric, "drying": drying,
                          "weight": bucket["weight"], "temp": min(target_temp, bucket["max_temp"]),
                          "items": bucket["items"]})
    lines = [
        "Laundry load plan", f"Machine capacity: {_fmt(capacity, 2)} kg",
        f"Requested wash temperature: {target_temp}°C",
        "Loads are separated by user-entered colour, fabric and drying groups; wash temperature is lowered to respect the lowest stated maximum in each load.",
        "",
    ]
    for index, load in enumerate(loads, 1):
        lines.append(f"Load {index}: {load['color']} | {load['fabric']} | dry: {load['drying']} | wash at up to {load['temp']}°C | {_fmt(load['weight'], 2)}/{_fmt(capacity, 2)} kg")
        for name, weight in load["items"]:
            lines.append(f"  - {name} ({_fmt(weight, 2)} kg)")
        lines.append("")
    if oversized:
        lines.extend(["Items too heavy for one machine load:"])
        for name, weight in oversized:
            lines.append(f"- {name}: {_fmt(weight, 2)} kg; split manually only if the item/care label allows it.")
    lines.append("Always follow each garment's care label and the washing-machine instructions.")
    return _write(path, "laundry-load-plan", "\n".join(lines), f"Grouped {len(items) - len(oversized)} items into {len(loads)} compatible load(s); {len(oversized)} oversized item(s).")


def trip_itinerary_planner(path: Path) -> dict:
    data = _read(path)
    start = _time(data.get("start_time"), "start_time")
    end = _time(data.get("end_time"), "end_time")
    if end <= start:
        raise RuntimeError("end_time must be later than start_time on the same day.")
    stops = data.get("stops")
    if not isinstance(stops, list) or not 1 <= len(stops) <= 100:
        raise RuntimeError("stops must contain 1 to 100 itinerary stops.")
    cursor = start
    lines = ["Day-trip itinerary", f"Available time: {_time_text(start)}–{_time_text(end)}", "Travel times are supplied by the user; no route or traffic estimate is invented.", ""]
    unscheduled = []
    for index, stop in enumerate(stops):
        if not isinstance(stop, dict):
            raise RuntimeError("Each stop must be an object.")
        name = _text(stop.get("name"), "stop name", 100)
        travel = _integer(stop.get("travel_minutes_from_previous", 0), f"{name} travel_minutes_from_previous", 0, 720)
        duration = _integer(stop.get("duration_minutes"), f"{name} duration_minutes", 1, 720)
        arrival = cursor + travel
        departure = arrival + duration
        if departure > end:
            unscheduled.extend([_text(row.get("name"), "stop name", 100) for row in stops[index:]])
            break
        lines.append(f"- {_time_text(cursor)}–{_time_text(arrival)} | Travel to {name} ({travel} min)")
        lines.append(f"  {_time_text(arrival)}–{_time_text(departure)} | Visit {name} ({duration} min)")
        cursor = departure
    lines.extend(["", f"Finish time: {_time_text(cursor)}", f"Free time remaining: {end - cursor} minutes"])
    if unscheduled:
        lines.append("Stops that do not fit in the available window, kept in original order:")
        lines.extend("- " + name for name in unscheduled)
    return _write(path, "trip-itinerary", "\n".join(lines), f"Scheduled {len(stops) - len(unscheduled)} of {len(stops)} stop(s).")


def vehicle_maintenance_planner(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    current_km = _integer(data.get("current_odometer_km"), "current_odometer_km", 0, 10_000_000)
    monthly_km = _number(data.get("estimated_monthly_km", 0), "estimated_monthly_km", 0, 200_000)
    horizon = _integer(data.get("window_days", 90), "window_days", 1, 730)
    tasks = data.get("maintenance")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 100:
        raise RuntimeError("maintenance must contain 1 to 100 service items.")
    rows = []
    for task in tasks:
        if not isinstance(task, dict):
            raise RuntimeError("Each maintenance item must be an object.")
        name = _text(task.get("name"), "maintenance name", 100)
        last_date = _date(task.get("last_service_date"), f"{name} last_service_date")
        last_km = _integer(task.get("last_service_odometer_km"), f"{name} last_service_odometer_km", 0, 10_000_000)
        months = _integer(task.get("interval_months"), f"{name} interval_months", 1, 120)
        km_interval = _integer(task.get("interval_km"), f"{name} interval_km", 1, 1_000_000)
        if last_date > as_of or last_km > current_km:
            raise RuntimeError(f"{name}: last service cannot be after the current date or odometer.")
        date_due = _month_add(last_date, months)
        km_due = last_km + km_interval
        km_reached = current_km >= km_due
        projected_date = None
        if km_reached:
            projected_date = as_of
        elif monthly_km > 0:
            remaining = Decimal(km_due - current_km)
            days = int((remaining / monthly_km * Decimal(30)).to_integral_value(rounding="ROUND_CEILING"))
            projected_date = as_of + timedelta(days=days)
        effective = min(date_due, projected_date) if projected_date else date_due
        overdue_days = max(0, (as_of - effective).days)
        if km_reached or date_due <= as_of:
            state = "DUE NOW / OVERDUE"
            effective = as_of
        elif effective <= as_of + timedelta(days=horizon):
            state = "Due within planning window"
        else:
            state = "Later"
        rows.append((effective, name.casefold(), name, date_due, km_due, current_km, state, overdue_days, projected_date))
    rows.sort(key=lambda row: (row[0], row[1]))
    lines = [
        "Vehicle maintenance plan", f"As of: {as_of.isoformat()}",
        f"Current odometer: {current_km:,} km", f"Estimated monthly distance: {_fmt(monthly_km, 0)} km",
        "Intervals come from the user's owner manual or service records; this is not a substitute for manufacturer guidance.",
        "",
    ]
    for effective, _, name, date_due, km_due, odometer, state, overdue_days, projected in rows:
        km_left = max(0, km_due - odometer)
        projected_text = projected.isoformat() if projected else "not projected (monthly distance is zero)"
        lines.append(f"- {name} | {state} | estimated trigger: {effective.isoformat()} | calendar interval: {date_due.isoformat()} | odometer trigger: {km_due:,} km ({km_left:,} km remaining) | mileage projection: {projected_text}")
        if overdue_days:
            lines.append(f"  Calendar projection is {overdue_days} day(s) past due.")
    return _write(path, "vehicle-maintenance", "\n".join(lines), f"Reviewed {len(rows)} vehicle service interval(s).")


def document_renewal_planner(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    window = _integer(data.get("window_days", 180), "window_days", 1, 1825)
    documents = data.get("documents")
    if not isinstance(documents, list) or not 1 <= len(documents) <= 150:
        raise RuntimeError("documents must contain 1 to 150 items.")
    rows = []
    for document in documents:
        if not isinstance(document, dict):
            raise RuntimeError("Each document must be an object.")
        name = _text(document.get("name"), "document name", 100)
        expires = _date(document.get("expiry_date"), f"{name} expiry_date")
        notice = _integer(document.get("remind_days_before", 60), f"{name} remind_days_before", 0, 3650)
        renewal_start = expires - timedelta(days=notice)
        if expires < as_of:
            state = "EXPIRED"
        elif renewal_start <= as_of:
            state = "Start/check renewal now"
        elif renewal_start <= as_of + timedelta(days=window):
            state = "Renewal window approaching"
        else:
            state = "Later"
        rows.append((renewal_start, expires, name.casefold(), name, notice, state))
    rows.sort(key=lambda row: (row[0], row[2]))
    lines = [
        "Document renewal reminders", f"As of: {as_of.isoformat()}",
        f"Planning window: {window} days",
        "Reminder windows are entered by the user. Confirm current requirements and processing times with the issuing authority or provider.",
        "",
    ]
    for start, expires, _, name, notice, state in rows:
        lines.append(f"- {name} | {state} | check renewal from {start.isoformat()} | expires {expires.isoformat()} | reminder lead time {notice} day(s)")
    return _write(path, "document-renewal", "\n".join(lines), f"Prepared renewal reminders for {len(rows)} document(s).")


def warranty_claim_assistant(path: Path) -> dict:
    data = _read(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    product = _text(data.get("product_name"), "product_name", 120)
    seller = _text(data.get("seller"), "seller", 120)
    purchase = _date(data.get("purchase_date"), "purchase_date")
    months = _integer(data.get("warranty_months"), "warranty_months", 0, 120)
    issue = _text(data.get("issue_description"), "issue_description", 2000)
    evidence = data.get("evidence", ["Purchase receipt"])
    if not isinstance(evidence, list) or len(evidence) > 30:
        raise RuntimeError("evidence must be a list of up to 30 items.")
    evidence = [_text(item, "evidence item", 100) for item in evidence]
    language = str(data.get("language", "vi")).strip().lower()
    if language not in {"vi", "en"}:
        raise RuntimeError("language must be vi or en.")
    if purchase > as_of:
        raise RuntimeError("purchase_date cannot be after as_of_date.")
    warranty_end = _month_add(purchase, months)
    if as_of <= warranty_end:
        status = "Trong thời hạn bảo hành ước tính theo dữ liệu đã nhập" if language == "vi" else "Inside the user-entered estimated warranty period"
        remaining = (warranty_end - as_of).days
    else:
        status = "Ngày kết thúc bảo hành ước tính đã qua" if language == "vi" else "User-entered estimated warranty end date has passed"
        remaining = 0
    if language == "vi":
        lines = [
            "Bản nháp yêu cầu kiểm tra bảo hành", f"Người nhận: {seller}",
            f"Sản phẩm: {product}", f"Ngày mua: {purchase.isoformat()}",
            f"Thời hạn bảo hành người dùng nhập: {months} tháng",
            f"Ngày kết thúc ước tính theo phép cộng tháng: {warranty_end.isoformat()}",
            f"Tình trạng theo dữ liệu đã nhập: {status}",
            f"Mô tả sự cố: {issue}", "",
            "Kính gửi bộ phận hỗ trợ,",
            f"Tôi muốn nhờ kiểm tra sản phẩm {product} đã mua ngày {purchase.isoformat()}. Sản phẩm hiện gặp vấn đề như sau: {issue}",
            "Nhờ quý bộ phận hướng dẫn quy trình kiểm tra và xác nhận điều kiện bảo hành áp dụng cho sản phẩm này.",
            "Tôi có thể cung cấp các tài liệu sau:",
        ]
        lines.extend("- " + item for item in evidence)
        lines.extend(["", "Xin cảm ơn.", ""])
        lines.append("Lưu ý: ngày kết thúc chỉ là phép tính từ thời hạn do người dùng nhập; hãy đối chiếu phiếu bảo hành, ngoại lệ, ngày kích hoạt và điều kiện của người bán/nhà sản xuất trước khi kết luận quyền lợi.")
    else:
        lines = [
            "Warranty inspection request draft", f"To: {seller}",
            f"Product: {product}", f"Purchase date: {purchase.isoformat()}",
            f"Warranty duration entered: {months} month(s)",
            f"Estimated end date from the entered duration: {warranty_end.isoformat()}",
            f"Status from supplied data: {status}",
            f"Issue: {issue}", "",
            "Hello,",
            f"I would like to request an inspection of {product}, purchased on {purchase.isoformat()}. The issue is: {issue}",
            "Please let me know the inspection process and confirm the warranty conditions that apply to this product.",
            "I can provide the following evidence:",
        ]
        lines.extend("- " + item for item in evidence)
        lines.extend(["", "Thank you.", ""])
        lines.append("Note: the end date is only a calculation based on the duration entered by the user. Check the actual warranty document, exclusions, activation date and seller/manufacturer terms before concluding coverage.")
    return _write(path, "warranty-claim", "\n".join(lines), f"Prepared a warranty enquiry draft; estimated end date {warranty_end.isoformat()} ({remaining} day(s) remaining by entered dates).")
