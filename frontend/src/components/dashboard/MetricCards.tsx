import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Wallet, Calendar, ShieldAlert } from 'lucide-react';
import { WeeklyComparison, Budget } from '../../types';

interface MetricCardsProps {
  weeklyData?: WeeklyComparison | null;
  budgets?: Budget[];
  todaySpent?: number;
  monthlySpent?: number;
  currencySymbol?: string;
}

export const MetricCards: React.FC<MetricCardsProps> = ({
  weeklyData,
  budgets = [],
  todaySpent = 0,
  monthlySpent = 0,
  currencySymbol = '₹',
}) => {
  const currentWeekTotal = weeklyData?.current_week?.total || 0;
  const previousWeekTotal = weeklyData?.previous_week?.total || 0;
  const changePercent = weeklyData?.change_percent;

  const isIncrease = (changePercent || 0) > 0;
  const overallBudget = budgets.find((b) => !b.category) || budgets[0];
  const budgetRemaining = overallBudget?.remaining ?? (overallBudget ? overallBudget.amount - monthlySpent : 0);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {/* 1. This Week's Spending */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden group hover:border-brand-500/40 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">This Week's Spending</span>
          <div className="w-8 h-8 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center">
            <DollarSign className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            {currencySymbol}{currentWeekTotal.toLocaleString()}
          </span>
          {changePercent !== null && changePercent !== undefined && (
            <span
              className={`inline-flex items-center text-xs font-bold px-2 py-0.5 rounded-full ${
                isIncrease
                  ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400'
                  : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
              }`}
            >
              {isIncrease ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
              {Math.abs(changePercent).toFixed(1)}%
            </span>
          )}
        </div>
        <p className="mt-2 text-[11px] text-slate-400">
          Prev week: {currencySymbol}{previousWeekTotal.toLocaleString()}
        </p>
      </div>

      {/* 2. Today's Spending */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden group hover:border-brand-500/40 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Today's Spending</span>
          <div className="w-8 h-8 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center">
            <Calendar className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            {currencySymbol}{todaySpent.toLocaleString()}
          </span>
          <span className="text-xs font-medium text-slate-400">Recorded today</span>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">Updated in real-time</p>
      </div>

      {/* 3. Monthly Total */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden group hover:border-brand-500/40 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Monthly Spending</span>
          <div className="w-8 h-8 rounded-xl bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center">
            <Wallet className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
            {currencySymbol}{monthlySpent.toLocaleString()}
          </span>
          <span className="text-xs font-medium text-slate-400">This month</span>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">Calendar month total</p>
      </div>

      {/* 4. Budget Remaining */}
      <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm relative overflow-hidden group hover:border-brand-500/40 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Remaining Budget</span>
          <div
            className={`w-8 h-8 rounded-xl flex items-center justify-center ${
              budgetRemaining < 0
                ? 'bg-rose-50 dark:bg-rose-950/60 text-rose-600'
                : 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span
            className={`text-2xl font-black tracking-tight ${
              budgetRemaining < 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-900 dark:text-white'
            }`}
          >
            {currencySymbol}{Math.max(0, budgetRemaining).toLocaleString()}
          </span>
          <span
            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              budgetRemaining < 0
                ? 'bg-rose-500/10 text-rose-600'
                : 'bg-emerald-500/10 text-emerald-600'
            }`}
          >
            {overallBudget ? `${overallBudget.percentage_used || 0}% used` : 'No budget set'}
          </span>
        </div>
        <p className="mt-2 text-[11px] text-slate-400">
          {overallBudget ? `Monthly cap: ${currencySymbol}${overallBudget.amount}` : 'Set a budget to track limits'}
        </p>
      </div>
    </div>
  );
};
