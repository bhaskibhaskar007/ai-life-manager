import React from 'react';
import { Budget } from '../../types';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

interface BudgetProgressMeterProps {
  budgets: Budget[];
  currencySymbol?: string;
}

export const BudgetProgressMeter: React.FC<BudgetProgressMeterProps> = ({
  budgets,
  currencySymbol = '₹',
}) => {
  if (!budgets || budgets.length === 0) {
    return (
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col items-center justify-center text-center">
        <ShieldCheck className="w-8 h-8 text-slate-300 mb-2" />
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300">No Active Budgets</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-xs">
          Set spending limits per category or an overall monthly budget to get proactive risk alerts.
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
      <div>
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">Budget Utilization</h3>
        <p className="text-xs text-slate-500">Live limits vs current expenditure</p>
      </div>

      <div className="space-y-4">
        {budgets.map((b) => {
          const pct = Math.min(100, b.percentage_used || 0);
          const isExceeded = (b.percentage_used || 0) > 100;
          const isAtRisk = (b.percentage_used || 0) >= 80 && !isExceeded;

          return (
            <div key={b.id} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-semibold">
                <div className="flex items-center space-x-1.5">
                  <span className="text-slate-800 dark:text-slate-200">{b.category || 'Overall Monthly Budget'}</span>
                  {isExceeded && <AlertOctagon className="w-3.5 h-3.5 text-rose-500" />}
                  {isAtRisk && <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />}
                </div>
                <span className="text-slate-500 font-medium">
                  {currencySymbol}{b.spent || 0} / {currencySymbol}{b.amount} ({b.percentage_used || 0}%)
                </span>
              </div>

              {/* Progress track */}
              <div className="w-full h-2.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isExceeded
                      ? 'bg-rose-500'
                      : isAtRisk
                      ? 'bg-amber-500'
                      : 'bg-emerald-500'
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
