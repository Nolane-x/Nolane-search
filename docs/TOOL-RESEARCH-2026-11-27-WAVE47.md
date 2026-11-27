# Wave 47 research — everyday-life utilities
Date: 2026-11-27

Eight bounded processors were selected because each creates a useful artifact or transparent calculation:
- QR PNG, Wi-Fi join QR, vCard contact bundle and iCalendar event file.
- Progressive electricity and water bill estimates.
- Mobile data and home broadband plan comparisons by expected usage.

QR rendering reuses the repository's qrcode/Pillow dependency. vCard and iCalendar use standard-library serialization. Financial arithmetic uses Decimal. No new hosted service, paid API, secret or D1 migration is introduced.

A QR does not prove a URL or Wi-Fi network safe. Wi-Fi QR and vCard files may contain sensitive information. Tariff and plan figures are user supplied and are not live official prices. Broadband advertised Mbps is not a measured speed test. Timed calendar entries require explicit timezone offsets and all-day DTEND is exclusive.

Release gate: TypeScript catalog, Python allowlist, handler registry and mirrored pipeline transitions must agree; targeted tests plus full CI/Worker build must pass.
