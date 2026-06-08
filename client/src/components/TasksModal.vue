<template>
  <BaseModal
    :isOpen="isOpen"
    :title="t('tasks.title')"
    maxWidth="900px"
    @close="close"
  >
    <!-- Add Task Form -->
    <div class="task-form">
      <div class="form-row">
        <div class="form-group flex-1">
          <label for="task-title">{{ t('tasks.taskTitle') }}</label>
          <input
            id="task-title"
            v-model="newTask.title"
            type="text"
            :placeholder="t('tasks.taskTitlePlaceholder')"
            class="task-input"
            @keyup.enter="handleAddTask"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="task-priority">{{ t('tasks.priority') }}</label>
          <select
            id="task-priority"
            v-model="newTask.priority"
            class="task-select"
          >
            <option value="high">{{ t('priority.high') }}</option>
            <option value="medium">{{ t('priority.medium') }}</option>
            <option value="low">{{ t('priority.low') }}</option>
          </select>
        </div>

        <div class="form-group">
          <label for="task-due-date">{{ t('tasks.dueDate') }}</label>
          <input
            id="task-due-date"
            v-model="newTask.dueDate"
            type="date"
            class="task-input"
          />
        </div>

        <div class="form-group-btn">
          <button @click="handleAddTask" class="task-add-btn" :disabled="!newTask.title.trim() || !newTask.dueDate">
            {{ t('tasks.addTask') }}
          </button>
        </div>
      </div>
    </div>

    <div class="tasks-divider"></div>

    <!-- Tasks List -->
    <div v-if="sortedTasks.length === 0" class="no-tasks">
      {{ t('tasks.noTasks') }}
    </div>

    <div v-else class="tasks-list">
      <div
        v-for="task in sortedTasks"
        :key="task.id"
        class="task-item"
        :class="[`priority-${task.priority}`, { completed: task.status === 'completed' }]"
      >
        <div class="task-header">
          <div class="task-check-title">
            <input
              type="checkbox"
              :checked="task.status === 'completed'"
              @change="$emit('toggle-task', task.id)"
              class="task-checkbox"
            />
            <span class="task-title" @click="$emit('toggle-task', task.id)">{{ task.title }}</span>
          </div>
          <button @click="$emit('delete-task', task.id)" class="task-delete-btn" title="Delete task">
            ×
          </button>
        </div>

        <div class="task-footer">
          <span class="priority-badge" :class="task.priority">
            {{ translatePriority(task.priority) }}
          </span>
          <div class="task-due-date">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <rect x="2" y="3" width="10" height="9" rx="1" stroke="currentColor" stroke-width="1.2"/>
              <path d="M4.5 1.5V4.5M9.5 1.5V4.5M2 6H12" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
            {{ formatDueDate(task.dueDate) }}
          </div>
          <span class="status-badge" :class="getStatusClass(task.dueDate, task.status)">
            {{ getStatusText(task.dueDate, task.status) }}
          </span>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn-secondary" @click="close">{{ t('profileDetails.close') }}</button>
    </template>
  </BaseModal>
</template>

<script>
import { ref, computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import BaseModal from './BaseModal.vue'

export default {
  name: 'TasksModal',
  components: { BaseModal },
  props: {
    isOpen: {
      type: Boolean,
      required: true
    },
    tasks: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'add-task', 'delete-task', 'toggle-task'],
  setup(props, { emit }) {
    const { t, currentLocale } = useI18n()
    const newTask = ref({
      title: '',
      priority: 'medium',
      dueDate: ''
    })

    const sortedTasks = computed(() => {
      // Don't sort - just return tasks in their current order (newest first)
      return [...props.tasks]
    })

    const close = () => {
      emit('close')
    }

    const handleAddTask = () => {
      if (newTask.value.title.trim() && newTask.value.dueDate) {
        emit('add-task', {
          title: newTask.value.title.trim(),
          priority: newTask.value.priority,
          dueDate: newTask.value.dueDate
        })
        newTask.value = {
          title: '',
          priority: 'medium',
          dueDate: ''
        }
      }
    }

    const formatDueDate = (dateString) => {
      const date = new Date(dateString)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const dueDate = new Date(date)
      dueDate.setHours(0, 0, 0, 0)

      const diffTime = dueDate - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

      const isJapanese = currentLocale.value === 'ja'

      if (diffDays === 0) return isJapanese ? '今日' : 'today'
      if (diffDays === 1) return isJapanese ? '明日' : 'tomorrow'
      if (diffDays === -1) return isJapanese ? '昨日' : 'yesterday'
      if (diffDays < 0) return isJapanese ? `${Math.abs(diffDays)}日前` : `${Math.abs(diffDays)} days ago`
      if (diffDays < 7) return isJapanese ? `${diffDays}日後` : `in ${diffDays} days`

      const locale = isJapanese ? 'ja-JP' : 'en-US'
      return date.toLocaleDateString(locale, {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
      })
    }

    const getStatusClass = (dueDate, status) => {
      if (status === 'completed') return 'completed'

      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const due = new Date(dueDate)
      due.setHours(0, 0, 0, 0)

      const diffTime = due - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

      if (diffDays < 0) return 'overdue'
      if (diffDays <= 1) return 'urgent'
      return 'upcoming'
    }

    const getStatusText = (dueDate, status) => {
      const isJapanese = currentLocale.value === 'ja'

      if (status === 'completed') return isJapanese ? '完了' : 'Completed'

      const statusClass = getStatusClass(dueDate, status)
      if (statusClass === 'overdue') return isJapanese ? '期限超過' : 'Overdue'
      if (statusClass === 'urgent') return isJapanese ? 'もうすぐ期限' : 'Due Soon'
      return isJapanese ? '予定' : 'Upcoming'
    }

    const translatePriority = (priority) => {
      const priorityMap = {
        'high': t('priority.high'),
        'medium': t('priority.medium'),
        'low': t('priority.low')
      }
      return priorityMap[priority] || priority
    }

    return {
      t,
      newTask,
      sortedTasks,
      close,
      handleAddTask,
      formatDueDate,
      getStatusClass,
      getStatusText,
      translatePriority
    }
  }
}
</script>

<style scoped>
.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: var(--color-bg-hover);
  color: #475569;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--color-border);
}

/* Task Form */
.task-form {
  background: var(--color-bg-page);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.form-group.flex-1 {
  flex: 1;
}

.form-group-btn {
  display: flex;
  align-items: flex-end;
}

label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.task-input,
.task-select {
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s ease;
  font-family: inherit;
}

.task-input:focus,
.task-select:focus {
  outline: none;
  border-color: #667eea;
}

.task-select {
  cursor: pointer;
  background: white;
}

.task-add-btn {
  padding: 0.75rem 1.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
  white-space: nowrap;
  height: fit-content;
}

.task-add-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.task-add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tasks-divider {
  height: 1px;
  background: var(--color-border);
  margin: 2rem 0;
}

.no-tasks {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-secondary);
  font-size: 1.1rem;
  font-style: italic;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.task-item {
  background: white;
  border: 2px solid var(--color-border);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  transition: all 0.2s ease;
}

.task-item:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.task-item.priority-high {
  border-left: 4px solid #dc2626;
}

.task-item.priority-medium {
  border-left: 4px solid #f59e0b;
}

.task-item.priority-low {
  border-left: 4px solid var(--color-primary);
}

.task-item.completed {
  opacity: 0.6;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.task-check-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.task-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #667eea;
  flex-shrink: 0;
}

.task-title {
  flex: 1;
  cursor: pointer;
  user-select: none;
  color: var(--color-text-primary);
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
}

.task-item.completed .task-title {
  text-decoration: line-through;
  color: #94a3b8;
}

.task-delete-btn {
  width: 28px;
  height: 28px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
}

.task-delete-btn:hover {
  background: #dc2626;
  transform: scale(1.1);
}

.task-footer {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.priority-badge {
  font-size: 0.688rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  letter-spacing: 0.025em;
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

.task-due-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.813rem;
  color: var(--color-text-secondary);
}

.task-due-date svg {
  color: #94a3b8;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  margin-left: auto;
}

.status-badge.overdue {
  background: #fecaca;
  color: #991b1b;
}

.status-badge.urgent {
  background: #fed7aa;
  color: #92400e;
}

.status-badge.upcoming {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}
</style>
