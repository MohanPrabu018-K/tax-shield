# SEO Audit (frontend productization)

## Implemented
- `src/app/robots.ts`: allows `/`, `/login`, `/register`; disallows
  `/dashboard`, `/transactions`, `/documents`, `/obligations`, `/deadlines`,
  `/scenarios`, `/reports`, `/assistant`, `/settings`, `/api/`.
- `src/app/sitemap.ts`: public routes only.
- Edge `middleware.ts`: `X-Robots-Tag: noindex, nofollow` on all private
  prefixes (defense in depth even if robots.txt is ignored).
- Root layout keeps global title/description; private pages carry no
  indexable metadata (all `'use client'`, no per-route metadata to index).

## Verified
- Playwright specs assert `x-robots-tag: noindex` on `/dashboard` and
  200s on `/robots.txt` + `/sitemap.xml` (run with live stack in CI).

## Next
Per-route server metadata for public marketing pages, canonical URLs,
Open Graph/Twitter cards, Organization + SoftwareApplication + FAQ JSON-LD
when the marketing site ships. No private financial page is exposed.
