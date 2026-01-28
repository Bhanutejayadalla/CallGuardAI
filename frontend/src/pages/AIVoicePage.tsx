import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  Mic,
  MicOff,
  Brain,
  Shield,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Loader2,
  Volume2,
  Languages,
  FileAudio,
  Info,
  BarChart2,
  AudioWaveform,
} from 'lucide-react';
import clsx from 'clsx';

interface AIVoiceResult {
  classification: string;
  is_ai_generated: boolean | null;
  confidence_score: number;
  confidence_percentage: number;
  language: string;
  language_name: string;
  explanation: string;
  analysis_details: {
    features_analyzed: string[];
    ai_indicators: string[];
    human_indicators: string[];
    spectral_analysis: Record<string, number>;
    temporal_analysis: Record<string, number>;
    prosody_analysis: Record<string, number>;
  };
  supported_languages: string[];
  status: string;
  request_id?: string;
  processed_at?: string;
}

const SUPPORTED_LANGUAGES = [
  { code: 'ta', name: 'Tamil', flag: '🇮🇳' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { code: 'ml', name: 'Malayalam', flag: '🇮🇳' },
  { code: 'te', name: 'Telugu', flag: '🇮🇳' },
];

export default function AIVoicePage() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AIVoiceResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [dragActive, setDragActive] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const handleFileSelect = (selectedFile: File) => {
    if (selectedFile.type.includes('audio') || selectedFile.name.endsWith('.mp3') || selectedFile.name.endsWith('.wav')) {
      setFile(selectedFile);
      setAudioBlob(null);
      setResult(null);
      setError(null);
    } else {
      setError('Please select a valid audio file (MP3 or WAV)');
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, []);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setFile(null);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const fileToBase64 = (file: File | Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = (reader.result as string).split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
    });
  };

  const analyzeAudio = async () => {
    const audioSource = file || audioBlob;
    if (!audioSource) {
      setError('Please upload or record an audio file first');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const base64Audio = await fileToBase64(audioSource);
      
      const response = await fetch('/api/v1/ai-voice/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audio: base64Audio,
          language: selectedLanguage || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getClassificationStyles = (classification: string) => {
    switch (classification) {
      case 'ai_generated':
        return {
          bg: 'bg-red-100 dark:bg-red-900/30',
          text: 'text-red-700 dark:text-red-400',
          border: 'border-red-200 dark:border-red-800',
          icon: AlertTriangle,
          label: 'AI Generated',
        };
      case 'human':
        return {
          bg: 'bg-green-100 dark:bg-green-900/30',
          text: 'text-green-700 dark:text-green-400',
          border: 'border-green-200 dark:border-green-800',
          icon: CheckCircle,
          label: 'Human Voice',
        };
      default:
        return {
          bg: 'bg-yellow-100 dark:bg-yellow-900/30',
          text: 'text-yellow-700 dark:text-yellow-400',
          border: 'border-yellow-200 dark:border-yellow-800',
          icon: HelpCircle,
          label: 'Uncertain',
        };
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl mb-4 shadow-lg"
        >
          <Brain className="w-8 h-8 text-white" />
        </motion.div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
          AI Voice Detection
        </h1>
        <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
          Detect whether a voice sample is AI-generated or human. 
          Supports <strong>Tamil, English, Hindi, Malayalam,</strong> and <strong>Telugu</strong>.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Panel */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          {/* Upload Area */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDrag}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            className={clsx(
              'border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer',
              dragActive
                ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                : 'border-slate-300 dark:border-slate-600 hover:border-purple-400 dark:hover:border-purple-500',
              'bg-white dark:bg-slate-800'
            )}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*,.mp3,.wav,.m4a,.webm"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
            />
            
            <div className="flex flex-col items-center space-y-4">
              <div className="p-4 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                <Upload className="w-8 h-8 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-lg font-medium text-slate-900 dark:text-white">
                  Drop audio file here or click to browse
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Supports MP3, WAV, M4A, WebM
                </p>
              </div>
            </div>
          </div>

          {/* Recording Controls */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center">
              <Mic className="w-5 h-5 mr-2 text-purple-500" />
              Record Audio
            </h3>
            
            <div className="flex items-center justify-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={isRecording ? stopRecording : startRecording}
                className={clsx(
                  'flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-colors',
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-purple-500 hover:bg-purple-600 text-white'
                )}
              >
                {isRecording ? (
                  <>
                    <MicOff className="w-5 h-5" />
                    <span>Stop Recording</span>
                  </>
                ) : (
                  <>
                    <Mic className="w-5 h-5" />
                    <span>Start Recording</span>
                  </>
                )}
              </motion.button>
            </div>
            
            {isRecording && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4 flex items-center justify-center space-x-2 text-red-500"
              >
                <span className="animate-pulse w-3 h-3 bg-red-500 rounded-full"></span>
                <span>Recording...</span>
              </motion.div>
            )}
          </div>

          {/* Selected File/Recording Display */}
          {(file || audioBlob) && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-lg flex items-center space-x-4"
            >
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
                <FileAudio className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-slate-900 dark:text-white">
                  {file ? file.name : 'Recorded Audio'}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Ready for analysis'}
                </p>
              </div>
              <Volume2 className="w-5 h-5 text-slate-400" />
            </motion.div>
          )}

          {/* Language Selection */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center">
              <Languages className="w-5 h-5 mr-2 text-purple-500" />
              Language (Optional)
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <button
                onClick={() => setSelectedLanguage('')}
                className={clsx(
                  'px-4 py-3 rounded-xl text-sm font-medium transition-colors',
                  selectedLanguage === ''
                    ? 'bg-purple-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                )}
              >
                Auto-Detect
              </button>
              {SUPPORTED_LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => setSelectedLanguage(lang.code)}
                  className={clsx(
                    'px-4 py-3 rounded-xl text-sm font-medium transition-colors flex items-center justify-center space-x-2',
                    selectedLanguage === lang.code
                      ? 'bg-purple-500 text-white'
                      : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                  )}
                >
                  <span>{lang.flag}</span>
                  <span>{lang.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Analyze Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={analyzeAudio}
            disabled={isAnalyzing || (!file && !audioBlob)}
            className={clsx(
              'w-full py-4 rounded-2xl font-semibold text-lg flex items-center justify-center space-x-3 transition-colors',
              isAnalyzing || (!file && !audioBlob)
                ? 'bg-slate-300 dark:bg-slate-700 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white hover:from-purple-600 hover:to-indigo-700 shadow-lg'
            )}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                <span>Analyzing Voice...</span>
              </>
            ) : (
              <>
                <Brain className="w-6 h-6" />
                <span>Detect AI Voice</span>
              </>
            )}
          </motion.button>

          {/* Error Display */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-start space-x-3"
              >
                <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-red-700 dark:text-red-400">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Results Panel */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          {!result && !isAnalyzing && (
            <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-lg text-center h-full flex flex-col items-center justify-center">
              <div className="p-4 bg-slate-100 dark:bg-slate-700 rounded-full mb-4">
                <Shield className="w-12 h-12 text-slate-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Ready to Analyze
              </h3>
              <p className="text-slate-500 dark:text-slate-400 max-w-sm">
                Upload an audio file or record your voice to detect if it's AI-generated or human.
              </p>
              
              <div className="mt-8 grid grid-cols-1 gap-4 w-full max-w-sm">
                <div className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-sm text-slate-600 dark:text-slate-300">Multi-language support</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-sm text-slate-600 dark:text-slate-300">Deep acoustic analysis</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-sm text-slate-600 dark:text-slate-300">Detailed explanations</span>
                </div>
              </div>
            </div>
          )}

          {isAnalyzing && (
            <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-lg text-center h-full flex flex-col items-center justify-center">
              <div className="relative">
                <Loader2 className="w-16 h-16 text-purple-500 animate-spin" />
                <Brain className="w-8 h-8 text-purple-600 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mt-4 mb-2">
                Analyzing Voice Sample
              </h3>
              <p className="text-slate-500 dark:text-slate-400">
                Extracting acoustic features and detecting AI patterns...
              </p>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Classification Result */}
              {(() => {
                const styles = getClassificationStyles(result.classification);
                const Icon = styles.icon;
                return (
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className={clsx(
                      'rounded-2xl p-6 border-2',
                      styles.bg,
                      styles.border
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className={clsx('p-3 rounded-xl', styles.bg)}>
                          <Icon className={clsx('w-8 h-8', styles.text)} />
                        </div>
                        <div>
                          <p className="text-sm text-slate-500 dark:text-slate-400">Classification</p>
                          <p className={clsx('text-2xl font-bold', styles.text)}>
                            {styles.label}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-slate-500 dark:text-slate-400">Confidence</p>
                        <p className={clsx('text-3xl font-bold', styles.text)}>
                          {result.confidence_percentage.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </motion.div>
                );
              })()}

              {/* Language Detected */}
              <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg">
                <div className="flex items-center space-x-3 mb-4">
                  <Languages className="w-5 h-5 text-purple-500" />
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Language Detected
                  </h3>
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {result.language_name}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Code: {result.language}
                </p>
              </div>

              {/* Explanation */}
              <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg">
                <div className="flex items-center space-x-3 mb-4">
                  <Info className="w-5 h-5 text-purple-500" />
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Analysis Explanation
                  </h3>
                </div>
                <p className="text-slate-600 dark:text-slate-300 whitespace-pre-line">
                  {result.explanation}
                </p>
              </div>

              {/* AI Indicators */}
              {result.analysis_details.ai_indicators.length > 0 && (
                <div className="bg-red-50 dark:bg-red-900/20 rounded-2xl p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <h3 className="text-lg font-semibold text-red-700 dark:text-red-400">
                      AI Indicators Found
                    </h3>
                  </div>
                  <ul className="space-y-2">
                    {result.analysis_details.ai_indicators.map((indicator, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-red-500 mt-1">•</span>
                        <span className="text-red-700 dark:text-red-300">{indicator}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Human Indicators */}
              {result.analysis_details.human_indicators.length > 0 && (
                <div className="bg-green-50 dark:bg-green-900/20 rounded-2xl p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <h3 className="text-lg font-semibold text-green-700 dark:text-green-400">
                      Human Voice Indicators
                    </h3>
                  </div>
                  <ul className="space-y-2">
                    {result.analysis_details.human_indicators.map((indicator, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-green-500 mt-1">•</span>
                        <span className="text-green-700 dark:text-green-300">{indicator}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Technical Analysis */}
              <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg">
                <div className="flex items-center space-x-3 mb-4">
                  <BarChart2 className="w-5 h-5 text-purple-500" />
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Technical Analysis
                  </h3>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {/* Spectral */}
                  <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Spectral Analysis</p>
                    <p className="text-lg font-semibold text-slate-900 dark:text-white">
                      {Object.keys(result.analysis_details.spectral_analysis || {}).length} features
                    </p>
                  </div>
                  
                  {/* Temporal */}
                  <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Temporal Analysis</p>
                    <p className="text-lg font-semibold text-slate-900 dark:text-white">
                      {Object.keys(result.analysis_details.temporal_analysis || {}).length} features
                    </p>
                  </div>
                  
                  {/* Prosody */}
                  <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Prosody Analysis</p>
                    <p className="text-lg font-semibold text-slate-900 dark:text-white">
                      {Object.keys(result.analysis_details.prosody_analysis || {}).length} features
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Info Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-12 bg-gradient-to-br from-purple-100 to-indigo-100 dark:from-purple-900/30 dark:to-indigo-900/30 rounded-2xl p-8"
      >
        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
          How AI Voice Detection Works
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-purple-500 rounded-lg">
              <AudioWaveform className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-900 dark:text-white">Spectral Analysis</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Analyzes frequency patterns that differ between AI and human voices.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-indigo-500 rounded-lg">
              <BarChart2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-900 dark:text-white">Prosody Detection</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Evaluates pitch, rhythm, and stress patterns for naturalness.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-violet-500 rounded-lg">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-900 dark:text-white">Pattern Recognition</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Identifies subtle artifacts common in AI-generated audio.
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
