import React from 'react';
import { Expense } from '../../types';

interface SpendingHeatmapProps {
  expenses: Expense[];
  currencySymbol?: string;
}

export const SpendingHeatmap: React.FC<SpendingHeatmapProps> = ({
  expenses,
  currencySymbol = '₹',
}) => {
  // Generate 28-day calendar grid for spending intensity
  const today = new Date();
  const days = Array.from({ length: 28 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() - (27 - i));
    const dateStr = d.toISOString().split('T')[0];
    const total = expenses.filter((e) => e.date === dateStr).reduce((s, e) => s + e.amount, 0);
    return { date: dateStr, dayNum: d.getDate(), total };
  });

  const maxTotal = Math.max(...days.map((d) => d.total), 1000);

  const getIntensityClass = (amount: number) => {
    if (amount === 0) return 'bg-slate-100 dark:bg-slate-800/80 text-slate-400';
    const ratio = amount / maxTotal;
    if (ratio < 0.25) return 'bg-brand-200 dark:bg-brand-950 text-brand-800 dark:text-brand-300 font-bold';
    if (ratio < 0.5) return 'bg-brand-400 dark:bg-brand-800 text-white font-bold';
    if (ratio < 0.75) return 'bg-brand-600 text-white font-bold';
    return 'bg-indigo-700 text-white font-bold shadow-md shadow-indigo-500/25';
  };

  return (
    <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">Spending Activity Heatmap</h3>
          <p className="text-xs text-slate-500">28-day intensity distribution</p>
        </div>
        <div className="flex items-center space-x-1.5 text-[10px] text-slate-400">
          <span>Less</span>
          <span className="w-2.5 h-2.5 rounded bg-slate-100 dark:bg-slate-800" />
          <span className="w-2.5 h-2.5 rounded bg-brand-300" />
          <span className="w-2.5 h-2.5 rounded bg-brand-500" />
          <span className="w-2.5 h-2.5 rounded bg-indigo-700" />
          <span>More</span>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-2">
        {days.map((d) => (
          <div
            key={d.date}
            title={`${d.date}: ${currencySymbol}${d.total.toLocaleString()}`}
            className={`h-10 rounded-xl flex flex-col items-center justify-center transition-transform hover:scale-105 cursor-pointer text-[11px] ${getIntensityClass(
              d.total
            )}`}
          >
            <span>{d.dayNum}</span>
            {d.total > 0 && (
              <span className="text-[8px] opacity-90 truncate max-w-[90%]">
                {currencySymbol}{d.total > 999 ? `${(d.total / 1000).toFixed(0)}k` : d.total}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
