import React from 'react';
import { Budget } from '../../types';
import { PiggyBank, Plus, AlertCircle, CheckCircle2, TrendingUp } from 'lucide-react';

interface BudgetListProps {
  budgets: Budget[];
  onOpenAddModal: () => void;
  currencySymbol?: string;
}

export const BudgetList: React.FC<BudgetListProps> = ({
  budgets,
  onOpenAddModal,
  currencySymbol = '₹',
}) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">Active Budget Caps</h3>
          <p className="text-xs text-slate-500">
            Automated spending controls monitored by FastMCP analytics
          </p>
        </div>
        <button
          onClick={onOpenAddModal}
          className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          <span>Set Budget</span>
        </button>
      </div>

      {budgets.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <PiggyBank className="w-12 h-12 text-brand-400 mx-auto mb-3" />
          <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">No Spending Limits Defined</h4>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Create an overall monthly budget or category-specific caps to receive risk alerts and safe daily spending guidelines.
          </p>
          <button
            onClick={onOpenAddModal}
            className="mt-4 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold transition-colors"
          >
            Create Your First Budget
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {budgets.map((b) => {
            const isExceeded = (b.percentage_used || 0) > 100;
            const isAtRisk = (b.percentage_used || 0) >= 80 && !isExceeded;
            const remaining = b.remaining !== undefined ? b.remaining : b.amount - (b.spent || 0);

            return (
              <div
                key={b.id}
                className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between space-y-4 hover:border-brand-500/40 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">
                      {b.category || 'Overall Monthly Limit'}
                    </span>
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                      {b.period}
                    </span>
                  </div>

                  <div className="mt-3 flex items-baseline justify-between">
                    <div>
                      <span className="text-xl font-black text-slate-900 dark:text-white">
                        {currencySymbol}{b.spent || 0}
                      </span>
                      <span className="text-xs text-slate-400"> / {currencySymbol}{b.amount}</span>
                    </div>
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                        isExceeded
                          ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400'
                          : isAtRisk
                          ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
                          : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                      }`}
                    >
                      {b.percentage_used || 0}%
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div>
                  <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden mb-2">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isExceeded ? 'bg-rose-500' : isAtRisk ? 'bg-amber-500' : 'bg-brand-600'
                      }`}
                      style={{ width: `${Math.min(100, b.percentage_used || 0)}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>
                      {remaining >= 0
                        ? `${currencySymbol}${remaining} remaining`
                        : `${currencySymbol}${Math.abs(remaining)} exceeded`}
                    </span>
                    <span className="capitalize font-medium text-slate-600 dark:text-slate-400">
                      {b.status?.replace('_', ' ') || 'On Track'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
