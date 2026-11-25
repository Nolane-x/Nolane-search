# Wave 69 research — Nearby Essentials and public website validation

Date: 2026-11-25

## Goal

Improve the low-volume Nearby Places feature without introducing a second provider request or a map tile dependency.

## User-facing change

A new category, **Tiện ích thiết yếu**, provides a single bounded Overpass query for:
- Food and drink: restaurant, cafe, fast_food
- Shopping: supermarket, convenience
- Pharmacy and healthcare: pharmacy, hospital, clinic, doctors, dentist
- Finance: ATM and bank
- Mobility: fuel and EV charging

Each returned place is labelled with its inferred category in the response. The UI continues to display the place-specific type and the source map link. Existing individual categories remain available.

## Query-cost boundary

- Essentials uses one POST to the same fixed Overpass endpoint.
- Only two static filters are generated: an allowlisted amenity group and an allowlisted shop group.
- The maximum radius for Essentials is 3,000 m; individual categories retain their existing 5,000 m maximum.
- The 25-item output cap and 18-second client timeout remain unchanged.
- The UI disables the 5 km option when Essentials is selected; the API independently rejects a forged 5 km request.
- No parallel queries, polling, background requests, or new geocoding provider are introduced.

## Result website validation

OSM `website` and `contact:website` fields are untrusted community data. They are now validated with the repository's shared `isSafePublicUrl` policy before a website link is returned. Non-HTTPS schemes, credentials, IP literals, local/private hostnames, and non-standard ports are omitted. This is a link-validation improvement; the Worker does not fetch the returned website URL.

## Tests

- Verify that the query contains both exact static allowlists and is sent only once.
- Verify the result category mapping for cafe, supermarket, pharmacy, ATM and EV charging.
- Verify the Essentials radius cap rejects 5 km before any upstream request.
- Verify that local/private IP website URLs, credentials and non-standard ports are omitted.
- Verify that the UI exposes Essentials and disables 5 km in that mode.
- Existing anonymous API 401 and same-origin behavior remain unchanged.

## Not included

- Turn-by-turn route distance or travel-time estimation.
- "Open now" verification, phone checks or reviews.
- Geocoding and autocomplete.
- Persistent recent locations, saved places, background tracking or history.
- Map tile embedding.
- An assertion that the public Overpass endpoint can sustain broad public traffic; it remains a low-volume personal-use integration.
