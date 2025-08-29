import { registerRealtimeEvents } from '@baserow/modules/core/plugins/clientHandler'

export default (context) => {
  const { store, app } = context

  // Register integration-related realtime events
  registerRealtimeEvents(app.$realtime, [
    {
      type: 'integration_connection_updated',
      handler({ connection_id, status }) {
        store.dispatch('integrations/updateConnectionStatus', { connection_id, status })
      },
    },
    {
      type: 'integration_sync_completed',
      handler({ sync_id, status, error_message }) {
        store.dispatch('integrations/updateSyncStatus', { sync_id, status, error_message })
      },
    },
  ])
}