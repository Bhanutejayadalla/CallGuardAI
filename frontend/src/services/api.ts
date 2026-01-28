import axios from 'axios';
import { AnalysisResult } from '../stores/analysisStore';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Analysis API
export const analyzeAudio = async (file: File, callerNumber?: string): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);
  if (callerNumber) {
    formData.append('caller_number', callerNumber);
  }

  const response = await api.post('/analyze/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const analyzeText = async (text: string, callerNumber?: string): Promise<AnalysisResult> => {
  const response = await api.post('/analyze/text', null, {
    params: { text, caller_number: callerNumber },
  });
  return response.data;
};

export const getAnalysisStatus = async (callId: string) => {
  const response = await api.get(`/analyze/status/${callId}`);
  return response.data;
};

// Calls API
export interface CallsQueryParams {
  page?: number;
  skip?: number;
  limit?: number;
  classification?: string;
  min_risk_score?: number;
  max_risk_score?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
}

export interface CallRecord {
  call_id: string;
  classification: string;
  risk_score: number;
  transcript?: string;
  duration?: number;
  created_at: string;
  fraud_indicators?: { indicator: string; severity: string; description: string }[];
  detected_keywords?: string[];
  voice_characteristics?: {
    tone: string;
    speaking_rate: string;
    stress_level: string;
    naturalness: number;
  };
  acoustic_features?: {
    pitch_mean: number;
    tempo: number;
    zero_crossing_rate: number;
    spectral_centroid: number;
  };
  linguistic_score?: number;
  acoustic_score?: number;
  behavioral_score?: number;
  confidence: number;
  explanation?: string;
}

export interface CallsResponse {
  calls: CallRecord[];
  total: number;
  page: number;
  limit: number;
}

export const getCalls = async (params: CallsQueryParams = {}): Promise<CallsResponse> => {
  // Convert page to skip for backend
  const { page, ...rest } = params;
  const skip = page ? (page - 1) * (params.limit || 10) : 0;
  const response = await api.get('/calls', { params: { ...rest, skip } });
  return {
    calls: response.data.calls || response.data,
    total: response.data.total || response.data?.length || 0,
    page: page || 1,
    limit: params.limit || 10,
  };
};

export const getCallsCount = async (classification?: string) => {
  const response = await api.get('/calls/count', { params: { classification } });
  return response.data;
};

export const getCallDetail = async (callId: string): Promise<AnalysisResult> => {
  const response = await api.get(`/calls/${callId}`);
  return response.data;
};

// Alias for getCallDetail used in CallDetailPage
export const getCall = getCallDetail;

export const deleteCall = async (callId: string) => {
  const response = await api.delete(`/calls/${callId}`);
  return response.data;
};

export const getRecentAlerts = async (limit: number = 10) => {
  const response = await api.get('/calls/recent/alerts', { params: { limit } });
  return response.data;
};

// Analytics API
export interface DashboardData {
  stats: {
    total_calls: number;
    analyzed_calls: number;
    safe_calls: number;
    spam_calls: number;
    fraud_calls: number;
    phishing_calls: number;
    robocall_calls: number;
    average_risk_score: number;
    detection_rate: number;
  };
  recent_calls: any[];
  risk_distribution: Record<string, number>;
  top_fraud_indicators: { indicator: string; count: number }[];
  classification_breakdown: Record<string, number>;
}

export const getDashboard = async (days: number = 30): Promise<DashboardData> => {
  const response = await api.get('/analytics/dashboard', { params: { days } });
  return response.data;
};

export const getTrends = async (days: number = 30) => {
  const response = await api.get('/analytics/trends', { params: { days } });
  return response.data;
};

export const getHeatmap = async (days: number = 7) => {
  const response = await api.get('/analytics/heatmap', { params: { days } });
  return response.data;
};

export const getTopKeywords = async (days: number = 30, limit: number = 20) => {
  const response = await api.get('/analytics/keywords', { params: { days, limit } });
  return response.data;
};

// Admin API
export interface Rule {
  id: number;
  name: string;
  description?: string;
  pattern: string;
  rule_type?: string;
  category: string;
  severity: string;
  keywords?: string[];
  patterns?: string[];
  weight?: number;
  score_impact: number;
  language?: string;
  is_active: boolean;
  priority?: number;
  created_at?: string;
}

export interface DetectionRule extends Rule {}

export const getRules = async (category?: string, isActive?: boolean): Promise<Rule[]> => {
  const response = await api.get('/admin/rules', { params: { category, is_active: isActive } });
  return response.data;
};

export const createRule = async (rule: Partial<Rule>): Promise<Rule> => {
  const response = await api.post('/admin/rules', rule);
  return response.data;
};

export const updateRule = async (ruleId: number, updates: Partial<DetectionRule>) => {
  const response = await api.put(`/admin/rules/${ruleId}`, updates);
  return response.data;
};

export const deleteRule = async (ruleId: number) => {
  const response = await api.delete(`/admin/rules/${ruleId}`);
  return response.data;
};

export const initializeDefaultRules = async () => {
  const response = await api.post('/admin/rules/init-defaults');
  return response.data;
};

export const getSystemStats = async () => {
  const response = await api.get('/admin/stats');
  return response.data;
};

// AI Voice Detection API
export interface AIVoiceDetectionRequest {
  audio: string; // Base64-encoded MP3
  language?: string; // Optional: ta, en, hi, ml, te
}

export interface AIVoiceAnalysisDetails {
  features_analyzed: string[];
  ai_indicators: string[];
  human_indicators: string[];
  spectral_analysis: Record<string, number>;
  temporal_analysis: Record<string, number>;
  prosody_analysis: Record<string, number>;
}

export interface AIVoiceDetectionResponse {
  classification: 'ai_generated' | 'human' | 'uncertain';
  is_ai_generated: boolean | null;
  confidence_score: number;
  confidence_percentage: number;
  language: string;
  language_name: string;
  explanation: string;
  analysis_details: AIVoiceAnalysisDetails;
  supported_languages: string[];
  status: string;
  request_id?: string;
  processed_at?: string;
}

export interface SupportedLanguagesResponse {
  languages: Record<string, string>;
  count: number;
}

export const detectAIVoice = async (request: AIVoiceDetectionRequest): Promise<AIVoiceDetectionResponse> => {
  const response = await api.post('/ai-voice/detect', request);
  return response.data;
};

export const getAIVoiceSupportedLanguages = async (): Promise<SupportedLanguagesResponse> => {
  const response = await api.get('/ai-voice/languages');
  return response.data;
};

export const getAIVoiceHealth = async () => {
  const response = await api.get('/ai-voice/health');
  return response.data;
};

export default api;
