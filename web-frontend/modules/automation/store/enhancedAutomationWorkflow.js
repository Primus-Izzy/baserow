import EnhancedAutomationService from '@baserow/modules/automation/services/enhancedAutomation'

const state = {
  // Visual Builder State
  selectedNodes: [],
  draggedNode: null,
  canvasZoom: 1,
  canvasPosition: { x: 0, y: 0 },
  
  // Testing and Debugging State
  testResults: null,
  debugResults: null,
  isTestingWorkflow: false,
  isDebuggingWorkflow: false,
  
  // Execution Monitoring State
  executionLogs: [],
  executionMetrics: {},
  isLoadingLogs: false,
  
  // IFTTT Builder State
  iftttRule: {
    trigger: null,
    actions: [],
  },
  
  // Templates State
  triggerTemplates: [],
  actionTemplates: [],
  isLoadingTemplates: false,
  
  // Validation State
  validationResults: {},
  
  // Performance Monitoring State
  performanceMetrics: {},
  workflowInsights: {},
  
  // Collaboration State
  workflowShares: [],
  workflowComments: [],
  
  // Versioning State
  workflowVersions: [],
  currentVersion: null,
  
  // Scheduling State
  workflowSchedules: [],
  
  // Analytics State
  workflowAnalytics: {},
  
  // Backup State
  workflowBackups: [],
}

const mutations = {
  // Visual Builder Mutations
  SET_SELECTED_NODES(state, nodes) {
    state.selectedNodes = nodes
  },
  
  ADD_SELECTED_NODE(state, node) {
    if (!state.selectedNodes.find(n => n.id === node.id)) {
      state.selectedNodes.push(node)
    }
  },
  
  REMOVE_SELECTED_NODE(state, nodeId) {
    state.selectedNodes = state.selectedNodes.filter(n => n.id !== nodeId)
  },
  
  CLEAR_SELECTED_NODES(state) {
    state.selectedNodes = []
  },
  
  SET_DRAGGED_NODE(state, node) {
    state.draggedNode = node
  },
  
  SET_CANVAS_ZOOM(state, zoom) {
    state.canvasZoom = zoom
  },
  
  SET_CANVAS_POSITION(state, position) {
    state.canvasPosition = position
  },
  
  // Testing and Debugging Mutations
  SET_TEST_RESULTS(state, results) {
    state.testResults = results
  },
  
  SET_DEBUG_RESULTS(state, results) {
    state.debugResults = results
  },
  
  SET_IS_TESTING_WORKFLOW(state, isTesting) {
    state.isTestingWorkflow = isTesting
  },
  
  SET_IS_DEBUGGING_WORKFLOW(state, isDebugging) {
    state.isDebuggingWorkflow = isDebugging
  },
  
  // Execution Monitoring Mutations
  SET_EXECUTION_LOGS(state, logs) {
    state.executionLogs = logs
  },
  
  ADD_EXECUTION_LOG(state, log) {
    state.executionLogs.unshift(log)
    
    // Keep only the last 100 logs
    if (state.executionLogs.length > 100) {
      state.executionLogs = state.executionLogs.slice(0, 100)
    }
  },
  
  SET_EXECUTION_METRICS(state, metrics) {
    state.executionMetrics = metrics
  },
  
  SET_IS_LOADING_LOGS(state, isLoading) {
    state.isLoadingLogs = isLoading
  },
  
  // IFTTT Builder Mutations
  SET_IFTTT_TRIGGER(state, trigger) {
    state.iftttRule.trigger = trigger
  },
  
  SET_IFTTT_ACTIONS(state, actions) {
    state.iftttRule.actions = actions
  },
  
  ADD_IFTTT_ACTION(state, action) {
    state.iftttRule.actions.push(action)
  },
  
  REMOVE_IFTTT_ACTION(state, actionIndex) {
    state.iftttRule.actions.splice(actionIndex, 1)
  },
  
  CLEAR_IFTTT_RULE(state) {
    state.iftttRule = {
      trigger: null,
      actions: [],
    }
  },
  
  // Templates Mutations
  SET_TRIGGER_TEMPLATES(state, templates) {
    state.triggerTemplates = templates
  },
  
  SET_ACTION_TEMPLATES(state, templates) {
    state.actionTemplates = templates
  },
  
  SET_IS_LOADING_TEMPLATES(state, isLoading) {
    state.isLoadingTemplates = isLoading
  },
  
  // Validation Mutations
  SET_VALIDATION_RESULTS(state, { nodeId, results }) {
    state.validationResults = {
      ...state.validationResults,
      [nodeId]: results,
    }
  },
  
  CLEAR_VALIDATION_RESULTS(state) {
    state.validationResults = {}
  },
  
  // Performance Monitoring Mutations
  SET_PERFORMANCE_METRICS(state, metrics) {
    state.performanceMetrics = metrics
  },
  
  SET_WORKFLOW_INSIGHTS(state, insights) {
    state.workflowInsights = insights
  },
  
  // Collaboration Mutations
  SET_WORKFLOW_SHARES(state, shares) {
    state.workflowShares = shares
  },
  
  ADD_WORKFLOW_SHARE(state, share) {
    state.workflowShares.push(share)
  },
  
  UPDATE_WORKFLOW_SHARE(state, { shareId, shareData }) {
    const index = state.workflowShares.findIndex(s => s.id === shareId)
    if (index !== -1) {
      state.workflowShares[index] = { ...state.workflowShares[index], ...shareData }
    }
  },
  
  REMOVE_WORKFLOW_SHARE(state, shareId) {
    state.workflowShares = state.workflowShares.filter(s => s.id !== shareId)
  },
  
  SET_WORKFLOW_COMMENTS(state, comments) {
    state.workflowComments = comments
  },
  
  ADD_WORKFLOW_COMMENT(state, comment) {
    state.workflowComments.push(comment)
  },
  
  UPDATE_WORKFLOW_COMMENT(state, { commentId, commentData }) {
    const index = state.workflowComments.findIndex(c => c.id === commentId)
    if (index !== -1) {
      state.workflowComments[index] = { ...state.workflowComments[index], ...commentData }
    }
  },
  
  REMOVE_WORKFLOW_COMMENT(state, commentId) {
    state.workflowComments = state.workflowComments.filter(c => c.id !== commentId)
  },
  
  // Versioning Mutations
  SET_WORKFLOW_VERSIONS(state, versions) {
    state.workflowVersions = versions
  },
  
  ADD_WORKFLOW_VERSION(state, version) {
    state.workflowVersions.unshift(version)
  },
  
  SET_CURRENT_VERSION(state, version) {
    state.currentVersion = version
  },
  
  // Scheduling Mutations
  SET_WORKFLOW_SCHEDULES(state, schedules) {
    state.workflowSchedules = schedules
  },
  
  ADD_WORKFLOW_SCHEDULE(state, schedule) {
    state.workflowSchedules.push(schedule)
  },
  
  UPDATE_WORKFLOW_SCHEDULE(state, { scheduleId, scheduleData }) {
    const index = state.workflowSchedules.findIndex(s => s.id === scheduleId)
    if (index !== -1) {
      state.workflowSchedules[index] = { ...state.workflowSchedules[index], ...scheduleData }
    }
  },
  
  REMOVE_WORKFLOW_SCHEDULE(state, scheduleId) {
    state.workflowSchedules = state.workflowSchedules.filter(s => s.id !== scheduleId)
  },
  
  // Analytics Mutations
  SET_WORKFLOW_ANALYTICS(state, analytics) {
    state.workflowAnalytics = analytics
  },
  
  // Backup Mutations
  SET_WORKFLOW_BACKUPS(state, backups) {
    state.workflowBackups = backups
  },
  
  ADD_WORKFLOW_BACKUP(state, backup) {
    state.workflowBackups.unshift(backup)
  },
  
  REMOVE_WORKFLOW_BACKUP(state, backupId) {
    state.workflowBackups = state.workflowBackups.filter(b => b.id !== backupId)
  },
}

const actions = {
  // Visual Builder Actions
  selectNodes({ commit }, nodes) {
    commit('SET_SELECTED_NODES', nodes)
  },
  
  addSelectedNode({ commit }, node) {
    commit('ADD_SELECTED_NODE', node)
  },
  
  removeSelectedNode({ commit }, nodeId) {
    commit('REMOVE_SELECTED_NODE', nodeId)
  },
  
  clearSelectedNodes({ commit }) {
    commit('CLEAR_SELECTED_NODES')
  },
  
  setDraggedNode({ commit }, node) {
    commit('SET_DRAGGED_NODE', node)
  },
  
  setCanvasZoom({ commit }, zoom) {
    commit('SET_CANVAS_ZOOM', zoom)
  },
  
  setCanvasPosition({ commit }, position) {
    commit('SET_CANVAS_POSITION', position)
  },
  
  // Testing and Debugging Actions
  async testWorkflow({ commit }, { workflowId, testData = {} }) {
    commit('SET_IS_TESTING_WORKFLOW', true)
    
    try {
      const response = await EnhancedAutomationService(this.$client).testWorkflow(workflowId, testData)
      commit('SET_TEST_RESULTS', response.data)
      return response
    } catch (error) {
      commit('SET_TEST_RESULTS', { error: error.response?.data || error.message })
      throw error
    } finally {
      commit('SET_IS_TESTING_WORKFLOW', false)
    }
  },
  
  async debugWorkflow({ commit }, { workflowId, debugOptions = {} }) {
    commit('SET_IS_DEBUGGING_WORKFLOW', true)
    
    try {
      const response = await EnhancedAutomationService(this.$client).debugWorkflow(workflowId, debugOptions)
      commit('SET_DEBUG_RESULTS', response.data)
      return response
    } catch (error) {
      commit('SET_DEBUG_RESULTS', { error: error.response?.data || error.message })
      throw error
    } finally {
      commit('SET_IS_DEBUGGING_WORKFLOW', false)
    }
  },
  
  // Execution Monitoring Actions
  async getExecutionLogs({ commit }, { workflowId, filters = {} }) {
    commit('SET_IS_LOADING_LOGS', true)
    
    try {
      const response = await EnhancedAutomationService(this.$client).getExecutionLogs(workflowId, filters)
      commit('SET_EXECUTION_LOGS', response.data)
      return response
    } catch (error) {
      console.error('Failed to fetch execution logs:', error)
      throw error
    } finally {
      commit('SET_IS_LOADING_LOGS', false)
    }
  },
  
  addExecutionLog({ commit }, log) {
    commit('ADD_EXECUTION_LOG', log)
  },
  
  async getExecutionMetrics({ commit }, { workflowId, timeRange = '24h' }) {
    try {
      const response = await EnhancedAutomationService(this.$client).getWorkflowMetrics(workflowId, timeRange)
      commit('SET_EXECUTION_METRICS', response.data)
      return response
    } catch (error) {
      console.error('Failed to fetch execution metrics:', error)
      throw error
    }
  },
  
  // IFTTT Builder Actions
  async createFromIftttRule({ commit }, { workflowId, ruleData }) {
    try {
      const response = await EnhancedAutomationService(this.$client).createFromIftttRule(workflowId, ruleData)
      commit('CLEAR_IFTTT_RULE')
      return response
    } catch (error) {
      console.error('Failed to create workflow from IFTTT rule:', error)
      throw error
    }
  },
  
  async testIftttRule({ commit }, { workflowId, ruleData }) {
    try {
      const response = await EnhancedAutomationService(this.$client).testIftttRule(workflowId, ruleData)
      return response
    } catch (error) {
      console.error('Failed to test IFTTT rule:', error)
      throw error
    }
  },
  
  setIftttTrigger({ commit }, trigger) {
    commit('SET_IFTTT_TRIGGER', trigger)
  },
  
  setIftttActions({ commit }, actions) {
    commit('SET_IFTTT_ACTIONS', actions)
  },
  
  addIftttAction({ commit }, action) {
    commit('ADD_IFTTT_ACTION', action)
  },
  
  removeIftttAction({ commit }, actionIndex) {
    commit('REMOVE_IFTTT_ACTION', actionIndex)
  },
  
  clearIftttRule({ commit }) {
    commit('CLEAR_IFTTT_RULE')
  },
  
  // Templates Actions
  async getTriggerTemplates({ commit }, category = null) {
    commit('SET_IS_LOADING_TEMPLATES', true)
    
    try {
      const response = await EnhancedAutomationService(this.$client).getTriggerTemplates(category)
      commit('SET_TRIGGER_TEMPLATES', response.data)
      return response
    } catch (error) {
      console.error('Failed to fetch trigger templates:', error)
      throw error
    } finally {
      commit('SET_IS_LOADING_TEMPLATES', false)
    }
  },
  
  async getActionTemplates({ commit }, category = null) {
    commit('SET_IS_LOADING_TEMPLATES', true)
    
    try {
      const response = await EnhancedAutomationService(this.$client).getActionTemplates(category)
      commit('SET_ACTION_TEMPLATES', response.data)
      return response
    } catch (error) {
      console.error('Failed to fetch action templates:', error)
      throw error
    } finally {
      commit('SET_IS_LOADING_TEMPLATES', false)
    }
  },
  
  async applyTriggerTemplate({ commit }, { workflowId, templateData }) {
    try {
      const response = await EnhancedAutomationService(this.$client).applyTriggerTemplate(workflowId, templateData)
      return response
    } catch (error) {
      console.error('Failed to apply trigger template:', error)
      throw error
    }
  },
  
  async applyActionTemplate({ commit }, { workflowId, templateData }) {
    try {
      const response = await EnhancedAutomationService(this.$client).applyActionTemplate(workflowId, templateData)
      return response
    } catch (error) {
      console.error('Failed to apply action template:', error)
      throw error
    }
  },
  
  // Validation Actions
  async validateWorkflow({ commit }, workflowId) {
    try {
      const response = await EnhancedAutomationService(this.$client).validateWorkflow(workflowId)
      commit('SET_VALIDATION_RESULTS', { nodeId: 'workflow', results: response.data })
      return response
    } catch (error) {
      console.error('Failed to validate workflow:', error)
      throw error
    }
  },
  
  async validateNode({ commit }, { nodeId, nodeType }) {
    try {
      let response
      if (nodeType === 'trigger') {
        response = await EnhancedAutomationService(this.$client).validateTrigger(nodeId)
      } else {
        response = await EnhancedAutomationService(this.$client).validateAction(nodeId)
      }
      
      commit('SET_VALIDATION_RESULTS', { nodeId, results: response.data })
      return response
    } catch (error) {
      console.error('Failed to validate node:', error)
      throw error
    }
  },
  
  clearValidationResults({ commit }) {
    commit('CLEAR_VALIDATION_RESULTS')
  },
  
  // Performance Monitoring Actions
  async getPerformanceMetrics({ commit }, { workflowId, timeRange = '7d' }) {
    try {
      const response = await EnhancedAutomationService(this.$client).getWorkflowPerformanceMetrics(workflowId, timeRange)
      commit('SET_PERFORMANCE_METRICS', response.data)
      return response
    } catch (error) {
      console.error('Failed to fetch performance metrics:', error)
      throw error
    }
  },
  
  async getWorkflowInsights({ commit }, workflowId) {
    try {
      const response = await EnhancedAutomationService(this.$client).getWorkflowInsights(workflowId)
      commit('SET_WORKFLOW_INSIGHTS', response.data)
      return response
    } catch (error) {
      console.error('Failed to fetch workflow insights:', error)
      throw error
    }
  },
  
  // Collaboration Actions
  async getWorkflowShares({ commit }, workflowId) {
    try {
      const response = await EnhancedAutomationService(this.$client).getWorkflowShares(workflowId)
      commit('SET_WORKFLOW_SHARES', response.data)
      return response
    } catch (error) {
      console.error('Failed to fetch workflow shares:', error)
      throw error
    }
  },
  
  async shareWorkflow({ commit }, { workflowId, shareData }) {
    try {
      const response = await EnhancedAutomationService(this.$client).shareWorkflow(workflowId, shareData)
      commit('ADD_WORKFLOW_SHARE', response.data)
      return response
    } catch (error) {
      console.error('Failed to share workflow:', error)
      throw error
    }
  },
  
  async updateWorkflowShare({ commit }, { shareId, shareData }) {
    try {
      const response = await EnhancedAutomationService(this.$client).updateWorkflowShare(shareId, shareData)
      commit('UPDATE_WORKFLOW_SHARE', { shareId, shareData: response.data })
      return response
    } catch (error) {
      console.error('Failed to update workflow share:', error)
      throw error
    }
  },
  
  async deleteWorkflowShare({ commit }, shareId) {
    try {
      await EnhancedAutomationService(this.$client).deleteWorkflowShare(shareId)
      commit('REMOVE_WORKFLOW_SHARE', shareId)
    } catch (error) {
      console.error('Failed to delete workflow share:', error)
      throw error
    }
  },
  
  // Analytics Actions
  async getWorkflowAnalytics({ commit }, { workflowId, analyticsType = 'overview', timeRange = '30d' }) {
    try {
      const response = await EnhancedAutomationService(this.$client).getWorkflowAnalytics(workflowId, analyticsType, timeRange)
      commit('SET_WORKFLOW_ANALYTICS', response.data)
      return response
    } catch (error) {
      console.error('Failed to fetch workflow analytics:', error)
      throw error
    }
  },
}

const getters = {
  // Visual Builder Getters
  getSelectedNodes: (state) => state.selectedNodes,
  getDraggedNode: (state) => state.draggedNode,
  getCanvasZoom: (state) => state.canvasZoom,
  getCanvasPosition: (state) => state.canvasPosition,
  
  // Testing and Debugging Getters
  getTestResults: (state) => state.testResults,
  getDebugResults: (state) => state.debugResults,
  isTestingWorkflow: (state) => state.isTestingWorkflow,
  isDebuggingWorkflow: (state) => state.isDebuggingWorkflow,
  
  // Execution Monitoring Getters
  getExecutionLogs: (state) => state.executionLogs,
  getExecutionMetrics: (state) => state.executionMetrics,
  isLoadingLogs: (state) => state.isLoadingLogs,
  
  // IFTTT Builder Getters
  getIftttRule: (state) => state.iftttRule,
  getIftttTrigger: (state) => state.iftttRule.trigger,
  getIftttActions: (state) => state.iftttRule.actions,
  
  // Templates Getters
  getTriggerTemplates: (state) => state.triggerTemplates,
  getActionTemplates: (state) => state.actionTemplates,
  isLoadingTemplates: (state) => state.isLoadingTemplates,
  
  // Validation Getters
  getValidationResults: (state) => state.validationResults,
  getNodeValidation: (state) => (nodeId) => state.validationResults[nodeId] || null,
  
  // Performance Monitoring Getters
  getPerformanceMetrics: (state) => state.performanceMetrics,
  getWorkflowInsights: (state) => state.workflowInsights,
  
  // Collaboration Getters
  getWorkflowShares: (state) => state.workflowShares,
  getWorkflowComments: (state) => state.workflowComments,
  
  // Versioning Getters
  getWorkflowVersions: (state) => state.workflowVersions,
  getCurrentVersion: (state) => state.currentVersion,
  
  // Scheduling Getters
  getWorkflowSchedules: (state) => state.workflowSchedules,
  
  // Analytics Getters
  getWorkflowAnalytics: (state) => state.workflowAnalytics,
  
  // Backup Getters
  getWorkflowBackups: (state) => state.workflowBackups,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}