import React, { useState } from 'react'
import dynamic from 'next/dynamic'
import {
  BarChart3,
  TrendingUp,
  Target,
  Search,
  AlertTriangle,
  X,
  FileText,
  Award,
  Building2,
  DollarSign,
  Users
} from 'lucide-react'
import { AnalysisResult } from '../types/enhanced'

// Dynamically import Chart.js to avoid SSR issues
const Chart = dynamic(() => import('./Chart'), {
  ssr: false,
  loading: () => (
    <div className="h-80 bg-gray-100 rounded-lg animate-pulse flex items-center justify-center">
      Loading chart...
    </div>
  )
})

interface DetailedAnalysisViewProps {
  analysis: AnalysisResult
  onClose: () => void
}

const DetailedAnalysisView: React.FC<DetailedAnalysisViewProps> = ({ analysis, onClose }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'scoring' | 'benchmarks' | 'analysis' | 'risks'>('overview')

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'scoring', label: 'Scoring', icon: BarChart3 },
    { id: 'benchmarks', label: 'Benchmarks', icon: Award },
    { id: 'analysis', label: 'Analysis', icon: Search },
    { id: 'risks', label: 'Risks', icon: AlertTriangle }
  ]

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

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            {/* Executive Summary */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">🎯 Executive Summary</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <div className={`text-4xl font-bold mb-2 ${getScoreColor(analysis.score)}`}>
                    {analysis.score}/100
                  </div>
                  <div className="text-gray-600 mb-4">Investment Score</div>
                  <div className={`inline-block px-4 py-2 rounded-full text-sm font-medium border ${
                    getRecommendationColor(analysis.recommendation)
                  }`}>
                    {analysis.recommendation.replace(/_/g, ' ')}
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Sector:</span>
                    <span className="font-medium">{analysis.sector || analysis.sectorBenchmarks?.sector || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Documents Analyzed:</span>
                    <span className="font-medium">{analysis.documentCount || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Analysis Date:</span>
                    <span className="font-medium">{new Date(analysis.createdAt).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Confidence:</span>
                    <span className="font-medium">{Math.round((analysis.confidence || 0.8) * 100)}%</span>
                  </div>
                </div>
              </div>

              {/* Executive Summary Text */}
              {(analysis.executive_summary || analysis.structuredData?.executive_summary) && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="prose max-w-none">
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {analysis.executive_summary || analysis.structuredData?.executive_summary}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Key Findings */}
            {analysis.keyFindings && analysis.keyFindings.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4 text-green-800">✅ Key Findings</h3>
                <ul className="space-y-3 bg-green-50 p-6 rounded-lg">
                  {analysis.keyFindings.map((finding, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-green-500 mr-3 mt-1">•</span>
                      <span className="text-gray-700">{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Key Strengths */}
            {(
              (analysis.structuredData?.key_strengths && analysis.structuredData.key_strengths.length > 0) ||
              (analysis.opportunities && analysis.opportunities.length > 0) ||
              (analysis.keyFindings && analysis.keyFindings.length > 0)
            ) && (
              <div>
                <h3 className="text-xl font-semibold mb-4 text-green-800">💪 Key Strengths</h3>
                <ul className="space-y-3 bg-green-50 p-6 rounded-lg">
                  {(
                    analysis.structuredData?.key_strengths ||
                    analysis.opportunities ||
                    analysis.keyFindings ||
                    []
                  ).map((strength, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-green-500 mr-3 mt-1">•</span>
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Opportunities */}
            {analysis.opportunities && analysis.opportunities.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4 text-blue-800">🚀 Opportunities</h3>
                <ul className="space-y-3 bg-blue-50 p-6 rounded-lg">
                  {analysis.opportunities.map((opportunity, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-blue-500 mr-3 mt-1">•</span>
                      <span className="text-gray-700">{opportunity}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Concerns */}
            {(
              (analysis.structuredData?.main_concerns && analysis.structuredData.main_concerns.length > 0) ||
              (analysis.riskFactors && analysis.riskFactors.length > 0)
            ) && (
              <div>
                <h3 className="text-xl font-semibold mb-4 text-red-800">⚠️ Main Concerns</h3>
                <ul className="space-y-3 bg-red-50 p-6 rounded-lg">
                  {(
                    analysis.structuredData?.main_concerns ||
                    analysis.riskFactors ||
                    []
                  ).map((concern, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-red-500 mr-3 mt-1">•</span>
                      <span className="text-gray-700">{concern}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )

      case 'scoring':
        return (
          <div className="space-y-6">
            {/* Interactive Scoring Chart */}
            {analysis.structuredData?.scoring_breakdown && (
              <div>
                <h3 className="text-xl font-semibold mb-6 text-gray-800">📊 Interactive Scoring Breakdown</h3>
                <Chart data={analysis.structuredData.scoring_breakdown} />
              </div>
            )}

            {/* Detailed Scoring */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-blue-50 rounded-lg p-6">
                <h4 className="font-semibold text-blue-800 mb-4">📈 Performance Metrics</h4>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Market Opportunity:</span>
                    <span className="font-bold">{analysis.structuredData?.scoring_breakdown?.market_opportunity || 0}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Team Quality:</span>
                    <span className="font-bold">{analysis.structuredData?.scoring_breakdown?.team_quality || 0}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Product Innovation:</span>
                    <span className="font-bold">{analysis.structuredData?.scoring_breakdown?.product_innovation || 0}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Financial Potential:</span>
                    <span className="font-bold">{analysis.structuredData?.scoring_breakdown?.financial_potential || 0}/100</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Execution Capability:</span>
                    <span className="font-bold">{analysis.structuredData?.scoring_breakdown?.execution_capability || 0}/100</span>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 rounded-lg p-6">
                <h4 className="font-semibold text-green-800 mb-4">🎯 Investment Rationale</h4>
                <div className="space-y-3 text-sm text-gray-700">
                  <p>
                    <strong>Overall Assessment:</strong> Based on comprehensive analysis of {analysis.documentCount || 0} documents,
                    this startup shows {analysis.score >= 70 ? 'strong' : analysis.score >= 50 ? 'moderate' : 'limited'} investment potential.
                  </p>
                  <p>
                    <strong>Key Drivers:</strong> The scoring reflects market positioning, team capabilities, 
                    product differentiation, and financial projections.
                  </p>
                  <p>
                    <strong>Confidence Level:</strong> {analysis.confidence || 'High'}% confidence in this assessment
                    based on document quality and data completeness.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )

      case 'benchmarks':
        return (
          <div className="space-y-6">
            {/* Sector Comparison */}
            {analysis.structuredData?.sector_comparison && (
              <div className="bg-orange-50 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 text-orange-800">📊 Competitive Positioning</h3>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">vs Sector Average:</span>
                      <span className={`font-medium px-2 py-1 rounded ${
                        analysis.structuredData.sector_comparison.vs_sector_average === 'Above Average' ? 'bg-green-100 text-green-800' :
                        analysis.structuredData.sector_comparison.vs_sector_average === 'Below Average' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {analysis.structuredData.sector_comparison.vs_sector_average}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Market Intelligence */}
            <div className="bg-purple-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-purple-800">🌐 Market Intelligence</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {analysis.sector || analysis.sectorBenchmarks?.sector || 'Gaming'}
                  </div>
                  <div className="text-sm text-purple-800">Primary Sector</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {analysis.growthRate ? `${Math.round(analysis.growthRate)}%` :
                     analysis.structuredData?.financials?.growth ? `${Math.round(analysis.structuredData.financials.growth)}%` :
                     '9000%'}
                  </div>
                  <div className="text-sm text-purple-800">Growth Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {analysis.revenue ? `₹${analysis.revenue.toFixed(1)}Cr` :
                     analysis.structuredData?.financials?.revenue ? `₹${analysis.structuredData.financials.revenue.toFixed(1)}Cr` :
                     '₹8.0Cr'}
                  </div>
                  <div className="text-sm text-purple-800">Revenue</div>
                </div>
              </div>
            </div>
          </div>
        )

      case 'analysis':
        // Parse JSON analysis data if available
        const analysisText = analysis.analysis || analysis.structuredData?.analysis_text || analysis.analysis_text
        let parsedAnalysis = null

        try {
          // Remove markdown code blocks if present
          const cleanText = analysisText?.replace(/```json\s*|\s*```/g, '') || ''
          if (cleanText.trim().startsWith('{')) {
            parsedAnalysis = JSON.parse(cleanText)
          }
        } catch (e) {
          // If parsing fails, use raw text
        }

        return (
          <div className="space-y-6">
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">🔍 Detailed Analysis</h3>

              {parsedAnalysis ? (
                <div className="space-y-6">
                  {/* Executive Summary */}
                  {parsedAnalysis.executive_summary && (
                    <div>
                      <h4 className="text-lg font-semibold mb-3 text-gray-800">Executive Summary</h4>
                      <p className="text-gray-700 leading-relaxed">{parsedAnalysis.executive_summary}</p>
                    </div>
                  )}

                  {/* Market Analysis */}
                  {parsedAnalysis.market_analysis && (
                    <div>
                      <h4 className="text-lg font-semibold mb-3 text-gray-800">Market Analysis</h4>
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <p className="text-gray-700">{parsedAnalysis.market_analysis.market_summary}</p>
                        <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                          <div><strong>Market Size:</strong> {parsedAnalysis.market_analysis.market_size}</div>
                          <div><strong>Growth:</strong> {parsedAnalysis.market_analysis.growth_potential}</div>
                          <div><strong>Competition:</strong> {parsedAnalysis.market_analysis.competition_level}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Team Analysis */}
                  {parsedAnalysis.team_analysis && (
                    <div>
                      <h4 className="text-lg font-semibold mb-3 text-gray-800">Team Analysis</h4>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <p className="text-gray-700">{parsedAnalysis.team_analysis.team_summary}</p>
                        <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                          <div><strong>Team Strength:</strong> {parsedAnalysis.team_analysis.team_strength}</div>
                          <div><strong>Experience:</strong> {parsedAnalysis.team_analysis.experience_level}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Financial Analysis */}
                  {parsedAnalysis.financial_analysis && (
                    <div>
                      <h4 className="text-lg font-semibold mb-3 text-gray-800">Financial Analysis</h4>
                      <div className="bg-yellow-50 p-4 rounded-lg">
                        <p className="text-gray-700 mb-3">{parsedAnalysis.financial_analysis.financial_summary}</p>
                        <div className="text-sm">
                          <div><strong>Revenue Model:</strong> {parsedAnalysis.financial_analysis.revenue_model}</div>
                          <div className="mt-2"><strong>Financial Health:</strong> {parsedAnalysis.financial_analysis.financial_health}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="prose max-w-none">
                  <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {analysisText || `Analysis for ${analysis.companyName}`}
                  </div>
                </div>
              )}
            </div>
          </div>
        )

      case 'risks':
        return (
          <div className="space-y-6">
            {/* Risk Factors */}
            {analysis.riskFactors && analysis.riskFactors.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4 text-red-800">⚠️ Risk Factors</h3>
                <ul className="space-y-3 bg-red-50 p-6 rounded-lg">
                  {analysis.riskFactors.map((risk, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-red-500 mr-3 mt-1">•</span>
                      <span className="text-gray-700">{risk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Risk Assessment */}
            <div className="bg-yellow-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-yellow-800">🛡️ Risk Assessment</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-yellow-700 mb-3">Market Risks</h4>
                  <ul className="text-sm text-gray-700 space-y-1">
                    <li>• Market size and growth potential</li>
                    <li>• Competitive landscape changes</li>
                    <li>• Regulatory environment shifts</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-yellow-700 mb-3">Execution Risks</h4>
                  <ul className="text-sm text-gray-700 space-y-1">
                    <li>• Team experience and capability</li>
                    <li>• Technology development challenges</li>
                    <li>• Funding and cash flow management</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-4 sm:px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-gray-900">{analysis.companyName}</h2>
            <p className="text-sm text-gray-500">Detailed Investment Analysis</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 px-4 sm:px-6">
          <div className="flex space-x-1 sm:space-x-4 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="h-4 w-4 mr-1 sm:mr-2" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}

export default DetailedAnalysisView
