import React from 'react';
import { Sparkles, Info, AlertCircle, ArrowUpRight } from 'lucide-react';
import { FinancialInsight } from '../../types';

interface FinancialInsightBannerProps {
  insight?: FinancialInsight | null;
  currencySymbol?: string;
  onExploreMore?: () => void;
}

export const FinancialInsightBanner: React.FC<FinancialInsightBannerProps> = ({
  insight,
  onExploreMore,
}) => {
  if (!insight) return null;

  return (
    <div className="p-5 rounded-2xl bg-gradient-to-r from-brand-600/10 via-indigo-600/10 to-purple-600/10 border border-brand-500/20 dark:border-brand-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
      <div className="flex items-start space-x-3.5">
        <div className="w-10 h-10 rounded-xl bg-brand-600 text-white flex items-center justify-center flex-shrink-0 shadow-md shadow-brand-500/20">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">AI Financial Insight</h4>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-700 dark:text-brand-300">
              Verified Data
            </span>
          </div>
          <p className="text-xs text-slate-700 dark:text-slate-300 mt-1 leading-relaxed max-w-2xl">
            {insight.insight_text}
          </p>
          <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 flex items-center gap-1">
            <Info className="w-3 h-3 inline" /> {insight.disclaimer}
          </p>
        </div>
      </div>

      {insight.unusual_expenses && insight.unusual_expenses.length > 0 && (
        <div className="flex-shrink-0 flex items-center space-x-2 bg-amber-500/10 border border-amber-500/20 px-3 py-2 rounded-xl text-amber-700 dark:text-amber-300 text-xs font-semibold">
          <AlertCircle className="w-4 h-4 text-amber-500" />
          <span>{insight.unusual_expenses.length} unusual expense flagged</span>
        </div>
      )}
    </div>
  );
};
