import { afterEach, describe, expect, it, vi } from "vitest";
import { runLiveEverydayTool } from "../src/live-everyday-tools";

afterEach(() => vi.unstubAllGlobals());
const place = {
  name: "Hai Phong", admin1: "Hai Phong", country: "Vietnam", country_code: "VN",
  latitude: 20.85, longitude: 106.68, timezone: "Asia/Ho_Chi_Minh",
};
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json" } });
}

describe("Live everyday information tools", () => {
  it("geocodes a place and returns a short weather forecast with attribution", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.hostname === "geocoding-api.open-meteo.com") {
        expect(url.searchParams.get("countryCode")).toBe("VN");
        return json({ results: [place] });
      }
      expect(url.hostname).toBe("api.open-meteo.com");
      expect(url.searchParams.get("forecast_days")).toBe("2");
      return json({
        timezone: "Asia/Ho_Chi_Minh",
        current: { time:"2026-11-24T12:00",temperature_2m:25,relative_humidity_2m:70,apparent_temperature:27,is_day:1,precipitation:0.2,weather_code:61,wind_speed_10m:12 },
        current_units: { temperature_2m:"°C" },
        daily: { time:["2026-11-24","2026-11-25"],weather_code:[61,3],temperature_2m_max:[27,28],temperature_2m_min:[22,23],precipitation_probability_max:[80,10],sunrise:["05:55","05:55"],sunset:["17:15","17:15"],uv_index_max:[6,7] },
      });
    });
    vi.stubGlobal("fetch", fetchMock);
    const result = JSON.parse(await runLiveEverydayTool("get_weather_forecast",{location:"Hai Phong",country_code:"VN",forecast_days:2}));
    expect(result.current.condition).toBe("Rain");
    expect(result.daily_forecast).toHaveLength(2);
    expect(result.attribution).toContain("CC BY 4.0");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("does not guess between same-named cities in different countries", async () => {
    const fetchMock = vi.fn(async () => json({results:[
      {...place,name:"Springfield",country:"United States",country_code:"US"},
      {...place,name:"Springfield",country:"Australia",country_code:"AU"},
    ]}));
    vi.stubGlobal("fetch",fetchMock);
    const result=JSON.parse(await runLiveEverydayTool("check_air_quality",{location:"Springfield"}));
    expect(result.status).toBe("needs_clarification");
    expect(result.choices).toHaveLength(2);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("returns modeled air-quality metrics and labels the US AQI", async () => {
    const fetchMock=vi.fn(async(input:RequestInfo|URL)=>{
      const url=new URL(String(input));
      if(url.hostname==="geocoding-api.open-meteo.com")return json({results:[place]});
      expect(url.hostname).toBe("air-quality-api.open-meteo.com");
      return json({timezone:"Asia/Ho_Chi_Minh",current:{time:"2026-11-24T12:00",us_aqi:123,european_aqi:42,pm2_5:45.2,pm10:61,ozone:30,nitrogen_dioxide:8,uv_index:4}});
    });
    vi.stubGlobal("fetch",fetchMock);
    const result=JSON.parse(await runLiveEverydayTool("check_air_quality",{location:"Hai Phong",country_code:"VN"}));
    expect(result.current.us_aqi_category).toBe("Unhealthy for sensitive groups");
    expect(result.current.pm2_5_ug_m3).toBe(45.2);
    expect(result.note).toContain("ground monitoring station");
  });

  it("converts an amount using the exact reference date returned by Frankfurter", async () => {
    const fetchMock=vi.fn(async(input:RequestInfo|URL)=>{
      const url=new URL(String(input));
      expect(url.hostname).toBe("api.frankfurter.dev");
      expect(url.pathname).toBe("/v2/rate/USD/VND");
      return json({date:"2026-11-23",base:"USD",quote:"VND",rate:26350});
    });
    vi.stubGlobal("fetch",fetchMock);
    const result=JSON.parse(await runLiveEverydayTool("convert_currency",{base_currency:"usd",quote_currency:"vnd",amount:10}));
    expect(result.converted_amount).toBe(263500);
    expect(result.reference_date).toBe("2026-11-23");
    expect(result.note).toContain("not a live trading quote");
  });

  it("filters official public holidays by month and first-level subdivision", async () => {
    const fetchMock=vi.fn(async(input:RequestInfo|URL)=>{
      const url=new URL(String(input));
      expect(url.hostname).toBe("nagerholidays.com");
      expect(url.pathname).toBe("/api/v4/Holidays/US/2026");
      return json([
        {date:"2026-07-04",name:"Independence Day",nationalHoliday:true,subdivisionCodes:null,holidayTypes:["Public"]},
        {date:"2026-07-24",name:"California Day",nationalHoliday:false,subdivisionCodes:["US-CA"],holidayTypes:["Public"]},
        {date:"2026-07-25",name:"Florida Day",nationalHoliday:false,subdivisionCodes:["US-FL"],holidayTypes:["Public"]},
        {date:"2026-07-26",name:"Bank closure",nationalHoliday:true,subdivisionCodes:null,holidayTypes:["Bank"]},
      ]);
    });
    vi.stubGlobal("fetch",fetchMock);
    const result=JSON.parse(await runLiveEverydayTool("get_public_holidays",{country_code:"US",year:2026,month:7,subdivision_code:"US-CA"}));
    expect(result.count).toBe(2);
    expect(result.holidays.map((h:{name:string})=>h.name)).toEqual(["Independence Day","California Day"]);
    expect(result.note).toContain("city");
  });

  it("finds potential long weekends from public holidays and selected weekend days", async () => {
    const fetchMock=vi.fn(async()=>json([
      {date:"2026-05-01",name:"Labour Day",nationalHoliday:true,subdivisionCodes:null,holidayTypes:["Public"]},
      {date:"2026-09-08",name:"Midweek holiday",nationalHoliday:true,subdivisionCodes:null,holidayTypes:["Public"]},
    ]));
    vi.stubGlobal("fetch",fetchMock);
    const result=JSON.parse(await runLiveEverydayTool("find_long_weekends",{country_code:"VN",year:2026,weekend_days:[0,6]}));
    expect(result.potential_long_weekends).toHaveLength(1);
    expect(result.potential_long_weekends[0]).toMatchObject({start_date:"2026-05-01",end_date:"2026-05-03",day_count:3,holidays:["Labour Day"]});
    expect(result.note).toContain("do not confirm");
  });

  it("rejects invalid currency codes and hides upstream response bodies", async () => {
    await expect(runLiveEverydayTool("convert_currency",{base_currency:"US",quote_currency:"VND"})).rejects.toThrow("three letters");
    vi.stubGlobal("fetch",vi.fn(async()=>new Response("private upstream body",{status:429})));
    await expect(runLiveEverydayTool("convert_currency",{base_currency:"USD",quote_currency:"VND"})).rejects.toThrow("HTTP 429");
  });
});
