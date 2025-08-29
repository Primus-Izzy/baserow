import CollaborationService from '@baserow/modules/database/services/collaboration'

export default function ({ app }, inject) {
  // Create collaboration service instance
  const collaborationService = new CollaborationService(app)
  
  // Inject as $collaboration
  inject('collaboration', collaborationService)
  
  // Also inject as $ws for backward compatibility
  inject('ws', collaborationService)
  
  // Auto-connect when user is authenticated
  app.$auth.onRedirect(() => {
    if (app.$auth.loggedIn) {
      collaborationService.connect().catch(error => {
        console.error('Failed to connect to collaboration service:', error)
      })
    }
  })
  
  // Disconnect when user logs out
  app.$auth.$storage.watchState('loggedIn', (loggedIn) => {
    if (!loggedIn) {
      collaborationService.disconnect()
    }
  })
}