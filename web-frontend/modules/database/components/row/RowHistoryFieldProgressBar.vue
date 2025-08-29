<template>
  <div class="row-history-field-progress-bar">
    <ProgressBarDisplay
      :value="value"
      :field="field"
      :show-percentage="true"
    />
  </div>
</template>

<script>
import ProgressBarDisplay from '@baserow/modules/database/components/field/ProgressBarDisplay'

export default {
  name: 'RowHistoryFieldProgressBar',
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
  },
  // Static height property for history layout calculations
  height: 20,
}
</script>

<style lang="scss" scoped>
.row-history-field-progress-bar {
  display: flex;
  align-items: center;
  width: 100%;
  height: 20px;
}
</style>