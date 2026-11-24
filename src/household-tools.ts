const HOUSEHOLD_TOOL_IDS = new Set([
  "appliance-energy-calculator", "floor-tile-calculator", "concrete-volume-calculator",
  "soil-mulch-calculator", "household-budget-calculator", "savings-goal-calculator",
  "travel-budget-calculator", "download-time-calculator", "work-hours-calculator",
  "battery-runtime-calculator", "water-tank-volume-calculator",
]);

type Input = Record<string, unknown>;

function parseInput(content: string): Input {
  let value: unknown;
  try { value = JSON.parse(content); }
  catch { throw new Error("Gửi dữ liệu JSON hợp lệ cho tiện ích này."); }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Dữ liệu tiện ích phải là một JSON object.");
  }
  return value as Input;
}

function numberValue(input: Input, key: string, min: number, max: number, fallback?: number): number {
  const raw = input[key] === undefined ? fallback : input[key];
  if (typeof raw !== "number" || !Number.isFinite(raw) || raw < min || raw > max) {
    throw new Error(key + " phải là số từ " + min + " đến " + max + ".");
  }
  return raw;
}

function integerValue(input: Input, key: string, min: number, max: number, fallback?: number): number {
  const value = numberValue(input, key, min, max, fallback);
  if (!Number.isInteger(value)) throw new Error(key + " phải là số nguyên.");
  return value;
}

function currencyCode(input: Input): string {
  const code = String(input.currency ?? "VND").trim().toUpperCase();
  if (!/^[A-Z]{3}$/.test(code)) throw new Error("currency phải là mã ba chữ cái, ví dụ VND, USD hoặc EUR.");
  return code;
}

function currencyDigits(code: string): number {
  if (["BIF","CLP","DJF","GNF","ISK","JPY","KMF","KRW","PYG","RWF","UGX","UYI","VND","VUV","XAF","XOF","XPF"].includes(code)) return 0;
  if (["BHD","IQD","JOD","KWD","LYD","OMR","TND"].includes(code)) return 3;
  return 2;
}

function round(value: number, digits = 2): number {
  const scale = 10 ** digits;
  return Math.round((value + Number.EPSILON) * scale) / scale;
}

function fmt(value: number, digits = 3): string {
  return Number(value.toFixed(digits)).toString();
}

function money(value: number, code: string): string {
  const digits = currencyDigits(code);
  return code + " " + round(value, digits).toFixed(digits);
}

function listItems(value: unknown, label: string, min = 1, max = 200): Record<string, unknown>[] {
  if (!Array.isArray(value) || value.length < min || value.length > max) {
    throw new Error(label + " phải có từ " + min + " đến " + max + " mục.");
  }
  if (value.some(item => !item || typeof item !== "object" || Array.isArray(item))) {
    throw new Error("Mỗi mục trong " + label + " phải là object.");
  }
  return value as Record<string, unknown>[];
}

export function runHouseholdTextTool(toolId: string, content: string): string {
  if (!HOUSEHOLD_TOOL_IDS.has(toolId)) throw new Error("Tiện ích gia đình không được bật cho ID này.");
  const input = parseInput(content);

  if (toolId === "appliance-energy-calculator") {
    const currency = currencyCode(input);
    const tariff = numberValue(input, "price_per_kwh", 0, 1e9);
    const items = listItems(input.appliances, "appliances");
    let totalKwh = 0, totalCost = 0;
    const lines = ["Home electricity-use estimate", "Price assumption: " + money(tariff, currency) + " per kWh", "", "Appliances:"];
    items.forEach((item,index) => {
      const name = String(item.name ?? ("Appliance " + (index+1))).slice(0,100);
      const watts = numberValue(item, "watts", 0.01, 1e6);
      const hours = numberValue(item, "hours_per_day", 0, 24);
      const days = numberValue(item, "days_per_month", 0, 31, 30);
      const quantity = integerValue(item, "quantity", 1, 1000, 1);
      const kwh = watts * hours * days * quantity / 1000;
      const cost = round(kwh * tariff, currencyDigits(currency));
      totalKwh += kwh; totalCost += cost;
      lines.push("- " + name + " ×" + quantity + ": " + fmt(watts) + " W × " + fmt(hours) +
        " h/day × " + fmt(days) + " days = " + fmt(kwh) + " kWh; " + money(cost,currency));
    });
    lines.push("", "Total monthly energy: " + fmt(totalKwh) + " kWh",
      "Estimated monthly cost: " + money(totalCost,currency),
      "Estimate only: actual meter readings, tiered tariffs, taxes and fixed charges may differ.");
    return lines.join("\n");
  }

  if (toolId === "floor-tile-calculator") {
    const currency = currencyCode(input), digits = currencyDigits(currency);
    const length = numberValue(input,"room_length_m",0.1,1000);
    const width = numberValue(input,"room_width_m",0.1,1000);
    const tileLength = numberValue(input,"tile_length_cm",1,300);
    const tileWidth = numberValue(input,"tile_width_cm",1,300);
    const waste = numberValue(input,"waste_percent",0,50,10);
    const perBox = integerValue(input,"tiles_per_box",1,1000);
    const price = round(numberValue(input,"price_per_box",0,1e12,0),digits);
    const area = length * width, tileArea = tileLength * tileWidth / 10000;
    const tileCount = Math.ceil(Math.ceil(area / tileArea) * (1+waste/100));
    const boxes = Math.ceil(tileCount / perBox), purchased = boxes * perBox;
    const cost = round(boxes * price,digits);
    return ["Floor tile estimator","Room: "+fmt(length)+" m × "+fmt(width)+" m = "+fmt(area,2)+" m²",
      "Tile: "+fmt(tileLength)+" cm × "+fmt(tileWidth)+" cm = "+fmt(tileArea,4)+" m² each",
      "Waste allowance: "+fmt(waste)+"%","Tiles required including waste: "+tileCount,
      "Tiles per box: "+perBox,"Boxes to buy: "+boxes+" ("+purchased+" tiles)",
      "Estimated material cost: "+money(cost,currency),
      "Estimate excludes grout, adhesive, trims and installation."].join("\n");
  }

  if (toolId === "concrete-volume-calculator") {
    const length=numberValue(input,"length_m",0.01,1000), width=numberValue(input,"width_m",0.01,1000);
    const depth=numberValue(input,"depth_m",0.001,100), waste=numberValue(input,"waste_percent",0,50,10);
    const base=length*width*depth, adjusted=base*(1+waste/100);
    const lines=["Concrete volume estimate","Dimensions: "+fmt(length)+" m × "+fmt(width)+" m × "+fmt(depth)+" m",
      "Base volume: "+fmt(base,4)+" m³ ("+fmt(base*1000,1)+" litres)","Waste allowance: "+fmt(waste)+"%",
      "Order estimate: "+fmt(adjusted,4)+" m³ ("+fmt(adjusted*1000,1)+" litres)"];
    if(input.bag_yield_l!==undefined){
      const yieldL=numberValue(input,"bag_yield_l",0.1,1000), bags=Math.ceil(adjusted*1000/yieldL);
      lines.push("Yield per bag: "+fmt(yieldL)+" litres","Bags required: "+bags);
      if(input.price_per_bag!==undefined){
        const currency=currencyCode(input), price=round(numberValue(input,"price_per_bag",0,1e12),currencyDigits(currency));
        lines.push("Estimated bag cost: "+money(bags*price,currency));
      }
    }
    lines.push("Estimate only; finished volume varies by mix, compaction, ground conditions and supplier yield.");
    return lines.join("\n");
  }

  if (toolId === "soil-mulch-calculator") {
    const area=numberValue(input,"area_m2",0.01,1e6), depth=numberValue(input,"depth_cm",0.1,500);
    const waste=numberValue(input,"waste_percent",0,50,10), base=area*depth*10, required=base*(1+waste/100);
    const lines=["Soil and mulch volume estimate","Area: "+fmt(area)+" m²","Depth: "+fmt(depth)+" cm",
      "Base volume: "+fmt(base,1)+" litres ("+fmt(base/1000,3)+" m³)","Waste allowance: "+fmt(waste)+"%",
      "Order estimate: "+fmt(required,1)+" litres ("+fmt(required/1000,3)+" m³)"];
    if(input.bag_volume_l!==undefined){
      const bagL=numberValue(input,"bag_volume_l",0.1,1000), bags=Math.ceil(required/bagL);
      lines.push("Bag size: "+fmt(bagL)+" litres","Bags required: "+bags);
      if(input.price_per_bag!==undefined){
        const currency=currencyCode(input), price=round(numberValue(input,"price_per_bag",0,1e12),currencyDigits(currency));
        lines.push("Estimated bag cost: "+money(bags*price,currency));
      }
    }
    return lines.join("\n");
  }

  if (toolId === "household-budget-calculator") {
    const currency=currencyCode(input), income=round(numberValue(input,"monthly_income",0,1e15),currencyDigits(currency));
    const expenses=listItems(input.expenses,"expenses",0);
    const groups=new Map<string,number>(); let total=0;
    expenses.forEach((item,index)=>{
      const category=String(item.category??"Other").slice(0,60)||"Other";
      const amount=round(numberValue(item,"monthly_amount",0,1e15),currencyDigits(currency));
      groups.set(category,(groups.get(category)??0)+amount); total+=amount;
    });
    const remaining=income-total;
    const lines=["Monthly household budget","Monthly income: "+money(income,currency),
      "Planned expenses: "+money(total,currency),"","Expenses by category:"];
    [...groups.entries()].sort((a,b)=>b[1]-a[1]).forEach(([name,value])=>{
      lines.push("- "+name+": "+money(value,currency)+" ("+(income?fmt(value/income*100,1):"n/a")+"% of income)");
    });
    lines.push("","Money remaining: "+money(remaining,currency),
      "Remaining share of income: "+(income?fmt(remaining/income*100,1):"n/a")+"%",
      "Cash-flow summary from the amounts entered; unlisted and irregular costs are excluded.");
    return lines.join("\n");
  }

  if (toolId === "savings-goal-calculator") {
    const currency=currencyCode(input), digits=currencyDigits(currency);
    const target=round(numberValue(input,"target_amount",0.01,1e15),digits);
    const current=round(numberValue(input,"current_savings",0,1e15,0),digits);
    const monthly=round(numberValue(input,"monthly_contribution",0,1e15),digits);
    const annual=numberValue(input,"annual_interest_rate_percent",0,100,0);
    if(current<target && monthly===0 && annual===0) throw new Error("The goal cannot be reached with zero monthly contributions and zero interest.");
    const rate=annual/1200; let balance=current, months=0;
    while(balance<target && months<1200){
      balance=round(balance*(1+rate)+monthly,digits); months++;
    }
    if(balance<target) throw new Error("Target not reached within 100 years; increase the contribution or adjust assumptions.");
    const contributed=round(current+monthly*months,digits), interest=round(balance-contributed,digits);
    const years=Math.floor(months/12), rem=months%12;
    return ["Savings goal estimate","Target: "+money(target,currency),"Starting savings: "+money(current,currency),
      "Monthly contribution: "+money(monthly,currency),"Annual interest assumption: "+fmt(annual)+"% (compounded monthly)",
      "Estimated time: "+months+" months ("+years+" years and "+rem+" months)",
      "Estimated balance at that point: "+money(balance,currency),"Total starting savings plus contributions: "+money(contributed,currency),
      "Estimated interest: "+money(interest,currency),
      "Illustration only: actual rates, taxes, fees, inflation and deposit timing can change the outcome."].join("\n");
  }

  if (toolId === "travel-budget-calculator") {
    const currency=currencyCode(input), digits=currencyDigits(currency);
    const people=integerValue(input,"travelers",1,1000), days=integerValue(input,"days",1,365);
    const buffer=numberValue(input,"buffer_percent",0,100,10), expenses=listItems(input.expenses,"expenses",0);
    const groups=new Map<string,number>(); let base=0;
    expenses.forEach((item,index)=>{
      const name=String(item.category??("Expense "+(index+1))).slice(0,80);
      const amount=round(numberValue(item,"total_cost",0,1e15),digits);
      groups.set(name,(groups.get(name)??0)+amount); base+=amount;
    });
    const total=round(base*(1+buffer/100),digits), perPerson=round(total/people,digits), perDay=round(perPerson/days,digits);
    const lines=["Travel budget estimate","Travelers: "+people,"Trip length: "+days+" days","","Budget by category:"];
    [...groups.entries()].sort((a,b)=>b[1]-a[1]).forEach(([name,value])=>lines.push("- "+name+": "+money(value,currency)));
    lines.push("","Base trip budget: "+money(base,currency),"Buffer: "+fmt(buffer)+"%",
      "Budget including buffer: "+money(total,currency),"Per person: "+money(perPerson,currency),
      "Per person per day: "+money(perDay,currency),"Costs not entered and exchange-rate changes are excluded.");
    return lines.join("\n");
  }

  if (toolId === "download-time-calculator") {
    const size=numberValue(input,"file_size",0.000001,1e15), sizeUnit=String(input.file_size_unit??"GB").trim().toUpperCase();
    const sizeFactors:Record<string,number>={B:1,KB:1e3,MB:1e6,GB:1e9,TB:1e12,KIB:1024,MIB:1048576,GIB:1073741824,TIB:1099511627776};
    if(!sizeFactors[sizeUnit]) throw new Error("file_size_unit must be B, KB, MB, GB, TB, KiB, MiB, GiB or TiB.");
    const speed=numberValue(input,"speed",0.000001,1e15), speedUnit=String(input.speed_unit??"Mbps").trim().toUpperCase();
    const speedFactors:Record<string,number>={BPS:1,Kbps:1000,KBPS:1000,MBPS:1e6,GBPS:1e9,"B/S":8,"KB/S":8000,"MB/S":8e6,"GB/S":8e9,"KIB/S":8192,"MIB/S":8388608,"GIB/S":8589934592};
    if(!speedFactors[speedUnit]) throw new Error("Use bps, Kbps, Mbps, Gbps, B/s, KB/s, MB/s, GB/s, KiB/s, MiB/s or GiB/s.");
    const overhead=numberValue(input,"overhead_percent",0,100,0);
    const seconds=size*sizeFactors[sizeUnit]*8*(1+overhead/100)/(speed*speedFactors[speedUnit]);
    const wholeMinutes=Math.floor(seconds/60), hours=Math.floor(wholeMinutes/60), minutes=wholeMinutes%60, rest=seconds-wholeMinutes*60;
    return ["Download time estimate","File size: "+fmt(size)+" "+sizeUnit,"Connection speed: "+fmt(speed)+" "+speedUnit,
      "Overhead allowance: "+fmt(overhead)+"%","Estimated time: "+hours+" h "+minutes+" min "+fmt(rest,1)+" sec",
      "Seconds: "+fmt(seconds,1),"Theoretical estimate assumes the stated speed is sustained; congestion and server limits can lengthen the transfer."].join("\n");
  }

  if (toolId === "work-hours-calculator") {
    const currency=currencyCode(input), digits=currencyDigits(currency);
    const rate=round(numberValue(input,"hourly_rate",0,1e12,0),digits), shifts=listItems(input.shifts,"shifts");
    let totalHours=0,totalPay=0;
    const lines=["Work hours summary","Hourly rate assumption: "+money(rate,currency),"","Shifts:"];
    shifts.forEach((item,index)=>{
      const label=String(item.label??("Shift "+(index+1))).slice(0,80);
      const start=String(item.start??""), end=String(item.end??"");
      const pattern=/^(?:[01]\d|2[0-3]):[0-5]\d$/;
      if(!pattern.test(start)||!pattern.test(end)) throw new Error(label+" start/end must use HH:MM (24-hour time).");
      const toMins=(s:string)=>Number(s.slice(0,2))*60+Number(s.slice(3));
      let duration=toMins(end)-toMins(start); if(duration<=0) duration+=1440;
      if(duration>=1440) throw new Error(label+" duration must be less than 24 hours.");
      const pause=integerValue(item,"break_minutes",0,duration-1,0);
      const paid=(duration-pause)/60, pay=round(paid*rate,digits);
      totalHours+=paid; totalPay+=pay;
      lines.push("- "+label+": "+start+"–"+end+"; break "+pause+" min; paid "+fmt(paid,2)+" h; pay "+money(pay,currency));
    });
    lines.push("","Total paid hours: "+fmt(totalHours,2),"Estimated gross pay: "+money(totalPay,currency),
      "Arithmetic estimate only; local overtime, tax, holiday and employment rules are not applied.");
    return lines.join("\n");
  }

  if (toolId === "battery-runtime-calculator") {
    const power=numberValue(input,"device_power_w",0.001,100000);
    const efficiency=numberValue(input,"efficiency_percent",0.1,100,85);
    const reserve=numberValue(input,"reserve_percent",0,90,0);
    let capacity:number;
    if(input.battery_wh!==undefined) capacity=numberValue(input,"battery_wh",0.001,1e8);
    else capacity=numberValue(input,"capacity_mah",0.001,1e9)*numberValue(input,"voltage_v",0.001,1000)/1000;
    const usable=capacity*(1-reserve/100)*efficiency/100, hours=usable/power;
    const whole=Math.round(hours*60), h=Math.floor(whole/60), m=whole%60;
    return ["Battery runtime estimate","Nominal energy: "+fmt(capacity,3)+" Wh","Efficiency assumption: "+fmt(efficiency)+"%",
      "Reserved capacity: "+fmt(reserve)+"%","Usable energy estimate: "+fmt(usable,3)+" Wh",
      "Device power draw: "+fmt(power)+" W","Estimated runtime: "+h+" h "+m+" min",
      "Estimate assumes constant power draw; battery age, temperature and device power management can change runtime."].join("\n");
  }

  if (toolId === "water-tank-volume-calculator") {
    const shape=String(input.shape??"rectangular").trim().toLowerCase();
    let capacity:number, dimensions:string;
    if(shape==="rectangular"){
      const length=numberValue(input,"length_m",0.01,1000), width=numberValue(input,"width_m",0.01,1000);
      const height=numberValue(input,"height_m",0.01,100);
      capacity=length*width*height*1000; dimensions=fmt(length)+" m × "+fmt(width)+" m × "+fmt(height)+" m";
    } else if(shape==="cylinder"){
      const radius=numberValue(input,"radius_m",0.01,100), height=numberValue(input,"height_m",0.01,1000);
      capacity=Math.PI*radius*radius*height*1000; dimensions="radius "+fmt(radius)+" m × height "+fmt(height)+" m";
    } else throw new Error("shape must be rectangular or cylinder.");
    const fill=numberValue(input,"fill_percent",0,100,100);
    return ["Water tank capacity","Shape: "+shape,"Dimensions: "+dimensions,
      "Full capacity: "+fmt(capacity,1)+" litres ("+fmt(capacity/1000,3)+" m³)",
      "Fill level: "+fmt(fill)+"%","Water at this fill level: "+fmt(capacity*fill/100,1)+" litres",
      "Geometric estimate; actual usable capacity is lower when fittings, freeboard and internal equipment take up space."].join("\n");
  }

  throw new Error("Unknown household utility.");
}
