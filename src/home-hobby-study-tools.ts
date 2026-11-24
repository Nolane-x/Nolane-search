export const HOME_HOBBY_STUDY_TOOL_IDS = new Set([
  "habit-history-analyzer",
  "plant-care-scheduler",
  "garden-bed-capacity-calculator",
  "home-inventory-report",
  "home-maintenance-scheduler",
  "pet-routine-planner",
  "event-seating-planner",
  "spaced-review-scheduler",
]);

type Input = Record<string, unknown>;
type Row = Record<string, unknown>;
const DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];

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
  const result = value.trim().replace(/\s+/g," ");
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
  const raw = textValue(value,key,10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(raw)) throw new Error(key + " phải có định dạng YYYY-MM-DD.");
  const result = new Date(raw + "T00:00:00.000Z");
  if (Number.isNaN(result.getTime()) || result.toISOString().slice(0,10) !== raw) throw new Error(key + " không phải ngày hợp lệ.");
  return result;
}
function dateKey(value: Date): string { return value.toISOString().slice(0,10); }
function addDays(value: Date, days: number): Date { return new Date(value.getTime() + days * 86400000); }
function dayDifference(later: Date, earlier: Date): number { return Math.round((later.getTime()-earlier.getTime())/86400000); }
function dayName(value: Date): string { return DAYS[(value.getUTCDay()+6)%7]!; }
function currencyCode(value: unknown, fallback="VND"): string {
  const code=String(value??fallback).trim().toUpperCase();
  if(!/^[A-Z]{3}$/.test(code))throw new Error("currency phải là mã ba chữ cái như VND, USD hoặc EUR.");
  return code;
}
function minorUnits(currency: string): number {
  if(["BIF","CLP","DJF","GNF","ISK","JPY","KMF","KRW","PYG","RWF","UGX","UYI","VND","VUV","XAF","XOF","XPF"].includes(currency))return 0;
  if(["BHD","IQD","JOD","KWD","LYD","OMR","TND"].includes(currency))return 3;
  return 2;
}
function rounded(value:number, places:number):number {
  const scale=10**places;
  return Math.round((value+Number.EPSILON)*scale)/scale;
}
function moneyText(value:number,currency:string):string {
  return currency+" "+rounded(value,minorUnits(currency)).toFixed(minorUnits(currency));
}
function addMonths(value:Date,months:number):Date {
  const total=value.getUTCFullYear()*12+value.getUTCMonth()+months;
  const year=Math.floor(total/12),month=total%12;
  const day=Math.min(value.getUTCDate(),new Date(Date.UTC(year,month+1,0)).getUTCDate());
  return new Date(Date.UTC(year,month,day));
}

export function runHomeHobbyStudyTextTool(toolId:string,content:string):string {
  if(!HOME_HOBBY_STUDY_TOOL_IDS.has(toolId))throw new Error("Home/hobby/study tool is not enabled for this ID.");
  const input=parseInput(content);

  if(toolId==="habit-history-analyzer"){
    const asOf=parseDate(input.as_of_date,"as_of_date");
    const window=integerValue(input.window_days,"window_days",7,365,30);
    if(!Array.isArray(input.habits)||input.habits.length<1||input.habits.length>100)throw new Error("habits phải có từ 1 đến 100 mục.");
    const start=addDays(asOf,-(window-1));
    const lines=["Habit history report","As of: "+dateKey(asOf),"Review window: "+window+" days",""];
    for(const raw of input.habits){
      const habit=row(raw,"habit");
      const name=textValue(habit.name,"habit name",100);
      const target=integerValue(habit.target_days_per_week,"target_days_per_week",1,7,7);
      if(!Array.isArray(habit.check_ins)||habit.check_ins.length>2000)throw new Error(name+": check_ins phải là danh sách tối đa 2.000 ngày.");
      const dates=new Set<string>();
      for(const item of habit.check_ins){const key=dateKey(parseDate(item,"check-in date"));if(key>dateKey(asOf))throw new Error(name+": check-in date không được sau as_of_date.");dates.add(key);}
      const recent=[...dates].filter(key=>key>=dateKey(start)&&key<=dateKey(asOf)).sort();
      const required=Math.ceil(window*target/7);
      const completion=Math.min(100,Math.round(recent.length/required*100));
      let longest=0,current=0,previous:Date|null=null;
      for(const key of [...dates].sort()){
        const currentDate=parseDate(key,"check-in date");
        current=previous&&dayDifference(currentDate,previous)===1?current+1:1;
        longest=Math.max(longest,current);previous=currentDate;
      }
      let cursor=dates.has(dateKey(asOf))?asOf:addDays(asOf,-1);
      let streak=0;
      while(dates.has(dateKey(cursor))){streak++;cursor=addDays(cursor,-1);}
      const sortedDates=[...dates].sort();
      const last=sortedDates[sortedDates.length-1];
      lines.push(name,"- Target: "+target+" check-in day(s) per week",
        "- Check-ins in window: "+recent.length+" / "+required+" target",
        "- Target completion: "+completion+"%",
        "- Current streak: "+streak+" day(s)",
        "- Longest recorded streak: "+longest+" day(s)",
        "- Last check-in: "+(last??"none recorded"),"");
    }
    lines.push("Check-ins are user supplied. The report does not infer missed days before the recorded history.");
    return lines.join("\n");
  }

  if(toolId==="plant-care-scheduler"){
    const asOf=parseDate(input.as_of_date,"as_of_date");
    const window=integerValue(input.window_days,"window_days",1,180,30);
    if(!Array.isArray(input.plants)||input.plants.length<1||input.plants.length>100)throw new Error("plants phải có từ 1 đến 100 cây.");
    const due:Array<{due:Date;plant:string;task:string;interval:number;overdue:number}>=[];
    let count=0;
    for(const raw of input.plants){
      const plant=row(raw,"plant"),plantName=textValue(plant.name,"plant name",100);
      if(!Array.isArray(plant.care_tasks)||plant.care_tasks.length<1||plant.care_tasks.length>20)throw new Error(plantName+": care_tasks phải có từ 1 đến 20 mục.");
      for(const item of plant.care_tasks){
        count++;if(count>300)throw new Error("Tổng số care tasks vượt 300.");
        const task=row(item,"care task"),name=textValue(task.task,"care task",60);
        const last=parseDate(task.last_done,"last_done"),interval=integerValue(task.every_days,"every_days",1,3650);
        const dueDate=addDays(last,interval);
        due.push({due:dueDate,plant:plantName,task:name,interval,overdue:Math.max(0,dayDifference(asOf,dueDate))});
      }
    }
    due.sort((a,b)=>dateKey(a.due).localeCompare(dateKey(b.due))||a.plant.localeCompare(b.plant)||a.task.localeCompare(b.task));
    const end=addDays(asOf,window);
    const lines=["Plant care schedule","As of: "+dateKey(asOf),"Planning window: "+window+" days",
      "Intervals are entered by the user; no species or weather recommendations are implied.",""];
    for(const item of due){
      const status=item.due<asOf?"OVERDUE by "+item.overdue+" day(s)":item.due.getTime()===asOf.getTime()?"Due today":"Upcoming";
      if(item.due<=end)lines.push("- "+dateKey(item.due)+" | "+item.plant+" | "+item.task+" | every "+item.interval+" day(s) | "+status);
      else lines.push("- "+item.plant+" | "+item.task+" | next due "+dateKey(item.due)+" (outside this window)");
    }
    return lines.join("\n");
  }

  if(toolId==="garden-bed-capacity-calculator"){
    if(!Array.isArray(input.beds)||input.beds.length<1||input.beds.length>50)throw new Error("beds phải có từ 1 đến 50 luống.");
    const lines=["Garden bed planting capacity","Estimates use rectangular beds and even row/plant spacing",""];
    let total=0,totalArea=0;
    for(const raw of input.beds){
      const bed=row(raw,"bed"),name=textValue(bed.name,"bed name",80);
      const length=numberValue(bed.length_m,"length_m",0.05,1000);
      const width=numberValue(bed.width_m,"width_m",0.05,1000);
      const plantSpacing=numberValue(bed.plant_spacing_cm,"plant_spacing_cm",1,5000);
      const rowSpacing=numberValue(bed.row_spacing_cm,"row_spacing_cm",1,5000);
      const margin=numberValue(bed.edge_margin_cm??0,"edge_margin_cm",0,500);
      const usableLength=length*100-margin*2,usableWidth=width*100-margin*2;
      if(usableLength<=0||usableWidth<=0)throw new Error(name+": edge margin leaves no usable planting area.");
      const plantsPerRow=Math.max(0,Math.floor(usableLength/plantSpacing));
      const rows=Math.max(0,Math.floor(usableWidth/rowSpacing));
      const count=plantsPerRow*rows,area=length*width;
      total+=count;totalArea+=area;
      lines.push(name,"- Bed size: "+area.toFixed(2)+" m²","- Rows: "+rows,
        "- Plants per row: "+plantsPerRow,"- Estimated capacity: "+count+" plant(s)","");
    }
    lines.push("Total garden area: "+totalArea.toFixed(2)+" m²","Estimated total planting capacity: "+total+" plant(s)",
      "Actual capacity varies with access paths, plant shape, growth habit and local growing guidance.");
    return lines.join("\n");
  }

  if(toolId==="home-inventory-report"){
    const asOf=parseDate(input.as_of_date,"as_of_date");
    if(!Array.isArray(input.items)||input.items.length<1||input.items.length>300)throw new Error("items phải có từ 1 đến 300 món.");
    const totals=new Map<string,number>(),categoryTotals=new Map<string,number>();
    const lines=["Home inventory report","As of: "+dateKey(asOf),"Items: "+input.items.length,""];
    for(const raw of input.items){
      const item=row(raw,"inventory item");
      const name=textValue(item.name,"item name",100),category=textValue(item.category??"Other","category",50);
      const quantity=integerValue(item.quantity,"quantity",1,1_000_000,1);
      const price=numberValue(item.purchase_price_per_item??0,"purchase_price_per_item",0,1_000_000_000_000);
      const currency=currencyCode(item.currency,input.currency===undefined?"VND":String(input.currency));
      const subtotal=rounded(price*quantity,minorUnits(currency));
      totals.set(currency,(totals.get(currency)??0)+subtotal);
      const catKey=currency+"\u0000"+category;categoryTotals.set(catKey,(categoryTotals.get(catKey)??0)+subtotal);
      const purchase=parseDate(item.purchase_date,"purchase_date");
      if(purchase>asOf)throw new Error(name+": purchase_date không được sau as_of_date.");
      lines.push("- "+name+" ("+category+") × "+quantity+": "+moneyText(subtotal,currency));
      if(item.warranty_months!==undefined){
        const warrantyMonths=integerValue(item.warranty_months,"warranty_months",0,600);
        const warranty=addMonths(purchase,warrantyMonths);
        lines.push("  Warranty: "+(warranty>=asOf?"active":"expired")+"; through "+dateKey(warranty));
      }
      if(item.expected_life_months!==undefined){
        const life=addMonths(purchase,integerValue(item.expected_life_months,"expected_life_months",1,1200));
        lines.push("  Expected service-life date entered by user: "+dateKey(life));
      }
      if(item.location!==undefined)lines.push("  Location: "+textValue(item.location,"location",80));
    }
    lines.push("","Value by currency");
    for(const currency of [...totals.keys()].sort())lines.push("- "+currency+": "+moneyText(totals.get(currency)!,currency));
    lines.push("","Value by category");
    for(const key of [...categoryTotals.keys()].sort()){
      const [currency,category]=key.split("\u0000");
      lines.push("- "+category+" ("+currency+"): "+moneyText(categoryTotals.get(key)!,currency!));
    }
    lines.push("Purchase values are historical user-entered amounts, not current resale values or insurance valuations.");
    return lines.join("\n");
  }

  if(toolId==="home-maintenance-scheduler"){
    const asOf=parseDate(input.as_of_date,"as_of_date"),window=integerValue(input.window_days,"window_days",1,730,90);
    if(!Array.isArray(input.tasks)||input.tasks.length<1||input.tasks.length>200)throw new Error("tasks phải có từ 1 đến 200 mục.");
    const rows=input.tasks.map(raw=>{
      const task=row(raw,"maintenance task"),name=textValue(task.name,"task name",100);
      const last=parseDate(task.last_completed,"last_completed");
      if(last>asOf)throw new Error(name+": last_completed không được sau as_of_date.");
      const interval=integerValue(task.every_days,"every_days",1,3650);
      const minutes=integerValue(task.estimated_minutes,"estimated_minutes",1,1440,30);
      const priority=integerValue(task.priority,"priority",1,5,3);
      const due=addDays(last,interval);
      const overdue=due<asOf?dayDifference(asOf,due):0;
      let next=new Date(due);
      while(next<asOf)next=addDays(next,interval);
      return {due,next,name,interval,minutes,priority,overdue};
    }).sort((a,b)=>a.due.getTime()-b.due.getTime()||b.priority-a.priority||a.name.localeCompare(b.name));
    const end=addDays(asOf,window);
    const lines=["Home maintenance schedule","As of: "+dateKey(asOf),"Planning window: "+window+" days",
      "Intervals and estimated times are supplied by the user.",""];
    for(const task of rows){
      if(task.due<=asOf)lines.push("- "+task.name+": OVERDUE since "+dateKey(task.due)+" by "+task.overdue+" day(s); next cycle "+dateKey(task.next)+" | priority "+task.priority+" | "+task.minutes+" min");
      else if(task.due<=end)lines.push("- "+dateKey(task.due)+" | "+task.name+" | every "+task.interval+" day(s) | priority "+task.priority+" | "+task.minutes+" min");
      else lines.push("- "+task.name+": next due "+dateKey(task.due)+" (outside this window)");
    }
    const dueSoon=rows.filter(task=>task.due>=asOf&&task.due<=end);
    lines.push("","Tasks due in this window: "+dueSoon.length,
      "Estimated minutes for non-overdue tasks due in this window: "+dueSoon.reduce((sum,task)=>sum+task.minutes,0));
    return lines.join("\n");
  }

  if(toolId==="pet-routine-planner"){
    const start=parseDate(input.start_date,"start_date"),days=integerValue(input.days,"days",1,31,7);
    if(!Array.isArray(input.pets)||input.pets.length<1||input.pets.length>30)throw new Error("pets phải có từ 1 đến 30 thú cưng.");
    const schedule=new Map<string,Array<{time:string;pet:string;task:string;note:string}>>();
    let count=0;
    for(const raw of input.pets){
      const pet=row(raw,"pet"),petName=textValue(pet.name,"pet name",80);
      if(!Array.isArray(pet.routines)||pet.routines.length<1||pet.routines.length>30)throw new Error(petName+": routines phải có từ 1 đến 30 mục.");
      for(const rawRoutine of pet.routines){
        count++;if(count>300)throw new Error("Tổng số pet routines vượt 300.");
        const routine=row(rawRoutine,"routine"),task=textValue(routine.task,"routine task",80);
        const time=textValue(routine.time??"09:00","routine time",5);
        if(!/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(time))throw new Error("routine time phải có định dạng HH:MM.");
        const selected=routine.days_of_week??DAYS;
        if(!Array.isArray(selected)||selected.length<1||selected.length>7)throw new Error("days_of_week phải có từ 1 đến 7 ngày.");
        const weekdays=new Set<number>();
        for(const value of selected){
          if(typeof value!=="string")throw new Error("days_of_week phải chứa tên ngày.");
          const idx=DAYS.findIndex(day=>day.toLowerCase()===value.trim().slice(0,3).toLowerCase());
          if(idx<0)throw new Error("days_of_week chỉ nhận Mon đến Sun.");
          weekdays.add(idx);
        }
        const note=routine.note===undefined?"":textValue(routine.note,"routine note",120);
        for(let offset=0;offset<days;offset++){
          const current=addDays(start,offset),weekday=(current.getUTCDay()+6)%7,key=dateKey(current);
          if(weekdays.has(weekday))schedule.set(key,[...(schedule.get(key)??[]),{time,pet:petName,task,note}]);
        }
      }
    }
    const lines=["Pet routine checklist","Start date: "+dateKey(start),"Planning horizon: "+days+" days",
      "Only non-medical daily care routines are included. Follow veterinary instructions for medical care.",""];
    for(const key of [...schedule.keys()].sort()){
      lines.push(key+" ("+DAYS[(parseDate(key,"date").getUTCDay()+6)%7]+")");
      for(const item of schedule.get(key)!.sort((a,b)=>a.time.localeCompare(b.time)||a.pet.localeCompare(b.pet))){
        lines.push("- [ ] "+item.time+" | "+item.pet+" | "+item.task+(item.note?" — "+item.note:""));
      }
      lines.push("");
    }
    if(schedule.size===0)lines.push("No routine occurrences fall within this planning window.");
    return lines.join("\n");
  }

  if(toolId==="event-seating-planner"){
    if(!Array.isArray(input.tables)||input.tables.length<1||input.tables.length>100)throw new Error("tables phải có từ 1 đến 100 bàn.");
    if(!Array.isArray(input.guest_groups)||input.guest_groups.length<1||input.guest_groups.length>300)throw new Error("guest_groups phải có từ 1 đến 300 nhóm.");
    const avoidRaw=input.avoid_pairs??[];
    if(!Array.isArray(avoidRaw)||avoidRaw.length>500)throw new Error("avoid_pairs chỉ được có tối đa 500 cặp.");
    const tables=input.tables.map(raw=>{
      const table=row(raw,"table"),name=textValue(table.name,"table name",80);
      const seats=integerValue(table.seats,"table seats",1,100);
      return {name,seats,guests:[] as string[]};
    });
    if(new Set(tables.map(x=>x.name.toLowerCase())).size!==tables.length)throw new Error("Tên bàn phải duy nhất.");
    const guestSet=new Set<string>();
    const groups=input.guest_groups.map(raw=>{
      const group=row(raw,"guest group"),name=textValue(group.name,"guest group name",80);
      if(!Array.isArray(group.guests)||group.guests.length<1||group.guests.length>100)throw new Error(name+": guests phải có từ 1 đến 100 người.");
      const guests=group.guests.map(value=>textValue(value,"guest name",80));
      if(new Set(guests.map(x=>x.toLowerCase())).size!==guests.length)throw new Error(name+": tên khách phải duy nhất trong nhóm.");
      for(const guest of guests){const key=guest.toLowerCase();if(guestSet.has(key))throw new Error("Guest appears more than once: "+guest+".");guestSet.add(key);}
      return {name,guests};
    }).sort((a,b)=>b.guests.length-a.guests.length||a.name.localeCompare(b.name));
    const blocked=new Set<string>();
    for(const raw of avoidRaw){
      if(!Array.isArray(raw)||raw.length!==2)throw new Error("Mỗi avoid_pairs entry phải có đúng hai tên.");
      const a=textValue(raw[0],"avoid guest name",80).toLowerCase(),b=textValue(raw[1],"avoid guest name",80).toLowerCase();
      if(a===b||!guestSet.has(a)||!guestSet.has(b))throw new Error("Avoid pairs phải gọi đúng hai khách khác nhau trong danh sách.");
      blocked.add([a,b].sort().join("\u0000"));
    }
    const unassigned:Array<{name:string;guests:string[]}>=[];
    for(const group of groups){
      const keys=group.guests.map(x=>x.toLowerCase());
      const options:Array<{remaining:number;index:number}>=[];
      tables.forEach((table,index)=>{
        const remaining=table.seats-table.guests.length;
        if(remaining<group.guests.length)return;
        const seated=table.guests.map(x=>x.toLowerCase());
        const conflict=keys.some(guest=>seated.some(other=>blocked.has([guest,other].sort().join("\u0000"))));
        if(!conflict)options.push({remaining:remaining-group.guests.length,index});
      });
      options.sort((a,b)=>a.remaining-b.remaining||a.index-b.index);
      if(!options.length){unassigned.push(group);continue;}
      tables[options[0]!.index]!.guests.push(...group.guests);
    }
    const lines=["Event seating plan","Guests: "+guestSet.size,"Tables: "+tables.length,
      "Each guest group is kept together; avoid pairs are never assigned to the same table.",""];
    let assigned=0;
    for(const table of tables){
      assigned+=table.guests.length;
      lines.push(table.name+" — "+table.guests.length+"/"+table.seats+" seats");
      for(const guest of table.guests)lines.push("- "+guest);
      lines.push("");
    }
    const notAssigned=unassigned.reduce((sum,x)=>sum+x.guests.length,0);
    lines.push("Assigned guests: "+assigned+"/"+guestSet.size,"Unassigned guests: "+notAssigned);
    if(unassigned.length){lines.push("Groups needing another table or relaxed constraints:");for(const group of unassigned)lines.push("- "+group.name+": "+group.guests.join(", "));}
    return lines.join("\n");
  }

  if(toolId==="spaced-review-scheduler"){
    const asOf=parseDate(input.as_of_date,"as_of_date"),window=integerValue(input.planning_days,"planning_days",1,90,14);
    if(!Array.isArray(input.topics)||input.topics.length<1||input.topics.length>300)throw new Error("topics phải có từ 1 đến 300 mục.");
    const intervals:Record<number,number>={1:1,2:2,3:4,4:7,5:14};
    const rows=input.topics.map(raw=>{
      const topic=row(raw,"topic"),name=textValue(topic.name,"topic name",100);
      const last=parseDate(topic.last_reviewed,"last_reviewed");
      if(last>asOf)throw new Error(name+": last_reviewed không được sau as_of_date.");
      const confidence=integerValue(topic.confidence,"confidence",1,5);
      const interval=integerValue(topic.interval_days,"interval_days",1,365,intervals[confidence]!);
      const due=addDays(last,interval),effective=due<asOf?asOf:due;
      return {name,confidence,interval,due,effective,overdue:due<asOf?dayDifference(asOf,due):0};
    }).sort((a,b)=>a.effective.getTime()-b.effective.getTime()||b.confidence-a.confidence||a.name.localeCompare(b.name));
    const end=addDays(asOf,window);
    const lines=["Spaced review plan","As of: "+dateKey(asOf),"Planning window: "+window+" days",
      "Confidence-based interval heuristic: 1→1 day, 2→2, 3→4, 4→7, 5→14. A custom interval_days overrides it.",
      "This is a simple planner, not the FSRS algorithm or a claim of scientifically optimised intervals.",""];
    for(const topic of rows){
      if(topic.effective<=end){
        const state=topic.overdue>0?"OVERDUE by "+topic.overdue+" day(s)":topic.due.getTime()===asOf.getTime()?"Review today":"Upcoming";
        lines.push("- "+dateKey(topic.effective)+" | "+topic.name+" | confidence "+topic.confidence+"/5 | interval "+topic.interval+" day(s) | "+state);
      } else lines.push("- "+topic.name+": next review "+dateKey(topic.effective)+" (outside this window)");
    }
    return lines.join("\n");
  }

  throw new Error("Unknown home/hobby/study tool.");
}
