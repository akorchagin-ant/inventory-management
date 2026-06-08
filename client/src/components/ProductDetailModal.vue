<template>
  <BaseModal
    :is-open="isOpen && !!product"
    title="Product Details"
    @close="emit('close')"
  >
    <div v-if="product">
      <div class="product-header">
        <div class="product-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect x="8" y="12" width="32" height="28" rx="2" stroke="currentColor" stroke-width="2.5"/>
            <path d="M16 8V16M32 8V16M8 20H40" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="product-title-section">
          <h4 class="product-name">{{ product.name }}</h4>
          <div class="product-sku">SKU: {{ product.sku }}</div>
        </div>
        <span class="stock-badge" :class="getStockBadgeClass(product.stockLevel)">
          {{ product.stockLevel }}
        </span>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">Category</div>
          <div class="info-value">{{ product.category }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">Warehouse</div>
          <div class="info-value">{{ product.warehouse }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">Units Ordered</div>
          <div class="info-value">{{ product.unitsOrdered }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">Total Revenue</div>
          <div class="info-value">{{ currencySymbol }}{{ product.revenue.toLocaleString() }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">Current Stock</div>
          <div class="info-value">{{ product.quantityOnHand }} units</div>
        </div>

        <div class="info-item">
          <div class="info-label">Reorder Point</div>
          <div class="info-value">{{ product.reorderPoint }} units</div>
        </div>

        <div class="info-item">
          <div class="info-label">First Order Date</div>
          <div class="info-value">{{ formatDate(product.firstOrderDate) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">Stock Status</div>
          <div class="info-value">
            <span :class="['badge', getStockBadgeClass(product.stockLevel)]">
              {{ product.stockLevel }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn-secondary" @click="emit('close')">Close</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from './BaseModal.vue'
import { useI18n } from '../composables/useI18n'

const { currentCurrency } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

// Not replaced by utils/format.js formatDate: local returns 'N/A' for falsy
// and uses month:'long' ("January 2, 2025") vs shared '-' and month:'short'
// ("Jan 2, 2025") — outputs differ so byte-identity requirement is not met.
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getStockBadgeClass = (stockLevel) => {
  if (stockLevel === 'In Stock') return 'success'
  if (stockLevel === 'Low Stock') return 'warning'
  if (stockLevel === 'Out of Stock') return 'danger'
  return 'info'
}
</script>

<style scoped>
.product-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 2rem;
}

.product-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #3b82f6 0%, var(--color-primary) 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.product-title-section {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.product-sku {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  font-family: 'Monaco', 'Courier New', monospace;
}

.stock-badge {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.stock-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.stock-badge.warning {
  background: #fed7aa;
  color: #92400e;
}

.stock-badge.danger {
  background: #fecaca;
  color: #991b1b;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
}

.info-value {
  font-size: 0.938rem;
  color: var(--color-text-primary);
  font-weight: 500;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: var(--color-bg-hover);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: var(--color-border);
  border-color: #cbd5e1;
}
</style>
