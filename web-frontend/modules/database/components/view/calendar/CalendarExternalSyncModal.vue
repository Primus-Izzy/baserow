<template>
  <Modal @close="$emit('close')">
    <template #header>
      <h2 class="modal__title">
        {{ $t('calendarView.externalSync') }}
      </h2>
    </template>

    <template #content>
      <div class="external-sync-modal">
        <!-- Existing sync configurations -->
        <div
          v-if="syncConfigs.length > 0"
          class="external-sync-modal__existing"
        >
          <h3>{{ $t('calendarView.existingSyncs') }}</h3>

          <div class="external-sync-modal__sync-list">
            <div
              v-for="config in syncConfigs"
              :key="config.id"
              class="external-sync-modal__sync-item"
            >
              <div class="external-sync-modal__sync-info">
                <div class="external-sync-modal__sync-provider">
                  <i :class="getProviderIcon(config.provider)"></i>
                  {{ getProviderLabel(config.provider) }}
                </div>
                <div class="external-sync-modal__sync-details">
                  <span class="external-sync-modal__sync-calendar">
                    {{ config.external_calendar_id }}
                  </span>
                  <span class="external-sync-modal__sync-direction">
                    {{ getSyncDirectionLabel(config.sync_direction) }}
                  </span>
                </div>
                <div
                  v-if="config.last_sync"
                  class="external-sync-modal__sync-last"
                >
                  {{ $t('calendarView.lastSync') }}:
                  {{ formatDate(config.last_sync) }}
                </div>
              </div>

              <div class="external-sync-modal__sync-actions">
                <button
                  class="button button--small"
                  @click="triggerSync(config.id)"
                  :disabled="syncing"
                >
                  <i class="iconoir-refresh" :class="{ rotating: syncing }"></i>
                  {{ $t('calendarView.syncNow') }}
                </button>

                <SwitchInput
                  :value="config.is_active"
                  @input="toggleSync(config.id, $event)"
                  :disabled="updating"
                />

                <button
                  class="button button--small button--error"
                  @click="deleteSync(config.id)"
                  :disabled="updating"
                >
                  <i class="iconoir-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Add new sync configuration -->
        <div class="external-sync-modal__add-new">
          <h3>{{ $t('calendarView.addNewSync') }}</h3>

          <form
            @submit.prevent="addSyncConfig"
            class="external-sync-modal__form"
          >
            <!-- Provider selection -->
            <div class="external-sync-modal__field">
              <label class="external-sync-modal__label">
                {{ $t('calendarView.provider') }}
              </label>
              <Dropdown
                v-model="newSync.provider"
                :show-search="false"
                class="external-sync-modal__dropdown"
              >
                <template #value>
                  <div v-if="newSync.provider">
                    <i :class="getProviderIcon(newSync.provider)"></i>
                    {{ getProviderLabel(newSync.provider) }}
                  </div>
                  <div v-else class="external-sync-modal__placeholder">
                    {{ $t('calendarView.selectProvider') }}
                  </div>
                </template>
                <DropdownItem
                  v-for="provider in availableProviders"
                  :key="provider.value"
                  :name="provider.label"
                  :value="provider.value"
                  :icon="provider.icon"
                />
              </Dropdown>
            </div>

            <!-- Calendar ID -->
            <div class="external-sync-modal__field">
              <label class="external-sync-modal__label">
                {{ $t('calendarView.calendarId') }}
              </label>
              <input
                v-model="newSync.external_calendar_id"
                type="text"
                class="input external-sync-modal__input"
                :placeholder="$t('calendarView.calendarIdPlaceholder')"
                required
              />
            </div>

            <!-- Sync direction -->
            <div class="external-sync-modal__field">
              <label class="external-sync-modal__label">
                {{ $t('calendarView.syncDirection') }}
              </label>
              <Dropdown
                v-model="newSync.sync_direction"
                :show-search="false"
                class="external-sync-modal__dropdown"
              >
                <template #value>
                  {{ getSyncDirectionLabel(newSync.sync_direction) }}
                </template>
                <DropdownItem
                  v-for="direction in syncDirections"
                  :key="direction.value"
                  :name="direction.label"
                  :value="direction.value"
                />
              </Dropdown>
            </div>

            <!-- Submit button -->
            <div class="external-sync-modal__actions">
              <button
                type="submit"
                class="button button--primary"
                :disabled="!canAddSync || adding"
              >
                <i v-if="adding" class="iconoir-refresh rotating"></i>
                {{ $t('calendarView.addSync') }}
              </button>
            </div>
          </form>
        </div>

        <!-- OAuth instructions -->
        <div class="external-sync-modal__instructions">
          <h4>{{ $t('calendarView.setupInstructions') }}</h4>
          <div class="external-sync-modal__instruction-content">
            <p>{{ $t('calendarView.oauthInstructions') }}</p>
            <ol>
              <li>{{ $t('calendarView.step1') }}</li>
              <li>{{ $t('calendarView.step2') }}</li>
              <li>{{ $t('calendarView.step3') }}</li>
            </ol>
          </div>
        </div>
      </div>
    </template>
  </Modal>
</template>

<script>
import Modal from '@baserow/modules/core/components/Modal'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'CalendarExternalSyncModal',
  components: {
    Modal,
  },
  props: {
    view: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      syncConfigs: [],
      newSync: {
        provider: '',
        external_calendar_id: '',
        sync_direction: 'bidirectional',
      },
      syncing: false,
      updating: false,
      adding: false,
      availableProviders: [
        {
          value: 'google',
          label: 'Google Calendar',
          icon: 'iconoir-google',
        },
        {
          value: 'outlook',
          label: 'Microsoft Outlook',
          icon: 'iconoir-microsoft',
        },
        {
          value: 'apple',
          label: 'Apple Calendar',
          icon: 'iconoir-apple',
        },
      ],
      syncDirections: [
        {
          value: 'import',
          label: this.$t('calendarView.importOnly'),
        },
        {
          value: 'export',
          label: this.$t('calendarView.exportOnly'),
        },
        {
          value: 'bidirectional',
          label: this.$t('calendarView.bidirectional'),
        },
      ],
    }
  },
  computed: {
    canAddSync() {
      return this.newSync.provider && this.newSync.external_calendar_id.trim()
    },
  },
  async mounted() {
    await this.fetchSyncConfigs()
  },
  methods: {
    async fetchSyncConfigs() {
      try {
        // This would fetch from the API
        // For now, using mock data
        this.syncConfigs = []
      } catch (error) {
        notifyIf(error, 'view')
      }
    },

    getProviderIcon(provider) {
      const icons = {
        google: 'iconoir-google',
        outlook: 'iconoir-microsoft',
        apple: 'iconoir-apple',
      }
      return icons[provider] || 'iconoir-calendar'
    },

    getProviderLabel(provider) {
      const labels = {
        google: 'Google Calendar',
        outlook: 'Microsoft Outlook',
        apple: 'Apple Calendar',
      }
      return labels[provider] || provider
    },

    getSyncDirectionLabel(direction) {
      const labels = {
        import: this.$t('calendarView.importOnly'),
        export: this.$t('calendarView.exportOnly'),
        bidirectional: this.$t('calendarView.bidirectional'),
      }
      return labels[direction] || direction
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },

    async addSyncConfig() {
      if (!this.canAddSync) return

      this.adding = true
      try {
        // This would call the API to create the sync config
        const newConfig = {
          id: Date.now(), // Mock ID
          ...this.newSync,
          is_active: true,
          last_sync: null,
        }

        this.syncConfigs.push(newConfig)

        // Reset form
        this.newSync = {
          provider: '',
          external_calendar_id: '',
          sync_direction: 'bidirectional',
        }

        this.$emit('updated')
      } catch (error) {
        notifyIf(error, 'view')
      } finally {
        this.adding = false
      }
    },

    async triggerSync(syncId) {
      this.syncing = true
      try {
        // This would call the API to trigger sync
        const config = this.syncConfigs.find((c) => c.id === syncId)
        if (config) {
          config.last_sync = new Date().toISOString()
        }

        this.$emit('updated')
      } catch (error) {
        notifyIf(error, 'view')
      } finally {
        this.syncing = false
      }
    },

    async toggleSync(syncId, isActive) {
      this.updating = true
      try {
        // This would call the API to update the sync config
        const config = this.syncConfigs.find((c) => c.id === syncId)
        if (config) {
          config.is_active = isActive
        }

        this.$emit('updated')
      } catch (error) {
        notifyIf(error, 'view')
      } finally {
        this.updating = false
      }
    },

    async deleteSync(syncId) {
      if (!confirm(this.$t('calendarView.confirmDeleteSync'))) {
        return
      }

      this.updating = true
      try {
        // This would call the API to delete the sync config
        this.syncConfigs = this.syncConfigs.filter((c) => c.id !== syncId)

        this.$emit('updated')
      } catch (error) {
        notifyIf(error, 'view')
      } finally {
        this.updating = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.external-sync-modal {
  padding: 20px;
  max-width: 600px;

  &__existing {
    margin-bottom: 32px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: $color-neutral-800;
      margin-bottom: 16px;
    }
  }

  &__sync-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  &__sync-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    border: 1px solid $color-neutral-200;
    border-radius: 6px;
    background-color: $color-neutral-25;
  }

  &__sync-info {
    flex: 1;
  }

  &__sync-provider {
    font-weight: 600;
    color: $color-neutral-800;
    margin-bottom: 4px;

    i {
      margin-right: 8px;
    }
  }

  &__sync-details {
    font-size: 14px;
    color: $color-neutral-600;
    margin-bottom: 4px;
  }

  &__sync-calendar {
    margin-right: 12px;
  }

  &__sync-direction {
    font-style: italic;
  }

  &__sync-last {
    font-size: 12px;
    color: $color-neutral-500;
  }

  &__sync-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  &__add-new {
    margin-bottom: 32px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: $color-neutral-800;
      margin-bottom: 16px;
    }
  }

  &__form {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  &__field {
    display: flex;
    flex-direction: column;
  }

  &__label {
    font-size: 14px;
    font-weight: 600;
    color: $color-neutral-700;
    margin-bottom: 6px;
  }

  &__input {
    width: 100%;
  }

  &__dropdown {
    width: 100%;
  }

  &__placeholder {
    color: $color-neutral-400;
    font-style: italic;
  }

  &__actions {
    display: flex;
    justify-content: flex-end;
  }

  &__instructions {
    border-top: 1px solid $color-neutral-200;
    padding-top: 20px;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: $color-neutral-800;
      margin-bottom: 12px;
    }
  }

  &__instruction-content {
    font-size: 14px;
    color: $color-neutral-700;
    line-height: 1.5;

    p {
      margin-bottom: 12px;
    }

    ol {
      margin-left: 20px;

      li {
        margin-bottom: 8px;
      }
    }
  }
}

.rotating {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .external-sync-modal {
    padding: 16px;

    &__sync-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    &__sync-actions {
      width: 100%;
      justify-content: space-between;
    }
  }
}
</style>
