// API Configuration for different environments

export const API_CONFIG = {
  // Backend URL - use environment variable or fallback to localhost for development
  BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  
  // Feature flags
  ENABLE_BACKEND: process.env.NEXT_PUBLIC_ENABLE_BACKEND !== 'false',
  
  // Timeout settings
  REQUEST_TIMEOUT: 60000, // Increased to 60 seconds
  
  // Endpoints
  ENDPOINTS: {
    ANALYZE: '/analyze',
    ANALYSES: '/analyses', 
    PROGRESS: '/progress',
    HEALTH: '/health'
  }
}

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BACKEND_URL}${endpoint}`
}

// Check if we're in production and backend is not available
export const isBackendAvailable = (): boolean => {
  // In production, if no backend URL is configured, disable backend features
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
    return API_CONFIG.BACKEND_URL !== 'http://localhost:8000' && API_CONFIG.ENABLE_BACKEND
  }
  return API_CONFIG.ENABLE_BACKEND
}
