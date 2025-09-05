<template>
  <div class="view-header">
    <div class="view-header__left">
      <slot name="title">
        <h2>{{ view.name }}</h2>
      </slot>
    </div>

    <div class="view-header__right">
      <slot name="menus"></slot>
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ViewHeader',
  props: {
    view: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      default: () => [],
    },
    table: {
      type: Object,
      required: false,
      default: null,
    },
    database: {
      type: Object,
      required: false,
      default: null,
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
    storePrefix: {
      type: String,
      default: '',
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@baserow/modules/core/assets/scss/colors.scss';

.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid $color-neutral-200;
  background-color: $color-neutral-50;

  &__left {
    display: flex;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
      color: $color-neutral-900;
    }
  }

  &__right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
}
</style>
