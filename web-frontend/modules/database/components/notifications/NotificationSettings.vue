<template>
  <Modal @close="$emit('close')">
    <template #header>
      <h2>Notification Settings</h2>
    </template>

    <template #content>
      <div class="notification-settings">
        <div v-if="loading" class="settings-loading">
          <div class="loading-spinner"></div>
          <span>Loading settings...</span>
        </div>

        <div v-else class="settings-content">
          <!-- Workspace Selector -->
          <div class="setting-section">
            <label class="setting-label">Workspace</label>
            <select
              v-model="selectedWorkspaceId"
              class="form-select"
              @change="loadPreferences"
            >
              <option :value="null">Global Settings</option>
              <option
                v-for="workspace in workspaces"
                :key="workspace.id"
                :value="workspace.id"
              >
                {{ workspace.name }}
              </option>
            </select>
          </div>

          <!-- Notification Type Preferences -->
          <div class="setting-section">
            <h3>Notification Types</h3>
            <p class="setting-description">
              Choose which notifications you want to receive and how you want to
              receive them.
            </p>

            <div class="notification-types">
              <div
                v-for="notificationType in notificationTypes"
                :key="notificationType.id"
                class="notification-type-setting"
              >
                <div class="type-header">
                  <h4>{{ getTypeDisplayName(notificationType.name) }}</h4>
                  <span class="type-category">{{
                    notificationType.category
                  }}</span>
                </div>
                <p class="type-description">
                  {{ notificationType.description }}
                </p>

                <div class="delivery-methods">
                  <div
                    v-for="method in notificationType.supported_delivery_methods"
                    :key="method"
                    class="delivery-method"
                  >
                    <label class="checkbox-label">
                      <input
                        type="checkbox"
                        :checked="
                          isMethodEnabled(notificationType.name, method)
                        "
                        @change="
                          updateMethodPreference(
                            notificationType.name,
                            method,
                            $event.target.checked
                          )
                        "
                      />
                      <span class="checkmark"></span>
                      {{ getMethodDisplayName(method) }}
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Email Batching Settings -->
          <div class="setting-section">
            <h3>Email Batching</h3>
            <p class="setting-description">
              Control how often you receive email notifications to avoid spam.
            </p>

            <div class="batching-options">
              <label class="radio-label">
                <input
                  type="radio"
                  value="immediate"
                  v-model="emailBatchFrequency"
                  @change="updateBatchingPreference"
                />
                <span class="radio-mark"></span>
                <div class="radio-content">
                  <strong>Immediate</strong>
                  <span>Send emails right away</span>
                </div>
              </label>

              <label class="radio-label">
                <input
                  type="radio"
                  value="hourly"
                  v-model="emailBatchFrequency"
                  @change="updateBatchingPreference"
                />
                <span class="radio-mark"></span>
                <div class="radio-content">
                  <strong>Hourly</strong>
                  <span>Bundle notifications into hourly emails</span>
                </div>
              </label>

              <label class="radio-label">
                <input
                  type="radio"
                  value="daily"
                  v-model="emailBatchFrequency"
                  @change="updateBatchingPreference"
                />
                <span class="radio-mark"></span>
                <div class="radio-content">
                  <strong>Daily</strong>
                  <span>Send a daily digest at 9 AM</span>
                </div>
              </label>

              <label class="radio-label">
                <input
                  type="radio"
                  value="weekly"
                  v-model="emailBatchFrequency"
                  @change="updateBatchingPreference"
                />
                <span class="radio-mark"></span>
                <div class="radio-content">
                  <strong>Weekly</strong>
                  <span>Send a weekly digest on Mondays</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Quiet Hours -->
          <div class="setting-section">
            <h3>Quiet Hours</h3>
            <p class="setting-description">
              Set quiet hours when you don't want to receive notifications.
            </p>

            <div class="quiet-hours-setting">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="quietHoursEnabled"
                  @change="updateQuietHoursPreference"
                />
                <span class="checkmark"></span>
                Enable quiet hours
              </label>

              <div v-if="quietHoursEnabled" class="quiet-hours-config">
                <div class="time-inputs">
                  <div class="time-input">
                    <label>Start time</label>
                    <input
                      type="time"
                      v-model="quietHoursStart"
                      @change="updateQuietHoursPreference"
                    />
                  </div>
                  <div class="time-input">
                    <label>End time</label>
                    <input
                      type="time"
                      v-model="quietHoursEnd"
                      @change="updateQuietHoursPreference"
                    />
                  </div>
                </div>

                <div class="timezone-input">
                  <label>Timezone</label>
                  <select
                    v-model="quietHoursTimezone"
                    @change="updateQuietHoursPreference"
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                    <option value="Europe/London">London</option>
                    <option value="Europe/Paris">Paris</option>
                    <option value="Asia/Tokyo">Tokyo</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="modal-actions">
        <button
          class="btn btn-outline"
          @click="resetToDefaults"
          :disabled="saving"
        >
          Reset to Defaults
        </button>
        <div class="action-group">
          <button class="btn btn-ghost" @click="$emit('close')">Cancel</button>
          <button
            class="btn btn-primary"
            @click="saveSettings"
            :disabled="saving"
          >
            {{ saving ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </div>
    </template>
  </Modal>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import Modal from '@baserow/modules/core/components/Modal'

export default {
  name: 'NotificationSettings',
  components: {
    Modal,
  },
  data() {
    return {
      loading: true,
      saving: false,
      selectedWorkspaceId: null,
      preferences: {},
      emailBatchFrequency: 'immediate',
      quietHoursEnabled: false,
      quietHoursStart: '22:00',
      quietHoursEnd: '08:00',
      quietHoursTimezone: 'UTC',
    }
  },
  computed: {
    ...mapState('database/notifications', ['notificationTypes']),
    workspaces() {
      return this.$store.getters['workspace/getAll']
    },
  },
  async mounted() {
    await this.loadInitialData()
  },
  methods: {
    ...mapActions('database/notifications', [
      'fetchNotificationTypes',
      'fetchPreferences',
      'updatePreferences',
      'resetPreferencesToDefaults',
    ]),

    async loadInitialData() {
      this.loading = true
      try {
        // Load notification types
        await this.fetchNotificationTypes()

        // Load preferences for current workspace
        await this.loadPreferences()
      } catch (error) {
        this.$toast.error('Failed to load notification settings')
      } finally {
        this.loading = false
      }
    },

    async loadPreferences() {
      try {
        const response = await this.fetchPreferences(this.selectedWorkspaceId)

        // Convert preferences array to object for easier access
        this.preferences = {}
        response.results.forEach((pref) => {
          this.preferences[pref.notification_type_name] = pref
        })

        // Set global settings from first preference (they should be the same)
        const firstPref = response.results[0]
        if (firstPref) {
          this.emailBatchFrequency = firstPref.email_batch_frequency
          this.quietHoursEnabled = firstPref.quiet_hours_enabled
          this.quietHoursStart = firstPref.quiet_hours_start || '22:00'
          this.quietHoursEnd = firstPref.quiet_hours_end || '08:00'
          this.quietHoursTimezone = firstPref.quiet_hours_timezone || 'UTC'
        }
      } catch (error) {
        this.$toast.error('Failed to load preferences')
      }
    },

    isMethodEnabled(typeName, method) {
      const pref = this.preferences[typeName]
      if (!pref) return false

      const methodMap = {
        in_app: 'in_app_enabled',
        email: 'email_enabled',
        webhook: 'webhook_enabled',
        slack: 'slack_enabled',
        teams: 'teams_enabled',
      }

      const field = methodMap[method]
      return field ? pref[field] : false
    },

    updateMethodPreference(typeName, method, enabled) {
      if (!this.preferences[typeName]) {
        this.preferences[typeName] = {}
      }

      const methodMap = {
        in_app: 'in_app_enabled',
        email: 'email_enabled',
        webhook: 'webhook_enabled',
        slack: 'slack_enabled',
        teams: 'teams_enabled',
      }

      const field = methodMap[method]
      if (field) {
        this.preferences[typeName][field] = enabled
      }
    },

    updateBatchingPreference() {
      // Update all preferences with new batching frequency
      Object.keys(this.preferences).forEach((typeName) => {
        this.preferences[typeName].email_batch_frequency =
          this.emailBatchFrequency
      })
    },

    updateQuietHoursPreference() {
      // Update all preferences with quiet hours settings
      Object.keys(this.preferences).forEach((typeName) => {
        this.preferences[typeName].quiet_hours_enabled = this.quietHoursEnabled
        this.preferences[typeName].quiet_hours_start = this.quietHoursStart
        this.preferences[typeName].quiet_hours_end = this.quietHoursEnd
        this.preferences[typeName].quiet_hours_timezone =
          this.quietHoursTimezone
      })
    },

    async saveSettings() {
      this.saving = true
      try {
        await this.updatePreferences({
          preferences: this.preferences,
          workspaceId: this.selectedWorkspaceId,
        })

        this.$emit('updated')
        this.$toast.success('Notification settings saved')
      } catch (error) {
        this.$toast.error('Failed to save settings')
      } finally {
        this.saving = false
      }
    },

    async resetToDefaults() {
      if (
        !confirm(
          'Are you sure you want to reset all notification settings to defaults?'
        )
      ) {
        return
      }

      this.saving = true
      try {
        await this.resetPreferencesToDefaults(this.selectedWorkspaceId)
        await this.loadPreferences()
        this.$toast.success('Settings reset to defaults')
      } catch (error) {
        this.$toast.error('Failed to reset settings')
      } finally {
        this.saving = false
      }
    },

    getTypeDisplayName(typeName) {
      const displayNames = {
        comment_mention: 'Comment Mentions',
        comment_reply: 'Comment Replies',
        row_assigned: 'Row Assignments',
        automation_failed: 'Automation Failures',
        form_submission: 'Form Submissions',
        workspace_invitation: 'Workspace Invitations',
        security_alert: 'Security Alerts',
        digest: 'Activity Digest',
      }

      return displayNames[typeName] || typeName
    },

    getMethodDisplayName(method) {
      const displayNames = {
        in_app: 'In-App',
        email: 'Email',
        webhook: 'Webhook',
        slack: 'Slack',
        teams: 'Microsoft Teams',
      }

      return displayNames[method] || method
    },
  },
}
</script>

<style lang="scss" scoped>
.notification-settings {
  max-width: 600px;
  margin: 0 auto;
}

.settings-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 12px;
  color: var(--color-neutral-600);
}

.setting-section {
  margin-bottom: 32px;

  &:last-child {
    margin-bottom: 0;
  }
}

.setting-label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-neutral-900);
}

.setting-description {
  color: var(--color-neutral-600);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.5;
}

.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-neutral-300);
  border-radius: 4px;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: var(--color-primary-500);
    box-shadow: 0 0 0 3px var(--color-primary-100);
  }
}

.notification-types {
  space-y: 24px;
}

.notification-type-setting {
  padding: 20px;
  border: 1px solid var(--color-neutral-200);
  border-radius: 8px;
  margin-bottom: 16px;
}

.type-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;

  h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--color-neutral-900);
  }
}

.type-category {
  padding: 4px 8px;
  background-color: var(--color-neutral-100);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  color: var(--color-neutral-600);
}

.type-description {
  color: var(--color-neutral-600);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.4;
}

.delivery-methods {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.delivery-method {
  flex: 1;
  min-width: 120px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;

  input[type='checkbox'] {
    display: none;
  }

  .checkmark {
    width: 18px;
    height: 18px;
    border: 2px solid var(--color-neutral-300);
    border-radius: 3px;
    margin-right: 8px;
    position: relative;
    transition: all 0.2s;

    &::after {
      content: '';
      position: absolute;
      left: 5px;
      top: 2px;
      width: 4px;
      height: 8px;
      border: solid white;
      border-width: 0 2px 2px 0;
      transform: rotate(45deg);
      opacity: 0;
      transition: opacity 0.2s;
    }
  }

  input[type='checkbox']:checked + .checkmark {
    background-color: var(--color-primary-500);
    border-color: var(--color-primary-500);

    &::after {
      opacity: 1;
    }
  }
}

.batching-options {
  space-y: 12px;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 12px;
  border: 1px solid var(--color-neutral-200);
  border-radius: 6px;
  margin-bottom: 8px;
  transition: all 0.2s;

  &:hover {
    border-color: var(--color-primary-300);
    background-color: var(--color-primary-25);
  }

  input[type='radio'] {
    display: none;
  }

  input[type='radio']:checked + .radio-mark {
    border-color: var(--color-primary-500);

    &::after {
      opacity: 1;
    }
  }

  input[type='radio']:checked ~ .radio-content {
    color: var(--color-primary-700);
  }
}

.radio-mark {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-neutral-300);
  border-radius: 50%;
  margin-right: 12px;
  position: relative;
  transition: all 0.2s;

  &::after {
    content: '';
    position: absolute;
    left: 4px;
    top: 4px;
    width: 6px;
    height: 6px;
    background-color: var(--color-primary-500);
    border-radius: 50%;
    opacity: 0;
    transition: opacity 0.2s;
  }
}

.radio-content {
  display: flex;
  flex-direction: column;

  strong {
    font-weight: 600;
    margin-bottom: 2px;
  }

  span {
    font-size: 13px;
    color: var(--color-neutral-600);
  }
}

.quiet-hours-setting {
  space-y: 16px;
}

.quiet-hours-config {
  margin-top: 16px;
  padding: 16px;
  background-color: var(--color-neutral-50);
  border-radius: 6px;
}

.time-inputs {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.time-input {
  flex: 1;

  label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    color: var(--color-neutral-700);
  }

  input[type='time'] {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--color-neutral-300);
    border-radius: 4px;
    font-size: 14px;

    &:focus {
      outline: none;
      border-color: var(--color-primary-500);
      box-shadow: 0 0 0 3px var(--color-primary-100);
    }
  }
}

.timezone-input {
  label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    color: var(--color-neutral-700);
  }

  select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--color-neutral-300);
    border-radius: 4px;
    font-size: 14px;

    &:focus {
      outline: none;
      border-color: var(--color-primary-500);
      box-shadow: 0 0 0 3px var(--color-primary-100);
    }
  }
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-group {
  display: flex;
  gap: 12px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-neutral-200);
  border-top: 2px solid var(--color-primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
