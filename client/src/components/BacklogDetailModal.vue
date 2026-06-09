<template>
  <BaseModal
    :isOpen="isOpen && !!backlogItem"
    title="Inventory Shortage Details"
    @close="close"
  >
    <div class="shortage-header">
      <div class="shortage-icon">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <path d="M24 8L24 28M24 34L24 36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
          <circle cx="24" cy="24" r="18" stroke="currentColor" stroke-width="3"/>
        </svg>
      </div>
      <div class="shortage-title-section">
        <h4 class="item-name">{{ translateProductName(backlogItem.item_name) }}</h4>
        <div class="item-sku">SKU: {{ backlogItem.item_sku }}</div>
      </div>
      <span class="priority-badge" :class="backlogItem.priority">
        {{ backlogItem.priority }} Priority
      </span>
    </div>

    <div class="shortage-summary">
      <div class="summary-card danger">
        <div class="summary-label">Shortage Amount</div>
        <div class="summary-value">{{ shortage }} units</div>
      </div>
      <div class="summary-card warning">
        <div class="summary-label">Days Delayed</div>
        <div class="summary-value">{{ backlogItem.days_delayed }} days</div>
      </div>
    </div>

    <div class="info-grid">
      <div class="info-item">
        <div class="info-label">Order ID</div>
        <div class="info-value order-id">{{ backlogItem.order_id }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">Item SKU</div>
        <div class="info-value sku">{{ backlogItem.item_sku }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">Quantity Needed</div>
        <div class="info-value">{{ backlogItem.quantity_needed }} units</div>
      </div>

      <div class="info-item">
        <div class="info-label">Quantity Available</div>
        <div class="info-value">{{ backlogItem.quantity_available }} units</div>
      </div>

      <div class="info-item">
        <div class="info-label">Expected Date</div>
        <div class="info-value">{{ formatDate(backlogItem.expected_date) }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">Status</div>
        <div class="info-value">
          <span class="badge danger">Backordered</span>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn-secondary" @click="close">Close</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed } from 'vue'
import BaseModal from './BaseModal.vue'
import { useI18n } from '../composables/useI18n'

const { translateProductName } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.shortage-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1.5rem;
}

.shortage-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.shortage-title-section {
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

.priority-badge {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.priority-badge.high {
  background: #fecaca;
  color: #991b1b;
}

.priority-badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.priority-badge.low {
  background: #dbeafe;
  color: #1e40af;
}

.shortage-summary {
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

.summary-card.danger {
  border-color: #fecaca;
  background: #fef2f2;
}

.summary-card.warning {
  border-color: #fed7aa;
  background: #fffbeb;
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

.summary-card.danger .summary-value {
  color: #dc2626;
}

.summary-card.warning .summary-value {
  color: #f59e0b;
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

.info-value.order-id,
.info-value.sku {
  font-family: 'Monaco', 'Courier New', monospace;
  color: var(--color-primary);
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
