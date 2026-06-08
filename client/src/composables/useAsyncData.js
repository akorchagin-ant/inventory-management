import { ref, onMounted, watch } from 'vue'

/**
 * Shared fetch lifecycle: loading/error state, initial load on mount,
 * and reload when watched sources (typically filter refs) change.
 *
 * The fetch function assigns results to the caller's own refs and may hit
 * several endpoints (Promise.all) — this composable only owns the lifecycle,
 * not the data, so multi-endpoint views work without special casing.
 *
 * @param {Function} fetchFn async function that loads data into caller refs
 * @param {Object} options
 * @param {Array}  options.watchSources reactive sources that trigger a reload
 * @param {String} options.errorMessage message prefix shown on failure
 * @param {Boolean} options.immediate load on mount (default true)
 */
export function useAsyncData(fetchFn, { watchSources = [], errorMessage = 'Failed to load data', immediate = true } = {}) {
  const loading = ref(true)
  const error = ref(null)

  const load = async () => {
    try {
      loading.value = true
      error.value = null
      await fetchFn()
    } catch (err) {
      error.value = `${errorMessage}: ${err.message}`
      console.error(errorMessage, err)
    } finally {
      loading.value = false
    }
  }

  if (immediate) {
    onMounted(load)
  }
  if (watchSources.length) {
    watch(watchSources, load)
  }

  return { loading, error, load }
}
