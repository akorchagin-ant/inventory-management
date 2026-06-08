---
name: vue-component-audit
description: Analyze Vue component structure and produce a prioritized report of performance and code-reuse optimizations. Use when asked to audit components, find performance issues, identify duplicated logic, or suggest refactoring opportunities in client/src.
---

# Vue Component Audit

This skill analyzes the Vue 3 frontend (`client/src/`) and produces a prioritized findings report covering two dimensions: **render performance** and **code reuse**. It is ANALYSIS-ONLY — it reads, measures, and reports. Applying fixes is a separate step the user must request, and any resulting `.vue` edit MUST be delegated to the `vue-expert` subagent (CLAUDE.md mandate).

## Ground Rules

1. **Read-only by default.** The deliverable is a report. Do not modify files during the audit.
2. **Verify every finding before reporting it.** The grep recipes below produce candidates, not findings. Read the surrounding code: a `formatCurrency()` call inside a `v-for` is a finding; the same call in a one-shot header is noise.
3. **Don't flag intentional design.** These are deliberate and documented — reporting them wastes the reader's time:
   - `.charts-grid` fixed `repeat(2, 1fr)` columns (Dashboard)
   - `.stats-grid-finance` 240px minmax (Spending — keeps 4 columns beside the sidebar)
   - No `overflow-y` on `.sidebar` (would clip drop-up menus)
   - The unscoped global style block in App.vue (it IS the design system)
4. **Anchor every finding to `file:line`** so it's clickable and verifiable.
5. If the user asks to APPLY findings afterward: delegate `.vue` changes to `vue-expert` (one delegation per file, self-contained prompts), verify each with Playwright MCP against http://localhost:3000, and respect the design system (tokens in App.vue `:root`, no emojis, slate/blue palette).

## Project Map (orient before measuring)

- **Views** (`client/src/views/`): Dashboard, Spending, Reports, Demand, Inventory, Orders are routed; **Backlog.vue is NOT routed** (dead-code candidate — report it, don't delete it unprompted).
- **Components** (`client/src/components/`): FilterBar, LanguageSwitcher, ProfileMenu, and SEVEN modal components (TasksModal, PurchaseOrderModal, InventoryDetailModal, CostDetailModal, BacklogDetailModal, ProductDetailModal, ProfileDetailsModal).
- **Composables** (`client/src/composables/`): useFilters (shared filter state), useI18n (custom i18n, not vue-i18n), useAuth (mock user).
- **Utilities**: `utils/currency.js` (formatCurrency), `api.js` (ALL HTTP goes through here — direct axios calls in components are findings).
- **Design system**: tokens in App.vue `:root`; canonical card/grid/title styles are global — scoped redefinitions of `.card`/`.card-header`/`.card-title`/`.page-header` are findings (this was normalized once; regressions creep back).
- **House conventions** (from client/CLAUDE.md): Composition API only; extract a component when template > 100 lines or logic > 150 lines; computed for derived data, methods for actions; unique `v-for` keys, never index; loading/error states on every fetch.

## Phase 1 — Inventory & Metrics

Collect the raw numbers first; they rank everything later.

```bash
cd client/src && wc -l views/*.vue components/*.vue composables/*.js | sort -rn
```

For each file over ~400 lines, also split the count by section (template vs script vs style) — a 900-line file that is 600 lines of scoped CSS is a different problem than one with a 600-line setup().

```bash
awk '/<template>/,/<\/template>/' views/Dashboard.vue | wc -l   # repeat per section
```

Flag against the house thresholds: template > 100 lines or logic > 150 lines → extraction candidate. (At last audit, Dashboard.vue was ~1,040 lines and Spending.vue ~850 — both far over threshold. Re-measure; do not reuse stale numbers.)

## Phase 2 — Performance Checks

Run each recipe, then READ the hits to confirm.

**P1. Per-render function calls in templates.** Function calls in interpolations re-execute on every render; inside `v-for` they multiply.
```bash
grep -n "{{ format\|{{ translate\|(get[A-Z][a-zA-Z]*(" views/*.vue components/*.vue
```
Severity rises with loop size: a formatter inside the 250-row Orders table is HIGH; in a 4-row table it's LOW. The fix is usually a computed that pre-maps the rows (`rowsForDisplay`), not memoizing the formatter.

**P2. v-for keyed by index.** Breaks DOM reuse when lists reorder/filter — and this codebase filters everything.
```bash
grep -rn ':key="index"\|:key="i"' client/src
```
(At last audit Reports.vue had three of these — quarterly table, bar chart, monthly table — despite CLAUDE.md rule #1. Use `q.quarter` / `month.month` style keys.)

**P3. Computed vs method misuse.** Derivations implemented as functions called from the template recompute every render; computeds cache.
```bash
grep -n "const get[A-Z]" views/*.vue   # then check if the template calls them with args
```
Functions taking per-row args can't be computeds directly — pre-mapping the collection in one computed is the pattern.

**P4. Watcher hygiene.** Every view watches filter state and refetches. Check each `watch(`:
- fires once per change or once per batch? (`useFilters` exposes multiple refs — watching them separately causes N fetches per reset)
- needs `{ deep: true }`? (deep watchers on large arrays are expensive and usually unnecessary here since API responses are replaced wholesale)
- search inputs: is there a debounce, or does each keystroke trigger work?

**P5. Reactivity overhead.** Large static datasets wrapped in `ref()` get deep proxies they don't need. Look for big constant lookup tables or chart configs inside `setup()` that never change — hoist to module scope or `markRaw`/`shallowRef`.

**P6. v-if vs v-show on hot toggles.** Modals that open/close frequently with heavy subtrees: `v-if` re-creates the subtree each open. The seven modals all mount on `v-if`-style `isOpen` props — fine for rarely-opened ones, worth `v-show` only if profiling shows open latency. Report only with evidence.

## Phase 3 — Reuse Checks

**R1. Modal scaffolding duplication.** All seven modals re-implement the same overlay, header/close button, transition, and click-outside handling (~60–100 lines each).
```bash
grep -c "modal-overlay" components/*Modal*.vue
```
Suggested shape: a `BaseModal.vue` with slots (header/body/footer), keeping per-modal content where it is. Estimate the line savings in the report (it was ~400+ lines at last audit).

**R2. Fetch lifecycle duplication.** Every view hand-rolls `loading` / `error` / `loadData` / `onMounted` / filter-watch:
```bash
grep -l "const loading" views/*.vue
```
Suggested shape: `useAsyncData(fetchFn)` composable returning `{ data, loading, error, reload }`, optionally `useFilteredData` that also wires the filter watch. This is the highest-leverage reuse fix — it touches all seven views.

**R3. Formatter duplication.** `utils/currency.js` exists, yet views define local `formatNumber`/`formatDate` and call `toLocaleString` inline:
```bash
grep -rn "toLocaleString\|const formatNumber\|const formatDate" views/ components/ | grep -v utils
```
Suggested shape: consolidate into `utils/format.js` (number, date, percent) and import everywhere. Check locale-awareness: useI18n drives currency (USD/JPY) — formatters that hardcode `'en-US'` are also correctness findings.

**R4. Scoped CSS duplicating the design system.** Token regressions and re-declared globals:
```bash
grep -rn "#0f172a\|#64748b\|#e2e8f0\|#2563eb" client/src/views client/src/components   # should be var(--...) now
grep -rn "^\.card\b\|^\.card-header\b\|^\.card-title\b\|^\.page-header\b" client/src/views
```
Anything matching is drift from the normalization pass.

**R5. Template pattern duplication.** Status badges, stat cards, and table headers repeat across views. Only report extraction when the pattern appears 3+ times AND has identical semantics — premature componentization is its own smell.

**R6. Dead code.** Backlog.vue (unrouted), unused composable exports, scoped CSS selectors absent from their templates:
```bash
# per scoped class: defined in <style> but absent from <template>
```
Dashboard accumulated ~200 lines of orphaned CSS once already; recheck after any template surgery.

## Phase 4 — Report

Produce a single markdown report, ranked by (severity, then effort ascending — quick high-impact wins first):

```markdown
# Vue Component Audit — <date>

## Summary
<3-5 sentences: overall health, the one or two themes, total estimated line savings>

## Findings

| # | Finding | Location | Dim | Severity | Effort | Suggested fix |
|---|---------|----------|-----|----------|--------|---------------|
| 1 | v-for keyed by index on filterable table | views/Reports.vue:28 | Perf | High | S | key on q.quarter |

## Detail per finding
<for each: what, why it matters HERE (loop size, render frequency), the concrete fix, and what NOT to change>

## Not flagged (checked and intentional)
<list what was examined and deliberately excluded, so the next audit doesn't re-litigate>
```

**Severity rubric** — High: measurable render cost on a hot path (large v-for, every-keystroke work) or a correctness risk (index keys on filtered lists, locale-blind formatting). Medium: multiplies maintenance cost (7-way duplication) or violates a documented convention. Low: style drift, dead code, minor dupes.

**Effort rubric** — S: one file, mechanical. M: one new shared unit + 2–4 call sites. L: touches most views or needs visual re-verification across routes.

## Phase 5 — Applying (only when the user asks)

1. Order: correctness (P2 keys, locale bugs) → extractions (R1/R2/R3) → performance polish (P1/P3) → dead code (R6).
2. One vue-expert delegation per file; paste the relevant finding, the house conventions, and the design-token list into each prompt (vue-expert has no memory of this skill).
3. Shared-unit extractions (BaseModal, useAsyncData, utils/format.js): create the shared unit FIRST in its own delegation, verify it in one consumer, then migrate remaining consumers in parallel delegations.
4. Verify with Playwright MCP after each batch: affected routes render identically, no console errors, filters and modals still work. Run `/test` at the end.
5. Commit per logical unit so regressions bisect.
