// Enhanced data models for the AI Analyst Platform

export interface StartupProfile {
  id: string
  companyName: string
  sector: string
  stage: string
  foundedYear?: number
  location?: string
  website?: string
  description?: string
  createdAt: Date
  updatedAt: Date
}

export interface AnalysisResult {
  id: string
  startupId: string
  documentId: string
  companyName: string
  score: number
  recommendation: 'INVEST' | 'HOLD' | 'DO_NOT_INVEST' | 'FURTHER_DUE_DILIGENCE_REQUIRED'
  
  // Core Analysis
  analysis: string
  keyFindings: string[]
  riskFactors: string[]
  opportunities: string[]
  
  // Structured Data
  structuredData: {
    financials?: {
      revenue?: number
      growth?: number
      burn?: number
      runway?: number
    }
    team?: {
      foundersCount?: number
      teamSize?: number
      keyHires?: string[]
    }
    market?: {
      size?: number
      growth?: number
      competition?: string[]
    }
    product?: {
      stage?: string
      traction?: string
      customers?: number
    }
  }
  
  // Benchmarking
  sectorBenchmarks: {
    sector: string
    avgValuation?: number
    avgGrowth?: number
    avgBurn?: number
    peerComparisons?: Array<{
      company: string
      metric: string
      value: number
      comparison: 'above' | 'below' | 'similar'
    }>
  }
  
  // Documents
  processedFiles: string[]
  fileTypes: string[]
  documentCount: number
  
  // Metadata
  createdAt: Date
  analysisVersion: string
  confidence: number
}

export interface ComparisonResult {
  id: string
  companyIds: string[]
  companyNames: string[]
  createdAt: Date
  
  // Comparison Metrics
  scoreComparison: Array<{
    companyName: string
    score: number
    recommendation: string
  }>
  
  // Side-by-side Analysis
  financialComparison: Array<{
    metric: string
    companies: Array<{
      name: string
      value: number | string
      rank: number
    }>
  }>
  
  // Investment Recommendation
  topChoice: {
    companyName: string
    reasons: string[]
  }
  
  summary: string
}

export interface SectorBenchmark {
  sector: string
  metrics: {
    avgValuation: number
    avgGrowth: number
    avgBurn: number
    avgTeamSize: number
    avgFundingRounds: number
  }
  updatedAt: Date
}

export interface RiskIndicator {
  type: 'financial' | 'market' | 'team' | 'product' | 'legal'
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  impact: string
  mitigation?: string
}

export interface InvestorPreferences {
  sectors: string[]
  stages: string[]
  minScore: number
  riskTolerance: 'low' | 'medium' | 'high'
  focusAreas: string[]
  customWeights: {
    team: number
    market: number
    product: number
    financials: number
    traction: number
  }
}
