import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { Expense } from '../../types';

interface DailySpendingBarChartProps {
  expenses: Expense[];
  currencySymbol?: string;
}

export const DailySpendingBarChart: React.FC<DailySpendingBarChartProps> = ({
  expenses,
  currencySymbol = '₹',
}) => {
  // Aggregate expenses for the past 7 calendar days
  const today = new Date();
  const past7Days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() - (6 - i));
    return d.toISOString().split('T')[0];
  });

  const chartData = past7Days.map((dateStr) => {
    const dayExpenses = expenses.filter((e) => e.date === dateStr);
    const total = dayExpenses.reduce((sum, e) => sum + e.amount, 0);
    const dayName = new Date(dateStr).toLocaleDateString([], { weekday: 'short' });
    return {
      date: dayName,
      fullDate: dateStr,
      amount: total,
    };
  });

  return (
    <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">Daily Spending Activity</h3>
          <p className="text-xs text-slate-500">Expenses recorded per day over the past week</p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(148, 163, 184, 0.15)" />
            <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <Tooltip
              formatter={(value: any) => [`${currencySymbol}${Number(value).toLocaleString()}`, 'Spent']}
              labelFormatter={(_, payload) => payload?.[0]?.payload?.fullDate || ''}
              contentStyle={{
                backgroundColor: '#1e293b',
                border: 'none',
                borderRadius: '0.75rem',
                color: '#fff',
                fontSize: '12px',
              }}
            />
            <Bar dataKey="amount" fill="#6366f1" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
