<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ mode === 'create' ? 'Create Purchase Order' : 'Purchase Order Details' }}
            </h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <!-- Create mode -->
            <form
              v-if="mode === 'create'"
              id="po-create-form"
              class="po-form"
              @submit.prevent="submitCreate"
            >
              <div class="item-context">
                <div class="context-label">Backlog Item</div>
                <div class="context-value">
                  {{ backlogItem.item_name }}
                  <span class="context-sku">{{ backlogItem.item_sku }}</span>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label" for="po-supplier-name">
                  Supplier Name <span class="required">*</span>
                </label>
                <input
                  id="po-supplier-name"
                  v-model="form.supplier_name"
                  type="text"
                  class="form-input"
                  placeholder="Enter supplier name"
                  required
                />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label" for="po-quantity">
                    Quantity <span class="required">*</span>
                  </label>
                  <input
                    id="po-quantity"
                    v-model.number="form.quantity"
                    type="number"
                    class="form-input"
                    min="1"
                    required
                  />
                </div>
                <div class="form-group">
                  <label class="form-label" for="po-unit-cost">
                    Unit Cost ($) <span class="required">*</span>
                  </label>
                  <input
                    id="po-unit-cost"
                    v-model.number="form.unit_cost"
                    type="number"
                    class="form-input"
                    min="0"
                    step="0.01"
                    required
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label" for="po-delivery-date">
                  Expected Delivery Date <span class="required">*</span>
                </label>
                <input
                  id="po-delivery-date"
                  v-model="form.expected_delivery_date"
                  type="date"
                  class="form-input"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="po-notes">Notes</label>
                <textarea
                  id="po-notes"
                  v-model="form.notes"
                  class="form-input form-textarea"
                  rows="3"
                  placeholder="Optional notes..."
                ></textarea>
              </div>

              <div v-if="submitError" class="inline-error">{{ submitError }}</div>
            </form>

            <!-- View mode -->
            <div v-else>
              <div v-if="fetchLoading" class="state-message">Loading purchase order...</div>
              <div v-else-if="fetchError" class="inline-error">{{ fetchError }}</div>
              <div v-else-if="purchaseOrder" class="po-detail">
                <div class="po-detail-header">
                  <div class="po-id">PO #{{ purchaseOrder.id }}</div>
                  <span class="status-badge" :class="statusClass(purchaseOrder.status)">
                    {{ purchaseOrder.status }}
                  </span>
                </div>

                <div class="info-grid">
                  <div class="info-item">
                    <div class="info-label">Supplier</div>
                    <div class="info-value">{{ purchaseOrder.supplier_name }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Quantity</div>
                    <div class="info-value">{{ purchaseOrder.quantity }} units</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Unit Cost</div>
                    <div class="info-value">${{ Number(purchaseOrder.unit_cost).toFixed(2) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Total Value</div>
                    <div class="info-value total-value">
                      ${{ (purchaseOrder.quantity * purchaseOrder.unit_cost).toFixed(2) }}
                    </div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Expected Delivery</div>
                    <div class="info-value">{{ formatDate(purchaseOrder.expected_delivery_date) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Created Date</div>
                    <div class="info-value">{{ formatDate(purchaseOrder.created_date) }}</div>
                  </div>
                  <div v-if="purchaseOrder.notes" class="info-item info-item-full">
                    <div class="info-label">Notes</div>
                    <div class="info-value">{{ purchaseOrder.notes }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="close">Close</button>
            <button
              v-if="mode === 'create'"
              type="submit"
              form="po-create-form"
              class="btn-primary"
              :disabled="submitLoading"
            >
              {{ submitLoading ? 'Creating...' : 'Create Purchase Order' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '../api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create'
  }
})

const emit = defineEmits(['close', 'po-created'])

// Create mode state
const form = ref({
  supplier_name: '',
  quantity: 0,
  unit_cost: 0,
  expected_delivery_date: '',
  notes: ''
})
const submitLoading = ref(false)
const submitError = ref(null)

// View mode state
const purchaseOrder = ref(null)
const fetchLoading = ref(false)
const fetchError = ref(null)

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return Math.max(0, props.backlogItem.quantity_needed - props.backlogItem.quantity_available)
})

// Initialize state when modal opens
watch(
  () => props.isOpen,
  async (open) => {
    if (!open) return

    if (props.mode === 'create') {
      form.value = {
        supplier_name: '',
        quantity: shortage.value,
        unit_cost: 0,
        expected_delivery_date: '',
        notes: ''
      }
      submitError.value = null
      submitLoading.value = false
    } else if (props.mode === 'view' && props.backlogItem) {
      purchaseOrder.value = null
      fetchError.value = null
      fetchLoading.value = true
      try {
        purchaseOrder.value = await api.getPurchaseOrderByBacklogItem(props.backlogItem.id)
      } catch (err) {
        fetchError.value = 'Failed to load purchase order details.'
        console.error(err)
      } finally {
        fetchLoading.value = false
      }
    }
  }
)

const close = () => {
  emit('close')
}

const submitCreate = async () => {
  if (submitLoading.value) return
  submitLoading.value = true
  submitError.value = null
  try {
    const payload = {
      backlog_item_id: props.backlogItem.id,
      supplier_name: form.value.supplier_name,
      quantity: form.value.quantity,
      unit_cost: form.value.unit_cost,
      expected_delivery_date: form.value.expected_delivery_date
    }
    if (form.value.notes) {
      payload.notes = form.value.notes
    }
    const po = await api.createPurchaseOrder(payload)
    emit('po-created', po)
    emit('close')
  } catch (err) {
    submitError.value = err.response?.data?.detail || 'Failed to create purchase order.'
    console.error(err)
  } finally {
    submitLoading.value = false
  }
}

const statusClass = (status) => {
  if (!status) return 'status-pending'
  switch (status.toLowerCase()) {
    case 'approved': return 'status-approved'
    case 'delivered': return 'status-delivered'
    case 'cancelled': return 'status-cancelled'
    default: return 'status-pending'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: var(--color-bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  max-width: 580px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: var(--space-2);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all 0.15s ease;
}

.close-button:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Create form */
.po-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.item-context {
  padding: var(--space-4);
  background: var(--color-primary-soft);
  border: 1px solid #bfdbfe;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-2);
}

.context-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary);
  margin-bottom: var(--space-1);
}

.context-value {
  font-size: 0.938rem;
  font-weight: 600;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.context-sku {
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.813rem;
  color: var(--color-primary);
  font-weight: 500;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.form-label {
  font-size: 0.813rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.required {
  color: #ef4444;
}

.form-input {
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.938rem;
  color: var(--color-text-primary);
  background: var(--color-bg-surface);
  font-family: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  line-height: 1.5;
}

/* View mode */
.state-message {
  padding: var(--space-8);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.po-detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.po-id {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: 'Monaco', 'Courier New', monospace;
}

.status-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-pending {
  background: #fef9c3;
  color: #854d0e;
}

.status-approved {
  background: #dbeafe;
  color: #1e40af;
}

.status-delivered {
  background: #dcfce7;
  color: #166534;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-5);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.info-item-full {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 0.75rem;
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

.total-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary);
}

/* Inline error */
.inline-error {
  padding: var(--space-3) var(--space-4);
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-sm);
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Footer buttons */
.btn-secondary {
  padding: var(--space-3) var(--space-5);
  background: var(--color-bg-hover);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  padding: var(--space-3) var(--space-5);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.875rem;
  color: white;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
