export const DAILY_LIFE_TOOL_IDS = new Set([
  "water-bill-calculator", "mobile-data-duration-calculator", "solar-panel-output-calculator",
  "wallpaper-roll-calculator", "curtain-fabric-calculator", "moving-box-calculator",
  "event-food-calculator", "fuel-economy-calculator", "gas-cylinder-runtime-calculator",
  "shipping-volumetric-weight-calculator", "storage-capacity-calculator",
]);

type Input = Record<string, unknown>;

function parseInput(content: string): Input {
  let value: unknown;
  try { value = JSON.parse(content); }
  catch { throw new Error("Gửi dữ liệu JSON hợp lệ cho tiện ích này."); }
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Dữ liệu tiện ích phải là một JSON object.");
  return value as Input;
}

function num(input: Input, key: string, min: number, max: number, fallback?: number): number {
  const value = input[key] === undefined ? fallback : input[key];
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) {
    throw new Error(key + " phải là số từ " + min + " đến " + max + ".");
  }
  return value;
}

function integer(input: Input, key: string, min: number, max: number, fallback?: number): number {
  const value = num(input, key, min, max, fallback);
  if (!Number.isInteger(value)) throw new Error(key + " phải là số nguyên.");
  return value;
}

function currency(input: Input): string {
  const code = String(input.currency ?? "VND").trim().toUpperCase();
  if (!/^[A-Z]{3}$/.test(code)) throw new Error("currency phải là mã ba chữ cái, ví dụ VND, USD hoặc EUR.");
  return code;
}

function digits(code: string): number {
  if (["BIF","CLP","DJF","GNF","ISK","JPY","KMF","KRW","PYG","RWF","UGX","UYI","VND","VUV","XAF","XOF","XPF"].includes(code)) return 0;
  if (["BHD","IQD","JOD","KWD","LYD","OMR","TND"].includes(code)) return 3;
  return 2;
}

function round(value: number, places = 2): number {
  const scale = 10 ** places;
  return Math.round((value + Number.EPSILON) * scale) / scale;
}

function fmt(value: number, places = 3): string {
  return Number(value.toFixed(places)).toString();
}

function money(value: number, code: string): string {
  const places = digits(code);
  return code + " " + round(value, places).toFixed(places);
}

export function runDailyLifeTextTool(toolId: string, content: string): string {
  if (!DAILY_LIFE_TOOL_IDS.has(toolId)) throw new Error("Daily life calculator is not enabled for this ID.");
  const input = parseInput(content);

  if (toolId === "water-bill-calculator") {
    const code = currency(input), places = digits(code);
    const previous = num(input,"previous_reading_m3",0,1e9), current = num(input,"current_reading_m3",0,1e9);
    if(current<previous) throw new Error("current_reading_m3 cannot be lower than previous_reading_m3.");
    const rate = round(num(input,"price_per_m3",0,1e9),places), fixed = round(num(input,"fixed_charge",0,1e12,0),places);
    const sewage = num(input,"sewage_percent",0,100,0), used=current-previous;
    const water=used*rate, sewageCost=round(water*sewage/100,places), total=round(water+sewageCost+fixed,places);
    return ["Water bill estimate","Previous meter reading: "+fmt(previous)+" m³","Current meter reading: "+fmt(current)+" m³",
      "Water used: "+fmt(used,3)+" m³","User-entered price: "+money(rate,code)+" per m³",
      "Water charge: "+money(water,code),"Sewage allowance: "+fmt(sewage)+"% ("+money(sewageCost,code)+")",
      "Fixed charge: "+money(fixed,code),"Estimated bill: "+money(total,code),
      "Estimate uses one user-entered unit price; actual tariffs may be tiered."].join("\n");
  }

  if (toolId === "mobile-data-duration-calculator") {
    const allowance=num(input,"allowance_gb",0.001,1e6), used=num(input,"used_gb",0,1e6,0);
    if(used>allowance) throw new Error("used_gb cannot exceed allowance_gb.");
    const daily=num(input,"daily_usage_gb",0.000001,10000), reserve=num(input,"reserve_percent",0,90,0);
    const available=(allowance-used)*(1-reserve/100), duration=available/daily;
    const lines=["Mobile data allowance estimate","Plan allowance: "+fmt(allowance)+" GB","Already used: "+fmt(used)+" GB",
      "Data remaining before reserve: "+fmt(allowance-used)+" GB","Reserve: "+fmt(reserve)+"%",
      "Usable data: "+fmt(available)+" GB","Average daily usage: "+fmt(daily)+" GB/day",
      "Estimated duration at this usage: "+fmt(duration,1)+" days"];
    if(input.days_until_reset!==undefined){
      const days=num(input,"days_until_reset",0.01,366), limit=available/days;
      lines.push("Days until plan reset: "+fmt(days),"Suggested average daily limit to last until reset: "+fmt(limit)+" GB/day",
        "Current usage is "+(daily>limit?"above":"within")+" that average daily limit.");
    }
    lines.push("Estimate assumes daily usage stays constant; video quality, background updates and tethering can change consumption.");
    return lines.join("\n");
  }

  if (toolId === "solar-panel-output-calculator") {
    const code=currency(input), places=digits(code);
    const watts=num(input,"panel_watts",1,5000), count=integer(input,"panel_count",1,100000);
    const sun=num(input,"peak_sun_hours_per_day",0,24), loss=num(input,"system_loss_percent",0,90,20);
    const days=integer(input,"days",1,366,30), kw=watts*count/1000, daily=kw*sun*(1-loss/100), total=daily*days;
    const lines=["Solar panel output estimate","Panel rating: "+fmt(watts)+" W × "+count,"System size: "+fmt(kw)+" kW",
      "Peak sun hours assumption: "+fmt(sun)+" h/day","System loss allowance: "+fmt(loss)+"%",
      "Estimated daily energy: "+fmt(daily,2)+" kWh","Estimated energy over "+days+" days: "+fmt(total,1)+" kWh"];
    if(input.price_per_kwh!==undefined) lines.push("Illustrative value at user-entered rate: "+money(round(total*num(input,"price_per_kwh",0,1e9),places),code));
    lines.push("Estimate only: weather, shading, orientation, temperature and inverter limits affect real output.");
    return lines.join("\n");
  }

  if (toolId === "wallpaper-roll-calculator") {
    const perimeter=num(input,"room_perimeter_m",0.1,10000), height=num(input,"wall_height_m",0.1,100);
    const width=num(input,"roll_width_m",0.1,5), length=num(input,"roll_length_m",0.1,100);
    const repeat=num(input,"pattern_repeat_cm",0,500,0), extra=integer(input,"extra_rolls",0,20,1);
    const strips=Math.ceil(perimeter/width);
    const drop=repeat>0?Math.ceil(height/(repeat/100))*(repeat/100):height;
    const drops=Math.floor(length/drop);
    if(drops<=0) throw new Error("A wallpaper roll is shorter than one required wall drop.");
    const base=Math.ceil(strips/drops), total=base+extra;
    return ["Wallpaper roll estimate","Room perimeter: "+fmt(perimeter)+" m","Wall height: "+fmt(height)+" m",
      "Roll size: "+fmt(width)+" m × "+fmt(length)+" m","Pattern repeat: "+fmt(repeat)+" cm",
      "Adjusted drop length: "+fmt(drop,3)+" m","Vertical strips required: "+strips,
      "Usable drops per roll: "+drops,"Base rolls required: "+base,"Extra rolls allowance: "+extra,
      "Suggested rolls to buy: "+total,"Estimate assumes full room perimeter is wallpapered."].join("\n");
  }

  if (toolId === "curtain-fabric-calculator") {
    const windowWidth=num(input,"window_width_cm",1,10000), windowHeight=num(input,"window_height_cm",1,10000);
    const fabricWidth=num(input,"fabric_width_cm",1,1000), fullness=num(input,"fullness_ratio",1,5,2);
    const side=num(input,"side_allowance_cm",0,1000,30), top=num(input,"top_hem_cm",0,100,10);
    const bottom=num(input,"bottom_hem_cm",0,200,20), repeat=num(input,"pattern_repeat_cm",0,500,0);
    const totalWidth=windowWidth*fullness+side, panels=Math.ceil(totalWidth/fabricWidth);
    let drop=windowHeight+top+bottom;
    if(repeat>0) drop=Math.ceil(drop/repeat)*repeat;
    const metres=panels*drop/100;
    return ["Curtain fabric estimate","Window width × height: "+fmt(windowWidth)+" cm × "+fmt(windowHeight)+" cm",
      "Fullness ratio: "+fmt(fullness)+"×","Total fabric width allowance: "+fmt(totalWidth)+" cm",
      "Fabric width: "+fmt(fabricWidth)+" cm","Panels/cuts required: "+panels,
      "Cut/drop length per panel: "+fmt(drop,1)+" cm","Total fabric length: "+fmt(metres,2)+" metres",
      "Estimate excludes lining, pattern matching and special header construction."].join("\n");
  }

  if (toolId === "moving-box-calculator") {
    const volume=num(input,"items_volume_m3",0.001,100000), boxL=num(input,"box_volume_l",1,1000);
    const fill=num(input,"usable_fill_percent",1,100,75), extra=num(input,"extra_boxes_percent",0,100,10);
    const effective=boxL/1000*fill/100, base=Math.ceil(volume/effective), boxes=Math.ceil(base*(1+extra/100));
    return ["Moving box estimator","Estimated items volume: "+fmt(volume,3)+" m³","Box nominal volume: "+fmt(boxL)+" litres",
      "Usable fill per box: "+fmt(effective*1000,1)+" litres ("+fmt(fill)+"%)","Base boxes: "+base,
      "Extra allowance: "+fmt(extra)+"%","Suggested boxes: "+boxes,
      "Estimate is volume-based; fragile and awkward items, weight limits and wardrobe boxes may change the quantity."].join("\n");
  }

  if (toolId === "event-food-calculator") {
    const guests=integer(input,"guests",1,100000), food=num(input,"food_grams_per_person",0,5000);
    const drink=num(input,"drink_ml_per_person",0,10000), snacks=num(input,"snack_grams_per_person",0,5000,0);
    const buffer=num(input,"extra_percent",0,100,10), factor=1+buffer/100;
    return ["Event food and drink estimate","Guests: "+guests,"Extra allowance: "+fmt(buffer)+"%",
      "Main food: "+fmt(guests*food*factor/1000,2)+" kg","Drinks: "+fmt(guests*drink*factor/1000,2)+" litres",
      "Snacks: "+fmt(guests*snacks*factor/1000,2)+" kg",
      "Portion sizes depend on event type, duration, menu and guest preferences."].join("\n");
  }

  if (toolId === "fuel-economy-calculator") {
    const code=currency(input), places=digits(code);
    const distance=num(input,"distance_km",0.01,1e8), litres=num(input,"fuel_litres",0.001,1e7);
    const price=round(num(input,"price_per_litre",0,1e9,0),places), consumption=litres/distance*100;
    const cost=round(litres*price,places);
    return ["Fuel economy calculator","Distance travelled: "+fmt(distance,2)+" km","Fuel used: "+fmt(litres,3)+" litres",
      "Average consumption: "+fmt(consumption,2)+" L/100 km","Equivalent economy: "+fmt(distance/litres,2)+" km/L",
      "Fuel price input: "+money(price,code)+" per litre","Estimated fuel cost: "+money(cost,code),
      "Fuel cost per kilometre: "+money(cost/distance,code),"Fuel-only estimate; excludes tolls, parking and maintenance."].join("\n");
  }

  if (toolId === "gas-cylinder-runtime-calculator") {
    const weight=num(input,"gas_weight_kg",0.01,10000), consumption=num(input,"consumption_grams_per_hour",0.01,1e6);
    const reserve=num(input,"reserve_percent",0,90,10), usable=weight*1000*(1-reserve/100), hours=usable/consumption;
    const lines=["Gas cylinder runtime estimate","Cylinder gas weight: "+fmt(weight)+" kg","Reserve allowance: "+fmt(reserve)+"%",
      "Usable gas estimate: "+fmt(usable,1)+" g","Appliance consumption: "+fmt(consumption)+" g/hour",
      "Estimated runtime: "+fmt(hours,1)+" hours"];
    if(input.hours_per_day!==undefined){
      const daily=num(input,"hours_per_day",0.01,24);
      lines.push("At "+fmt(daily)+" hours/day: about "+fmt(hours/daily,1)+" days");
    }
    lines.push("Estimate assumes constant burner consumption; flame setting and residual gas affect real runtime.");
    return lines.join("\n");
  }

  if (toolId === "shipping-volumetric-weight-calculator") {
    const length=num(input,"length_cm",0.1,100000), width=num(input,"width_cm",0.1,100000);
    const height=num(input,"height_cm",0.1,100000), actual=num(input,"actual_weight_kg",0,1e6);
    const divisor=num(input,"volumetric_divisor",1,1e6), volume=length*width*height;
    const volumetric=volume/divisor, billable=Math.max(actual,volumetric);
    const lines=["Shipping volumetric weight estimate","Parcel size: "+fmt(length)+" × "+fmt(width)+" × "+fmt(height)+" cm",
      "Parcel volume: "+fmt(volume,1)+" cm³","Actual weight: "+fmt(actual,3)+" kg",
      "Volumetric divisor: "+fmt(divisor)+" cm³/kg","Volumetric weight: "+fmt(volumetric,3)+" kg",
      "Estimated billable weight: "+fmt(billable,3)+" kg"];
    if(input.price_per_kg!==undefined){
      const code=currency(input), places=digits(code), rate=round(num(input,"price_per_kg",0,1e9),places);
      lines.push("Illustrative shipping charge at entered rate: "+money(billable*rate,code));
    }
    lines.push("Carrier rules differ; confirm divisor, rounding and minimum charges with the carrier.");
    return lines.join("\n");
  }

  if (toolId === "storage-capacity-calculator") {
    const capacity=num(input,"capacity_gb",0.001,1e7), reserve=num(input,"reserve_percent",0,99,10);
    const usable=capacity*1000*(1-reserve/100), photo=num(input,"photo_size_mb",0.001,1e6,4);
    const video=num(input,"video_size_mb_per_minute",0.001,1e6,150), doc=num(input,"document_size_mb",0.001,1e6,1);
    return ["Storage capacity estimate","Nominal capacity: "+fmt(capacity)+" GB","Reserved space: "+fmt(reserve)+"%",
      "Usable estimate: "+fmt(usable/1000,2)+" GB","At "+fmt(photo)+" MB/photo: about "+Math.floor(usable/photo).toLocaleString("en-US")+" photos",
      "At "+fmt(video)+" MB/minute: about "+fmt(usable/video,1)+" minutes of video",
      "At "+fmt(doc)+" MB/document: about "+Math.floor(usable/doc).toLocaleString("en-US")+" documents",
      "Illustrative estimates; actual usable capacity is lower due to formatting, operating system, apps and varying file sizes."].join("\n");
  }

  throw new Error("Unknown daily life calculator.");
}
