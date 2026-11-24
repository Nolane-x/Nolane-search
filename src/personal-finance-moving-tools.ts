export const PERSONAL_FINANCE_MOVING_TOOL_IDS = new Set([
  "bank-csv-expense-analyzer",
  "bill-cashflow-calendar-planner",
  "shared-expense-settler",
  "moving-day-checklist-planner",
  "moving-box-label-maker",
  "return-deadline-tracker",
  "gift-budget-planner",
  "household-emergency-kit-planner",
]);

type Input = Record<string, unknown>;
type Row = Record<string, unknown>;

function parseInput(content: string): Input {
  let value: unknown;
  try { value = JSON.parse(content); }
  catch { throw new Error("Gửi dữ liệu JSON hợp lệ cho công cụ này."); }
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Dữ liệu phải là một JSON object.");
  return value as Input;
}
function row(value: unknown, label: string): Row {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(label + " phải là object.");
  return value as Row;
}
function textValue(value: unknown, key: string, max = 120): string {
  if (typeof value !== "string") throw new Error(key + " phải là văn bản.");
  const result = value.trim().replace(/\s+/g, " ");
  if (!result || result.length > max) throw new Error(key + " phải có từ 1 đến " + max + " ký tự.");
  return result;
}
function numberValue(value: unknown, key: string, min = 0, max = 1_000_000_000_000): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) {
    throw new Error(key + " phải là số hữu hạn trong phạm vi hợp lệ.");
  }
  return value;
}
function centsValue(value: unknown, key: string, allowZero = true): number {
  const n = numberValue(value, key, allowZero ? 0 : 0.01);
  const cents = Math.round(n * 100);
  if (Math.abs(n * 100 - cents) > 1e-6) throw new Error(key + " chỉ được có tối đa hai chữ số thập phân.");
  return cents;
}
function integerValue(value: unknown, key: string, min: number, max: number, fallback?: number): number {
  const v = value === undefined ? fallback : value;
  const n = numberValue(v, key, min, max);
  if (!Number.isInteger(n)) throw new Error(key + " phải là số nguyên.");
  return n;
}
function parseDate(value: unknown, key: string): Date {
  const raw = textValue(value, key, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(raw)) throw new Error(key + " phải có định dạng YYYY-MM-DD.");
  const result = new Date(raw + "T00:00:00.000Z");
  if (Number.isNaN(result.getTime()) || result.toISOString().slice(0, 10) !== raw) throw new Error(key + " không phải ngày hợp lệ.");
  return result;
}
function dateKey(value: Date): string { return value.toISOString().slice(0, 10); }
function addDays(value: Date, days: number): Date { return new Date(value.getTime() + days * 86400000); }
function monthAdd(value: Date, months: number): Date {
  const total = value.getUTCFullYear() * 12 + value.getUTCMonth() + months;
  const year = Math.floor(total / 12), month = total % 12;
  const day = Math.min(value.getUTCDate(), new Date(Date.UTC(year, month + 1, 0)).getUTCDate());
  return new Date(Date.UTC(year, month, day));
}
function currency(value: unknown): string {
  const code = textValue(value, "currency", 8).toUpperCase();
  if (!/^[A-Z0-9]{3,8}$/.test(code)) throw new Error("currency phải là mã 3–8 ký tự như VND, USD hoặc EUR.");
  return code;
}
function fmtCents(cents: number): string {
  const rendered = (cents / 100).toFixed(2);
  return rendered.replace(/\.?0+$/, "");
}
function fmt(value: number, places = 3): string { return Number(value.toFixed(places)).toString(); }
function list(value: unknown, key: string, min = 1, max = 300): unknown[] {
  if (!Array.isArray(value) || value.length < min || value.length > max) throw new Error(key + " phải có từ " + min + " đến " + max + " mục.");
  return value;
}
function sortNames(a: string, b: string): number { return a.localeCompare(b, "en", { sensitivity: "base" }); }

function bankExpenseSummary(input: Input): string {
  const transactions = list(input.transactions, "transactions", 1, 20000).map((raw, index) => {
    const item = row(raw, "transaction " + (index + 1));
    const day = parseDate(item.date, "transaction " + (index + 1) + " date");
    const description = textValue(item.description, "transaction description", 240);
    const amount = numberValue(item.amount, "transaction amount", -1_000_000_000_000, 1_000_000_000_000);
    const code = currency(item.currency ?? input.default_currency ?? "VND");
    const category = typeof item.category === "string" && item.category.trim() ? item.category.trim().slice(0, 80) : "Uncategorised";
    return { day, description, cents: Math.round(amount * 100), currency: code, category };
  });
  const month = new Map<string, { income: number; expenses: number; count: number }>();
  const categories = new Map<string, { income: number; expenses: number; count: number }>();
  const totals = new Map<string, { income: number; expenses: number; count: number }>();
  const seen = new Set<string>();
  let duplicates = 0;
  const ensure = (map: Map<string, { income: number; expenses: number; count: number }>, key: string) => {
    if (!map.has(key)) map.set(key, { income: 0, expenses: 0, count: 0 });
    return map.get(key)!;
  };
  for (const tx of transactions) {
    const key = [dateKey(tx.day), tx.description.toLocaleLowerCase(), tx.cents, tx.currency].join("|");
    if (seen.has(key)) duplicates++;
    seen.add(key);
    const direction = tx.cents > 0 ? "income" : "expenses";
    const amount = Math.abs(tx.cents);
    const m = ensure(month, tx.currency + "|" + dateKey(tx.day).slice(0, 7));
    const c = ensure(categories, tx.currency + "|" + tx.category);
    const t = ensure(totals, tx.currency);
    m[direction] += amount; m.count++;
    c[direction] += amount; c.count++;
    t[direction] += amount; t.count++;
  }
  const lines = ["Bank CSV expense summary", "Transactions analysed: " + transactions.length,
    "Possible exact duplicate rows: " + duplicates,
    "Amounts are grouped by currency; negative values are outflows and positive values are inflows.",
    "Category totals use the supplied category; blank categories are Uncategorised.", "", "TOTALS BY CURRENCY"];
  for (const code of [...totals.keys()].sort()) {
    const t = totals.get(code)!;
    lines.push("- " + code + ": income " + fmtCents(t.income) + "; expenses " + fmtCents(t.expenses) +
      "; net " + fmtCents(t.income - t.expenses) + "; rows " + t.count);
  }
  lines.push("", "MONTHLY TOTALS");
  for (const [key, value] of [...month.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const [code, period] = key.split("|");
    lines.push("- " + period + " | " + code + " | income " + fmtCents(value.income) + " | expenses " +
      fmtCents(value.expenses) + " | net " + fmtCents(value.income - value.expenses) + " | rows " + value.count);
  }
  lines.push("", "EXPENSES BY CATEGORY");
  for (const [key, value] of [...categories.entries()].sort((a, b) => {
    const [ca, na] = a[0].split("|"), [cb, nb] = b[0].split("|");
    return ca!.localeCompare(cb!) || b[1].expenses - a[1].expenses || na!.localeCompare(nb!);
  })) {
    const [code, name] = key.split("|");
    lines.push("- " + code + " | " + name + " | expenses " + fmtCents(value.expenses) + " | income " +
      fmtCents(value.income) + " | rows " + value.count);
  }
  lines.push("", "Review possible duplicate rows before making changes to your bank records.");
  return lines.join("\n");
}

function billCashflow(input: Input): string {
  const asOf = parseDate(input.as_of_date, "as_of_date");
  const horizon = integerValue(input.horizon_days, "horizon_days", 1, 730, 90);
  const end = addDays(asOf, horizon);
  const opening = new Map<string, number>();
  for (const [index, raw] of (Array.isArray(input.opening_balances) ? input.opening_balances : []).entries()) {
    const item = row(raw, "opening balance " + (index + 1));
    const code = currency(item.currency);
    if (opening.has(code)) throw new Error("opening balance " + code + " bị trùng.");
    opening.set(code, centsValue(item.amount, "opening balance amount"));
  }
  const occurrences: Array<{ day: Date; name: string; currency: string; signed: number; direction: string }> = [];
  const events = list(input.events, "events", 1, 250);
  for (const [index, raw] of events.entries()) {
    const item = row(raw, "event " + (index + 1));
    const name = textValue(item.name, "event name", 100);
    const amount = centsValue(item.amount, name + " amount", false);
    const code = currency(item.currency);
    const direction = String(item.direction ?? "").trim().toLowerCase();
    if (direction !== "income" && direction !== "expense") throw new Error(name + ": direction phải là income hoặc expense.");
    const first = parseDate(item.first_date, name + " first_date");
    const last = item.last_date === undefined ? end : parseDate(item.last_date, name + " last_date");
    if (last.getTime() < first.getTime()) throw new Error(name + ": last_date không được trước first_date.");
    const recurrence = String(item.recurrence ?? "once").trim().toLowerCase();
    if (!["once", "weekly", "monthly", "quarterly", "yearly"].includes(recurrence)) throw new Error(name + ": recurrence không được hỗ trợ.");
    const maxDate = last.getTime() < end.getTime() ? last : end;
    for (let n = 0; n < 3000; n++) {
      let day: Date;
      if (recurrence === "once") day = first;
      else if (recurrence === "weekly") day = addDays(first, n * 7);
      else if (recurrence === "monthly") day = monthAdd(first, n);
      else if (recurrence === "quarterly") day = monthAdd(first, n * 3);
      else day = monthAdd(first, n * 12);
      if (day.getTime() > maxDate.getTime()) break;
      if (day.getTime() >= asOf.getTime()) {
        const signed = direction === "income" ? amount : -amount;
        occurrences.push({ day, name, currency: code, signed, direction });
        if (occurrences.length > 5000) throw new Error("Lịch dòng tiền vượt quá 5.000 sự kiện.");
      }
      if (recurrence === "once") break;
      if (n === 2999) throw new Error(name + ": lịch lặp vượt giới hạn.");
    }
  }
  occurrences.sort((a, b) => a.day.getTime() - b.day.getTime() || a.currency.localeCompare(b.currency) || sortNames(a.name, b.name));
  const balances = new Map<string, number>(opening);
  const totals = new Map<string, { income: number; expenses: number; count: number }>();
  const lines = ["Recurring bills and cash-flow calendar", "As of: " + dateKey(asOf),
    "Forecast window: " + horizon + " days (through " + dateKey(end) + ")",
    "Each currency is forecast separately. Amounts and recurrence rules are user supplied; this is not a bank balance or guarantee of future payment.", "", "SCHEDULE"];
  if (!occurrences.length) lines.push("- No due events fall inside the selected window.");
  for (const event of occurrences) {
    const balance = (balances.get(event.currency) ?? 0) + event.signed;
    balances.set(event.currency, balance);
    if (!totals.has(event.currency)) totals.set(event.currency, { income: 0, expenses: 0, count: 0 });
    const total = totals.get(event.currency)!;
    total[event.direction as "income" | "expenses"] += Math.abs(event.signed);
    total.count++;
    lines.push("- " + dateKey(event.day) + " | " + event.name + " | " + event.direction + " " +
      fmtCents(Math.abs(event.signed)) + " " + event.currency + " | projected balance " + fmtCents(balance) + " " + event.currency);
  }
  lines.push("", "FORECAST TOTALS");
  for (const code of [...new Set([...balances.keys(), ...totals.keys()])].sort()) {
    const total = totals.get(code) ?? { income: 0, expenses: 0, count: 0 };
    lines.push("- " + code + ": opening " + fmtCents(opening.get(code) ?? 0) + " | income " + fmtCents(total.income) +
      " | bills/expenses " + fmtCents(total.expenses) + " | projected closing " + fmtCents(balances.get(code) ?? 0));
  }
  return lines.join("\n");
}

function sharedExpenseSettle(input: Input): string {
  const code = currency(input.currency);
  const participants = list(input.participants, "participants", 2, 100).map((value, i) => textValue(value, "participant " + (i + 1), 80));
  if (new Set(participants.map(p => p.toLocaleLowerCase())).size !== participants.length) throw new Error("Tên người tham gia phải khác nhau.");
  const balances = new Map(participants.map(p => [p, 0]));
  const expenses = list(input.expenses, "expenses", 1, 500);
  for (const [index, raw] of expenses.entries()) {
    const item = row(raw, "expense " + (index + 1));
    const name = textValue(item.name, "expense name", 120);
    const amount = centsValue(item.amount, name + " amount", false);
    const payer = textValue(item.paid_by, name + " paid_by", 80);
    if (!balances.has(payer)) throw new Error(name + ": paid_by phải là người trong danh sách.");
    const split = (item.split_among === undefined ? participants : list(item.split_among, name + " split_among", 1, 100))
      .map((v, i) => textValue(v, name + " split participant " + (i + 1), 80));
    if (new Set(split).size !== split.length || split.some(p => !balances.has(p))) throw new Error(name + ": split_among có tên trùng hoặc không hợp lệ.");
    let shares = new Map<string, number>();
    if (item.shares === undefined) {
      const base = Math.floor(amount / split.length), remainder = amount % split.length;
      split.forEach((person, i) => shares.set(person, base + (i < remainder ? 1 : 0)));
    } else {
      const rawShares = list(item.shares, name + " shares", 1, 100);
      for (const rawShare of rawShares) {
        const share = row(rawShare, name + " share");
        const person = textValue(share.participant, name + " share participant", 80);
        if (!split.includes(person) || shares.has(person)) throw new Error(name + ": shares có người trùng hoặc không thuộc split_among.");
        shares.set(person, centsValue(share.amount, name + " share amount"));
      }
      if (shares.size !== split.length || [...shares.values()].reduce((a, b) => a + b, 0) !== amount) {
        throw new Error(name + ": tổng các khoản chia phải bằng đúng tổng chi phí.");
      }
    }
    balances.set(payer, balances.get(payer)! + amount);
    for (const [person, share] of shares) balances.set(person, balances.get(person)! - share);
  }
  const settlements = input.settlements === undefined ? [] : list(input.settlements, "settlements", 0, 500);
  for (const [index, raw] of settlements.entries()) {
    const item = row(raw, "settlement " + (index + 1));
    const from = textValue(item.from, "settlement from", 80), to = textValue(item.to, "settlement to", 80);
    const amount = centsValue(item.amount, "settlement amount", false);
    if (!balances.has(from) || !balances.has(to) || from === to) throw new Error("Khoản thanh toán phải nối hai người khác nhau trong danh sách.");
    balances.set(from, balances.get(from)! + amount);
    balances.set(to, balances.get(to)! - amount);
  }
  const sum = [...balances.values()].reduce((a, b) => a + b, 0);
  if (sum !== 0) throw new Error("Số dư quyết toán không cân bằng; hãy kiểm tra các khoản chia.");
  const debtors = [...balances.entries()].filter(([, v]) => v < 0).map(([name, amount]) => ({ name, amount: -amount }));
  const creditors = [...balances.entries()].filter(([, v]) => v > 0).map(([name, amount]) => ({ name, amount }));
  debtors.sort((a, b) => b.amount - a.amount || sortNames(a.name, b.name));
  creditors.sort((a, b) => b.amount - a.amount || sortNames(a.name, b.name));
  const transfers: Array<{ from: string; to: string; amount: number }> = [];
  let di = 0, ci = 0;
  while (di < debtors.length && ci < creditors.length) {
    const debtor = debtors[di]!, creditor = creditors[ci]!;
    const amount = Math.min(debtor.amount, creditor.amount);
    if (amount > 0) transfers.push({ from: debtor.name, to: creditor.name, amount });
    debtor.amount -= amount; creditor.amount -= amount;
    if (debtor.amount === 0) di++;
    if (creditor.amount === 0) ci++;
  }
  const lines = ["Shared expense settlement", "Currency: " + code, "Participants: " + participants.length + " | Expenses: " + expenses.length,
    "Net balances are based on listed expenses and any payments already made. Transfers are a compact settlement plan, not proof that payment occurred.", "",
    "NET BALANCES (positive = should receive; negative = should pay)"];
  for (const person of participants) {
    const value = balances.get(person)!;
    lines.push("- " + person + ": " + fmtCents(Math.abs(value)) + " " + code + " (" + (value > 0 ? "receive" : value < 0 ? "pay" : "settled") + ")");
  }
  lines.push("", "SUGGESTED TRANSFERS");
  if (!transfers.length) lines.push("- Everyone is settled.");
  else for (const transfer of transfers) lines.push("- " + transfer.from + " pays " + transfer.to + ": " + fmtCents(transfer.amount) + " " + code);
  lines.push("", "Confirm the figures and the group's agreement before sending money.");
  return lines.join("\n");
}

function movingDayChecklist(input: Input): string {
  const asOf = parseDate(input.as_of_date, "as_of_date"), moveDate = parseDate(input.move_date, "move_date");
  if (moveDate.getTime() < asOf.getTime()) throw new Error("move_date không được trước as_of_date.");
  const tasks = list(input.tasks, "tasks", 1, 250).map((raw, i) => {
    const item = row(raw, "task " + (i + 1));
    const name = textValue(item.name, "task name", 120);
    const days = integerValue(item.days_before_move, "days_before_move", 0, 3650);
    const minutes = integerValue(item.estimated_minutes, "estimated_minutes", 1, 1440, 30);
    const assignee = typeof item.assignee === "string" && item.assignee.trim() ? item.assignee.trim().slice(0, 80) : "Unassigned";
    const priority = String(item.priority ?? "normal").trim().toLowerCase();
    if (!["low", "normal", "high", "urgent"].includes(priority)) throw new Error(name + ": priority không hợp lệ.");
    const completed = item.completed ?? false;
    if (typeof completed !== "boolean") throw new Error(name + ": completed phải là true hoặc false.");
    const due = addDays(moveDate, -days);
    return { name, days, minutes, assignee, priority, completed, due,
      state: completed ? "Completed" : due.getTime() < asOf.getTime() ? "OVERDUE" : due.getTime() === asOf.getTime() ? "Due today" : "Upcoming" };
  });
  const rank: Record<string, number> = { urgent: 0, high: 1, normal: 2, low: 3 };
  tasks.sort((a, b) => a.due.getTime() - b.due.getTime() || rank[a.priority]! - rank[b.priority]! || sortNames(a.name, b.name));
  const workload = new Map<string, number>();
  for (const task of tasks) workload.set(task.assignee, (workload.get(task.assignee) ?? 0) + task.minutes);
  const lines = ["Moving-day checklist", "Today: " + dateKey(asOf), "Moving day: " + dateKey(moveDate),
    "Days remaining: " + Math.round((moveDate.getTime() - asOf.getTime()) / 86400000), "", "TASK SCHEDULE"];
  for (const task of tasks) lines.push("- " + dateKey(task.due) + " | " + task.name + " | " + task.state + " | " +
    task.priority + " priority | " + task.assignee + " | " + task.minutes + " min | " + task.days + " day(s) before moving");
  lines.push("", "ESTIMATED WORKLOAD BY PERSON");
  for (const [assignee, minutes] of [...workload.entries()].sort(([a], [b]) => sortNames(a, b))) {
    lines.push("- " + assignee + ": " + minutes + " min (" + Math.floor(minutes / 60) + " h " + minutes % 60 + " min)");
  }
  lines.push("", "Overdue tasks not marked complete: " + tasks.filter(t => t.state === "OVERDUE").length +
    ". Adjust dates to match bookings, landlord/utility arrangements and the actual move plan.");
  return lines.join("\n");
}

function movingBoxLabels(input: Input): string {
  const boxes = list(input.boxes, "boxes", 1, 300);
  const seen = new Set<string>(), roomCounts = new Map<string, number>();
  const parsed = boxes.map((raw, i) => {
    const item = row(raw, "box " + (i + 1));
    const id = textValue(item.box_id, "box_id", 24), key = id.toLowerCase();
    if (seen.has(key)) throw new Error("Mã thùng bị trùng: " + id + ".");
    seen.add(key);
    const room = textValue(item.room, "room", 60);
    const contents = list(item.contents, id + " contents", 1, 30).map((v, j) => textValue(v, id + " content " + (j + 1), 100));
    const fragile = item.fragile ?? false, openFirst = item.open_first ?? false, heavy = item.heavy ?? false;
    if ([fragile, openFirst, heavy].some(v => typeof v !== "boolean")) throw new Error(id + ": fragile/open_first/heavy phải là true hoặc false.");
    const notes = typeof item.notes === "string" ? item.notes.trim().slice(0, 120) : "";
    roomCounts.set(room, (roomCounts.get(room) ?? 0) + 1);
    return { id, room, contents, fragile, openFirst, heavy, notes };
  }).sort((a, b) => Number(b.openFirst) - Number(a.openFirst) || sortNames(a.room, b.room) || sortNames(a.id, b.id));
  const lines = ["Moving box labels", "Total boxes: " + parsed.length, "Print or copy each label and attach it to at least two visible sides of its box.", ""];
  for (const box of parsed) {
    const flags = [box.openFirst ? "OPEN FIRST" : "", box.fragile ? "FRAGILE" : "", box.heavy ? "HEAVY" : ""].filter(Boolean);
    lines.push("=".repeat(44), "BOX " + box.id + " | ROOM: " + box.room.toUpperCase(),
      "FLAGS: " + (flags.join(", ") || "STANDARD"), "CONTENTS:");
    for (const value of box.contents) lines.push("- " + value);
    if (box.notes) lines.push("NOTES: " + box.notes);
    lines.push("=".repeat(44));
  }
  lines.push("", "BOX COUNT BY ROOM");
  for (const [room, count] of [...roomCounts.entries()].sort(([a], [b]) => sortNames(a, b))) lines.push("- " + room + ": " + count);
  return lines.join("\n");
}

function returnDeadlines(input: Input): string {
  const asOf = parseDate(input.as_of_date, "as_of_date");
  const defaultNotice = integerValue(input.default_remind_days, "default_remind_days", 0, 90, 5);
  const purchases = list(input.purchases, "purchases", 1, 200).map((raw, i) => {
    const item = row(raw, "purchase " + (i + 1));
    const product = textValue(item.product, "product", 120), seller = textValue(item.seller, "seller", 120);
    const purchased = parseDate(item.purchase_date, "purchase_date");
    const days = integerValue(item.return_window_days, "return_window_days", 0, 730);
    const notice = integerValue(item.remind_days_before, "remind_days_before", 0, 90, defaultNotice);
    const started = item.return_started ?? false;
    if (typeof started !== "boolean") throw new Error(product + ": return_started phải là true hoặc false.");
    const deadline = addDays(purchased, days);
    const remaining = Math.round((deadline.getTime() - asOf.getTime()) / 86400000);
    const state = started ? "Return already started (user-marked)" : remaining < 0 ? "RETURN WINDOW MAY HAVE PASSED" :
      remaining <= notice ? "Check return now" : remaining <= 30 ? "Deadline approaching" : "Within stated return window";
    return { product, seller, purchased, days, deadline, state };
  }).sort((a, b) => a.deadline.getTime() - b.deadline.getTime() || sortNames(a.product, b.product));
  const lines = ["Product return deadline tracker", "As of: " + dateKey(asOf),
    "Deadlines are calculated as purchase date + the return-window length entered by the user. Retailer policies may count days differently and may have exclusions.", ""];
  for (const item of purchases) lines.push("- " + item.product + " | " + item.seller + " | " + item.state +
    " | purchased " + dateKey(item.purchased) + " | entered window " + item.days + " days | estimated last date " + dateKey(item.deadline));
  lines.push("", "Check the seller's current terms, proof-of-purchase rules, item condition, delivery/collection deadlines and any statutory rights for the place of purchase. This tool does not determine legal eligibility.");
  return lines.join("\n");
}

function giftBudget(input: Input): string {
  const code = currency(input.currency), totalBudget = centsValue(input.total_budget, "total_budget");
  const recipients = list(input.recipients, "recipients", 1, 200);
  const seen = new Set<string>();
  let plannedTotal = 0, purchasedTotal = 0;
  const parsed = recipients.map((raw, i) => {
    const item = row(raw, "recipient " + (i + 1));
    const name = textValue(item.name, "recipient name", 100);
    if (seen.has(name.toLowerCase())) throw new Error("Tên người nhận phải duy nhất.");
    seen.add(name.toLowerCase());
    const budget = centsValue(item.budget, name + " budget");
    const gifts = item.gifts === undefined ? [] : list(item.gifts, name + " gifts", 0, 30);
    let planned = 0, purchased = 0;
    const rows = gifts.map((rawGift, j) => {
      const gift = row(rawGift, name + " gift " + (j + 1));
      const giftName = textValue(gift.item, "gift item", 100);
      const price = centsValue(gift.price, "gift price");
      const isPurchased = gift.purchased ?? false;
      if (typeof isPurchased !== "boolean") throw new Error("purchased phải là true hoặc false.");
      planned += price;
      if (isPurchased) purchased += price;
      return { name: giftName, price, isPurchased };
    });
    plannedTotal += planned; purchasedTotal += purchased;
    return { name, budget, planned, purchased, gifts: rows };
  });
  const lines = ["Gift budget plan", "Currency: " + code, "Overall budget: " + fmtCents(totalBudget) + " " + code,
    "Planned gifts: " + fmtCents(plannedTotal) + " " + code, "Already purchased: " + fmtCents(purchasedTotal) + " " + code,
    "Overall budget remaining: " + fmtCents(totalBudget - plannedTotal) + " " + code, ""];
  for (const person of parsed) {
    lines.push(person.name + " | allowance " + fmtCents(person.budget) + " " + code + " | planned " + fmtCents(person.planned) +
      " | purchased " + fmtCents(person.purchased) + " | remaining allowance " + fmtCents(person.budget - person.planned));
    for (const gift of person.gifts) lines.push("  - " + gift.name + ": " + fmtCents(gift.price) + " " + code +
      " (" + (gift.isPurchased ? "purchased" : "not yet purchased") + ")");
  }
  if (plannedTotal > totalBudget) lines.push("WARNING: planned gifts exceed the overall budget by " + fmtCents(plannedTotal - totalBudget) + " " + code + ".");
  return lines.join("\n");
}

function emergencyKit(input: Input): string {
  const household = integerValue(input.household_size, "household_size", 1, 100);
  const days = integerValue(input.days, "days", 1, 90);
  const items = list(input.items, "items", 1, 200);
  const groups = new Map<string, Array<{ name: string; required: number; onHand: number; missing: number; unit: string }>>();
  let deficits = 0;
  for (const [i, raw] of items.entries()) {
    const item = row(raw, "item " + (i + 1));
    const name = textValue(item.name, "item name", 100);
    const group = typeof item.category === "string" && item.category.trim() ? item.category.trim().slice(0, 60) : "General";
    const unit = textValue(item.unit, "unit", 30);
    const perPersonDay = numberValue(item.per_person_per_day ?? 0, name + " per_person_per_day");
    const perHousehold = numberValue(item.per_household ?? 0, name + " per_household");
    const onHand = numberValue(item.on_hand ?? 0, name + " on_hand");
    const required = perPersonDay * household * days + perHousehold;
    const missing = Math.max(0, required - onHand);
    if (missing > 1e-8) deficits++;
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group)!.push({ name, required, onHand, missing, unit });
  }
  const lines = ["Household emergency-supplies checklist", "Household size: " + household + " | Planning duration: " + days + " day(s)",
    "Quantities are calculated only from the per-person/per-day and per-household amounts you enter. This is not an official safety standard or a guarantee of preparedness.", ""];
  for (const [group, rows] of [...groups.entries()].sort(([a], [b]) => sortNames(a, b))) {
    lines.push(group.toUpperCase());
    for (const item of rows) lines.push("- " + item.name + ": target " + fmt(item.required) + " " + item.unit +
      " | on hand " + fmt(item.onHand) + " " + item.unit + " | still needed " + fmt(item.missing) + " " + item.unit);
  }
  lines.push("", "Items with a remaining shortfall: " + deficits + ".",
    "Review local authority guidance for hazards in your area, household-specific needs, storage limits, expiry dates and safe handling. Add or remove items to match your actual plan.");
  return lines.join("\n");
}

export function runPersonalFinanceMovingTextTool(toolId: string, content: string): string {
  if (!PERSONAL_FINANCE_MOVING_TOOL_IDS.has(toolId)) throw new Error("Personal finance/moving tool is not enabled for this ID.");
  const input = parseInput(content);
  if (toolId === "bank-csv-expense-analyzer") return bankExpenseSummary(input);
  if (toolId === "bill-cashflow-calendar-planner") return billCashflow(input);
  if (toolId === "shared-expense-settler") return sharedExpenseSettle(input);
  if (toolId === "moving-day-checklist-planner") return movingDayChecklist(input);
  if (toolId === "moving-box-label-maker") return movingBoxLabels(input);
  if (toolId === "return-deadline-tracker") return returnDeadlines(input);
  if (toolId === "gift-budget-planner") return giftBudget(input);
  if (toolId === "household-emergency-kit-planner") return emergencyKit(input);
  throw new Error("Unknown personal finance/moving tool.");
}
