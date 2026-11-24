"""Personal planning and everyday-life tools for Nolane Wave 42.

These are deterministic offline planners. Prices, dates, availability and travel
conditions are supplied by the user; no live provider, weather or retailer data
is fetched and no upstream project code is copied.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP
from pathlib import Path

MAX_JSON_BYTES = 1 * 1024 * 1024
MAX_ITEMS = 300
ZERO = Decimal("0")


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contains a duplicate object key.")
        result[key] = value
    return result


def _load(path: Path) -> dict:
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            raise RuntimeError("Planner request exceeds the 1 MiB input limit.")
        value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_reject_duplicate_keys)
    except RuntimeError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError("Upload a valid UTF-8 JSON planning request.") from exc
    if not isinstance(value, dict):
        raise RuntimeError("Planning request must be one JSON object.")
    return value


def _text(value, label: str, maximum: int = 120) -> str:
    if not isinstance(value, str):
        raise RuntimeError(f"{label} must be text.")
    result = " ".join(value.split()).strip()
    if not result or len(result) > maximum:
        raise RuntimeError(f"{label} must contain 1 to {maximum} characters.")
    return result


def _decimal(value, label: str, minimum=ZERO, maximum=Decimal("1000000000")) -> Decimal:
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
    result = _decimal(value, label, minimum, maximum)
    if result != result.to_integral_value():
        raise RuntimeError(f"{label} must be a whole number.")
    return int(result)


def _currency(value, default="VND") -> str:
    code = str(value or default).strip().upper()
    if len(code) != 3 or not code.isalpha():
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


def _fmt(value: Decimal, places: int = 3) -> str:
    value = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    rendered = format(value, "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def _write(path: Path, suffix: str, body: str, summary: str | None = None) -> dict:
    output = path.with_name((path.stem[:64] or "nolane") + "-" + suffix + ".txt")
    output.write_text(body.rstrip() + "\n", encoding="utf-8")
    return {"summary": summary or body.splitlines()[0][:500], "output_path": str(output)}


def meal_shopping_list_planner(path: Path) -> dict:
    data = _load(path)
    meals = data.get("meals")
    if not isinstance(meals, list) or not 1 <= len(meals) <= 50:
        raise RuntimeError("meals must contain between 1 and 50 meal objects.")
    totals = {}
    total_ingredients = 0
    for meal_index, meal in enumerate(meals, 1):
        if not isinstance(meal, dict):
            raise RuntimeError(f"meals[{meal_index}] must be an object.")
        meal_name = _text(meal.get("name"), f"meals[{meal_index}].name", 100)
        servings = _decimal(meal.get("servings"), "servings", "0.1", 1000)
        target = _decimal(meal.get("target_servings"), "target_servings", "0.1", 1000)
        ingredients = meal.get("ingredients")
        if not isinstance(ingredients, list) or not 1 <= len(ingredients) <= 100:
            raise RuntimeError(f"{meal_name} must contain 1 to 100 ingredients.")
        factor = target / servings
        for ingredient_index, ingredient in enumerate(ingredients, 1):
            total_ingredients += 1
            if total_ingredients > MAX_ITEMS:
                raise RuntimeError("Combined ingredient count exceeds 300.")
            if not isinstance(ingredient, dict):
                raise RuntimeError(f"Ingredient {ingredient_index} in {meal_name} must be an object.")
            name = _text(ingredient.get("name"), "ingredient name", 100)
            unit = _text(ingredient.get("unit"), "ingredient unit", 24)
            category = _text(ingredient.get("category", "Other"), "ingredient category", 40)
            quantity = _decimal(ingredient.get("quantity"), "ingredient quantity", "0.000001", 1000000) * factor
            key = (name.casefold(), unit.casefold())
            if key not in totals:
                totals[key] = {"name": name, "unit": unit, "category": category, "quantity": ZERO, "meals": set()}
            totals[key]["quantity"] += quantity
            totals[key]["meals"].add(meal_name)

    grouped = defaultdict(list)
    for item in totals.values():
        grouped[item["category"]].append(item)
    lines = ["Meal plan shopping list", f"Meals: {len(meals)}", f"Unique shopping items: {len(totals)}",
             "Quantities are scaled to each meal's target servings; identical names and units are combined."]
    for category in sorted(grouped, key=str.casefold):
        lines.append("")
        lines.append(category)
        for item in sorted(grouped[category], key=lambda x: x["name"].casefold()):
            lines.append(f"- [ ] {_fmt(item['quantity'])} {item['unit']} {item['name']}")
    return _write(path, "meal-shopping-list", "\n".join(lines),
                  f"Combined {len(totals)} shopping items from {len(meals)} meals.")


def travel_packing_checklist(path: Path) -> dict:
    data = _load(path)
    days = _integer(data.get("days"), "days", 1, 365)
    travelers = _integer(data.get("travelers"), "travelers", 1, 30)
    nights = _integer(data.get("nights", max(0, days - 1)), "nights", 0, 365)
    if nights > days:
        raise RuntimeError("nights cannot exceed days.")
    climate = str(data.get("climate", "mild")).strip().lower()
    if climate not in {"hot", "mild", "cold", "rainy", "mixed"}:
        raise RuntimeError("climate must be hot, mild, cold, rainy or mixed.")
    activities = data.get("activities", [])
    allowed = {"beach", "swimming", "hiking", "business", "formal", "camping", "gym"}
    if not isinstance(activities, list) or len(activities) > 12 or any(not isinstance(x, str) or x.strip().lower() not in allowed for x in activities):
        raise RuntimeError("activities must be a list of up to 12 supported activity tags.")
    activities = {x.strip().lower() for x in activities}
    laundry = data.get("laundry_available", False)
    international = data.get("international", False)
    if not isinstance(laundry, bool) or not isinstance(international, bool):
        raise RuntimeError("laundry_available and international must be true or false.")

    items = []
    def add(category, name, quantity):
        if quantity > 0:
            items.append((category, name, quantity))

    clothing_days = min(days, 5) if laundry else days
    add("Clothing", "Tops / shirts", clothing_days * travelers)
    add("Clothing", "Underwear", (min(days + 1, 6) if laundry else days + 1) * travelers)
    add("Clothing", "Socks", (min(days + 1, 6) if laundry else days + 1) * travelers)
    add("Clothing", "Bottoms / trousers", max(1, math.ceil(days / 2)) * travelers)
    add("Clothing", "Sleepwear", max(1, math.ceil(max(nights, 1) / 2)) * travelers)
    add("Essentials", "Toiletry kit", travelers)
    add("Essentials", "Phone charger", travelers)
    add("Essentials", "Photo ID", travelers)
    add("Essentials", "Passport / international travel document", travelers if international else 0)
    add("Essentials", "Travel medication and prescriptions", travelers)
    add("Essentials", "Reusable water bottle", travelers)
    add("Footwear", "Comfortable everyday shoes", travelers)
    if climate in {"cold", "mixed"}:
        add("Weather", "Warm layer / jacket", travelers)
        add("Weather", "Thermal layer", travelers if climate == "cold" else 0)
    if climate in {"rainy", "mixed"}:
        add("Weather", "Rain jacket", travelers)
        add("Weather", "Compact umbrella", 1)
    if climate == "hot":
        add("Weather", "Sun hat", travelers)
        add("Weather", "Sunscreen", max(1, math.ceil(travelers / 2)))
    if activities.intersection({"beach", "swimming"}):
        add("Activities", "Swimwear", travelers)
        add("Activities", "Quick-dry towel", travelers)
    if "hiking" in activities:
        add("Activities", "Hiking shoes", travelers)
        add("Activities", "Daypack", travelers)
    if "business" in activities or "formal" in activities:
        add("Activities", "Smart / formal outfit", travelers)
    if "gym" in activities:
        add("Activities", "Workout outfit", travelers)
    if "camping" in activities:
        add("Activities", "Headlamp / flashlight", travelers)
        add("Activities", "Reusable snack / food container", travelers)

    extras = data.get("custom_items", [])
    if not isinstance(extras, list) or len(extras) > 50:
        raise RuntimeError("custom_items must be a list of up to 50 item names.")
    lines = ["Travel packing checklist", f"Trip length: {days} days / {nights} nights",
             f"Travellers: {travelers}", f"Climate supplied by user: {climate}",
             "Suggested quantities are general starting points, not personal or official travel requirements.", ""]
    current = None
    for category, name, quantity in items:
        if category != current:
            current = category
            lines.append(category)
        lines.append(f"- [ ] {quantity} × {name}")
    if extras:
        lines.extend(["", "Your extra items"])
        for extra in extras:
            lines.append("- [ ] " + _text(extra, "custom item", 100))
    return _write(path, "packing-checklist", "\n".join(lines),
                  f"Prepared a {days}-day packing checklist for {travelers} traveller(s).")


def study_plan_scheduler(path: Path) -> dict:
    data = _load(path)
    try:
        start = date.fromisoformat(_text(data.get("start_date"), "start_date", 10))
    except ValueError:
        raise RuntimeError("start_date must use YYYY-MM-DD.") from None
    daily_capacity = _integer(data.get("available_minutes_per_day"), "available_minutes_per_day", 15, 720)
    session = _integer(data.get("session_minutes", 50), "session_minutes", 10, 180)
    days_raw = data.get("study_days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    if not isinstance(days_raw, list) or not 1 <= len(days_raw) <= 7:
        raise RuntimeError("study_days must contain between 1 and 7 weekday labels.")
    try:
        study_days = {day_map[str(x).strip().lower()[:3]] for x in days_raw}
    except KeyError:
        raise RuntimeError("study_days labels must be Mon, Tue, Wed, Thu, Fri, Sat or Sun.") from None
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 60:
        raise RuntimeError("tasks must contain between 1 and 60 tasks.")
    parsed = []
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise RuntimeError("Each study task must be an object.")
        name = _text(task.get("name"), "task name", 100)
        try:
            due = date.fromisoformat(_text(task.get("due_date"), "due_date", 10))
        except ValueError:
            raise RuntimeError("Each due_date must use YYYY-MM-DD.") from None
        if due < start or (due - start).days > 366:
            raise RuntimeError("Each due_date must be between start_date and 366 days later.")
        minutes = int((_decimal(task.get("estimated_hours"), "estimated_hours", "0.01", 500) * 60)
                      .quantize(Decimal("1"), rounding=ROUND_CEILING))
        priority = _integer(task.get("priority", 3), "priority", 1, 5)
        parsed.append({"name": name, "due": due, "remaining": minutes, "priority": priority, "order": index})
    parsed.sort(key=lambda x: (x["due"], -x["priority"], x["order"]))

    capacity = {}
    schedule = defaultdict(list)
    for task in parsed:
        day = start
        while day <= task["due"] and task["remaining"] > 0:
            if day.weekday() in study_days:
                remaining_today = capacity.get(day, daily_capacity)
                chunk = min(session, task["remaining"], remaining_today)
                if chunk > 0:
                    schedule[day].append((task["name"], chunk))
                    capacity[day] = remaining_today - chunk
                    task["remaining"] -= chunk
            day += timedelta(days=1)

    lines = ["Study plan schedule", f"Start date: {start.isoformat()}",
             f"Daily study capacity: {daily_capacity} minutes",
             f"Session target: up to {session} minutes",
             "Tasks are scheduled by earliest deadline, then higher priority. Breaks are not included in study minutes.", ""]
    for day in sorted(schedule):
        lines.append(f"{day.isoformat()} ({day.strftime('%A')})")
        for name, minutes in schedule[day]:
            lines.append(f"- {minutes} min · {name}")
        lines.append(f"  Planned total: {sum(minutes for _, minutes in schedule[day])} min")
    incomplete = [task for task in parsed if task["remaining"] > 0]
    lines.extend(["", f"Tasks: {len(parsed)}",
                  f"Scheduled study time: {sum(sum(minutes for _, minutes in entries) for entries in schedule.values())} minutes",
                  f"Unscheduled tasks: {len(incomplete)}"])
    if incomplete:
        lines.append("Not enough study capacity before these deadlines:")
        for task in incomplete:
            lines.append(f"- {task['name']}: {_fmt(Decimal(task['remaining']) / 60, 2)} hours remain")
    return _write(path, "study-plan", "\n".join(lines),
                  f"Scheduled {len(parsed) - len(incomplete)} of {len(parsed)} study tasks.")


def weekly_chore_planner(path: Path) -> dict:
    data = _load(path)
    people = data.get("people")
    chores = data.get("chores")
    if not isinstance(people, list) or not 1 <= len(people) <= 20:
        raise RuntimeError("people must contain 1 to 20 names.")
    names = [_text(person, "person name", 60) for person in people]
    if len({name.casefold() for name in names}) != len(names):
        raise RuntimeError("people names must be unique.")
    if not isinstance(chores, list) or not 1 <= len(chores) <= 100:
        raise RuntimeError("chores must contain 1 to 100 chores.")
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_load = [0] * 7
    person_load = [0] * len(names)
    schedule = [[] for _ in range(7)]
    total_occurrences = 0
    for chore in chores:
        if not isinstance(chore, dict):
            raise RuntimeError("Each chore must be an object.")
        chore_name = _text(chore.get("name"), "chore name", 100)
        frequency = _integer(chore.get("times_per_week", 1), "times_per_week", 1, 7)
        duration = _integer(chore.get("duration_minutes"), "duration_minutes", 1, 480)
        preferred = chore.get("preferred_days", day_names)
        if not isinstance(preferred, list) or not preferred:
            raise RuntimeError("preferred_days must be a non-empty weekday list.")
        day_lookup = {name.casefold(): i for i, name in enumerate(day_names)}
        try:
            allowed_days = sorted({day_lookup[str(x).strip()[:3].title().casefold()] for x in preferred})
        except KeyError:
            raise RuntimeError("preferred_days must use Mon, Tue, Wed, Thu, Fri, Sat or Sun.") from None
        if frequency > len(allowed_days):
            raise RuntimeError("times_per_week cannot exceed the number of preferred days.")
        used_days = set()
        for occurrence in range(frequency):
            total_occurrences += 1
            if total_occurrences > MAX_ITEMS:
                raise RuntimeError("Total chore occurrences exceed 300.")
            choices = [d for d in allowed_days if d not in used_days]
            day = min(choices, key=lambda d: (day_load[d], len(schedule[d]), d))
            used_days.add(day)
            person_index = min(range(len(names)), key=lambda i: (person_load[i], i))
            schedule[day].append((chore_name, names[person_index], duration))
            day_load[day] += duration
            person_load[person_index] += duration
    lines = ["Weekly household chore plan", "Assignments balance estimated minutes between people and spread tasks across allowed days.", ""]
    for index, entries in enumerate(schedule):
        if entries:
            lines.append(day_names[index])
            for chore_name, person, duration in entries:
                lines.append(f"- {chore_name}: {person} ({duration} min)")
            lines.append(f"  Day total: {day_load[index]} min")
    lines.extend(["", "Weekly workload by person"])
    for index, name in enumerate(names):
        lines.append(f"- {name}: {person_load[index]} min")
    return _write(path, "weekly-chores", "\n".join(lines),
                  f"Scheduled {total_occurrences} chore occurrences across {len(names)} people.")


def subscription_cost_calculator(path: Path) -> dict:
    data = _load(path)
    subscriptions = data.get("subscriptions")
    if not isinstance(subscriptions, list) or not 1 <= len(subscriptions) <= 200:
        raise RuntimeError("subscriptions must contain 1 to 200 items.")
    factors = {"weekly": Decimal(52), "monthly": Decimal(12), "quarterly": Decimal(4),
               "semiannual": Decimal(2), "yearly": Decimal(1)}
    totals = defaultdict(lambda: ZERO)
    entries = []
    for item in subscriptions:
        if not isinstance(item, dict):
            raise RuntimeError("Each subscription must be an object.")
        name = _text(item.get("name"), "subscription name", 100)
        amount = _decimal(item.get("amount"), "subscription amount", ZERO, "1000000000")
        cycle = str(item.get("billing_cycle", "")).strip().lower()
        if cycle not in factors:
            raise RuntimeError("billing_cycle must be weekly, monthly, quarterly, semiannual or yearly.")
        currency = _currency(item.get("currency"), str(data.get("currency", "VND")))
        annual = _money(amount * factors[cycle], currency)
        totals[currency] += annual
        entries.append((name, amount, cycle, currency, annual))
    lines = ["Recurring subscription cost report", f"Subscriptions: {len(entries)}",
             "Annualized totals assume the same price and billing cycle for 12 months; no currency conversion is performed.", ""]
    for name, amount, cycle, currency, annual in entries:
        lines.append(f"- {name}: {currency} {_fmt(_money(amount, currency), _minor_units(currency))} / {cycle}")
        lines.append(f"  Annualized: {currency} {_fmt(annual, _minor_units(currency))}")
    lines.extend(["", "Totals by currency"])
    for currency in sorted(totals):
        total = _money(totals[currency], currency)
        lines.append(f"- {currency}: {currency} {_fmt(total, _minor_units(currency))} per year; "
                     f"{currency} {_fmt(_money(total / 12, currency), _minor_units(currency))} average per month")
    return _write(path, "subscription-costs", "\n".join(lines),
                  f"Annualized {len(entries)} subscriptions in {len(totals)} currency group(s).")


def commute_cost_calculator(path: Path) -> dict:
    data = _load(path)
    mode = str(data.get("mode", "")).strip().lower()
    if mode not in {"car", "public_transport"}:
        raise RuntimeError("mode must be car or public_transport.")
    days = _integer(data.get("commute_days_per_month"), "commute_days_per_month", 1, 31)
    currency = _currency(data.get("currency"))
    lines = ["Monthly commute cost estimate", f"Commute days per month: {days}", f"Mode: {mode}"]
    if mode == "car":
        distance = _decimal(data.get("distance_one_way_km"), "distance_one_way_km", "0.01", 1000)
        consumption = _decimal(data.get("consumption_l_per_100km"), "consumption_l_per_100km", "0.01", 100)
        fuel_price = _decimal(data.get("fuel_price_per_litre"), "fuel_price_per_litre", ZERO, "100000000")
        parking = _decimal(data.get("parking_per_day", 0), "parking_per_day", ZERO, "100000000")
        tolls = _decimal(data.get("tolls_per_day", 0), "tolls_per_day", ZERO, "100000000")
        shared = _integer(data.get("people_sharing", 1), "people_sharing", 1, 20)
        litres = distance * 2 * days * consumption / 100
        fuel_cost = _money(litres * fuel_price, currency)
        other = _money((parking + tolls) * days, currency)
        total = _money(fuel_cost + other, currency)
        per_person = _money(total / shared, currency)
        lines.extend([f"Round-trip distance per commute day: {_fmt(distance * 2, 2)} km",
                      f"Estimated fuel use per month: {_fmt(litres, 2)} L",
                      f"Fuel cost: {currency} {_fmt(fuel_cost, _minor_units(currency))}",
                      f"Parking and tolls: {currency} {_fmt(other, _minor_units(currency))}",
                      f"Total monthly commute cost: {currency} {_fmt(total, _minor_units(currency))}",
                      f"People sharing: {shared}",
                      f"Estimated monthly cost per person: {currency} {_fmt(per_person, _minor_units(currency))}",
                      "Estimate uses user-entered fuel consumption, fuel price, parking and tolls."])
    else:
        fare = _decimal(data.get("round_trip_fare"), "round_trip_fare", ZERO, "100000000")
        pass_price = data.get("monthly_pass_price")
        pay_as_you_go = _money(fare * days, currency)
        total = pay_as_you_go
        lines.append(f"Pay-as-you-go total: {currency} {_fmt(pay_as_you_go, _minor_units(currency))}")
        if pass_price is not None:
            monthly_pass = _money(_decimal(pass_price, "monthly_pass_price", ZERO, "100000000"), currency)
            total = min(pay_as_you_go, monthly_pass)
            lines.append(f"Monthly pass price: {currency} {_fmt(monthly_pass, _minor_units(currency))}")
            lines.append("Lower-cost option based on entered values: " + ("monthly pass" if monthly_pass < pay_as_you_go else "pay as you go"))
        lines.extend([f"Estimated monthly transit cost: {currency} {_fmt(total, _minor_units(currency))}",
                      "Estimate uses fares supplied by the user; concession, peak and route-specific fares are not checked."])
    return _write(path, "commute-cost", "\n".join(lines),
                  f"Estimated monthly commute cost: {currency} {_fmt(total, _minor_units(currency))}.")


def reading_plan_calculator(path: Path) -> dict:
    data = _load(path)
    pages = _integer(data.get("pages_remaining"), "pages_remaining", 1, 10000000)
    days = _integer(data.get("days_until_deadline"), "days_until_deadline", 1, 3660)
    days_per_week = _integer(data.get("reading_days_per_week", 7), "reading_days_per_week", 1, 7)
    full_weeks, remainder = divmod(days, 7)
    sessions = full_weeks * days_per_week + min(days_per_week, remainder)
    sessions = max(1, sessions)
    per_session = Decimal(pages) / Decimal(sessions)
    suggested = int(per_session.to_integral_value(rounding=ROUND_CEILING))
    lines = ["Reading goal plan", f"Pages remaining: {pages}",
             f"Days until deadline: {days}", f"Reading sessions assumed: {sessions}",
             f"Suggested pace: about {suggested} pages per reading day"]
    rate = data.get("pages_per_hour")
    if rate is not None:
        pages_per_hour = _decimal(rate, "pages_per_hour", "0.1", 1000)
        minutes = Decimal(suggested) / pages_per_hour * 60
        lines.append(f"Estimated reading time per session: about {_fmt(minutes, 1)} minutes")
        lines.append("Time estimate depends on the user's reading speed and text difficulty.")
    else:
        lines.append("Add pages_per_hour to estimate reading minutes; actual reading speed varies.")
    return _write(path, "reading-plan", "\n".join(lines),
                  f"Plan about {suggested} pages across each of {sessions} reading sessions.")


def grocery_budget_planner(path: Path) -> dict:
    data = _load(path)
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        raise RuntimeError("items must contain 1 to 300 shopping items.")
    currency = _currency(data.get("currency"))
    budget = _money(_decimal(data.get("budget"), "budget", ZERO, "1000000000000"), currency)
    category_totals = defaultdict(lambda: ZERO)
    total = ZERO
    rows = []
    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError("Each shopping item must be an object.")
        name = _text(item.get("name"), "item name", 100)
        quantity = _decimal(item.get("quantity"), "quantity", "0.000001", "1000000")
        unit_price = _decimal(item.get("unit_price"), "unit_price", ZERO, "1000000000")
        category = _text(item.get("category", "Other"), "category", 40)
        line_total = _money(quantity * unit_price, currency)
        total += line_total
        category_totals[category] += line_total
        rows.append((name, quantity, unit_price, line_total, category))
    total = _money(total, currency)
    difference = _money(budget - total, currency)
    lines = ["Grocery and shopping budget", f"Currency: {currency}",
             f"Budget: {currency} {_fmt(budget, _minor_units(currency))}", ""]
    for name, quantity, unit_price, line_total, category in rows:
        lines.append(f"- {name} ({category}): {_fmt(quantity)} × {currency} {_fmt(unit_price, _minor_units(currency))} = {currency} {_fmt(line_total, _minor_units(currency))}")
    lines.extend(["", "Spending by category"])
    for category in sorted(category_totals, key=str.casefold):
        lines.append(f"- {category}: {currency} {_fmt(_money(category_totals[category], currency), _minor_units(currency))}")
    lines.extend(["", f"Estimated total: {currency} {_fmt(total, _minor_units(currency))}"])
    if difference >= ZERO:
        lines.append(f"Budget remaining: {currency} {_fmt(difference, _minor_units(currency))}")
    else:
        lines.append(f"Over budget by: {currency} {_fmt(-difference, _minor_units(currency))}")
    lines.append("Prices and quantities are user-entered estimates; no retailer prices or stock are checked.")
    return _write(path, "grocery-budget", "\n".join(lines),
                  f"Shopping total: {currency} {_fmt(total, _minor_units(currency))}.")


