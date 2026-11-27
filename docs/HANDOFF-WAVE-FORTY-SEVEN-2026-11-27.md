# Wave 47 handoff — everyday-life utilities
Date: 2026-11-27

Adds eight JSON-input processors: QR PNG creation, Wi-Fi QR creation, vCard contact bundle, iCalendar event file, progressive electricity and water bill arithmetic, mobile data plan comparison and home broadband comparison.

Production baseline before this candidate: 534 file processors. Candidate catalog size: 542. These are file processors, not new AI Agent function tools. No live tariff API, carrier price scraper, paid service, new secret or D1 migration is added. Wi-Fi QR and contact outputs may contain sensitive information. Bill and plan calculations use user-entered figures only.

Acceptance: TypeScript catalog IDs match Python allowlist IDs and handlers; pipeline transitions are mirrored in both languages; targeted tests and full CI/Worker build pass before deployment.
