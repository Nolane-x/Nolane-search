# Wave 47 — live everyday information tools

Date: 2026-11-24
Status: merged and deployed to production on 2026-11-24.
Pull request: https://github.com/Nolane-x/Nolane-search/pull/100
Merge commit: 76337ff06613b851359ade8330966c925b825316
Scope: five AI-callable public-information functions. Existing 534 file processors remain unchanged.

## Why this wave

Waves 39–46 already added many offline calculations and personal-life workflows. This wave adds source-backed information users ask for directly in chat, without a file upload or API-key setup. The AI receives structured data and must preserve source dates and limitations.

## GitHub projects and API services reviewed

| Project | Research notes | Decision |
|---|---|---|
| https://github.com/open-meteo/open-meteo | Reviewed public forecast/geocoding/air-quality APIs, supported variables and published terms. | Use the public HTTPS APIs only; no source code or assets copied. Free API is non-commercial; data attribution is CC BY 4.0. |
| https://github.com/lineofflight/frankfurter | Reviewed API v2 single-pair rate endpoint, README and MIT license. | Use dated daily reference rates from central-bank/official sources; no source code copied. |
| https://github.com/nager/Nager.Date | Reviewed README and v4 REST examples; v4 response uses nationalHoliday, subdivisionCodes and holidayTypes. | Use public Holidays endpoint v4; no source code copied. First-level subdivisions only, not cities. |

Earlier waves also reviewed consumer workflow projects including Omni Tools, Privatools, Lifehack Toolbox, Actual Budget, Grocy, Mealie, OpenSpeedTest, LubeLogger and HomeBox. Their workflow lessons informed the ordinary-user direction; no upstream source or assets were imported.

## Functions

| Function | User outcome | Provider |
|---|---|---|
| get_weather_forecast | Current weather and 1–7 day forecast by city | Open-Meteo geocoding + forecast |
| check_air_quality | US/EU AQI, PM2.5, PM10 and selected pollutants | Open-Meteo Air Quality |
| convert_currency | Amount conversion with exact rate date and pair | Frankfurter API v2 |
| get_public_holidays | Country/year public holiday lookup with optional month/subdivision | Nager.Date API v4 |
| find_long_weekends | Potential 3+ day holiday/weekend clusters for configurable weekends | Nager.Date + deterministic calendar logic |

## Safety and limitations

- Directly model-callable; no upload, API key, paid service, D1 migration or new dependency.
- Requests use fixed HTTPS hosts, reject redirects, time out after 12 seconds and cap JSON bodies at 500 KB.
- Ambiguous city names return candidate locations and require clarification.
- Open-Meteo results are model-derived, not guarantees or ground-station measurements. The free hosted API is non-commercial only; every result carries CC BY 4.0 attribution.
- Frankfurter returns a daily reference rate, not a live trading, bank cash, card or remittance rate. The precise provider date is returned.
- Nager.Date provides national and first-level subdivision public holidays; it does not establish city/employer/school closure rules.
- Long-weekend ranges are candidates based on listed public holidays and selected weekend days; they do not establish substitute holidays, paid leave or employer policy.
- No upstream source code, assets or dependencies were copied.

## Validation plan

CI must pass TypeScript type-check, full Vitest suite, Python runner tests and Worker build. Focused mocked-fetch tests cover every function, source dates, ambiguity, AQI classification, regional filtering, weekend calculations and upstream errors. CI does not make live upstream calls.

Open-Meteo's free endpoint must not be used for commercial deployment. Select an appropriately licensed provider or self-hosted/commercial service before commercial use.


## Release verification

- PR #100 merged at 2026-11-24T05:47:55Z using squash merge.
- PR CI: https://github.com/Nolane-x/Nolane-search/actions/runs/45335641289 — passed.
- Main CI: https://github.com/Nolane-x/Nolane-search/actions/runs/45335826762 — passed TypeScript, Vitest, deployment-script checks, Python runner tests and Cloudflare Worker build.
- Cloudflare deployment: https://github.com/Nolane-x/Nolane-search/actions/runs/45335826780 — passed, including source verification, bundle dry-run validation, Worker upload, runtime-secret upload and Telegram webhook/command registration.
- Worker export and smoke test: https://github.com/Nolane-x/Nolane-search/actions/runs/45335826815 — passed build/export and live /health smoke check.
- D1 migration step was skipped because the merge introduced no database migration.
- This validates the hosted Worker deployment path; it does not establish a commercial right to use Open-Meteo's free API. Keep that integration for non-commercial use or replace it before commercial operation.
