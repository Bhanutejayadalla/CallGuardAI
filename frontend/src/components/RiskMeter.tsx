import { motion } from 'framer-motion';
import clsx from 'clsx';

interface RiskMeterProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export default function RiskMeter({ score, size = 'md', showLabel = true }: RiskMeterProps) {
  const getRiskLevel = (score: number) => {
    if (score < 20) return { level: 'Safe', color: 'text-success-500', bgColor: 'bg-success-500' };
    if (score < 40) return { level: 'Low Risk', color: 'text-success-500', bgColor: 'bg-success-500' };
    if (score < 60) return { level: 'Medium Risk', color: 'text-warning-500', bgColor: 'bg-warning-500' };
    if (score < 80) return { level: 'High Risk', color: 'text-danger-500', bgColor: 'bg-danger-500' };
    return { level: 'Critical', color: 'text-danger-600', bgColor: 'bg-danger-600' };
  };

  const { level, color, bgColor: _bgColor } = getRiskLevel(score);
  void _bgColor; // Suppress unused variable warning
  
  const sizeConfig = {
    sm: { width: 'w-32', height: 'h-32', text: 'text-2xl', subtext: 'text-xs' },
    md: { width: 'w-48', height: 'h-48', text: 'text-4xl', subtext: 'text-sm' },
    lg: { width: 'w-64', height: 'h-64', text: 'text-5xl', subtext: 'text-base' },
  };

  const { width, height, text, subtext } = sizeConfig[size];

  // Calculate the stroke dasharray for the progress arc
  const circumference = 2 * Math.PI * 45; // radius = 45
  const progress = (score / 100) * circumference * 0.75; // 75% of circle (270 degrees)

  return (
    <div className="flex flex-col items-center">
      <div className={clsx('relative', width, height)}>
        <svg className="w-full h-full transform -rotate-135" viewBox="0 0 100 100">
          {/* Background arc */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            className="text-slate-200 dark:text-slate-700"
            strokeDasharray={`${circumference * 0.75} ${circumference}`}
          />
          {/* Progress arc */}
          <motion.circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            className={color}
            strokeDasharray={`${circumference * 0.75} ${circumference}`}
            initial={{ strokeDashoffset: circumference * 0.75 }}
            animate={{ strokeDashoffset: circumference * 0.75 - progress }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className={clsx(text, 'font-bold', color)}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.3 }}
          >
            {Math.round(score)}
          </motion.span>
          <span className={clsx(subtext, 'text-slate-500 dark:text-slate-400 mt-1')}>
            / 100
          </span>
        </div>
      </div>
      
      {showLabel && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className={clsx(
            'mt-4 px-4 py-2 rounded-full text-sm font-medium',
            score < 40
              ? 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400'
              : score < 70
              ? 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-400'
              : 'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-400'
          )}
        >
          {level}
        </motion.div>
      )}
    </div>
  );
}
