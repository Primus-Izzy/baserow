export default (client) => {
  return {
    // Visual Automation Builder APIs
    testWorkflow(workflowId, testData = {}) {
      return client.post(`automation/workflow/${workflowId}/test/`, testData)
    },

    debugWorkflow(workflowId, debugOptions = {}) {
      return client.post(`automation/workflow/${workflowId}/debug/`, debugOptions)
    },

    getExecutionLogs(workflowId, filters = {}) {
      const params = new URLSearchParams(filters).toString()
      return client.get(`automation/workflow/${workflowId}/execution-logs/?${params}`)
    },

    // IFTTT Rule Builder APIs
    createFromIftttRule(workflowId, ruleData) {
      return client.post(`automation/workflow/${workflowId}/ifttt-rule/`, ruleData)
    },

    testIftttRule(workflowId, ruleData) {
      return client.post(`automation/workflow/${workflowId}/ifttt-rule/test/`, ruleData)
    },

    // Enhanced Trigger APIs
    createDateBasedTrigger(workflowId, triggerData) {
      return client.post(`automation/workflow/${workflowId}/triggers/date-based/`, triggerData)
    },

    updateDateBasedTrigger(triggerId, triggerData) {
      return client.patch(`automation/triggers/date-based/${triggerId}/`, triggerData)
    },

    createWebhookTrigger(workflowId, triggerData) {
      return client.post(`automation/workflow/${workflowId}/triggers/webhook/`, triggerData)
    },

    updateWebhookTrigger(triggerId, triggerData) {
      return client.patch(`automation/triggers/webhook/${triggerId}/`, triggerData)
    },

    createLinkedRecordChangeTrigger(workflowId, triggerData) {
      return client.post(`automation/workflow/${workflowId}/triggers/linked-record-change/`, triggerData)
    },

    updateLinkedRecordChangeTrigger(triggerId, triggerData) {
      return client.patch(`automation/triggers/linked-record-change/${triggerId}/`, triggerData)
    },

    createConditionalTrigger(workflowId, triggerData) {
      return client.post(`automation/workflow/${workflowId}/triggers/conditional/`, triggerData)
    },

    updateConditionalTrigger(triggerId, triggerData) {
      return client.patch(`automation/triggers/conditional/${triggerId}/`, triggerData)
    },

    // Trigger Templates APIs
    getTriggerTemplates(category = null) {
      const params = category ? `?category=${category}` : ''
      return client.get(`automation/trigger-templates/${params}`)
    },

    applyTriggerTemplate(workflowId, templateData) {
      return client.post(`automation/workflow/${workflowId}/apply-trigger-template/`, templateData)
    },

    // Enhanced Action APIs
    createNotificationAction(workflowId, actionData) {
      return client.post(`automation/workflow/${workflowId}/actions/notification/`, actionData)
    },

    updateNotificationAction(actionId, actionData) {
      return client.patch(`automation/actions/notification/${actionId}/`, actionData)
    },

    createWebhookAction(workflowId, actionData) {
      return client.post(`automation/workflow/${workflowId}/actions/webhook/`, actionData)
    },

    updateWebhookAction(actionId, actionData) {
      return client.patch(`automation/actions/webhook/${actionId}/`, actionData)
    },

    createStatusChangeAction(workflowId, actionData) {
      return client.post(`automation/workflow/${workflowId}/actions/status-change/`, actionData)
    },

    updateStatusChangeAction(actionId, actionData) {
      return client.patch(`automation/actions/status-change/${actionId}/`, actionData)
    },

    createConditionalBranchAction(workflowId, actionData) {
      return client.post(`automation/workflow/${workflowId}/actions/conditional-branch/`, actionData)
    },

    updateConditionalBranchAction(actionId, actionData) {
      return client.patch(`automation/actions/conditional-branch/${actionId}/`, actionData)
    },

    createDelayAction(workflowId, actionData) {
      return client.post(`automation/workflow/${workflowId}/actions/delay/`, actionData)
    },

    updateDelayAction(actionId, actionData) {
      return client.patch(`automation/actions/delay/${actionId}/`, actionData)
    },

    // Action Templates APIs
    getActionTemplates(category = null) {
      const params = category ? `?category=${category}` : ''
      return client.get(`automation/action-templates/${params}`)
    },

    applyActionTemplate(workflowId, templateData) {
      return client.post(`automation/workflow/${workflowId}/apply-action-template/`, templateData)
    },

    // Workflow Validation APIs
    validateWorkflow(workflowId) {
      return client.post(`automation/workflow/${workflowId}/validate/`)
    },

    validateTrigger(triggerId) {
      return client.post(`automation/trigger/${triggerId}/validate/`)
    },

    validateAction(actionId) {
      return client.post(`automation/action/${actionId}/validate/`)
    },

    // Workflow Monitoring APIs
    getWorkflowMetrics(workflowId, timeRange = '24h') {
      return client.get(`automation/workflow/${workflowId}/metrics/?range=${timeRange}`)
    },

    getWorkflowExecutionHistory(workflowId, limit = 50, offset = 0) {
      return client.get(`automation/workflow/${workflowId}/execution-history/?limit=${limit}&offset=${offset}`)
    },

    // Workflow Export/Import APIs
    exportWorkflow(workflowId, format = 'json') {
      return client.get(`automation/workflow/${workflowId}/export/?format=${format}`)
    },

    importWorkflow(automationId, workflowData) {
      return client.post(`automation/${automationId}/import-workflow/`, workflowData)
    },

    // Workflow Collaboration APIs
    shareWorkflow(workflowId, shareData) {
      return client.post(`automation/workflow/${workflowId}/share/`, shareData)
    },

    getWorkflowShares(workflowId) {
      return client.get(`automation/workflow/${workflowId}/shares/`)
    },

    updateWorkflowShare(shareId, shareData) {
      return client.patch(`automation/workflow-share/${shareId}/`, shareData)
    },

    deleteWorkflowShare(shareId) {
      return client.delete(`automation/workflow-share/${shareId}/`)
    },

    // Workflow Comments APIs
    getWorkflowComments(workflowId) {
      return client.get(`automation/workflow/${workflowId}/comments/`)
    },

    createWorkflowComment(workflowId, commentData) {
      return client.post(`automation/workflow/${workflowId}/comments/`, commentData)
    },

    updateWorkflowComment(commentId, commentData) {
      return client.patch(`automation/workflow-comment/${commentId}/`, commentData)
    },

    deleteWorkflowComment(commentId) {
      return client.delete(`automation/workflow-comment/${commentId}/`)
    },

    // Workflow Versioning APIs
    getWorkflowVersions(workflowId) {
      return client.get(`automation/workflow/${workflowId}/versions/`)
    },

    createWorkflowVersion(workflowId, versionData) {
      return client.post(`automation/workflow/${workflowId}/versions/`, versionData)
    },

    restoreWorkflowVersion(workflowId, versionId) {
      return client.post(`automation/workflow/${workflowId}/restore-version/${versionId}/`)
    },

    compareWorkflowVersions(workflowId, version1Id, version2Id) {
      return client.get(`automation/workflow/${workflowId}/compare-versions/?v1=${version1Id}&v2=${version2Id}`)
    },

    // Workflow Performance APIs
    getWorkflowPerformanceMetrics(workflowId, timeRange = '7d') {
      return client.get(`automation/workflow/${workflowId}/performance/?range=${timeRange}`)
    },

    optimizeWorkflow(workflowId, optimizationOptions = {}) {
      return client.post(`automation/workflow/${workflowId}/optimize/`, optimizationOptions)
    },

    // Workflow Scheduling APIs
    scheduleWorkflow(workflowId, scheduleData) {
      return client.post(`automation/workflow/${workflowId}/schedule/`, scheduleData)
    },

    updateWorkflowSchedule(scheduleId, scheduleData) {
      return client.patch(`automation/workflow-schedule/${scheduleId}/`, scheduleData)
    },

    deleteWorkflowSchedule(scheduleId) {
      return client.delete(`automation/workflow-schedule/${scheduleId}/`)
    },

    getWorkflowSchedules(workflowId) {
      return client.get(`automation/workflow/${workflowId}/schedules/`)
    },

    // Workflow Analytics APIs
    getWorkflowAnalytics(workflowId, analyticsType = 'overview', timeRange = '30d') {
      return client.get(`automation/workflow/${workflowId}/analytics/?type=${analyticsType}&range=${timeRange}`)
    },

    getWorkflowInsights(workflowId) {
      return client.get(`automation/workflow/${workflowId}/insights/`)
    },

    // Workflow Backup APIs
    createWorkflowBackup(workflowId, backupData) {
      return client.post(`automation/workflow/${workflowId}/backup/`, backupData)
    },

    getWorkflowBackups(workflowId) {
      return client.get(`automation/workflow/${workflowId}/backups/`)
    },

    restoreWorkflowBackup(workflowId, backupId) {
      return client.post(`automation/workflow/${workflowId}/restore-backup/${backupId}/`)
    },

    deleteWorkflowBackup(backupId) {
      return client.delete(`automation/workflow-backup/${backupId}/`)
    },
  }
}