import { create } from 'zustand';

export interface AnalysisResult {
  call_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  classification: 'safe' | 'spam' | 'fraud' | 'phishing' | 'robocall' | 'unknown';
  risk_score: number;
  spam_score: number;
  fraud_score: number;
  phishing_score: number;
  robocall_score: number;
  transcript: string;
  transcript_language: string;
  transcript_confidence: number;
  suspicious_keywords: string[];
  fraud_indicators: FraudIndicator[];
  highlighted_phrases: HighlightedPhrase[];
  voice_characteristics: VoiceCharacteristics;
  acoustic_features: AcousticFeatures;
  behavioral_patterns: BehavioralPatterns;
  intent_analysis: IntentAnalysis;
  ai_explanation: string;
  confidence_score: number;
  duration_seconds: number;
  analyzed_at: string | null;
}

export interface FraudIndicator {
  type: string;
  category: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
}

export interface HighlightedPhrase {
  text: string;
  start: number;
  end: number;
  category: string;
  severity: string;
}

export interface VoiceCharacteristics {
  tone?: string;
  speed?: string;
  stress?: string;
  urgency?: number;
  naturalness?: number;
}

export interface AcousticFeatures {
  duration?: number;
  pitch_mean?: number;
  pitch_std?: number;
  energy_mean?: number;
  speaking_rate?: number;
  stress_level?: number;
  synthetic_probability?: number;
}

export interface BehavioralPatterns {
  intent?: IntentAnalysis;
  pressure_score?: number;
  commands?: Command[];
}

export interface IntentAnalysis {
  primary_intent?: string;
  category?: string;
  all_intents?: string[];
  confidence?: number;
}

export interface Command {
  type: string;
  match: string;
  risk_level: string;
}

interface AnalysisState {
  currentResult: AnalysisResult | null;
  isAnalyzing: boolean;
  progress: number;
  error: string | null;
  recentResults: AnalysisResult[];
  setResult: (result: AnalysisResult) => void;
  setAnalyzing: (analyzing: boolean) => void;
  setProgress: (progress: number) => void;
  setError: (error: string | null) => void;
  addToRecent: (result: AnalysisResult) => void;
  clearResult: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  currentResult: null,
  isAnalyzing: false,
  progress: 0,
  error: null,
  recentResults: [],
  setResult: (result) => set({ currentResult: result, isAnalyzing: false, progress: 100 }),
  setAnalyzing: (analyzing) => set({ isAnalyzing: analyzing, error: null }),
  setProgress: (progress) => set({ progress }),
  setError: (error) => set({ error, isAnalyzing: false }),
  addToRecent: (result) => set((state) => ({
    recentResults: [result, ...state.recentResults.slice(0, 9)]
  })),
  clearResult: () => set({ currentResult: null, progress: 0, error: null }),
}));
