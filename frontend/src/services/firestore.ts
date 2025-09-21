import { 
  collection, 
  doc, 
  addDoc, 
  getDoc, 
  getDocs, 
  updateDoc, 
  deleteDoc, 
  query, 
  where, 
  orderBy, 
  limit,
  Timestamp 
} from 'firebase/firestore'
import { db } from '@/lib/firebase'
import { AnalysisResult, StartupProfile, ComparisonResult } from '@/types/enhanced'

// Collections
const STARTUPS_COLLECTION = 'startups'
const ANALYSES_COLLECTION = 'analyses'
const COMPARISONS_COLLECTION = 'comparisons'

export class FirestoreService {

  // Check if Firebase is available
  private static isFirebaseAvailable(): boolean {
    if (!db) {
      console.warn('⚠️ Firebase not available - running in offline mode')
      return false
    }
    return true
  }

  // Startup Profile Management
  static async saveStartupProfile(profile: Omit<StartupProfile, 'id' | 'createdAt' | 'updatedAt'>) {
    if (!this.isFirebaseAvailable()) {
      console.log('📱 Offline mode: Startup profile would be saved:', profile.companyName)
      return { id: 'offline-' + Date.now() }
    }

    try {
      const docRef = await addDoc(collection(db, STARTUPS_COLLECTION), {
        ...profile,
        createdAt: Timestamp.now(),
        updatedAt: Timestamp.now()
      })
      console.log('✅ Startup profile saved:', docRef.id)
      return docRef.id
    } catch (error) {
      console.error('❌ Error saving startup profile:', error)
      throw error
    }
  }

  static async getStartupProfile(id: string): Promise<StartupProfile | null> {
    try {
      const docRef = doc(db, STARTUPS_COLLECTION, id)
      const docSnap = await getDoc(docRef)
      
      if (docSnap.exists()) {
        return {
          id: docSnap.id,
          ...docSnap.data(),
          createdAt: docSnap.data().createdAt.toDate(),
          updatedAt: docSnap.data().updatedAt.toDate()
        } as StartupProfile
      }
      return null
    } catch (error) {
      console.error('❌ Error getting startup profile:', error)
      throw error
    }
  }

  static async getAllStartups(): Promise<StartupProfile[]> {
    if (!this.isFirebaseAvailable()) {
      console.log('📱 Offline mode: Returning empty startups list')
      return []
    }

    try {
      const q = query(
        collection(db, STARTUPS_COLLECTION),
        orderBy('updatedAt', 'desc')
      )
      const querySnapshot = await getDocs(q)

      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt.toDate(),
        updatedAt: doc.data().updatedAt.toDate()
      })) as StartupProfile[]
    } catch (error) {
      console.error('❌ Error getting all startups:', error)
      throw error
    }
  }

  // Analysis Management
  static async saveAnalysis(analysis: Omit<AnalysisResult, 'id' | 'createdAt'>) {
    if (!this.isFirebaseAvailable()) {
      console.log('📱 Offline mode: Analysis would be saved:', analysis.companyName)
      return { id: 'offline-' + Date.now() }
    }

    try {
      const docRef = await addDoc(collection(db, ANALYSES_COLLECTION), {
        ...analysis,
        createdAt: Timestamp.now()
      })
      console.log('✅ Analysis saved to Firestore:', docRef.id)

      // Also save to backend BigQuery if available
      try {
        const backendData = {
          analysis_id: docRef.id,
          company_name: analysis.companyName,
          sector: analysis.sectorBenchmarks?.sector || 'Unknown',
          score: analysis.score,
          recommendation: analysis.recommendation,
          analysis_text: analysis.analysis || '',
          revenue: (analysis.structuredData as any)?.financials?.revenue || (analysis.structuredData as any)?.revenue || 0,
          growth_rate: (analysis.structuredData as any)?.financials?.growth || (analysis.structuredData as any)?.growthRate || 0,
          funding: (analysis.structuredData as any)?.financials?.funding || (analysis.structuredData as any)?.funding || 0,
          document_count: 1,
          file_types: JSON.stringify(['pdf']),
          analysis_timestamp: new Date().toISOString(),
          confidence_score: analysis.confidence || 0.8,
          // Add missing analysis content fields - these are top-level fields from backend
          key_strengths: (analysis as any)?.key_strengths || [],
          main_concerns: (analysis as any)?.main_concerns || [],
          executive_summary: (analysis as any)?.executive_summary || '',
          // Add scoring breakdown fields - these are from top-level scoring_breakdown
          market_opportunity_score: (analysis as any)?.scoring_breakdown?.market_opportunity || 0,
          team_quality_score: (analysis as any)?.scoring_breakdown?.team_quality || 0,
          product_innovation_score: (analysis as any)?.scoring_breakdown?.product_innovation || 0,
          financial_potential_score: (analysis as any)?.scoring_breakdown?.financial_potential || 0,
          execution_capability_score: (analysis as any)?.scoring_breakdown?.execution_capability || 0
        }

        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://startup-ai-analyst-backend-281259205924.us-central1.run.app'}/api/analyses`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(backendData)
        })

        if (response.ok) {
          console.log('✅ Analysis also saved to backend BigQuery')
        } else {
          console.log('⚠️ Backend save failed but Firestore succeeded')
        }
      } catch (backendError) {
        console.log('⚠️ Backend save failed (this is okay, Firestore is primary)', backendError)
      }

      return docRef.id
    } catch (error) {
      console.error('❌ Error saving analysis:', error)
      throw error
    }
  }

  static async getAnalysis(id: string): Promise<AnalysisResult | null> {
    try {
      const docRef = doc(db, ANALYSES_COLLECTION, id)
      const docSnap = await getDoc(docRef)
      
      if (docSnap.exists()) {
        return {
          id: docSnap.id,
          ...docSnap.data(),
          createdAt: docSnap.data().createdAt.toDate()
        } as AnalysisResult
      }
      return null
    } catch (error) {
      console.error('❌ Error getting analysis:', error)
      throw error
    }
  }

  static async getAnalysesByStartup(startupId: string): Promise<AnalysisResult[]> {
    try {
      const q = query(
        collection(db, ANALYSES_COLLECTION),
        where('startupId', '==', startupId),
        orderBy('createdAt', 'desc')
      )
      const querySnapshot = await getDocs(q)
      
      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt.toDate()
      })) as AnalysisResult[]
    } catch (error) {
      console.error('❌ Error getting analyses by startup:', error)
      throw error
    }
  }

  static async getAllAnalyses(limitCount: number = 50): Promise<AnalysisResult[]> {
    if (!this.isFirebaseAvailable()) {
      console.log('📱 Offline mode: Returning empty analyses list')
      return []
    }

    try {
      const q = query(
        collection(db, ANALYSES_COLLECTION),
        orderBy('createdAt', 'desc'),
        limit(limitCount)
      )
      const querySnapshot = await getDocs(q)
      
      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt.toDate()
      })) as AnalysisResult[]
    } catch (error) {
      console.error('❌ Error getting all analyses:', error)
      throw error
    }
  }

  // Comparison Management
  static async saveComparison(comparison: Omit<ComparisonResult, 'id' | 'createdAt'>) {
    try {
      const docRef = await addDoc(collection(db, COMPARISONS_COLLECTION), {
        ...comparison,
        createdAt: Timestamp.now()
      })
      console.log('✅ Comparison saved:', docRef.id)
      return docRef.id
    } catch (error) {
      console.error('❌ Error saving comparison:', error)
      throw error
    }
  }

  static async getComparison(id: string): Promise<ComparisonResult | null> {
    try {
      const docRef = doc(db, COMPARISONS_COLLECTION, id)
      const docSnap = await getDoc(docRef)
      
      if (docSnap.exists()) {
        return {
          id: docSnap.id,
          ...docSnap.data(),
          createdAt: docSnap.data().createdAt.toDate()
        } as ComparisonResult
      }
      return null
    } catch (error) {
      console.error('❌ Error getting comparison:', error)
      throw error
    }
  }

  static async getAllComparisons(): Promise<ComparisonResult[]> {
    try {
      const q = query(
        collection(db, COMPARISONS_COLLECTION),
        orderBy('createdAt', 'desc')
      )
      const querySnapshot = await getDocs(q)
      
      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt.toDate()
      })) as ComparisonResult[]
    } catch (error) {
      console.error('❌ Error getting all comparisons:', error)
      throw error
    }
  }

  // Search and Filter
  static async searchStartupsByName(searchTerm: string): Promise<StartupProfile[]> {
    try {
      // Note: Firestore doesn't support full-text search natively
      // For production, consider using Algolia or Elasticsearch
      const q = query(
        collection(db, STARTUPS_COLLECTION),
        where('companyName', '>=', searchTerm),
        where('companyName', '<=', searchTerm + '\uf8ff'),
        limit(10)
      )
      const querySnapshot = await getDocs(q)
      
      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt.toDate(),
        updatedAt: doc.data().updatedAt.toDate()
      })) as StartupProfile[]
    } catch (error) {
      console.error('❌ Error searching startups:', error)
      throw error
    }
  }

  static async getAnalysesBySector(sector: string): Promise<AnalysisResult[]> {
    try {
      const q = query(
        collection(db, ANALYSES_COLLECTION),
        where('sectorBenchmarks.sector', '==', sector),
        orderBy('createdAt', 'desc'),
        limit(20)
      )
      const querySnapshot = await getDocs(q)
      
      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data(),
        createdAt: doc.data().createdAt.toDate()
      })) as AnalysisResult[]
    } catch (error) {
      console.error('❌ Error getting analyses by sector:', error)
      throw error
    }
  }

  // Delete analysis
  static async deleteAnalysis(analysisId: string): Promise<void> {
    if (!this.isFirebaseAvailable()) {
      throw new Error('Firebase not available')
    }

    try {
      console.log('🗑️ Deleting analysis from Firestore:', analysisId)

      const analysisRef = doc(db, ANALYSES_COLLECTION, analysisId)
      await deleteDoc(analysisRef)

      console.log('✅ Analysis deleted successfully')
    } catch (error) {
      console.error('❌ Error deleting analysis:', error)
      throw error
    }
  }
}
