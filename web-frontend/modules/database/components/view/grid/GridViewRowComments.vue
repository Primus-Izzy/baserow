<template>
  <div class="grid-view-row-comments">
    <!-- Comment button in table row -->
    <CommentButton
      :table-id="table.id"
      :row-id="row.id"
      size="small"
      @click="handleCommentClick"
    />
    
    <!-- Comment sidebar -->
    <CommentSidebar
      :visible="showComments && selectedRowId === row.id"
      :table-id="table.id"
      :row-id="selectedRowId"
      @close="handleCloseSidebar"
    />
  </div>
</template>

<script>
import CommentButton from '@/modules/database/components/collaboration/CommentButton.vue'
import CommentSidebar from '@/modules/database/components/collaboration/CommentSidebar.vue'

export default {
  name: 'GridViewRowComments',
  components: {
    CommentButton,
    CommentSidebar,
  },
  props: {
    table: {
      type: Object,
      required: true,
    },
    row: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      showComments: false,
      selectedRowId: null,
    }
  },
  methods: {
    handleCommentClick(data) {
      this.selectedRowId = data.rowId
      this.showComments = true
      
      // Emit event to parent component
      this.$emit('show-comments', data)
    },
    handleCloseSidebar() {
      this.showComments = false
      this.selectedRowId = null
      
      // Emit event to parent component
      this.$emit('hide-comments')
    },
  },
}
</script>

<style lang="scss" scoped>
.grid-view-row-comments {
  display: inline-block;
}
</style>