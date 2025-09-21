import React, { useState, useEffect } from 'react'
import {
  BarChart3,
  FileText,
  Download,
  Eye,
  Trash2,
  Filter,
  ChevronLeft,
  ChevronRight,
  Building2,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Target,
  Users,
  DollarSign
} from 'lucide-react'
import { AnalysisResult, StartupProfile } from '../types/enhanced'
import { FirestoreService } from '../services/firestore'
import DetailedAnalysisView from './DetailedAnalysisView'
import InvestmentCharts from './InvestmentCharts'

interface AnalyticsDashboardProps {
  analyses: AnalysisResult[]
  startups?: StartupProfile[]
  onCompareSelected?: (analysisIds: string[]) => void
  onRefresh?: () => void
  onDeleteAnalysis?: (analysisId: string) => void
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  analyses,
  startups,
  onCompareSelected,
  onDeleteAnalysis
}) => {
  const [selectedAnalyses, setSelectedAnalyses] = useState<string[]>([])
  const [filterSector, setFilterSector] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'score' | 'date' | 'company'>('date')
  const [selectedAnalysisForDetail, setSelectedAnalysisForDetail] = useState<AnalysisResult | null>(null)

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(12)
  const [hideDuplicates, setHideDuplicates] = useState(true) // Hide duplicates by default

  // Get unique sectors - handle both old and new data structures
  const sectors = Array.from(new Set(
    analyses.map(a =>
      a.sectorBenchmarks?.sector ||
      (a as any).sector_benchmarks?.detected_sector ||
      'Unknown'
    ).filter(Boolean)
  ))

  // Duplicate detection logic - group by company name only
  const findDuplicates = () => {
    const duplicateGroups: { [key: string]: AnalysisResult[] } = {}

    analyses.forEach(analysis => {
      const key = analysis.companyName.toLowerCase().trim() // Group by name only
      if (!duplicateGroups[key]) {
        duplicateGroups[key] = []
      }
      duplicateGroups[key].push(analysis)
    })

    return Object.values(duplicateGroups).filter(group => group.length > 1)
  }

  const duplicateGroups = findDuplicates()
  const duplicateIds = new Set(
    duplicateGroups.flatMap(group => {
      // Sort by date (most recent first) and keep the most recent one
      const sortedGroup = group.sort((a, b) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      )
      // Mark all except the most recent as duplicates
      return sortedGroup.slice(1).map(analysis => analysis.id)
    })
  )

  // Filter and sort analyses - handle both old and new data structures
  const filteredAnalyses = analyses
    .filter(analysis => {
      const sector = analysis.sectorBenchmarks?.sector ||
                    (analysis as any).sector_benchmarks?.detected_sector ||
                    'Unknown'
      const sectorMatch = filterSector === 'all' || sector === filterSector

      const statusMatch = filterStatus === 'all' || analysis.recommendation === filterStatus

      // Hide duplicates if option is enabled
      const duplicateMatch = !hideDuplicates || !duplicateIds.has(analysis.id)

      return sectorMatch && statusMatch && duplicateMatch
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.score - a.score
        case 'company':
          return a.companyName.localeCompare(b.companyName)
        case 'date':
        default:
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      }
    })

  // Pagination calculations
  const totalItems = filteredAnalyses.length
  const totalPages = Math.ceil(totalItems / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedAnalyses = filteredAnalyses.slice(startIndex, endIndex)

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filterSector, filterStatus, sortBy, hideDuplicates])



  // Delete analysis function
  const handleDeleteAnalysis = async (analysisId: string) => {
    if (!onDeleteAnalysis) return

    try {
      await onDeleteAnalysis(analysisId)
      // Refresh will be handled by parent component
    } catch (error) {
      console.error('Failed to delete analysis:', error)
      alert('Failed to delete analysis. Please try again.')
    }
  }

  // Pagination component
  const PaginationControls = () => {
    // Always show pagination controls if there are items, even if only 1 page
    if (totalItems === 0) return null

    const getPageNumbers = () => {
      const pages = []
      const maxVisible = 5

      if (totalPages <= maxVisible) {
        for (let i = 1; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        if (currentPage <= 3) {
          for (let i = 1; i <= 4; i++) pages.push(i)
          pages.push('...')
          pages.push(totalPages)
        } else if (currentPage >= totalPages - 2) {
          pages.push(1)
          pages.push('...')
          for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i)
        } else {
          pages.push(1)
          pages.push('...')
          for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i)
          pages.push('...')
          pages.push(totalPages)
        }
      }
      return pages
    }

    return (
      <div className="flex items-center justify-between mt-6 px-4">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <span>Show:</span>
          <select
            value={itemsPerPage}
            onChange={(e) => {
              setItemsPerPage(Number(e.target.value))
              setCurrentPage(1)
            }}
            className="border border-gray-300 rounded px-2 py-1 text-sm"
          >
            <option value={6}>6 per page</option>
            <option value={12}>12 per page</option>
            <option value={24}>24 per page</option>
            <option value={48}>48 per page</option>
          </select>
          <span className="ml-4">
            Showing {startIndex + 1}-{Math.min(endIndex, totalItems)} of {totalItems} results
          </span>
        </div>

        {totalPages > 1 && (
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            {getPageNumbers().map((page, index) => (
              <button
                key={index}
                onClick={() => typeof page === 'number' && setCurrentPage(page)}
                disabled={page === '...'}
                className={`px-3 py-1 text-sm border border-gray-300 rounded ${
                  page === currentPage
                    ? 'bg-blue-500 text-white border-blue-500'
                    : page === '...'
                    ? 'cursor-default'
                    : 'hover:bg-gray-50'
                }`}
              >
                {page}
              </button>
            ))}

            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </div>
    )
  }

  const handleAnalysisSelect = (analysisId: string) => {
    setSelectedAnalyses(prev => {
      let newSelection
      if (prev.includes(analysisId)) {
        newSelection = prev.filter(id => id !== analysisId)
      } else if (prev.length < 3) { // Limit to 3 comparisons
        newSelection = [...prev, analysisId]
      } else {
        newSelection = prev
      }
      console.log('Analysis selection updated:', newSelection)
      return newSelection
    })
  }

  const exportSingleAnalysisToPDF = (analysisId: string) => {
    const analysis = analyses.find(a => a.id === analysisId)
    if (!analysis) return

    // Import jsPDF dynamically
    import('jspdf').then(({ default: jsPDF }) => {
      const pdf = new jsPDF()
      const margin = 20
      let yPosition = margin
      const pageHeight = pdf.internal.pageSize.height
      const pageWidth = pdf.internal.pageSize.width

      // Helper function to add text with word wrapping and page breaks
      const addText = (text: string, fontSize = 12, isBold = false, color = [0, 0, 0]) => {
        pdf.setFontSize(fontSize)
        pdf.setFont('helvetica', isBold ? 'bold' : 'normal')
        pdf.setTextColor(color[0], color[1], color[2])

        const lines = pdf.splitTextToSize(text, pageWidth - 2 * margin)

        // Check if we need a new page
        if (yPosition + lines.length * (fontSize * 0.4) > pageHeight - 30) {
          pdf.addPage()
          yPosition = margin
        }

        pdf.text(lines, margin, yPosition)
        yPosition += lines.length * (fontSize * 0.4) + 5
      }

      const addSection = (title: string, content: string[] | string, color = [0, 0, 0]) => {
        yPosition += 5
        addText(title, 14, true, [0, 100, 200])
        yPosition += 2

        if (Array.isArray(content)) {
          content.forEach(item => {
            addText(`• ${item}`, 11, false, color)
          })
        } else {
          addText(content, 11, false, color)
        }
        yPosition += 5
      }

      // Header
      addText('AI STARTUP ANALYSIS REPORT', 20, true, [0, 50, 150])
      yPosition += 5
      addText(`Company: ${analysis.companyName}`, 16, true)
      addText(`Analysis Date: ${new Date(analysis.createdAt).toLocaleDateString()}`, 12)
      addText(`Sector: ${analysis.sectorBenchmarks?.sector || 'Unknown'}`, 12)
      yPosition += 10

      // Executive Summary Box
      pdf.setDrawColor(0, 100, 200)
      pdf.setFillColor(240, 248, 255)
      pdf.rect(margin, yPosition, pageWidth - 2 * margin, 40, 'FD')
      yPosition += 10

      addText(`INVESTMENT SCORE: ${analysis.score}/100`, 16, true, [0, 150, 0])
      addText(`RECOMMENDATION: ${analysis.recommendation.replace(/_/g, ' ')}`, 14, true, [200, 0, 0])
      addText(`Confidence Level: ${analysis.confidence || 'High'}%`, 12)
      yPosition += 15

      // Key Findings
      if (analysis.keyFindings && analysis.keyFindings.length > 0) {
        addSection('KEY FINDINGS', analysis.keyFindings, [0, 120, 0])
      }

      // Key Strengths
      if (analysis.structuredData?.key_strengths) {
        addSection('KEY STRENGTHS', analysis.structuredData.key_strengths, [0, 120, 0])
      }

      // Opportunities
      if (analysis.opportunities && analysis.opportunities.length > 0) {
        addSection('OPPORTUNITIES', analysis.opportunities, [0, 0, 200])
      }

      // Risk Factors
      if (analysis.riskFactors && analysis.riskFactors.length > 0) {
        addSection('RISK FACTORS', analysis.riskFactors, [200, 0, 0])
      }

      // Main Concerns
      if (analysis.structuredData?.main_concerns) {
        addSection('MAIN CONCERNS', analysis.structuredData.main_concerns, [200, 0, 0])
      }

      // Detailed Analysis
      if (analysis.analysis) {
        addSection('DETAILED ANALYSIS', analysis.analysis)
      }

      // Scoring Breakdown
      if (analysis.structuredData?.scoring_breakdown) {
        const scoring = analysis.structuredData.scoring_breakdown
        yPosition += 10
        addText('SCORING BREAKDOWN', 14, true, [0, 100, 200])
        yPosition += 5

        Object.entries(scoring).forEach(([key, value]) => {
          const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
          addText(`${label}: ${value}/100`, 11)
        })
      }

      // Footer
      pdf.setFontSize(8)
      pdf.setTextColor(100, 100, 100)
      pdf.text('Generated by AI Startup Analyst Platform', margin, pageHeight - 10)
      pdf.text(`Report generated on ${new Date().toLocaleDateString()}`, pageWidth - margin - 60, pageHeight - 10)

      // Save the PDF
      const fileName = `${analysis.companyName.replace(/\s+/g, '_')}_Analysis_Report.pdf`
      pdf.save(fileName)
    })
  }

  const exportMultipleAnalysesToPDF = (analysisIds: string[]) => {
    const selectedAnalyses = analyses.filter(a => analysisIds.includes(a.id))

    import('jspdf').then(({ default: jsPDF }) => {
      const pdf = new jsPDF()
      const margin = 20
      let yPosition = margin
      const pageHeight = pdf.internal.pageSize.height
      const pageWidth = pdf.internal.pageSize.width

      // Helper function to add text with proper encoding and page breaks
      const addText = (text: string, fontSize = 12, isBold = false, color = [0, 0, 0]) => {
        pdf.setFontSize(fontSize)
        pdf.setFont('helvetica', isBold ? 'bold' : 'normal')
        pdf.setTextColor(color[0], color[1], color[2])

        const lines = pdf.splitTextToSize(text, pageWidth - 2 * margin)

        if (yPosition + lines.length * (fontSize * 0.4) > pageHeight - 30) {
          pdf.addPage()
          yPosition = margin
        }

        pdf.text(lines, margin, yPosition)
        yPosition += lines.length * (fontSize * 0.4) + 5
      }

      // Header
      addText('STARTUP COMPARISON REPORT', 20, true, [0, 50, 150])
      yPosition += 5
      addText(`Generated: ${new Date().toLocaleDateString()}`, 12)
      addText(`Companies Compared: ${selectedAnalyses.length}`, 12)
      yPosition += 15

      // Executive Summary
      const avgScore = Math.round(selectedAnalyses.reduce((sum, a) => sum + a.score, 0) / selectedAnalyses.length)
      const topCompany = selectedAnalyses.reduce((prev, current) => (prev.score > current.score) ? prev : current)

      pdf.setDrawColor(0, 100, 200)
      pdf.setFillColor(240, 248, 255)
      pdf.rect(margin, yPosition, pageWidth - 2 * margin, 30, 'FD')
      yPosition += 10

      addText('EXECUTIVE SUMMARY', 14, true, [0, 100, 200])
      addText(`Average Score: ${avgScore}/100`, 12)
      addText(`Top Performer: ${topCompany.companyName} (${topCompany.score}/100)`, 12)
      yPosition += 15

      // Detailed Comparison
      selectedAnalyses.forEach((analysis, index) => {
        yPosition += 10

        // Company header with colored background
        const bgColor = analysis.score >= 80 ? [220, 255, 220] : analysis.score >= 60 ? [255, 255, 220] : [255, 220, 220]
        pdf.setFillColor(bgColor[0], bgColor[1], bgColor[2])
        pdf.rect(margin, yPosition - 5, pageWidth - 2 * margin, 25, 'F')

        addText(`${index + 1}. ${analysis.companyName}`, 16, true, [0, 0, 0])

        // Key metrics
        addText(`Investment Score: ${analysis.score}/100`, 12, true)
        addText(`Recommendation: ${analysis.recommendation.replace(/_/g, ' ')}`, 12)
        addText(`Sector: ${analysis.sectorBenchmarks?.sector || 'Unknown'}`, 11)
        addText(`Documents Analyzed: ${analysis.documentCount || 0}`, 11)
        addText(`Analysis Date: ${new Date(analysis.createdAt).toLocaleDateString()}`, 11)

        // Key findings (first 3)
        if (analysis.keyFindings && analysis.keyFindings.length > 0) {
          yPosition += 5
          addText('Key Findings:', 12, true, [0, 100, 0])
          analysis.keyFindings.slice(0, 3).forEach(finding => {
            addText(`• ${finding}`, 10)
          })
        }

        // Risk factors (first 2)
        if (analysis.riskFactors && analysis.riskFactors.length > 0) {
          yPosition += 5
          addText('Key Risks:', 12, true, [200, 0, 0])
          analysis.riskFactors.slice(0, 2).forEach(risk => {
            addText(`• ${risk}`, 10)
          })
        }

        yPosition += 10
      })

      // Comparison Summary
      yPosition += 10
      addText('INVESTMENT RECOMMENDATION SUMMARY', 14, true, [0, 100, 200])
      yPosition += 5

      const investRecommendations = selectedAnalyses.filter(a => a.recommendation === 'INVEST')
      const holdRecommendations = selectedAnalyses.filter(a => a.recommendation === 'HOLD')
      const avoidRecommendations = selectedAnalyses.filter(a => a.recommendation === 'DO_NOT_INVEST')

      addText(`INVEST: ${investRecommendations.length} companies`, 12, false, [0, 150, 0])
      addText(`HOLD: ${holdRecommendations.length} companies`, 12, false, [200, 150, 0])
      addText(`AVOID: ${avoidRecommendations.length} companies`, 12, false, [200, 0, 0])

      // Footer
      pdf.setFontSize(8)
      pdf.setTextColor(100, 100, 100)
      pdf.text('Generated by AI Startup Analyst Platform', margin, pageHeight - 10)
      pdf.text(`Comparison report generated on ${new Date().toLocaleDateString()}`, pageWidth - margin - 80, pageHeight - 10)

      pdf.save('Startup_Comparison_Report.pdf')
    })
  }

  const exportAllAnalysesToPDF = () => {
    import('jspdf').then(({ default: jsPDF }) => {
      const pdf = new jsPDF()
      const margin = 20
      let yPosition = margin
      const pageHeight = pdf.internal.pageSize.height
      const pageWidth = pdf.internal.pageSize.width

      const addText = (text: string, fontSize = 12, isBold = false, color = [0, 0, 0]) => {
        pdf.setFontSize(fontSize)
        pdf.setFont('helvetica', isBold ? 'bold' : 'normal')
        pdf.setTextColor(color[0], color[1], color[2])

        const lines = pdf.splitTextToSize(text, pageWidth - 2 * margin)

        if (yPosition + lines.length * (fontSize * 0.4) > pageHeight - 30) {
          pdf.addPage()
          yPosition = margin
        }

        pdf.text(lines, margin, yPosition)
        yPosition += lines.length * (fontSize * 0.4) + 5
      }

      // Header
      addText('COMPLETE PORTFOLIO ANALYSIS', 20, true, [0, 50, 150])
      yPosition += 5
      addText(`Generated: ${new Date().toLocaleDateString()}`, 12)
      addText(`Total Analyses: ${analyses.length}`, 12)
      yPosition += 15

      // Portfolio Summary
      pdf.setDrawColor(0, 100, 200)
      pdf.setFillColor(240, 248, 255)
      pdf.rect(margin, yPosition, pageWidth - 2 * margin, 40, 'FD')
      yPosition += 10

      addText('PORTFOLIO SUMMARY', 14, true, [0, 100, 200])
      addText(`Average Score: ${stats.avgScore}/100`, 12, true)
      addText(`Investment Ready: ${stats.investRecommendations} companies`, 12)
      addText(`Top Sector: ${stats.topSector}`, 12)
      yPosition += 20

      // Sector breakdown
      const sectorCounts = analyses.reduce((acc, analysis) => {
        const sector = analysis.sectorBenchmarks?.sector || 'Unknown'
        acc[sector] = (acc[sector] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      addText('SECTOR DISTRIBUTION', 14, true, [0, 100, 200])
      Object.entries(sectorCounts).forEach(([sector, count]) => {
        addText(`${sector}: ${count} companies`, 11)
      })
      yPosition += 10

      // Score distribution
      const scoreRanges = {
        'Excellent (80-100)': analyses.filter(a => a.score >= 80).length,
        'Good (60-79)': analyses.filter(a => a.score >= 60 && a.score < 80).length,
        'Fair (40-59)': analyses.filter(a => a.score >= 40 && a.score < 60).length,
        'Poor (0-39)': analyses.filter(a => a.score < 40).length
      }

      addText('SCORE DISTRIBUTION', 14, true, [0, 100, 200])
      Object.entries(scoreRanges).forEach(([range, count]) => {
        addText(`${range}: ${count} companies`, 11)
      })
      yPosition += 15

      // Top performers
      const topPerformers = analyses
        .sort((a, b) => b.score - a.score)
        .slice(0, 5)

      addText('TOP 5 PERFORMERS', 14, true, [0, 150, 0])
      topPerformers.forEach((analysis, index) => {
        addText(`${index + 1}. ${analysis.companyName} - ${analysis.score}/100`, 11, true)
        addText(`   ${analysis.recommendation} | ${analysis.sectorBenchmarks?.sector || 'Unknown'}`, 10)
      })
      yPosition += 15

      // All analyses summary
      addText('COMPLETE ANALYSIS LIST', 14, true, [0, 100, 200])
      analyses.forEach((analysis, index) => {
        if (yPosition > pageHeight - 40) {
          pdf.addPage()
          yPosition = margin
        }

        const scoreColor = analysis.score >= 80 ? [0, 150, 0] : analysis.score >= 60 ? [200, 150, 0] : [200, 0, 0]
        addText(`${index + 1}. ${analysis.companyName} - ${analysis.score}/100`, 11, true, scoreColor)
        addText(`   ${analysis.recommendation.replace(/_/g, ' ')} | ${analysis.sectorBenchmarks?.sector || 'Unknown'}`, 10)
        addText(`   Analyzed: ${new Date(analysis.createdAt).toLocaleDateString()}`, 9, false, [100, 100, 100])
        yPosition += 3
      })

      // Footer
      pdf.setFontSize(8)
      pdf.setTextColor(100, 100, 100)
      pdf.text('Generated by AI Startup Analyst Platform', margin, pageHeight - 10)
      pdf.text(`Portfolio report generated on ${new Date().toLocaleDateString()}`, pageWidth - margin - 80, pageHeight - 10)

      pdf.save('Complete_Portfolio_Analysis.pdf')
    })
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

  // Calculate dashboard stats - handle both old and new data structures
  const stats = {
    totalAnalyses: analyses.length,
    avgScore: analyses.length > 0 ? Math.round(analyses.reduce((sum, a) => sum + a.score, 0) / analyses.length) : 0,
    investRecommendations: analyses.filter(a =>
      a.recommendation === 'INVEST' ||
      (a as any).recommendation === 'INVEST'
    ).length,
    topSector: sectors.length > 0 ? sectors.reduce((a, b) => {
      const countA = analyses.filter(analysis =>
        analysis.sectorBenchmarks?.sector === a ||
        (analysis as any).sector_benchmarks?.detected_sector === a
      ).length
      const countB = analyses.filter(analysis =>
        analysis.sectorBenchmarks?.sector === b ||
        (analysis as any).sector_benchmarks?.detected_sector === b
      ).length
      return countA > countB ? a : b
    }) : 'N/A'
  }

  if (analyses.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="text-gray-400 text-6xl mb-4">📊</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Analyses Yet</h2>
        <p className="text-gray-600 mb-6">Upload and analyze some startup documents to see your dashboard.</p>

        <div className="bg-blue-50 rounded-lg p-4 text-left max-w-md mx-auto">
          <h3 className="font-semibold text-blue-800 mb-2">💡 Getting Started:</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Upload startup documents (pitch decks, financials, business plans)</li>
            <li>• Click "Analyze with AI" to get investment insights</li>
            <li>• Your analyses will automatically appear here</li>
            <li>• Use the dashboard to compare multiple startups</li>
          </ul>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-lg sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-0">📊 <span className="hidden sm:inline">Investment Analytics</span> Dashboard</h2>
          <div className="text-xs sm:text-sm text-gray-500">
            Last updated: {new Date().toLocaleDateString()}
          </div>
        </div>

        {/* Duplicate Warning & Toggle */}
        {duplicateGroups.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    {duplicateGroups.length} Duplicate Groups Found
                  </h3>
                  <div className="mt-1 text-sm text-yellow-700">
                    <p>
                      {hideDuplicates
                        ? `${duplicateIds.size} duplicates hidden (showing ${filteredAnalyses.length} unique companies)`
                        : `Showing all ${analyses.length} companies including duplicates`
                      }
                    </p>
                    <p className="mt-1 text-xs">
                      Companies: {duplicateGroups.map(group => group[0].companyName).join(', ')}
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={hideDuplicates}
                    onChange={(e) => setHideDuplicates(e.target.checked)}
                    className="sr-only"
                  />
                  <div className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    hideDuplicates ? 'bg-green-600' : 'bg-gray-200'
                  }`}>
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      hideDuplicates ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </div>
                  <span className="ml-2 text-sm text-yellow-800">Hide Duplicates</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-4 sm:mb-6">
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 sm:p-4 border border-blue-200">
            <div className="text-xl sm:text-2xl font-bold text-blue-600">{stats.totalAnalyses}</div>
            <div className="text-xs sm:text-sm text-blue-800">Total Analyses</div>
          </div>
          <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-3 sm:p-4 border border-green-200">
            <div className="text-xl sm:text-2xl font-bold text-green-600">{stats.avgScore}/100</div>
            <div className="text-xs sm:text-sm text-green-800">Average Score</div>
          </div>
          <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-3 sm:p-4 border border-purple-200">
            <div className="text-xl sm:text-2xl font-bold text-purple-600">{stats.investRecommendations}</div>
            <div className="text-xs sm:text-sm text-purple-800">Investment Ready</div>
          </div>
          <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-3 sm:p-4 border border-orange-200">
            <div className="text-xl sm:text-2xl font-bold text-orange-600 truncate">{stats.topSector}</div>
            <div className="text-xs sm:text-sm text-orange-800">Top Sector</div>
          </div>
        </div>

        {/* Instructions */}
        <div className="mb-4 bg-blue-50 rounded-lg p-3 sm:p-4">
          <p className="text-xs sm:text-sm text-blue-800">
            💡 <strong>How to compare:</strong> Click on startup cards to select them (up to 3), then click "Compare Selected" to see side-by-side analysis.
          </p>
        </div>

        {/* Filters and Controls */}
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-start sm:items-center justify-between">
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 w-full sm:w-auto">
            <select
              value={filterSector}
              onChange={(e) => setFilterSector(e.target.value)}
              className="px-2 sm:px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm sm:text-base w-full sm:w-auto"
            >
              <option value="all">All Sectors</option>
              {sectors.map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-2 sm:px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm sm:text-base w-full sm:w-auto"
            >
              <option value="all">All Status</option>
              <option value="INVEST">💰 Invest</option>
              <option value="HOLD">⏳ Hold</option>
              <option value="FURTHER_DUE_DILIGENCE_REQUIRED">🔍 Due Diligence</option>
              <option value="DO_NOT_INVEST">❌ Pass</option>
            </select>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-2 sm:px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm sm:text-base w-full sm:w-auto"
            >
              <option value="date">Sort by Date</option>
              <option value="score">Sort by Score</option>
              <option value="company">Sort by Company</option>
            </select>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4 w-full sm:w-auto">
            {selectedAnalyses.length > 0 && (
              <span className="text-xs sm:text-sm text-gray-600">
                {selectedAnalyses.length} selected
              </span>
            )}

            <div className="flex flex-wrap items-center gap-2">
              {selectedAnalyses.length === 1 && (
                <button
                  onClick={() => exportSingleAnalysisToPDF(selectedAnalyses[0])}
                  className="px-2 sm:px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium text-xs sm:text-sm"
                >
                  <Download className="h-4 w-4 mr-1" />
                  <span className="hidden sm:inline">Export </span>PDF
                </button>
              )}

              {selectedAnalyses.length > 1 && (
                <>
                  <button
                    onClick={() => {
                      console.log('Compare button clicked with:', selectedAnalyses)
                      onCompareSelected && onCompareSelected(selectedAnalyses)
                    }}
                    className="px-2 sm:px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-xs sm:text-sm"
                  >
                    <BarChart3 className="h-4 w-4 mr-1" />
                    Compare ({selectedAnalyses.length})
                  </button>

                  <button
                    onClick={() => exportMultipleAnalysesToPDF(selectedAnalyses)}
                    className="px-2 sm:px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium text-xs sm:text-sm"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    <span className="hidden sm:inline">Export </span>All
                  </button>
                </>
              )}

              {selectedAnalyses.length === 0 && (
                <button
                  onClick={() => exportAllAnalysesToPDF()}
                  className="px-2 sm:px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium text-xs sm:text-sm"
                >
                  <Download className="h-4 w-4 mr-1" />
                  <span className="hidden sm:inline">Export All </span>Data
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Investment Charts & Insights */}
      <InvestmentCharts analyses={analyses} />

      {/* Analyses Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {paginatedAnalyses.map((analysis) => (
          <div
            key={analysis.id}
            data-company-name={analysis.companyName || analysis.company_name || 'Unknown'}
            className={`bg-white rounded-xl shadow-lg p-4 sm:p-6 cursor-pointer transition-all hover:shadow-xl relative ${
              selectedAnalyses.includes(analysis.id) ? 'ring-2 ring-blue-500 bg-blue-50' : ''
            }`}
            onClick={() => handleAnalysisSelect(analysis.id)}
          >
            {/* Selection Indicator */}
            {selectedAnalyses.includes(analysis.id) && (
              <div className="absolute top-2 right-2 bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                ✓
              </div>
            )}

            {/* Company Header */}
            <div className="flex items-center justify-between mb-3 sm:mb-4">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 truncate pr-2">
                {analysis.companyName}
              </h3>
              <div className={`text-xl sm:text-2xl font-bold ${getScoreColor(analysis.score)}`}>
                {analysis.score}
              </div>
            </div>

            {/* Recommendation Badge */}
            <div className={`inline-block px-2 sm:px-3 py-1 rounded-full text-xs font-medium border mb-3 ${
              getRecommendationColor(analysis.recommendation)
            }`}>
              <span className="hidden sm:inline">{analysis.recommendation.replace(/_/g, ' ')}</span>
              <span className="sm:hidden">{analysis.recommendation.split('_')[0]}</span>
            </div>

            {/* Key Info */}
            <div className="space-y-1 sm:space-y-2 text-xs sm:text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Sector:</span>
                <span className="font-medium text-right truncate ml-2">
                  {analysis.sectorBenchmarks?.sector ||
                   (analysis as any).sector_benchmarks?.detected_sector ||
                   'Unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Documents:</span>
                <span className="font-medium">
                  {analysis.documentCount || (analysis as any).document_count || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Analyzed:</span>
                <span className="font-medium text-right">
                  <span className="hidden sm:inline">{new Date(analysis.createdAt || Date.now()).toLocaleDateString()}</span>
                  <span className="sm:hidden">{new Date(analysis.createdAt || Date.now()).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                </span>
              </div>
            </div>

            {/* Analysis Preview */}
            <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-gray-200">
              <p className="text-xs sm:text-sm text-gray-700 line-clamp-2 sm:line-clamp-3">
                {(() => {
                  // Try to get executive summary from structured data first
                  if (analysis.structuredData?.executive_summary) {
                    return analysis.structuredData.executive_summary.substring(0, 120) + '...'
                  }

                  // Try to parse JSON analysis if it exists
                  try {
                    const analysisText = analysis.analysis || analysis.analysis_text || ''
                    const cleanText = analysisText.replace(/```json\s*|\s*```/g, '')
                    if (cleanText.trim().startsWith('{')) {
                      const parsed = JSON.parse(cleanText)
                      if (parsed.executive_summary) {
                        return parsed.executive_summary.substring(0, 120) + '...'
                      }
                    }
                  } catch (e) {
                    // If parsing fails, continue to fallback
                  }

                  // Fallback to basic analysis text or default message
                  const analysisText = analysis.analysis || analysis.analysis_text || ''
                  if (analysisText && !analysisText.includes('```json')) {
                    return analysisText.substring(0, 120) + '...'
                  }

                  return `Investment analysis for ${analysis.companyName} with ${analysis.score}/100 score and ${analysis.recommendation.replace(/_/g, ' ').toLowerCase()} recommendation.`
                })()}
              </p>
              <div className="flex justify-between items-center mt-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    console.log('🔍 Opening detailed analysis for:', analysis.companyName, analysis)
                    setSelectedAnalysisForDetail(analysis)
                  }}
                  className="text-xs sm:text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  <Eye className="h-4 w-4 mr-1" />
                  View Full Analysis
                </button>

                {/* Delete Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteAnalysis(analysis.id)
                  }}
                  className="text-xs sm:text-sm text-red-600 hover:text-red-800 font-medium px-2 py-1 rounded hover:bg-red-50 transition-colors"
                  title="Delete Analysis"
                >
                  Delete
                </button>
              </div>
            </div>

            {/* Selection Indicator */}
            {selectedAnalyses.includes(analysis.id) && (
              <div className="mt-3 sm:mt-4 flex items-center text-blue-600">
                <svg className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-xs sm:text-sm font-medium">Selected for comparison</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      <PaginationControls />

      {filteredAnalyses.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg">No analyses found</div>
          <div className="text-gray-500 text-sm mt-2">
            {(filterSector !== 'all' || filterStatus !== 'all' || hideDuplicates) ?
              'Try changing the filters above or toggle duplicate visibility' :
              'Upload and analyze some startups to get started'}
          </div>
        </div>
      )}

      {/* Detailed Analysis Modal */}
      {selectedAnalysisForDetail && (
        <DetailedAnalysisView
          analysis={selectedAnalysisForDetail}
          onClose={() => setSelectedAnalysisForDetail(null)}
        />
      )}
    </div>
  )
}

export default AnalyticsDashboard
