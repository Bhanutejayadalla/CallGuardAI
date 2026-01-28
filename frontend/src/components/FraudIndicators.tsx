import { useTranslation } from 'react-i18next';
import { AlertTriangle, Tag, Shield } from 'lucide-react';
import clsx from 'clsx';
import { FraudIndicator } from '../stores/analysisStore';

interface FraudIndicatorsProps {
  indicators: FraudIndicator[];
  keywords: string[];
}

export default function FraudIndicators({ indicators, keywords }: FraudIndicatorsProps) {
  const { t } = useTranslation();

  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'high':
        return {
          color: 'text-danger-600 dark:text-danger-400',
          bg: 'bg-danger-100 dark:bg-danger-900/30',
          border: 'border-danger-200 dark:border-danger-800',
        };
      case 'medium':
        return {
          color: 'text-warning-600 dark:text-warning-400',
          bg: 'bg-warning-100 dark:bg-warning-900/30',
          border: 'border-warning-200 dark:border-warning-800',
        };
      default:
        return {
          color: 'text-slate-600 dark:text-slate-400',
          bg: 'bg-slate-100 dark:bg-slate-700',
          border: 'border-slate-200 dark:border-slate-600',
        };
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'fraud':
        return '🚨';
      case 'phishing':
        return '🎣';
      case 'spam':
        return '📢';
      case 'robocall':
        return '🤖';
      default:
        return '⚠️';
    }
  };

  return (
    <div className="card p-6">
      <div className="flex items-center space-x-2 mb-4">
        <AlertTriangle className="h-5 w-5 text-warning-500" />
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          {t('results.indicators')}
        </h3>
      </div>

      {/* Indicators List */}
      {indicators && indicators.length > 0 ? (
        <div className="space-y-3 mb-6">
          {indicators.map((indicator, index) => {
            const config = getSeverityConfig(indicator.severity);
            return (
              <div
                key={index}
                className={clsx(
                  'p-3 rounded-lg border',
                  config.bg,
                  config.border
                )}
              >
                <div className="flex items-start space-x-3">
                  <span className="text-xl">{getCategoryIcon(indicator.category)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className={clsx('font-medium capitalize', config.color)}>
                        {indicator.type}
                      </span>
                      <span className={clsx(
                        'px-2 py-0.5 text-xs rounded-full capitalize',
                        indicator.severity === 'high'
                          ? 'bg-danger-200 text-danger-700 dark:bg-danger-800 dark:text-danger-200'
                          : indicator.severity === 'medium'
                          ? 'bg-warning-200 text-warning-700 dark:bg-warning-800 dark:text-warning-200'
                          : 'bg-slate-200 text-slate-700 dark:bg-slate-600 dark:text-slate-200'
                      )}>
                        {indicator.severity}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">
                      {indicator.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="flex items-center space-x-2 text-success-600 dark:text-success-400 mb-6">
          <Shield className="h-5 w-5" />
          <span>No fraud indicators detected</span>
        </div>
      )}

      {/* Suspicious Keywords */}
      <div>
        <div className="flex items-center space-x-2 mb-3">
          <Tag className="h-4 w-4 text-slate-400" />
          <h4 className="font-medium text-slate-700 dark:text-slate-300">
            {t('results.keywords')}
          </h4>
        </div>

        {keywords && keywords.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {keywords.map((keyword, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-300 rounded-full text-sm"
              >
                {keyword}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            No suspicious keywords found
          </p>
        )}
      </div>
    </div>
  );
}
