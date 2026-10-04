# Accessibility Audit (frontend productization)

## Implemented
- Semantic landmarks: `aside` nav (labeled), `main`, headings hierarchy per page.
- All icon-only buttons have `aria-label`; modals use `role=dialog` +
  `aria-modal` + labelledby/describedby; close buttons labeled.
- Form inputs use `label` (Input/Select) or `aria-label`; checkboxes have
  associated text; tabs use `tablist/tab/tabpanel` with `aria-selected`.
- Live regions: loading (`role=status`), errors (`role=alert`), forecast/totals
  (`aria-live=polite`), search results announced via headings.
- Color is never the only signal: risk/status shown as text badges alongside color.
- Touch targets: nav rows ≥40px, cart steppers have labels; mobile menu tested
  at Pixel 7 viewport in Playwright matrix.

## Known gaps (next pass)
- Modal lacks focus trap + Escape-to-close + scroll lock.
- Settings tabs lack arrow-key navigation.
- Charts (Recharts) need text alternatives beyond adjacent tables.
- `prefers-reduced-motion` media query not yet wired to disable animation.
