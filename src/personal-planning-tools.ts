export const PERSONAL_PLANNING_TOOL_IDS = new Set([
  "meal-shopping-list-planner",
  "travel-packing-checklist",
  "study-plan-scheduler",
  "weekly-chore-planner",
  "subscription-cost-calculator",
  "commute-cost-calculator",
  "reading-plan-calculator",
  "grocery-budget-planner",
]);

type Input = Record<string, unknown>;
type MealTotal = { name: string; unit: string; category: string; quantity: number };

function parseInput(content: string): Input {
  let value: unknown;
  try { value = JSON.parse(content); }
  catch { throw new Error("Gửi dữ liệu JSON hợp lệ cho công cụ lập kế hoạch này."); }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Dữ liệu phải là một JSON object.");
  }
  return value as Input;
}

function textValue(value: unknown, key: string, max = 120): string {
  if (typeof value !== "string") throw new Error(key + " phải là văn bản.");
  const result = value.trim().replace(/\s+/g, " ");
  if (!result || result.length > max) throw new Error(key + " phải có từ 1 đến " + max + " ký tự.");
  return result;
}

function numberValue(input: Input, key: string, min: number, max: number, fallback?: number): number {
  const value = input[key] === undefined ? fallback : input[key];
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) {
    throw new Error(key + " phải là số hữu hạn từ " + min + " đến " + max + ".");
  }
  return value;
}

function integerValue(input: Input, key: string, min: number, max: number, fallback?: number): number {
  const value = numberValue(input, key, min, max, fallback);
  if (!Number.isInteger(value)) throw new Error(key + " phải là số nguyên.");
  return value;
}

function currencyCode(value: unknown, fallback = "VND"): string {
  const code = String(value ?? fallback).trim().toUpperCase();
  if (!/^[A-Z]{3}$/.test(code)) throw new Error("currency phải là mã ba chữ cái như VND, USD hoặc EUR.");
  return code;
}

function moneyDigits(currency: string): number {
  if (["BIF","CLP","DJF","GNF","ISK","JPY","KMF","KRW","PYG","RWF","UGX","UYI","VND","VUV","XAF","XOF","XPF"].includes(currency)) return 0;
  if (["BHD","IQD","JOD","KWD","LYD","OMR","TND"].includes(currency)) return 3;
  return 2;
}

function rounded(value: number, places = 2): number {
  const scale = 10 ** places;
  return Math.round((value + Number.EPSILON) * scale) / scale;
}

function fmt(value: number, places = 3): string {
  return Number(value.toFixed(places)).toString();
}

function moneyText(value: number, currency: string): string {
  const places = moneyDigits(currency);
  return currency + " " + rounded(value, places).toFixed(places);
}

function parseDate(value: unknown, key: string): Date {
  const raw = textValue(value, key, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(raw)) throw new Error(key + " phải có định dạng YYYY-MM-DD.");
  const date = new Date(raw + "T00:00:00.000Z");
  if (Number.isNaN(date.getTime()) || date.toISOString().slice(0, 10) !== raw) {
    throw new Error(key + " không phải ngày hợp lệ.");
  }
  return date;
}

export function runPersonalPlanningTextTool(toolId: string, content: string): string {
  if (!PERSONAL_PLANNING_TOOL_IDS.has(toolId)) throw new Error("Personal planning tool is not enabled for this ID.");
  const input = parseInput(content);

  if (toolId === "meal-shopping-list-planner") {
    const meals = input.meals;
    if (!Array.isArray(meals) || meals.length < 1 || meals.length > 50) throw new Error("meals phải có từ 1 đến 50 món.");
    const totals = new Map<string, MealTotal>();
    let ingredientCount = 0;
    for (let mealIndex = 0; mealIndex < meals.length; mealIndex++) {
      const meal = meals[mealIndex];
      if (!meal || typeof meal !== "object" || Array.isArray(meal)) throw new Error("Mỗi meal phải là object.");
      const row = meal as Record<string, unknown>;
      const name = textValue(row.name, "meal name", 100);
      const servings = typeof row.servings === "number" && Number.isFinite(row.servings) ? row.servings : NaN;
      const target = typeof row.target_servings === "number" && Number.isFinite(row.target_servings) ? row.target_servings : NaN;
      if (servings < 0.1 || servings > 1000 || target < 0.1 || target > 1000) throw new Error("servings và target_servings phải từ 0.1 đến 1000.");
      if (!Array.isArray(row.ingredients) || row.ingredients.length < 1 || row.ingredients.length > 100) throw new Error(name + " phải có từ 1 đến 100 nguyên liệu.");
      for (const rawIngredient of row.ingredients) {
        ingredientCount++;
        if (ingredientCount > 300) throw new Error("Tổng số nguyên liệu vượt giới hạn 300.");
        if (!rawIngredient || typeof rawIngredient !== "object" || Array.isArray(rawIngredient)) throw new Error("Mỗi ingredient phải là object.");
        const ingredient = rawIngredient as Record<string, unknown>;
        const itemName = textValue(ingredient.name, "ingredient name", 100);
        const unit = textValue(ingredient.unit, "ingredient unit", 24);
        const category = textValue(ingredient.category ?? "Other", "ingredient category", 40);
        const qty = typeof ingredient.quantity === "number" && Number.isFinite(ingredient.quantity) ? ingredient.quantity : NaN;
        if (qty < 0.000001 || qty > 1_000_000) throw new Error("ingredient quantity phải từ 0.000001 đến 1000000.");
        const key = itemName.toLocaleLowerCase() + "\u0000" + unit.toLocaleLowerCase();
        const current = totals.get(key) ?? { name: itemName, unit, category, quantity: 0 };
        current.quantity += qty * target / servings;
        totals.set(key, current);
      }
    }
    const grouped = new Map<string, MealTotal[]>();
    for (const item of totals.values()) grouped.set(item.category, [...(grouped.get(item.category) ?? []), item]);
    const lines = ["Meal plan shopping list", "Meals: " + meals.length, "Unique shopping items: " + totals.size,
      "Quantities are scaled to each meal's target servings; identical names and units are combined."];
    for (const category of [...grouped.keys()].sort((a,b)=>a.localeCompare(b))) {
      lines.push("", category);
      for (const item of grouped.get(category)!.sort((a,b)=>a.name.localeCompare(b.name))) {
        lines.push("- [ ] " + fmt(item.quantity) + " " + item.unit + " " + item.name);
      }
    }
    return lines.join("\n");
  }

  if (toolId === "travel-packing-checklist") {
    const days = integerValue(input, "days", 1, 365);
    const travelers = integerValue(input, "travelers", 1, 30);
    const nights = integerValue(input, "nights", 0, 365, Math.max(0, days - 1));
    if (nights > days) throw new Error("nights không được lớn hơn days.");
    const climate = String(input.climate ?? "mild").trim().toLowerCase();
    if (!["hot","mild","cold","rainy","mixed"].includes(climate)) throw new Error("climate phải là hot, mild, cold, rainy hoặc mixed.");
    const allowed = new Set(["beach","swimming","hiking","business","formal","camping","gym"]);
    if (input.activities !== undefined && (!Array.isArray(input.activities) || input.activities.length > 12 ||
      input.activities.some(value => typeof value !== "string" || !allowed.has(value.trim().toLowerCase())))) {
      throw new Error("activities chỉ nhận tối đa 12 nhãn hoạt động được hỗ trợ.");
    }
    const activities = new Set((input.activities as string[] | undefined ?? []).map(value=>value.trim().toLowerCase()));
    const laundry = input.laundry_available ?? false;
    const international = input.international ?? false;
    if (typeof laundry !== "boolean" || typeof international !== "boolean") throw new Error("laundry_available và international phải là true hoặc false.");
    const items: Array<[string,string,number]> = [];
    const add = (category:string,name:string,quantity:number) => { if(quantity>0) items.push([category,name,quantity]); };
    const clothingDays = laundry ? Math.min(days,5) : days;
    add("Clothing","Tops / shirts",clothingDays*travelers);
    add("Clothing","Underwear",(laundry?Math.min(days+1,6):days+1)*travelers);
    add("Clothing","Socks",(laundry?Math.min(days+1,6):days+1)*travelers);
    add("Clothing","Bottoms / trousers",Math.max(1,Math.ceil(days/2))*travelers);
    add("Clothing","Sleepwear",Math.max(1,Math.ceil(Math.max(nights,1)/2))*travelers);
    add("Essentials","Toiletry kit",travelers);
    add("Essentials","Phone charger",travelers);
    add("Essentials","Photo ID",travelers);
    add("Essentials","Passport / international travel document",international?travelers:0);
    add("Essentials","Travel medication and prescriptions",travelers);
    add("Essentials","Reusable water bottle",travelers);
    add("Footwear","Comfortable everyday shoes",travelers);
    if(climate==="cold"||climate==="mixed"){add("Weather","Warm layer / jacket",travelers);add("Weather","Thermal layer",climate==="cold"?travelers:0);}
    if(climate==="rainy"||climate==="mixed"){add("Weather","Rain jacket",travelers);add("Weather","Compact umbrella",1);}
    if(climate==="hot"){add("Weather","Sun hat",travelers);add("Weather","Sunscreen",Math.max(1,Math.ceil(travelers/2)));}
    if(activities.has("beach")||activities.has("swimming")){add("Activities","Swimwear",travelers);add("Activities","Quick-dry towel",travelers);}
    if(activities.has("hiking")){add("Activities","Hiking shoes",travelers);add("Activities","Daypack",travelers);}
    if(activities.has("business")||activities.has("formal"))add("Activities","Smart / formal outfit",travelers);
    if(activities.has("gym"))add("Activities","Workout outfit",travelers);
    if(activities.has("camping")){add("Activities","Headlamp / flashlight",travelers);add("Activities","Reusable snack / food container",travelers);}
    const extras = input.custom_items ?? [];
    if(!Array.isArray(extras)||extras.length>50)throw new Error("custom_items phải là danh sách tối đa 50 món.");
    const lines=["Travel packing checklist","Trip length: "+days+" days / "+nights+" nights","Travellers: "+travelers,
      "Climate supplied by user: "+climate,"Suggested quantities are general starting points, not personal or official travel requirements."];
    let category="";
    for(const [group,name,quantity] of items){if(group!==category){category=group;lines.push("",group);}lines.push("- [ ] "+quantity+" × "+name);}
    if(extras.length){lines.push("","Your extra items");for(const extra of extras)lines.push("- [ ] "+textValue(extra,"custom item",100));}
    return lines.join("\n");
  }

  if (toolId === "study-plan-scheduler") {
    const start = parseDate(input.start_date, "start_date");
    const available = integerValue(input, "available_minutes_per_day", 15, 720);
    const session = integerValue(input, "session_minutes", 10, 180, 50);
    const dayNames = ["mon","tue","wed","thu","fri","sat","sun"];
    const daysRaw = input.study_days ?? ["Mon","Tue","Wed","Thu","Fri"];
    if(!Array.isArray(daysRaw)||daysRaw.length<1||daysRaw.length>7)throw new Error("study_days phải có từ 1 đến 7 ngày.");
    const studyDays = new Set<number>();
    for(const value of daysRaw){if(typeof value!=="string"||!dayNames.includes(value.trim().slice(0,3).toLowerCase()))throw new Error("study_days chỉ nhận Mon đến Sun.");studyDays.add(dayNames.indexOf(value.trim().slice(0,3).toLowerCase()));}
    const tasksRaw = input.tasks;
    if(!Array.isArray(tasksRaw)||tasksRaw.length<1||tasksRaw.length>60)throw new Error("tasks phải có từ 1 đến 60 mục.");
    const tasks = tasksRaw.map((raw,index)=>{
      if(!raw||typeof raw!=="object"||Array.isArray(raw))throw new Error("Mỗi study task phải là object.");
      const row=raw as Record<string,unknown>, name=textValue(row.name,"task name",100);
      const due=parseDate(row.due_date,"due_date");
      const delta=Math.floor((due.getTime()-start.getTime())/86400000);
      if(delta<0||delta>366)throw new Error("due_date phải từ start_date đến 366 ngày sau.");
      const hours=numberValue(row,"estimated_hours",0.01,500);
      const priority=integerValue(row,"priority",1,5,3);
      return {name,due:due.toISOString().slice(0,10),remaining:Math.ceil(hours*60),priority,order:index};
    }).sort((a,b)=>a.due.localeCompare(b.due)||b.priority-a.priority||a.order-b.order);
    const capacity = new Map<string,number>();
    const schedule = new Map<string,Array<[string,number]>>();
    const dayMs = 86400000;
    for(const task of tasks){
      let cursor=new Date(start.getTime());
      const due=new Date(task.due+"T00:00:00.000Z");
      while(cursor.getTime()<=due.getTime()&&task.remaining>0){
        const weekday=(cursor.getUTCDay()+6)%7;
        const key=cursor.toISOString().slice(0,10);
        if(studyDays.has(weekday)){
          const remainToday=capacity.get(key)??available;
          const chunk=Math.min(session,task.remaining,remainToday);
          if(chunk>0){schedule.set(key,[...(schedule.get(key)??[]),[task.name,chunk]]);capacity.set(key,remainToday-chunk);task.remaining-=chunk;}
        }
        cursor=new Date(cursor.getTime()+dayMs);
      }
    }
    const lines=["Study plan schedule","Start date: "+start.toISOString().slice(0,10),"Daily study capacity: "+available+" minutes",
      "Session target: up to "+session+" minutes","Tasks are scheduled by earliest deadline, then higher priority. Breaks are not included in study minutes.",""];
    let total=0;
    for(const key of [...schedule.keys()].sort()){
      const entries=schedule.get(key)!;
      lines.push(key+" ("+new Date(key+"T00:00:00.000Z").toLocaleDateString("en-US",{weekday:"long",timeZone:"UTC"})+")");
      for(const [name,minutes] of entries){lines.push("- "+minutes+" min · "+name);total+=minutes;}
      lines.push("  Planned total: "+entries.reduce((sum,item)=>sum+item[1],0)+" min");
    }
    const incomplete=tasks.filter(task=>task.remaining>0);
    lines.push("","Tasks: "+tasks.length,"Scheduled study time: "+total+" minutes","Unscheduled tasks: "+incomplete.length);
    if(incomplete.length){lines.push("Not enough study capacity before these deadlines:");for(const task of incomplete)lines.push("- "+task.name+": "+fmt(task.remaining/60,2)+" hours remain");}
    return lines.join("\n");
  }

  if (toolId === "weekly-chore-planner") {
    if(!Array.isArray(input.people)||input.people.length<1||input.people.length>20)throw new Error("people phải có từ 1 đến 20 tên.");
    const people=input.people.map(value=>textValue(value,"person name",60));
    if(new Set(people.map(value=>value.toLocaleLowerCase())).size!==people.length)throw new Error("Tên thành viên phải khác nhau.");
    if(!Array.isArray(input.chores)||input.chores.length<1||input.chores.length>100)throw new Error("chores phải có từ 1 đến 100 việc.");
    const dayNames=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
    const dayLoad=Array(7).fill(0) as number[];
    const personLoad=Array(people.length).fill(0) as number[];
    const schedule=Array.from({length:7},()=>[] as Array<[string,string,number]>);
    let occurrenceCount=0;
    for(const raw of input.chores){
      if(!raw||typeof raw!=="object"||Array.isArray(raw))throw new Error("Mỗi chore phải là object.");
      const chore=raw as Record<string,unknown>;
      const name=textValue(chore.name,"chore name",100);
      const frequency=integerValue(chore,"times_per_week",1,7,1);
      const duration=integerValue(chore,"duration_minutes",1,480);
      const preferred=chore.preferred_days??dayNames;
      if(!Array.isArray(preferred)||preferred.length<1)throw new Error("preferred_days phải là danh sách ngày không rỗng.");
      const allowed=[...new Set(preferred.map(value=>{
        if(typeof value!=="string")throw new Error("preferred_days phải chứa tên ngày.");
        const day=dayNames.findIndex(item=>item.toLowerCase()===value.trim().slice(0,3).toLowerCase());
        if(day<0)throw new Error("preferred_days chỉ nhận Mon đến Sun.");
        return day;
      }))].sort((a,b)=>a-b);
      if(frequency>allowed.length)throw new Error("times_per_week không được lớn hơn số preferred_days.");
      const used=new Set<number>();
      for(let index=0;index<frequency;index++){
        occurrenceCount++;if(occurrenceCount>300)throw new Error("Tổng số lần phân công vượt 300.");
        const choices=allowed.filter(day=>!used.has(day));
        const day=choices.sort((a,b)=>dayLoad[a]-dayLoad[b]||schedule[a]!.length-schedule[b]!.length||a-b)[0]!;
        used.add(day);
        const personIndex=people.map((_name,i)=>i).sort((a,b)=>personLoad[a]-personLoad[b]||a-b)[0]!;
        schedule[day]!.push([name,people[personIndex]!,duration]);
        dayLoad[day]+=duration;personLoad[personIndex]+=duration;
      }
    }
    const lines=["Weekly household chore plan","Assignments balance estimated minutes between people and spread tasks across allowed days.",""];
    for(let day=0;day<7;day++){const entries=schedule[day]!;if(entries.length){lines.push(dayNames[day]!);for(const [name,person,duration] of entries)lines.push("- "+name+": "+person+" ("+duration+" min)");lines.push("  Day total: "+dayLoad[day]+" min");}}
    lines.push("","Weekly workload by person");
    people.forEach((name,index)=>lines.push("- "+name+": "+personLoad[index]+" min"));
    return lines.join("\n");
  }

  if (toolId === "subscription-cost-calculator") {
    if(!Array.isArray(input.subscriptions)||input.subscriptions.length<1||input.subscriptions.length>200)throw new Error("subscriptions phải có từ 1 đến 200 mục.");
    const factors:Record<string,number>={weekly:52,monthly:12,quarterly:4,semiannual:2,yearly:1};
    const totals=new Map<string,number>();
    const entries=input.subscriptions.map(raw=>{
      if(!raw||typeof raw!=="object"||Array.isArray(raw))throw new Error("Mỗi subscription phải là object.");
      const item=raw as Record<string,unknown>;
      const name=textValue(item.name,"subscription name",100);
      const amount=numberValue(item,"amount",0,1_000_000_000);
      const cycle=String(item.billing_cycle??"").trim().toLowerCase();
      if(factors[cycle]===undefined)throw new Error("billing_cycle phải là weekly, monthly, quarterly, semiannual hoặc yearly.");
      const currency=currencyCode(item.currency,input.currency===undefined?"VND":String(input.currency));
      const annual=rounded(amount*factors[cycle],moneyDigits(currency));
      totals.set(currency,(totals.get(currency)??0)+annual);
      return {name,amount,cycle,currency,annual};
    });
    const lines=["Recurring subscription cost report","Subscriptions: "+entries.length,
      "Annualized totals assume the same price and billing cycle for 12 months; no currency conversion is performed.",""];
    for(const entry of entries){lines.push("- "+entry.name+": "+moneyText(entry.amount,entry.currency)+" / "+entry.cycle);lines.push("  Annualized: "+moneyText(entry.annual,entry.currency));}
    lines.push("","Totals by currency");
    for(const currency of [...totals.keys()].sort()){
      const annual=rounded(totals.get(currency)!,moneyDigits(currency));
      lines.push("- "+currency+": "+moneyText(annual,currency)+" per year; "+moneyText(annual/12,currency)+" average per month");
    }
    return lines.join("\n");
  }

  if (toolId === "commute-cost-calculator") {
    const mode=String(input.mode??"").trim().toLowerCase();
    if(mode!=="car"&&mode!=="public_transport")throw new Error("mode phải là car hoặc public_transport.");
    const days=integerValue(input,"commute_days_per_month",1,31);
    const currency=currencyCode(input.currency);
    let total=0;
    const lines=["Monthly commute cost estimate","Commute days per month: "+days,"Mode: "+mode];
    if(mode==="car"){
      const distance=numberValue(input,"distance_one_way_km",0.01,1000);
      const consumption=numberValue(input,"consumption_l_per_100km",0.01,100);
      const price=numberValue(input,"fuel_price_per_litre",0,100_000_000);
      const parking=numberValue(input,"parking_per_day",0,100_000_000,0);
      const tolls=numberValue(input,"tolls_per_day",0,100_000_000,0);
      const sharing=integerValue(input,"people_sharing",1,20,1);
      const litres=distance*2*days*consumption/100;
      const fuel=rounded(litres*price,moneyDigits(currency));
      const other=rounded((parking+tolls)*days,moneyDigits(currency));
      total=rounded(fuel+other,moneyDigits(currency));
      const perPerson=rounded(total/sharing,moneyDigits(currency));
      lines.push("Round-trip distance per commute day: "+fmt(distance*2,2)+" km",
        "Estimated fuel use per month: "+fmt(litres,2)+" L",
        "Fuel cost: "+moneyText(fuel,currency),"Parking and tolls: "+moneyText(other,currency),
        "Total monthly commute cost: "+moneyText(total,currency),"People sharing: "+sharing,
        "Estimated monthly cost per person: "+moneyText(perPerson,currency),
        "Estimate uses user-entered fuel consumption, fuel price, parking and tolls.");
    } else {
      const fare=numberValue(input,"round_trip_fare",0,100_000_000);
      const payg=rounded(fare*days,moneyDigits(currency));
      total=payg;
      lines.push("Pay-as-you-go total: "+moneyText(payg,currency));
      if(input.monthly_pass_price!==undefined){
        const pass=rounded(numberValue(input,"monthly_pass_price",0,100_000_000),moneyDigits(currency));
        total=Math.min(payg,pass);
        lines.push("Monthly pass price: "+moneyText(pass,currency),
          "Lower-cost option based on entered values: "+(pass<payg?"monthly pass":"pay as you go"));
      }
      lines.push("Estimated monthly transit cost: "+moneyText(total,currency),
        "Estimate uses fares supplied by the user; concession, peak and route-specific fares are not checked.");
    }
    return lines.join("\n");
  }

  if (toolId === "reading-plan-calculator") {
    const pages=integerValue(input,"pages_remaining",1,10_000_000);
    const days=integerValue(input,"days_until_deadline",1,3660);
    const perWeek=integerValue(input,"reading_days_per_week",1,7,7);
    const fullWeeks=Math.floor(days/7), remainder=days%7;
    const sessions=Math.max(1,fullWeeks*perWeek+Math.min(perWeek,remainder));
    const suggested=Math.ceil(pages/sessions);
    const lines=["Reading goal plan","Pages remaining: "+pages,"Days until deadline: "+days,
      "Reading sessions assumed: "+sessions,"Suggested pace: about "+suggested+" pages per reading day"];
    if(input.pages_per_hour!==undefined){
      const rate=numberValue(input,"pages_per_hour",0.1,1000);
      lines.push("Estimated reading time per session: about "+fmt(suggested/rate*60,1)+" minutes",
        "Time estimate depends on the user's reading speed and text difficulty.");
    } else lines.push("Add pages_per_hour to estimate reading minutes; actual reading speed varies.");
    return lines.join("\n");
  }

  if (toolId === "grocery-budget-planner") {
    if(!Array.isArray(input.items)||input.items.length<1||input.items.length>300)throw new Error("items phải có từ 1 đến 300 món.");
    const currency=currencyCode(input.currency);
    const budget=rounded(numberValue(input,"budget",0,1_000_000_000_000),moneyDigits(currency));
    const totals=new Map<string,number>();
    let total=0;
    const rows=input.items.map(raw=>{
      if(!raw||typeof raw!=="object"||Array.isArray(raw))throw new Error("Mỗi item phải là object.");
      const item=raw as Record<string,unknown>;
      const name=textValue(item.name,"item name",100);
      const quantity=numberValue(item,"quantity",0.000001,1_000_000);
      const unitPrice=numberValue(item,"unit_price",0,1_000_000_000);
      const category=textValue(item.category??"Other","category",40);
      const line=rounded(quantity*unitPrice,moneyDigits(currency));
      total+=line;totals.set(category,(totals.get(category)??0)+line);
      return {name,quantity,unitPrice,category,line};
    });
    total=rounded(total,moneyDigits(currency));
    const difference=rounded(budget-total,moneyDigits(currency));
    const lines=["Grocery and shopping budget","Currency: "+currency,"Budget: "+moneyText(budget,currency),""];
    for(const row of rows)lines.push("- "+row.name+" ("+row.category+"): "+fmt(row.quantity)+" × "+moneyText(row.unitPrice,currency)+" = "+moneyText(row.line,currency));
    lines.push("","Spending by category");
    for(const category of [...totals.keys()].sort((a,b)=>a.localeCompare(b)))lines.push("- "+category+": "+moneyText(rounded(totals.get(category)!,moneyDigits(currency)),currency));
    lines.push("","Estimated total: "+moneyText(total,currency));
    lines.push(difference>=0?"Budget remaining: "+moneyText(difference,currency):"Over budget by: "+moneyText(-difference,currency));
    lines.push("Prices and quantities are user-entered estimates; no retailer prices or stock are checked.");
    return lines.join("\n");
  }

  throw new Error("Unknown personal planning tool.");
}
