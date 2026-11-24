import { readJsonResponse } from "./http";

type Obj = Record<string, unknown>;

const WORLD_BANK_BASE = "https://api.worldbank.org/v2";
const GBIF_BASE = "https://api.gbif.org/v1";
const GBIF_USER_AGENT = "NolaneSearch/0.1 (https://github.com/Nolane-x/Nolane-search)";
const WORLD_BANK_NOTE = "World Bank World Development Indicators. Latest available non-empty annual observation is returned per country and indicator; years can differ between indicators. Missing values are not estimated or interpolated.";
const GBIF_NOTE = "GBIF aggregates records from many contributing datasets. Occurrence records are evidence of recorded observations, not proof that a species is currently present at a site. Coordinates and locality descriptions are deliberately omitted to avoid exposing sensitive species locations.";

const INDICATORS = {
  population_total: { code: "SP.POP.TOTL", label: "Population, total" },
  gdp_current_usd: { code: "NY.GDP.MKTP.CD", label: "GDP (current US$)" },
  gdp_per_capita_usd: { code: "NY.GDP.PCAP.CD", label: "GDP per capita (current US$)" },
  gdp_growth_annual_percent: { code: "NY.GDP.MKTP.KD.ZG", label: "GDP growth (annual %)" },
  life_expectancy_years: { code: "SP.DYN.LE00.IN", label: "Life expectancy at birth (years)" },
  internet_users_percent: { code: "IT.NET.USER.ZS", label: "Individuals using the Internet (% of population)" },
  unemployment_percent: { code: "SL.UEM.TOTL.ZS", label: "Unemployment (% of labor force, ILO estimate)" },
  inflation_annual_percent: { code: "FP.CPI.TOTL.ZG", label: "Inflation, consumer prices (annual %)" },
  co2_emissions_per_capita: { code: "EN.ATM.CO2E.PC", label: "CO2 emissions (metric tons per capita)" },
  urban_population_percent: { code: "SP.URB.TOTL.IN.ZS", label: "Urban population (% of total)" },
} as const;

type IndicatorKey = keyof typeof INDICATORS;

function object(value: unknown, label: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(label + " returned an unexpected response.");
  return value as Obj;
}
function cleanString(value: unknown, key: string, min = 2, max = 160): string {
  if (typeof value !== "string") throw new Error(key + " is required.");
  const result = value.normalize("NFKC").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  if (result.length < min || result.length > max) throw new Error(key + " must contain " + min + " to " + max + " characters.");
  return result;
}
function wholeNumber(value: unknown, key: string, fallback: number, min: number, max: number): number {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < min || value > max) {
    throw new Error(key + " must be a whole number from " + min + " to " + max + ".");
  }
  return value;
}
function numberOrNull(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}
async function getJson<T>(url: URL, provider: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: { accept: "application/json", "user-agent": GBIF_USER_AGENT },
      redirect: "error",
      signal: AbortSignal.timeout(12_000),
    });
  } catch {
    throw new Error(provider + " could not be reached or the request timed out.");
  }
  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    if (response.status === 429) throw new Error(provider + " is rate-limiting requests. Reduce query frequency and retry later.");
    throw new Error(provider + " returned HTTP " + response.status + ".");
  }
  return readJsonResponse<T>(response, 500_000);
}
function worldBankRows(payload: unknown, provider: string): Obj[] {
  if (!Array.isArray(payload)) throw new Error(provider + " returned an unexpected JSON envelope.");
  const rows = payload[1];
  if (rows === null || rows === undefined) return [];
  if (!Array.isArray(rows)) throw new Error(provider + " returned an unexpected record list.");
  return rows.filter((row): row is Obj => !!row && typeof row === "object" && !Array.isArray(row));
}
function normalizeCountry(row: Obj): Obj | null {
  const name = typeof row.name === "string" ? row.name : "";
  const iso2 = typeof row.iso2Code === "string" ? row.iso2Code.toUpperCase() : "";
  const iso3 = typeof row.id === "string" ? row.id.toUpperCase() : typeof row.iso3Code === "string" ? row.iso3Code.toUpperCase() : "";
  const region = row.region && typeof row.region === "object" ? row.region as Obj : {};
  const income = row.incomeLevel && typeof row.incomeLevel === "object" ? row.incomeLevel as Obj : {};
  const lending = row.lendingType && typeof row.lendingType === "object" ? row.lendingType as Obj : {};
  if (!name || !/^[A-Z]{2}$/.test(iso2) || !/^[A-Z]{3}$/.test(iso3) ||
      region.value === "Aggregates") return null;
  return {
    name: name.slice(0, 140),
    iso2_code: iso2,
    iso3_code: iso3,
    capital_city: typeof row.capitalCity === "string" && row.capitalCity ? row.capitalCity.slice(0, 120) : null,
    region: typeof region.value === "string" ? region.value : null,
    income_level: typeof income.value === "string" ? income.value : null,
    lending_type: typeof lending.value === "string" ? lending.value : null,
    latitude: numberOrNull(typeof row.latitude === "string" && row.latitude.trim() ? Number(row.latitude) : row.latitude),
    longitude: numberOrNull(typeof row.longitude === "string" && row.longitude.trim() ? Number(row.longitude) : row.longitude),
    world_bank_country_url: "https://api.worldbank.org/v2/country/" + iso3 + "?format=json",
  };
}
function fold(value: string): string {
  return value.normalize("NFKD").replace(/\p{M}/gu, "").toLocaleLowerCase().replace(/[^\p{L}\p{N}]/gu, "");
}
async function searchCountries(args: Obj): Promise<string> {
  const query = cleanString(args.query, "query", 2, 120);
  const regionFilter = args.region === undefined ? "" : cleanString(args.region, "region", 2, 80);
  const limit = wholeNumber(args.limit, "limit", 6, 1, 12);
  const url = new URL(WORLD_BANK_BASE + "/country");
  url.searchParams.set("format", "json");
  url.searchParams.set("per_page", "400");
  const payload = await getJson<unknown>(url, "World Bank country metadata");
  const countries = worldBankRows(payload, "World Bank country metadata")
    .map(normalizeCountry).filter((item): item is Obj => item !== null);
  const needle = fold(query);
  const regionNeedle = fold(regionFilter);
  const matches = countries.filter(country => {
    const region = typeof country.region === "string" ? country.region : "";
    if (regionNeedle && !fold(region).includes(regionNeedle)) return false;
    return [country.name, country.iso2_code, country.iso3_code, country.capital_city, country.region, country.income_level]
      .some(value => typeof value === "string" && fold(value).includes(needle));
  });
  const score = (country: Obj): number => {
    const name = fold(String(country.name));
    const iso2 = String(country.iso2_code).toLowerCase();
    const iso3 = String(country.iso3_code).toLowerCase();
    if (name === needle || iso2 === needle || iso3 === needle) return 0;
    if (name.startsWith(needle)) return 1;
    return 2;
  };
  matches.sort((a, b) => score(a) - score(b) || String(a.name).localeCompare(String(b.name)));
  const selected = matches.slice(0, limit);
  return JSON.stringify({
    status: selected.length ? "ok" : "not_found",
    source: "World Bank Country API",
    source_url: WORLD_BANK_BASE + "/country?format=json&per_page=400",
    query,
    region_filter: regionFilter || null,
    total_matches: matches.length,
    result_count: selected.length,
    countries: selected,
    note: "Country metadata includes ISO codes, capital city, region, World Bank income group and approximate capital coordinates. The World Bank's regions and income groups are its own classifications, not travel, visa or legal advice.",
  });
}

function indicatorKeys(value: unknown): IndicatorKey[] {
  const defaults: IndicatorKey[] = [
    "population_total", "gdp_per_capita_usd", "gdp_growth_annual_percent",
    "life_expectancy_years", "internet_users_percent",
  ];
  if (value === undefined || value === null) return defaults;
  if (!Array.isArray(value) || value.length < 1 || value.length > 8) {
    throw new Error("indicators must contain between 1 and 8 supported indicator keys.");
  }
  const seen = new Set<string>();
  const result: IndicatorKey[] = [];
  for (const item of value) {
    if (typeof item !== "string" || !Object.prototype.hasOwnProperty.call(INDICATORS, item)) throw new Error("Unsupported indicator key: " + String(item) + ".");
    if (!seen.has(item)) { seen.add(item); result.push(item as IndicatorKey); }
  }
  return result;
}
async function getCountryIndicators(args: Obj): Promise<string> {
  if (!Array.isArray(args.country_codes) || args.country_codes.length < 1 || args.country_codes.length > 5) {
    throw new Error("country_codes must be an array of 1 to 5 ISO alpha-2 or alpha-3 country codes.");
  }
  const countryCodes = [...new Set(args.country_codes.map((value) => {
    if (typeof value !== "string" || !/^[A-Za-z]{2,3}$/.test(value.trim())) {
      throw new Error("Each country code must be a two- or three-letter ISO code, such as VN or VNM.");
    }
    return value.trim().toUpperCase();
  }))];
  const keys = indicatorKeys(args.indicators);
  const apiCodes = keys.map(key => INDICATORS[key].code);
  const url = new URL(WORLD_BANK_BASE + "/country/" + countryCodes.join(";") + "/indicator/" + apiCodes.join(";"));
  url.searchParams.set("format", "json");
  url.searchParams.set("source", "2");
  url.searchParams.set("mrnev", "1");
  url.searchParams.set("per_page", "100");
  const payload = await getJson<unknown>(url, "World Bank indicator API");
  const rows = worldBankRows(payload, "World Bank indicator API");
  const countries = new Map<string, { name: string; iso3_code: string; indicators: Record<string, Obj> }>();
  for (const row of rows) {
    const country = row.country && typeof row.country === "object" ? row.country as Obj : {};
    const indicator = row.indicator && typeof row.indicator === "object" ? row.indicator as Obj : {};
    const iso3 = typeof row.countryiso3code === "string" && /^[A-Z]{3}$/i.test(row.countryiso3code)
      ? row.countryiso3code.toUpperCase() : typeof country.id === "string" ? country.id.toUpperCase() : "";
    if (!iso3) continue;
    if (!countries.has(iso3)) countries.set(iso3, {
      name: typeof country.value === "string" ? country.value.slice(0, 140) : iso3,
      iso3_code: iso3,
      indicators: {},
    });
    const code = typeof indicator.id === "string" ? indicator.id : "";
    const key = keys.find(candidate => INDICATORS[candidate].code === code);
    if (!key) continue;
    const value = numberOrNull(row.value);
    countries.get(iso3)!.indicators[key] = {
      label: INDICATORS[key].label,
      indicator_code: code,
      year: typeof row.date === "string" ? row.date : null,
      value,
      unit: typeof row.unit === "string" && row.unit ? row.unit.slice(0, 80) : null,
      observation_status: typeof row.obs_status === "string" && row.obs_status ? row.obs_status.slice(0, 100) : null,
      source_url: "https://data.worldbank.org/indicator/" + encodeURIComponent(code) + "?locations=" + encodeURIComponent(iso3),
    };
  }
  const results = [...countries.values()];
  return JSON.stringify({
    status: rows.length ? "ok" : "not_found",
    source: "World Bank World Development Indicators (source 2)",
    source_url: WORLD_BANK_BASE,
    requested_country_codes: countryCodes,
    countries: results,
    country_count: results.length,
    indicator_keys: keys,
    note: WORLD_BANK_NOTE,
  });
}

function allowedGbifLicense(value: unknown): { code: string; url: string } | null {
  if (typeof value !== "string") return null;
  const license = value.trim();
  const normalized = license.toUpperCase();
  if (normalized === "CC0_1_0" || /creativecommons\.org\/publicdomain\/zero\/1\.0\/?(?:legalcode)?$/i.test(license)) {
    return { code: "CC0_1_0", url: "https://creativecommons.org/publicdomain/zero/1.0/" };
  }
  if (normalized === "CC_BY_4_0" || /creativecommons\.org\/licenses\/by\/4\.0\/?(?:legalcode)?$/i.test(license)) {
    return { code: "CC_BY_4_0", url: "https://creativecommons.org/licenses/by/4.0/" };
  }
  return null;
}
async function searchGbifSpecies(args: Obj): Promise<string> {
  const name = cleanString(args.name, "name", 2, 160);
  const strict = args.strict === undefined ? false : args.strict;
  if (typeof strict !== "boolean") throw new Error("strict must be a boolean.");
  const url = new URL(GBIF_BASE + "/species/match");
  url.searchParams.set("name", name);
  url.searchParams.set("strict", String(strict));
  url.searchParams.set("verbose", "true");
  const row = object(await getJson<unknown>(url, "GBIF species API"), "GBIF species match");
  const usageKey = numberOrNull(row.acceptedUsageKey) ?? numberOrNull(row.usageKey);
  if (row.matchType === "NONE" || usageKey === null) {
    return JSON.stringify({
      status: "not_found", source: "GBIF Taxonomic Backbone",
      source_url: "https://www.gbif.org/tools/species-lookup",
      query: name, match_type: typeof row.matchType === "string" ? row.matchType : "NONE",
      confidence: numberOrNull(row.confidence),
      note: "No usable taxon key was returned. Try a scientific name or a more precise common name; a fuzzy match is not a confirmed identification.",
    });
  }
  const acceptedName = typeof row.canonicalName === "string" ? row.canonicalName : typeof row.scientificName === "string" ? row.scientificName : name;
  return JSON.stringify({
    status: "ok",
    source: "GBIF Taxonomic Backbone",
    source_url: "https://www.gbif.org/species/" + usageKey,
    query: name,
    taxon_key: usageKey,
    scientific_name: typeof row.scientificName === "string" ? row.scientificName : acceptedName,
    canonical_name: acceptedName,
    rank: typeof row.rank === "string" ? row.rank : null,
    taxonomic_status: typeof row.status === "string" ? row.status : null,
    match_type: typeof row.matchType === "string" ? row.matchType : null,
    confidence: numberOrNull(row.confidence),
    kingdom: typeof row.kingdom === "string" ? row.kingdom : null,
    phylum: typeof row.phylum === "string" ? row.phylum : null,
    class: typeof row.class === "string" ? row.class : null,
    order: typeof row.order === "string" ? row.order : null,
    family: typeof row.family === "string" ? row.family : null,
    genus: typeof row.genus === "string" ? row.genus : null,
    note: "GBIF backbone name matching is a taxonomy lookup, not image recognition or confirmation of a real-world specimen. Check the match type and confidence before using it as an identification.",
  });
}
async function searchGbifObservations(args: Obj): Promise<string> {
  const taxonKey = wholeNumber(args.taxon_key, "taxon_key", 1, 1, 2_147_483_647);
  let country: string | null = null;
  if (args.country_code !== undefined && args.country_code !== null && args.country_code !== "") {
    if (typeof args.country_code !== "string" || !/^[A-Za-z]{2}$/.test(args.country_code.trim())) {
      throw new Error("country_code must be a two-letter ISO country code.");
    }
    country = args.country_code.trim().toUpperCase();
  }
  const fromYear = args.year_from === undefined ? null : wholeNumber(args.year_from, "year_from", 2000, 1600, 2100);
  const toYear = args.year_to === undefined ? null : wholeNumber(args.year_to, "year_to", new Date().getUTCFullYear(), 1600, 2100);
  if (fromYear !== null && toYear !== null && fromYear > toYear) throw new Error("year_from cannot be later than year_to.");
  const limit = wholeNumber(args.limit, "limit", 5, 1, 10);
  const url = new URL(GBIF_BASE + "/occurrence/search");
  url.searchParams.set("taxonKey", String(taxonKey));
  url.searchParams.set("basisOfRecord", "HUMAN_OBSERVATION");
  url.searchParams.set("occurrenceStatus", "PRESENT");
  url.searchParams.set("limit", "100");
  url.searchParams.set("offset", "0");
  if (country) url.searchParams.set("country", country);
  if (fromYear !== null || toYear !== null) {
    url.searchParams.set("year", (fromYear ?? 1600) + "," + (toYear ?? new Date().getUTCFullYear()));
  }
  const payload = object(await getJson<unknown>(url, "GBIF occurrence API"), "GBIF occurrences");
  const raw = Array.isArray(payload.results) ? payload.results : [];
  const records = raw.flatMap((item): Obj[] => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const row = item as Obj;
    const license = allowedGbifLicense(row.license);
    const key = numberOrNull(row.key);
    if (!license || key === null) return [];
    const datasetKey = typeof row.datasetKey === "string" && /^[0-9a-f-]{36}$/i.test(row.datasetKey) ? row.datasetKey : null;
    const recordedBy = typeof row.recordedBy === "string" ? row.recordedBy.slice(0, 180) : null;
    return [{
      gbif_id: key,
      scientific_name: typeof row.scientificName === "string" ? row.scientificName.slice(0, 220) : null,
      vernacular_name: typeof row.vernacularName === "string" ? row.vernacularName.slice(0, 180) : null,
      event_date: typeof row.eventDate === "string" ? row.eventDate.slice(0, 40) : null,
      country: typeof row.country === "string" ? row.country.slice(0, 100) : null,
      country_code: typeof row.countryCode === "string" ? row.countryCode.slice(0, 2) : country,
      basis_of_record: typeof row.basisOfRecord === "string" ? row.basisOfRecord : "HUMAN_OBSERVATION",
      dataset_name: typeof row.datasetName === "string" ? row.datasetName.slice(0, 220) : null,
      dataset_key: datasetKey,
      dataset_url: datasetKey ? "https://www.gbif.org/dataset/" + datasetKey : null,
      recorded_by: recordedBy,
      attribution: [recordedBy, typeof row.datasetName === "string" ? row.datasetName : null].filter(Boolean).join("; ") || "See the contributing dataset",
      license: license.code,
      license_url: license.url,
      gbif_record_url: "https://www.gbif.org/occurrence/" + key,
    }];
  });
  const selected = records.slice(0, limit);
  return JSON.stringify({
    status: selected.length ? "ok" : "no_reusable_records",
    source: "GBIF Occurrence API",
    source_url: "https://www.gbif.org/occurrence/search",
    taxon_key: taxonKey,
    country_code: country,
    year_from: fromYear,
    year_to: toYear,
    matching_record_count: numberOrNull(payload.count),
    records_returned: selected.length,
    records: selected,
    note: GBIF_NOTE + " This tool only returns records explicitly marked CC0 1.0 or CC BY 4.0; other and unspecified licenses are excluded. For CC BY records, retain the included contributor/dataset attribution and license link. The search API can be rate-limited under server load; reduce query frequency after HTTP 429.",
  });
}

export async function runWorldDataTool(name: string, rawArgs: unknown): Promise<string> {
  if (!rawArgs || typeof rawArgs !== "object" || Array.isArray(rawArgs)) throw new Error("Tool arguments must be a JSON object.");
  const args = rawArgs as Obj;
  if (name === "search_country_profiles") return searchCountries(args);
  if (name === "get_world_bank_indicators") return getCountryIndicators(args);
  if (name === "search_gbif_species") return searchGbifSpecies(args);
  if (name === "search_gbif_observations") return searchGbifObservations(args);
  throw new Error("Unknown world data tool.");
}
