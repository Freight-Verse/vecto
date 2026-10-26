# Brand and design tokens

**FreightVerse** is the company: an umbrella of open-source logistics software. **Vecto** is its
open-source TMS. FreightVerse is monochrome; each product adds one accent. Vecto's accent is
**signal orange**. Light and dark themes are equal; every token has both values.

## Rules
- Primary buttons are `primary` (ink in light, near-white in dark) — one per view, like Frappe UI.
- `signal` only for: the Vecto mark, focus rings, the selected navigation marker, and Vecto Assistant (AI) actions. Never a status, never body text.
- Text on `signal` is always `on-signal` (ink). White on signal fails contrast (3.4:1).
- Statuses use `success`, `warning`, `danger`, `info` (+ `-tint` background, `-ink` text). `warning` is yellow-amber so it is never confused with signal.
- Borders, not shadows: cards use `line`; `shadow-overlay` only for menus, popovers, dialogs.
- Type: Inter (400/500/600); JetBrains Mono for IDs and reference numbers. Spacing on a 4px base; radii 6/8/12.

## Colour tokens
| Token | Light | Dark | Usage |
|---|---|---|---|
| `paper` | #F4F4F2 | #0E0F12 | Page background (surface-0). Light: warm off-white. Dark: near-black. |
| `surface` | #FAFAF9 | #16181C | In-flow cards and table headers on paper. |
| `surface-raised` | #FFFFFF | #1C1F24 | Panels, inputs, the load page side panel. |
| `surface-overlay` | #FFFFFF | #23262C | Menus, popovers, dialogs. |
| `line` | #E4E4E0 | #2A2D33 | Default hairline: dividers, card and input borders. |
| `line-strong` | #D2D2CC | #3A3E45 | Hover borders, emphasised dividers. |
| `ink` | #111318 | #F2F2F0 | Primary text and icons on paper, surface and surface-raised. FreightVerse's mark colour. |
| `ink-secondary` | #55585F | #A9ACB3 | Supporting text, table cell secondary values. |
| `ink-muted` | #6B6E75 | #868A92 | Captions, placeholders, metadata. Meets 4.5:1 on surface-raised in both themes. |
| `primary` | #111318 | #F2F2F0 | Primary button fill (one per view). Ink in light, inverted to near-white in dark. |
| `primary-hover` | #2A2D33 | #D9D9D6 | Primary button hover. |
| `on-primary` | #FFFFFF | #111318 | Text on primary. |
| `signal` | #F05A1A | #FF6A2B | Vecto signal orange. Logo, focus ring, selected nav item marker, Vecto Assistant actions. Never a status, never body text on paper. |
| `signal-hover` | #D94C10 | #FF844F | Hover on signal fills. |
| `on-signal` | #111318 | #111318 | Text on signal fills: always ink (white on signal fails contrast). |
| `signal-text` | #C2410C | #FF8A57 | Signal-coloured text and links where the accent must read as text (5.2:1 on white, 8.2:1 on dark paper). |
| `signal-tint` | #FDEBE2 | #3A1C10 | Quiet signal wash: assistant message background, selected row. |
| `signal-tint-ink` | #9A3412 | #FFB08C | Text on signal-tint. |
| `focus` | = signal | = signal | Focus ring colour: 2px, offset 2px. 3:1 on paper in light, 6.7:1 in dark. |
| `success` | #1F9D55 | #3FBF73 | Success fills and dots: delivered, compliant, paid. |
| `success-tint` | #E3F3E8 | #12301F | Success badge background. |
| `success-ink` | #166534 | #6EE7A1 | Text on success-tint. |
| `warning` | #E5B400 | #F2C200 | Warning fills and dots: at risk, expiring. Yellow-amber so it is never mistaken for signal orange. |
| `warning-tint` | #FFF5CC | #3A3110 | Warning badge background. |
| `warning-ink` | #7A5A00 | #F7D35C | Text on warning-tint. |
| `danger` | #D92D20 | #F04438 | Danger fills and dots: exception, blocked, failed. |
| `danger-tint` | #FDECEA | #3E1715 | Danger badge background. |
| `danger-ink` | #B42318 | #FF8A80 | Text on danger-tint. |
| `info` | #2563EB | #6C9BFF | Info fills and dots: in transit, scheduled. |
| `info-tint` | #E8EFFD | #162545 | Info badge background. |
| `info-ink` | #1D4ED8 | #8AB4FF | Text on info-tint. |

## Frappe UI mapping
Frappe UI `surface-*` → `paper`/`surface`/`surface-raised`/`surface-overlay`; `ink-*` → `ink`/`ink-secondary`/`ink-muted`;
`outline-*` → `line`/`line-strong`. Implement as a Frappe UI theme override (CSS variables under
`[data-theme="light"]` and `[data-theme="dark"]`); components use tokens, never literal hex.
