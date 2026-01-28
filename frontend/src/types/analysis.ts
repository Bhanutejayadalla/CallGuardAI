export interface AcousticFeatures {
  tempo?: number;
  zero_crossing_rate?: number;
  spectral_centroid?: number;
  [key: string]: any;
}

export interface VoiceCharacteristics {
  pitch?: number;
  energy?: number;
  clarity?: number;
  [key: string]: any;
}

export interface AnalysisResult {
  detected_keywords?: string[];
  linguistic_score?: number;
  acoustic_score?: number;
  behavioral_score?: number;
  confidence?: number;
  explanation?: string;
  ai_explanation?: string;
  features?: AcousticFeatures;
  characteristics?: VoiceCharacteristics;
  [key: string]: any;
}
