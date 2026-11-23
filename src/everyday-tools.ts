export const EVERYDAY_TOOL_IDS = new Set([
  "bill-split-calculator", "loan-payment-calculator", "date-calculator", "timezone-converter",
  "recipe-scaler", "grade-calculator", "paint-calculator", "fuel-trip-calculator",
  "discount-calculator", "unit-price-comparator",
]);

type Input = Record<string, unknown>;
type UnitInfo = { dimension: string; base: string; factor: number };

function parseInput(content: string): Input {
  let value: unknown;
  try { value = JSON.parse(content); }
  catch { throw new Error("Gửi dữ liệu theo dạng JSON hợp lệ cho máy tính này."); }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Dữ liệu máy tính phải là một JSON object.");
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
  const currency = String(input.currency ?? "USD").trim().toUpperCase();
  if (!/^[A-Z]{3}$/.test(currency)) throw new Error("currency phải là mã tiền tệ ba chữ cái, ví dụ VND, USD hoặc EUR.");
  return currency;
}

function decimalsFor(currency: string): number {
  if (["BIF","CLP","DJF","GNF","ISK","JPY","KMF","KRW","PYG","RWF","UGX","UYI","VND","VUV","XAF","XOF","XPF"].includes(currency)) return 0;
  if (["BHD","IQD","JOD","KWD","LYD","OMR","TND"].includes(currency)) return 3;
  return 2;
}

function rounded(value: number, digits: number): number {
  const scale = 10 ** digits;
  return Math.round((value + Number.EPSILON) * scale) / scale;
}

function fmt(value: number, digits = 4): string {
  return Number(value.toFixed(digits)).toString();
}

function formatMoney(value: number, currency: string): string {
  return currency + " " + rounded(value, decimalsFor(currency)).toFixed(decimalsFor(currency));
}

function parseDate(value: unknown, key: string): Date {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error(key + " phải có định dạng YYYY-MM-DD.");
  const date = new Date(value + "T00:00:00.000Z");
  if (Number.isNaN(date.getTime()) || date.toISOString().slice(0, 10) !== value) throw new Error(key + " không phải ngày hợp lệ.");
  return date;
}

function dayText(date: Date): string {
  return ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"][date.getUTCDay()]!;
}

function getLocalParts(instant: Date, timezone: string): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: timezone, year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
  }).formatToParts(instant);
  const values = Object.fromEntries(parts.map(part => [part.type, part.value]));
  return values.year + "-" + values.month + "-" + values.day + "T" +
    values.hour + ":" + values.minute + ":" + values.second;
}

function timezoneOffsetMinutes(instant: Date, timezone: string): number {
  const local = getLocalParts(instant, timezone);
  const asUtc = Date.parse(local + "Z");
  return Math.round((asUtc - instant.getTime()) / 60000);
}

function timezoneConversion(input: Input): string {
  const value = String(input.local_datetime ?? "");
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/.exec(value);
  if (!match) throw new Error("local_datetime phải có dạng YYYY-MM-DDTHH:MM[:SS] không kèm UTC offset.");
  const parts = match.slice(1).map((part, index) => Number(part ?? (index === 5 ? 0 : 0)));
  const [year, month, day, hour, minute, second] = parts;
  const naive = new Date(Date.UTC(year!, month! - 1, day!, hour!, minute!, second!));
  if (naive.getUTCFullYear() !== year || naive.getUTCMonth() + 1 !== month ||
      naive.getUTCDate() !== day || naive.getUTCHours() !== hour ||
      naive.getUTCMinutes() !== minute || naive.getUTCSeconds() !== second) {
    throw new Error("local_datetime không phải thời gian hợp lệ.");
  }
  const source = String(input.from_timezone ?? "").trim();
  const target = String(input.to_timezone ?? "").trim();
  if (!source || !target || source.length > 80 || target.length > 80) throw new Error("Cần from_timezone và to_timezone là tên múi giờ IANA.");
  let offsets: number[];
  try {
    offsets = [];
    for (let hours = -48; hours <= 48; hours += 3) {
      offsets.push(timezoneOffsetMinutes(new Date(naive.getTime() + hours * 3600000), source));
    }
    // Validate target timezone before computing the conversion.
    getLocalParts(naive, target);
  } catch {
    throw new Error("Hãy dùng tên múi giờ IANA hợp lệ, ví dụ Asia/Ho_Chi_Minh hoặc America/New_York.");
  }
  const wanted = value.length === 16 ? value + ":00" : value;
  const candidates = [...new Set(offsets)].map(offset => new Date(naive.getTime() - offset * 60000))
    .filter(candidate => getLocalParts(candidate, source) === wanted)
    .sort((a,b) => a.getTime() - b.getTime());
  const fold = input.fold;
  if (fold !== undefined && fold !== 0 && fold !== 1) throw new Error("fold chỉ nhận giá trị 0 hoặc 1.");
  if (candidates.length === 0) throw new Error("Thời gian địa phương không tồn tại do đồng hồ của múi giờ chuyển giờ.");
  const selected = candidates.length > 1 && fold !== undefined ? [candidates[fold]!] : candidates;
  const lines = ["Timezone converter", "From: " + source, "To: " + target];
  selected.forEach((candidate, index) => {
    lines.push(
      (selected.length > 1 ? "Possible interpretation " + (index + 1) : "Local time") + ": " + wanted,
      "UTC: " + candidate.toISOString(),
      "Converted: " + getLocalParts(candidate, target) + " (" + target + ")",
    );
  });
  if (selected.length > 1) lines.push("Giờ địa phương này xuất hiện hai lần khi chuyển DST; cả hai cách hiểu hợp lệ được liệt kê. Dùng fold 0 hoặc 1 để chọn.");
  return lines.join("\n");
}

const UNIT_MAP: Record<string, UnitInfo> = {
  mg:{dimension:"mass",base:"g",factor:0.001}, milligram:{dimension:"mass",base:"g",factor:0.001}, milligrams:{dimension:"mass",base:"g",factor:0.001},
  g:{dimension:"mass",base:"g",factor:1}, gram:{dimension:"mass",base:"g",factor:1}, grams:{dimension:"mass",base:"g",factor:1},
  kg:{dimension:"mass",base:"g",factor:1000}, kilogram:{dimension:"mass",base:"g",factor:1000}, kilograms:{dimension:"mass",base:"g",factor:1000},
  ml:{dimension:"volume",base:"mL",factor:1}, milliliter:{dimension:"volume",base:"mL",factor:1}, milliliters:{dimension:"volume",base:"mL",factor:1}, millilitre:{dimension:"volume",base:"mL",factor:1}, millilitres:{dimension:"volume",base:"mL",factor:1},
  l:{dimension:"volume",base:"mL",factor:1000}, liter:{dimension:"volume",base:"mL",factor:1000}, liters:{dimension:"volume",base:"mL",factor:1000}, litre:{dimension:"volume",base:"mL",factor:1000}, litres:{dimension:"volume",base:"mL",factor:1000},
  cm:{dimension:"length",base:"cm",factor:1}, centimeter:{dimension:"length",base:"cm",factor:1}, centimeters:{dimension:"length",base:"cm",factor:1}, centimetre:{dimension:"length",base:"cm",factor:1}, centimetres:{dimension:"length",base:"cm",factor:1},
  m:{dimension:"length",base:"cm",factor:100}, meter:{dimension:"length",base:"cm",factor:100}, meters:{dimension:"length",base:"cm",factor:100}, metre:{dimension:"length",base:"cm",factor:100}, metres:{dimension:"length",base:"cm",factor:100},
  each:{dimension:"count",base:"each",factor:1}, unit:{dimension:"count",base:"each",factor:1}, units:{dimension:"count",base:"each",factor:1}, pc:{dimension:"count",base:"each",factor:1}, pcs:{dimension:"count",base:"each",factor:1}, piece:{dimension:"count",base:"each",factor:1}, pieces:{dimension:"count",base:"each",factor:1},
};

export function runEverydayTextTool(toolId: string, content: string): string {
  if (!EVERYDAY_TOOL_IDS.has(toolId)) throw new Error("Máy tính đời thường không được bật cho ID này.");
  const input = parseInput(content);
  const moneyPlaces = (currency: string) => decimalsFor(currency);
  if (toolId === "bill-split-calculator") {
    const currency = currencyCode(input); const digits = moneyPlaces(currency);
    const subtotal = rounded(numberValue(input,"bill_amount",0.01,1e15),digits);
    const tipPercent = numberValue(input,"tip_percent",0,100,0);
    const taxPercent = numberValue(input,"tax_percent",0,100,0);
    const people = integerValue(input,"people",1,1000);
    const tip = rounded(subtotal * tipPercent / 100,digits);
    const tax = rounded(subtotal * taxPercent / 100,digits);
    const total = rounded(subtotal + tip + tax,digits);
    const share = rounded(total / people,digits);
    const last = rounded(total - share * (people-1),digits);
    return [
      "Bill split calculator", "Subtotal: " + formatMoney(subtotal,currency),
      "Tax (" + fmt(taxPercent) + "%): " + formatMoney(tax,currency),
      "Tip (" + fmt(tipPercent) + "%): " + formatMoney(tip,currency),
      "Total: " + formatMoney(total,currency), "People: " + people,
      "Per person (first " + (people-1) + "): " + formatMoney(share,currency),
      "Final person's adjusted share: " + formatMoney(last,currency),
    ].join("\n");
  }
  if (toolId === "loan-payment-calculator") {
    const currency=currencyCode(input), digits=moneyPlaces(currency);
    const principal=rounded(numberValue(input,"principal",0.01,1e15),digits);
    const apr=numberValue(input,"annual_rate_percent",0,500);
    const months=integerValue(input,"term_months",1,600);
    const extra=rounded(numberValue(input,"extra_monthly_payment",0,1e15,0),digits);
    const rate=apr/1200;
    const scheduled=rounded(rate===0 ? principal/months : principal*rate/(1-Math.pow(1+rate,-months)),digits);
    let balance=principal, interestTotal=0, totalPaid=0, count=0;
    while(balance>0 && count<months){
      count++;
      const interest=rounded(balance*rate,digits);
      const due=rounded(scheduled+extra,digits);
      if(due<=interest) throw new Error("Khoản thanh toán tháng không giảm được dư nợ; tăng mức trả hoặc rút ngắn kỳ hạn.");
      const actual=Math.min(due,rounded(balance+interest,digits));
      const principalPaid=rounded(actual-interest,digits);
      balance=rounded(balance-principalPaid,digits);
      interestTotal=rounded(interestTotal+interest,digits);
      totalPaid=rounded(totalPaid+actual,digits);
    }
    return ["Loan payment calculator", "Scheduled payment: "+formatMoney(scheduled,currency)+" per month before extras",
      "Months to repay: "+count, "Total paid: "+formatMoney(totalPaid,currency),
      "Total interest: "+formatMoney(interestTotal,currency),
      "This is a mathematical estimate, not a lender quote; fees, insurance and variable rates are excluded."].join("\n");
  }
  if (toolId === "date-calculator") {
    const start=parseDate(input.start_date,"start_date");
    if(input.end_date===undefined){
      const offset=integerValue(input,"offset_days",-365000,365000);
      const result=new Date(start.getTime()+offset*86400000);
      return ["Date calculator","Start: "+input.start_date+" ("+dayText(start)+")",
        "Offset: "+(offset>=0?"+":"")+offset+" days",
        "Result: "+result.toISOString().slice(0,10)+" ("+dayText(result)+")"].join("\n");
    }
    const end=parseDate(input.end_date,"end_date");
    const include=input.include_end_date===undefined?true:input.include_end_date;
    if(typeof include!=="boolean") throw new Error("include_end_date phải là true hoặc false.");
    const delta=Math.round((end.getTime()-start.getTime())/86400000);
    const first=Math.min(start.getTime(),end.getTime()), last=Math.max(start.getTime(),end.getTime());
    let weekdays=0;
    for(let day=first;day<=last;day+=86400000){
      const date=new Date(day);
      if(date.getUTCDay()!==0 && date.getUTCDay()!==6 && (include || day!==end.getTime())) weekdays++;
    }
    return ["Date calculator","Start: "+input.start_date+" ("+dayText(start)+")",
      "End: "+input.end_date+" ("+dayText(end)+")",
      "Elapsed days: "+delta,
      "Calendar days in range: "+(Math.abs(delta)+(include?1:0)),
      "Weekdays in range: "+weekdays].join("\n");
  }
  if (toolId === "timezone-converter") return timezoneConversion(input);
  if (toolId === "recipe-scaler") {
    const original=numberValue(input,"original_servings",0.01,100000);
    const target=numberValue(input,"target_servings",0.01,100000);
    if(!Array.isArray(input.ingredients)||input.ingredients.length<1||input.ingredients.length>200) throw new Error("ingredients cần từ 1 đến 200 nguyên liệu.");
    const factor=target/original;
    const lines=["Recipe scaler","Servings: "+fmt(original)+" → "+fmt(target),"Scale factor: ×"+fmt(factor,4),"","Ingredients:"];
    input.ingredients.forEach((raw,index)=>{
      if(!raw||typeof raw!=="object"||Array.isArray(raw)) throw new Error("Ingredient "+(index+1)+" phải là object.");
      const item=raw as Record<string,unknown>, name=String(item.name??"").trim(), unit=String(item.unit??"").trim();
      if(!name||name.length>120||unit.length>32) throw new Error("Mỗi nguyên liệu cần tên và đơn vị ngắn.");
      if(typeof item.amount==="number" && Number.isFinite(item.amount) && item.amount>=0){
        lines.push((index+1)+". "+fmt(item.amount*factor,4)+" "+unit+" "+name);
      } else if(typeof item.amount==="string" && item.amount.trim().length>0 && item.amount.length<=80){
        lines.push((index+1)+". "+item.amount.trim()+" "+unit+" "+name+" (unchanged; non-numeric amount)");
      } else throw new Error("amount cần là số không âm hoặc nội dung như 'to taste'.");
    });
    return lines.join("\n");
  }
  if (toolId === "grade-calculator") {
    if(!Array.isArray(input.components)||input.components.length<1||input.components.length>200) throw new Error("components cần từ 1 đến 200 môn/đầu điểm.");
    let weight=0, earned=0;
    const lines=["Grade calculator","Components:"];
    input.components.forEach((raw,index)=>{
      if(!raw||typeof raw!=="object"||Array.isArray(raw)) throw new Error("Component "+(index+1)+" phải là object.");
      const item=raw as Record<string,unknown>, name=String(item.name??("Component "+(index+1))).slice(0,100);
      const score=numberValue(item,"score",0,1e6);
      const max=numberValue(item,"max_score",0.000001,1e6,100);
      const share=numberValue(item,"weight_percent",0.000001,100);
      if(score>max) throw new Error(name+" score không được vượt max_score.");
      weight+=share; const percent=score/max*100; earned+=percent*share/100;
      lines.push("- "+name+": "+fmt(score)+"/"+fmt(max)+" = "+fmt(percent,2)+"%; weight "+fmt(share)+"%");
    });
    if(weight>100) throw new Error("Tổng weight_percent không được vượt 100.");
    const remaining=100-weight, average=weight?earned/weight*100:0;
    lines.push("Graded weight: "+fmt(weight)+"%","Remaining weight: "+fmt(remaining)+"%",
      "Weighted points already earned: "+fmt(earned,2)+"/100",
      "Average across graded components: "+fmt(average,2)+"%");
    if(input.target_overall_percent!==undefined){
      const target=numberValue(input,"target_overall_percent",0,100);
      lines.push("Target overall result: "+fmt(target)+"%");
      if(remaining===0) lines.push(earned>=target?"Target reached.":"Target cannot be reached from entered completed components.");
      else {
        const needed=(target-earned)/remaining*100;
        lines.push("Required average across remaining work: "+fmt(needed,2)+"%");
        if(needed>100) lines.push("Target is not reachable under a 100% score cap.");
        else if(needed<=0) lines.push("Target is already secured with zero points on remaining work.");
      }
    }
    return lines.join("\n");
  }
  if (toolId === "paint-calculator") {
    const length=numberValue(input,"length_m",0.1,1000), width=numberValue(input,"width_m",0.1,1000);
    const height=numberValue(input,"height_m",0.1,100), coats=integerValue(input,"coats",1,5,2);
    const coverage=numberValue(input,"coverage_m2_per_liter",0.1,1000,10);
    const doors=integerValue(input,"doors_count",0,100,0), doorArea=numberValue(input,"door_area_m2",0,20,2);
    const windows=integerValue(input,"windows_count",0,100,0), windowArea=numberValue(input,"window_area_m2",0,20,1.5);
    const waste=numberValue(input,"waste_percent",0,50,10), ceiling=input.include_ceiling??false;
    if(typeof ceiling!=="boolean") throw new Error("include_ceiling phải là true hoặc false.");
    const gross=2*(length+width)*height, openings=doors*doorArea+windows*windowArea;
    if(openings>=gross) throw new Error("Diện tích cửa phải nhỏ hơn tổng diện tích tường.");
    const area=gross-openings+(ceiling?length*width:0), required=area*coats/coverage*(1+waste/100);
    const recommended=Math.ceil(required/0.5)*0.5;
    return ["Paint coverage calculator","Gross wall area: "+fmt(gross,2)+" m²",
      "Openings deducted: "+fmt(openings,2)+" m²","Paintable area: "+fmt(area,2)+" m²",
      "Coats: "+coats,"Coverage: "+fmt(coverage)+" m²/L","Waste allowance: "+fmt(waste)+"%",
      "Estimated paint: "+fmt(required,2)+" L","Practical purchase estimate: about "+fmt(recommended,1)+" L"].join("\n");
  }
  if (toolId === "fuel-trip-calculator") {
    const currency=currencyCode(input), digits=moneyPlaces(currency);
    const distance=numberValue(input,"distance_km",0.01,1e7);
    if(input.round_trip!==undefined&&typeof input.round_trip!=="boolean") throw new Error("round_trip phải là true hoặc false.");
    const trips=integerValue(input,"trips",1,1000,1), passengers=integerValue(input,"passengers",1,1000,1);
    const consumption=numberValue(input,"consumption_l_per_100km",0.01,200);
    const price=rounded(numberValue(input,"fuel_price_per_liter",0.0001,1e9),digits);
    const totalDistance=distance*(input.round_trip===true?2:1)*trips;
    const liters=totalDistance*consumption/100, cost=rounded(liters*price,digits);
    return ["Fuel trip calculator","Total distance: "+fmt(totalDistance,2)+" km",
      "Estimated fuel: "+fmt(liters,2)+" L","Fuel cost: "+formatMoney(cost,currency),
      "Passengers: "+passengers,"Estimated cost per passenger: "+formatMoney(rounded(cost/passengers,digits),currency),
      "Fuel-only estimate; excludes tolls, parking and price changes."].join("\n");
  }
  if (toolId === "discount-calculator") {
    const currency=currencyCode(input), digits=moneyPlaces(currency);
    const price=rounded(numberValue(input,"original_price",0.01,1e15),digits);
    const discount=numberValue(input,"discount_percent",0,100);
    const extra=numberValue(input,"extra_discount_percent",0,100,0);
    const tax=numberValue(input,"tax_percent",0,100,0), quantity=integerValue(input,"quantity",1,100000,1);
    const discounted=price*(1-discount/100)*(1-extra/100);
    const taxAmount=rounded(discounted*tax/100,digits), unit=rounded(discounted+taxAmount,digits);
    const total=rounded(unit*quantity,digits);
    return ["Discount calculator","Original unit price: "+formatMoney(price,currency),
      "Price after discounts: "+formatMoney(discounted,currency),
      "Tax per item: "+formatMoney(taxAmount,currency),"Final unit price: "+formatMoney(unit,currency),
      "Quantity: "+quantity,"Total: "+formatMoney(total,currency)].join("\n");
  }
  if (toolId === "unit-price-comparator") {
    if(!Array.isArray(input.items)||input.items.length<2||input.items.length>100) throw new Error("items cần từ 2 đến 100 sản phẩm.");
    const currency=currencyCode(input), digits=moneyPlaces(currency);
    let dimension="", base="";
    const rows=input.items.map((raw,index)=>{
      if(!raw||typeof raw!=="object"||Array.isArray(raw)) throw new Error("Item "+(index+1)+" phải là object.");
      const item=raw as Record<string,unknown>, name=String(item.name??("Package "+(index+1))).slice(0,100);
      const price=rounded(numberValue(item,"price",0.0001,1e15),digits);
      const qty=numberValue(item,"quantity",0.000001,1e9);
      const unit=String(item.unit??"").trim().toLowerCase(), info=UNIT_MAP[unit];
      if(!info) throw new Error("Đơn vị phải là g, kg, mg, mL, L, cm, m hoặc each.");
      if(dimension && info.dimension!==dimension) throw new Error("Chỉ so sánh các sản phẩm cùng nhóm đơn vị.");
      dimension=info.dimension; base=info.base;
      return {name,price,qty,unit,unitPrice:price/(qty*info.factor)};
    }).sort((a,b)=>a.unitPrice-b.unitPrice);
    return ["Unit price comparator","Currency: "+currency,"Dimension: "+dimension+" (normalized to "+base+")",
      ...rows.map((row,index)=>(index+1)+". "+row.name+": "+formatMoney(row.price,currency)+" / "+fmt(row.qty)+" "+row.unit+
        "; "+formatMoney(row.unitPrice,currency)+" per "+base),
      "Best unit price: "+rows[0]!.name].join("\n");
  }
  throw new Error("Unknown everyday calculator.");
}
