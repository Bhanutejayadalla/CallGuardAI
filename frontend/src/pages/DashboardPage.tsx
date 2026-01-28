import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import {
  Phone,
  AlertTriangle,
  Shield,
  TrendingUp,
  Loader2,
  RefreshCw,
  Calendar,
} from 'lucide-react';
import clsx from 'clsx';

import { getDashboard, getTrends } from '../services/api';

const COLORS = {
  safe: '#22c55e',
  spam: '#f97316',
  fraud: '#ef4444',
  phishing: '#a855f7',
  robocall: '#3b82f6',
};

export default function DashboardPage() {
  const { t } = useTranslation();

  const { data: dashboard, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['dashboard', 30],
    queryFn: () => getDashboard(30),
  });

  const { data: trends } = useQuery({
    queryKey: ['trends', 30],
    queryFn: () => getTrends(30),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  const stats = dashboard?.stats;
  const classificationData = dashboard?.classification_breakdown
    ? Object.entries(dashboard.classification_breakdown).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
        color: COLORS[name as keyof typeof COLORS] || '#64748b',
      }))
    : [];

  const riskDistributionData = dashboard?.risk_distribution
    ? Object.entries(dashboard.risk_distribution).map(([range, count]) => ({
        range,
        count,
      }))
    : [];

  const trendData = trends?.trends?.slice(-14) || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            {t('dashboard.title')}
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Real-time call analysis insights
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className={clsx('h-4 w-4', isRefetching && 'animate-spin')} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title={t('dashboard.totalCalls')}
          value={stats?.total_calls || 0}
          icon={Phone}
          color="text-primary-500"
          bgColor="bg-primary-100 dark:bg-primary-900/30"
        />
        <StatCard
          title={t('dashboard.fraudDetected')}
          value={(stats?.fraud_calls || 0) + (stats?.phishing_calls || 0)}
          icon={AlertTriangle}
          color="text-danger-500"
          bgColor="bg-danger-100 dark:bg-danger-900/30"
        />
        <StatCard
          title={t('dashboard.avgRiskScore')}
          value={`${stats?.average_risk_score?.toFixed(1) || 0}`}
          icon={TrendingUp}
          color="text-warning-500"
          bgColor="bg-warning-100 dark:bg-warning-900/30"
          suffix="/100"
        />
        <StatCard
          title={t('dashboard.detectionRate')}
          value={`${stats?.detection_rate?.toFixed(1) || 0}%`}
          icon={Shield}
          color="text-success-500"
          bgColor="bg-success-100 dark:bg-success-900/30"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Trend Chart */}
        <motion.div
          className="card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              {t('dashboard.trends')}
            </h3>
            <div className="flex items-center space-x-2 text-sm text-slate-500">
              <Calendar className="h-4 w-4" />
              <span>Last 14 days</span>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorFraud" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  stroke="#94a3b8"
                  fontSize={12}
                />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#f8fafc',
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#0ea5e9"
                  fillOpacity={1}
                  fill="url(#colorTotal)"
                  name="Total Calls"
                />
                <Area
                  type="monotone"
                  dataKey="fraud"
                  stroke="#ef4444"
                  fillOpacity={1}
                  fill="url(#colorFraud)"
                  name="Fraud"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Classification Pie Chart */}
        <motion.div
          className="card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Classification Breakdown
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={classificationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {classificationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#f8fafc',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            {classificationData.map((item) => (
              <div key={item.name} className="flex items-center space-x-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm text-slate-600 dark:text-slate-400">
                  {item.name}: {item.value}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Risk Distribution */}
        <motion.div
          className="card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            {t('dashboard.distribution')}
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDistributionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="range" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#f8fafc',
                  }}
                />
                <Bar
                  dataKey="count"
                  fill="#0ea5e9"
                  radius={[4, 4, 0, 0]}
                  name="Calls"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Top Fraud Indicators */}
        <motion.div
          className="card p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Top Fraud Indicators
          </h3>
          <div className="space-y-3">
            {dashboard?.top_fraud_indicators?.slice(0, 6).map((indicator, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{index < 3 ? '🔴' : '🟡'}</span>
                  <span className="text-slate-700 dark:text-slate-300 capitalize">
                    {indicator.indicator.replace(/_/g, ' ')}
                  </span>
                </div>
                <span className="font-semibold text-slate-900 dark:text-white">
                  {indicator.count}
                </span>
              </div>
            )) || (
              <p className="text-slate-500 text-center py-8">No data available</p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Recent Calls */}
      <motion.div
        className="card p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          {t('dashboard.recentCalls')}
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Call ID</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Classification</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Risk Score</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Time</th>
              </tr>
            </thead>
            <tbody>
              {dashboard?.recent_calls?.map((call) => (
                <tr
                  key={call.call_id}
                  className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                >
                  <td className="py-3 px-4 text-sm font-mono text-slate-600 dark:text-slate-400">
                    {call.call_id}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={clsx(
                        'px-2 py-1 rounded-full text-xs font-medium capitalize',
                        call.classification === 'safe'
                          ? 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400'
                          : call.classification === 'fraud' || call.classification === 'phishing'
                          ? 'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-400'
                          : 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-400'
                      )}
                    >
                      {call.classification}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className={clsx(
                            'h-full rounded-full',
                            call.risk_score < 40 ? 'bg-success-500' :
                            call.risk_score < 70 ? 'bg-warning-500' : 'bg-danger-500'
                          )}
                          style={{ width: `${call.risk_score}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                        {call.risk_score.toFixed(0)}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-500">
                    {new Date(call.created_at).toLocaleString()}
                  </td>
                </tr>
              )) || (
                <tr>
                  <td colSpan={4} className="text-center py-8 text-slate-500">
                    No recent calls
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
  bgColor,
  suffix,
}: {
  title: string;
  value: number | string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  suffix?: string;
}) {
  return (
    <motion.div
      className="card p-6"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">{title}</p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
            {value}
            {suffix && <span className="text-sm font-normal text-slate-500">{suffix}</span>}
          </p>
        </div>
        <div className={clsx('p-3 rounded-lg', bgColor)}>
          <Icon className={clsx('h-6 w-6', color)} />
        </div>
      </div>
    </motion.div>
  );
}
