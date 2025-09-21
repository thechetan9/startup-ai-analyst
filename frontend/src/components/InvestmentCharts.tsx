import React from 'react'
import { AnalysisResult } from '../types/enhanced'

interface InvestmentChartsProps {
  analyses: AnalysisResult[]
}

const InvestmentCharts: React.FC<InvestmentChartsProps> = ({ analyses }) => {
  // Only show charts if we have enough data
  if (analyses.length < 3) {
    return null
  }

  // Calculate sector distribution
  const sectorDistribution = analyses.reduce((acc, analysis) => {
    const sector = analysis.sectorBenchmarks?.sector || 'Unknown'
    acc[sector] = (acc[sector] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  // Calculate investment opportunities
  const investmentOpportunities = analyses.filter(a => a.recommendation === 'INVEST').length
  const monitorOpportunities = analyses.filter(a => a.recommendation === 'HOLD' || a.recommendation === 'FURTHER_DUE_DILIGENCE_REQUIRED').length
  const passOpportunities = analyses.filter(a => a.recommendation === 'DO_NOT_INVEST').length

  // Top performing sectors
  const sectorPerformance = Object.entries(
    analyses.reduce((acc, analysis) => {
      const sector = analysis.sectorBenchmarks?.sector || 'Unknown'
      if (!acc[sector]) {
        acc[sector] = { total: 0, count: 0, scores: [] }
      }
      acc[sector].total += analysis.score
      acc[sector].count += 1
      acc[sector].scores.push(analysis.score)
      return acc
    }, {} as Record<string, { total: number; count: number; scores: number[] }>)
  ).map(([sector, data]) => ({
    sector,
    avgScore: Math.round(data.total / data.count),
    count: data.count,
    maxScore: Math.max(...data.scores),
    minScore: Math.min(...data.scores)
  })).sort((a, b) => b.avgScore - a.avgScore)

  // Market opportunities by score ranges
  const scoreRanges = {
    'High Potential (80-100)': analyses.filter(a => a.score >= 80).length,
    'Good Potential (60-79)': analyses.filter(a => a.score >= 60 && a.score < 80).length,
    'Moderate Potential (40-59)': analyses.filter(a => a.score >= 40 && a.score < 60).length,
    'Low Potential (0-39)': analyses.filter(a => a.score < 40).length
  }

  // Simple bar chart component
  const BarChart = ({ data, title, color = 'blue' }: { data: Record<string, number>, title: string, color?: string }) => {
    const maxValue = Math.max(...Object.values(data))
    const colorClasses = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      yellow: 'bg-yellow-500',
      red: 'bg-red-500',
      purple: 'bg-purple-500'
    }

    return (
      <div className="bg-white rounded-lg p-4 shadow-lg">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>
        <div className="space-y-3">
          {Object.entries(data).map(([label, value]) => (
            <div key={label} className="flex items-center">
              <div className="w-24 text-sm text-gray-600 truncate" title={label}>
                {label}
              </div>
              <div className="flex-1 mx-3">
                <div className="bg-gray-200 rounded-full h-4 relative">
                  <div
                    className={`${colorClasses[color]} h-4 rounded-full transition-all duration-500`}
                    style={{ width: `${(value / maxValue) * 100}%` }}
                  />
                </div>
              </div>
              <div className="w-8 text-sm font-medium text-gray-800">
                {value}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Investment recommendation pie chart (simplified)
  const RecommendationChart = () => {
    const total = analyses.length
    const investPercent = (investmentOpportunities / total) * 100
    const monitorPercent = (monitorOpportunities / total) * 100
    const passPercent = (passOpportunities / total) * 100

    return (
      <div className="bg-white rounded-lg p-4 shadow-lg">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">Investment Recommendations</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
              <span className="text-sm">Invest</span>
            </div>
            <div className="text-sm font-medium">
              {investmentOpportunities} ({investPercent.toFixed(1)}%)
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
              <span className="text-sm">Monitor/DD</span>
            </div>
            <div className="text-sm font-medium">
              {monitorOpportunities} ({monitorPercent.toFixed(1)}%)
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
              <span className="text-sm">Pass</span>
            </div>
            <div className="text-sm font-medium">
              {passOpportunities} ({passPercent.toFixed(1)}%)
            </div>
          </div>
          
          {/* Visual bar */}
          <div className="mt-4">
            <div className="flex h-6 rounded-full overflow-hidden">
              <div 
                className="bg-green-500" 
                style={{ width: `${investPercent}%` }}
                title={`Invest: ${investPercent.toFixed(1)}%`}
              />
              <div 
                className="bg-yellow-500" 
                style={{ width: `${monitorPercent}%` }}
                title={`Monitor: ${monitorPercent.toFixed(1)}%`}
              />
              <div 
                className="bg-red-500" 
                style={{ width: `${passPercent}%` }}
                title={`Pass: ${passPercent.toFixed(1)}%`}
              />
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">📈 Investment Insights & Analytics</h2>
        <div className="text-sm text-gray-500">
          Based on {analyses.length} analyses
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BarChart 
          data={sectorDistribution} 
          title="📊 Sector Distribution" 
          color="blue" 
        />
        
        <RecommendationChart />
        
        <BarChart 
          data={scoreRanges} 
          title="🎯 Market Opportunities by Score" 
          color="purple" 
        />

        {/* Top Performing Sectors */}
        <div className="bg-white rounded-lg p-4 shadow-lg">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">🏆 Top Performing Sectors</h3>
          <div className="space-y-3">
            {sectorPerformance.slice(0, 5).map((sector, index) => (
              <div key={sector.sector} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white mr-3 ${
                    index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-orange-500' : 'bg-blue-500'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{sector.sector}</div>
                    <div className="text-sm text-gray-500">{sector.count} companies</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-lg text-gray-900">{sector.avgScore}</div>
                  <div className="text-xs text-gray-500">avg score</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Investment Insights */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 className="text-lg font-semibold mb-4 text-gray-800 flex items-center">
          💡 Key Investment Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl font-bold text-green-600">{investmentOpportunities}</div>
            <div className="text-sm text-gray-600">Strong Investment Opportunities</div>
            <div className="text-xs text-gray-500 mt-1">
              {((investmentOpportunities / analyses.length) * 100).toFixed(1)}% of analyzed companies
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600">{sectorPerformance[0]?.sector || 'N/A'}</div>
            <div className="text-sm text-gray-600">Top Performing Sector</div>
            <div className="text-xs text-gray-500 mt-1">
              Avg score: {sectorPerformance[0]?.avgScore || 0}/100
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl font-bold text-purple-600">
              {Math.round(analyses.reduce((sum, a) => sum + a.score, 0) / analyses.length)}
            </div>
            <div className="text-sm text-gray-600">Portfolio Average Score</div>
            <div className="text-xs text-gray-500 mt-1">
              Across all {analyses.length} companies
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl font-bold text-orange-600">
              {Object.keys(sectorDistribution).length}
            </div>
            <div className="text-sm text-gray-600">Sectors Covered</div>
            <div className="text-xs text-gray-500 mt-1">
              Diversified portfolio
            </div>
          </div>
        </div>
      </div>

      {/* Business Model & Market Opportunities */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6 border border-green-200">
        <h3 className="text-lg font-semibold mb-4 text-gray-800 flex items-center">
          🚀 Market Opportunities & Business Models
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 mb-3">📈 Growth Potential</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">High Growth (80+ score):</span>
                <span className="font-medium">{scoreRanges['High Potential (80-100)']} companies</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Scalable Models:</span>
                <span className="font-medium">{analyses.filter(a => a.sectorBenchmarks?.sector?.includes('SaaS') || a.sectorBenchmarks?.sector?.includes('AI')).length} companies</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Market Leaders:</span>
                <span className="font-medium">{analyses.filter(a => a.score >= 85).length} companies</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 mb-3">💰 Investment Focus Areas</h4>
            <div className="space-y-2">
              {sectorPerformance.slice(0, 3).map((sector, index) => (
                <div key={sector.sector} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{sector.sector}:</span>
                  <div className="flex items-center">
                    <span className="font-medium mr-2">{sector.count} companies</span>
                    <div className={`w-2 h-2 rounded-full ${
                      sector.avgScore >= 80 ? 'bg-green-500' :
                      sector.avgScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InvestmentCharts
