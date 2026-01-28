import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Phone,
  Calendar,
  AlertTriangle,
  ExternalLink,
} from 'lucide-react';
import clsx from 'clsx';

import { getCalls, CallRecord } from '../services/api';

const CLASSIFICATIONS = ['all', 'safe', 'spam', 'fraud', 'phishing', 'robocall'];

export default function HistoryPage() {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const [classification, setClassification] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const pageSize = 10;

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['calls', page, pageSize, classification],
    queryFn: () =>
      getCalls({
        page,
        limit: pageSize,
        classification: classification === 'all' ? undefined : classification,
      }),
    placeholderData: (previousData) => previousData,
  });

  const calls = data?.calls || [];
  const totalCalls = data?.total || 0;
  const totalPages = Math.ceil(totalCalls / pageSize);

  const filteredCalls = searchQuery
    ? calls.filter(
        (call) =>
          call.call_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          call.transcript?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : calls;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          {t('history.title')}
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Browse and search through analyzed calls
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by call ID or transcript..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10 w-full"
          />
        </div>

        {/* Classification Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-slate-400" />
          <select
            value={classification}
            onChange={(e) => {
              setClassification(e.target.value);
              setPage(1);
            }}
            className="input min-w-[150px]"
          >
            {CLASSIFICATIONS.map((cls) => (
              <option key={cls} value={cls}>
                {cls === 'all' ? 'All Classifications' : cls.charAt(0).toUpperCase() + cls.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
        </div>
      ) : filteredCalls.length === 0 ? (
        <div className="card p-12 text-center">
          <Phone className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300">
            No calls found
          </h3>
          <p className="text-slate-500 mt-2">
            Try adjusting your filters or analyze some calls first
          </p>
        </div>
      ) : (
        <>
          {/* Call List */}
          <div className="space-y-4">
            {filteredCalls.map((call, index) => (
              <CallCard key={call.call_id || index} call={call} index={index} />
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Showing {(page - 1) * pageSize + 1} to{' '}
              {Math.min(page * pageSize, totalCalls)} of {totalCalls} calls
            </p>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1 || isFetching}
                className="btn-secondary p-2 disabled:opacity-50"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
              <span className="text-sm text-slate-600 dark:text-slate-400 px-4">
                Page {page} of {totalPages || 1}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages || isFetching}
                className="btn-secondary p-2 disabled:opacity-50"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function CallCard({ call, index }: { call: CallRecord; index: number }) {
  const getClassificationStyle = (classification: string) => {
    switch (classification) {
      case 'safe':
        return 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400';
      case 'fraud':
      case 'phishing':
        return 'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-400';
      case 'spam':
      case 'robocall':
        return 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-400';
      default:
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400';
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 40) return 'text-success-500';
    if (score < 70) return 'text-warning-500';
    return 'text-danger-500';
  };

  return (
    <motion.div
      className="card p-4 hover:shadow-lg transition-shadow"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Call Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-3 mb-2">
            <span
              className={clsx(
                'px-2.5 py-1 rounded-full text-xs font-medium capitalize',
                getClassificationStyle(call.classification)
              )}
            >
              {call.classification}
            </span>
            <span className="text-sm font-mono text-slate-500 truncate">
              {call.call_id}
            </span>
          </div>
          {call.transcript && (
            <p className="text-slate-600 dark:text-slate-400 text-sm line-clamp-2">
              {call.transcript}
            </p>
          )}
        </div>

        {/* Metrics */}
        <div className="flex items-center space-x-6">
          {/* Risk Score */}
          <div className="text-center">
            <div className={clsx('text-2xl font-bold', getRiskColor(call.risk_score))}>
              {call.risk_score.toFixed(0)}
            </div>
            <div className="text-xs text-slate-500">Risk</div>
          </div>

          {/* Duration */}
          {call.duration && (
            <div className="text-center">
              <div className="text-lg font-semibold text-slate-700 dark:text-slate-300">
                {Math.floor(call.duration / 60)}:{String(Math.floor(call.duration % 60)).padStart(2, '0')}
              </div>
              <div className="text-xs text-slate-500">Duration</div>
            </div>
          )}

          {/* Date */}
          <div className="text-center hidden sm:block">
            <div className="flex items-center space-x-1 text-slate-600 dark:text-slate-400">
              <Calendar className="h-4 w-4" />
              <span className="text-sm">
                {new Date(call.created_at).toLocaleDateString()}
              </span>
            </div>
            <div className="text-xs text-slate-500">
              {new Date(call.created_at).toLocaleTimeString()}
            </div>
          </div>

          {/* View Details */}
          <Link
            to={`/calls/${call.call_id}`}
            className="btn-primary p-2"
          >
            <ExternalLink className="h-5 w-5" />
          </Link>
        </div>
      </div>

      {/* Indicators Preview */}
      {call.fraud_indicators && call.fraud_indicators.length > 0 && (
        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
          <div className="flex flex-wrap gap-2">
            {call.fraud_indicators.slice(0, 3).map((indicator, i) => (
              <span
                key={i}
                className="inline-flex items-center space-x-1 px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs text-slate-600 dark:text-slate-400"
              >
                <AlertTriangle className="h-3 w-3 text-warning-500" />
                <span className="capitalize">{(indicator.type || indicator.category || '').replace(/_/g, ' ')}</span>
              </span>
            ))}
            {call.fraud_indicators.length > 3 && (
              <span className="text-xs text-slate-500 py-1">
                +{call.fraud_indicators.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}
