import { useTranslation } from 'react-i18next';
import { FileText, Globe } from 'lucide-react';
import clsx from 'clsx';
import { HighlightedPhrase } from '../stores/analysisStore';

interface TranscriptViewerProps {
  transcript: string;
  highlights: HighlightedPhrase[];
  language: string;
}

export default function TranscriptViewer({ transcript, highlights, language }: TranscriptViewerProps) {
  const { t } = useTranslation();

  const languageNames: Record<string, string> = {
    en: 'English',
    hi: 'Hindi',
    ta: 'Tamil',
    te: 'Telugu',
    bn: 'Bengali',
    mr: 'Marathi',
    gu: 'Gujarati',
    kn: 'Kannada',
    ml: 'Malayalam',
    pa: 'Punjabi',
  };

  // Apply highlights to transcript
  const renderHighlightedTranscript = () => {
    if (!highlights || highlights.length === 0) {
      return <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{transcript}</p>;
    }

    // Sort highlights by start position
    const sortedHighlights = [...highlights].sort((a, b) => a.start - b.start);
    
    const parts: JSX.Element[] = [];
    let lastIndex = 0;

    sortedHighlights.forEach((highlight, index) => {
      // Add text before highlight
      if (highlight.start > lastIndex) {
        parts.push(
          <span key={`text-${index}`}>
            {transcript.slice(lastIndex, highlight.start)}
          </span>
        );
      }

      // Add highlighted text
      const highlightClass = getHighlightClass(highlight.category, highlight.severity);
      parts.push(
        <span
          key={`highlight-${index}`}
          className={clsx(
            'px-1 py-0.5 rounded cursor-help relative group',
            highlightClass
          )}
          title={`${highlight.category}: ${highlight.text}`}
        >
          {highlight.text}
          {/* Tooltip */}
          <span className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-slate-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
            {highlight.category.charAt(0).toUpperCase() + highlight.category.slice(1)} - {highlight.severity}
          </span>
        </span>
      );

      lastIndex = highlight.end;
    });

    // Add remaining text
    if (lastIndex < transcript.length) {
      parts.push(
        <span key="text-end">
          {transcript.slice(lastIndex)}
        </span>
      );
    }

    return <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{parts}</p>;
  };

  const getHighlightClass = (category: string, severity: string): string => {
    const base = {
      spam: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300',
      fraud: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
      phishing: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300',
      robocall: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
      general: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
    };

    return base[category as keyof typeof base] || base.general;
  };

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <FileText className="h-5 w-5 text-slate-400" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            {t('results.transcript')}
          </h3>
        </div>
        <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
          <Globe className="h-4 w-4" />
          <span>{languageNames[language] || language.toUpperCase()}</span>
        </div>
      </div>

      {/* Legend */}
      {highlights && highlights.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="text-xs text-slate-500">Highlights:</span>
          <span className="px-2 py-0.5 text-xs rounded bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300">
            Fraud
          </span>
          <span className="px-2 py-0.5 text-xs rounded bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300">
            Phishing
          </span>
          <span className="px-2 py-0.5 text-xs rounded bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300">
            Spam
          </span>
          <span className="px-2 py-0.5 text-xs rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300">
            Urgency
          </span>
        </div>
      )}

      {/* Transcript content */}
      <div className="max-h-96 overflow-y-auto bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4">
        {transcript ? (
          renderHighlightedTranscript()
        ) : (
          <p className="text-slate-500 dark:text-slate-400 italic">
            No transcript available
          </p>
        )}
      </div>

      {/* Stats */}
      {transcript && (
        <div className="mt-4 flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
          <span>{transcript.split(/\s+/).length} words</span>
          <span>{highlights?.length || 0} suspicious phrases detected</span>
        </div>
      )}
    </div>
  );
}
