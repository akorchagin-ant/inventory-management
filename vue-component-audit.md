# Vue Component Audit — 2026-06-08

## Summary

The frontend is structurally healthy after the sidebar redesign (centralized API client, shared filter/i18n composables, design tokens in the views), but two themes dominate: **per-render work in hot templates** (the 250-row Orders table executes ~1,000 function calls per render; three views re-filter arrays inside template expressions) and **seven-way duplication** (every modal re-implements the same ~100-line overlay scaffold; every view hand-rolls the same fetch lifecycle; date/number formatters are redefined per file). One correctness bug surfaced: the Finance view ignores three of the four global filters. Estimated reclaimable code: 600–800 lines.

## Findings

| # | Finding | Location | Dim | Severity | Effort | Suggested fix |
|---|---------|----------|-----|----------|--------|---------------|
| 1 | Spending ignores warehouse/category/status filters: fetches orders unfiltered, watches only `selectedPeriod` | views/Spending.vue:355,374 | Correctness | High | S | pass `getCurrentFilters()` to `api.getOrders`, watch all four filter refs |
| 2 | `v-for` keyed by index on three filterable lists | views/Reports.vue:28,51,82 | Correctness/Perf | High | S | key on `q.quarter` / `month.month` |
| 3 | 250-row Orders table: `translateCustomerName`/`translateProductName`/`formatDate`×2 per row (~1,000 calls/render) | views/Orders.vue:48–70 | Perf | High | M | one computed pre-mapping rows for display |
| 4 | Orders stat cards re-filter the 250-order array 4× per render in template (`getOrdersByStatus(...).length`) | views/Orders.vue:14–26 | Perf | Medium | S | single `statusCounts` computed |
| 5 | Demand filters forecast array 3× per render in template (`getForecastsByTrend(...)`) | views/Demand.vue:21,40,59 | Perf | Medium | S | computeds per trend (or one grouped computed) |
| 6 | `:key="idx"` on order line-items | views/Orders.vue:57 | Perf | Medium | S | key on `item.sku` |
| 7 | Fetch lifecycle (loading/error/load/onMounted/filter-watch) duplicated in all 7 views | views/*.vue | Reuse | Medium | L | `useAsyncData(fetchFn)` composable; views keep only their fetch logic |
| 8 | Modal scaffold (overlay, header/close, transition, isOpen/close) duplicated across 7 modals; none close on Escape | components/*Modal*.vue | Reuse | Medium | L | `BaseModal.vue` with header/body/footer slots + Escape handling |
| 9 | Formatters redefined per file (formatDate ×4 variants, formatNumber, formatDateShort); Reports hardcodes `en-US` | Spending.vue:396,403; Reports.vue; Orders.vue; modals | Reuse | Medium | M | `utils/format.js` (formatNumber/formatDate/formatDateShort/formatPercent); keep currency in utils/currency.js |
| 10 | 128 raw design-token hex values in scoped styles — the modals were never tokenized during the redesign | 7 modals + ProfileMenu, LanguageSwitcher, Dashboard, Orders, Demand | Drift | Low | M | replace exact token matches with `var(--...)` during the same per-file passes |
| 11 | Backlog.vue is unrouted dead code (152 lines) | views/Backlog.vue, main.js | Dead code | Low | — | product decision: add a route or delete; NOT auto-fixed |
| 12 | Transaction details shown via `alert()` while every other detail view uses a modal | views/Spending.vue:452 | UX consistency | Low | M | reuse CostDetailModal pattern; noted, not fixed in this pass |

## Detail highlights

- **#1** is the only behavior bug: `loadData` runs `api.getOrders()` with no arguments while Dashboard and Orders pass `getCurrentFilters()`. Changing Location/Category/Status in the global FilterBar updates every other view but leaves Finance numbers stale. CLAUDE.md specifies all four filters apply to all data.
- **#3/#4**: Vue re-runs template function calls on every render. With 250 rows × 4 calls plus 4 stat-card array filters, a single filter keystroke re-executes ~1,250 calls. Pre-mapping rows in one computed makes re-renders proportional to actual changes.
- **#8**: none of the seven modals handles Escape — a BaseModal centralizes the fix in one place (accessibility win on top of the ~400-line dedup).
- **#10**: the redesign tokenized views and the three layout components; the seven modals predate it or (PurchaseOrderModal) copied per-modal styles from older modals.

## Not flagged (checked, intentional or clean)

- `.charts-grid` fixed 2 columns (Dashboard), `.stats-grid-finance` 240px minmax (Spending), no sidebar overflow — documented design decisions
- views/Inventory.vue:229 scoped `.card-header` — flex-alignment-only remnant kept deliberately during normalization
- Inventory search: client-side computed over 32 rows — no debounce needed
- No `{ deep: true }` watchers, no direct axios usage outside api.js, no orphaned scoped CSS found in the Spending/Dashboard samples (post-cleanup)
- Modal `v-if` mounting: appropriate for rarely-opened dialogs; no evidence of open-latency problems
