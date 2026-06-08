<template>
  <BaseModal
    :isOpen="isOpen && !!inventoryItem"
    title="Inventory Item Details"
    maxWidth="700px"
    @close="close"
  >
    <template #footer>
      <button class="btn-secondary" @click="close">Close</button>
    </template>

    <div class="item-header">
      <div class="item-icon" :class="getStockIconClass()">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <rect x="8" y="12" width="32" height="28" rx="2" stroke="currentColor" stroke-width="2.5"/>
          <path d="M16 8V16M32 8V16M8 20H40" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          <path d="M16 28H32M16 34H24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="item-title-section">
        <h4 class="item-name">{{ translateProductName(inventoryItem.name) }}</h4>
        <div class="item-sku">SKU: {{ inventoryItem.sku }}</div>
      </div>
      <span class="stock-badge" :class="getStockStatusClass()">
        {{ getStockStatus() }}
      </span>
    </div>

    <div class="stock-summary">
      <div class="summary-card primary">
        <div class="summary-label">Quantity on Hand</div>
        <div class="summary-value">{{ inventoryItem.quantity_on_hand }} units</div>
      </div>
      <div class="summary-card" :class="getSummaryCardClass()">
        <div class="summary-label">Stock Level</div>
        <div class="summary-value">{{ stockPercentage }}%</div>
        <div class="summary-subtitle">vs. reorder point</div>
      </div>
    </div>

    <div class="info-grid">
      <div class="info-item">
        <div class="info-label">Category</div>
        <div class="info-value">{{ inventoryItem.category }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">Location</div>
        <div class="info-value">{{ inventoryItem.location }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">Reorder Point</div>
        <div class="info-value">{{ inventoryItem.reorder_point }} units</div>
      </div>

      <div class="info-item">
        <div class="info-label">Units Remaining</div>
        <div class="info-value">
          <span :style="{ color: inventoryItem.quantity_on_hand <= inventoryItem.reorder_point ? '#ef4444' : '#10b981' }">
            {{ inventoryItem.quantity_on_hand - inventoryItem.reorder_point }} units
          </span>
        </div>
      </div>

      <div class="info-item">
        <div class="info-label">Unit Cost</div>
        <div class="info-value">{{ currencySymbol }}{{ inventoryItem.unit_cost.toFixed(2) }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">Total Value</div>
        <div class="info-value total-value">
          {{ currencySymbol }}{{ totalValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
        </div>
      </div>

      <div class="info-item">
        <div class="info-label">Warehouse</div>
        <div class="info-value">{{ translateWarehouse(inventoryItem.location) }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">Status</div>
        <div class="info-value">
          <span :class="['badge', getStockStatusClass()]">
            {{ getStockStatus() }}
          </span>
        </div>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import BaseModal from './BaseModal.vue'

const { currentCurrency, translateProductName, translateWarehouse } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  inventoryItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalValue = computed(() => {
  if (!props.inventoryItem) return 0
  return props.inventoryItem.quantity_on_hand * props.inventoryItem.unit_cost
})

const stockPercentage = computed(() => {
  if (!props.inventoryItem || props.inventoryItem.reorder_point === 0) return 0
  return Math.round((props.inventoryItem.quantity_on_hand / props.inventoryItem.reorder_point) * 100)
})

const close = () => {
  emit('close')
}

const getStockStatus = () => {
  if (!props.inventoryItem) return 'Unknown'
  if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point) {
    return 'Low Stock'
  } else if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point * 1.5) {
    return 'Adequate'
  } else {
    return 'In Stock'
  }
}

const getStockStatusClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger'
  if (status === 'Adequate') return 'warning'
  return 'success'
}

const getStockIconClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger-icon'
  if (status === 'Adequate') return 'warning-icon'
  return 'success-icon'
}

const getSummaryCardClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger-card'
  if (status === 'Adequate') return 'warning-card'
  return 'success-card'
}
</script>

<style scoped>
.item-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1.5rem;
}

.item-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.item-icon.success-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.item-icon.warning-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.item-icon.danger-icon {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.item-title-section {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.item-sku {
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

.stock-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-card {
  padding: 1.25rem;
  border-radius: 10px;
  border: 2px solid;
}

.summary-card.primary {
  border-color: #bfdbfe;
  background: var(--color-primary-soft);
}

.summary-card.success-card {
  border-color: #a7f3d0;
  background: #d1fae5;
}

.summary-card.warning-card {
  border-color: #fed7aa;
  background: #fffbeb;
}

.summary-card.danger-card {
  border-color: #fecaca;
  background: #fef2f2;
}

.summary-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.summary-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.summary-subtitle {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
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

.info-value.total-value {
  font-size: 1.125rem;
  color: var(--color-primary);
  font-weight: 700;
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
