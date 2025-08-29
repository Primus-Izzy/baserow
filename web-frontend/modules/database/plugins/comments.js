import CommentsService from '@/modules/database/services/comments'

export default function ({ app }, inject) {
  // Register comments service
  const commentsService = CommentsService(app.$axios)
  
  // Inject into context
  inject('comments', commentsService)
  
  // Also add to services object if it exists
  if (!app.$services) {
    app.$services = {}
  }
  app.$services.comments = commentsService
}