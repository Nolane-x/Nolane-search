"""Wave 45 personal finance, shared trips and moving-day planners.

Processors are offline and deterministic. Money stays separated by currency.
CSV amounts use signed values: negative means money out, positive means money in.
All dates, policies, amounts, service terms and household quantities are user supplied.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

MAX_JSON_BYTES = 2 * 1024 * 1024
CENT = Decimal("0.01")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key.")
        result[key] = value
    return result


def _read_json(path: Path) -> dict:
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


def _text(value, label: str, maximum: int = 120) -> str:
    if not isinstance(value, str):
        raise RuntimeError(f"{label} must be text.")
    result = " ".join(value.split()).strip()
    if not result or len(result) > maximum:
        raise RuntimeError(f"{label} must contain 1 to {maximum} characters.")
    return result


def _decimal(value, label: str, minimum=None, maximum=Decimal("1000000000000")) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise RuntimeError(f"{label} must be a number.")
    try:
        result = Decimal(str(value).strip().replace(",", ""))
    except (InvalidOperation, ValueError, AttributeError):
        raise RuntimeError(f"{label} must be a number.") from None
    if not result.is_finite() or (minimum is not None and result < Decimal(str(minimum))) or result > Decimal(str(maximum)):
        raise RuntimeError(f"{label} is outside the permitted numeric range.")
    return result


def _money(value, label: str, allow_zero=True) -> Decimal:
    result = _decimal(value, label, Decimal("0") if allow_zero else CENT)
    rounded = result.quantize(CENT, rounding=ROUND_HALF_UP)
    if abs(result - rounded) > Decimal("0.0000001"):
        raise RuntimeError(f"{label} must have no more than two decimal places.")
    return rounded


def _integer(value, label: str, minimum: int, maximum: int, default=None) -> int:
    if value is None and default is not None:
        value = default
    result = _decimal(value, label, minimum, maximum)
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


def _currency(value) -> str:
    code = _text(value, "currency", 8).upper()
    if not re.fullmatch(r"[A-Z0-9]{3,8}", code):
        raise RuntimeError("currency must be a 3–8 character code such as VND, USD or EUR.")
    return code


def _fmt(value: Decimal, places=2) -> str:
    rounded = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    rendered = format(rounded, "f")
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def _write(path: Path, suffix: str, body: str, summary: str) -> dict:
    output = path.with_name((path.stem[:64] or "nolane") + "-" + suffix + ".txt")
    output.write_text(body.rstrip() + "\n", encoding="utf-8")
    return {"summary": summary[:500], "output_path": str(output)}


def _row(value, label: str) -> dict:
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be an object.")
    return value


def _list(value, label: str, minimum=1, maximum=300) -> list:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise RuntimeError(f"{label} must contain {minimum} to {maximum} items.")
    return value


def _json_transactions(data: dict) -> list:
    items = _list(data.get("transactions"), "transactions", 1, 20000)
    rows = []
    for i, raw in enumerate(items, 1):
        item = _row(raw, f"transaction {i}")
        day = _date(item.get("date"), f"transaction {i} date")
        description = _text(item.get("description"), f"transaction {i} description", 240)
        amount = _decimal(item.get("amount"), f"transaction {i} amount", Decimal("-1000000000000"))
        currency = _currency(item.get("currency", data.get("default_currency", "VND")))
        category = " ".join(str(item.get("category", "Uncategorised")).split()).strip()[:80] or "Uncategorised"
        rows.append((day, description, amount, currency, category))
    return rows


def _csv_transactions(path: Path) -> list:
    aliases = {
        "date": {"date", "transaction date", "posted date", "booking date", "value date"},
        "description": {"description", "details", "payee", "merchant", "transaction description", "narrative"},
        "amount": {"amount", "signed amount", "transaction amount", "value"},
        "debit": {"debit", "withdrawal", "money out", "outflow"},
        "credit": {"credit", "deposit", "money in", "inflow"},
        "currency": {"currency", "ccy"},
        "category": {"category", "type", "expense category"},
    }
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames:
                raise RuntimeError("CSV file must contain a header row.")
            mapped = {}
            for field, choices in aliases.items():
                match = next((header for header in reader.fieldnames if header and header.strip().casefold() in choices), None)
                if match:
                    mapped[field] = match
            if "date" not in mapped or "description" not in mapped:
                raise RuntimeError("CSV needs date and description/payee columns.")
            if "amount" not in mapped and not ({"debit", "credit"} & mapped.keys()):
                raise RuntimeError("CSV needs an amount column or debit/credit columns.")
            rows = []
            for line_no, raw in enumerate(reader, 2):
                if len(rows) >= 20000:
                    raise RuntimeError("CSV exceeds 20,000 transaction rows.")
                if not any(str(v or "").strip() for v in raw.values()):
                    continue
                day_text = str(raw.get(mapped["date"], "") or "").strip()
                # ISO timestamps are accepted; locale-ambiguous dates are not guessed.
                day = _date(day_text[:10], f"CSV row {line_no} date")
                description = _text(str(raw.get(mapped["description"], "") or ""), f"CSV row {line_no} description", 240)
                if "amount" in mapped:
                    amount_text = str(raw.get(mapped["amount"], "") or "").strip()
                    amount = _decimal(amount_text, f"CSV row {line_no} amount", Decimal("-1000000000000"))
                else:
                    debit_text = str(raw.get(mapped.get("debit", ""), "") or "0").strip() or "0"
                    credit_text = str(raw.get(mapped.get("credit", ""), "") or "0").strip() or "0"
                    debit = _decimal(debit_text, f"CSV row {line_no} debit", 0)
                    credit = _decimal(credit_text, f"CSV row {line_no} credit", 0)
                    if debit and credit:
                        raise RuntimeError(f"CSV row {line_no} cannot contain both debit and credit.")
                    amount = credit - debit
                currency = _currency(str(raw.get(mapped.get("currency", ""), "") or "VND"))
                category = str(raw.get(mapped.get("category", ""), "") or "Uncategorised").strip()[:80] or "Uncategorised"
                rows.append((day, description, amount, currency, category))
    except RuntimeError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise RuntimeError("Could not read the CSV transaction file.") from exc
    if not rows:
        raise RuntimeError("CSV contains no transaction rows.")
    return rows


def bank_csv_expense_analyzer(path: Path) -> dict:
    transactions = _csv_transactions(path) if path.suffix.lower() == ".csv" else _json_transactions(_read_json(path))
    monthly = defaultdict(lambda: {"income": Decimal("0"), "expenses": Decimal("0"), "count": 0})
    categories = defaultdict(lambda: {"expenses": Decimal("0"), "income": Decimal("0"), "count": 0})
    totals = defaultdict(lambda: {"income": Decimal("0"), "expenses": Decimal("0"), "count": 0})
    seen = set()
    duplicates = 0
    for day, description, amount, currency, category in transactions:
        key = (day, description.casefold(), amount, currency)
        if key in seen:
            duplicates += 1
        seen.add(key)
        direction = "income" if amount > 0 else "expenses"
        magnitude = abs(amount)
        month_key = (currency, day.strftime("%Y-%m"))
        category_key = (currency, category)
        monthly[month_key][direction] += magnitude
        monthly[month_key]["count"] += 1
        categories[category_key][direction] += magnitude
        categories[category_key]["count"] += 1
        totals[currency][direction] += magnitude
        totals[currency]["count"] += 1
    lines = [
        "Bank CSV expense summary", f"Transactions analysed: {len(transactions)}",
        f"Possible exact duplicate rows: {duplicates}",
        "Amounts are grouped by currency; negative values are outflows and positive values are inflows.",
        "No transaction is deleted or changed. Category totals use the supplied CSV category column; blank categories are Uncategorised.",
        "",
        "TOTALS BY CURRENCY",
    ]
    for currency in sorted(totals):
        row = totals[currency]
        lines.append(f"- {currency}: income {_fmt(row['income'])}; expenses {_fmt(row['expenses'])}; net {_fmt(row['income'] - row['expenses'])}; rows {row['count']}")
    lines.extend(["", "MONTHLY TOTALS"])
    for (currency, month), row in sorted(monthly.items()):
        lines.append(f"- {month} | {currency} | income {_fmt(row['income'])} | expenses {_fmt(row['expenses'])} | net {_fmt(row['income'] - row['expenses'])} | rows {row['count']}")
    lines.extend(["", "EXPENSES BY CATEGORY"])
    for (currency, category), row in sorted(categories.items(), key=lambda pair: (pair[0][0], -pair[1]["expenses"], pair[0][1].casefold())):
        lines.append(f"- {currency} | {category} | expenses {_fmt(row['expenses'])} | income {_fmt(row['income'])} | rows {row['count']}")
    lines.extend(["", "Review possible duplicate rows before making any changes to your bank records."])
    return _write(path, "bank-expense-summary", "\n".join(lines), f"Summarised {len(transactions)} transactions across {len(totals)} currency group(s).")


def _add_months(value: date, months: int) -> date:
    absolute = value.year * 12 + value.month - 1 + months
    year, month_zero = divmod(absolute, 12)
    month = month_zero + 1
    import calendar
    return date(year, month, min(value.day, calendar.monthrange(year, month)[1]))


def _occurrence(first: date, recurrence: str, index: int) -> date:
    if recurrence == "once":
        return first
    if recurrence == "weekly":
        return first + timedelta(days=7 * index)
    if recurrence == "monthly":
        return _add_months(first, index)
    if recurrence == "quarterly":
        return _add_months(first, index * 3)
    if recurrence == "yearly":
        return _add_months(first, index * 12)
    raise RuntimeError("recurrence must be once, weekly, monthly, quarterly or yearly.")


def bill_cashflow_calendar_planner(path: Path) -> dict:
    data = _read_json(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    horizon = _integer(data.get("horizon_days", 90), "horizon_days", 1, 730)
    end = as_of + timedelta(days=horizon)
    opening = {}
    for i, item in enumerate(data.get("opening_balances", []), 1):
        item = _row(item, f"opening balance {i}")
        currency = _currency(item.get("currency"))
        if currency in opening:
            raise RuntimeError(f"opening balance currency {currency} is duplicated.")
        opening[currency] = _money(item.get("amount"), f"opening balance {i} amount")
    events = _list(data.get("events"), "events", 1, 250)
    expanded = []
    for i, raw in enumerate(events, 1):
        item = _row(raw, f"event {i}")
        name = _text(item.get("name"), f"event {i} name", 100)
        amount = _money(item.get("amount"), f"{name} amount", allow_zero=False)
        currency = _currency(item.get("currency"))
        direction = str(item.get("direction", "")).strip().lower()
        if direction not in {"income", "expense"}:
            raise RuntimeError(f"{name}: direction must be income or expense.")
        first = _date(item.get("first_date"), f"{name} first_date")
        last = _date(item["last_date"], f"{name} last_date") if item.get("last_date") else end
        recurrence = str(item.get("recurrence", "once")).strip().lower()
        if recurrence not in {"once", "weekly", "monthly", "quarterly", "yearly"}:
            raise RuntimeError(f"{name}: unsupported recurrence.")
        if last < first:
            raise RuntimeError(f"{name}: last_date cannot precede first_date.")
        if recurrence == "once":
            occurrences = [first] if as_of <= first <= min(end, last) else []
        else:
            occurrences = []
            for index in range(3000):
                day = _occurrence(first, recurrence, index)
                if day > min(end, last):
                    break
                if day >= as_of:
                    occurrences.append(day)
            else:
                raise RuntimeError(f"{name}: recurrence exceeds the supported schedule limit.")
        for day in occurrences:
            signed = amount if direction == "income" else -amount
            expanded.append((day, name, currency, signed, direction))
            if len(expanded) > 5000:
                raise RuntimeError("Expanded cash-flow calendar exceeds 5,000 events.")
    expanded.sort(key=lambda row: (row[0], row[2], row[1].casefold()))
    balances = defaultdict(Decimal)
    balances.update(opening)
    totals = defaultdict(lambda: {"income": Decimal("0"), "expenses": Decimal("0"), "count": 0})
    lines = [
        "Recurring bills and cash-flow calendar", f"As of: {as_of.isoformat()}",
        f"Forecast window: {horizon} days (through {end.isoformat()})",
        "Each currency is forecast separately. Amounts and recurrence rules are user supplied; this is not a bank balance or guarantee of future payment.",
        "",
        "SCHEDULE",
    ]
    if not expanded:
        lines.append("- No due events fall inside the selected window.")
    for day, name, currency, signed, direction in expanded:
        balances[currency] += signed
        totals[currency][direction] += abs(signed)
        totals[currency]["count"] += 1
        lines.append(f"- {day.isoformat()} | {name} | {direction} {_fmt(abs(signed))} {currency} | projected balance {_fmt(balances[currency])} {currency}")
    lines.extend(["", "FORECAST TOTALS"])
    for currency in sorted(set(balances) | set(totals)):
        row = totals[currency]
        lines.append(f"- {currency}: opening {_fmt(opening.get(currency, Decimal('0')))} | income {_fmt(row['income'])} | bills/expenses {_fmt(row['expenses'])} | projected closing {_fmt(balances[currency])}")
    return _write(path, "bill-cashflow-calendar", "\n".join(lines), f"Scheduled {len(expanded)} recurring/one-off cash-flow events through {end.isoformat()}.")


def shared_expense_settler(path: Path) -> dict:
    data = _read_json(path)
    currency = _currency(data.get("currency"))
    participants = [_text(name, "participant name", 80) for name in _list(data.get("participants"), "participants", 2, 100)]
    if len({name.casefold() for name in participants}) != len(participants):
        raise RuntimeError("Participant names must be unique, ignoring letter case.")
    balances = {name: Decimal("0.00") for name in participants}
    expenses = _list(data.get("expenses"), "expenses", 1, 500)
    for i, raw in enumerate(expenses, 1):
        item = _row(raw, f"expense {i}")
        name = _text(item.get("name"), f"expense {i} name", 120)
        amount = _money(item.get("amount"), f"{name} amount", allow_zero=False)
        payer = _text(item.get("paid_by"), f"{name} paid_by", 80)
        if payer not in balances:
            raise RuntimeError(f"{name}: paid_by must be a listed participant.")
        split_among = item.get("split_among", participants)
        if not isinstance(split_among, list) or not split_among:
            raise RuntimeError(f"{name}: split_among must contain at least one participant.")
        split_among = [_text(person, f"{name} split participant", 80) for person in split_among]
        if len(set(split_among)) != len(split_among) or any(person not in balances for person in split_among):
            raise RuntimeError(f"{name}: split_among contains duplicate or unknown participants.")
        shares = item.get("shares")
        if shares is None:
            cents = int(amount * 100)
            base, remainder = divmod(cents, len(split_among))
            share_values = {person: Decimal(base + (1 if j < remainder else 0)) / 100 for j, person in enumerate(split_among)}
        else:
            if not isinstance(shares, list) or len(shares) != len(split_among):
                raise RuntimeError(f"{name}: shares must provide one amount for every split participant.")
            share_values = {}
            for share in shares:
                share = _row(share, f"{name} share")
                person = _text(share.get("participant"), f"{name} share participant", 80)
                if person not in split_among or person in share_values:
                    raise RuntimeError(f"{name}: shares contains an unknown or duplicated participant.")
                share_values[person] = _money(share.get("amount"), f"{name} share amount")
            if set(share_values) != set(split_among) or sum(share_values.values(), Decimal("0")) != amount:
                raise RuntimeError(f"{name}: custom share amounts must add up exactly to the expense total.")
        balances[payer] += amount
        for person, share in share_values.items():
            balances[person] -= share
    settlements = data.get("settlements", [])
    if not isinstance(settlements, list) or len(settlements) > 500:
        raise RuntimeError("settlements must contain up to 500 payments.")
    for i, raw in enumerate(settlements, 1):
        item = _row(raw, f"settlement {i}")
        sender = _text(item.get("from"), f"settlement {i} from", 80)
        recipient = _text(item.get("to"), f"settlement {i} to", 80)
        amount = _money(item.get("amount"), f"settlement {i} amount", allow_zero=False)
        if sender not in balances or recipient not in balances or sender == recipient:
            raise RuntimeError(f"settlement {i} must move money between two different listed participants.")
        balances[sender] += amount
        balances[recipient] -= amount
    cents = sum((int((value * 100).to_integral_value()) for value in balances.values()), 0)
    if cents != 0:
        raise RuntimeError("Internal settlement balances do not net to zero; review the provided expense splits.")
    debtors = [[name, -amount] for name, amount in balances.items() if amount < 0]
    creditors = [[name, amount] for name, amount in balances.items() if amount > 0]
    debtors.sort(key=lambda row: (-row[1], row[0].casefold()))
    creditors.sort(key=lambda row: (-row[1], row[0].casefold()))
    transfers = []
    di = ci = 0
    while di < len(debtors) and ci < len(creditors):
        debtor, debt = debtors[di]
        creditor, credit = creditors[ci]
        amount = min(debt, credit).quantize(CENT)
        if amount > 0:
            transfers.append((debtor, creditor, amount))
        debtors[di][1] -= amount
        creditors[ci][1] -= amount
        if debtors[di][1] == 0:
            di += 1
        if creditors[ci][1] == 0:
            ci += 1
    lines = [
        "Shared expense settlement", f"Currency: {currency}",
        f"Participants: {len(participants)} | Expenses: {len(expenses)}",
        "Net balances are based on listed expenses and any payments already made. Transfers are a compact settlement plan, not proof that payment occurred.",
        "",
        "NET BALANCES (positive = should receive; negative = should pay)",
    ]
    for name in participants:
        state = "receive" if balances[name] > 0 else ("pay" if balances[name] < 0 else "settled")
        lines.append(f"- {name}: {_fmt(abs(balances[name]))} {currency} ({state})")
    lines.extend(["", "SUGGESTED TRANSFERS"])
    if transfers:
        for sender, recipient, amount in transfers:
            lines.append(f"- {sender} pays {recipient}: {_fmt(amount)} {currency}")
    else:
        lines.append("- Everyone is settled.")
    lines.extend(["", "Confirm the figures and the group's agreement before sending money."])
    return _write(path, "shared-expense-settlement", "\n".join(lines), f"Calculated {len(transfers)} suggested transfer(s) for {len(participants)} people.")


def moving_day_checklist_planner(path: Path) -> dict:
    data = _read_json(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    move_date = _date(data.get("move_date"), "move_date")
    if move_date < as_of:
        raise RuntimeError("move_date cannot be before as_of_date.")
    tasks = _list(data.get("tasks"), "tasks", 1, 250)
    parsed = []
    workload = defaultdict(int)
    for i, raw in enumerate(tasks, 1):
        item = _row(raw, f"task {i}")
        name = _text(item.get("name"), f"task {i} name", 120)
        days_before = _integer(item.get("days_before_move"), f"{name} days_before_move", 0, 3650)
        minutes = _integer(item.get("estimated_minutes", 30), f"{name} estimated_minutes", 1, 1440)
        assignee = " ".join(str(item.get("assignee", "")).split()).strip()[:80] or "Unassigned"
        priority = str(item.get("priority", "normal")).strip().lower()
        if priority not in {"low", "normal", "high", "urgent"}:
            raise RuntimeError(f"{name}: priority must be low, normal, high or urgent.")
        complete = item.get("completed", False)
        if not isinstance(complete, bool):
            raise RuntimeError(f"{name}: completed must be true or false.")
        due = move_date - timedelta(days=days_before)
        state = "Completed" if complete else ("OVERDUE" if due < as_of else ("Due today" if due == as_of else "Upcoming"))
        parsed.append((due, priority, name, assignee, minutes, state, days_before))
        workload[assignee] += minutes
    order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
    parsed.sort(key=lambda row: (row[0], order[row[1]], row[2].casefold()))
    lines = [
        "Moving-day checklist", f"Today: {as_of.isoformat()}",
        f"Moving day: {move_date.isoformat()}", f"Days remaining: {(move_date - as_of).days}",
        "",
        "TASK SCHEDULE",
    ]
    for due, priority, name, assignee, minutes, state, days_before in parsed:
        lines.append(f"- {due.isoformat()} | {name} | {state} | {priority} priority | {assignee} | {minutes} min | {days_before} day(s) before moving")
    lines.extend(["", "ESTIMATED WORKLOAD BY PERSON"])
    for assignee, minutes in sorted(workload.items(), key=lambda row: row[0].casefold()):
        lines.append(f"- {assignee}: {minutes} min ({minutes // 60} h {minutes % 60} min)")
    overdue = sum(1 for row in parsed if row[5] == "OVERDUE")
    lines.extend(["", f"Overdue tasks not marked complete: {overdue}. Adjust dates to match bookings, landlord/utility arrangements and the actual move plan."])
    return _write(path, "moving-day-checklist", "\n".join(lines), f"Scheduled {len(parsed)} moving tasks; {overdue} are overdue.")


def moving_box_label_maker(path: Path) -> dict:
    data = _read_json(path)
    boxes = _list(data.get("boxes"), "boxes", 1, 300)
    seen = set()
    parsed = []
    room_counts = defaultdict(int)
    for i, raw in enumerate(boxes, 1):
        item = _row(raw, f"box {i}")
        box_id = _text(item.get("box_id"), f"box {i} box_id", 24)
        if box_id.casefold() in seen:
            raise RuntimeError(f"Duplicate box ID: {box_id}.")
        seen.add(box_id.casefold())
        room = _text(item.get("room"), f"box {i} room", 60)
        contents = _list(item.get("contents"), f"{box_id} contents", 1, 30)
        contents = [_text(entry, f"{box_id} content", 100) for entry in contents]
        fragile = item.get("fragile", False)
        open_first = item.get("open_first", False)
        heavy = item.get("heavy", False)
        if any(not isinstance(v, bool) for v in (fragile, open_first, heavy)):
            raise RuntimeError(f"{box_id}: fragile, open_first and heavy must be true or false.")
        notes = " ".join(str(item.get("notes", "")).split()).strip()[:120]
        room_counts[room] += 1
        parsed.append({"id": box_id, "room": room, "contents": contents, "fragile": fragile, "open_first": open_first, "heavy": heavy, "notes": notes})
    parsed.sort(key=lambda row: (not row["open_first"], row["room"].casefold(), row["id"].casefold()))
    lines = [
        "Moving box labels", f"Total boxes: {len(parsed)}",
        "Print or copy each label and attach it to at least two visible sides of its box.",
        "",
    ]
    for box in parsed:
        flags = []
        if box["open_first"]:
            flags.append("OPEN FIRST")
        if box["fragile"]:
            flags.append("FRAGILE")
        if box["heavy"]:
            flags.append("HEAVY")
        lines.extend([
            "=" * 44,
            f"BOX {box['id']}  |  ROOM: {box['room'].upper()}",
            "FLAGS: " + (", ".join(flags) if flags else "STANDARD"),
            "CONTENTS:",
        ])
        lines.extend("- " + value for value in box["contents"])
        if box["notes"]:
            lines.append("NOTES: " + box["notes"])
        lines.append("=" * 44)
    lines.extend(["", "BOX COUNT BY ROOM"])
    for room, count in sorted(room_counts.items(), key=lambda row: row[0].casefold()):
        lines.append(f"- {room}: {count}")
    return _write(path, "moving-box-labels", "\n".join(lines), f"Created printable labels for {len(parsed)} boxes in {len(room_counts)} room(s).")


def return_deadline_tracker(path: Path) -> dict:
    data = _read_json(path)
    as_of = _date(data.get("as_of_date"), "as_of_date")
    notice = _integer(data.get("default_remind_days", 5), "default_remind_days", 0, 90)
    purchases = _list(data.get("purchases"), "purchases", 1, 200)
    rows = []
    for i, raw in enumerate(purchases, 1):
        item = _row(raw, f"purchase {i}")
        product = _text(item.get("product"), f"purchase {i} product", 120)
        seller = _text(item.get("seller"), f"{product} seller", 120)
        purchased = _date(item.get("purchase_date"), f"{product} purchase_date")
        days = _integer(item.get("return_window_days"), f"{product} return_window_days", 0, 730)
        reminder = _integer(item.get("remind_days_before", notice), f"{product} remind_days_before", 0, 90)
        started = item.get("return_started", False)
        if not isinstance(started, bool):
            raise RuntimeError(f"{product}: return_started must be true or false.")
        deadline = purchased + timedelta(days=days)
        if started:
            state = "Return already started (user-marked)"
        elif as_of > deadline:
            state = "RETURN WINDOW MAY HAVE PASSED"
        elif deadline - as_of <= timedelta(days=reminder):
            state = "Check return now"
        elif deadline - as_of <= timedelta(days=30):
            state = "Deadline approaching"
        else:
            state = "Within stated return window"
        rows.append((deadline, product.casefold(), product, seller, purchased, days, state, started))
    rows.sort(key=lambda row: (row[0], row[1]))
    lines = [
        "Product return deadline tracker", f"As of: {as_of.isoformat()}",
        "Deadlines are calculated as purchase date + the return-window length entered by the user. Retailer policies may count days differently and may have exclusions.",
        "",
    ]
    for deadline, _, product, seller, purchased, days, state, started in rows:
        lines.append(f"- {product} | {seller} | {state} | purchased {purchased.isoformat()} | entered window {days} days | estimated last date {deadline.isoformat()}")
    lines.extend(["", "Check the seller's current terms, proof-of-purchase rules, item condition, delivery/collection deadlines and any statutory rights for the place of purchase. This tool does not determine legal eligibility."])
    return _write(path, "return-deadlines", "\n".join(lines), f"Tracked {len(rows)} return deadline(s).")


def gift_budget_planner(path: Path) -> dict:
    data = _read_json(path)
    currency = _currency(data.get("currency"))
    total_budget = _money(data.get("total_budget"), "total_budget")
    recipients = _list(data.get("recipients"), "recipients", 1, 200)
    used_names = set()
    planned_total = Decimal("0.00")
    purchased_total = Decimal("0.00")
    rows = []
    for i, raw in enumerate(recipients, 1):
        item = _row(raw, f"recipient {i}")
        name = _text(item.get("name"), f"recipient {i} name", 100)
        if name.casefold() in used_names:
            raise RuntimeError("Recipient names must be unique.")
        used_names.add(name.casefold())
        limit = _money(item.get("budget"), f"{name} budget")
        gifts = item.get("gifts", [])
        if not isinstance(gifts, list) or len(gifts) > 30:
            raise RuntimeError(f"{name}: gifts must contain up to 30 items.")
        recipient_planned = Decimal("0.00")
        recipient_purchased = Decimal("0.00")
        gift_items = []
        for gift in gifts:
            gift = _row(gift, f"{name} gift")
            gift_name = _text(gift.get("item"), f"{name} gift item", 100)
            price = _money(gift.get("price"), f"{name} gift price")
            purchased = gift.get("purchased", False)
            if not isinstance(purchased, bool):
                raise RuntimeError(f"{name}: purchased must be true or false.")
            recipient_planned += price
            if purchased:
                recipient_purchased += price
            gift_items.append((gift_name, price, purchased))
        planned_total += recipient_planned
        purchased_total += recipient_purchased
        rows.append((name, limit, recipient_planned, recipient_purchased, gift_items))
    lines = [
        "Gift budget plan", f"Currency: {currency}",
        f"Overall budget: {_fmt(total_budget)} {currency}",
        f"Planned gifts: {_fmt(planned_total)} {currency}",
        f"Already purchased: {_fmt(purchased_total)} {currency}",
        f"Overall budget remaining: {_fmt(total_budget - planned_total)} {currency}",
        "",
    ]
    for name, limit, planned, purchased, gifts in rows:
        lines.append(f"{name} | allowance {_fmt(limit)} {currency} | planned {_fmt(planned)} | purchased {_fmt(purchased)} | remaining allowance {_fmt(limit - planned)}")
        for gift_name, price, is_purchased in gifts:
            lines.append(f"  - {gift_name}: {_fmt(price)} {currency} ({'purchased' if is_purchased else 'not yet purchased'})")
    if planned_total > total_budget:
        lines.append(f"WARNING: planned gifts exceed the overall budget by {_fmt(planned_total - total_budget)} {currency}.")
    return _write(path, "gift-budget", "\n".join(lines), f"Planned {_fmt(planned_total)} {currency} across {len(recipients)} recipients.")


def household_emergency_kit_planner(path: Path) -> dict:
    data = _read_json(path)
    household_size = _integer(data.get("household_size"), "household_size", 1, 100)
    days = _integer(data.get("days"), "days", 1, 90)
    items = _list(data.get("items"), "items", 1, 200)
    groups = defaultdict(list)
    total_deficit_count = 0
    lines = [
        "Household emergency-supplies checklist",
        f"Household size: {household_size} | Planning duration: {days} day(s)",
        "Quantities are calculated only from the per-person/per-day and per-household amounts you enter. This is not an official safety standard or a guarantee of preparedness.",
        "",
    ]
    for i, raw in enumerate(items, 1):
        item = _row(raw, f"item {i}")
        name = _text(item.get("name"), f"item {i} name", 100)
        category = " ".join(str(item.get("category", "General")).split()).strip()[:60] or "General"
        unit = _text(item.get("unit"), f"{name} unit", 30)
        per_person_day = _decimal(item.get("per_person_per_day", 0), f"{name} per_person_per_day", 0)
        per_household = _decimal(item.get("per_household", 0), f"{name} per_household", 0)
        on_hand = _decimal(item.get("on_hand", 0), f"{name} on_hand", 0)
        required = per_person_day * household_size * days + per_household
        missing = max(Decimal("0"), required - on_hand)
        if missing > 0:
            total_deficit_count += 1
        groups[category].append((name, required, on_hand, missing, unit))
    for category, rows in sorted(groups.items(), key=lambda row: row[0].casefold()):
        lines.append(category.upper())
        for name, required, on_hand, missing, unit in rows:
            lines.append(f"- {name}: target {_fmt(required, 3)} {unit} | on hand {_fmt(on_hand, 3)} {unit} | still needed {_fmt(missing, 3)} {unit}")
    lines.extend(["", f"Items with a remaining shortfall: {total_deficit_count}.",
                  "Review local authority guidance for hazards in your area, household-specific needs, storage limits, expiry dates and safe handling. Add or remove items to match your actual plan."])
    return _write(path, "emergency-kit-checklist", "\n".join(lines), f"Calculated user-defined quantities for {len(items)} supplies, with {total_deficit_count} shortfall(s).")
