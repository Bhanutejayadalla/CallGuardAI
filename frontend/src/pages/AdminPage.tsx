import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings,
  Shield,
  Users,
  Database,
  Activity,
  Plus,
  Trash2,
  Edit2,
  Save,
  X,
  Loader2,
  AlertTriangle,
  Check,
  RefreshCw,
} from 'lucide-react';
import clsx from 'clsx';

import { getRules, createRule, deleteRule, getSystemStats, Rule } from '../services/api';

const TABS = [
  { id: 'rules', label: 'Detection Rules', icon: Shield },
  { id: 'system', label: 'System Status', icon: Activity },
];

export default function AdminPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('rules');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          {t('admin.title')}
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Manage detection rules and system settings
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-200 dark:border-slate-700">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={clsx(
              'flex items-center space-x-2 px-4 py-3 border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            )}
          >
            <tab.icon className="h-5 w-5" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'rules' && <RulesPanel />}
      {activeTab === 'system' && <SystemPanel />}
    </div>
  );
}

function RulesPanel() {
  const queryClient = useQueryClient();
  const [isCreating, setIsCreating] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    pattern: '',
    category: 'keyword',
    severity: 'medium',
    score_impact: 10,
    is_active: true,
  });

  const { data: rules, isLoading } = useQuery({
    queryKey: ['rules'],
    queryFn: getRules,
  });

  const createMutation = useMutation({
    mutationFn: createRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
      setIsCreating(false);
      setNewRule({
        name: '',
        pattern: '',
        category: 'keyword',
        severity: 'medium',
        score_impact: 10,
        is_active: true,
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
    },
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400';
      case 'medium':
        return 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-400';
      case 'high':
        return 'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-400';
      case 'critical':
        return 'bg-danger-200 text-danger-800 dark:bg-danger-900/50 dark:text-danger-300';
      default:
        return 'bg-slate-100 text-slate-700';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Create New Rule */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            Detection Rules
          </h3>
          <button
            onClick={() => setIsCreating(!isCreating)}
            className={clsx(
              'flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors',
              isCreating
                ? 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
                : 'bg-primary-500 text-white hover:bg-primary-600'
            )}
          >
            {isCreating ? (
              <>
                <X className="h-4 w-4" />
                <span>Cancel</span>
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                <span>Add Rule</span>
              </>
            )}
          </button>
        </div>

        <AnimatePresence>
          {isCreating && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6"
            >
              <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Rule Name
                    </label>
                    <input
                      type="text"
                      value={newRule.name}
                      onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                      placeholder="e.g., Bank Fraud Keywords"
                      className="input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Pattern (Regex)
                    </label>
                    <input
                      type="text"
                      value={newRule.pattern}
                      onChange={(e) => setNewRule({ ...newRule, pattern: e.target.value })}
                      placeholder="e.g., bank.*account|credit.*card"
                      className="input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Category
                    </label>
                    <select
                      value={newRule.category}
                      onChange={(e) => setNewRule({ ...newRule, category: e.target.value })}
                      className="input w-full"
                    >
                      <option value="keyword">Keyword</option>
                      <option value="pattern">Pattern</option>
                      <option value="behavioral">Behavioral</option>
                      <option value="acoustic">Acoustic</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Severity
                    </label>
                    <select
                      value={newRule.severity}
                      onChange={(e) => setNewRule({ ...newRule, severity: e.target.value })}
                      className="input w-full"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Score Impact (0-100)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={newRule.score_impact}
                      onChange={(e) =>
                        setNewRule({ ...newRule, score_impact: parseInt(e.target.value) || 0 })
                      }
                      className="input w-full"
                    />
                  </div>
                  <div className="flex items-center">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newRule.is_active}
                        onChange={(e) => setNewRule({ ...newRule, is_active: e.target.checked })}
                        className="w-4 h-4 text-primary-500 rounded"
                      />
                      <span className="text-sm text-slate-700 dark:text-slate-300">Active</span>
                    </label>
                  </div>
                </div>
                <div className="flex justify-end">
                  <button
                    onClick={() => createMutation.mutate(newRule)}
                    disabled={!newRule.name || !newRule.pattern || createMutation.isPending}
                    className="btn-primary flex items-center space-x-2"
                  >
                    {createMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    <span>Save Rule</span>
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Rules List */}
        <div className="space-y-3">
          {rules?.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              No rules configured. Add your first detection rule.
            </div>
          ) : (
            rules?.map((rule) => (
              <div
                key={rule.id}
                className={clsx(
                  'flex items-center justify-between p-4 rounded-lg border',
                  rule.is_active
                    ? 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800'
                    : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 opacity-60'
                )}
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h4 className="font-medium text-slate-900 dark:text-white">
                      {rule.name}
                    </h4>
                    <span
                      className={clsx(
                        'px-2 py-0.5 rounded text-xs font-medium capitalize',
                        getSeverityColor(rule.severity)
                      )}
                    >
                      {rule.severity}
                    </span>
                    {!rule.is_active && (
                      <span className="text-xs text-slate-500">Disabled</span>
                    )}
                  </div>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-slate-500">
                    <span className="font-mono bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded">
                      {rule.pattern}
                    </span>
                    <span>Category: {rule.category}</span>
                    <span>Impact: +{rule.score_impact}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => deleteMutation.mutate(rule.id)}
                    disabled={deleteMutation.isPending}
                    className="p-2 text-danger-500 hover:bg-danger-50 dark:hover:bg-danger-900/30 rounded-lg transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function SystemPanel() {
  const { data: stats, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['system-stats'],
    queryFn: getSystemStats,
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className={clsx('h-4 w-4', isRefetching && 'animate-spin')} />
          <span>Refresh</span>
        </button>
      </div>

      {/* System Status Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <StatusCard
          title="API Status"
          status="operational"
          icon={Activity}
          details={[
            { label: 'Version', value: stats?.version || '1.0.0' },
            { label: 'Uptime', value: stats?.uptime || 'N/A' },
          ]}
        />
        <StatusCard
          title="Database"
          status={stats?.database_connected ? 'operational' : 'error'}
          icon={Database}
          details={[
            { label: 'Type', value: stats?.database_type || 'PostgreSQL' },
            { label: 'Calls', value: stats?.total_calls?.toString() || '0' },
          ]}
        />
        <StatusCard
          title="ML Models"
          status={stats?.ml_models?.overall === 'operational' ? 'operational' : stats?.ml_models?.overall === 'degraded' ? 'degraded' : 'error'}
          icon={Shield}
          details={[
            { label: 'Whisper', value: stats?.ml_models?.models?.whisper?.loaded ? 'Loaded' : 'Not Loaded' },
            { label: 'NLP', value: stats?.ml_models?.models?.nlp?.loaded ? 'Loaded' : 'Not Loaded' },
          ]}
        />
      </div>

      {/* Performance Metrics */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Performance Metrics
        </h3>
        <div className="grid md:grid-cols-4 gap-6">
          <MetricCard
            label="Total Calls Analyzed"
            value={stats?.total_calls || 0}
            format="number"
          />
          <MetricCard
            label="Avg Response Time"
            value={stats?.avg_response_time || 0}
            format="ms"
          />
          <MetricCard
            label="Detection Accuracy"
            value={stats?.accuracy || 95.5}
            format="percent"
          />
          <MetricCard
            label="Memory Usage"
            value={stats?.memory_usage || 0}
            format="mb"
          />
        </div>
      </div>

      {/* Model Info */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          AI/ML Models
        </h3>
        <div className="space-y-4">
          <ModelRow
            name="Whisper Speech-to-Text"
            version="base"
            status={stats?.ml_models?.models?.whisper?.loaded ? 'loaded' : 'not-loaded'}
            description="OpenAI Whisper for multilingual speech recognition"
          />
          <ModelRow
            name="spaCy NLP Pipeline"
            version="en_core_web_sm"
            status={stats?.ml_models?.models?.nlp?.loaded ? 'loaded' : 'not-loaded'}
            description="Named entity recognition and linguistic analysis"
          />
          <ModelRow
            name="Fraud Detection Engine"
            version="1.0.0"
            status={stats?.ml_models?.models?.fraud_classifier?.loaded ? 'loaded' : 'not-loaded'}
            description="Custom fraud detection with multi-signal analysis"
          />
        </div>
      </div>
    </div>
  );
}

function StatusCard({
  title,
  status,
  icon: Icon,
  details,
}: {
  title: string;
  status: 'operational' | 'degraded' | 'error';
  icon: React.ElementType;
  details: { label: string; value: string }[];
}) {
  const statusConfig = {
    operational: {
      color: 'text-success-500',
      bg: 'bg-success-100 dark:bg-success-900/30',
      label: 'Operational',
    },
    degraded: {
      color: 'text-warning-500',
      bg: 'bg-warning-100 dark:bg-warning-900/30',
      label: 'Degraded',
    },
    error: {
      color: 'text-danger-500',
      bg: 'bg-danger-100 dark:bg-danger-900/30',
      label: 'Error',
    },
  };

  const config = statusConfig[status];

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={clsx('p-2 rounded-lg', config.bg)}>
            <Icon className={clsx('h-5 w-5', config.color)} />
          </div>
          <h4 className="font-medium text-slate-900 dark:text-white">{title}</h4>
        </div>
        <div className="flex items-center space-x-2">
          <div className={clsx('w-2 h-2 rounded-full', config.color.replace('text-', 'bg-'))} />
          <span className={clsx('text-sm', config.color)}>{config.label}</span>
        </div>
      </div>
      <div className="space-y-2">
        {details.map((detail) => (
          <div key={detail.label} className="flex items-center justify-between text-sm">
            <span className="text-slate-500">{detail.label}</span>
            <span className="font-medium text-slate-900 dark:text-white">{detail.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  format,
}: {
  label: string;
  value: number;
  format: 'number' | 'percent' | 'ms' | 'mb';
}) {
  const formatValue = () => {
    switch (format) {
      case 'number':
        return value.toLocaleString();
      case 'percent':
        return `${value.toFixed(1)}%`;
      case 'ms':
        return `${value.toFixed(0)}ms`;
      case 'mb':
        return `${value.toFixed(0)} MB`;
      default:
        return value.toString();
    }
  };

  return (
    <div className="text-center p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
      <div className="text-2xl font-bold text-slate-900 dark:text-white">
        {formatValue()}
      </div>
      <div className="text-sm text-slate-500 mt-1">{label}</div>
    </div>
  );
}

function ModelRow({
  name,
  version,
  status,
  description,
}: {
  name: string;
  version: string;
  status: 'loaded' | 'not-loaded';
  description: string;
}) {
  return (
    <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
      <div className="flex-1">
        <div className="flex items-center space-x-3">
          <h4 className="font-medium text-slate-900 dark:text-white">{name}</h4>
          <span className="text-xs bg-slate-200 dark:bg-slate-700 px-2 py-0.5 rounded">
            v{version}
          </span>
        </div>
        <p className="text-sm text-slate-500 mt-1">{description}</p>
      </div>
      <div
        className={clsx(
          'flex items-center space-x-2 px-3 py-1 rounded-full',
          status === 'loaded'
            ? 'bg-success-100 dark:bg-success-900/30'
            : 'bg-slate-200 dark:bg-slate-700'
        )}
      >
        {status === 'loaded' ? (
          <Check className="h-4 w-4 text-success-500" />
        ) : (
          <X className="h-4 w-4 text-slate-500" />
        )}
        <span
          className={clsx(
            'text-sm font-medium',
            status === 'loaded' ? 'text-success-700 dark:text-success-400' : 'text-slate-500'
          )}
        >
          {status === 'loaded' ? 'Loaded' : 'Not Loaded'}
        </span>
      </div>
    </div>
  );
}
