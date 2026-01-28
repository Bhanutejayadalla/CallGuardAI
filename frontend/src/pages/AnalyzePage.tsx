import { useState, useCallback, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useDropzone } from 'react-dropzone';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  Upload,
  Mic,
  FileText,
  Loader2,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Volume2,
  Square,
  Play,
  Pause,
} from 'lucide-react';
import clsx from 'clsx';

import { analyzeAudio, analyzeText } from '../services/api';
import { useAnalysisStore, AnalysisResult } from '../stores/analysisStore';
import RiskMeter from '../components/RiskMeter';
import TranscriptViewer from '../components/TranscriptViewer';
import FraudIndicators from '../components/FraudIndicators';
import VoiceAnalysis from '../components/VoiceAnalysis';

type AnalysisMode = 'upload' | 'record' | 'text';

export default function AnalyzePage() {
  const { t } = useTranslation();
  const [mode, setMode] = useState<AnalysisMode>('upload');
  const [textInput, setTextInput] = useState('');
  const { currentResult, isAnalyzing, setResult, setAnalyzing, setError } = useAnalysisStore();

  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);

  // File upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => analyzeAudio(file),
    onMutate: () => {
      setAnalyzing(true);
    },
    onSuccess: (data: AnalysisResult) => {
      setResult(data);
      toast.success('Analysis complete!');
    },
    onError: (error: Error) => {
      setError(error.message);
      toast.error('Analysis failed: ' + error.message);
    },
  });

  // Text analysis mutation
  const textMutation = useMutation({
    mutationFn: (text: string) => analyzeText(text),
    onMutate: () => {
      setAnalyzing(true);
    },
    onSuccess: (data: AnalysisResult) => {
      setResult(data);
      toast.success('Analysis complete!');
    },
    onError: (error: Error) => {
      setError(error.message);
      toast.error('Analysis failed: ' + error.message);
    },
  });

  // Dropzone configuration
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      uploadMutation.mutate(acceptedFiles[0]);
    }
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.ogg', '.flac', '.m4a'],
      'video/*': ['.mp4', '.webm', '.mkv', '.avi', '.mov'],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  // Recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(1000); // Collect data every second
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev: number) => prev + 1);
      }, 1000);

      toast.success('Recording started');
    } catch (err) {
      toast.error('Could not access microphone. Please check permissions.');
      console.error('Microphone error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      toast.success('Recording stopped');
    }
  };

  const analyzeRecording = () => {
    if (audioBlob) {
      const file = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
      uploadMutation.mutate(file);
    }
  };

  const discardRecording = () => {
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setRecordingTime(0);
  };

  const togglePlayback = () => {
    if (!audioElementRef.current && audioUrl) {
      audioElementRef.current = new Audio(audioUrl);
      audioElementRef.current.onended = () => setIsPlaying(false);
    }
    
    if (audioElementRef.current) {
      if (isPlaying) {
        audioElementRef.current.pause();
      } else {
        audioElementRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      if (audioElementRef.current) {
        audioElementRef.current.pause();
        audioElementRef.current = null;
      }
    };
  }, [audioUrl]);

  const handleTextAnalysis = () => {
    if (textInput.trim().length < 10) {
      toast.error('Please enter at least 10 characters');
      return;
    }
    textMutation.mutate(textInput);
  };

  const tabs = [
    { id: 'upload' as AnalysisMode, label: t('analyze.upload'), icon: Upload },
    { id: 'record' as AnalysisMode, label: t('analyze.recording'), icon: Mic },
    { id: 'text' as AnalysisMode, label: t('analyze.text'), icon: FileText },
  ];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
          {t('analyze.title')}
        </h1>
        <p className="text-slate-600 dark:text-slate-400">
          Upload, record, or enter call transcript for fraud analysis
        </p>
      </div>

      {/* Mode Tabs */}
      <div className="flex justify-center">
        <div className="inline-flex bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setMode(tab.id)}
              className={clsx(
                'flex items-center space-x-2 px-6 py-2 rounded-lg text-sm font-medium transition-colors',
                mode === tab.id
                  ? 'bg-white dark:bg-slate-700 text-primary-600 dark:text-primary-400 shadow'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              )}
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Section */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left: Input */}
        <div className="card p-6">
          <AnimatePresence mode="wait">
            {mode === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <div
                  {...getRootProps()}
                  className={clsx(
                    'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors',
                    isDragActive
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-300 dark:border-slate-600 hover:border-primary-400'
                  )}
                >
                  <input {...getInputProps()} />
                  <Upload className={clsx(
                    'h-12 w-12 mx-auto mb-4',
                    isDragActive ? 'text-primary-500' : 'text-slate-400'
                  )} />
                  <p className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-2">
                    {isDragActive ? 'Drop the file here' : 'Drag & drop audio or video file'}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    or click to browse • WAV, MP3, MP4, WEBM, MKV • Max 50MB
                  </p>
                </div>
              </motion.div>
            )}

            {mode === 'record' && (
              <motion.div
                key="record"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-center py-8"
              >
                {!audioBlob ? (
                  // Recording controls
                  <div className="space-y-6">
                    <div className="relative inline-flex">
                      <div className={clsx(
                        'w-24 h-24 rounded-full flex items-center justify-center transition-colors',
                        isRecording 
                          ? 'bg-danger-100 dark:bg-danger-900/30' 
                          : 'bg-slate-100 dark:bg-slate-700'
                      )}>
                        <Mic className={clsx(
                          'h-10 w-10',
                          isRecording ? 'text-danger-500' : 'text-slate-400'
                        )} />
                      </div>
                      {isRecording && (
                        <div className="absolute inset-0 bg-danger-500 rounded-full opacity-25 animate-ping"></div>
                      )}
                    </div>

                    {isRecording && (
                      <div className="text-2xl font-mono font-bold text-danger-500">
                        {formatTime(recordingTime)}
                      </div>
                    )}

                    <p className="text-lg font-medium text-slate-700 dark:text-slate-300">
                      {isRecording ? 'Recording...' : 'Click to start recording'}
                    </p>

                    <div className="flex justify-center gap-4">
                      {!isRecording ? (
                        <button
                          onClick={startRecording}
                          className="btn-primary flex items-center space-x-2 px-8"
                        >
                          <Mic className="h-5 w-5" />
                          <span>Start Recording</span>
                        </button>
                      ) : (
                        <button
                          onClick={stopRecording}
                          className="bg-danger-500 hover:bg-danger-600 text-white px-8 py-2 rounded-lg flex items-center space-x-2"
                        >
                          <Square className="h-5 w-5" />
                          <span>Stop Recording</span>
                        </button>
                      )}
                    </div>
                  </div>
                ) : (
                  // Recorded audio preview and actions
                  <div className="space-y-6">
                    <div className="w-24 h-24 mx-auto bg-success-100 dark:bg-success-900/30 rounded-full flex items-center justify-center">
                      <CheckCircle className="h-10 w-10 text-success-500" />
                    </div>
                    
                    <p className="text-lg font-medium text-slate-700 dark:text-slate-300">
                      Recording Complete ({formatTime(recordingTime)})
                    </p>

                    <div className="flex justify-center gap-4">
                      <button
                        onClick={togglePlayback}
                        className="btn-secondary flex items-center space-x-2"
                      >
                        {isPlaying ? (
                          <><Pause className="h-5 w-5" /><span>Pause</span></>
                        ) : (
                          <><Play className="h-5 w-5" /><span>Play</span></>
                        )}
                      </button>
                      <button
                        onClick={discardRecording}
                        className="btn-secondary flex items-center space-x-2 text-danger-600"
                      >
                        <XCircle className="h-5 w-5" />
                        <span>Discard</span>
                      </button>
                      <button
                        onClick={analyzeRecording}
                        disabled={isAnalyzing}
                        className="btn-primary flex items-center space-x-2"
                      >
                        {isAnalyzing ? (
                          <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                          <AlertTriangle className="h-5 w-5" />
                        )}
                        <span>Analyze</span>
                      </button>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {mode === 'text' && (
              <motion.div
                key="text"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="space-y-4"
              >
                <label className="label">Enter Call Transcript</label>
                <textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Paste or type the call transcript here..."
                  className="input h-48 resize-none"
                />
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-500">
                    {textInput.length} characters
                  </span>
                  <button
                    onClick={handleTextAnalysis}
                    disabled={isAnalyzing || textInput.length < 10}
                    className="btn-primary flex items-center space-x-2"
                  >
                    {isAnalyzing ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <FileText className="h-4 w-4" />
                    )}
                    <span>Analyze Text</span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Loading State */}
          {isAnalyzing && (
            <div className="mt-6 text-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary-500 mx-auto" />
              <p className="mt-2 text-slate-600 dark:text-slate-400">
                {t('analyze.analyzing')}
              </p>
              <div className="mt-4 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-primary-500 rounded-full animate-pulse w-2/3"></div>
              </div>
            </div>
          )}
        </div>

        {/* Right: Quick Results or Placeholder */}
        <div className="card p-6">
          {currentResult ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Quick Results
                </h3>
                <ClassificationBadge classification={currentResult.classification} />
              </div>
              <RiskMeter score={currentResult.risk_score} />
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                  <p className="text-sm text-slate-500 dark:text-slate-400">Spam Score</p>
                  <p className="text-2xl font-bold text-orange-500">
                    {(currentResult.spam_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                  <p className="text-sm text-slate-500 dark:text-slate-400">Fraud Score</p>
                  <p className="text-2xl font-bold text-red-500">
                    {(currentResult.fraud_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                  <p className="text-sm text-slate-500 dark:text-slate-400">Phishing Score</p>
                  <p className="text-2xl font-bold text-purple-500">
                    {(currentResult.phishing_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
                  <p className="text-sm text-slate-500 dark:text-slate-400">Robocall Score</p>
                  <p className="text-2xl font-bold text-blue-500">
                    {(currentResult.robocall_score * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center py-12">
              <Volume2 className="h-16 w-16 text-slate-300 dark:text-slate-600 mb-4" />
              <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300">
                No Analysis Yet
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Upload an audio file or enter text to start analysis
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Detailed Results */}
      {currentResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* AI Explanation */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              AI Explanation
            </h3>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              {currentResult.ai_explanation}
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Transcript */}
            <TranscriptViewer
              transcript={currentResult.transcript}
              highlights={currentResult.highlighted_phrases}
              language={currentResult.transcript_language}
            />

            {/* Fraud Indicators */}
            <FraudIndicators
              indicators={currentResult.fraud_indicators}
              keywords={currentResult.suspicious_keywords}
            />
          </div>

          {/* Voice Analysis */}
          {Object.keys(currentResult.voice_characteristics).length > 0 && (
            <VoiceAnalysis
              characteristics={currentResult.voice_characteristics}
              features={currentResult.acoustic_features}
            />
          )}
        </motion.div>
      )}
    </div>
  );
}

function ClassificationBadge({ classification }: { classification: string }) {
  const config: Record<string, { icon: React.ElementType; color: string; bg: string }> = {
    safe: { icon: CheckCircle, color: 'text-success-600', bg: 'bg-success-100 dark:bg-success-900/30' },
    spam: { icon: AlertTriangle, color: 'text-orange-600', bg: 'bg-orange-100 dark:bg-orange-900/30' },
    fraud: { icon: XCircle, color: 'text-danger-600', bg: 'bg-danger-100 dark:bg-danger-900/30' },
    phishing: { icon: AlertTriangle, color: 'text-purple-600', bg: 'bg-purple-100 dark:bg-purple-900/30' },
    robocall: { icon: Volume2, color: 'text-blue-600', bg: 'bg-blue-100 dark:bg-blue-900/30' },
    unknown: { icon: AlertTriangle, color: 'text-slate-600', bg: 'bg-slate-100 dark:bg-slate-700' },
  };

  const { icon: Icon, color, bg } = config[classification] || config.unknown;

  return (
    <div className={clsx('inline-flex items-center space-x-2 px-3 py-1 rounded-full', bg)}>
      <Icon className={clsx('h-4 w-4', color)} />
      <span className={clsx('text-sm font-medium capitalize', color)}>{classification}</span>
    </div>
  );
}
