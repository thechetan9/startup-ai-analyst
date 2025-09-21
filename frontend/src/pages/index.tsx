import React, { useState, useEffect, useCallback, useMemo } from 'react'
import Head from 'next/head'
import { useDropzone } from 'react-dropzone'
import { useRouter } from 'next/router'
import axios from 'axios'
import dynamic from 'next/dynamic'
import confetti from 'canvas-confetti'
import {
  TrendingUp,
  FileText,
  Upload,
  BarChart3,
  Target,
  CheckCircle,
  DollarSign,
  Users,
  Plus,
  Rocket,
  Zap,
  ArrowRight
} from 'lucide-react'
import Footer from '../components/Footer'

// Loading components (defined outside to prevent re-creation)
const ChartLoading = () => (
  <div className="h-80 bg-gray-100 rounded-lg animate-pulse flex items-center justify-center">
    Loading chart...
  </div>
)

// Dynamically import Chart.js to avoid SSR issues
const Chart = dynamic(() => import('../components/Chart'), {
  ssr: false,
  loading: ChartLoading
})

// Import the new progress loader
const ProgressLoader = dynamic(() => import('../components/ProgressLoader'), {
  ssr: false
})

// Removed FirestoreService - using BigQuery only
import { AnalysisResult as EnhancedAnalysisResult, StartupProfile } from '../types/enhanced'
import AnalyticsDashboard from '../components/AnalyticsDashboard'
import { API_CONFIG, getApiUrl, isBackendAvailable } from '../config/api'

interface AnalysisResult {
  company_name: string
  score: number
  recommendation: string
  analysis: string
  document_count: number
  processed_files: string[]
  file_types: string[]
  extracted_metrics?: {
    revenue?: string
    users?: string
    growth_rate?: string
    funding?: string
  }
  sector_benchmarks?: {
    detected_sector?: string
    avg_valuation_multiple?: number
    avg_growth_rate?: number
    avg_funding_stage?: string
    key_metrics?: string[]
    benchmark_companies?: string[]
  }
  market_data?: {
    news_sentiment?: string
    market_trend?: string
    competitive_landscape?: string
    hiring_trends?: string
  }
  id?: string
  saved_date?: string
  structured_data: {
    investment_score: number
    recommendation: string
    executive_summary: string
    key_strengths: string[]
    main_concerns: string[]
    market_analysis: {
      market_size: string
      growth_potential: string
      competition_level: string
      market_summary: string
    }
    team_analysis: {
      team_strength: string
      experience_level: string
      team_summary: string
    }
    financial_analysis: {
      revenue_model: string
      financial_health: string
      funding_stage: string
      financial_summary: string
    }
    risk_assessment: {
      overall_risk: string
      key_risks: string[]
    }
    scoring_breakdown: {
      market: number
      team: number
      product: number
      financials: number
      execution: number
      market_opportunity: number
      team_quality: number
      product_innovation: number
      financial_potential: number
      execution_capability: number
    }
    sector_comparison?: {
      vs_sector_average?: string
      valuation_multiple_vs_peers?: string
      growth_vs_sector?: string
      competitive_position?: string
      sector_outlook?: string
    }
  }
}

export default function Home() {
  const router = useRouter()
  const [files, setFiles] = useState<File[]>([])
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState('')
  const [savedAnalyses, setSavedAnalyses] = useState<AnalysisResult[]>([])
  const [showComparison, setShowComparison] = useState(false)
  const [currentDocumentId, setCurrentDocumentId] = useState<string | null>(null)

  // Enhanced state for Firebase integration
  const [allAnalyses, setAllAnalyses] = useState<EnhancedAnalysisResult[]>([])
  const [startupProfiles, setStartupProfiles] = useState<StartupProfile[]>([])
  const [loading, setLoading] = useState(false)


  // Load analyses from backend on component mount
  useEffect(() => {
    loadAnalysesFromBackend()
  }, [])



  const loadAnalysesFromBackend = async () => {
    try {
      setLoading(true)

      // First try to load from backend (BigQuery)
      if (isBackendAvailable()) {
        try {
          console.log('🔍 Main page: Trying to load from backend...')
          const response = await axios.get(getApiUrl(API_CONFIG.ENDPOINTS.ANALYSES), {
            timeout: API_CONFIG.REQUEST_TIMEOUT
          })
          console.log('📊 Main page: Backend response:', response.data)

          // Check if we have valid response data
          if (response.data && response.data.analyses && Array.isArray(response.data.analyses)) {
            console.log('📊 Main page: Found', response.data.analyses.length, 'analyses from backend')

            // Convert backend format to frontend format
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
                console.warn('Failed to parse fileTypes:', analysis.fileTypes);
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
                keyFindings: [],
                riskFactors: [],
                opportunities: [],
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
                  executive_summary: analysis.executive_summary || '',
                  sector_comparison: {}
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
            console.log('✅ Loaded analyses from BigQuery:', uniqueAnalyses.length)
            return // Successfully loaded from backend, exit function
          } else {
            console.log('⚠️ Backend response format invalid, trying Firestore...')
          }
        } catch (backendError) {
          console.log('❌ Backend error:', backendError)
          console.log('❌ Backend not available - no fallback storage')
          setAllAnalyses([])
          setStartupProfiles([])
        }
      }
    } catch (error) {
      console.error('❌ Failed to load analyses from Firestore:', error)
    } finally {
      setLoading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    multiple: true,
    maxSize: 200 * 1024 * 1024, // 200MB limit
    onDrop: (acceptedFiles, rejectedFiles) => {
      // Handle accepted files - replace existing files to avoid duplicates
      setFiles(acceptedFiles)
      setError('') // Clear any previous errors

      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const rejectedMessages = rejectedFiles.map(rejection => {
          const file = rejection.file
          const errors = rejection.errors.map(error => {
            if (error.code === 'file-too-large') {
              return `${file.name} is too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Maximum: 200MB`
            }
            if (error.code === 'file-invalid-type') {
              return `${file.name} has unsupported format. Use PDF, DOC, or DOCX only`
            }
            return error.message
          })
          return errors.join(', ')
        })
        setError(rejectedMessages.join('\n'))
      } else {
        setError(null)
      }
    }
  })

  const removeFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }, [])

  const clearAllFiles = useCallback(() => {
    setFiles([])
  }, [])

  const saveAnalysisForComparison = () => {
    if (!result) return

    // Check if this analysis is already saved (prevent duplicates)
    // Use more robust duplicate detection based on company name and similar score
    const isAlreadySaved = savedAnalyses.some(analysis =>
      analysis.company_name === result.company_name &&
      Math.abs(analysis.score - result.score) < 2 // Allow 2-point difference
    )

    if (isAlreadySaved) {
      setError('⚠️ This analysis is already saved for comparison!')
      setTimeout(() => setError(''), 3000)
      return
    }

    const analysisWithId = {
      ...result,
      id: Date.now().toString(),
      saved_date: new Date().toISOString()
    }

    setSavedAnalyses(prev => {
      const updated = [...prev, analysisWithId]
      // Keep only last 5 analyses
      const final = updated.slice(-5)

      // TODO: Save to localStorage later
      // try {
      //   localStorage.setItem('savedAnalyses', JSON.stringify(final))
      // } catch (error) {
      //   console.error('Failed to save analyses to localStorage:', error)
      // }

      return final
    })

    // Show success message briefly with green styling
    setError('')
    setSuccessMessage('✅ Analysis saved for comparison!')
    setTimeout(() => setSuccessMessage(''), 2000)
  }

  // Utility function to remove undefined values from objects (Firestore doesn't allow undefined)
  const cleanUndefinedValues = (obj: any): any => {
    if (obj === null || obj === undefined) return null
    if (typeof obj !== 'object') return obj
    if (Array.isArray(obj)) return obj.map(cleanUndefinedValues)

    const cleaned: any = {}
    for (const [key, value] of Object.entries(obj)) {
      if (value !== undefined) {
        cleaned[key] = cleanUndefinedValues(value)
      }
    }
    return cleaned
  }

  // Save analysis directly to BigQuery (no Firestore)
  const saveAnalysisToBigQuery = async (companyData: any) => {
    try {
      console.log('💾 saveAnalysisToBigQuery called with:', companyData)
      console.log('🔍 DEBUG: Available keys in companyData:', Object.keys(companyData))
      console.log('🔍 DEBUG: key_strengths =', companyData.key_strengths)
      console.log('🔍 DEBUG: main_concerns =', companyData.main_concerns)
      console.log('🔍 DEBUG: executive_summary =', companyData.executive_summary)
      console.log('🔍 DEBUG: scoring_breakdown =', companyData.scoring_breakdown)

      // Validate required fields
      if (!companyData?.company_name || companyData.company_name.trim() === '') {
        console.error('❌ Cannot save: Missing company name')
        return
      }

      // Check for duplicates before saving - more strict duplicate detection
      const isDuplicate = allAnalyses.some(analysis => {
        const isSameCompany = analysis.companyName === companyData.company_name
        const isSimilarScore = Math.abs(analysis.score - (companyData.score || 0)) < 5
        const isRecentlySaved = new Date().getTime() - new Date(analysis.createdAt || (analysis as any).analysis_timestamp).getTime() < 60000 // Within 1 minute

        return isSameCompany && (isSimilarScore || isRecentlySaved)
      })

      if (isDuplicate) {
        console.log(`⚠️ Skipping duplicate: ${companyData.company_name} (already exists with similar score or recently saved)`)
        return
      }

      // Prepare complete data for BigQuery
      const backendData = {
        analysis_id: companyData.document_id || `analysis-${Date.now()}`,
        company_name: companyData.company_name,
        sector: companyData.sector || 'Unknown',
        score: companyData.score,
        recommendation: companyData.recommendation,
        analysis_text: companyData.analysis || '',
        revenue: companyData.extracted_metrics?.revenue || 0,
        growth_rate: companyData.extracted_metrics?.growth_rate || 0,
        funding: companyData.extracted_metrics?.funding || 0,
        document_count: companyData.document_count || 1,
        file_types: JSON.stringify(companyData.file_types || ['pdf']),
        analysis_timestamp: new Date().toISOString(),
        confidence_score: companyData.confidence || 0.8,
        // Add complete analysis content fields
        key_strengths: companyData.key_strengths || [],
        main_concerns: companyData.main_concerns || [],
        executive_summary: companyData.executive_summary || '',
        // Add scoring breakdown fields
        market_opportunity_score: companyData.scoring_breakdown?.market_opportunity || 0,
        team_quality_score: companyData.scoring_breakdown?.team_quality || 0,
        product_innovation_score: companyData.scoring_breakdown?.product_innovation || 0,
        financial_potential_score: companyData.scoring_breakdown?.financial_potential || 0,
        execution_capability_score: companyData.scoring_breakdown?.execution_capability || 0
      }

      // Send directly to BigQuery backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://startup-ai-analyst-backend-281259205924.us-central1.run.app'}/api/analyses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendData)
      })

      if (response.ok) {
        console.log(`✅ Saved ${companyData.company_name} to BigQuery`)
      } else {
        console.error(`❌ Failed to save ${companyData.company_name} to BigQuery:`, await response.text())
      }
    } catch (error) {
      console.error(`❌ Failed to save ${companyData.company_name}:`, error)
    }
  }

  // Removed saveAnalysisToFirestore - using BigQuery only

  const clearSavedAnalyses = () => {
    setSavedAnalyses([])
    // TODO: Clear from localStorage later
    // try {
    //   localStorage.removeItem('savedAnalyses')
    // } catch (error) {
    //   console.error('Failed to clear saved analyses from localStorage:', error)
    // }
  }

  // File management functions are already declared above

  const exportToPDF = async () => {
    if (!result) return

    try {
      const { jsPDF } = await import('jspdf')
      const pdf = new jsPDF()

      // Set up the PDF with UTF-8 support
      const pageWidth = pdf.internal.pageSize.width
      const margin = 20
      let yPosition = margin

      // Helper function to clean and add text with word wrapping
      const addText = (text: string, fontSize: number = 12, isBold: boolean = false) => {
        // Clean text to remove special characters that cause issues
        const cleanText = text
          .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII characters
          .replace(/\s+/g, ' ') // Normalize whitespace
          .trim()

        if (!cleanText) return

        pdf.setFontSize(fontSize)
        if (isBold) pdf.setFont(undefined, 'bold')
        else pdf.setFont(undefined, 'normal')

        const lines = pdf.splitTextToSize(cleanText, pageWidth - 2 * margin)
        pdf.text(lines, margin, yPosition)
        yPosition += lines.length * (fontSize * 0.4) + 5

        // Add new page if needed
        if (yPosition > pdf.internal.pageSize.height - margin) {
          pdf.addPage()
          yPosition = margin
        }
      }

      // Title
      addText(`🚀 AI Startup Analysis Report`, 20, true)
      addText(`Company: ${result.company_name}`, 16, true)
      addText(`Analysis Date: ${new Date().toLocaleDateString()}`, 12)
      addText(`Documents Analyzed: ${result.processed_files && result.processed_files.length > 0 ? result.processed_files.join(', ') : 'N/A'}`, 12)
      yPosition += 10

      // Score and Recommendation
      addText(`📊 INVESTMENT SCORE: ${result.score}/100`, 16, true)
      addText(`💡 RECOMMENDATION: ${result.recommendation}`, 14, true)
      yPosition += 10

      // Executive Summary
      if (result.structured_data?.executive_summary) {
        addText('📋 EXECUTIVE SUMMARY', 14, true)
        addText(result.structured_data.executive_summary, 11)
        yPosition += 5
      }

      // Key Metrics
      if (result.extracted_metrics && Object.keys(result.extracted_metrics).length > 0) {
        addText('📊 KEY METRICS EXTRACTED', 14, true)
        Object.entries(result.extracted_metrics).forEach(([key, value]) => {
          addText(`• ${key.replace('_', ' ').toUpperCase()}: ${value}`, 11)
        })
        yPosition += 5
      }

      // Scoring Breakdown
      if (result.structured_data?.scoring_breakdown) {
        addText('📈 SCORING BREAKDOWN', 14, true)
        const scores = result.structured_data.scoring_breakdown
        addText(`• Market Opportunity: ${scores.market_opportunity || 0}/100`, 11)
        addText(`• Team Quality: ${scores.team_quality || 0}/100`, 11)
        addText(`• Product Innovation: ${scores.product_innovation || 0}/100`, 11)
        addText(`• Financial Potential: ${scores.financial_potential || 0}/100`, 11)
        addText(`• Execution Capability: ${scores.execution_capability || 0}/100`, 11)
        yPosition += 5
      }

      // Key Strengths
      if (result.structured_data?.key_strengths) {
        addText('✅ KEY STRENGTHS', 14, true)
        result.structured_data.key_strengths.forEach((strength: string) => {
          addText(`• ${strength}`, 11)
        })
        yPosition += 5
      }

      // Main Concerns
      if (result.structured_data?.main_concerns) {
        addText('⚠️ MAIN CONCERNS', 14, true)
        result.structured_data.main_concerns.forEach((concern: string) => {
          addText(`• ${concern}`, 11)
        })
        yPosition += 5
      }

      // Risk Assessment
      if (result.structured_data?.risk_assessment) {
        addText('⚡ RISK ASSESSMENT', 14, true)
        addText(`Overall Risk Level: ${result.structured_data.risk_assessment.overall_risk}`, 12, true)
        if (result.structured_data.risk_assessment.key_risks) {
          result.structured_data.risk_assessment.key_risks.forEach((risk: string) => {
            addText(`• ${risk}`, 11)
          })
        }
      }

      // Footer
      pdf.setFontSize(8)
      pdf.setFont(undefined, 'normal')
      pdf.text('Generated by AI Startup Analyst Platform', margin, pdf.internal.pageSize.height - 10)

      // Save the PDF
      const fileName = `${result.company_name.replace(/\s+/g, '_')}_Analysis_Report_${new Date().toISOString().split('T')[0]}.pdf`
      pdf.save(fileName)

    } catch (error) {
      console.error('PDF export failed:', error)
      setError('Failed to export PDF. Please try again.')
    }
  }


  const handleAnalyze = async () => {
    if (files.length === 0) {
      setError('Please select at least one file')
      return
    }

    setAnalyzing(true)
    setError(null)
    setResult(null)
    setCurrentDocumentId(null)

    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      const response = await axios.post(getApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: API_CONFIG.REQUEST_TIMEOUT
      })

      // Set the document ID for progress tracking
      if (response.data.document_id) {
        setCurrentDocumentId(response.data.document_id)
      }

      setResult(response.data)
    } catch (err: any) {
      console.error('Analysis failed:', err)
      let errorMessage = 'Analysis failed. Please try again.'

      if (err.response?.status === 413) {
        errorMessage = '📄 Files are too large. Please upload smaller documents (max 50MB each).'
      } else if (err.response?.status === 400) {
        errorMessage = '📄 Invalid file format. Please upload PDF, DOC, or DOCX files only.'
      } else if (err.code === 'NETWORK_ERROR' || err.code === 'ECONNABORTED') {
        errorMessage = '🌐 Request timeout. Large files may take longer to process. Please try again.'
      } else if (err.response?.data?.detail) {
        errorMessage = `⚠️ ${err.response.data.detail}`
      }

      setError(errorMessage)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleProgressComplete = useCallback(async (results: any) => {
    console.log('Processing completed:', results)
    setResult(results)
    setAnalyzing(false)

    // Auto-save the analysis to BigQuery
    try {
      console.log('🔄 Auto-saving analysis to BigQuery...', results)
      await saveAnalysisToBigQuery(results)
      console.log('✅ Analysis auto-saved successfully!')

      // Refresh the analyses list
      console.log('🔄 Refreshing analyses list...')
      await loadAnalysesFromBackend()
      console.log('✅ Analyses list refreshed!')
    } catch (error) {
      console.error('❌ Failed to auto-save analysis:', error)
      // Still show success message even if save failed
      console.log('⚠️ Continuing despite save error...')
    }

    // 🎉 Trigger confetti celebration
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    })

    // Show success message
    setSuccessMessage('🎉 Analysis completed and saved successfully! Redirecting to dashboard...')

    // Auto-redirect to dashboard after celebration
    setTimeout(() => {
      console.log('🎯 Redirecting to dashboard with company:', results.company_name)
      router.push(`/dashboard?scrollTo=${encodeURIComponent(results.company_name || 'latest')}`)
    }, 2000) // 2 second delay to show confetti and message
  }, [router])

  const handleProgressError = useCallback((error: string) => {
    console.error('Processing error:', error)
    setError(error)
    setAnalyzing(false)
  }, [])

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'INVEST': return 'text-green-600 bg-green-100 border-green-200'
      case 'MONITOR': return 'text-yellow-600 bg-yellow-100 border-yellow-200'
      case 'PASS': return 'text-red-600 bg-red-100 border-red-200'
      default: return 'text-gray-600 bg-gray-100 border-gray-200'
    }
  }

  return (
    <>
      <Head>
        <title>AI Startup Analyst Platform</title>
        <meta name="description" content="AI-powered startup investment analysis" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-2 sm:px-4 py-4 sm:py-8">
          {/* Header */}
          <div className="text-center mb-6 sm:mb-12">
            <div className="flex items-center justify-center mb-4">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-full mr-4">
                <Rocket className="h-8 w-8 sm:h-12 sm:w-12 text-white" />
              </div>
              <h1 className="text-2xl sm:text-4xl lg:text-5xl font-bold text-gray-900">
                AI Startup Analyst
              </h1>
            </div>
            <p className="text-lg sm:text-xl text-gray-600 px-2">
              Upload startup documents for AI-powered investment analysis
            </p>
          </div>

          {/* Upload Section */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-4 sm:p-8 mb-4 sm:mb-8">
              <div className="flex items-center mb-4 sm:mb-6">
                <FileText className="h-6 w-6 text-blue-600 mr-3" />
                <h2 className="text-xl sm:text-2xl font-semibold">Upload Documents</h2>
              </div>
              


              {/* File Upload */}
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${
                  isDragActive 
                    ? 'border-blue-400 bg-blue-50 scale-105' 
                    : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                }`}
              >
                <input {...getInputProps()} />
                <div className="text-gray-600">
                  {isDragActive ? (
                    <div className="flex items-center justify-center">
                      <Upload className="h-8 w-8 text-blue-600 mr-3" />
                      <p className="text-lg font-medium text-blue-600">Drop the files here...</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-lg font-medium mb-2">Drag & drop files here, or click to select</p>
                      <p className="text-sm text-gray-500">Supports PDF, DOCX, DOC files</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Selected Files */}
              {files.length > 0 && (
                <div className="mt-6 bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-700">
                      ✅ Selected Files ({files.length})
                    </h3>
                    <button
                      onClick={clearAllFiles}
                      className="text-sm text-red-600 hover:text-red-800 font-medium"
                    >
                      Clear All
                    </button>
                  </div>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {files.map((file, index) => {
                      const fileSizeMB = file.size / 1024 / 1024
                      const isLarge = fileSizeMB > 50
                      const isVeryLarge = fileSizeMB > 100

                      return (
                        <div key={index} className="flex items-center text-sm text-gray-600 bg-white rounded p-3 shadow-sm">
                          <div className="flex-1">
                            <div className="font-medium flex items-center">
                              <FileText className="h-4 w-4 text-blue-600 mr-2" />
                              {file.name}
                              {isVeryLarge && <span className="ml-2 text-xs bg-red-100 text-red-600 px-2 py-1 rounded">Very Large</span>}
                              {isLarge && !isVeryLarge && <span className="ml-2 text-xs bg-yellow-100 text-yellow-600 px-2 py-1 rounded">Large</span>}
                            </div>
                            <div className="text-xs text-gray-400 mt-1 flex items-center">
                              <span>{fileSizeMB.toFixed(2)} MB • {file.type || 'Unknown type'}</span>
                              {isLarge && (
                                <span className="ml-2 text-xs text-blue-600">
                                  ⚡ Will use chunked processing
                                </span>
                              )}
                            </div>
                          </div>
                          <button
                            onClick={() => removeFile(index)}
                            className="ml-3 text-red-500 hover:text-red-700 font-bold text-lg"
                            title="Remove file"
                          >
                            ×
                          </button>
                        </div>
                      )
                    })}
                  </div>
                  <div className="mt-3 text-xs text-gray-500 text-center space-y-1">
                    <div>💡 Tip: Upload multiple related documents (pitch deck, financials, business plan) for better analysis</div>
                    {files.some(f => f.size > 50 * 1024 * 1024) && (
                      <div className="text-blue-600">
                        ⚡ Large files detected - processing may take 3-5 minutes with detailed progress tracking
                      </div>
                    )}
                    {files.some(f => f.size > 100 * 1024 * 1024) && (
                      <div className="text-orange-600">
                        🔧 Very large files will be processed in chunks to ensure reliability
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={analyzing || files.length === 0}
                className={`mt-8 w-full py-4 px-6 rounded-lg font-medium text-lg transition-all duration-200 ${
                  analyzing || files.length === 0
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 transform hover:scale-105 shadow-lg'
                }`}
              >
                {analyzing ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                    <span>🤖 Processing with AI...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center">
                    <Zap className="h-5 w-5 mr-2" />
                    Analyze with AI
                  </div>
                )}
              </button>

              {/* Dashboard Link - Only show if there are existing analyses */}
              {allAnalyses.length > 0 && (
                <div className="mt-6 text-center">
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="inline-flex items-center space-x-3 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-all duration-200 font-medium text-sm shadow-lg hover:shadow-xl transform hover:scale-105"
                  >
                    <BarChart3 className="h-5 w-5" />
                    <span>View Dashboard ({allAnalyses.length} analyses)</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
                <p className="text-red-600 font-medium">❌ {error}</p>
              </div>
            )}

            {/* Success Message Display */}
            {successMessage && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-8">
                <p className="text-green-600 font-medium">{successMessage}</p>
              </div>
            )}

            {/* Enhanced Results Display with Tabs */}
            {result && (
              <div id="results-section" className="space-y-4 sm:space-y-8">
                {/* Header Section */}
                <div className="bg-white rounded-xl shadow-lg p-4 sm:p-8">
                  <div className="border-l-4 border-blue-500 pl-4 sm:pl-6 mb-4 sm:mb-8">
                    <h2 className="text-xl sm:text-3xl font-bold text-gray-900 mb-2">{result.company_name}</h2>
                    <p className="text-sm sm:text-base text-gray-600 mb-4">
                      📄 Analyzed {result.document_count || 0} documents{result.processed_files && result.processed_files.length > 0 ? `: ${result.processed_files.slice(0, 2).join(', ')}${result.processed_files.length > 2 ? '...' : ''}` : ''}
                    </p>

                    {/* Show extracted metrics if available */}
                    {result.extracted_metrics && Object.keys(result.extracted_metrics).length > 0 && (
                      <div className="bg-blue-50 rounded-lg p-3 sm:p-4 mb-4">
                        <h4 className="font-semibold text-blue-800 mb-2 text-sm sm:text-base">📊 Key Metrics Extracted:</h4>
                        <div className="flex flex-wrap gap-2 sm:gap-4 text-xs sm:text-sm">
                          {result.extracted_metrics.revenue && (
                            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full flex items-center">
                              <DollarSign className="h-3 w-3 mr-1" />
                              Revenue: ${result.extracted_metrics.revenue}
                            </span>
                          )}
                          {result.extracted_metrics.users && (
                            <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full flex items-center">
                              <Users className="h-3 w-3 mr-1" />
                              Users: {result.extracted_metrics.users}
                            </span>
                          )}
                          {result.extracted_metrics.growth_rate && (
                            <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full flex items-center">
                              <TrendingUp className="h-3 w-3 mr-1" />
                              Growth: {result.extracted_metrics.growth_rate}
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
                      <div className="flex items-center justify-center sm:justify-start space-x-4 sm:space-x-6">
                        <div className="text-center">
                          <div className="text-2xl sm:text-4xl font-bold text-blue-600 mb-1">
                            {result.score}/100
                          </div>
                          <div className="text-xs sm:text-sm text-gray-500">Investment Score</div>
                        </div>
                        <div className={`px-4 sm:px-6 py-2 sm:py-3 rounded-full border font-bold text-sm sm:text-lg ${getRecommendationColor(result.recommendation)}`}>
                          {result.recommendation}
                        </div>
                      </div>

                      {/* Success Message and Next Steps */}
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3 sm:p-4 mt-4 sm:mt-0">
                        <div className="flex items-start space-x-2 sm:space-x-3">
                          <div className="flex-shrink-0">
                            <div className="w-6 h-6 sm:w-8 sm:h-8 bg-green-100 rounded-full flex items-center justify-center">
                              <CheckCircle className="h-4 w-4 sm:h-5 sm:w-5 text-green-600" />
                            </div>
                          </div>
                          <div className="flex-1">
                            <h3 className="text-xs sm:text-sm font-medium text-green-800 mb-1">
                              Analysis Complete!
                            </h3>
                            <p className="text-xs sm:text-sm text-green-700 mb-2 sm:mb-3">
                              Your startup analysis has been automatically saved. View it in your dashboard to compare with other analyses, export reports, and get deeper insights.
                            </p>
                            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
                              <button
                                onClick={async () => {
                                  try {
                                    // Auto-save to ensure it's in dashboard
                                    await saveAnalysisToBigQuery(result)
                                    // Navigate to dashboard with company name for auto-scroll
                                    const companyName = result?.company_name || 'Unknown'
                                    router.push(`/dashboard?scrollTo=${encodeURIComponent(companyName)}`)
                                  } catch (error) {
                                    console.error('Failed to save before navigation:', error)
                                    // Navigate anyway since analysis might already be saved
                                    const companyName = result?.company_name || 'Unknown'
                                    router.push(`/dashboard?scrollTo=${encodeURIComponent(companyName)}`)
                                  }
                                }}
                                className="inline-flex items-center justify-center space-x-2 px-3 sm:px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors font-medium text-xs sm:text-sm"
                              >
                                <BarChart3 className="h-4 w-4" />
                                <span>View in Dashboard</span>
                              </button>
                              <button
                                onClick={() => {
                                  setResult(null)
                                  setFiles([])
                                  setError('')
                                  setSuccessMessage('')
                                }}
                                className="inline-flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors font-medium text-sm"
                              >
                                <Plus className="h-4 w-4" />
                                <span>Analyze More Files</span>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>


              </div>
            )}

            {/* Simplified Upload Tips */}
            {!result && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 sm:p-6 mt-4 sm:mt-8 border border-blue-200">
                <div className="flex items-center mb-2 sm:mb-3">
                  <Zap className="h-4 w-4 text-blue-600 mr-2" />
                  <h3 className="font-semibold text-blue-800 text-sm sm:text-base">Tips for Better Analysis</h3>
                </div>
                <div className="text-xs sm:text-sm text-blue-700 space-y-1">
                  <p>• Upload multiple documents (pitch decks, financials, business plans)</p>
                  <p>• Supports PDF and Word documents</p>
                  <p>• AI analyzes all documents together for comprehensive insights</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dashboard is now a separate page */}

      {/* Comparison Modal - Removed for simplicity */}
      {false && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-2 sm:p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-3 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900">📊 Startup Comparison</h2>
              <button
                onClick={() => setShowComparison(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <p className="text-gray-600">
                  Comparison feature coming soon...
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="text-left p-3 font-semibold">Company</th>
                      <th className="text-center p-3 font-semibold">Score</th>
                      <th className="text-center p-3 font-semibold">Recommendation</th>
                      <th className="text-center p-3 font-semibold">Sector</th>
                      <th className="text-center p-3 font-semibold">Documents</th>
                      <th className="text-center p-3 font-semibold">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allAnalyses
                      .slice(0, 3)
                      .map((analysis) => (
                        <tr key={analysis.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="p-3 font-medium">{analysis.companyName}</td>
                          <td className="p-3 text-center">
                            <span className={`font-bold text-lg ${
                              analysis.score >= 80 ? 'text-green-600' :
                              analysis.score >= 60 ? 'text-yellow-600' :
                              analysis.score >= 40 ? 'text-orange-600' : 'text-red-600'
                            }`}>
                              {analysis.score}/100
                            </span>
                          </td>
                          <td className="p-3 text-center">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                              analysis.recommendation === 'INVEST' ? 'bg-green-100 text-green-800 border-green-200' :
                              analysis.recommendation === 'HOLD' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                              analysis.recommendation === 'DO_NOT_INVEST' ? 'bg-red-100 text-red-800 border-red-200' :
                              'bg-blue-100 text-blue-800 border-blue-200'
                            }`}>
                              {analysis.recommendation.replace(/_/g, ' ')}
                            </span>
                          </td>
                          <td className="p-3 text-center">
                            {analysis.sectorBenchmarks?.sector || 'Unknown'}
                          </td>
                          <td className="p-3 text-center">{analysis.documentCount || 0}</td>
                          <td className="p-3 text-center text-sm text-gray-500">
                            {new Date(analysis.createdAt).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-6 text-sm text-gray-600 bg-blue-50 rounded-lg p-4">
                💡 <strong>Comparison Insights:</strong> Use this table to evaluate multiple startups side-by-side.
                Higher scores indicate better investment opportunities. Consider sector, recommendation, and document quality when making decisions.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Progress Loader */}
      <ProgressLoader
        isVisible={analyzing}
        documentIds={currentDocumentId ? [currentDocumentId] : []}
        onComplete={handleProgressComplete}
        onError={handleProgressError}
      />

      <Footer />
    </>
  )
}
