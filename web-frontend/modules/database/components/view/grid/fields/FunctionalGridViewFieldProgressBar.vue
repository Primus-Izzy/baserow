<template>
  <div class="grid-view__cell">
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
  name: 'FunctionalGridViewFieldProgressBar',
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
}
</script>

<style lang="scss" scoped>
.grid-view__cell {
  display: flex;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 4px 8px;
}
</style>