<template>
  <div class="form-view-shareable-links">
    <div class="form-view-shareable-links__header">
      <h3>{{ $t('formViewShareableLinks.title') }}</h3>
      <p class="form-view-shareable-links__description">
        {{ $t('formViewShareableLinks.description') }}
      </p>
    </div>

    <div class="form-view-shareable-links__actions">
      <Button
        type="primary"
        icon="iconoir-plus"
        @click="showCreateModal = true"
      >
        {{ $t('formViewShareableLinks.createLink') }}
      </Button>
    </div>

    <div class="form-view-shareable-links__list">
      <div
        v-for="link in shareableLinks"
        :key="link.id"
        class="form-view-shareable-links__link"
        :class="{
          'form-view-shareable-links__link--inactive': !link.is_active,
        }"
      >
        <div class="form-view-shareable-links__link-info">
          <div class="form-view-shareable-links__link-name">
            {{ link.name }}
          </div>
          <div class="form-view-shareable-links__link-description">
            {{ link.description || $t('formViewShareableLinks.noDescription') }}
          </div>
          <div class="form-view-shareable-links__link-meta">
            <span class="form-view-shareable-links__link-type">
              {{ $t(`formViewShareableLinks.accessTypes.${link.access_type}`) }}
            </span>
            <span
              v-if="link.expires_at"
              class="form-view-shareable-links__link-expires"
            >
              {{
                $t('formViewShareableLinks.expiresAt', {
                  date: formatDate(link.expires_at),
                })
              }}
            </span>
            <span class="form-view-shareable-links__link-submissions">
              {{
                $t('formViewShareableLinks.submissions', {
                  current: link.current_submissions,
                  max: link.max_submissions || '∞',
                })
              }}
            </span>
          </div>
        </div>

        <div class="form-view-shareable-links__link-url">
          <div class="form-view-shareable-links__url-container">
            <FormInput
              :value="getLinkUrl(link)"
              readonly
              class="form-view-shareable-links__url-input"
            />
            <Button
              type="secondary"
              size="small"
              icon="iconoir-copy"
              @click="copyLinkUrl(link)"
            >
              {{ $t('formViewShareableLinks.copy') }}
            </Button>
          </div>
        </div>

        <div class="form-view-shareable-links__link-actions">
          <Button
            type="secondary"
            size="small"
            icon="iconoir-edit"
            @click="editLink(link)"
          >
            {{ $t('formViewShareableLinks.edit') }}
          </Button>
          <Button
            type="secondary"
            size="small"
            :icon="link.is_active ? 'iconoir-pause' : 'iconoir-play'"
            @click="toggleLinkStatus(link)"
          >
            {{
              link.is_active
                ? $t('formViewShareableLinks.disable')
                : $t('formViewShareableLinks.enable')
            }}
          </Button>
          <Button
            type="danger"
            size="small"
            icon="iconoir-bin"
            @click="deleteLink(link)"
          >
            {{ $t('formViewShareableLinks.delete') }}
          </Button>
        </div>
      </div>

      <div
        v-if="shareableLinks.length === 0"
        class="form-view-shareable-links__empty"
      >
        <p>{{ $t('formViewShareableLinks.noLinks') }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormViewShareableLinks',
  props: {
    view: {
      type: Object,
      required: true,
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      shareableLinks: [...(this.view.shareable_links || [])],
    }
  },
  methods: {
    editLink(link) {
      this.$emit('edit-link', link)
    },
    async toggleLinkStatus(link) {
      if (this.readOnly) return

      try {
        await this.$emit('update-shareable-link', link.id, {
          ...link,
          is_active: !link.is_active,
        })
      } catch (error) {
        this.$store.dispatch('toast/error', {
          title: this.$t('formViewShareableLinks.toggleError'),
          message: error.response?.data?.error || error.message,
        })
      }
    },
    async deleteLink(link) {
      if (this.readOnly) return

      const confirmed = confirm(
        this.$t('formViewShareableLinks.deleteConfirmMessage', {
          name: link.name,
        })
      )

      if (confirmed) {
        try {
          await this.$emit('delete-shareable-link', link.id)
        } catch (error) {
          this.$store.dispatch('toast/error', {
            title: this.$t('formViewShareableLinks.deleteError'),
            message: error.response?.data?.error || error.message,
          })
        }
      }
    },
    getLinkUrl(link) {
      const baseUrl = window.location.origin
      return `${baseUrl}/form/${this.view.slug}?token=${link.token}`
    },
    async copyLinkUrl(link) {
      const url = this.getLinkUrl(link)
      try {
        await navigator.clipboard.writeText(url)
        this.$store.dispatch('toast/success', {
          title: this.$t('formViewShareableLinks.copySuccess'),
        })
      } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea')
        textArea.value = url
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)

        this.$store.dispatch('toast/success', {
          title: this.$t('formViewShareableLinks.copySuccess'),
        })
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
  },
}
</script>

<style lang="scss" scoped>
.form-view-shareable-links {
  &__header {
    margin-bottom: 24px;

    h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
      color: #2d3748;
    }
  }

  &__description {
    margin: 0;
    font-size: 14px;
    color: #718096;
  }

  &__actions {
    margin-bottom: 24px;
  }

  &__list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  &__link {
    padding: 20px;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    background-color: white;

    &--inactive {
      opacity: 0.6;
      background-color: #f8f9fa;
    }
  }

  &__link-info {
    margin-bottom: 16px;
  }

  &__link-name {
    font-size: 16px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 4px;
  }

  &__link-description {
    font-size: 14px;
    color: #718096;
    margin-bottom: 8px;
  }

  &__link-meta {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: #a0aec0;

    span {
      padding: 2px 8px;
      background-color: #edf2f7;
      border-radius: 12px;
    }
  }

  &__link-url {
    margin-bottom: 16px;
  }

  &__url-container {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  &__url-input {
    flex: 1;
  }

  &__link-actions {
    display: flex;
    gap: 8px;
  }

  &__empty {
    padding: 40px;
    text-align: center;
    color: #718096;
    font-style: italic;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    background-color: #f8f9fa;
  }
}
</style>
