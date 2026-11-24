"""Daily life planning calculators for Nolane Wave 41.

All rates, quantities and prices are supplied by the user. These utilities are
offline estimates and intentionally avoid external tariff, retailer or carrier APIs.
"""
from __future__ import annotations

import json
import math
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


def water_bill_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    previous = _decimal(data.get("previous_reading_m3"), "previous_reading_m3", 0, "1000000000")
    current = _decimal(data.get("current_reading_m3"), "current_reading_m3", 0, "1000000000")
    if current < previous:
        raise RuntimeError("current_reading_m3 cannot be lower than previous_reading_m3.")
    rate = _money(_decimal(data.get("price_per_m3"), "price_per_m3", 0, "1000000000"), currency)
    fixed = _money(_decimal(data.get("fixed_charge", 0), "fixed_charge", 0, "1000000000000"), currency)
    sewage = _decimal(data.get("sewage_percent", 0), "sewage_percent", 0, 100)
    consumption = current - previous
    usage_cost = consumption * rate
    sewage_cost = _money(usage_cost * sewage / 100, currency)
    total = _money(usage_cost + sewage_cost + fixed, currency)
    lines = [
        "Water bill estimate",
        f"Previous meter reading: {_fmt(previous)} m³",
        f"Current meter reading: {_fmt(current)} m³",
        f"Water used: {_fmt(consumption, 3)} m³",
        f"User-entered price: {currency} {_fmt(rate, places)} per m³",
        f"Water charge: {currency} {_fmt(_money(usage_cost, currency), places)}",
        f"Sewage allowance: {_fmt(sewage)}% ({currency} {_fmt(sewage_cost, places)})",
        f"Fixed charge: {currency} {_fmt(fixed, places)}",
        f"Estimated bill: {currency} {_fmt(total, places)}",
        "Estimate uses a single user-entered unit price; real tariffs may be tiered and can include taxes or other fees.",
    ]
    return _write(path, "water-bill", "\n".join(lines),
                  f"Water use {_fmt(consumption, 2)} m³; estimated bill {currency} {_fmt(total, places)}.")


def mobile_data_duration_calculator(path: Path) -> dict:
    data = _load_request(path)
    allowance = _decimal(data.get("allowance_gb"), "allowance_gb", "0.001", 1000000)
    used = _decimal(data.get("used_gb", 0), "used_gb", 0, 1000000)
    if used > allowance:
        raise RuntimeError("used_gb cannot exceed allowance_gb.")
    daily = _decimal(data.get("daily_usage_gb"), "daily_usage_gb", "0.000001", 10000)
    reserve = _decimal(data.get("reserve_percent", 0), "reserve_percent", 0, 90)
    days_to_reset_raw = data.get("days_until_reset")
    available = (allowance - used) * (ONE - reserve / 100)
    days_last = available / daily
    lines = [
        "Mobile data allowance estimate",
        f"Plan allowance: {_fmt(allowance)} GB",
        f"Already used: {_fmt(used)} GB",
        f"Data remaining before reserve: {_fmt(allowance-used, 3)} GB",
        f"Reserve: {_fmt(reserve)}%",
        f"Usable data: {_fmt(available, 3)} GB",
        f"Average daily usage: {_fmt(daily, 3)} GB/day",
        f"Estimated duration at this usage: {_fmt(days_last, 1)} days",
    ]
    summary = f"Remaining data should last about {_fmt(days_last, 1)} days at {_fmt(daily, 2)} GB/day."
    if days_to_reset_raw is not None:
        reset = _decimal(days_to_reset_raw, "days_until_reset", "0.01", 366)
        daily_budget = available / reset
        lines.extend([
            f"Days until plan reset: {_fmt(reset)}",
            f"Suggested average daily limit to last until reset: {_fmt(daily_budget, 3)} GB/day",
            f"Current usage is {'above' if daily > daily_budget else 'within'} that average daily limit.",
        ])
        summary += f" To last {_fmt(reset)} days, average no more than {_fmt(daily_budget, 2)} GB/day."
    lines.append("Estimate assumes daily usage stays constant; background updates, video quality and tethering can change consumption.")
    return _write(path, "mobile-data-duration", "\n".join(lines), summary)


def solar_panel_output_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    watt = _decimal(data.get("panel_watts"), "panel_watts", "1", 5000)
    panels = _integer(data.get("panel_count"), "panel_count", 1, 100000)
    sun = _decimal(data.get("peak_sun_hours_per_day"), "peak_sun_hours_per_day", 0, 24)
    loss = _decimal(data.get("system_loss_percent", 20), "system_loss_percent", 0, 90)
    days = _integer(data.get("days", 30), "days", 1, 366)
    system_kw = watt * panels / Decimal(1000)
    daily_kwh = system_kw * sun * (ONE - loss / 100)
    total_kwh = daily_kwh * days
    lines = [
        "Solar panel output estimate",
        f"Panel rating: {_fmt(watt)} W × {panels}",
        f"System size: {_fmt(system_kw, 3)} kW",
        f"Peak sun hours assumption: {_fmt(sun)} h/day",
        f"System loss allowance: {_fmt(loss)}%",
        f"Estimated daily energy: {_fmt(daily_kwh, 2)} kWh",
        f"Estimated energy over {days} days: {_fmt(total_kwh, 1)} kWh",
    ]
    summary = f"Estimated solar output {_fmt(daily_kwh, 2)} kWh/day or {_fmt(total_kwh, 1)} kWh over {days} days."
    if data.get("price_per_kwh") is not None:
        rate = _money(_decimal(data.get("price_per_kwh"), "price_per_kwh", 0, "1000000000"), currency)
        value = _money(total_kwh * rate, currency)
        lines.append(f"Illustrative value at user-entered rate: {currency} {_fmt(value, places)}")
        summary += f" At the entered rate, that is {currency} {_fmt(value, places)}."
    lines.append("Estimate only: actual output depends on weather, shading, orientation, temperature, inverter limits and local installation.")
    return _write(path, "solar-output", "\n".join(lines), summary)


def wallpaper_roll_calculator(path: Path) -> dict:
    data = _load_request(path)
    perimeter = _decimal(data.get("room_perimeter_m"), "room_perimeter_m", "0.1", 10000)
    height = _decimal(data.get("wall_height_m"), "wall_height_m", "0.1", 100)
    roll_width = _decimal(data.get("roll_width_m"), "roll_width_m", "0.1", 5)
    roll_length = _decimal(data.get("roll_length_m"), "roll_length_m", "0.1", 100)
    repeat_cm = _decimal(data.get("pattern_repeat_cm", 0), "pattern_repeat_cm", 0, 500)
    extra = _integer(data.get("extra_rolls", 1), "extra_rolls", 0, 20)
    strips = int((perimeter / roll_width).to_integral_value(rounding=ROUND_CEILING))
    drop = height
    if repeat_cm > 0:
        repeat_m = repeat_cm / 100
        drop = (height / repeat_m).to_integral_value(rounding=ROUND_CEILING) * repeat_m
    drops_per_roll = int((roll_length / drop).to_integral_value(rounding=ROUND_CEILING)) if roll_length < drop else int(roll_length // drop)
    if drops_per_roll <= 0:
        raise RuntimeError("A wallpaper roll is shorter than one required wall drop.")
    base_rolls = int((Decimal(strips) / drops_per_roll).to_integral_value(rounding=ROUND_CEILING))
    total_rolls = base_rolls + extra
    lines = [
        "Wallpaper roll estimate",
        f"Room perimeter: {_fmt(perimeter)} m",
        f"Wall height: {_fmt(height)} m",
        f"Roll size: {_fmt(roll_width)} m × {_fmt(roll_length)} m",
        f"Pattern repeat: {_fmt(repeat_cm)} cm",
        f"Adjusted drop length: {_fmt(drop, 3)} m",
        f"Vertical strips required: {strips}",
        f"Usable drops per roll: {drops_per_roll}",
        f"Base rolls required: {base_rolls}",
        f"Extra rolls allowance: {extra}",
        f"Suggested rolls to buy: {total_rolls}",
        "Estimate assumes full room perimeter is wallpapered; deduct doors/windows only by adjusting the supplied perimeter or adding a separate allowance.",
    ]
    return _write(path, "wallpaper-estimate", "\n".join(lines),
                  f"About {strips} strips; buy approximately {total_rolls} rolls including {extra} spare.")


def curtain_fabric_calculator(path: Path) -> dict:
    data = _load_request(path)
    window_width = _decimal(data.get("window_width_cm"), "window_width_cm", "1", 10000)
    window_height = _decimal(data.get("window_height_cm"), "window_height_cm", "1", 10000)
    fabric_width = _decimal(data.get("fabric_width_cm"), "fabric_width_cm", "1", 1000)
    fullness = _decimal(data.get("fullness_ratio", 2), "fullness_ratio", "1", 5)
    side_allowance = _decimal(data.get("side_allowance_cm", 30), "side_allowance_cm", 0, 1000)
    top_hem = _decimal(data.get("top_hem_cm", 10), "top_hem_cm", 0, 100)
    bottom_hem = _decimal(data.get("bottom_hem_cm", 20), "bottom_hem_cm", 0, 200)
    repeat = _decimal(data.get("pattern_repeat_cm", 0), "pattern_repeat_cm", 0, 500)
    target_width = window_width * fullness + side_allowance
    panels = int((target_width / fabric_width).to_integral_value(rounding=ROUND_CEILING))
    drop = window_height + top_hem + bottom_hem
    if repeat > 0:
        drop = (drop / repeat).to_integral_value(rounding=ROUND_CEILING) * repeat
    total_length_cm = panels * drop
    metres = total_length_cm / 100
    lines = [
        "Curtain fabric estimate",
        f"Window width × height: {_fmt(window_width)} cm × {_fmt(window_height)} cm",
        f"Fullness ratio: {_fmt(fullness)}×",
        f"Total fabric width allowance: {_fmt(target_width)} cm",
        f"Fabric width: {_fmt(fabric_width)} cm",
        f"Panels/cuts required: {panels}",
        f"Cut/drop length per panel: {_fmt(drop, 1)} cm",
        f"Total fabric length: {_fmt(metres, 2)} metres",
        "Estimate excludes lining, pattern matching across panels and special pleat/header construction.",
    ]
    return _write(path, "curtain-fabric", "\n".join(lines),
                  f"Approximately {panels} panels and {_fmt(metres, 2)} metres of fabric.")


def moving_box_calculator(path: Path) -> dict:
    data = _load_request(path)
    volume = _decimal(data.get("items_volume_m3"), "items_volume_m3", "0.001", 100000)
    box_l = _decimal(data.get("box_volume_l"), "box_volume_l", "1", 1000)
    fill = _decimal(data.get("usable_fill_percent", 75), "usable_fill_percent", "1", 100)
    extra = _decimal(data.get("extra_boxes_percent", 10), "extra_boxes_percent", 0, 100)
    effective = box_l / 1000 * fill / 100
    base = (volume / effective).to_integral_value(rounding=ROUND_CEILING)
    boxes = int((base * (ONE + extra / 100)).to_integral_value(rounding=ROUND_CEILING))
    lines = [
        "Moving box estimator",
        f"Estimated items volume: {_fmt(volume, 3)} m³",
        f"Box nominal volume: {_fmt(box_l)} litres",
        f"Usable fill per box: {_fmt(effective * 1000, 1)} litres ({_fmt(fill)}%)",
        f"Base boxes: {int(base)}",
        f"Extra allowance: {_fmt(extra)}%",
        f"Suggested boxes: {boxes}",
        "Estimate is based on total packed volume; fragile items, awkward shapes, weight limits and wardrobe boxes may change the quantity.",
    ]
    return _write(path, "moving-box-estimate", "\n".join(lines),
                  f"Plan for approximately {boxes} boxes including the extra allowance.")


def event_food_calculator(path: Path) -> dict:
    data = _load_request(path)
    people = _integer(data.get("guests"), "guests", 1, 100000)
    food = _decimal(data.get("food_grams_per_person"), "food_grams_per_person", 0, 5000)
    drink = _decimal(data.get("drink_ml_per_person"), "drink_ml_per_person", 0, 10000)
    snack = _decimal(data.get("snack_grams_per_person", 0), "snack_grams_per_person", 0, 5000)
    buffer = _decimal(data.get("extra_percent", 10), "extra_percent", 0, 100)
    factor = ONE + buffer / 100
    food_total = Decimal(people) * food * factor
    drink_total = Decimal(people) * drink * factor
    snack_total = Decimal(people) * snack * factor
    lines = [
        "Event food and drink estimate",
        f"Guests: {people}",
        f"Extra allowance: {_fmt(buffer)}%",
        f"Main food: {_fmt(food_total / 1000, 2)} kg ({_fmt(food_total, 0)} g)",
        f"Drinks: {_fmt(drink_total / 1000, 2)} litres",
        f"Snacks: {_fmt(snack_total / 1000, 2)} kg",
        "Portion sizes depend on event type, duration, menu and guest preferences; use values appropriate to your event.",
    ]
    return _write(path, "event-food-estimate", "\n".join(lines),
                  f"For {people} guests, plan about {_fmt(food_total/1000, 2)} kg main food and {_fmt(drink_total/1000, 2)} L drinks.")


def fuel_economy_calculator(path: Path) -> dict:
    data = _load_request(path)
    currency = _currency(data.get("currency"))
    places = _minor_units(currency)
    distance = _decimal(data.get("distance_km"), "distance_km", "0.01", 100000000)
    litres = _decimal(data.get("fuel_litres"), "fuel_litres", "0.001", 10000000)
    price = _money(_decimal(data.get("price_per_litre", 0), "price_per_litre", 0, "1000000000"), currency)
    consumption = litres / distance * 100
    cost = _money(litres * price, currency)
    cost_km = _money(cost / distance, currency)
    lines = [
        "Fuel economy calculator",
        f"Distance travelled: {_fmt(distance, 2)} km",
        f"Fuel used: {_fmt(litres, 3)} litres",
        f"Average consumption: {_fmt(consumption, 2)} L/100 km",
        f"Equivalent economy: {_fmt(distance / litres, 2)} km/L",
        f"Fuel price input: {currency} {_fmt(price, places)} per litre",
        f"Estimated fuel cost: {currency} {_fmt(cost, places)}",
        f"Fuel cost per kilometre: {currency} {_fmt(cost_km, places)}",
        "Fuel-only estimate; excludes tolls, parking, maintenance and route differences.",
    ]
    return _write(path, "fuel-economy", "\n".join(lines),
                  f"Average fuel use {_fmt(consumption, 2)} L/100 km; fuel cost {currency} {_fmt(cost, places)}.")


def gas_cylinder_runtime_calculator(path: Path) -> dict:
    data = _load_request(path)
    weight = _decimal(data.get("gas_weight_kg"), "gas_weight_kg", "0.01", 10000)
    consumption = _decimal(data.get("consumption_grams_per_hour"), "consumption_grams_per_hour", "0.01", 1000000)
    reserve = _decimal(data.get("reserve_percent", 10), "reserve_percent", 0, 90)
    hours_per_day = data.get("hours_per_day")
    usable_g = weight * 1000 * (ONE - reserve / 100)
    hours = usable_g / consumption
    lines = [
        "Gas cylinder runtime estimate",
        f"Cylinder gas weight: {_fmt(weight)} kg",
        f"Reserve allowance: {_fmt(reserve)}%",
        f"Usable gas estimate: {_fmt(usable_g, 1)} g",
        f"Appliance consumption: {_fmt(consumption)} g/hour",
        f"Estimated runtime: {_fmt(hours, 1)} hours",
    ]
    summary = f"Estimated runtime about {_fmt(hours, 1)} hours at the stated gas consumption."
    if hours_per_day is not None:
        daily = _decimal(hours_per_day, "hours_per_day", "0.01", 24)
        days = hours / daily
        lines.append(f"At {_fmt(daily)} hours/day: about {_fmt(days, 1)} days")
        summary += f" At {_fmt(daily)} hours/day, approximately {_fmt(days, 1)} days."
    lines.append("Estimate assumes constant burner consumption; flame setting, appliance efficiency and usable residual gas affect real runtime.")
    return _write(path, "gas-cylinder-runtime", "\n".join(lines), summary)


def shipping_volumetric_weight_calculator(path: Path) -> dict:
    data = _load_request(path)
    length = _decimal(data.get("length_cm"), "length_cm", "0.1", 100000)
    width = _decimal(data.get("width_cm"), "width_cm", "0.1", 100000)
    height = _decimal(data.get("height_cm"), "height_cm", "0.1", 100000)
    actual = _decimal(data.get("actual_weight_kg"), "actual_weight_kg", 0, 1000000)
    divisor = _decimal(data.get("volumetric_divisor"), "volumetric_divisor", "1", 1000000)
    volume_cm3 = length * width * height
    volumetric = volume_cm3 / divisor
    billable = max(actual, volumetric)
    lines = [
        "Shipping volumetric weight estimate",
        f"Parcel size: {_fmt(length)} × {_fmt(width)} × {_fmt(height)} cm",
        f"Parcel volume: {_fmt(volume_cm3, 1)} cm³",
        f"Actual weight: {_fmt(actual, 3)} kg",
        f"Volumetric divisor: {_fmt(divisor)} cm³/kg",
        f"Volumetric weight: {_fmt(volumetric, 3)} kg",
        f"Estimated billable weight: {_fmt(billable, 3)} kg",
        "Carrier rules differ; confirm the divisor, rounding increment, minimum charge and dimensional measurement policy with the carrier.",
    ]
    summary = f"Volumetric weight {_fmt(volumetric, 2)} kg; estimated billable weight {_fmt(billable, 2)} kg."
    if data.get("price_per_kg") is not None:
        currency = _currency(data.get("currency"))
        places = _minor_units(currency)
        rate = _money(_decimal(data.get("price_per_kg"), "price_per_kg", 0, "1000000000"), currency)
        cost = _money(billable * rate, currency)
        lines.append(f"Illustrative shipping charge at entered rate: {currency} {_fmt(cost, places)}")
        summary += f" At the entered rate, charge estimate {currency} {_fmt(cost, places)}."
    return _write(path, "shipping-volumetric-weight", "\n".join(lines), summary)


def storage_capacity_calculator(path: Path) -> dict:
    data = _load_request(path)
    capacity = _decimal(data.get("capacity_gb"), "capacity_gb", "0.001", 10000000)
    reserve = _decimal(data.get("reserve_percent", 10), "reserve_percent", 0, 99)
    usable_mb = capacity * 1000 * (ONE - reserve / 100)
    photos = _decimal(data.get("photo_size_mb", 4), "photo_size_mb", "0.001", 1000000)
    video = _decimal(data.get("video_size_mb_per_minute", 150), "video_size_mb_per_minute", "0.001", 1000000)
    document = _decimal(data.get("document_size_mb", 1), "document_size_mb", "0.001", 1000000)
    lines = [
        "Storage capacity estimate",
        f"Nominal capacity: {_fmt(capacity)} GB",
        f"Reserved space: {_fmt(reserve)}%",
        f"Usable estimate: {_fmt(usable_mb / 1000, 2)} GB",
        f"At {_fmt(photos)} MB/photo: about {int(usable_mb // photos):,} photos",
        f"At {_fmt(video)} MB/minute: about {_fmt(usable_mb / video, 1)} minutes of video",
        f"At {_fmt(document)} MB/document: about {int(usable_mb // document):,} documents",
        "Illustrative estimates: actual usable capacity is lower due to formatting, operating system, apps and varying file sizes.",
    ]
    return _write(path, "storage-capacity", "\n".join(lines),
                  f"About {_fmt(usable_mb/1000, 2)} GB usable, or {_fmt(usable_mb/video, 1)} minutes of video at the entered rate.")
