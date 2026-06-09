<template>
  <BaseModal
    :is-open="isOpen"
    :title="t('profileDetails.title')"
    max-width="600px"
    @close="$emit('close')"
  >
    <div class="profile-section">
      <div class="avatar-section">
        <div class="avatar-xl">
          {{ getInitials(currentUser.name) }}
        </div>
        <h4 class="profile-name">{{ currentUser.name }}</h4>
        <p class="profile-job-title">{{ currentUser.jobTitle }}</p>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.email') }}</div>
          <div class="info-value">{{ currentUser.email }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.department') }}</div>
          <div class="info-value">{{ currentUser.department }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.location') }}</div>
          <div class="info-value">{{ currentUser.location }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.phone') }}</div>
          <div class="info-value">{{ currentUser.phone }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.joinDate') }}</div>
          <div class="info-value">{{ formatDate(currentUser.joinDate) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">{{ t('profileDetails.employeeId') }}</div>
          <div class="info-value">CC-{{ currentUser.id.toString().padStart(5, '0') }}</div>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn-secondary" @click="$emit('close')">{{ t('profileDetails.close') }}</button>
    </template>
  </BaseModal>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'
import BaseModal from './BaseModal.vue'

const { currentUser, getInitials } = useAuth()
const { t, currentLocale } = useI18n()

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
  return date.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.profile-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.avatar-xl {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 2rem;
  letter-spacing: 0.025em;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.profile-job-title {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
