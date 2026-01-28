import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Loader2,
  Download,
  Share2,
  AlertTriangle,
  Shield,
  Clock,
  Calendar,
  Volume2,
  FileText,
} from 'lucide-react';
import clsx from 'clsx';

import { getCall } from '../services/api';
import RiskMeter from '../components/RiskMeter';
import TranscriptViewer from '../components/TranscriptViewer';
import FraudIndicators from '../components/FraudIndicators';
import VoiceAnalysis from '../components/VoiceAnalysis';

export default function CallDetailPage() {
  useTranslation();
  const { callId, id } = useParams<{ callId?: string; id?: string }>();
  const callIdParam = callId || id;

  const { data: call, isLoading, error } = useQuery({
    queryKey: ['call', callIdParam],
    queryFn: () => getCall(callIdParam!),
    enabled: !!callIdParam,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  if (error || !call) {
    return (
      <div className="card p-12 text-center">
        <AlertTriangle className="h-12 w-12 text-danger-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-slate-900 dark:text-white">
          Call Not Found
        </h2>
        <p className="text-slate-500 mt-2">
          The call you're looking for doesn't exist or has been deleted.
        </p>
        <Link to="/history" className="btn-primary mt-4 inline-flex items-center space-x-2">
          <ArrowLeft className="h-4 w-4" />
          <span>Back to History</span>
        </Link>
      </div>
    );
  }

  const getClassificationStyle = (classification: string) => {
    switch (classification) {
      case 'safe':
        return 'bg-success-500 text-white';
      case 'fraud':
      case 'phishing':
        return 'bg-danger-500 text-white';
      case 'spam':
      case 'robocall':
        return 'bg-warning-500 text-white';
      default:
        return 'bg-slate-500 text-white';
    }
  };

  const getClassificationIcon = (classification: string) => {
    switch (classification) {
      case 'safe':
        return <Shield className="h-6 w-6" />;
      default:
        return <AlertTriangle className="h-6 w-6" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link
            to="/history"
            className="inline-flex items-center space-x-2 text-slate-500 hover:text-primary-500 mb-4"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to History</span>
          </Link>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Call Analysis Details
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1 font-mono">
            {call.call_id}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button className="btn-secondary flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button className="btn-secondary flex items-center space-x-2">
            <Share2 className="h-4 w-4" />
            <span>Share</span>
          </button>
        </div>
      </div>

      {/* Classification Banner */}
      <motion.div
        className={clsx(
          'p-6 rounded-xl flex items-center justify-between',
          getClassificationStyle(call.classification)
        )}
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center space-x-4">
          {getClassificationIcon(call.classification)}
          <div>
            <h2 className="text-2xl font-bold capitalize">
              {call.classification} Call
            </h2>
            <p className="opacity-90">
              {call.classification === 'safe'
                ? 'This call appears to be legitimate'
                : `This call has been classified as ${call.classification}`}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-4xl font-bold">{call.risk_score.toFixed(0)}</div>
          <div className="text-sm opacity-90">Risk Score</div>
        </div>
      </motion.div>

      {/* Metadata Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetadataCard
          icon={Calendar}
          label="Analyzed"
          value={call.created_at ? new Date(call.created_at).toLocaleDateString() : 'N/A'}
        />
        <MetadataCard
          icon={Clock}
          label="Duration"
          value={
            call.duration
              ? `${Math.floor(call.duration / 60)}:${String(
                  Math.floor(call.duration % 60)
                ).padStart(2, '0')}`
              : 'N/A'
          }
        />
        <MetadataCard
          icon={FileText}
          label="Words"
          value={call.transcript?.split(' ').length.toString() || '0'}
        />
        <MetadataCard
          icon={AlertTriangle}
          label="Indicators"
          value={call.fraud_indicators?.length.toString() || '0'}
        />
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Transcript */}
        <div className="lg:col-span-2 space-y-6">
          {/* Transcript */}
          {call.transcript && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <TranscriptViewer
                transcript={call.transcript}
                suspiciousPhrases={call.detected_keywords || call.suspicious_keywords || []}
              />
            </motion.div>
          )}

          {/* Fraud Indicators */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <FraudIndicators
              indicators={call.fraud_indicators || []}
              keywords={call.detected_keywords || call.suspicious_keywords || []}
            />
          </motion.div>
        </div>

        {/* Right Column - Metrics */}
        <div className="space-y-6">
          {/* Risk Meter */}
          <motion.div
            className="card p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Risk Assessment
            </h3>
            <div className="flex justify-center">
              <RiskMeter score={call.risk_score} size="lg" />
            </div>
          </motion.div>

          {/* Scores Breakdown */}
          <motion.div
            className="card p-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Analysis Scores
            </h3>
            <div className="space-y-4">
              <ScoreBar
                label="Linguistic Score"
                value={call.linguistic_score ?? 0}
              />
              <ScoreBar
                label="Acoustic Score"
                value={call.acoustic_score ?? 0}
              />
              <ScoreBar
                label="Behavioral Score"
                value={call.behavioral_score ?? call.risk_score ?? 0}
              />
              <ScoreBar
                label="Confidence"
                value={(call.confidence ?? call.confidence_score ?? 0) * 100}
              />
            </div>
          </motion.div>

          {/* Voice Analysis */}
          {call.voice_characteristics && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <VoiceAnalysis characteristics={call.voice_characteristics} />
            </motion.div>
          )}

          {/* Acoustic Features */}
          {call.acoustic_features && (
            <motion.div
              className="card p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                Acoustic Features
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  <div className="text-lg font-semibold text-slate-900 dark:text-white">
                    {call.acoustic_features.pitch_mean?.toFixed(0) || 'N/A'}
                  </div>
                  <div className="text-xs text-slate-500">Pitch (Hz)</div>
                </div>
                <div className="text-center p-3 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  <div className="text-lg font-semibold text-slate-900 dark:text-white">
                    {call.acoustic_features.tempo?.toFixed(0) || 'N/A'}
                  </div>
                  <div className="text-xs text-slate-500">Tempo (BPM)</div>
                </div>
                <div className="text-center p-3 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  <div className="text-lg font-semibold text-slate-900 dark:text-white">
                    {((call.acoustic_features.zero_crossing_rate ?? 0) * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-slate-500">ZCR</div>
                </div>
                <div className="text-center p-3 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  <div className="text-lg font-semibold text-slate-900 dark:text-white">
                    {((call.acoustic_features.spectral_centroid ?? 0) / 1000).toFixed(1)}k
                  </div>
                  <div className="text-xs text-slate-500">Spectral</div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* AI Explanation */}
      {(call.explanation || call.ai_explanation) && (
        <motion.div
          className="card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
            <Volume2 className="h-5 w-5 text-primary-500" />
            <span>AI Explanation</span>
          </h3>
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
            {call.explanation || call.ai_explanation}
          </p>
        </motion.div>
      )}
    </div>
  );
}

function MetadataCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
}) {
  return (
    <div className="card p-4 flex items-center space-x-3">
      <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
        <Icon className="h-5 w-5 text-primary-500" />
      </div>
      <div>
        <div className="text-xs text-slate-500">{label}</div>
        <div className="font-semibold text-slate-900 dark:text-white">{value}</div>
      </div>
    </div>
  );
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  const getColor = (score: number) => {
    if (score < 40) return 'bg-success-500';
    if (score < 70) return 'bg-warning-500';
    return 'bg-danger-500';
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-slate-600 dark:text-slate-400">{label}</span>
        <span className="text-sm font-semibold text-slate-900 dark:text-white">
          {value.toFixed(1)}%
        </span>
      </div>
      <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
        <motion.div
          className={clsx('h-full rounded-full', getColor(value))}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  );
}
