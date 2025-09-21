import React, { useState, useEffect, useRef } from 'react'
import { API_CONFIG, getApiUrl } from '../config/api'

interface ProgressLoaderProps {
  isVisible: boolean
  documentIds?: string[]
  onComplete?: (results: any) => void
  onError?: (error: string) => void
}

interface ProgressData {
  document_id: string
  progress: number
  status: string
  message: string
  completed: boolean
  error?: string
}

const ProgressLoader: React.FC<ProgressLoaderProps> = ({
  isVisible,
  documentIds = [],
  onComplete,
  onError
}) => {
  const [progressData, setProgressData] = useState<Record<string, ProgressData>>({})
  const [overallProgress, setOverallProgress] = useState(0)
  const [currentMessage, setCurrentMessage] = useState("Initializing...")
  const [timeElapsed, setTimeElapsed] = useState(0)

  // Use refs to store the latest callback functions without causing re-renders
  const onCompleteRef = useRef(onComplete)
  const onErrorRef = useRef(onError)

  // Update refs when props change
  onCompleteRef.current = onComplete
  onErrorRef.current = onError

  // Reset state when not visible
  useEffect(() => {
    if (!isVisible) {
      setProgressData({})
      setOverallProgress(0)
      setTimeElapsed(0)
      setCurrentMessage("Initializing...")
    }
  }, [isVisible])

  // Main polling effect - only runs when visible
  useEffect(() => {
    if (!isVisible) {
      return
    }

    // Start timer
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1)
    }, 1000)

    // Poll for progress updates
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.PROGRESS))
        const data = await response.json()

        if (data.progress_data) {
          console.log('📊 Progress data received:', data.progress_data)
          setProgressData(data.progress_data)

          // Calculate overall progress
          const relevantDocs = Object.values(data.progress_data).filter((doc: any) =>
            documentIds.length === 0 || documentIds.includes(doc.document_id)
          ) as ProgressData[]

          if (relevantDocs.length > 0) {
            const totalProgress = relevantDocs.reduce((sum: number, doc: ProgressData) =>
              sum + Math.max(0, doc.progress), 0
            )
            const avgProgress = totalProgress / relevantDocs.length
            setOverallProgress(Math.round(avgProgress))

            // Update current message
            const activeDoc = relevantDocs.find((doc: ProgressData) => !doc.completed && doc.progress >= 0)
            if (activeDoc) {
              setCurrentMessage(activeDoc.message || "Processing...")
            }

            // Check if all completed
            const allCompleted = relevantDocs.every((doc: ProgressData) => doc.completed)
            const hasErrors = relevantDocs.some((doc: ProgressData) => doc.error || doc.progress < 0)

            if (allCompleted) {
              clearInterval(pollInterval)
              clearInterval(timer)

              if (hasErrors) {
                const errorDoc = relevantDocs.find((doc: ProgressData) => doc.error)
                console.log('🚨 Analysis failed with error:', errorDoc?.error)
                onErrorRef.current?.(errorDoc?.error || "Processing failed")
              } else {
                console.log('✅ Analysis completed, calling onComplete with:', relevantDocs)
                onCompleteRef.current?.(relevantDocs)
              }
            }
          }
        }
      } catch (error) {
        console.error('❌ Failed to fetch progress:', error)
        // If backend is not available, show a more graceful message
        if (error instanceof TypeError && error.message === 'Failed to fetch') {
          setCurrentMessage('Connecting to backend...')
          // Don't call onError immediately, give backend time to start
        }
      }
    }, 1000) // Poll every second

    return () => {
      clearInterval(pollInterval)
      clearInterval(timer)
    }
  }, [isVisible, documentIds])

  if (!isVisible) return null

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getProgressColor = (progress: number) => {
    if (progress < 0) return 'bg-red-500'
    if (progress < 30) return 'bg-blue-500'
    if (progress < 70) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getStatusIcon = (progress: number, status: string) => {
    if (progress < 0 || status === 'error') return '❌'
    if (progress >= 100 || status === 'completed') return '✅'
    return '🔄'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🤖</div>
          <h3 className="text-xl font-semibold text-gray-800">
            Analyzing with Gemini 2.5 Flash
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Processing documents and extracting insights
          </p>
        </div>

        {/* Overall Progress */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Overall Progress</span>
            <span className={`text-sm font-bold ${overallProgress === 100 ? 'text-green-600' : 'text-blue-600'}`}>
              {overallProgress === 100 ? '✅ Complete!' : `${overallProgress}%`}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-500 ${getProgressColor(overallProgress)}`}
              style={{ width: `${Math.max(0, overallProgress)}%` }}
            />
          </div>
        </div>

        {/* Current Status */}
        <div className="mb-6">
          <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            <span>{currentMessage}</span>
          </div>
        </div>

        {/* Individual Document Progress */}
        {Object.keys(progressData).length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Document Status</h4>
            <div className="space-y-3 max-h-40 overflow-y-auto">
              {Object.values(progressData)
                .filter((doc: ProgressData) =>
                  documentIds.length === 0 || documentIds.includes(doc.document_id)
                )
                .map((doc: ProgressData) => (
                <div key={doc.document_id} className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2">
                      <span>{getStatusIcon(doc.progress, doc.status)}</span>
                      <span className="text-sm font-medium text-gray-700">
                        {(doc as any).file_progress && Object.keys((doc as any).file_progress).length > 0
                          ? `Processing ${Object.keys((doc as any).file_progress).length} files`
                          : doc.message || 'Processing documents'
                        }
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={doc.progress < 0 ? 'text-red-500' : 'text-green-600 font-medium'}>
                        {doc.progress < 0 ? 'Error' : `${doc.progress}%`}
                      </span>
                    </div>
                  </div>

                  {/* Individual File Progress */}
                  {(() => {
                    const fileProgress = (doc as any).file_progress;
                    console.log('📄 File progress for doc:', doc.document_id, fileProgress);
                    return fileProgress && Object.keys(fileProgress).length > 0;
                  })() && (
                    <div className="ml-6 space-y-1">
                      {Object.entries((doc as any).file_progress).map(([filename, fileData]: [string, any]) => (
                        <div key={filename} className="flex items-center justify-between text-xs text-gray-600">
                          <div className="flex items-center space-x-2">
                            <span className={`w-2 h-2 rounded-full ${
                              fileData.progress === 100 ? 'bg-green-500' :
                              fileData.progress > 0 ? 'bg-blue-500' : 'bg-gray-400'
                            }`}></span>
                            <span className="truncate max-w-32 font-medium" title={filename}>
                              📄 {filename.length > 20 ? filename.substring(0, 20) + '...' : filename}
                            </span>
                          </div>
                          <span className={`font-medium ${
                            fileData.progress === 100 ? 'text-green-600' : 'text-blue-600'
                          }`}>
                            {fileData.progress}%
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Time and Tips */}
        <div className="text-center">
          <div className="text-xs text-gray-500 mb-3">
            Time elapsed: {formatTime(timeElapsed)}
          </div>
          <div className="text-xs text-gray-400">
            💡 Large files may take 2-5 minutes to process completely
          </div>
        </div>

        {/* Processing Steps Indicator */}
        <div className="mt-6 flex justify-center space-x-2">
          {['📄', '🔍', '🧠', '📊', '✨'].map((emoji, index) => (
            <div
              key={index}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm transition-all duration-300 ${
                overallProgress > index * 20 
                  ? 'bg-blue-100 text-blue-600 scale-110' 
                  : 'bg-gray-100 text-gray-400'
              }`}
            >
              {emoji}
            </div>
          ))}
        </div>
        
        <div className="mt-2 flex justify-center space-x-4 text-xs text-gray-500">
          <span>Upload</span>
          <span>Extract</span>
          <span>Analyze</span>
          <span>Score</span>
          <span>Report</span>
        </div>
      </div>
    </div>
  )
}

export default ProgressLoader
