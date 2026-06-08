---
name: sidebar-redesign
description: Playbook for migrating the Vue 3 client from the top nav bar to a left sidebar SaaS layout with CSS design tokens and normalized spacing. Use when asked to redesign the UI layout, add a sidebar, introduce design tokens, or normalize spacing/styling across client/src views.
---

# SaaS Sidebar Redesign Playbook

This skill migrates the Factory Inventory Management UI from its top nav bar to a modern SaaS-style layout: a fixed light sidebar on the left, CSS design tokens, and normalized spacing across all views. Execute the phases in order — the ordering exists to isolate regressions (tokens before layout, layout before per-view cleanup).

## Purpose & Scope

**In scope:**
- Replace `header.top-nav` in `client/src/App.vue` with a fixed 240px left sidebar (light style: white background, slate text, blue active pill)
- Introduce CSS design tokens (`:root` variables) — the codebase currently has **zero CSS variables and zero media queries**
- Normalize spacing/card drift across the 6 routed views (Dashboard, Inventory, Orders, Spending, Demand, Reports)
- Relocate LanguageSwitcher and ProfileMenu to the sidebar bottom (dropdowns flip to drop-up)
- One desktop media query at 1024px

**Out of scope (do not improvise):**
- Mobile layout, hamburger menus, JS collapse toggles
- `client/src/views/Backlog.vue` — it is NOT routed in `main.js` and has no style block. Do not normalize it, do not add a nav link for it.
- Backend, business logic, data flow, filter behavior
- Icon sets — the nav is text-only (Notion-style)

## Non-Negotiable Project Rules

These restate CLAUDE.md so this skill is self-contained:

1. **Any `.vue` file creation or modification MUST be delegated to the `vue-expert` subagent** via the Task tool. The main agent may directly edit only non-`.vue` files (here: `client/src/locales/en.js` and `ja.js`).
2. **vue-expert has no memory of this skill.** Every delegation prompt must be self-contained: paste the design token block (Section "Design Tokens"), the relevant phase spec, exact file paths, and acceptance criteria into the prompt.
3. **Verify in the browser with Playwright MCP tools** (`mcp__playwright__*`) against `http://localhost:3000`. If servers aren't running, use the `/start` skill first.
4. **No emojis in the UI.** Nav items are text-only.
5. **Stay in the slate/blue palette** (#0f172a, #64748b, #e2e8f0, primary #2563eb). The tokens below encode it — do not invent new colors.

## Target Layout

```
┌──────────────┬──────────────────────────────────────────┐
│ aside        │ div.content-area                         │
│ .sidebar     │   margin-left: var(--sidebar-width)      │
│              │ ┌──────────────────────────────────────┐ │
│ fixed,       │ │ <FilterBar/>   sticky, top: 0        │ │
│ 240px wide,  │ ├──────────────────────────────────────┤ │
│ 100vh        │ │ <main.main-content>                  │ │
│              │ │   <router-view/>                     │ │
│ Logo +       │ │   max-width: var(--content-max-width)│ │
│ subtitle     │ │   padding: var(--content-padding)    │ │
│ ──────────   │ │                                      │ │
│ Overview     │ │  (body remains the scroll container  │ │
│ Inventory    │ │   — do NOT put overflow on           │ │
│ Orders       │ │   .content-area)                     │ │
│ Finance      │ │                                      │ │
│ Demand       │ └──────────────────────────────────────┘ │
│ Reports      │                                          │
│ ──────────   │                                          │
│ Language     │                                          │
│ Profile      │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### Sidebar spec (concrete values)

```css
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: var(--color-bg-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: 50;
  /* CRITICAL: no overflow-y: auto — it would clip the bottom drop-up menus */
}
```

- **Logo block (top):** `padding: 1.25rem 1rem`. Company name `1rem / 600 / var(--color-text-primary)`, subtitle `0.75rem / var(--color-text-secondary)`. Keep both bound to `t('nav.companyName')` / `t('nav.subtitle')`.
- **Nav (middle):** `flex: 1; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.25rem`. Six `router-link`s in existing order: `/` Overview, `/inventory`, `/orders`, `/spending` Finance, `/demand`, `/reports`.
- **Nav link:** `display: block; padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.875rem; font-weight: 500; color: var(--color-text-secondary); text-decoration: none;`
  - Hover: `background: var(--color-bg-hover); color: var(--color-text-primary)`
  - Active: `background: var(--color-primary-soft); color: var(--color-primary); font-weight: 600`
  - Keep the existing active-state mechanism: `:class="{ active: $route.path === '...' }"`
  - Do NOT add `white-space: nowrap` — Japanese labels are longer and must wrap.
- **Bottom block:** `border-top: 1px solid var(--color-border); padding: 0.75rem; display: flex; flex-direction: column; gap: 0.5rem`. Holds `<LanguageSwitcher />` then `<ProfileMenu />`, stacked.
- **Content column:** `div.content-area { margin-left: var(--sidebar-width); }` wraps `<FilterBar />` and `main.main-content`. The `body` stays the scroll container.

## Design Tokens

**Paste this block verbatim into every vue-expert delegation prompt.** It goes into `:root` at the top of App.vue's existing UNSCOPED `<style>` block (currently lines ~164–486) — that block is the project's de-facto global stylesheet, so no new file or import is needed.

```css
:root {
  /* color */
  --color-text-primary: #0f172a;
  --color-text-secondary: #64748b;
  --color-text-muted: #94a3b8;
  --color-border: #e2e8f0;
  --color-bg-page: #f8fafc;        /* confirm against the actual body bg in App.vue during Phase 2 */
  --color-bg-surface: #ffffff;
  --color-bg-hover: #f1f5f9;
  --color-primary: #2563eb;
  --color-primary-soft: #eff6ff;

  /* spacing (4px scale) */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  /* radius */
  --radius-sm: 6px;   /* badges, buttons, nav pills */
  --radius-md: 10px;  /* cards — canonical */
  --radius-lg: 12px;  /* modals, dropdowns */

  /* shadow — overlays only, never on cards */
  --shadow-sm: 0 1px 2px rgb(15 23 42 / 0.06);
  --shadow-md: 0 4px 12px rgb(15 23 42 / 0.10);

  /* layout */
  --sidebar-width: 240px;
  --content-max-width: 1600px;
  --content-padding: 2rem;
}
```

### Canonical values (the normalization contract)

The views have drifted. These are the single correct values; anything else gets converged to them:

| Property | Current drift | Canonical |
|---|---|---|
| Card padding | 1.25rem vs 1.5rem | `var(--space-6)` (1.5rem) |
| Grid gaps | 1rem / 1.25rem / 1.5rem | `var(--space-5)` (1.25rem) |
| Section margin-bottom | 1rem–2rem | `var(--space-6)` (1.5rem) |
| `.card-title` size | 1rem / 1.125rem / 1.25rem | `1rem`, weight 600 |
| Card border-radius | 10px vs 12px (Reports) | `var(--radius-md)` (10px) |
| Card elevation | border vs shadow (Reports) | `1px solid var(--color-border)` only — shadows reserved for dropdowns/modals |

**Normalization rule: DELETE scoped overrides so the globals apply. Do not copy token values into the scoped overrides** — that preserves the duplication this skill exists to remove.

## Migration Phases

Run phases strictly in order. Verify with Playwright between phases — the phase boundaries are regression gates.

### Phase 0 — Preflight (main agent)

1. Ensure servers are running (`/start` skill, or confirm `http://localhost:3000` and `http://localhost:8001/docs` return 200).
2. Playwright: navigate to each of the 6 routes (`/`, `/inventory`, `/orders`, `/spending`, `/demand`, `/reports`) and take a baseline screenshot of each. These are the comparison set for Phase 2's "zero visual change" gate.

### Phase 1 — Locale keys (main agent — no .vue files)

The Reports nav link is hardcoded English in App.vue (`Reports`, around line 26) because `nav.reports` does not exist in the locales.

1. In `client/src/locales/en.js`, add `reports: 'Reports'` to the `nav` object.
2. In `client/src/locales/ja.js`, add the matching key. Check the tone/style of the existing `nav` entries in `ja.js` before choosing the translation (likely `レポート`), so it is consistent with its neighbors.

This goes first so Phase 3's `t('nav.reports')` resolves the moment it's introduced.

### Phase 2 — Token foundation (vue-expert; App.vue only; ZERO visual change)

Delegate to vue-expert with the token block pasted in. Instructions for the delegation:

1. Add the `:root` block at the top of App.vue's existing unscoped `<style>` section.
2. Before writing `--color-bg-page`, read the actual `body` background value in App.vue and use that (expected `#f8fafc`).
3. Mechanically replace hardcoded values in that style block with the matching tokens (`#e2e8f0` → `var(--color-border)`, `#64748b` → `var(--color-text-secondary)`, `10px` card radius → `var(--radius-md)`, etc.). Values with no matching token stay as-is — do not invent tokens.
4. Do NOT change any selector, layout property, or value that lacks an exact token equivalent. This phase is a pure refactor.

**Acceptance:** Playwright screenshots of all 6 routes are pixel-identical to the Phase 0 baselines. If anything moved, a replacement was wrong — fix before proceeding.

### Phase 3 — Layout shell (vue-expert; ATOMIC across 4 files)

These four files must change in ONE delegation because they are coupled: deleting the 70px header breaks FilterBar's `top: 70px` sticky offset and strands the dropdown anchoring in the same moment.

Files: `client/src/App.vue`, `client/src/components/FilterBar.vue`, `client/src/components/LanguageSwitcher.vue`, `client/src/components/ProfileMenu.vue`.

**App.vue:**
1. Replace `header.top-nav > .nav-container` with `aside.sidebar` per the Target Layout spec above. Same 6 router-links, same `t('nav.*')` bindings and active-class mechanism.
2. Change the hardcoded `Reports` link text to `{{ t('nav.reports') }}` (key added in Phase 1).
3. Move `<LanguageSwitcher />` and `<ProfileMenu />` into the sidebar bottom block. Keep ProfileMenu's `@show-profile-details` / `@show-tasks` events wired to the same modals.
4. Wrap `<FilterBar />` and `main.main-content` in `<div class="content-area">` with `margin-left: var(--sidebar-width)`.
5. Delete the now-dead styles: `.top-nav`, `.nav-container`, `.nav-tabs` (including the `::after` active underline). Add the sidebar styles.
6. `.app` no longer needs to be a flex column for the header; keep it simple (`min-height: 100vh`).

**FilterBar.vue:**
- `.filters-bar`: `top: 70px` → `top: 0` (the 70px referenced the deleted header height). Keep `position: sticky` and the z-index below the sidebar's 50.
- `.filters-container`: keep `max-width: var(--content-max-width)`; it now centers within the content column.

**LanguageSwitcher.vue and ProfileMenu.vue:**
- Both dropdowns are anchored `top: calc(100% + 0.5rem); right: 0` — correct for a top bar, wrong at the bottom of a sidebar (they'd open downward off-screen).
- Flip both to drop-UP: `bottom: calc(100% + 0.5rem); left: 0; top: auto; right: auto`.
- Make the trigger buttons full-width within the sidebar bottom block so they read as menu rows, not floating pills.
- Keep the existing open/close behavior (`@blur` + timeout) and z-index 1000.

**Acceptance:** every route renders with the sidebar; no `.top-nav` in the DOM; FilterBar sticks to the top of the content column when scrolling; both bottom menus open upward and are fully visible.

### Phase 4 — Per-view normalization (one vue-expert delegation PER view)

Order is riskiest-first, cleanest last as a control. Paste the token block AND the canonical-values table into each delegation. The instruction pattern for every view: **delete scoped redefinitions of global classes so App.vue's globals apply; convert genuinely view-specific styles to tokens.**

1. **Reports.vue** (most divergent): delete its scoped `.card` redefinition entirely (it uses 12px radius + box-shadow instead of the global border style), and its `.card-header` / `.card-title` redefinitions. The global `.card` takes over. Tokenize remaining view-specific spacing.
2. **Dashboard.vue**: remove the scoped `.page-header` override (flex layout stays only if the header genuinely contains right-aligned content — check first); tokenize `.kpi-grid` and `.charts-grid` (gap → `var(--space-5)`); keep `.charts-grid`'s `repeat(2, 1fr)` columns.
3. **Inventory.vue**: remove the scoped `.page-header`, `.card-header`, `.card-title` redefinitions (they duplicate/conflict with globals). Keep search/sort control styles, tokenized.
4. **Demand.vue**: tokenize `.demand-trend-cards` (gap, margins) and `.trend-card` (padding → `var(--space-6)`, which is the canonical card padding it already uses).
5. **Spending.vue**: `.stats-grid-finance` — if its column behavior matches the global `.stats-grid` (`auto-fit, minmax(...)`), delete it and use the global class in the template; if the minmax genuinely differs for layout reasons, keep it but tokenize gap/margins. Keep the accent-border revenue/cost card variants; tokenize their spacing.
6. **Orders.vue** (verify-only control): it consumes globals cleanly. Make no changes; just verify it still renders correctly after the global changes — if Orders regressed, a global edit in an earlier phase was wrong.

**Acceptance per view:** card padding, gaps, title sizes, and radii visually match the other already-normalized views; no scoped selector redefines `.card`, `.card-header`, `.card-title`, or `.page-header`.

### Phase 5 — Responsive (vue-expert; App.vue)

Add the project's first media query to the unscoped style block:

```css
@media (max-width: 1024px) {
  :root {
    --sidebar-width: 200px;
    --content-padding: 1.5rem;
  }
}
```

Because the sidebar width and content margin both derive from `--sidebar-width`, this one rule shrinks the whole layout coherently. No JS, no collapse toggle.

### Phase 6 — Final verification (main agent + code-reviewer)

1. Run the full Verification Checklist below with Playwright.
2. Delegate a `code-reviewer` subagent pass over the complete diff (`git diff`).
3. Run existing tests if any touch the frontend; backend tests (`tests/backend/`) should be untouched and still pass.

## Verification Checklist (Playwright)

For EACH route — `/`, `/inventory`, `/orders`, `/spending`, `/demand`, `/reports`:

1. `browser_navigate` to the route, then `browser_snapshot`:
   - `aside.sidebar` present; NO `header.top-nav` in the DOM
   - Exactly one nav link has active styling, and it matches the current route
2. Scroll down (Inventory and Orders have long tables): FilterBar sticks at the top of the content column; it never overlaps or slides under the sidebar; the sidebar stays fixed.
3. Console (`browser_console_messages`): no new errors.

Once, globally:

4. Open LanguageSwitcher, switch to Japanese: all 6 nav labels translate — **including Reports** (this catches a missed Phase 1). Labels wrap inside the 240px sidebar rather than overflowing. Check the logo block (companyName/subtitle) also fits in ja.
5. Open ProfileMenu at the sidebar bottom: dropdown opens UPWARD, fully visible, not clipped by the sidebar edge or viewport.
6. `browser_resize` to 1280x800, then 1000x800: at 1000px the 1024px media query applies (narrower sidebar); no horizontal scrollbar at either size.
7. Compare screenshots across views: card padding, grid gaps, and card-title sizes look uniform (the Phase 4 contract).
8. Switch back to English; confirm locale persistence still works (localStorage key `app-locale`).

## Pitfalls

Each of these has bitten a layout migration like this one — the phases above are sequenced specifically to avoid them:

1. **The 70px coupling.** `FilterBar.vue` is sticky at `top: 70px` only because the old header was 70px tall. Removing the header without fixing FilterBar in the same change leaves a 70px dead zone — this is why Phase 3 is atomic across 4 files.
2. **App.vue's style block is UNSCOPED (global).** Every edit there propagates to all views instantly. That's why tokens land first as a zero-visual-change refactor (Phase 2) — if tokenization and layout changed together, you couldn't tell which one broke a view.
3. **Scoped overrides shadow globals.** Dashboard, Inventory, and Reports redefine `.page-header` / `.card-header` / `.card` in scoped blocks. Fixing the global definition does nothing for those views until the scoped overrides are DELETED. Restyling the overrides in place defeats the purpose.
4. **The scroll-container trap.** If `.content-area` gets `overflow: auto`, `position: sticky` inside it re-anchors to that container and the body scrollbar disappears. Keep `body` as the scroll container: sidebar `position: fixed`, content offset via `margin-left`.
5. **Sidebar overflow clips drop-ups.** `overflow-y: auto` on the sidebar would clip the LanguageSwitcher/ProfileMenu drop-up menus. The nav fits in any reasonable viewport; leave overflow visible.
6. **Backlog.vue is a trap.** It exists in `views/` but is not routed and has no style block. Don't add it to the nav, don't normalize it.
7. **Stale 1600px containers.** `.nav-container`'s max-width dies with the header. `.main-content` and `.filters-container` keep `var(--content-max-width)`, now applied within the content column — don't center them against the full viewport width.
8. **No emojis as nav icons.** The design system forbids emojis in the UI. The nav is text-only; if icons are requested later, they must be inline SVG (separate task, not this skill).

## Delegation Prompt Template

Use this shape for every vue-expert Task call:

```
You are modifying the Vue 3 frontend of the Factory Inventory Management app
(client/ directory, Vite dev server on http://localhost:3000).

CONTEXT: We are migrating from a top nav bar to a fixed 240px left sidebar
(light SaaS style) with CSS design tokens. [One sentence on which phase this is.]

DESIGN TOKENS (already in / to be added to App.vue's unscoped <style> :root):
[paste the full token block from the skill]

CANONICAL VALUES:
[paste the normalization table — Phases 4+ only]

YOUR TASK:
[paste the exact phase instructions and file paths]

CONSTRAINTS:
- No emojis in the UI. Slate/blue palette only — use the tokens, do not invent colors.
- [Phase-specific constraints, e.g. "zero visual change" for Phase 2]

ACCEPTANCE:
[paste the phase's acceptance criteria]
```
