const errorQueue = []

export const logger = {
  logError(error, context = '') {
    const logEntry = {
      timestamp: new Date().toISOString(),
      message: error?.message || String(error),
      stack: error?.stack || null,
      context: context
    }
    
    errorQueue.push(logEntry)
    
    if (errorQueue.length > 100) {
      errorQueue.shift()
    }

    console.error(`💥 [Observability Log] [${context}]:`, error)
  },

  getLogs() {
    return [...errorQueue]
  }
}