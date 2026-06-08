// Shared display formatters. Currency formatting lives in utils/currency.js
// because it also handles USD->JPY conversion; everything else lands here.
//
// These intentionally reproduce the exact output of the per-view formatters
// they replace (en-US month names, MM/DD/YY short dates) so consolidating
// them causes zero visual change. Pass a locale to localize.

export function formatNumber(value, locale = 'en-US') {
  if (value === null || value === undefined || isNaN(value)) return '0'
  return value.toLocaleString(locale, { maximumFractionDigits: 2 })
}

export function formatDate(dateString, locale = 'en-US') {
  // Falsy must be checked before construction: new Date(null) is the Unix
  // epoch (a VALID date), so isNaN alone would render "Jan 1, 1970" for
  // null delivery dates instead of a dash.
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '-'
  return date.toLocaleDateString(locale, { month: 'short', day: 'numeric', year: 'numeric' })
}

export function formatDateShort(dateString, locale = 'en-US') {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return '-'
  return date.toLocaleDateString(locale, { month: '2-digit', day: '2-digit', year: '2-digit' })
}

// Always renders the given number of decimals (1234 -> "1,234.00").
// Use for money-like columns where trailing zeros must not be dropped.
export function formatNumberFixed(value, decimals = 2, locale = 'en-US') {
  if (value === null || value === undefined || isNaN(value)) return '0'
  return value.toLocaleString(locale, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined || isNaN(value)) return '-'
  return `${value.toFixed(decimals)}%`
}
