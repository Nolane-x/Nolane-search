export const HOME_VEHICLE_RENTAL_TOOL_IDS = new Set([
  "vehicle-fuel-log-analyzer",
  "vehicle-ownership-cost-report",
  "appliance-repair-replace-comparator",
  "home-repair-quote-comparator",
  "rental-move-in-inspection-report",
  "rental-move-out-condition-report",
  "rental-offer-cost-comparator",
  "appliance-service-history-report",
]);

type Input = Record<string, unknown>;
type Row = Record<string, unknown>;
const CONDITIONS = new Set(["good", "worn", "damaged", "missing", "not_tested"]);

function parseInput(content: string): Input {
  let value: unknown;
  try { value = JSON.parse(content); } catch { throw new Error("Gửi dữ liệu JSON hợp lệ cho công cụ này."); }
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
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) throw new Error(key + " phải là số hữu hạn trong phạm vi hợp lệ.");
  return value;
}
function money(value: unknown, key: string): number {
  const raw = numberValue(value, key);
  const cents = Math.round(raw * 100);
  if (Math.abs(raw * 100 - cents) > 1e-6) throw new Error(key + " chỉ được có tối đa hai chữ số thập phân.");
  return cents;
}
function integerValue(value: unknown, key: string, min = 0, max = 1_000_000): number {
  const n = numberValue(value, key, min, max);
  if (!Number.isInteger(n)) throw new Error(key + " phải là số nguyên.");
  return n;
}
function parseDate(value: unknown, key: string): Date {
  const raw = textValue(value, key, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(raw)) throw new Error(key + " phải có định dạng YYYY-MM-DD.");
  const d = new Date(raw + "T00:00:00.000Z");
  if (Number.isNaN(d.getTime()) || d.toISOString().slice(0, 10) !== raw) throw new Error(key + " không phải ngày hợp lệ.");
  return d;
}
function dateKey(d: Date): string { return d.toISOString().slice(0, 10); }
function addDays(d: Date, n: number): Date { return new Date(d.getTime() + n * 86400000); }
function monthAdd(d: Date, months: number): Date {
  const n = d.getUTCFullYear() * 12 + d.getUTCMonth() + months;
  const year = Math.floor(n / 12), month = n % 12;
  return new Date(Date.UTC(year, month, Math.min(d.getUTCDate(), new Date(Date.UTC(year, month + 1, 0)).getUTCDate())));
}
function currency(value: unknown): string {
  const code = textValue(value, "currency", 8).toUpperCase();
  if (!/^[A-Z0-9]{3,8}$/.test(code)) throw new Error("currency phải là mã 3–8 ký tự như VND, USD hoặc EUR.");
  return code;
}
function fmt(value: number, places = 2): string { return Number(value.toFixed(places)).toString(); }
function fmtCents(value: number): string { return (value / 100).toFixed(2).replace(/\.?0+$/, ""); }
function list(value: unknown, key: string, min = 1, max = 300): unknown[] {
  if (!Array.isArray(value) || value.length < min || value.length > max) throw new Error(key + " phải có từ " + min + " đến " + max + " mục.");
  return value;
}
function condition(value: unknown, key: string): string {
  const v = String(value ?? "").trim().toLowerCase();
  if (!CONDITIONS.has(v)) throw new Error(key + " phải là good, worn, damaged, missing hoặc not_tested.");
  return v;
}
function sortNames(a: string, b: string): number { return a.localeCompare(b, "en", { sensitivity: "base" }); }

function vehicleFuelLog(input: Input): string {
  const code = currency(input.currency);
  const entries = list(input.entries, "entries", 2, 2000).map((raw, i) => {
    const item = row(raw, "fuel entry " + (i + 1));
    const day = parseDate(item.date, "fuel entry date");
    const odometer = numberValue(item.odometer_km, "odometer_km", 0, 10_000_000);
    const litres = numberValue(item.litres, "litres", 0.001, 1000);
    const price = money(item.price_per_litre, "price_per_litre");
    if (typeof item.full_tank !== "boolean") throw new Error("full_tank phải là true hoặc false.");
    return { day, odometer, litres, price, full: item.full_tank, index: i };
  }).sort((a, b) => a.day.getTime() - b.day.getTime() || a.odometer - b.odometer || a.index - b.index);
  for (let i = 1; i < entries.length; i++) if (entries[i]!.odometer <= entries[i - 1]!.odometer) throw new Error("Số kilomet trên đồng hồ phải tăng nghiêm ngặt theo thứ tự thời gian.");
  const monthly = new Map<string, { litres: number; cost: number; count: number }>();
  let allLitres = 0, allCost = 0;
  const intervals: Array<{ start: Date; end: Date; km: number; litres: number; cost: number }> = [];
  let lastFull = -1;
  for (let i = 0; i < entries.length; i++) {
    const item = entries[i]!;
    const cost = item.litres * item.price / 100;
    allLitres += item.litres; allCost += cost;
    const month = dateKey(item.day).slice(0, 7);
    if (!monthly.has(month)) monthly.set(month, { litres: 0, cost: 0, count: 0 });
    const m = monthly.get(month)!; m.litres += item.litres; m.cost += cost; m.count++;
    if (item.full) {
      if (lastFull >= 0) {
        const previous = entries[lastFull]!;
        const litres = entries.slice(lastFull + 1, i + 1).reduce((sum, v) => sum + v.litres, 0);
        const intervalCost = entries.slice(lastFull + 1, i + 1).reduce((sum, v) => sum + v.litres * v.price / 100, 0);
        intervals.push({ start: previous.day, end: item.day, km: item.odometer - previous.odometer, litres, cost: intervalCost });
      }
      lastFull = i;
    }
  }
  const lines = ["Vehicle fuel log summary", "Currency: " + code, "Fuel entries: " + entries.length,
    "Total fuel: " + fmt(allLitres, 3) + " L", "Total fuel spend: " + fmtCents(Math.round(allCost * 100)) + " " + code,
    "Consumption is calculated only between consecutive full-tank entries. Partial-fill intervals are not compared in isolation.", "", "FULL-TANK CONSUMPTION INTERVALS"];
  if (!intervals.length) lines.push("- At least two full-tank entries are needed for a consumption interval.");
  for (const v of intervals) lines.push("- " + dateKey(v.start) + " to " + dateKey(v.end) + " | " + fmt(v.km, 1) +
    " km | " + fmt(v.litres, 3) + " L | " + fmt(v.litres / v.km * 100, 2) + " L/100 km | " +
    fmt(v.km / v.litres, 2) + " km/L | fuel cost " + fmt(v.cost, 2) + " " + code);
  lines.push("", "MONTHLY FUEL SPEND");
  for (const [month, m] of [...monthly.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    lines.push("- " + month + ": " + fmt(m.cost, 2) + " " + code + " | " + fmt(m.litres, 3) + " L | " + m.count + " fill(s)");
  }
  return lines.join("\n");
}

function vehicleOwnershipCost(input: Input): string {
  const code = currency(input.currency);
  const distance = numberValue(input.distance_km, "distance_km", 0.001, 100_000_000);
  const expenses = list(input.expenses, "expenses", 1, 5000);
  const categories = new Map<string, { cents: number; count: number }>(), months = new Map<string, number>();
  let total = 0;
  for (const [i, raw] of expenses.entries()) {
    const item = row(raw, "expense " + (i + 1));
    const day = parseDate(item.date, "expense date");
    textValue(item.name, "expense name", 120);
    const cat = textValue(item.category, "expense category", 80);
    const amount = money(item.amount, "expense amount");
    if (!categories.has(cat)) categories.set(cat, { cents: 0, count: 0 });
    const rowData = categories.get(cat)!; rowData.cents += amount; rowData.count++;
    const m = dateKey(day).slice(0, 7);
    months.set(m, (months.get(m) ?? 0) + amount);
    total += amount;
  }
  const lines = ["Vehicle ownership cost report", "Currency: " + code, "Distance covered in the reporting period: " + fmt(distance, 1) + " km",
    "Recorded expenses: " + expenses.length, "Total recorded running cost: " + fmtCents(total) + " " + code,
    "Recorded cost per kilometre: " + fmt(total / 100 / distance, 4) + " " + code + "/km",
    "Only expenses entered in this file are included. Depreciation, finance, resale value and unlisted costs are not inferred.", "", "COST BY CATEGORY"];
  for (const [cat, v] of [...categories.entries()].sort((a, b) => b[1].cents - a[1].cents || sortNames(a[0], b[0]))) {
    lines.push("- " + cat + ": " + fmtCents(v.cents) + " " + code + " | " + v.count + " record(s)");
  }
  lines.push("", "MONTHLY COST");
  for (const [month, cents] of [...months.entries()].sort(([a], [b]) => a.localeCompare(b))) lines.push("- " + month + ": " + fmtCents(cents) + " " + code);
  return lines.join("\n");
}

function applianceRepairReplace(input: Input): string {
  const name = textValue(input.appliance_name, "appliance_name", 120), code = currency(input.currency);
  const repairCost = money(input.repair_cost, "repair_cost") / 100;
  const yearsAfter = numberValue(input.expected_years_after_repair, "expected_years_after_repair", 0.1, 100);
  const oldEnergy = money(input.annual_energy_cost_after_repair, "annual_energy_cost_after_repair") / 100;
  const replacementCost = money(input.replacement_cost, "replacement_cost") / 100;
  const newLife = numberValue(input.replacement_expected_life_years, "replacement_expected_life_years", 0.1, 100);
  const newEnergy = money(input.replacement_annual_energy_cost, "replacement_annual_energy_cost") / 100;
  const repairWarranty = integerValue(input.repair_warranty_months ?? 0, "repair_warranty_months", 0, 120);
  const newWarranty = integerValue(input.replacement_warranty_months ?? 0, "replacement_warranty_months", 0, 240);
  const repairAnnual = repairCost / yearsAfter + oldEnergy, replaceAnnual = replacementCost / newLife + newEnergy;
  const delta = replaceAnnual - repairAnnual, energySaving = oldEnergy - newEnergy;
  const payback = energySaving > 0 && replacementCost > repairCost ? (replacementCost - repairCost) / energySaving : null;
  const lines = ["Appliance repair-versus-replace comparison", "Appliance: " + name, "Currency: " + code, "",
    "REPAIR OPTION", "- Repair cost now: " + fmt(repairCost) + " " + code,
    "- Expected years after repair (user estimate): " + fmt(yearsAfter, 1),
    "- Estimated annual energy cost: " + fmt(oldEnergy) + " " + code,
    "- Repair warranty: " + repairWarranty + " month(s)", "- Annualised cost proxy: " + fmt(repairAnnual) + " " + code + "/year",
    "", "REPLACEMENT OPTION", "- Replacement cost now: " + fmt(replacementCost) + " " + code,
    "- Expected product life (user estimate): " + fmt(newLife, 1) + " years",
    "- Estimated annual energy cost: " + fmt(newEnergy) + " " + code,
    "- Replacement warranty: " + newWarranty + " month(s)", "- Annualised cost proxy: " + fmt(replaceAnnual) + " " + code + "/year",
    "", "COMPARISON"];
  if (delta < -1e-8) lines.push("- Replacement has the lower annualised cost proxy by " + fmt(Math.abs(delta)) + " " + code + "/year under the entered assumptions.");
  else if (delta > 1e-8) lines.push("- Repair has the lower annualised cost proxy by " + fmt(delta) + " " + code + "/year under the entered assumptions.");
  else lines.push("- The annualised cost proxies are equal under the entered assumptions.");
  if (payback !== null) lines.push("- Estimated simple payback for the extra replacement purchase cost from energy savings alone: " + fmt(payback, 2) + " years.");
  else lines.push("- No positive energy-savings payback period can be calculated from the supplied values.");
  lines.push("", "This arithmetic comparison does not inspect appliance safety, reliability, repair quality, environmental impact, product features or actual lifespan. Confirm repair advice and warranty conditions with a qualified provider/manufacturer.");
  return lines.join("\n");
}

function homeRepairQuotes(input: Input): string {
  const project = textValue(input.project_name, "project_name", 120), code = currency(input.currency);
  const required = list(input.required_work, "required_work", 1, 100);
  const requirements = new Map<string, string>();
  for (const [i, raw] of required.entries()) {
    const item = row(raw, "required work " + (i + 1)), id = textValue(item.id, "required work id", 40);
    if (requirements.has(id)) throw new Error("Required work IDs must be unique.");
    requirements.set(id, textValue(item.description, "required work description", 160));
  }
  const quotes = list(input.quotes, "quotes", 1, 30).map((raw, i) => {
    const item = row(raw, "quote " + (i + 1)), provider = textValue(item.provider, "provider", 120);
    const labour = money(item.labour_cost ?? 0, "labour_cost"), materials = money(item.materials_cost ?? 0, "materials_cost");
    const fees = money(item.other_fees ?? 0, "other_fees"), taxPercent = numberValue(item.tax_percent ?? 0, "tax_percent", 0, 100);
    const subtotal = labour + materials + fees, tax = Math.round(subtotal * taxPercent / 100), total = subtotal + tax;
    const includedRaw = item.included_work_ids ?? [], excludedRaw = item.excluded_work ?? [];
    if (!Array.isArray(includedRaw) || includedRaw.some(v => typeof v !== "string")) throw new Error(provider + ": included_work_ids phải là danh sách ID.");
    const included = new Set(includedRaw as string[]);
    if (included.size !== includedRaw.length || [...included].some(id => !requirements.has(id))) throw new Error(provider + ": included_work_ids chứa ID trùng hoặc không tồn tại.");
    if (!Array.isArray(excludedRaw) || excludedRaw.length > 100) throw new Error(provider + ": excluded_work phải là danh sách tối đa 100 mục.");
    const excluded = excludedRaw.map(v => textValue(v, "excluded work", 160));
    const warranty = integerValue(item.workmanship_warranty_months ?? 0, "workmanship_warranty_months", 0, 120);
    const days = integerValue(item.estimated_days ?? 0, "estimated_days", 0, 730);
    return { provider, labour, materials, fees, tax, total, included, missing: [...requirements.keys()].filter(id => !included.has(id)).sort(),
      excluded, warranty, days };
  }).sort((a, b) => b.included.size - a.included.size || a.total - b.total || sortNames(a.provider, b.provider));
  const lines = ["Home repair quote comparison", "Project: " + project, "Currency: " + code, "Required scope items: " + requirements.size,
    "Quotes are compared using only the amounts and scope details supplied. A lower price does not establish better workmanship or suitability.", ""];
  quotes.forEach((q, i) => {
    lines.push((i + 1) + ". " + q.provider + " — " + fmtCents(q.total) + " " + code,
      "- Labour: " + fmtCents(q.labour) + "; materials: " + fmtCents(q.materials) + "; other fees: " + fmtCents(q.fees) + "; entered tax: " + fmtCents(q.tax),
      "- Scope included: " + q.included.size + "/" + requirements.size,
      "- Workmanship warranty entered: " + q.warranty + " month(s); estimated duration: " + q.days + " day(s)");
    if (q.missing.length) lines.push("- Required items not marked included: " + q.missing.map(id => id + " (" + requirements.get(id) + ")").join(", "));
    if (q.excluded.length) lines.push("- Explicit exclusions: " + q.excluded.join("; "));
    lines.push("");
  });
  lines.push("Ask each provider to clarify missing scope, materials/brands, permits, cleanup, payment milestones, change orders and warranty terms before deciding.");
  return lines.join("\n");
}

function rentalMoveIn(input: Input): string {
  const property = textValue(input.property, "property", 160), tenant = textValue(input.tenant, "tenant", 120);
  const landlord = textValue(input.landlord_or_agent, "landlord_or_agent", 120), day = parseDate(input.inspection_date, "inspection_date");
  const checks = list(input.checks, "checks", 1, 500).map((raw, i) => {
    const item = row(raw, "check " + (i + 1));
    const area = textValue(item.area, "area", 80), name = textValue(item.item, "item", 120);
    const state = condition(item.condition, "condition");
    const note = typeof item.note === "string" ? item.note.trim().replace(/\s+/g, " ").slice(0, 400) : "";
    const refs = item.evidence_refs ?? [];
    if (!Array.isArray(refs) || refs.length > 20) throw new Error(area + "/" + name + ": evidence_refs phải là danh sách tối đa 20 nhãn.");
    return { area, name, state, note, refs: refs.map(v => textValue(v, "evidence reference", 120)) };
  }).sort((a, b) => sortNames(a.area, b.area) || sortNames(a.name, b.name));
  const meters = input.meter_readings === undefined ? [] : list(input.meter_readings, "meter_readings", 0, 50);
  const meterRows = meters.map((raw, i) => {
    const item = row(raw, "meter reading " + (i + 1));
    return { utility: textValue(item.utility, "utility", 60), reading: textValue(item.reading, "reading", 80), unit: textValue(item.unit, "unit", 30) };
  });
  const counts = new Map<string, number>();
  for (const s of CONDITIONS) counts.set(s, 0);
  const lines = ["Rental move-in condition report", "Property: " + property, "Tenant: " + tenant + " | Landlord/agent: " + landlord,
    "Inspection date: " + dateKey(day), "This report records observations entered by the user at inspection time. Attach and retain the original evidence separately.", "", "ROOM-BY-ROOM CHECKS"];
  for (const check of checks) {
    counts.set(check.state, (counts.get(check.state) ?? 0) + 1);
    lines.push("- " + check.area + " | " + check.name + " | " + check.state);
    if (check.note) lines.push("  Note: " + check.note);
    if (check.refs.length) lines.push("  Evidence references: " + check.refs.join(", "));
  }
  lines.push("", "METER READINGS");
  if (meterRows.length) for (const m of meterRows) lines.push("- " + m.utility + ": " + m.reading + " " + m.unit);
  else lines.push("- None recorded.");
  lines.push("", "CONDITION SUMMARY");
  for (const s of [...CONDITIONS].sort()) lines.push("- " + s + ": " + counts.get(s));
  lines.push("", "Review this record together, note any disagreement and keep dated photographs/videos and signed copies with the tenancy documents. This report does not determine responsibility for damage or deposit rights.");
  return lines.join("\n");
}

function rentalMoveOut(input: Input): string {
  const property = textValue(input.property, "property", 160), tenant = textValue(input.tenant, "tenant", 120);
  const moveIn = parseDate(input.move_in_date, "move_in_date"), moveOut = parseDate(input.move_out_date, "move_out_date");
  if (moveOut.getTime() < moveIn.getTime()) throw new Error("move_out_date không được trước move_in_date.");
  const indexChecks = (value: unknown, label: string) => {
    const entries = list(value, label, 1, 500), result = new Map<string, { area: string; name: string; state: string; note: string }>();
    for (const [i, raw] of entries.entries()) {
      const item = row(raw, label + " " + (i + 1)), id = textValue(item.id, label + " id", 60);
      if (result.has(id)) throw new Error(label + " có ID trùng.");
      result.set(id, { area: textValue(item.area, "area", 80), name: textValue(item.item, "item", 120),
        state: condition(item.condition, "condition"), note: typeof item.note === "string" ? item.note.trim().slice(0, 400) : "" });
    }
    return result;
  };
  const before = indexChecks(input.move_in_checks, "move_in_checks"), after = indexChecks(input.move_out_checks, "move_out_checks");
  const code = currency(input.currency ?? "VND"), deposit = money(input.deposit_amount ?? 0, "deposit_amount");
  const deductions = input.proposed_deductions === undefined ? [] : list(input.proposed_deductions, "proposed_deductions", 0, 200);
  let deductionTotal = 0;
  const ded = deductions.map((raw, i) => {
    const item = row(raw, "deduction " + (i + 1)), desc = textValue(item.description, "deduction description", 160), amount = money(item.amount, "deduction amount");
    deductionTotal += amount;
    return { desc, amount };
  });
  const keys = [...new Set([...before.keys(), ...after.keys()])].sort();
  const lines = ["Rental move-out condition comparison", "Property: " + property, "Tenant: " + tenant,
    "Move-in inspection: " + dateKey(moveIn), "Move-out inspection: " + dateKey(moveOut),
    "This is a comparison of user-entered labels, not a finding about cause, fair wear and tear or legal responsibility.", "", "ITEM-BY-ITEM COMPARISON"];
  for (const id of keys) {
    const old = before.get(id), current = after.get(id);
    if (!old) lines.push("- " + id + " | Added at move-out | move-out: " + current!.area + " / " + current!.name + " / " + current!.state + " — " + current!.note);
    else if (!current) lines.push("- " + id + " | Not inspected at move-out | move-in: " + old.area + " / " + old.name + " / " + old.state + " — " + old.note);
    else {
      const status = old.state === current.state ? "Same recorded condition" : "Condition label changed";
      lines.push("- " + id + " | " + status + " | move-in " + old.state + " → move-out " + current.state);
      if (old.note || current.note) lines.push("  Move-in note: " + (old.note || "(none)") + " | Move-out note: " + (current.note || "(none)"));
    }
  }
  lines.push("", "USER-ENTERED DEPOSIT FIGURES", "- Deposit amount: " + fmtCents(deposit) + " " + code,
    "- Proposed deductions: " + fmtCents(deductionTotal) + " " + code, "- Arithmetic remainder: " + fmtCents(deposit - deductionTotal) + " " + code);
  for (const item of ded) lines.push("  - " + item.desc + ": " + fmtCents(item.amount) + " " + code);
  lines.push("", "Request itemised explanations and supporting evidence for any proposed deductions. Check the signed agreement and local rules; this arithmetic report does not decide lawful deposit deductions.");
  return lines.join("\n");
}

function rentalOfferComparator(input: Input): string {
  const code = currency(input.currency), months = integerValue(input.lease_months, "lease_months", 1, 120);
  const offers = list(input.offers, "offers", 1, 50).map((raw, i) => {
    const item = row(raw, "offer " + (i + 1)), name = textValue(item.name, "offer name", 120);
    const rent = money(item.monthly_rent, "monthly_rent"), utilities = money(item.monthly_utilities ?? 0, "monthly_utilities");
    const fees = money(item.monthly_fees ?? 0, "monthly_fees"), deposit = money(item.refundable_deposit ?? 0, "refundable_deposit");
    const nonrefundable = money(item.one_time_nonrefundable_fees ?? 0, "one_time_nonrefundable_fees");
    const moveCost = money(item.move_in_costs ?? 0, "move_in_costs"), monthly = rent + utilities + fees;
    const leaseCost = monthly * months + nonrefundable + moveCost;
    const cashNeeded = monthly + deposit + nonrefundable + moveCost;
    return { name, rent, utilities, fees, deposit, nonrefundable, moveCost, monthly, leaseCost, cashNeeded };
  }).sort((a, b) => a.leaseCost - b.leaseCost || sortNames(a.name, b.name));
  const lines = ["Rental offer cost comparison", "Currency: " + code, "Comparison period: " + months + " month(s)",
    "Recurring costs and one-off costs are compared separately. Refundable deposits count as cash required up front, not as a lease expense in the total-cost comparison.", ""];
  for (const [i, o] of offers.entries()) lines.push((i + 1) + ". " + o.name,
    "- Monthly rent: " + fmtCents(o.rent) + " | utilities: " + fmtCents(o.utilities) + " | recurring fees: " + fmtCents(o.fees),
    "- Estimated recurring monthly total: " + fmtCents(o.monthly) + " " + code,
    "- Refundable deposit: " + fmtCents(o.deposit) + " " + code,
    "- Non-refundable one-time fees: " + fmtCents(o.nonrefundable) + " " + code + " | move-in costs: " + fmtCents(o.moveCost) + " " + code,
    "- Cash required at start (one month + deposit + one-off costs): " + fmtCents(o.cashNeeded) + " " + code,
    "- Estimated " + months + "-month cost excluding refundable deposit: " + fmtCents(o.leaseCost) + " " + code, "");
  if (offers.length > 1) lines.push("Lowest entered " + months + "-month cost: " + offers[0]!.name + " (" + fmtCents(offers[0]!.leaseCost) + " " + code + "); this does not assess location, property condition, landlord, lease clauses or suitability.");
  return lines.join("\n");
}

function applianceServiceHistory(input: Input): string {
  const asOf = parseDate(input.as_of_date, "as_of_date");
  const appliances = list(input.appliances, "appliances", 1, 200).map((raw, i) => {
    const item = row(raw, "appliance " + (i + 1)), name = textValue(item.name, "appliance name", 120);
    const category = typeof item.category === "string" && item.category.trim() ? item.category.trim().slice(0, 80) : "General";
    const code = currency(item.currency ?? "VND"), purchase = parseDate(item.purchase_date, "purchase_date");
    const warranty = integerValue(item.warranty_months ?? 0, "warranty_months", 0, 120), end = monthAdd(purchase, warranty);
    const entries = item.service_entries === undefined ? [] : list(item.service_entries, name + " service_entries", 0, 100);
    let total = 0, downtime = 0, latest: Date | null = null;
    const types = new Map<string, number>();
    for (const [j, rawEntry] of entries.entries()) {
      const entry = row(rawEntry, "service entry " + (j + 1)), day = parseDate(entry.date, "service date");
      if (day.getTime() > asOf.getTime()) throw new Error(name + ": service entry cannot be after as_of_date.");
      const event = textValue(entry.event, "service event", 120), cost = money(entry.cost ?? 0, "service cost"), days = integerValue(entry.downtime_days ?? 0, "downtime_days", 0, 3650);
      total += cost; downtime += days; types.set(event, (types.get(event) ?? 0) + 1);
      if (!latest || day.getTime() > latest.getTime()) latest = day;
    }
    const nextDue = item.next_service_due === undefined ? null : parseDate(item.next_service_due, "next_service_due");
    return { name, category, currency: code, purchase, warrantyEnd: end, total, downtime, count: entries.length, latest, types, nextDue };
  }).sort((a, b) => sortNames(a.category, b.category) || sortNames(a.name, b.name));
  const lines = ["Appliance service history report", "As of: " + dateKey(asOf),
    "Service costs, events and warranty durations are user-entered. Estimated warranty end dates do not establish coverage.", ""];
  for (const item of appliances) {
    lines.push(item.name + " | " + item.category,
      "- Purchased: " + dateKey(item.purchase) + " | estimated warranty end: " + dateKey(item.warrantyEnd) + " (" + (asOf.getTime() <= item.warrantyEnd.getTime() ? "within entered warranty dates" : "entered warranty end date passed") + ")",
      "- Service records: " + item.count + " | recorded service spend: " + fmtCents(item.total) + " " + item.currency + " | recorded downtime: " + item.downtime + " day(s)",
      "- Latest service entry: " + (item.latest ? dateKey(item.latest) : "none recorded"));
    if (item.types.size) lines.push("- Event types: " + [...item.types.entries()].sort(([a], [b]) => sortNames(a, b)).map(([name, count]) => name + " (" + count + ")").join(", "));
    if (item.nextDue) lines.push("- Next service date entered: " + dateKey(item.nextDue) + " (" + (item.nextDue.getTime() <= asOf.getTime() ? "due/overdue" : "upcoming") + ")");
    lines.push("");
  }
  return lines.join("\n");
}

export function runHomeVehicleRentalTextTool(toolId: string, content: string): string {
  if (!HOME_VEHICLE_RENTAL_TOOL_IDS.has(toolId)) throw new Error("Home/vehicle/rental tool is not enabled for this ID.");
  const input = parseInput(content);
  if (toolId === "vehicle-fuel-log-analyzer") return vehicleFuelLog(input);
  if (toolId === "vehicle-ownership-cost-report") return vehicleOwnershipCost(input);
  if (toolId === "appliance-repair-replace-comparator") return applianceRepairReplace(input);
  if (toolId === "home-repair-quote-comparator") return homeRepairQuotes(input);
  if (toolId === "rental-move-in-inspection-report") return rentalMoveIn(input);
  if (toolId === "rental-move-out-condition-report") return rentalMoveOut(input);
  if (toolId === "rental-offer-cost-comparator") return rentalOfferComparator(input);
  if (toolId === "appliance-service-history-report") return applianceServiceHistory(input);
  throw new Error("Unknown home/vehicle/rental tool.");
}
