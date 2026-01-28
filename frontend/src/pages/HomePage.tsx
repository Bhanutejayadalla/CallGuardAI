import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  Shield,
  Mic,
  Brain,
  Globe,
  Eye,
  Zap,
  BarChart3,
  Lock,
  ArrowRight,
  Phone,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';

export default function HomePage() {
  const { t } = useTranslation();

  const features = [
    {
      icon: Zap,
      title: t('home.features.realtime'),
      description: t('home.features.realtimeDesc'),
      color: 'text-yellow-500',
      bg: 'bg-yellow-100 dark:bg-yellow-900/20',
    },
    {
      icon: Brain,
      title: t('home.features.aiPowered'),
      description: t('home.features.aiPoweredDesc'),
      color: 'text-purple-500',
      bg: 'bg-purple-100 dark:bg-purple-900/20',
    },
    {
      icon: Globe,
      title: t('home.features.multilingual'),
      description: t('home.features.multilingualDesc'),
      color: 'text-blue-500',
      bg: 'bg-blue-100 dark:bg-blue-900/20',
    },
    {
      icon: Eye,
      title: t('home.features.explainable'),
      description: t('home.features.explainableDesc'),
      color: 'text-green-500',
      bg: 'bg-green-100 dark:bg-green-900/20',
    },
  ];

  const threatTypes = [
    { name: 'Spam', icon: Phone, color: 'text-orange-500', count: '45%' },
    { name: 'Fraud', icon: AlertTriangle, color: 'text-red-500', count: '28%' },
    { name: 'Phishing', icon: Lock, color: 'text-purple-500', count: '18%' },
    { name: 'Robocall', icon: BarChart3, color: 'text-blue-500', count: '9%' },
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center space-x-2 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 px-4 py-2 rounded-full mb-6">
            <Shield className="h-4 w-4" />
            <span className="text-sm font-medium">AI-Powered Protection</span>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-slate-900 dark:text-white mb-6">
            {t('home.title')}
          </h1>
          
          <p className="text-lg md:text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto mb-8">
            {t('home.subtitle')}
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Link to="/analyze" className="btn-primary flex items-center space-x-2 text-lg px-8 py-3">
              <Mic className="h-5 w-5" />
              <span>{t('home.cta')}</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link to="/dashboard" className="btn-secondary flex items-center space-x-2 text-lg px-8 py-3">
              <BarChart3 className="h-5 w-5" />
              <span>View Dashboard</span>
            </Link>
          </div>
        </motion.div>

        {/* Animated Shield */}
        <motion.div
          className="mt-12 relative"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <div className="relative w-64 h-64 mx-auto">
            <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-primary-600 rounded-full opacity-20 animate-pulse"></div>
            <div className="absolute inset-4 bg-gradient-to-r from-primary-500 to-primary-700 rounded-full opacity-30 animate-pulse" style={{ animationDelay: '0.5s' }}></div>
            <div className="absolute inset-8 bg-white dark:bg-slate-800 rounded-full shadow-xl flex items-center justify-center">
              <Shield className="h-24 w-24 text-primary-500" />
            </div>
          </div>
        </motion.div>
      </section>

      {/* Stats Section */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Calls Analyzed', value: '2.5M+' },
          { label: 'Threats Blocked', value: '450K+' },
          { label: 'Accuracy Rate', value: '99.2%' },
          { label: 'Languages', value: '10+' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            className="card p-6 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * index }}
          >
            <div className="text-3xl md:text-4xl font-bold text-primary-500 mb-2">
              {stat.value}
            </div>
            <div className="text-sm text-slate-600 dark:text-slate-400">
              {stat.label}
            </div>
          </motion.div>
        ))}
      </section>

      {/* Features Section */}
      <section>
        <h2 className="text-2xl md:text-3xl font-bold text-center text-slate-900 dark:text-white mb-8">
          Comprehensive Call Protection
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="card p-6 hover:shadow-lg transition-shadow"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
            >
              <div className={`inline-flex p-3 rounded-lg ${feature.bg} mb-4`}>
                <feature.icon className={`h-6 w-6 ${feature.color}`} />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Threat Types Section */}
      <section className="card p-8">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6 text-center">
          Threats We Detect
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {threatTypes.map((threat) => (
            <div key={threat.name} className="text-center">
              <div className={`inline-flex p-4 rounded-full bg-slate-100 dark:bg-slate-700 mb-3`}>
                <threat.icon className={`h-8 w-8 ${threat.color}`} />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white">{threat.name}</h3>
              <p className="text-2xl font-bold text-primary-500 mt-1">{threat.count}</p>
              <p className="text-xs text-slate-500">of detected threats</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section>
        <h2 className="text-2xl md:text-3xl font-bold text-center text-slate-900 dark:text-white mb-8">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              step: 1,
              title: 'Upload or Stream',
              description: 'Upload a recorded call or stream live audio for analysis',
              icon: Mic,
            },
            {
              step: 2,
              title: 'AI Analysis',
              description: 'Our AI analyzes voice, language, and behavior patterns',
              icon: Brain,
            },
            {
              step: 3,
              title: 'Get Results',
              description: 'Receive instant classification with detailed explanations',
              icon: CheckCircle,
            },
          ].map((item, index) => (
            <motion.div
              key={item.step}
              className="text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 * index }}
            >
              <div className="relative inline-flex">
                <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                  <item.icon className="h-8 w-8 text-primary-500" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {item.step}
                </div>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mt-4 mb-2">
                {item.title}
              </h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                {item.description}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="card bg-gradient-to-r from-primary-500 to-primary-700 p-8 md:p-12 text-center text-white">
        <h2 className="text-2xl md:text-3xl font-bold mb-4">
          Ready to Protect Your Calls?
        </h2>
        <p className="text-primary-100 mb-6 max-w-2xl mx-auto">
          Start analyzing calls now and protect yourself from spam, fraud, and phishing attempts.
        </p>
        <Link
          to="/analyze"
          className="inline-flex items-center space-x-2 bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
        >
          <Mic className="h-5 w-5" />
          <span>Start Free Analysis</span>
        </Link>
      </section>
    </div>
  );
}
