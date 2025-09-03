<template>
  <div class="row-card-field-progress-bar">
    <ProgressBarDisplay
      :value="value"
      :field="field"
      :show-percentage="true"
      :is-mobile="true"
    />
  </div>
</template>

<script>
import ProgressBarDisplay from '@baserow/modules/database/components/field/ProgressBarDisplay'

export default {
  name: 'RowCardFieldProgressBar',
  components: {
    ProgressBarDisplay,
  },
  props: {
    field: {
      type: Object,
      required: true,
    },
    value: {
      type: [Number, String],
      default: null,
    },
    row: {
      type: Object,
      required: true,
    },
    workspaceId: {
      type: Number,
      required: false,
      default: null,
    },
  },
  // Static height property for card layout calculations
  height: 24,
}
</script>

<style lang="scss" scoped>
.row-card-field-progress-bar {
  display: flex;
  align-items: center;
  width: 100%;
  height: 24px;
  padding: 2px 0;
}
</style>
