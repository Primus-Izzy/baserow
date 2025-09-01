/**
 * Enhanced logging utility for Baserow frontend
 * Provides structured logging with different levels and proper error handling
 */

const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3
}

class Logger {
  constructor(context = 'App') {
    this.context = context
    this.level = this.getLogLevel()
  }

  getLogLevel() {
    if (process.env.NODE_ENV === 'production') {
      return LOG_LEVELS.WARN
    } else if (process.env.NODE_ENV === 'test') {
      return LOG_LEVELS.ERROR
    }
    return LOG_LEVELS.DEBUG
  }

  shouldLog(level) {
    return level <= this.level
  }

  formatMessage(level, message, ...args) {
    const timestamp = new Date().toISOString()
    const levelName = Object.keys(LOG_LEVELS)[level]
    return {
      timestamp,
      level: levelName,
      context: this.context,
      message,
      args
    }
  }

  error(message, error = null, ...args) {
    if (!this.shouldLog(LOG_LEVELS.ERROR)) return

    const logData = this.formatMessage(LOG_LEVELS.ERROR, message, ...args)
    
    if (process.env.NODE_ENV === 'production') {
      // In production, send to error reporting service
      this.sendToErrorService(logData, error)
    } else {
      console.error(`[${logData.timestamp}] [${logData.level}] [${logData.context}]`, message, error, ...args)
    }
  }

  warn(message, ...args) {
    if (!this.shouldLog(LOG_LEVELS.WARN)) return

    const logData = this.formatMessage(LOG_LEVELS.WARN, message, ...args)
    
    if (process.env.NODE_ENV !== 'production') {
      console.warn(`[${logData.timestamp}] [${logData.level}] [${logData.context}]`, message, ...args)
    }
  }

  info(message, ...args) {
    if (!this.shouldLog(LOG_LEVELS.INFO)) return

    const logData = this.formatMessage(LOG_LEVELS.INFO, message, ...args)
    
    if (process.env.NODE_ENV !== 'production') {
      console.info(`[${logData.timestamp}] [${logData.level}] [${logData.context}]`, message, ...args)
    }
  }

  debug(message, ...args) {
    if (!this.shouldLog(LOG_LEVELS.DEBUG)) return

    const logData = this.formatMessage(LOG_LEVELS.DEBUG, message, ...args)
    
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[${logData.timestamp}] [${logData.level}] [${logData.context}]`, message, ...args)
    }
  }

  performance(name, fn) {
    if (!this.shouldLog(LOG_LEVELS.DEBUG)) {
      return fn()
    }

    const start = performance.now()
    const result = fn()
    const end = performance.now()
    
    this.debug(`Performance: ${name} took ${end - start} milliseconds`)
    return result
  }

  async performanceAsync(name, fn) {
    if (!this.shouldLog(LOG_LEVELS.DEBUG)) {
      return await fn()
    }

    const start = performance.now()
    const result = await fn()
    const end = performance.now()
    
    this.debug(`Performance: ${name} took ${end - start} milliseconds`)
    return result
  }

  sendToErrorService(logData, error) {
    // In a real application, this would send to Sentry, LogRocket, etc.
    // For now, we'll just store in a queue for potential batch sending
    try {
      const errorQueue = JSON.parse(localStorage.getItem('baserow-error-queue') || '[]')
      errorQueue.push({
        ...logData,
        error: error ? {
          name: error.name,
          message: error.message,
          stack: error.stack
        } : null,
        userAgent: navigator.userAgent,
        url: window.location.href
      })
      
      // Keep only last 50 errors to prevent storage bloat
      if (errorQueue.length > 50) {
        errorQueue.splice(0, errorQueue.length - 50)
      }
      
      localStorage.setItem('baserow-error-queue', JSON.stringify(errorQueue))
    } catch (storageError) {
      // Fallback to console if localStorage fails
      console.error('Failed to store error log:', storageError)
      console.error('Original error:', logData, error)
    }
  }

  createContextLogger(context) {
    return new Logger(`${this.context}:${context}`)
  }
}

// Create default logger instance
const logger = new Logger('Baserow')

// Export both the class and default instance
export { Logger, LOG_LEVELS }
export default logger