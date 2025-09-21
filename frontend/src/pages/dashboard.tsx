import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import axios from 'axios'
import { ArrowLeft, BarChart3, FileText } from 'lucide-react'
// Removed FirestoreService - using BigQuery only
import AnalyticsDashboard from '../components/AnalyticsDashboard'
import Footer from '../components/Footer'
import { AnalysisResult, StartupProfile } from '../types/enhanced'
import { API_CONFIG, getApiUrl, isBackendAvailable } from '../config/api'

// Using AnalysisResult from types/enhanced.ts

export default function Dashboard() {
  const router = useRouter()
  const [allAnalyses, setAllAnalyses] = useState<AnalysisResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showComparison, setShowComparison] = useState(false)
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>([])
  const { scrollTo } = router.query

  // Load analyses from backend (BigQuery only)
  const loadAnalysesFromBackend = async () => {
    try {
      setLoading(true)

      // First try to load from backend (BigQuery)
      try {
        console.log('🔍 Dashboard: Trying to load from backend...')
        const response = await axios.get(getApiUrl(API_CONFIG.ENDPOINTS.ANALYSES), {
          timeout: API_CONFIG.REQUEST_TIMEOUT
        })
        console.log('📊 Dashboard: Backend response:', response.data)

        // Check if we have valid response data
        if (response.data && response.data.analyses && Array.isArray(response.data.analyses)) {
          console.log('📊 Dashboard: Found', response.data.analyses.length, 'analyses from backend')

          // Convert backend format to frontend format with rich data
          const backendAnalyses = response.data.analyses.map((analysis: any) => {
            // Parse fileTypes if it's a JSON string
            let fileTypes = [];
            try {
              if (typeof analysis.fileTypes === 'string') {
                fileTypes = JSON.parse(analysis.fileTypes);
              } else if (Array.isArray(analysis.fileTypes)) {
                fileTypes = analysis.fileTypes;
              }
            } catch (e) {
              console.warn('Dashboard: Failed to parse fileTypes:', analysis.fileTypes);
              fileTypes = [];
            }

            return {
              id: analysis.id || `backend-${Date.now()}-${Math.random()}`,
              startupId: analysis.id || `startup-${Date.now()}`,
              documentId: analysis.id || `doc-${Date.now()}`,
              companyName: analysis.companyName || 'Unknown Company',
              score: analysis.score || 0,
              recommendation: analysis.recommendation || 'FURTHER_DUE_DILIGENCE_REQUIRED',
              analysis: analysis.analysis || `Analysis for ${analysis.companyName || 'Unknown Company'}`,
              executive_summary: analysis.executive_summary || '',
              keyFindings: analysis.keyFindings || [],
              riskFactors: analysis.riskFactors || [],
              opportunities: analysis.opportunities || [],
              structuredData: {
                financials: {
                  revenue: analysis.revenue || 0,
                  growth: analysis.growthRate || 0
                },
                scoring_breakdown: analysis.scoring_breakdown || {
                  market_opportunity: (analysis.score || 0) * 0.2,
                  team_quality: (analysis.score || 0) * 0.2,
                  product_innovation: (analysis.score || 0) * 0.2,
                  financial_potential: (analysis.score || 0) * 0.2,
                  execution_capability: (analysis.score || 0) * 0.2
                },
                main_concerns: analysis.main_concerns || [],
                key_strengths: analysis.key_strengths || [],
                sector_comparison: analysis.sector_comparison || {}
              },
              sectorBenchmarks: {
                sector: analysis.sector || 'Unknown'
              },
              processedFiles: fileTypes.map((type: string) => `document.${type}`),
              fileTypes: fileTypes,
              documentCount: analysis.documentCount || 0,
              analysisVersion: '1.0',
              confidence: analysis.confidence || 0.8,
              createdAt: new Date(analysis.createdAt || Date.now())
            }
          })

          // Remove exact duplicates only (same company, same score, same date)
          const uniqueAnalyses = backendAnalyses.filter((analysis, index, self) =>
            index === self.findIndex(a =>
              a.companyName === analysis.companyName &&
              a.score === analysis.score &&
              a.createdAt.getTime() === analysis.createdAt.getTime()
            )
          )

          setAllAnalyses(uniqueAnalyses)
          console.log('✅ Dashboard loaded analyses from BigQuery:', uniqueAnalyses.length)
          return // Successfully loaded from backend, exit function
        } else {
          console.log('⚠️ Dashboard: Backend response format invalid, trying Firestore...')
        }
      } catch (backendError) {
        console.log('❌ Dashboard backend error:', error)
        console.log('❌ Backend not available for dashboard')
        setAllAnalyses([])
        setError('Failed to connect to backend')
      }
    } catch (error) {
      console.error('❌ Failed to load analyses for dashboard:', error)
      setError('Failed to load analyses from database')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAnalysesFromBackend()
  }, [])

  // Auto-scroll to specific company when scrollTo parameter is present
  useEffect(() => {
    if (scrollTo && allAnalyses.length > 0) {
      const targetCompany = decodeURIComponent(scrollTo as string)
      console.log(`🎯 Auto-scrolling to company: ${targetCompany}`)

      // Wait a bit for the DOM to render
      setTimeout(() => {
        // Find the company card by company name
        const companyCard = document.querySelector(`[data-company-name="${targetCompany}"]`)
        if (companyCard) {
          companyCard.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          })
          console.log(`✅ Scrolled to company: ${targetCompany}`)

          // Add a highlight effect
          companyCard.classList.add('ring-4', 'ring-blue-500', 'ring-opacity-50')
          setTimeout(() => {
            companyCard.classList.remove('ring-4', 'ring-blue-500', 'ring-opacity-50')
          }, 3000)
        } else {
          console.log(`❌ Company card not found: ${targetCompany}`)
        }
      }, 500)
    }
  }, [scrollTo, allAnalyses])

  const handleBackToHome = () => {
    router.push('/')
  }

  const handleCompareSelected = (analysisIds: string[]) => {
    console.log('Dashboard: Compare selected called with:', analysisIds)
    setSelectedForComparison(analysisIds)
    setShowComparison(true)
  }

  const handleDeleteAnalysis = async (analysisId: string) => {
    // Show confirmation dialog
    if (!confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
      return
    }

    try {
      console.log('🗑️ Deleting analysis from BigQuery:', analysisId)

      // Delete from BigQuery (only storage)
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://startup-ai-analyst-backend-281259205924.us-central1.run.app'
      const response = await axios.delete(`${backendUrl}/api/analyses/${analysisId}`, {
        timeout: API_CONFIG.REQUEST_TIMEOUT
      })

      if (response.data.success) {
        console.log('✅ Analysis deleted from BigQuery')

        // Refresh the analyses list
        await loadAnalysesFromBackend()

        alert('Analysis deleted successfully!')
      } else {
        throw new Error(response.data.message || 'Delete failed')
      }

    } catch (error) {
      console.error('❌ Failed to delete analysis:', error)
      alert('Failed to delete analysis. Please try again.')
    }
  }

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'INVEST': return 'bg-green-100 text-green-800 border-green-200'
      case 'HOLD': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'DO_NOT_INVEST': return 'bg-red-100 text-red-800 border-red-200'
      case 'FURTHER_DUE_DILIGENCE_REQUIRED': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    if (score >= 40) return 'text-orange-600'
    return 'text-red-600'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2 sm:space-x-4">
              <button
                onClick={handleBackToHome}
                className="inline-flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors text-sm sm:text-base"
              >
                <ArrowLeft className="h-4 w-4" />
                <span className="hidden sm:inline">Back to Analyzer</span>
                <span className="sm:hidden">Back</span>
              </button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center">
                <BarChart3 className="h-6 w-6 text-blue-600 mr-3" />
                <h1 className="text-lg sm:text-2xl font-bold text-gray-900">
                  <span className="hidden sm:inline">Investment Analytics</span> Dashboard
                </h1>
              </div>
            </div>
            <div className="text-xs sm:text-sm text-gray-500">
              {allAnalyses.length} {allAnalyses.length === 1 ? 'Analysis' : 'Analyses'}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading analyses...</span>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
            <button
              onClick={loadAnalysesFromBackend}
              className="mt-2 text-red-600 hover:text-red-800 underline"
            >
              Try Again
            </button>
          </div>
        ) : allAnalyses.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Analyses Yet</h3>
            <p className="text-gray-600 mb-6">Start by analyzing some startup documents to see insights here.</p>
            <button
              onClick={handleBackToHome}
              className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <FileText className="h-5 w-5" />
              <span>Analyze Documents</span>
            </button>
          </div>
        ) : (
          <AnalyticsDashboard
            analyses={allAnalyses}
            onRefresh={loadAnalysesFromBackend}
            onCompareSelected={handleCompareSelected}
            onDeleteAnalysis={handleDeleteAnalysis}
          />
        )}
      </div>

      {/* Comparison Modal */}
      {showComparison && selectedForComparison.length > 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-4 sm:px-6 py-4 flex items-center justify-between">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900">📊 Startup Comparison</h2>
              <button
                onClick={() => setShowComparison(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>
            <div className="p-4 sm:p-6">
              <div className="mb-4">
                <p className="text-gray-600 text-sm sm:text-base">
                  Comparing {selectedForComparison.length} selected startups
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full border-collapse min-w-[600px]">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="text-left p-2 sm:p-3 font-semibold text-sm sm:text-base">Company</th>
                      <th className="text-center p-2 sm:p-3 font-semibold text-sm sm:text-base">Score</th>
                      <th className="text-center p-2 sm:p-3 font-semibold text-sm sm:text-base">Recommendation</th>
                      <th className="text-center p-2 sm:p-3 font-semibold text-sm sm:text-base">Sector</th>
                      <th className="text-center p-2 sm:p-3 font-semibold text-sm sm:text-base hidden sm:table-cell">Documents</th>
                      <th className="text-center p-2 sm:p-3 font-semibold text-sm sm:text-base hidden md:table-cell">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allAnalyses
                      .filter(analysis => selectedForComparison.includes(analysis.id))
                      .map((analysis) => (
                        <tr key={analysis.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="p-2 sm:p-3 font-medium text-sm sm:text-base">{analysis.companyName}</td>
                          <td className={`p-2 sm:p-3 text-center font-bold text-lg sm:text-xl ${getScoreColor(analysis.score)}`}>
                            {analysis.score}
                          </td>
                          <td className="p-2 sm:p-3 text-center">
                            <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium border ${
                              getRecommendationColor(analysis.recommendation)
                            }`}>
                              {analysis.recommendation.replace(/_/g, ' ')}
                            </span>
                          </td>
                          <td className="p-2 sm:p-3 text-center text-sm sm:text-base">
                            {analysis.sectorBenchmarks?.sector || 'Unknown'}
                          </td>
                          <td className="p-2 sm:p-3 text-center text-sm sm:text-base hidden sm:table-cell">{analysis.documentCount || 0}</td>
                          <td className="p-2 sm:p-3 text-center text-xs sm:text-sm text-gray-500 hidden md:table-cell">
                            {new Date(analysis.createdAt).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-6 text-xs sm:text-sm text-gray-600 bg-blue-50 rounded-lg p-4">
                💡 <strong>Comparison Insights:</strong> Use this table to evaluate multiple startups side-by-side.
                Higher scores indicate better investment opportunities. Consider sector, recommendation, and document quality when making decisions.
              </div>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  )
}
