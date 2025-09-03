<template>
  <div class="visual-automation-builder">
    <!-- Enhanced Workflow Editor with Drag & Drop -->
    <div class="builder-canvas">
      <VueFlow
        class="enhanced-workflow-editor"
        :nodes="enhancedDisplayNodes"
        :edges="enhancedComputedEdges"
        :zoom-on-scroll="true"
        :nodes-draggable="true"
        :zoom-on-drag="true"
        :pan-on-scroll="true"
        :node-drag-threshold="10"
        :zoom-on-double-click="true"
        fit-view-on-init
        :max-zoom="2"
        :min-zoom="0.3"
        @nodes-change="onNodesChange"
        @edges-change="onEdgesChange"
        @connect="onConnect"
      >
        <Controls :show-interactive="true" />
        <MiniMap />
        <Background pattern-color="#f0f0f0" :size="2" :gap="20" />

        <!-- Enhanced Trigger Node -->
        <template #node-enhanced-trigger="slotProps">
          <EnhancedTriggerNode
            :id="slotProps.id"
            :data="slotProps.data"
            :selected="slotProps.selected"
            @configure="openNodeConfiguration"
            @delete="deleteNode"
          />
        </template>

        <!-- Enhanced Action Node -->
        <template #node-enhanced-action="slotProps">
          <EnhancedActionNode
            :id="slotProps.id"
            :data="slotProps.data"
            :selected="slotProps.selected"
            @configure="openNodeConfiguration"
            @delete="deleteNode"
          />
        </template>

        <!-- Conditional Branch Node -->
        <template #node-conditional-branch="slotProps">
          <ConditionalBranchNode
            :id="slotProps.id"
            :data="slotProps.data"
            :selected="slotProps.selected"
            @configure="openNodeConfiguration"
            @delete="deleteNode"
          />
        </template>

        <!-- Delay Node -->
        <template #node-delay="slotProps">
          <DelayNode
            :id="slotProps.id"
            :data="slotProps.data"
            :selected="slotProps.selected"
            @configure="openNodeConfiguration"
            @delete="deleteNode"
          />
        </template>

        <!-- Enhanced Edge with Conditional Logic -->
        <template #edge-enhanced-edge="slotProps">
          <EnhancedWorkflowEdge
            :id="slotProps.id"
            :source-x="slotProps.sourceX"
            :source-y="slotProps.sourceY"
            :target-x="slotProps.targetX"
            :target-y="slotProps.targetY"
            :data="slotProps.data"
          />
        </template>
      </VueFlow>
    </div>

    <!-- Node Palette -->
    <div class="node-palette">
      <div class="palette-header">
        <h3>{{ $t('visualBuilder.nodeLibrary') }}</h3>
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('visualBuilder.searchNodes')"
          class="palette-search"
        />
      </div>

      <div class="palette-categories">
        <div
          v-for="category in filteredNodeCategories"
          :key="category.name"
          class="palette-category"
        >
          <h4 class="category-title">{{ category.label }}</h4>
          <div class="category-nodes">
            <div
              v-for="nodeType in category.nodes"
              :key="nodeType.type"
              class="palette-node"
              draggable="true"
              @dragstart="onNodeDragStart($event, nodeType)"
            >
              <i :class="nodeType.iconClass"></i>
              <span>{{ nodeType.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuration Panel -->
    <div v-if="selectedNode" class="configuration-panel">
      <div class="panel-header">
        <h3>{{ $t('visualBuilder.configureNode') }}</h3>
        <button @click="closeConfiguration" class="close-btn">
          <i class="iconoir-cancel"></i>
        </button>
      </div>

      <div class="panel-content">
        <component
          :is="selectedNodeConfigComponent"
          v-if="selectedNodeConfigComponent"
          :node="selectedNode"
          :workflow="workflow"
          @update="updateNodeConfiguration"
        />
      </div>
    </div>

    <!-- Testing Panel -->
    <div class="testing-panel">
      <div class="panel-header">
        <h3>{{ $t('visualBuilder.testWorkflow') }}</h3>
        <div class="test-controls">
          <button
            @click="testWorkflow"
            :disabled="isTestingWorkflow"
            class="btn btn-primary"
          >
            <i class="iconoir-play" v-if="!isTestingWorkflow"></i>
            <i class="loading" v-else></i>
            {{ $t('visualBuilder.runTest') }}
          </button>
          <button
            @click="debugWorkflow"
            :disabled="isDebuggingWorkflow"
            class="btn btn-secondary"
          >
            <i class="iconoir-bug" v-if="!isDebuggingWorkflow"></i>
            <i class="loading" v-else></i>
            {{ $t('visualBuilder.debug') }}
          </button>
        </div>
      </div>

      <div class="test-results" v-if="testResults">
        <div class="results-header">
          <h4>{{ $t('visualBuilder.testResults') }}</h4>
          <span :class="['status', testResults.status]">
            {{ testResults.status }}
          </span>
        </div>
        <div class="results-content">
          <pre>{{ JSON.stringify(testResults.data, null, 2) }}</pre>
        </div>
      </div>
    </div>

    <!-- Execution Monitoring -->
    <div class="monitoring-panel">
      <div class="panel-header">
        <h3>{{ $t('visualBuilder.executionLogs') }}</h3>
        <div class="monitoring-controls">
          <button @click="refreshLogs" class="btn btn-ghost">
            <i class="iconoir-refresh"></i>
            {{ $t('visualBuilder.refresh') }}
          </button>
          <select v-model="logFilter" class="log-filter">
            <option value="all">{{ $t('visualBuilder.allLogs') }}</option>
            <option value="success">
              {{ $t('visualBuilder.successOnly') }}
            </option>
            <option value="failed">{{ $t('visualBuilder.errorsOnly') }}</option>
          </select>
        </div>
      </div>

      <div class="execution-logs">
        <div
          v-for="log in filteredExecutionLogs"
          :key="log.id"
          :class="['log-entry', log.status]"
        >
          <div class="log-header">
            <span class="log-timestamp">{{
              formatTimestamp(log.created_at)
            }}</span>
            <span :class="['log-status', log.status]">{{ log.status }}</span>
            <span class="log-duration">{{ log.execution_time_ms }}ms</span>
          </div>
          <div class="log-content">
            <div class="log-node">{{ getNodeLabel(log.node) }}</div>
            <div v-if="log.error_message" class="log-error">
              {{ log.error_message }}
            </div>
            <div class="log-data">
              <details>
                <summary>{{ $t('visualBuilder.viewData') }}</summary>
                <pre>{{ JSON.stringify(log.output_data, null, 2) }}</pre>
              </details>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { VueFlow, useVueFlow } from '@vue2-flow/core'
import { MiniMap } from '@vue2-flow/minimap'
import { Controls } from '@vue2-flow/controls'
import { Background } from '@vue2-flow/background'
import EnhancedTriggerNode from './nodes/EnhancedTriggerNode.vue'
import EnhancedActionNode from './nodes/EnhancedActionNode.vue'
import ConditionalBranchNode from './nodes/ConditionalBranchNode.vue'
import DelayNode from './nodes/DelayNode.vue'
import EnhancedWorkflowEdge from './edges/EnhancedWorkflowEdge.vue'

export default {
  name: 'VisualAutomationBuilder',
  components: {
    VueFlow,
    MiniMap,
    Controls,
    Background,
    EnhancedTriggerNode,
    EnhancedActionNode,
    ConditionalBranchNode,
    DelayNode,
    EnhancedWorkflowEdge,
  },
  props: {
    workflow: {
      type: Object,
      required: true,
    },
    nodes: {
      type: Array,
      default: () => [],
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      searchQuery: '',
      selectedNode: null,
      testResults: null,
      isTestingWorkflow: false,
      isDebuggingWorkflow: false,
      executionLogs: [],
      logFilter: 'all',
      draggedNodeType: null,
    }
  },
  computed: {
    enhancedDisplayNodes() {
      return this.nodes.map((node) => ({
        id: node.id.toString(),
        type: this.getNodeType(node),
        position: node.position || { x: 0, y: 0 },
        data: {
          ...node,
          readOnly: this.readOnly,
        },
      }))
    },

    enhancedComputedEdges() {
      const edges = []

      // Create edges based on node connections
      this.nodes.forEach((node, index) => {
        if (index < this.nodes.length - 1) {
          const nextNode = this.nodes[index + 1]
          edges.push({
            id: `e-${node.id}-${nextNode.id}`,
            source: node.id.toString(),
            target: nextNode.id.toString(),
            type: 'enhanced-edge',
            data: {
              condition: node.condition || null,
            },
          })
        }
      })

      return edges
    },

    filteredNodeCategories() {
      const categories = [
        {
          name: 'triggers',
          label: this.$t('visualBuilder.triggers'),
          nodes: this.getAvailableNodeTypes('trigger'),
        },
        {
          name: 'actions',
          label: this.$t('visualBuilder.actions'),
          nodes: this.getAvailableNodeTypes('action'),
        },
        {
          name: 'logic',
          label: this.$t('visualBuilder.logic'),
          nodes: this.getAvailableNodeTypes('logic'),
        },
      ]

      if (this.searchQuery) {
        return categories
          .map((category) => ({
            ...category,
            nodes: category.nodes.filter((node) =>
              node.name.toLowerCase().includes(this.searchQuery.toLowerCase())
            ),
          }))
          .filter((category) => category.nodes.length > 0)
      }

      return categories
    },

    selectedNodeConfigComponent() {
      if (!this.selectedNode) return null

      const nodeType = this.$registry.get('node', this.selectedNode.type)
      return nodeType?.configComponent || null
    },

    filteredExecutionLogs() {
      if (this.logFilter === 'all') {
        return this.executionLogs
      }

      return this.executionLogs.filter((log) => {
        if (this.logFilter === 'success') {
          return log.status === 'success'
        }
        if (this.logFilter === 'failed') {
          return log.status === 'failed'
        }
        return true
      })
    },
  },
  methods: {
    getNodeType(node) {
      const nodeType = this.$registry.get('node', node.type)

      if (nodeType.isTrigger) {
        return 'enhanced-trigger'
      }

      if (node.type === 'conditional_branch') {
        return 'conditional-branch'
      }

      if (node.type === 'delay') {
        return 'delay'
      }

      return 'enhanced-action'
    },

    getAvailableNodeTypes(category) {
      const nodeTypes = this.$registry.getOrderedList('node')

      switch (category) {
        case 'trigger':
          return nodeTypes.filter((type) => type.isTrigger)
        case 'action':
          return nodeTypes.filter(
            (type) => type.isWorkflowAction && !type.isLogicNode
          )
        case 'logic':
          return nodeTypes.filter((type) => type.isLogicNode)
        default:
          return []
      }
    },

    onNodeDragStart(event, nodeType) {
      this.draggedNodeType = nodeType
      event.dataTransfer.effectAllowed = 'move'
    },

    onNodesChange(changes) {
      // Handle node position changes, deletions, etc.
      changes.forEach((change) => {
        if (change.type === 'position' && change.position) {
          this.updateNodePosition(change.id, change.position)
        }
      })
    },

    onEdgesChange(changes) {
      // Handle edge changes
      this.$emit('edges-change', changes)
    },

    onConnect(connection) {
      // Handle new connections between nodes
      this.$emit('connect', connection)
    },

    openNodeConfiguration(nodeId) {
      this.selectedNode = this.nodes.find(
        (node) => node.id.toString() === nodeId
      )
    },

    closeConfiguration() {
      this.selectedNode = null
    },

    updateNodeConfiguration(nodeId, configuration) {
      this.$emit('update-node', { nodeId, configuration })
    },

    updateNodePosition(nodeId, position) {
      this.$emit('update-node-position', { nodeId, position })
    },

    deleteNode(nodeId) {
      this.$emit('delete-node', nodeId)
    },

    async testWorkflow() {
      this.isTestingWorkflow = true
      this.testResults = null

      try {
        const response = await this.$store.dispatch('automationWorkflow/test', {
          workflowId: this.workflow.id,
        })

        this.testResults = {
          status: 'success',
          data: response.data,
        }
      } catch (error) {
        this.testResults = {
          status: 'failed',
          data: error.response?.data || error.message,
        }
      } finally {
        this.isTestingWorkflow = false
      }
    },

    async debugWorkflow() {
      this.isDebuggingWorkflow = true

      try {
        const response = await this.$store.dispatch(
          'automationWorkflow/debug',
          {
            workflowId: this.workflow.id,
          }
        )

        this.testResults = {
          status: 'debug',
          data: response.data,
        }
      } catch (error) {
        this.testResults = {
          status: 'failed',
          data: error.response?.data || error.message,
        }
      } finally {
        this.isDebuggingWorkflow = false
      }
    },

    async refreshLogs() {
      try {
        const response = await this.$store.dispatch(
          'automationWorkflow/getExecutionLogs',
          {
            workflowId: this.workflow.id,
          }
        )

        this.executionLogs = response.data
      } catch (error) {
        console.error('Failed to fetch execution logs:', error)
      }
    },

    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleString()
    },

    getNodeLabel(nodeId) {
      const node = this.nodes.find((n) => n.id === nodeId)
      if (!node) return `Node ${nodeId}`

      const nodeType = this.$registry.get('node', node.type)
      return nodeType?.getLabel({ node }) || node.type
    },
  },

  mounted() {
    this.refreshLogs()

    // Set up real-time log updates
    this.$realtime.subscribe('automation_execution_log', (data) => {
      if (data.workflow_id === this.workflow.id) {
        this.executionLogs.unshift(data)

        // Keep only the last 100 logs
        if (this.executionLogs.length > 100) {
          this.executionLogs = this.executionLogs.slice(0, 100)
        }
      }
    })
  },

  beforeDestroy() {
    this.$realtime.unsubscribe('automation_execution_log')
  },
}
</script>

<style lang="scss" scoped>
.visual-automation-builder {
  display: grid;
  grid-template-columns: 300px 1fr 350px;
  grid-template-rows: 1fr 300px;
  grid-template-areas:
    'palette canvas config'
    'palette testing monitoring';
  height: 100vh;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
}

.builder-canvas {
  grid-area: canvas;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.enhanced-workflow-editor {
  width: 100%;
  height: 100%;
}

.node-palette {
  grid-area: palette;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  overflow-y: auto;
}

.palette-header {
  margin-bottom: 1rem;

  h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    font-weight: 600;
  }
}

.palette-search {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.palette-category {
  margin-bottom: 1.5rem;
}

.category-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.category-nodes {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.palette-node {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s ease;

  &:hover {
    background: #e9ecef;
    border-color: #007bff;
  }

  &:active {
    cursor: grabbing;
  }

  i {
    font-size: 1.2rem;
    color: #007bff;
  }

  span {
    font-size: 0.9rem;
    font-weight: 500;
  }
}

.configuration-panel {
  grid-area: config;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.testing-panel {
  grid-area: testing;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.monitoring-panel {
  grid-area: monitoring;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;

  h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }
}

.panel-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

.test-controls {
  display: flex;
  gap: 0.5rem;
}

.test-results {
  margin-top: 1rem;

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;

    h4 {
      margin: 0;
      font-size: 0.9rem;
    }
  }

  .status {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;

    &.success {
      background: #d4edda;
      color: #155724;
    }

    &.failed {
      background: #f8d7da;
      color: #721c24;
    }

    &.debug {
      background: #fff3cd;
      color: #856404;
    }
  }

  .results-content {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 0.75rem;
    font-family: monospace;
    font-size: 0.8rem;
    max-height: 200px;
    overflow-y: auto;
  }
}

.monitoring-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.log-filter {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.8rem;
}

.execution-logs {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.log-entry {
  margin-bottom: 1rem;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;

  &.success {
    border-left: 4px solid #28a745;
  }

  &.failed {
    border-left: 4px solid #dc3545;
  }

  &.pending {
    border-left: 4px solid #ffc107;
  }
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}

.log-timestamp {
  color: #666;
}

.log-status {
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
  font-weight: 600;
  text-transform: uppercase;

  &.success {
    background: #d4edda;
    color: #155724;
  }

  &.failed {
    background: #f8d7da;
    color: #721c24;
  }

  &.pending {
    background: #fff3cd;
    color: #856404;
  }
}

.log-duration {
  color: #666;
  font-family: monospace;
}

.log-content {
  font-size: 0.9rem;
}

.log-node {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.log-error {
  color: #dc3545;
  margin-bottom: 0.5rem;
  font-family: monospace;
  font-size: 0.8rem;
}

.log-data {
  details {
    summary {
      cursor: pointer;
      font-size: 0.8rem;
      color: #007bff;

      &:hover {
        text-decoration: underline;
      }
    }

    pre {
      margin-top: 0.5rem;
      background: #f8f9fa;
      padding: 0.5rem;
      border-radius: 4px;
      font-size: 0.7rem;
      overflow-x: auto;
    }
  }
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: #666;

  &:hover {
    color: #000;
  }
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.btn-primary {
    background: #007bff;
    color: white;

    &:hover:not(:disabled) {
      background: #0056b3;
    }
  }

  &.btn-secondary {
    background: #6c757d;
    color: white;

    &:hover:not(:disabled) {
      background: #545b62;
    }
  }

  &.btn-ghost {
    background: transparent;
    color: #007bff;
    border: 1px solid #007bff;

    &:hover:not(:disabled) {
      background: #007bff;
      color: white;
    }
  }
}
</style>
