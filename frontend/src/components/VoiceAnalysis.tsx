import { useTranslation } from 'react-i18next';
import { Volume2, Activity, Gauge, Zap, Brain } from 'lucide-react';
import clsx from 'clsx';

interface VoiceAnalysisProps {
  features?: any;
  characteristics?: any;
}


export default function VoiceAnalysis({ characteristics, features }: VoiceAnalysisProps) {
  const { t } = useTranslation();

  const getToneEmoji = (tone?: string) => {
    switch (tone) {
      case 'aggressive': return '😠';
      case 'assertive': return '💪';
      case 'subdued': return '😔';
      default: return '😐';
    }
  };

  const getSpeedLabel = (speed?: string) => {
    switch (speed) {
      case 'fast': return { label: 'Fast', color: 'text-warning-500' };
      case 'slow': return { label: 'Slow', color: 'text-blue-500' };
      default: return { label: 'Normal', color: 'text-success-500' };
    }
  };

  const getStressLevel = (stress?: string) => {
    switch (stress) {
      case 'high': return { label: 'High', color: 'text-danger-500', width: 'w-full' };
      case 'moderate': return { label: 'Moderate', color: 'text-warning-500', width: 'w-2/3' };
      default: return { label: 'Low', color: 'text-success-500', width: 'w-1/3' };
    }
  };

  const speedConfig = getSpeedLabel(characteristics?.speed);
  const stressConfig = getStressLevel(characteristics?.stress);
  
  // Safely access features with default empty object
  const safeFeatures = features || {};

  return (
    <div className="card p-6">
      <div className="flex items-center space-x-2 mb-6">
        <Volume2 className="h-5 w-5 text-primary-500" />
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          {t('results.voiceAnalysis')}
        </h3>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Tone */}
        <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 min-w-0">
          <div className="flex items-center space-x-2 mb-3">
            <Activity className="h-4 w-4 text-slate-400 flex-shrink-0" />
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Tone</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-2xl flex-shrink-0">{getToneEmoji(characteristics?.tone)}</span>
            <span className="text-base font-semibold text-slate-900 dark:text-white capitalize truncate">
              {characteristics?.tone || 'Neutral'}
            </span>
          </div>
        </div>

        {/* Speaking Speed */}
        <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 min-w-0">
          <div className="flex items-center space-x-2 mb-3">
            <Gauge className="h-4 w-4 text-slate-400 flex-shrink-0" />
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Speed</span>
          </div>
          <div className="flex flex-col">
            <span className={clsx('text-base font-semibold', speedConfig.color)}>
              {speedConfig.label}
            </span>
            {safeFeatures.speaking_rate && (
              <span className="text-xs text-slate-500 mt-1">
                {Math.round(safeFeatures.speaking_rate)} WPM
              </span>
            )}
          </div>
        </div>

        {/* Stress Level */}
        <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 min-w-0">
          <div className="flex items-center space-x-2 mb-3">
            <Zap className="h-4 w-4 text-slate-400 flex-shrink-0" />
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Stress</span>
          </div>
          <div className="space-y-2">
            <span className={clsx('text-base font-semibold', stressConfig.color)}>
              {stressConfig.label}
            </span>
            <div className="h-2 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
              <div className={clsx('h-full rounded-full transition-all', stressConfig.width, 
                stressConfig.color === 'text-danger-500' ? 'bg-danger-500' :
                stressConfig.color === 'text-warning-500' ? 'bg-warning-500' : 'bg-success-500'
              )} />
            </div>
          </div>
        </div>

        {/* Naturalness */}
        <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 min-w-0">
          <div className="flex items-center space-x-2 mb-3">
            <Brain className="h-4 w-4 text-slate-400 flex-shrink-0" />
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Naturalness</span>
          </div>
          <div className="space-y-2">
            <span className={clsx(
              'text-base font-semibold',
              (characteristics?.naturalness || 1) > 0.7 ? 'text-success-500' :
              (characteristics?.naturalness || 1) > 0.4 ? 'text-warning-500' : 'text-danger-500'
            )}>
              {((characteristics?.naturalness || 1) * 100).toFixed(0)}%
            </span>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {(characteristics.naturalness || 1) > 0.7 ? 'Likely human voice' :
               (characteristics.naturalness || 1) > 0.4 ? 'Possibly synthetic' : 'Likely robotic'}
            </p>
          </div>
        </div>
      </div>

      {/* Urgency Meter */}
      {characteristics.urgency !== undefined && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Urgency Level
            </span>
            <span className={clsx(
              'text-sm font-semibold',
              characteristics.urgency > 0.7 ? 'text-danger-500' :
              characteristics.urgency > 0.4 ? 'text-warning-500' : 'text-success-500'
            )}>
              {(characteristics.urgency * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
            <div
              className={clsx(
                'h-full rounded-full transition-all',
                characteristics.urgency > 0.7 ? 'bg-danger-500' :
                characteristics.urgency > 0.4 ? 'bg-warning-500' : 'bg-success-500'
              )}
              style={{ width: `${characteristics.urgency * 100}%` }}
            />
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {characteristics.urgency > 0.7 
              ? '⚠️ High urgency detected - common in scam calls'
              : characteristics.urgency > 0.4
              ? 'Moderate urgency - exercise caution'
              : 'Normal conversational pace'}
          </p>
        </div>
      )}

      {/* Technical Details */}
      {features && Object.keys(features).length > 0 && (
        <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
          <details className="group">
            <summary className="cursor-pointer text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Technical Details
            </summary>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              {safeFeatures.duration && (
                <div>
                  <span className="text-slate-500">Duration</span>
                  <p className="font-medium text-slate-900 dark:text-white">
                    {safeFeatures.duration.toFixed(1)}s
                  </p>
                </div>
              )}
              {safeFeatures.pitch_mean && (
                <div>
                  <span className="text-slate-500">Pitch (Mean)</span>
                  <p className="font-medium text-slate-900 dark:text-white">
                    {safeFeatures.pitch_mean.toFixed(0)} Hz
                  </p>
                </div>
              )}
              {safeFeatures.energy_mean && (
                <div>
                  <span className="text-slate-500">Energy (Mean)</span>
                  <p className="font-medium text-slate-900 dark:text-white">
                    {safeFeatures.energy_mean.toFixed(4)}
                  </p>
                </div>
              )}
              {safeFeatures.synthetic_probability !== undefined && (
                <div>
                  <span className="text-slate-500">Synthetic Prob.</span>
                  <p className="font-medium text-slate-900 dark:text-white">
                    {(safeFeatures.synthetic_probability * 100).toFixed(1)}%
                  </p>
                </div>
              )}
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
