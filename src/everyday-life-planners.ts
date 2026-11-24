export const EVERYDAY_LIFE_PLANNER_TOOL_IDS = new Set([
  "pantry-use-first-planner",
  "pantry-recipe-matcher",
  "meal-prep-timeline-planner",
  "laundry-load-organizer",
  "trip-itinerary-planner",
  "vehicle-maintenance-planner",
  "document-renewal-planner",
  "warranty-claim-assistant",
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
function numberValue(value: unknown, key: string, min: number, max: number): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) {
    throw new Error(key + " phải là số hữu hạn từ " + min + " đến " + max + ".");
  }
  return value;
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
function dayDifference(later: Date, earlier: Date): number { return Math.round((later.getTime() - earlier.getTime()) / 86400000); }
function parseTime(value: unknown, key: string): number {
  const raw = textValue(value, key, 5);
  if (!/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(raw)) throw new Error(key + " phải theo định dạng HH:MM (24 giờ).");
  return Number(raw.slice(0, 2)) * 60 + Number(raw.slice(3));
}
function clock(minutes: number): string {
  if (!Number.isInteger(minutes) || minutes < 0 || minutes >= 1440) throw new Error("Lịch trình có bước vượt quá nửa đêm.");
  return String(Math.floor(minutes / 60)).padStart(2, "0") + ":" + String(minutes % 60).padStart(2, "0");
}
function fmt(value: number, places = 3): string {
  return Number(value.toFixed(places)).toString();
}
function monthAdd(value: Date, months: number): Date {
  const total = value.getUTCFullYear() * 12 + value.getUTCMonth() + months;
  const year = Math.floor(total / 12), month = total % 12;
  const day = Math.min(value.getUTCDate(), new Date(Date.UTC(year, month + 1, 0)).getUTCDate());
  return new Date(Date.UTC(year, month, day));
}
function rows(value: unknown, key: string, min: number, max: number): Row[] {
  if (!Array.isArray(value) || value.length < min || value.length > max) {
    throw new Error(key + " phải có từ " + min + " đến " + max + " mục.");
  }
  return value.map((item, index) => row(item, key + "[" + index + "]"));
}

function pantryUseFirst(input: Input): string {
  const asOf = parseDate(input.as_of_date, "as_of_date");
  const window = integerValue(input.window_days, "window_days", 1, 365, 14);
  const kinds: Record<string, string> = { use_by: "Use-by date", best_before: "Best-before date", expiry: "Expiry date" };
  const items = rows(input.items, "items", 1, 300).map(item => {
    const name = textValue(item.name, "item name", 100);
    const day = parseDate(item.date, name + " date");
    const kind = String(item.date_type ?? "best_before").trim().toLowerCase();
    if (!kinds[kind]) throw new Error(name + ": date_type phải là use_by, best_before hoặc expiry.");
    let quantity = "";
    if (item.quantity !== undefined) {
      const q = numberValue(item.quantity, name + " quantity", 0.000001, 1_000_000);
      quantity = " | " + fmt(q) + " " + textValue(item.unit, name + " unit", 24);
    }
    const location = typeof item.location === "string" ? item.location.trim().slice(0, 60) : "";
    const days = dayDifference(day, asOf);
    const status = days < 0 ? "PAST DATE" : days === 0 ? "DATE IS TODAY" : days <= window ? "Within planning window" : "Later";
    return { name, day, kind, quantity, location, days, status };
  }).sort((a, b) => a.day.getTime() - b.day.getTime() || a.name.localeCompare(b.name));
  const lines = ["Pantry use-first list", "As of: " + dateKey(asOf), "Planning window: " + window + " days",
    "Items are sorted by the date supplied by the user. This report does not determine whether food is safe to eat.", ""];
  for (const item of items) {
    const delta = item.days < 0 ? Math.abs(item.days) + " day(s) ago" : item.days > 0 ? "in " + item.days + " day(s)" : "today";
    const parts = [dateKey(item.day), item.name, kinds[item.kind]!, item.status, delta];
    if (item.quantity) parts.push(item.quantity.replace(/^ \| /, ""));
    if (item.location) parts.push("location: " + item.location);
    lines.push("- " + parts.join(" | "));
  }
  lines.push("", "Check package instructions and local food-safety guidance; a date alone is not a safety assessment.");
  return lines.join("\n");
}

function pantryRecipeMatch(input: Input): string {
  if (!Array.isArray(input.available_ingredients) || input.available_ingredients.length < 1 || input.available_ingredients.length > 300) {
    throw new Error("available_ingredients phải có từ 1 đến 300 tên nguyên liệu.");
  }
  if (input.pantry_staples !== undefined && (!Array.isArray(input.pantry_staples) || input.pantry_staples.length > 100)) {
    throw new Error("pantry_staples phải có tối đa 100 mục.");
  }
  const normalise = (value: unknown) => textValue(value, "ingredient", 100).toLocaleLowerCase();
  const stock = new Set([...(input.available_ingredients as unknown[]), ...((input.pantry_staples as unknown[] | undefined) ?? [])].map(normalise));
  const maxMissing = integerValue(input.max_missing, "max_missing", 0, 30, 5);
  const recipes = rows(input.recipes, "recipes", 1, 100);
  let total = 0;
  const result = recipes.map(recipe => {
    const name = textValue(recipe.name, "recipe name", 100);
    const ingredients = rowsAsStrings(recipe.ingredients, name + " ingredients", 1, 100, normalise);
    const optional = recipe.optional_ingredients === undefined ? [] : rowsAsStrings(recipe.optional_ingredients, name + " optional_ingredients", 0, 50, normalise);
    const required = [...new Set(ingredients)];
    total += required.length;
    if (total > 300) throw new Error("Tổng nguyên liệu bắt buộc của các công thức vượt 300.");
    const missing = required.filter(value => !stock.has(value));
    const optionalMissing = optional.filter(value => !stock.has(value));
    return { name, present: required.length - missing.length, required: required.length, missing, optionalMissing };
  }).sort((a, b) => a.missing.length - b.missing.length || (b.present / b.required) - (a.present / a.required) || a.name.localeCompare(b.name));
  const lines = ["Recipes matched against your ingredients", "Available ingredients: " + stock.size + " (including user-listed staples)",
    "Matching is exact after case/space normalisation; aliases and substitutions are not guessed.", ""];
  for (const recipe of result) {
    const score = Math.round(recipe.present / recipe.required * 100);
    const state = recipe.missing.length === 0 ? "Ready from listed ingredients" : recipe.missing.length <= maxMissing ? "Close match" : "Needs more ingredients";
    lines.push(recipe.name + " — " + score + "% ingredient match — " + state,
      "- Required items present: " + recipe.present + "/" + recipe.required);
    if (recipe.missing.length) lines.push("- Missing: " + recipe.missing.join(", "));
    if (recipe.optionalMissing.length) lines.push("- Optional items not listed: " + recipe.optionalMissing.join(", "));
    lines.push("");
  }
  return lines.join("\n");
}
function rowsAsStrings(value: unknown, key: string, min: number, max: number, map: (x: unknown) => string): string[] {
  if (!Array.isArray(value) || value.length < min || value.length > max) throw new Error(key + " phải có từ " + min + " đến " + max + " mục.");
  return value.map(map);
}

function mealPrepTimeline(input: Input): string {
  const start = parseTime(input.start_time, "start_time");
  const tasks = rows(input.tasks, "tasks", 1, 100).map((task, index) => {
    const id = textValue(task.id ?? "task-" + (index + 1), "task id", 50);
    const name = textValue(task.name, "task name", 100);
    const duration = integerValue(task.duration_minutes, name + " duration_minutes", 1, 480);
    const resource = textValue(task.resource ?? "hands", name + " resource", 40).toLocaleLowerCase();
    const depsRaw = task.depends_on ?? [];
    if (!Array.isArray(depsRaw) || depsRaw.length > 100 || depsRaw.some(dep => typeof dep !== "string")) throw new Error(name + ": depends_on phải là danh sách task ID.");
    const attention = task.attention_required ?? true;
    if (typeof attention !== "boolean") throw new Error(name + ": attention_required phải là true hoặc false.");
    return { id, name, duration, resource, deps: depsRaw as string[], attention, order: index };
  });
  const byId = new Map<string, typeof tasks[number]>();
  for (const task of tasks) {
    if (byId.has(task.id)) throw new Error("ID các bước nấu phải khác nhau.");
    byId.set(task.id, task);
  }
  for (const task of tasks) if (task.deps.includes(task.id) || task.deps.some(dep => !byId.has(dep))) {
    throw new Error(task.name + ": depends_on chứa ID không tồn tại hoặc tham chiếu chính nó.");
  }
  const reserved = new Map<string, Array<{ start: number; end: number }>>();
  const scheduled = new Map<string, { start: number; end: number; task: typeof tasks[number] }>();
  let pending = [...tasks];
  while (pending.length) {
    const ready = pending.filter(task => task.deps.every(dep => scheduled.has(dep)));
    if (!ready.length) throw new Error("Các bước nấu có quan hệ phụ thuộc tạo thành vòng lặp.");
    for (const task of ready.sort((a, b) => a.order - b.order)) {
      let candidate = Math.max(start, ...task.deps.map(dep => scheduled.get(dep)!.end));
      const resources = task.resource === "none" ? [] : [task.resource];
      if (task.attention && !resources.includes("hands")) resources.push("hands");
      while (true) {
        let conflictEnd: number | null = null;
        for (const resource of resources) for (const slot of reserved.get(resource) ?? []) {
          if (candidate < slot.end && candidate + task.duration > slot.start) conflictEnd = Math.max(conflictEnd ?? 0, slot.end);
        }
        if (conflictEnd === null) break;
        candidate = conflictEnd;
      }
      const end = candidate + task.duration;
      if (end >= 1440) throw new Error(task.name + ": lịch trình vượt quá nửa đêm.");
      for (const resource of resources) reserved.set(resource, [...(reserved.get(resource) ?? []), { start: candidate, end }]);
      scheduled.set(task.id, { start: candidate, end, task });
    }
    pending = pending.filter(task => !scheduled.has(task.id));
  }
  const timeline = [...scheduled.values()].sort((a, b) => a.start - b.start || a.end - b.end || a.task.order - b.task.order);
  const finish = Math.max(...timeline.map(item => item.end));
  const lines = ["Meal-preparation timeline", "Start time: " + clock(start), "Estimated finish: " + clock(finish),
    "Elapsed time: " + (finish - start) + " minutes",
    "Tasks using attention and the same appliance are scheduled without overlap. Passive steps can run while another task is active when resources differ.", ""];
  for (const item of timeline) lines.push("- " + clock(item.start) + "–" + clock(item.end) + " | " + item.task.name +
    " | " + item.task.duration + " min | resource: " + item.task.resource + " | after: " + (item.task.deps.join(", ") || "none"));
  return lines.join("\n");
}

function laundryLoadOrganizer(input: Input): string {
  const capacity = numberValue(input.machine_capacity_kg, "machine_capacity_kg", 0.1, 30);
  const targetTemp = integerValue(input.target_temp_c, "target_temp_c", 20, 90, 30);
  if (targetTemp % 10) throw new Error("target_temp_c phải theo bước 10 độ.");
  const colors = new Set(["white", "light", "bright", "dark"]);
  const fabrics = new Set(["normal", "delicate", "wool", "silk", "denim", "towel"]);
  const dryingTypes = new Set(["air", "flat", "tumble"]);
  const items = rows(input.items, "items", 1, 300).map(item => {
    const name = textValue(item.name, "laundry item name", 100);
    const weight = numberValue(item.weight_kg, name + " weight_kg", 0.01, 30);
    const color = String(item.color_group ?? "dark").trim().toLowerCase();
    const fabric = String(item.fabric_group ?? "normal").trim().toLowerCase();
    const drying = String(item.drying ?? "air").trim().toLowerCase();
    const maxTemp = integerValue(item.max_temp_c, name + " max_temp_c", 20, 90, 30);
    if (maxTemp % 10 || !colors.has(color) || !fabrics.has(fabric) || !dryingTypes.has(drying)) {
      throw new Error(name + ": nhóm màu, chất liệu, sấy hoặc nhiệt độ không được hỗ trợ.");
    }
    return { name, weight, color, fabric, drying, maxTemp };
  });
  const groups = new Map<string, typeof items>();
  const oversized: typeof items = [];
  for (const item of items) {
    if (item.weight > capacity) { oversized.push(item); continue; }
    const key = [item.color, item.fabric, item.drying].join("|");
    groups.set(key, [...(groups.get(key) ?? []), item]);
  }
  const loads: Array<{ color: string; fabric: string; drying: string; weight: number; temp: number; items: typeof items }> = [];
  for (const [key, group] of [...groups.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const [color, fabric, drying] = key.split("|");
    const bins: Array<{ items: typeof items; weight: number; maxTemp: number }> = [];
    for (const item of group.sort((a, b) => b.weight - a.weight || a.name.localeCompare(b.name))) {
      let bucket = bins.find(load => load.weight + item.weight <= capacity);
      if (!bucket) { bucket = { items: [], weight: 0, maxTemp: targetTemp }; bins.push(bucket); }
      bucket.items.push(item); bucket.weight += item.weight; bucket.maxTemp = Math.min(bucket.maxTemp, item.maxTemp);
    }
    for (const bin of bins) loads.push({ color: color!, fabric: fabric!, drying: drying!, weight: bin.weight,
      temp: Math.min(targetTemp, bin.maxTemp), items: bin.items });
  }
  const lines = ["Laundry load plan", "Machine capacity: " + fmt(capacity, 2) + " kg", "Requested wash temperature: " + targetTemp + "°C",
    "Loads are separated by user-entered colour, fabric and drying groups; wash temperature is lowered to respect the lowest stated maximum in each load.", ""];
  loads.forEach((load, index) => {
    lines.push("Load " + (index + 1) + ": " + load.color + " | " + load.fabric + " | dry: " + load.drying +
      " | wash at up to " + load.temp + "°C | " + fmt(load.weight, 2) + "/" + fmt(capacity, 2) + " kg");
    for (const item of load.items) lines.push("  - " + item.name + " (" + fmt(item.weight, 2) + " kg)");
    lines.push("");
  });
  if (oversized.length) {
    lines.push("Items too heavy for one machine load:");
    for (const item of oversized) lines.push("- " + item.name + ": " + fmt(item.weight, 2) + " kg; split manually only if the item/care label allows it.");
  }
  lines.push("Always follow each garment's care label and the washing-machine instructions.");
  return lines.join("\n");
}

function tripItinerary(input: Input): string {
  const start = parseTime(input.start_time, "start_time"), end = parseTime(input.end_time, "end_time");
  if (end <= start) throw new Error("end_time phải sau start_time trong cùng một ngày.");
  const stops = rows(input.stops, "stops", 1, 100);
  let cursor = start, scheduled = 0;
  const lines = ["Day-trip itinerary", "Available time: " + clock(start) + "–" + clock(end),
    "Travel times are supplied by the user; no route or traffic estimate is invented.", ""];
  for (let index = 0; index < stops.length; index++) {
    const stop = stops[index]!;
    const name = textValue(stop.name, "stop name", 100);
    const travel = integerValue(stop.travel_minutes_from_previous, name + " travel_minutes_from_previous", 0, 720, 0);
    const duration = integerValue(stop.duration_minutes, name + " duration_minutes", 1, 720);
    const arrival = cursor + travel, departure = arrival + duration;
    if (departure > end) break;
    lines.push("- " + clock(cursor) + "–" + clock(arrival) + " | Travel to " + name + " (" + travel + " min)",
      "  " + clock(arrival) + "–" + clock(departure) + " | Visit " + name + " (" + duration + " min)");
    cursor = departure; scheduled++;
  }
  lines.push("", "Finish time: " + clock(cursor), "Free time remaining: " + (end - cursor) + " minutes");
  if (scheduled < stops.length) {
    lines.push("Stops that do not fit in the available window, kept in original order:");
    for (const stop of stops.slice(scheduled)) lines.push("- " + textValue(stop.name, "stop name", 100));
  }
  return lines.join("\n");
}

function vehicleMaintenance(input: Input): string {
  const asOf = parseDate(input.as_of_date, "as_of_date");
  const currentKm = integerValue(input.current_odometer_km, "current_odometer_km", 0, 10_000_000);
  const monthlyKm = numberValue(input.estimated_monthly_km ?? 0, "estimated_monthly_km", 0, 200_000);
  const window = integerValue(input.window_days, "window_days", 1, 730, 90);
  const tasks = rows(input.maintenance, "maintenance", 1, 100).map(task => {
    const name = textValue(task.name, "maintenance name", 100);
    const lastDate = parseDate(task.last_service_date, name + " last_service_date");
    const lastKm = integerValue(task.last_service_odometer_km, name + " last_service_odometer_km", 0, 10_000_000);
    const months = integerValue(task.interval_months, name + " interval_months", 1, 120);
    const intervalKm = integerValue(task.interval_km, name + " interval_km", 1, 1_000_000);
    if (lastDate > asOf || lastKm > currentKm) throw new Error(name + ": last service cannot be after the current date or odometer.");
    const dateDue = monthAdd(lastDate, months), kmDue = lastKm + intervalKm;
    const kmReached = currentKm >= kmDue;
    let projected: Date | null = null;
    if (kmReached) projected = asOf;
    else if (monthlyKm > 0) projected = addDays(asOf, Math.ceil((kmDue - currentKm) / monthlyKm * 30));
    let effective = projected ? (dateDue.getTime() < projected.getTime() ? dateDue : projected) : dateDue;
    let state: string;
    if (kmReached || dateDue.getTime() <= asOf.getTime()) { state = "DUE NOW / OVERDUE"; effective = asOf; }
    else state = effective.getTime() <= addDays(asOf, window).getTime() ? "Due within planning window" : "Later";
    return { name, effective, dateDue, kmDue, kmLeft: Math.max(0, kmDue - currentKm), state,
      overdue: Math.max(0, dayDifference(asOf, effective)), projected };
  }).sort((a, b) => a.effective.getTime() - b.effective.getTime() || a.name.localeCompare(b.name));
  const lines = ["Vehicle maintenance plan", "As of: " + dateKey(asOf), "Current odometer: " + currentKm.toLocaleString("en-US") + " km",
    "Estimated monthly distance: " + fmt(monthlyKm, 0) + " km",
    "Intervals come from the user's owner manual or service records; this is not a substitute for manufacturer guidance.", ""];
  for (const task of tasks) {
    const projected = task.projected ? dateKey(task.projected) : "not projected (monthly distance is zero)";
    lines.push("- " + task.name + " | " + task.state + " | estimated trigger: " + dateKey(task.effective) +
      " | calendar interval: " + dateKey(task.dateDue) + " | odometer trigger: " + task.kmDue.toLocaleString("en-US") +
      " km (" + task.kmLeft.toLocaleString("en-US") + " km remaining) | mileage projection: " + projected);
    if (task.overdue) lines.push("  Calendar projection is " + task.overdue + " day(s) past due.");
  }
  return lines.join("\n");
}

function documentRenewal(input: Input): string {
  const asOf = parseDate(input.as_of_date, "as_of_date");
  const window = integerValue(input.window_days, "window_days", 1, 1825, 180);
  const docs = rows(input.documents, "documents", 1, 150).map(document => {
    const name = textValue(document.name, "document name", 100);
    const expires = parseDate(document.expiry_date, name + " expiry_date");
    const notice = integerValue(document.remind_days_before, name + " remind_days_before", 0, 3650, 60);
    const renewalStart = addDays(expires, -notice);
    const state = expires.getTime() < asOf.getTime() ? "EXPIRED" :
      renewalStart.getTime() <= asOf.getTime() ? "Start/check renewal now" :
      renewalStart.getTime() <= addDays(asOf, window).getTime() ? "Renewal window approaching" : "Later";
    return { name, expires, notice, renewalStart, state };
  }).sort((a, b) => a.renewalStart.getTime() - b.renewalStart.getTime() || a.name.localeCompare(b.name));
  const lines = ["Document renewal reminders", "As of: " + dateKey(asOf), "Planning window: " + window + " days",
    "Reminder windows are entered by the user. Confirm current requirements and processing times with the issuing authority or provider.", ""];
  for (const doc of docs) lines.push("- " + doc.name + " | " + doc.state + " | check renewal from " + dateKey(doc.renewalStart) +
    " | expires " + dateKey(doc.expires) + " | reminder lead time " + doc.notice + " day(s)");
  return lines.join("\n");
}

function warrantyClaim(input: Input): string {
  const asOf = parseDate(input.as_of_date, "as_of_date");
  const product = textValue(input.product_name, "product_name", 120);
  const seller = textValue(input.seller, "seller", 120);
  const purchase = parseDate(input.purchase_date, "purchase_date");
  const months = integerValue(input.warranty_months, "warranty_months", 0, 120);
  const issue = textValue(input.issue_description, "issue_description", 2000);
  const evidenceRaw = input.evidence ?? ["Purchase receipt"];
  if (!Array.isArray(evidenceRaw) || evidenceRaw.length > 30) throw new Error("evidence phải là danh sách tối đa 30 mục.");
  const evidence = evidenceRaw.map(item => textValue(item, "evidence item", 100));
  const language = String(input.language ?? "vi").trim().toLowerCase();
  if (language !== "vi" && language !== "en") throw new Error("language chỉ nhận vi hoặc en.");
  if (purchase.getTime() > asOf.getTime()) throw new Error("purchase_date không được sau as_of_date.");
  const warrantyEnd = monthAdd(purchase, months);
  const remaining = asOf.getTime() <= warrantyEnd.getTime() ? dayDifference(warrantyEnd, asOf) : 0;
  const status = asOf.getTime() <= warrantyEnd.getTime()
    ? (language === "vi" ? "Trong thời hạn bảo hành ước tính theo dữ liệu đã nhập" : "Inside the user-entered estimated warranty period")
    : (language === "vi" ? "Ngày kết thúc bảo hành ước tính đã qua" : "User-entered estimated warranty end date has passed");
  const lines = language === "vi" ? [
    "Bản nháp yêu cầu kiểm tra bảo hành", "Người nhận: " + seller, "Sản phẩm: " + product,
    "Ngày mua: " + dateKey(purchase), "Thời hạn bảo hành người dùng nhập: " + months + " tháng",
    "Ngày kết thúc ước tính theo phép cộng tháng: " + dateKey(warrantyEnd), "Tình trạng theo dữ liệu đã nhập: " + status,
    "Mô tả sự cố: " + issue, "", "Kính gửi bộ phận hỗ trợ,",
    "Tôi muốn nhờ kiểm tra sản phẩm " + product + " đã mua ngày " + dateKey(purchase) + ". Sản phẩm hiện gặp vấn đề như sau: " + issue,
    "Nhờ quý bộ phận hướng dẫn quy trình kiểm tra và xác nhận điều kiện bảo hành áp dụng cho sản phẩm này.",
    "Tôi có thể cung cấp các tài liệu sau:", ...evidence.map(item => "- " + item), "", "Xin cảm ơn.", "",
    "Lưu ý: ngày kết thúc chỉ là phép tính từ thời hạn do người dùng nhập; hãy đối chiếu phiếu bảo hành, ngoại lệ, ngày kích hoạt và điều kiện của người bán/nhà sản xuất trước khi kết luận quyền lợi.",
  ] : [
    "Warranty inspection request draft", "To: " + seller, "Product: " + product, "Purchase date: " + dateKey(purchase),
    "Warranty duration entered: " + months + " month(s)", "Estimated end date from the entered duration: " + dateKey(warrantyEnd),
    "Status from supplied data: " + status, "Issue: " + issue, "", "Hello,",
    "I would like to request an inspection of " + product + ", purchased on " + dateKey(purchase) + ". The issue is: " + issue,
    "Please let me know the inspection process and confirm the warranty conditions that apply to this product.",
    "I can provide the following evidence:", ...evidence.map(item => "- " + item), "", "Thank you.", "",
    "Note: the end date is only a calculation based on the duration entered by the user. Check the actual warranty document, exclusions, activation date and seller/manufacturer terms before concluding coverage.",
  ];
  return lines.join("\n");
}

export function runEverydayLifePlannerTextTool(toolId: string, content: string): string {
  if (!EVERYDAY_LIFE_PLANNER_TOOL_IDS.has(toolId)) throw new Error("Everyday life planner is not enabled for this ID.");
  const input = parseInput(content);
  if (toolId === "pantry-use-first-planner") return pantryUseFirst(input);
  if (toolId === "pantry-recipe-matcher") return pantryRecipeMatch(input);
  if (toolId === "meal-prep-timeline-planner") return mealPrepTimeline(input);
  if (toolId === "laundry-load-organizer") return laundryLoadOrganizer(input);
  if (toolId === "trip-itinerary-planner") return tripItinerary(input);
  if (toolId === "vehicle-maintenance-planner") return vehicleMaintenance(input);
  if (toolId === "document-renewal-planner") return documentRenewal(input);
  if (toolId === "warranty-claim-assistant") return warrantyClaim(input);
  throw new Error("Unknown everyday life planner.");
}
