<template>
  <Modal
    ref="modal"
    :title="$t('dashboardExport.title')"
    :loading="loading"
    @hidden="$emit('hidden')"
  >
    <div class="dashboard-export-modal">
      <!-- Export Options -->
      <div class="export-options">
        <h3>{{ $t('dashboardExport.exportOptions') }}</h3>

        <div class="form-group">
          <label>{{ $t('dashboardExport.format') }}</label>
          <select v-model="exportConfig.format" class="form-control">
            <option value="pdf">{{ $t('dashboardExport.formatPdf') }}</option>
            <option value="png">{{ $t('dashboardExport.formatPng') }}</option>
            <option value="csv">{{ $t('dashboardExport.formatCsv') }}</option>
          </select>
        </div>

        <div v-if="exportConfig.format === 'pdf'" class="pdf-options">
          <div class="form-group">
            <label>{{ $t('dashboardExport.pageSize') }}</label>
            <select
              v-model="exportConfig.configuration.pageSize"
              class="form-control"
            >
              <option value="A4">A4</option>
              <option value="A3">A3</option>
              <option value="Letter">Letter</option>
            </select>
          </div>

          <div class="form-group">
            <label>{{ $t('dashboardExport.orientation') }}</label>
            <select
              v-model="exportConfig.configuration.orientation"
              class="form-control"
            >
              <option value="portrait">
                {{ $t('dashboardExport.portrait') }}
              </option>
              <option value="landscape">
                {{ $t('dashboardExport.landscape') }}
              </option>
            </select>
          </div>
        </div>

        <div v-if="exportConfig.format === 'png'" class="png-options">
          <div class="form-group">
            <label>{{ $t('dashboardExport.resolution') }}</label>
            <select
              v-model="exportConfig.configuration.resolution"
              class="form-control"
            >
              <option value="1x">
                {{ $t('dashboardExport.resolution1x') }}
              </option>
              <option value="2x">
                {{ $t('dashboardExport.resolution2x') }}
              </option>
              <option value="3x">
                {{ $t('dashboardExport.resolution3x') }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>
            <input v-model="exportConfig.includeTitle" type="checkbox" />
            {{ $t('dashboardExport.includeTitle') }}
          </label>
        </div>

        <div class="form-group">
          <label>
            <input v-model="exportConfig.includeTimestamp" type="checkbox" />
            {{ $t('dashboardExport.includeTimestamp') }}
          </label>
        </div>
      </div>

      <!-- Delivery Options -->
      <div class="delivery-options">
        <h3>{{ $t('dashboardExport.deliveryOptions') }}</h3>

        <div class="form-group">
          <label>
            <input v-model="exportConfig.sendEmail" type="checkbox" />
            {{ $t('dashboardExport.sendEmail') }}
          </label>
        </div>

        <div v-if="exportConfig.sendEmail" class="form-group">
          <label>{{ $t('dashboardExport.emailAddress') }}</label>
          <input
            v-model="exportConfig.deliveryEmail"
            type="email"
            class="form-control"
            :placeholder="$t('dashboardExport.emailPlaceholder')"
          />
        </div>
      </div>

      <!-- Scheduling Options -->
      <div class="scheduling-options">
        <h3>{{ $t('dashboardExport.schedulingOptions') }}</h3>

        <div class="form-group">
          <label>
            <input v-model="exportConfig.isScheduled" type="checkbox" />
            {{ $t('dashboardExport.scheduleExport') }}
          </label>
        </div>

        <div v-if="exportConfig.isScheduled" class="schedule-config">
          <div class="form-group">
            <label>{{ $t('dashboardExport.frequency') }}</label>
            <select v-model="exportConfig.scheduleType" class="form-control">
              <option value="daily">{{ $t('dashboardExport.daily') }}</option>
              <option value="weekly">{{ $t('dashboardExport.weekly') }}</option>
              <option value="monthly">
                {{ $t('dashboardExport.monthly') }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>{{ $t('dashboardExport.deliveryEmailRequired') }}</label>
            <input
              v-model="exportConfig.deliveryEmail"
              type="email"
              class="form-control"
              :placeholder="$t('dashboardExport.emailPlaceholder')"
              required
            />
          </div>
        </div>
      </div>

      <!-- Export History -->
      <div class="export-history">
        <h3>{{ $t('dashboardExport.exportHistory') }}</h3>

        <div v-if="exports.length === 0" class="no-exports">
          <p class="text-muted">{{ $t('dashboardExport.noExports') }}</p>
        </div>

        <div v-else class="exports-list">
          <div
            v-for="exportJob in exports"
            :key="exportJob.id"
            class="export-item"
            :class="{ 'export-failed': exportJob.status === 'failed' }"
          >
            <div class="export-info">
              <div class="export-format">
                <i :class="getFormatIcon(exportJob.export_format)"></i>
                <span>{{ exportJob.export_format.toUpperCase() }}</span>
              </div>
              <div class="export-details">
                <div class="export-date">
                  {{ formatDate(exportJob.created_at) }}
                </div>
                <div class="export-status">
                  <span :class="`status-${exportJob.status}`">
                    {{ $t(`dashboardExport.status.${exportJob.status}`) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="export-actions">
              <button
                v-if="exportJob.status === 'completed'"
                class="btn btn-sm btn-primary"
                @click="downloadExport(exportJob.id)"
              >
                <i class="fas fa-download"></i>
                {{ $t('dashboardExport.download') }}
              </button>

              <button
                v-if="
                  exportJob.status === 'pending' ||
                  exportJob.status === 'processing'
                "
                class="btn btn-sm btn-secondary"
                @click="cancelExport(exportJob.id)"
              >
                <i class="fas fa-times"></i>
                {{ $t('dashboardExport.cancel') }}
              </button>

              <button
                class="btn btn-sm btn-outline-danger"
                @click="deleteExport(exportJob.id)"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn btn-secondary" @click="hide">
        {{ $t('action.cancel') }}
      </button>
      <button
        class="btn btn-primary"
        :disabled="loading || !isValidConfig"
        @click="startExport"
      >
        <i class="fas fa-download"></i>
        {{
          exportConfig.isScheduled
            ? $t('dashboardExport.scheduleExport')
            : $t('dashboardExport.startExport')
        }}
      </button>
    </template>
  </Modal>
</template>

<script>
import Modal from '@baserow/modules/core/components/Modal'
import { notifyIf } from '@baserow/modules/core/utils/error'

export default {
  name: 'DashboardExportModal',
  components: {
    Modal,
  },
  props: {
    dashboard: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      loading: false,
      exports: [],
      exportConfig: {
        format: 'pdf',
        configuration: {
          pageSize: 'A4',
          orientation: 'landscape',
          resolution: '2x',
        },
        includeTitle: true,
        includeTimestamp: true,
        sendEmail: false,
        deliveryEmail: '',
        isScheduled: false,
        scheduleType: 'daily',
      },
    }
  },
  computed: {
    isValidConfig() {
      if (this.exportConfig.isScheduled && !this.exportConfig.deliveryEmail) {
        return false
      }
      if (this.exportConfig.sendEmail && !this.exportConfig.deliveryEmail) {
        return false
      }
      return true
    },
  },
  async mounted() {
    await this.loadExports()
  },
  methods: {
    show() {
      this.$refs.modal.show()
    },
    hide() {
      this.$refs.modal.hide()
    },
    async loadExports() {
      try {
        this.loading = true
        const { data } = await this.$client.get(
          `/dashboard/exports/dashboards/${this.dashboard.id}/exports/`
        )
        this.exports = data.exports
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async startExport() {
      try {
        this.loading = true

        const payload = {
          export_format: this.exportConfig.format,
          configuration: {
            ...this.exportConfig.configuration,
            include_title: this.exportConfig.includeTitle,
            include_timestamp: this.exportConfig.includeTimestamp,
          },
        }

        if (this.exportConfig.sendEmail || this.exportConfig.isScheduled) {
          payload.delivery_email = this.exportConfig.deliveryEmail
        }

        if (this.exportConfig.isScheduled) {
          payload.schedule_config = {
            type: this.exportConfig.scheduleType,
          }
        }

        const { data } = await this.$client.post(
          `/dashboard/exports/dashboards/${this.dashboard.id}/create_export/`,
          payload
        )

        await this.loadExports()

        if (this.exportConfig.isScheduled) {
          this.$toast.success(this.$t('dashboardExport.exportScheduled'))
        } else {
          this.$toast.success(this.$t('dashboardExport.exportStarted'))
        }

        // Reset form
        this.resetForm()
      } catch (error) {
        notifyIf(error, 'dashboard')
      } finally {
        this.loading = false
      }
    },
    async downloadExport(exportId) {
      try {
        const response = await this.$client.get(
          `/dashboard/exports/dashboards/download/?export_id=${exportId}`,
          { responseType: 'blob' }
        )

        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url

        // Get filename from response headers or generate one
        const contentDisposition = response.headers['content-disposition']
        let filename = 'dashboard_export'
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/)
          if (filenameMatch) {
            filename = filenameMatch[1]
          }
        }

        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        notifyIf(error, 'dashboard')
      }
    },
    async cancelExport(exportId) {
      try {
        await this.$client.post('/dashboard/exports/dashboards/cancel/', {
          export_id: exportId,
        })

        await this.loadExports()
        this.$toast.success(this.$t('dashboardExport.exportCancelled'))
      } catch (error) {
        notifyIf(error, 'dashboard')
      }
    },
    async deleteExport(exportId) {
      try {
        await this.$client.delete(
          `/dashboard/exports/dashboards/delete_export/?export_id=${exportId}`
        )

        await this.loadExports()
        this.$toast.success(this.$t('dashboardExport.exportDeleted'))
      } catch (error) {
        notifyIf(error, 'dashboard')
      }
    },
    resetForm() {
      this.exportConfig = {
        format: 'pdf',
        configuration: {
          pageSize: 'A4',
          orientation: 'landscape',
          resolution: '2x',
        },
        includeTitle: true,
        includeTimestamp: true,
        sendEmail: false,
        deliveryEmail: '',
        isScheduled: false,
        scheduleType: 'daily',
      }
    },
    getFormatIcon(format) {
      const icons = {
        pdf: 'fas fa-file-pdf',
        png: 'fas fa-file-image',
        csv: 'fas fa-file-csv',
      }
      return icons[format] || 'fas fa-file'
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },
  },
}
</script>

<style lang="scss" scoped>
.dashboard-export-modal {
  .export-options,
  .delivery-options,
  .scheduling-options,
  .export-history {
    margin-bottom: 2rem;

    h3 {
      margin-bottom: 1rem;
      font-size: 1.1rem;
      font-weight: 600;
    }
  }

  .pdf-options,
  .png-options,
  .schedule-config {
    margin-left: 1rem;
    padding-left: 1rem;
    border-left: 2px solid #e9ecef;
  }

  .exports-list {
    max-height: 300px;
    overflow-y: auto;

    .export-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      border: 1px solid #e9ecef;
      border-radius: 0.25rem;
      margin-bottom: 0.5rem;

      &.export-failed {
        border-color: #dc3545;
        background-color: #f8d7da;
      }

      .export-info {
        display: flex;
        align-items: center;

        .export-format {
          display: flex;
          align-items: center;
          margin-right: 1rem;

          i {
            margin-right: 0.5rem;
            width: 1rem;
          }

          span {
            font-weight: 500;
          }
        }

        .export-details {
          .export-date {
            font-size: 0.875rem;
            color: #6c757d;
          }

          .export-status {
            .status-pending {
              color: #ffc107;
            }

            .status-processing {
              color: #17a2b8;
            }

            .status-completed {
              color: #28a745;
            }

            .status-failed {
              color: #dc3545;
            }
          }
        }
      }

      .export-actions {
        display: flex;
        gap: 0.5rem;
      }
    }
  }

  .no-exports {
    text-align: center;
    padding: 2rem;
  }
}
</style>
