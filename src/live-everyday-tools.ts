import { readJsonResponse } from "./http";

type Obj = Record<string, unknown>;
const OPEN_METEO_NOTE = "Open-Meteo model data (CC BY 4.0). Its free API is for non-commercial use.";
const HOLIDAY_NOTE = "Nager.Date covers country-level and first-level subdivision holidays, not city, employer or school closure rules.";

function obj(value: unknown, label: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(label + " response has an unexpected format.");
  return value as Obj;
}
function text(args: Obj, key: string, max = 100): string {
  const value = args[key];
  if (typeof value !== "string") throw new Error(key + " is required.");
  const clean = value.normalize("NFKC").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  if (clean.length < 2 || clean.length > max) throw new Error(key + " must contain 2 to " + max + " characters.");
  return clean;
}
function countryCode(value: unknown): string | undefined {
  if (value === undefined || value === null || value === "") return undefined;
  if (typeof value !== "string" || !/^[A-Za-z]{2}$/.test(value.trim())) throw new Error("country_code must be a two-letter ISO country code.");
  return value.trim().toUpperCase();
}
function integer(value: unknown, key: string, fallback: number, min: number, max: number): number {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < min || value > max) throw new Error(key + " must be a whole number from " + min + " to " + max + ".");
  return value;
}
function numeric(value: unknown, key: string, fallback: number, min: number, max: number): number {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) throw new Error(key + " must be a number from " + min + " to " + max + ".");
  return value;
}
function maybeNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}
async function getJson<T>(url: URL, provider: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET", headers: { accept: "application/json" },
      redirect: "error", signal: AbortSignal.timeout(12_000),
    });
  } catch {
    throw new Error(provider + " could not be reached or the request timed out.");
  }
  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    throw new Error(provider + " returned HTTP " + response.status + ".");
  }
  return readJsonResponse<T>(response, 500_000);
}

interface Place {
  name: string; admin1: string | null; country: string; country_code: string;
  latitude: number; longitude: number; timezone: string | null;
}
async function locate(args: Obj): Promise<{ place?: Place; choices?: Place[] }> {
  const location = text(args, "location");
  const cc = countryCode(args.country_code);
  const url = new URL("https://geocoding-api.open-meteo.com/v1/search");
  url.searchParams.set("name", location);
  url.searchParams.set("count", "5");
  url.searchParams.set("language", "en");
  url.searchParams.set("format", "json");
  if (cc) url.searchParams.set("countryCode", cc);
  const data = obj(await getJson<unknown>(url, "Open-Meteo geocoding"), "Geocoding");
  const raw = Array.isArray(data.results) ? data.results : [];
  const places = raw.map((item): Place | null => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return null;
    const row = item as Obj;
    if (typeof row.name !== "string" || typeof row.country !== "string" || typeof row.country_code !== "string" ||
        typeof row.latitude !== "number" || !Number.isFinite(row.latitude) ||
        typeof row.longitude !== "number" || !Number.isFinite(row.longitude)) return null;
    return {
      name: row.name.slice(0, 100), admin1: typeof row.admin1 === "string" ? row.admin1.slice(0, 100) : null,
      country: row.country.slice(0, 100), country_code: row.country_code.slice(0, 2).toUpperCase(),
      latitude: row.latitude, longitude: row.longitude,
      timezone: typeof row.timezone === "string" ? row.timezone.slice(0, 80) : null,
    };
  }).filter((item): item is Place => item !== null);
  if (!places.length) throw new Error("No matching city was found. Try adding its country or a more specific name.");
  const exact = places.filter(p => p.name.toLocaleLowerCase() === location.toLocaleLowerCase());
  const pool = exact.length ? exact : places;
  if (!cc && new Set(pool.map(p => p.country_code)).size > 1) return { choices: pool.slice(0, 5) };
  return { place: pool[0]! };
}
function ambiguity(choices: Place[]): string {
  return JSON.stringify({
    status: "needs_clarification",
    message: "Several places share this name. Ask the user which country or region they mean; do not guess.",
    choices: choices.map(p => ({ name: p.name, admin1: p.admin1, country: p.country, country_code: p.country_code })),
  });
}
function wmo(value: unknown): string {
  if (typeof value !== "number") return "Unknown";
  if (value === 0) return "Clear sky";
  if (value === 1) return "Mainly clear";
  if (value === 2) return "Partly cloudy";
  if (value === 3) return "Overcast";
  if (value === 45 || value === 48) return "Fog";
  if ([51,53,55,56,57].includes(value)) return "Drizzle or freezing drizzle";
  if ([61,63,65,66,67].includes(value)) return "Rain or freezing rain";
  if ([71,73,75,77,85,86].includes(value)) return "Snow";
  if ([80,81,82].includes(value)) return "Rain showers";
  if ([95,96,99].includes(value)) return "Thunderstorm";
  return "Unknown weather code " + value;
}
function usAqi(value: unknown): string | null {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  if (value <= 50) return "Good";
  if (value <= 100) return "Moderate";
  if (value <= 150) return "Unhealthy for sensitive groups";
  if (value <= 200) return "Unhealthy";
  if (value <= 300) return "Very unhealthy";
  return "Hazardous";
}

async function weather(args: Obj): Promise<string> {
  const resolved = await locate(args);
  if (resolved.choices) return ambiguity(resolved.choices);
  const place = resolved.place!;
  const days = integer(args.forecast_days, "forecast_days", 3, 1, 7);
  const url = new URL("https://api.open-meteo.com/v1/forecast");
  url.searchParams.set("latitude", String(place.latitude));
  url.searchParams.set("longitude", String(place.longitude));
  url.searchParams.set("current", "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m");
  url.searchParams.set("daily", "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset,uv_index_max");
  url.searchParams.set("timezone", "auto");
  url.searchParams.set("forecast_days", String(days));
  const data = obj(await getJson<unknown>(url, "Open-Meteo forecast"), "Forecast");
  const current = obj(data.current, "Current weather");
  const daily = obj(data.daily, "Daily weather");
  const dates = Array.isArray(daily.time) ? daily.time : [];
  const at = (key: string, i: number): unknown => Array.isArray(daily[key]) ? (daily[key] as unknown[])[i] : null;
  const forecast = dates.slice(0, days).map((date, i) => {
    const code = at("weather_code", i);
    return {
      date, weather_code: code, condition: wmo(code),
      temperature_min_c: maybeNumber(at("temperature_2m_min", i)),
      temperature_max_c: maybeNumber(at("temperature_2m_max", i)),
      precipitation_probability_max_percent: maybeNumber(at("precipitation_probability_max", i)),
      uv_index_max: maybeNumber(at("uv_index_max", i)),
      sunrise: at("sunrise", i), sunset: at("sunset", i),
    };
  });
  return JSON.stringify({
    status: "ok", source: "Open-Meteo", source_url: "https://open-meteo.com/",
    attribution: OPEN_METEO_NOTE, location: place,
    timezone: typeof data.timezone === "string" ? data.timezone : place.timezone,
    current: {
      time: current.time ?? null, condition: wmo(current.weather_code), weather_code: current.weather_code ?? null,
      temperature_c: maybeNumber(current.temperature_2m), feels_like_c: maybeNumber(current.apparent_temperature),
      relative_humidity_percent: maybeNumber(current.relative_humidity_2m),
      precipitation_mm: maybeNumber(current.precipitation), wind_speed_km_per_hour: maybeNumber(current.wind_speed_10m),
      is_day: current.is_day === 1, units: data.current_units ?? {},
    },
    daily_forecast: forecast,
    note: "Forecast/model output, not a guarantee of local conditions. Times use the returned location timezone.",
  });
}
async function air(args: Obj): Promise<string> {
  const resolved = await locate(args);
  if (resolved.choices) return ambiguity(resolved.choices);
  const place = resolved.place!;
  const url = new URL("https://air-quality-api.open-meteo.com/v1/air-quality");
  url.searchParams.set("latitude", String(place.latitude));
  url.searchParams.set("longitude", String(place.longitude));
  url.searchParams.set("current", "us_aqi,european_aqi,pm2_5,pm10,ozone,nitrogen_dioxide,uv_index");
  url.searchParams.set("timezone", "auto");
  const data = obj(await getJson<unknown>(url, "Open-Meteo air quality"), "Air quality");
  const current = obj(data.current, "Current air quality");
  return JSON.stringify({
    status: "ok", source: "Open-Meteo Air Quality",
    source_url: "https://open-meteo.com/en/docs/air-quality-api", attribution: OPEN_METEO_NOTE,
    location: place, timezone: typeof data.timezone === "string" ? data.timezone : place.timezone,
    current: {
      time: current.time ?? null, us_aqi: maybeNumber(current.us_aqi), us_aqi_category: usAqi(current.us_aqi),
      european_aqi: maybeNumber(current.european_aqi), pm2_5_ug_m3: maybeNumber(current.pm2_5),
      pm10_ug_m3: maybeNumber(current.pm10), ozone_ug_m3: maybeNumber(current.ozone),
      nitrogen_dioxide_ug_m3: maybeNumber(current.nitrogen_dioxide), uv_index: maybeNumber(current.uv_index),
      units: data.current_units ?? {},
    },
    note: "Model-derived near-current estimates, not a reading from a ground monitoring station. Do not use as the sole basis for medical decisions.",
  });
}
async function currency(args: Obj): Promise<string> {
  const base = text(args, "base_currency", 3).toUpperCase();
  const quote = text(args, "quote_currency", 3).toUpperCase();
  if (!/^[A-Z]{3}$/.test(base) || !/^[A-Z]{3}$/.test(quote)) throw new Error("Currency codes must contain three letters, such as USD or VND.");
  const amount = numeric(args.amount, "amount", 1, 0, 1_000_000_000_000_000);
  const url = new URL("https://api.frankfurter.dev/v2/rate/" + base + "/" + quote);
  const data = obj(await getJson<unknown>(url, "Frankfurter exchange-rate service"), "Exchange rate");
  if (typeof data.rate !== "number" || !Number.isFinite(data.rate) || data.rate <= 0 ||
      typeof data.date !== "string" || typeof data.base !== "string" || typeof data.quote !== "string") {
    throw new Error("Frankfurter returned an incomplete rate for this currency pair.");
  }
  const converted = amount * data.rate;
  if (!Number.isFinite(converted)) throw new Error("Converted amount is outside the supported numeric range.");
  return JSON.stringify({
    status: "ok", source: "Frankfurter v2", source_url: "https://frankfurter.dev/",
    reference_date: data.date, base_currency: data.base, quote_currency: data.quote,
    amount, rate: data.rate, converted_amount: Number(converted.toPrecision(12)),
    note: "Daily reference rate from central-bank and official sources; not a live trading quote, cash-exchange rate or guaranteed transaction rate.",
  });
}

interface Holiday {
  date: string; name: string; national_holiday: boolean; subdivision_codes: string[]; holiday_types: string[];
}
function yearArg(value: unknown): number {
  return integer(value, "year", new Date().getUTCFullYear(), 1900, 2100);
}
function subdivision(value: unknown, country: string): string | undefined {
  if (value === undefined || value === null || value === "") return undefined;
  if (typeof value !== "string") throw new Error("subdivision_code must be an ISO 3166-2 code.");
  const code = value.trim().toUpperCase();
  if (!new RegExp("^" + country + "-[A-Z0-9]{1,6}$").test(code)) throw new Error("subdivision_code must start with " + country + "-, e.g. " + country + "-CA.");
  return code;
}
async function holidays(country: string, year: number, region?: string): Promise<Holiday[]> {
  const url = new URL("https://nagerholidays.com/api/v4/Holidays/" + country + "/" + year);
  const payload = await getJson<unknown>(url, "Nager.Date public-holiday service");
  if (!Array.isArray(payload)) throw new Error("Nager.Date returned an unexpected holiday list.");
  return payload.map((item): Holiday | null => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return null;
    const row = item as Obj;
    if (typeof row.date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(row.date) || typeof row.name !== "string") return null;
    const regions = Array.isArray(row.subdivisionCodes) ? row.subdivisionCodes.filter((x): x is string => typeof x === "string").slice(0,30) : [];
    const types = Array.isArray(row.holidayTypes) ? row.holidayTypes.filter((x): x is string => typeof x === "string").slice(0,10) : [];
    if (!types.includes("Public")) return null;
    const national = row.nationalHoliday === true;
    if (region && !national && !regions.includes(region)) return null;
    return { date: row.date, name: row.name.slice(0,160), national_holiday: national, subdivision_codes: regions, holiday_types: types };
  }).filter((item): item is Holiday => item !== null)
    .sort((a,b) => a.date.localeCompare(b.date) || a.name.localeCompare(b.name));
}
async function holidayCalendar(args: Obj): Promise<string> {
  const country = countryCode(args.country_code);
  if (!country) throw new Error("country_code is required; use a two-letter ISO country code.");
  const year = yearArg(args.year);
  const month = args.month === undefined ? null : integer(args.month, "month", 1, 1, 12);
  const region = subdivision(args.subdivision_code, country);
  const all = await holidays(country, year, region);
  const selected = month === null ? all : all.filter(h => Number(h.date.slice(5,7)) === month);
  return JSON.stringify({
    status: "ok", source: "Nager.Date API v4", source_url: "https://nagerholidays.com/",
    country_code: country, year, subdivision_code: region ?? null, count: selected.length,
    holidays: selected, note: HOLIDAY_NOTE,
  });
}
function addDay(day: string, offset: number): string {
  const p = day.split("-").map(Number);
  return new Date(Date.UTC(p[0]!, p[1]! - 1, p[2]! + offset)).toISOString().slice(0,10);
}
function weekday(day: string): number {
  return new Date(day + "T00:00:00Z").getUTCDay();
}
async function longWeekends(args: Obj): Promise<string> {
  const country = countryCode(args.country_code);
  if (!country) throw new Error("country_code is required; use a two-letter ISO country code.");
  const year = yearArg(args.year);
  const region = subdivision(args.subdivision_code, country);
  let days = [0,6];
  if (args.weekend_days !== undefined) {
    if (!Array.isArray(args.weekend_days) || args.weekend_days.length < 1 || args.weekend_days.length > 7 ||
        args.weekend_days.some(x => typeof x !== "number" || !Number.isInteger(x) || x < 0 || x > 6)) {
      throw new Error("weekend_days must be weekday numbers from 0 (Sunday) to 6 (Saturday).");
    }
    days = [...new Set(args.weekend_days as number[])].sort((a,b) => a-b);
  }
  const weekend = new Set(days);
  const all = await holidays(country, year, region);
  const names = new Map<string,string[]>();
  for (const h of all) names.set(h.date, [...(names.get(h.date) ?? []), h.name]);
  const found = new Map<string,{start_date:string;end_date:string;day_count:number;holidays:string[]}>();
  for (const h of all) {
    let start = h.date, end = h.date;
    for (let i=0;i<7;i++) { const prev=addDay(start,-1); if (weekend.has(weekday(prev)) || names.has(prev)) start=prev; else break; }
    for (let i=0;i<7;i++) { const next=addDay(end,1); if (weekend.has(weekday(next)) || names.has(next)) end=next; else break; }
    const count = Math.round((Date.parse(end+"T00:00:00Z")-Date.parse(start+"T00:00:00Z"))/86_400_000)+1;
    const includesWeekend = Array.from({length:count},(_,i)=>addDay(start,i)).some(day=>weekend.has(weekday(day)));
    if (count >= 3 && includesWeekend) {
      const key=start+"/"+end;
      const included=[...names.entries()].filter(([date])=>date>=start&&date<=end).flatMap(([,list])=>list);
      found.set(key,{start_date:start,end_date:end,day_count:count,holidays:[...new Set(included)].sort()});
    }
  }
  const candidates=[...found.values()].sort((a,b)=>a.start_date.localeCompare(b.start_date));
  return JSON.stringify({
    status:"ok",source:"Nager.Date API v4 plus Nolane calendar calculation",source_url:"https://nagerholidays.com/",
    country_code:country,year,subdivision_code:region??null,weekend_days:days,
    count:candidates.length,potential_long_weekends:candidates,
    note:"Candidate clusters contain at least one listed public holiday and configured weekend days. They do not confirm substitute days off, school closures or employer policy.",
  });
}

export async function runLiveEverydayTool(name: string, rawArgs: unknown): Promise<string> {
  const args = obj(rawArgs, "Tool arguments");
  if (name === "get_weather_forecast") return weather(args);
  if (name === "check_air_quality") return air(args);
  if (name === "convert_currency") return currency(args);
  if (name === "get_public_holidays") return holidayCalendar(args);
  if (name === "find_long_weekends") return longWeekends(args);
  throw new Error("Unknown live everyday information tool.");
}
