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
async function getJson<T>(url: URL, provider: string, extraHeaders: Record<string, string> = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET", headers: { accept: "application/json", ...extraHeaders },
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
  if ([51,53,55].includes(value)) return "Drizzle";
  if ([56,57].includes(value)) return "Freezing drizzle";
  if ([61,63,65].includes(value)) return "Rain";
  if ([66,67].includes(value)) return "Freezing rain";
  if ([71,73,75,77].includes(value)) return "Snow";
  if ([85,86].includes(value)) return "Snow showers";
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


function distanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const rad = (value: number) => value * Math.PI / 180;
  const dLat = rad(lat2 - lat1), dLon = rad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.min(1, Math.sqrt(a)));
}

async function marineForecast(args: Obj): Promise<string> {
  const resolved = await locate(args);
  if (resolved.choices) return ambiguity(resolved.choices);
  const place = resolved.place!;
  const days = integer(args.forecast_days, "forecast_days", 3, 1, 7);
  const url = new URL("https://marine-api.open-meteo.com/v1/marine");
  url.searchParams.set("latitude", String(place.latitude));
  url.searchParams.set("longitude", String(place.longitude));
  url.searchParams.set("current", "wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,swell_wave_period,sea_surface_temperature,ocean_current_velocity,ocean_current_direction");
  url.searchParams.set("daily", "wave_height_max,wave_direction_dominant,wave_period_max,swell_wave_height_max,swell_wave_direction_dominant,swell_wave_period_max");
  url.searchParams.set("forecast_days", String(days));
  url.searchParams.set("timezone", "auto");
  url.searchParams.set("cell_selection", "sea");
  const data = obj(await getJson<unknown>(url, "Open-Meteo marine forecast"), "Marine forecast");
  const current = obj(data.current, "Marine current conditions");
  const daily = obj(data.daily, "Daily marine conditions");
  const dates = Array.isArray(daily.time) ? daily.time.slice(0, days) : [];
  const at = (key: string, i: number): unknown => Array.isArray(daily[key]) ? (daily[key] as unknown[])[i] : null;
  const forecast = dates.map((date, i) => ({
    date,
    maximum_wave_height_m: maybeNumber(at("wave_height_max", i)),
    dominant_wave_direction_deg_from_north: maybeNumber(at("wave_direction_dominant", i)),
    maximum_wave_period_seconds: maybeNumber(at("wave_period_max", i)),
    maximum_swell_height_m: maybeNumber(at("swell_wave_height_max", i)),
    dominant_swell_direction_deg_from_north: maybeNumber(at("swell_wave_direction_dominant", i)),
    maximum_swell_period_seconds: maybeNumber(at("swell_wave_period_max", i)),
  }));
  const modelLatitude = maybeNumber(data.latitude);
  const modelLongitude = maybeNumber(data.longitude);
  const modelDistance = modelLatitude !== null && modelLongitude !== null
    ? distanceKm(place.latitude, place.longitude, modelLatitude, modelLongitude) : null;
  return JSON.stringify({
    status: "ok",
    source: "Open-Meteo Marine API",
    source_url: "https://open-meteo.com/en/docs/marine-weather-api",
    attribution: OPEN_METEO_NOTE,
    requested_location: place,
    marine_model_grid: {
      latitude: modelLatitude,
      longitude: modelLongitude,
      distance_from_requested_location_km: modelDistance === null ? null : Math.round(modelDistance * 10) / 10,
      cell_selection: "nearest sea cell",
    },
    timezone: typeof data.timezone === "string" ? data.timezone : place.timezone,
    current: {
      time: current.time ?? null,
      wave_height_m: maybeNumber(current.wave_height),
      wave_direction_deg_from_north: maybeNumber(current.wave_direction),
      wave_period_seconds: maybeNumber(current.wave_period),
      swell_height_m: maybeNumber(current.swell_wave_height),
      swell_direction_deg_from_north: maybeNumber(current.swell_wave_direction),
      swell_period_seconds: maybeNumber(current.swell_wave_period),
      sea_surface_temperature_c: maybeNumber(current.sea_surface_temperature),
      ocean_current_speed_km_per_hour: maybeNumber(current.ocean_current_velocity),
      ocean_current_direction_deg: maybeNumber(current.ocean_current_direction),
      units: data.current_units ?? {},
    },
    daily_forecast: forecast,
    note: "Marine model estimates, not a navigation, swimming, rescue or severe-weather warning service. Check local maritime authorities and beach flags. The nearest sea grid may be far from the requested city; treat the forecast cautiously when the reported grid distance is large.",
    location_warning: modelDistance !== null && modelDistance > 80
      ? "The nearest sea grid is more than 80 km from the requested location; it may not represent nearby coastal conditions."
      : null,
  });
}

async function earthquakeActivity(args: Obj): Promise<string> {
  const resolved = await locate(args);
  if (resolved.choices) return ambiguity(resolved.choices);
  const place = resolved.place!;
  const days = integer(args.days_back, "days_back", 7, 1, 30);
  const radius = numeric(args.radius_km, "radius_km", 250, 10, 1000);
  const magnitude = numeric(args.minimum_magnitude, "minimum_magnitude", 2.5, 0, 9.9);
  const end = new Date();
  const start = new Date(end.getTime() - days * 86_400_000);
  const url = new URL("https://earthquake.usgs.gov/fdsnws/event/1/query");
  url.searchParams.set("format", "geojson");
  url.searchParams.set("starttime", start.toISOString());
  url.searchParams.set("endtime", end.toISOString());
  url.searchParams.set("latitude", String(place.latitude));
  url.searchParams.set("longitude", String(place.longitude));
  url.searchParams.set("maxradiuskm", String(radius));
  url.searchParams.set("minmagnitude", String(magnitude));
  url.searchParams.set("orderby", "time");
  url.searchParams.set("limit", "30");
  const data = obj(await getJson<unknown>(url, "USGS earthquake catalog"), "Earthquake catalog");
  const features = Array.isArray(data.features) ? data.features : [];
  const events = features.slice(0, 30).flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const feature = raw as Obj;
    if (!feature.properties || typeof feature.properties !== "object" || Array.isArray(feature.properties)) return [];
    const properties = feature.properties as Obj;
    const coordinates = feature.geometry && typeof feature.geometry === "object" && !Array.isArray(feature.geometry)
      ? (feature.geometry as Obj).coordinates : null;
    const coordinateList = Array.isArray(coordinates) ? coordinates : [];
    const longitude = typeof coordinateList[0] === "number" ? coordinateList[0] : null;
    const latitude = typeof coordinateList[1] === "number" ? coordinateList[1] : null;
    const depthKm = typeof coordinateList[2] === "number" ? coordinateList[2] : null;
    const eventDate = typeof properties.time === "number" ? new Date(properties.time) : null;
    const timestamp = eventDate && Number.isFinite(eventDate.getTime()) ? eventDate.toISOString() : null;
    const eventUrl = typeof properties.url === "string" ? (() => {
      try {
        const candidate = new URL(properties.url as string);
        return candidate.protocol === "https:" && candidate.hostname === "earthquake.usgs.gov" ? candidate.toString() : null;
      } catch { return null; }
    })() : null;
    return [{
      id: typeof feature.id === "string" ? feature.id.slice(0, 80) : null,
      magnitude: maybeNumber(properties.mag),
      magnitude_type: typeof properties.magType === "string" ? properties.magType.slice(0, 12) : null,
      place: typeof properties.place === "string" ? properties.place.slice(0, 220) : "Location not reported",
      time_utc: timestamp,
      depth_km: depthKm,
      coordinates: longitude !== null && latitude !== null ? { latitude, longitude } : null,
      detail_url: eventUrl,
      tsunami_flag_reported_by_usgs: properties.tsunami === 1,
    }];
  });
  const metadata = data.metadata && typeof data.metadata === "object" && !Array.isArray(data.metadata) ? data.metadata as Obj : {};
  return JSON.stringify({
    status: "ok",
    source: "USGS Earthquake Catalog",
    source_url: "https://earthquake.usgs.gov/fdsnws/event/1/",
    query: {
      location: place, days_back: days, radius_km: radius, minimum_magnitude: magnitude,
      start_time_utc: start.toISOString(), end_time_utc: end.toISOString(),
    },
    event_count: events.length,
    catalog_count: maybeNumber(metadata.count),
    events,
    note: "This is a catalog of reported earthquake events, not an earthquake early-warning system. Event completeness and reporting delays vary by location and magnitude. Follow official local emergency information; absence of listed events does not prove an area is safe.",
  });
}

let lastOpenLibraryRequestAt = 0;
async function searchBooks(args: Obj): Promise<string> {
  const query = text(args, "query", 140);
  const limit = integer(args.limit, "limit", 5, 1, 10);
  const now = Date.now();
  if (now - lastOpenLibraryRequestAt < 1000) {
    throw new Error("Open Library search is limited to one request per second. Please retry shortly.");
  }
  lastOpenLibraryRequestAt = now;
  const url = new URL("https://openlibrary.org/search.json");
  url.searchParams.set("q", query);
  url.searchParams.set("limit", String(limit));
  url.searchParams.set("fields", "key,title,author_name,first_publish_year,edition_count,isbn,subject");
  const data = obj(await getJson<unknown>(url, "Open Library", {
    "user-agent": "NolaneSearch/1.0 (https://github.com/Nolane-x/Nolane-search)",
  }), "Open Library search");
  const docs = Array.isArray(data.docs) ? data.docs : [];
  const books = docs.slice(0, limit).flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const row = raw as Obj;
    if (typeof row.title !== "string" || !row.title.trim()) return [];
    const key = typeof row.key === "string" && /^\/works\/[A-Za-z0-9]+$/.test(row.key) ? row.key : null;
    return [{
      title: row.title.slice(0, 240),
      authors: Array.isArray(row.author_name) ? row.author_name.filter((x): x is string => typeof x === "string").slice(0, 4).map(x => x.slice(0, 100)) : [],
      first_publication_year: maybeNumber(row.first_publish_year),
      edition_count: maybeNumber(row.edition_count),
      isbn_examples: Array.isArray(row.isbn) ? row.isbn.filter((x): x is string => typeof x === "string").slice(0, 3) : [],
      subjects: Array.isArray(row.subject) ? row.subject.filter((x): x is string => typeof x === "string").slice(0, 4).map(x => x.slice(0, 80)) : [],
      open_library_url: key ? "https://openlibrary.org" + key : null,
    }];
  });
  return JSON.stringify({
    status: "ok", source: "Open Library", source_url: "https://openlibrary.org/developers/api",
    query, total_matching_records: maybeNumber(data.numFound), result_count: books.length, books,
    note: "Catalog metadata can be incomplete or duplicated. A catalog record does not confirm that an edition is currently available to borrow or buy. This tool makes human-initiated, low-volume searches only and does not harvest the catalog.",
  });
}

async function postalCodeLookup(args: Obj): Promise<string> {
  const country = countryCode(args.country_code);
  if (!country) throw new Error("country_code is required; use a two-letter ISO country code.");
  const code = text(args, "postal_code", 20);
  if (!/^[A-Za-z0-9][A-Za-z0-9 .-]{0,18}$/.test(code)) {
    throw new Error("postal_code may contain letters, numbers, spaces, periods or hyphens only.");
  }
  const url = new URL("https://api.zippopotam.us/" + country.toLowerCase() + "/" + encodeURIComponent(code));
  let payload: unknown;
  try {
    payload = await getJson<unknown>(url, "Zippopotam.us postal-code service");
  } catch (error) {
    if (error instanceof Error && error.message.includes("HTTP 404")) {
      return JSON.stringify({
        status: "not_found", country_code: country, postal_code: code,
        message: "No matching postal-code record was returned. The service does not cover every country or all postal-code details.",
      });
    }
    throw error;
  }
  const data = obj(payload, "Postal-code");
  const places = Array.isArray(data.places) ? data.places.slice(0, 10).flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const place = raw as Obj;
    return [{
      place_name: typeof place["place name"] === "string" ? place["place name"].slice(0, 120) : null,
      state_or_region: typeof place.state === "string" ? place.state.slice(0, 120) : null,
      state_abbreviation: typeof place["state abbreviation"] === "string" ? place["state abbreviation"].slice(0, 20) : null,
      latitude: typeof place.latitude === "string" && Number.isFinite(Number(place.latitude)) ? Number(place.latitude) : null,
      longitude: typeof place.longitude === "string" && Number.isFinite(Number(place.longitude)) ? Number(place.longitude) : null,
    }];
  }) : [];
  return JSON.stringify({
    status: "ok", source: "Zippopotam.us / GeoNames", source_url: "https://docs.zippopotam.us/",
    country: typeof data.country === "string" ? data.country.slice(0, 100) : null,
    country_code: typeof data["country abbreviation"] === "string" ? data["country abbreviation"].slice(0, 2) : country,
    postal_code: typeof data["post code"] === "string" ? data["post code"].slice(0, 30) : code,
    places,
    note: "Postal-code data is provided as-is from GeoNames and may be incomplete or approximate in some countries. It is not an official proof of deliverability or a replacement for a local postal authority.",
  });
}


let lastDictionaryRequestAt = 0;
let lastGutendexRequestAt = 0;
let lastAicRequestAt = 0;
let lastEonetRequestAt = 0;

function requireMinInterval(last: number, minimumMs: number, provider: string): number {
  const now = Date.now();
  if (now - last < minimumMs) {
    throw new Error(provider + " requests are limited to one request per second per warm Worker isolate. Please retry shortly.");
  }
  return now;
}

function boundedString(value: unknown, key: string, max: number): string | undefined {
  if (value === undefined || value === null || value === "") return undefined;
  if (typeof value !== "string") throw new Error(key + " must be text.");
  const clean = value.normalize("NFKC").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  if (clean.length < 2 || clean.length > max) throw new Error(key + " must contain 2 to " + max + " characters.");
  return clean;
}

function safeExternalHttpsUrl(value: unknown): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.username || url.password || !url.hostname.includes(".")) return null;
    return url.toString();
  } catch {
    return null;
  }
}

function trustedHttpsUrl(value: unknown, allowedHosts: string[]): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value.startsWith("//") ? "https:" + value : value);
    if (url.protocol !== "https:" || url.username || url.password || !allowedHosts.includes(url.hostname.toLowerCase())) return null;
    return url.toString();
  } catch {
    return null;
  }
}

async function defineEnglishWord(args: Obj): Promise<string> {
  const word = text(args, "word", 50);
  if (!/^[A-Za-z][A-Za-z'-]{0,49}$/.test(word)) {
    throw new Error("Enter one English word using letters, apostrophes or hyphens only.");
  }
  lastDictionaryRequestAt = requireMinInterval(lastDictionaryRequestAt, 1000, "Free Dictionary API");
  const normalized = word.toLowerCase();
  const url = new URL("https://api.dictionaryapi.dev/api/v2/entries/en/" + encodeURIComponent(normalized));
  let payload: unknown;
  try {
    payload = await getJson<unknown>(url, "Free Dictionary API");
  } catch (error) {
    if (error instanceof Error && error.message.includes("HTTP 404")) {
      return JSON.stringify({
        status: "not_found",
        word: normalized,
        message: "No English entry was returned for this spelling. Check the spelling or try a different word.",
        source: "Free Dictionary API",
        source_url: "https://dictionaryapi.dev/",
      });
    }
    throw error;
  }
  if (!Array.isArray(payload)) throw new Error("Free Dictionary API returned an unexpected dictionary record.");
  const entries = payload.slice(0, 3).flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const entry = raw as Obj;
    const phonetics = Array.isArray(entry.phonetics) ? entry.phonetics : [];
    const pronunciations = phonetics.slice(0, 5).flatMap((rawPhonetic) => {
      if (!rawPhonetic || typeof rawPhonetic !== "object" || Array.isArray(rawPhonetic)) return [];
      const phonetic = rawPhonetic as Obj;
      const audio = trustedHttpsUrl(phonetic.audio, ["ssl.gstatic.com", "api.dictionaryapi.dev"]);
      return [{
        ipa: typeof phonetic.text === "string" ? phonetic.text.slice(0, 80) : null,
        audio_url: audio,
      }];
    });
    const meanings = Array.isArray(entry.meanings) ? entry.meanings.slice(0, 6).flatMap((rawMeaning) => {
      if (!rawMeaning || typeof rawMeaning !== "object" || Array.isArray(rawMeaning)) return [];
      const meaning = rawMeaning as Obj;
      const definitions = Array.isArray(meaning.definitions) ? meaning.definitions.slice(0, 4).flatMap((rawDefinition) => {
        if (!rawDefinition || typeof rawDefinition !== "object" || Array.isArray(rawDefinition)) return [];
        const definition = rawDefinition as Obj;
        if (typeof definition.definition !== "string") return [];
        return [{
          definition: definition.definition.slice(0, 700),
          example: typeof definition.example === "string" ? definition.example.slice(0, 350) : null,
          synonyms: Array.isArray(definition.synonyms) ? definition.synonyms.filter((item): item is string => typeof item === "string").slice(0, 6) : [],
          antonyms: Array.isArray(definition.antonyms) ? definition.antonyms.filter((item): item is string => typeof item === "string").slice(0, 6) : [],
        }];
      }) : [];
      if (!definitions.length) return [];
      return [{
        part_of_speech: typeof meaning.partOfSpeech === "string" ? meaning.partOfSpeech.slice(0, 40) : null,
        definitions,
      }];
    }) : [];
    if (!meanings.length) return [];
    return [{
      word: typeof entry.word === "string" ? entry.word.slice(0, 80) : normalized,
      phonetic: typeof entry.phonetic === "string" ? entry.phonetic.slice(0, 100) : pronunciations.find(item => item.ipa)?.ipa ?? null,
      pronunciations,
      origin: typeof entry.origin === "string" ? entry.origin.slice(0, 500) : null,
      meanings,
    }];
  });
  if (!entries.length) return JSON.stringify({
    status: "not_found", word: normalized, source: "Free Dictionary API",
    message: "The provider returned no usable English definitions for this spelling.",
  });
  return JSON.stringify({
    status: "ok",
    source: "Free Dictionary API",
    source_url: "https://dictionaryapi.dev/",
    project_url: "https://github.com/meetDeveloper/freeDictionaryAPI",
    word: normalized,
    entries,
    note: "Definitions are supplied by a community-maintained English dictionary API and may be incomplete. Pronunciation audio is linked from the provider's returned audio host. Results are short, on-demand lookup excerpts, not a licensed dictionary export.",
  });
}

async function searchPublicDomainBooks(args: Obj): Promise<string> {
  const query = text(args, "query", 140);
  const languageRaw = args.language === undefined ? "en" : typeof args.language === "string" ? args.language.trim() : "";
  if (!/^[A-Za-z]{2}$/.test(languageRaw)) throw new Error("language must be a two-letter language code, such as en, fr, de or es.");
  const topic = boundedString(args.topic, "topic", 80);
  const limit = integer(args.limit, "limit", 8, 1, 10);
  lastGutendexRequestAt = requireMinInterval(lastGutendexRequestAt, 1000, "Gutendex");
  const url = new URL("https://gutendex.com/books/");
  url.searchParams.set("search", query);
  url.searchParams.set("languages", languageRaw.toLowerCase());
  url.searchParams.set("copyright", "false");
  if (topic) url.searchParams.set("topic", topic);
  url.searchParams.set("page", "1");
  const data = obj(await getJson<unknown>(url, "Gutendex public-domain book catalog", {
    "user-agent": "NolaneSearch/1.0 (https://github.com/Nolane-x/Nolane-search)",
  }), "Gutendex");
  const rawBooks = Array.isArray(data.results) ? data.results : [];
  const books = rawBooks.slice(0, 32).flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const book = raw as Obj;
    if (book.copyright !== false || typeof book.id !== "number" || !Number.isSafeInteger(book.id) || book.id < 1 ||
        typeof book.title !== "string") return [];
    const authors = Array.isArray(book.authors) ? book.authors.slice(0, 4).flatMap((rawPerson) => {
      if (!rawPerson || typeof rawPerson !== "object" || Array.isArray(rawPerson)) return [];
      const person = rawPerson as Obj;
      return [{
        name: typeof person.name === "string" ? person.name.slice(0, 120) : "Unknown author",
        birth_year: maybeNumber(person.birth_year),
        death_year: maybeNumber(person.death_year),
      }];
    }) : [];
    const subjects = Array.isArray(book.subjects) ? book.subjects.filter((item): item is string => typeof item === "string").slice(0, 6).map(item => item.slice(0, 120)) : [];
    const bookshelves = Array.isArray(book.bookshelves) ? book.bookshelves.filter((item): item is string => typeof item === "string").slice(0, 5).map(item => item.slice(0, 100)) : [];
    const languages = Array.isArray(book.languages) ? book.languages.filter((item): item is string => typeof item === "string").slice(0, 5) : [];
    return [{
      id: book.id,
      title: book.title.slice(0, 240),
      authors,
      languages,
      subjects,
      bookshelves,
      download_count: maybeNumber(book.download_count),
      available_formats: book.formats && typeof book.formats === "object" && !Array.isArray(book.formats)
        ? Object.keys(book.formats as Obj).filter(item => item.length <= 80).slice(0, 8)
        : [],
      catalog_url: "https://www.gutenberg.org/ebooks/" + book.id,
      copyright_status: "Gutendex marks this record as public domain in the United States.",
    }];
  }).slice(0, limit);
  return JSON.stringify({
    status: "ok",
    source: "Gutendex / Project Gutenberg catalog",
    source_url: "https://gutendex.com/",
    project_url: "https://github.com/garethbjohnson/gutendex",
    query,
    language: languageRaw.toLowerCase(),
    public_domain_filter: "copyright=false (U.S. public-domain status as represented by Gutendex)",
    total_matching_records: maybeNumber(data.count),
    result_count: books.length,
    books,
    note: "Project Gutenberg follows U.S. copyright law. A book marked public domain in the United States may still be copyrighted or restricted in Vietnam or another country. Check local law before downloading, redistributing or reusing a title. This tool searches catalog metadata only; it does not download books.",
  });
}

async function searchMuseumArtworks(args: Obj): Promise<string> {
  const query = text(args, "query", 140);
  const limit = integer(args.limit, "limit", 6, 1, 8);
  lastAicRequestAt = requireMinInterval(lastAicRequestAt, 1000, "Art Institute of Chicago API");
  const url = new URL("https://api.artic.edu/api/v1/artworks/search");
  url.searchParams.set("params", JSON.stringify({
    q: query,
    query: { term: { is_public_domain: true } },
    page: 1,
    limit,
    fields: [
      "id", "title", "artist_title", "date_display", "medium_display", "dimensions",
      "main_reference_number", "image_id", "is_public_domain", "copyright_notice",
      "web_url", "place_of_origin", "artwork_type_title",
    ],
  }));
  const data = obj(await getJson<unknown>(url, "Art Institute of Chicago API", {
    "AIC-User-Agent": "NolaneSearch/1.0 (https://github.com/Nolane-x/Nolane-search)",
  }), "Art Institute artwork search");
  const rawArtworks = Array.isArray(data.data) ? data.data : [];
  const artworks = rawArtworks.slice(0, limit).flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const artwork = raw as Obj;
    if (artwork.is_public_domain !== true || typeof artwork.id !== "number" ||
        typeof artwork.image_id !== "string" || !/^[a-f0-9-]{36}$/i.test(artwork.image_id) ||
        typeof artwork.title !== "string") return [];
    const museumUrl = trustedHttpsUrl(artwork.web_url, ["www.artic.edu"]);
    return [{
      id: artwork.id,
      title: artwork.title.slice(0, 240),
      artist: typeof artwork.artist_title === "string" ? artwork.artist_title.slice(0, 140) : null,
      date: typeof artwork.date_display === "string" ? artwork.date_display.slice(0, 100) : null,
      medium: typeof artwork.medium_display === "string" ? artwork.medium_display.slice(0, 220) : null,
      dimensions: typeof artwork.dimensions === "string" ? artwork.dimensions.slice(0, 180) : null,
      origin: typeof artwork.place_of_origin === "string" ? artwork.place_of_origin.slice(0, 100) : null,
      artwork_type: typeof artwork.artwork_type_title === "string" ? artwork.artwork_type_title.slice(0, 80) : null,
      reference_number: typeof artwork.main_reference_number === "string" ? artwork.main_reference_number.slice(0, 60) : null,
      is_public_domain: true,
      copyright_notice: typeof artwork.copyright_notice === "string" ? artwork.copyright_notice.slice(0, 240) : null,
      image_url: "https://www.artic.edu/iiif/2/" + artwork.image_id + "/full/843,/0/default.jpg",
      museum_page: museumUrl,
      image_license_note: "Returned only when the museum API marks the artwork as public domain. Check the item's notice and the museum's terms before reuse.",
    }];
  });
  const pagination = data.pagination && typeof data.pagination === "object" && !Array.isArray(data.pagination)
    ? data.pagination as Obj : {};
  return JSON.stringify({
    status: "ok",
    source: "Art Institute of Chicago",
    source_url: "https://api.artic.edu/docs/",
    repository_url: "https://github.com/art-institute-of-chicago/api-data",
    query,
    public_domain_only: true,
    total_matching_records: maybeNumber(pagination.total),
    result_count: artworks.length,
    artworks,
    note: "Small, on-demand search only. The API allows 60 anonymous requests per minute; this client self-throttles per warm Worker isolate and sends the requested AIC-User-Agent header. Artwork image links are returned only for records tagged public domain.",
  });
}

async function naturalEvents(args: Obj): Promise<string> {
  const category = boundedString(args.category, "category", 40);
  if (category && !/^[A-Za-z][A-Za-z0-9_-]{0,39}$/.test(category)) {
    throw new Error("category must be a NASA EONET category ID, such as wildfires, severeStorms or landslides.");
  }
  const rawStatus = args.status === undefined ? "open" : args.status;
  if (rawStatus !== "open" && rawStatus !== "closed" && rawStatus !== "all") {
    throw new Error("status must be open, closed or all.");
  }
  const days = integer(args.days_back, "days_back", 30, 1, 90);
  const limit = integer(args.limit, "limit", 10, 1, 30);
  lastEonetRequestAt = requireMinInterval(lastEonetRequestAt, 1000, "NASA EONET");
  const url = new URL("https://eonet.gsfc.nasa.gov/api/v3/events");
  url.searchParams.set("status", rawStatus);
  url.searchParams.set("days", String(days));
  url.searchParams.set("limit", String(limit));
  if (category) url.searchParams.set("category", category);
  const data = obj(await getJson<unknown>(url, "NASA Earth Observatory Natural Event Tracker"), "NASA EONET");
  const rawEvents = Array.isArray(data.events) ? data.events : [];
  const events = rawEvents.slice(0, limit).flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const event = raw as Obj;
    if (typeof event.title !== "string") return [];
    const apiLink = trustedHttpsUrl(event.link, ["eonet.gsfc.nasa.gov"]);
    const categories = Array.isArray(event.categories) ? event.categories.slice(0, 6).flatMap((rawCategory) => {
      if (!rawCategory || typeof rawCategory !== "object" || Array.isArray(rawCategory)) return [];
      const item = rawCategory as Obj;
      return [{
        id: typeof item.id === "string" ? item.id.slice(0, 60) : null,
        title: typeof item.title === "string" ? item.title.slice(0, 100) : null,
      }];
    }) : [];
    const sources = Array.isArray(event.sources) ? event.sources.slice(0, 5).flatMap((rawSource) => {
      if (!rawSource || typeof rawSource !== "object" || Array.isArray(rawSource)) return [];
      const item = rawSource as Obj;
      return [{
        title: typeof item.title === "string" ? item.title.slice(0, 100) : null,
        source_url: safeExternalHttpsUrl(item.source ?? item.url),
        api_url: trustedHttpsUrl(item.link, ["eonet.gsfc.nasa.gov"]),
      }];
    }) : [];
    const geometry = Array.isArray(event.geometry) ? event.geometry.slice(-3).flatMap((rawGeometry) => {
      if (!rawGeometry || typeof rawGeometry !== "object" || Array.isArray(rawGeometry)) return [];
      const item = rawGeometry as Obj;
      const coordinates = Array.isArray(item.coordinates) ? item.coordinates : [];
      const point = item.type === "Point" && coordinates.length >= 2 &&
        typeof coordinates[0] === "number" && typeof coordinates[1] === "number"
        ? { longitude: coordinates[0], latitude: coordinates[1] } : null;
      return [{
        date: typeof item.date === "string" ? item.date.slice(0, 40) : null,
        geometry_type: typeof item.type === "string" ? item.type.slice(0, 30) : null,
        point,
      }];
    }) : [];
    return [{
      id: typeof event.id === "string" ? event.id.slice(0, 100) : null,
      title: event.title.slice(0, 240),
      description: typeof event.description === "string" ? event.description.slice(0, 700) : null,
      status: event.closed ? "closed" : "open",
      closed_at: typeof event.closed === "string" ? event.closed.slice(0, 40) : null,
      categories,
      sources,
      recent_geometry: geometry,
      nasa_event_api_url: apiLink,
    }];
  });
  return JSON.stringify({
    status: "ok",
    source: "NASA Earth Observatory Natural Event Tracker (EONET) v3",
    source_url: "https://eonet.gsfc.nasa.gov/docs/v3",
    query: { category: category ?? null, status: rawStatus, days_back: days, limit },
    event_count: events.length,
    events,
    note: "EONET is a curated natural-event metadata feed, not an emergency alert, official warning, or exhaustive real-time sensor network. Event descriptions and locations can be approximate or delayed. Follow local meteorological, geological and emergency authorities for safety decisions.",
  });
}

async function localTime(args: Obj): Promise<string> {
  const resolved = await locate(args);
  if (resolved.choices) return ambiguity(resolved.choices);
  const place = resolved.place!;
  if (!place.timezone) throw new Error("The geocoding service did not provide a time zone for this location.");
  const now = new Date();
  let parts: Intl.DateTimeFormatPart[];
  try {
    parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: place.timezone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      weekday: "long",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hourCycle: "h23",
      timeZoneName: "longOffset",
    }).formatToParts(now);
  } catch {
    throw new Error("The returned time zone is not a valid IANA time-zone identifier.");
  }
  const values: Record<string, string> = {};
  for (const part of parts) if (part.type !== "literal") values[part.type] = part.value;
  return JSON.stringify({
    status: "ok",
    source: "Cloudflare Worker clock + Open-Meteo geocoding time-zone identifier",
    location: place,
    time_zone: place.timezone,
    local_date: values.year && values.month && values.day ? values.year + "-" + values.month + "-" + values.day : null,
    local_time: values.hour && values.minute && values.second ? values.hour + ":" + values.minute + ":" + values.second : null,
    weekday: values.weekday ?? null,
    utc_offset: values.timeZoneName ?? null,
    observed_at_utc: now.toISOString(),
    note: "Local time is calculated from the current server clock and the geocoder's IANA time zone. It is not a forecast or opening-hours check.",
  });
}

export async function runLiveEverydayTool(name: string, rawArgs: unknown): Promise<string> {
  const args = obj(rawArgs, "Tool arguments");
  if (name === "get_weather_forecast") return weather(args);
  if (name === "check_air_quality") return air(args);
  if (name === "convert_currency") return currency(args);
  if (name === "get_public_holidays") return holidayCalendar(args);
  if (name === "find_long_weekends") return longWeekends(args);
  if (name === "get_marine_forecast") return marineForecast(args);
  if (name === "get_earthquake_activity") return earthquakeActivity(args);
  if (name === "search_books") return searchBooks(args);
  if (name === "lookup_postal_code") return postalCodeLookup(args);
  if (name === "define_english_word") return defineEnglishWord(args);
  if (name === "search_public_domain_books") return searchPublicDomainBooks(args);
  if (name === "search_museum_artworks") return searchMuseumArtworks(args);
  if (name === "get_natural_events") return naturalEvents(args);
  if (name === "get_local_time") return localTime(args);
  throw new Error("Unknown live everyday information tool.");
}
