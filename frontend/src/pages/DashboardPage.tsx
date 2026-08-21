import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import {
  Expense,
  Reminder,
  Budget,
  WeeklyComparison,
  CategoryBreakdownItem,
  FinancialInsight,
  WeatherData,
} from '../types';
import { MetricCards } from '../components/dashboard/MetricCards';
import { WeeklySpendingChart } from '../components/dashboard/WeeklySpendingChart';
import { CategoryBreakdownChart } from '../components/dashboard/CategoryBreakdownChart';
import { DailySpendingBarChart } from '../components/dashboard/DailySpendingBarChart';
import { BudgetProgressMeter } from '../components/dashboard/BudgetProgressMeter';
import { SpendingHeatmap } from '../components/dashboard/SpendingHeatmap';
import { FinancialInsightBanner } from '../components/dashboard/FinancialInsightBanner';
import { WeatherWidget } from '../components/dashboard/WeatherWidget';
import { ReminderList } from '../components/reminders/ReminderList';
import { Plus, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface DashboardPageProps {
  onOpenAddExpense: () => void;
  currencySymbol?: string;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onOpenAddExpense,
  currencySymbol = '₹',
}) => {
  const { user } = useAuth();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [weeklyComparison, setWeeklyComparison] = useState<WeeklyComparison | null>(null);
  const [breakdown, setBreakdown] = useState<CategoryBreakdownItem[]>([]);
  const [insight, setInsight] = useState<FinancialInsight | null>(null);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [
        expList,
        remList,
        bList,
        weeklyComp,
        catBreakdown,
        insightsData,
      ] = await Promise.allSettled([
        api.getExpenses({ limit: 50 }),
        api.getReminders('today'),
        api.getBudgets(),
        api.getWeeklyComparison(),
        api.getCategoryBreakdown(),
        api.getFinancialInsights(),
      ]);

      if (expList.status === 'fulfilled') setExpenses(expList.value);
      if (remList.status === 'fulfilled') setReminders(remList.value);
      if (bList.status === 'fulfilled') setBudgets(bList.value);
      if (weeklyComp.status === 'fulfilled') setWeeklyComparison(weeklyComp.value);
      if (catBreakdown.status === 'fulfilled') setBreakdown(catBreakdown.value.breakdown);
      if (insightsData.status === 'fulfilled') setInsight(insightsData.value);

      // Attempt to load weather
      try {
        const plan = await api.getDayPlan();
        if (plan.weather) setWeather(plan.weather);
      } catch {
        // Ignore weather fallback
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const todayStr = new Date().toISOString().split('T')[0];
  const todaySpent = expenses
    .filter((e) => e.date === todayStr)
    .reduce((sum, e) => sum + e.amount, 0);

  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  const monthlySpent = expenses
    .filter((e) => {
      const d = new Date(e.date);
      return d.getMonth() === currentMonth && d.getFullYear() === currentYear;
    })
    .reduce((sum, e) => sum + e.amount, 0);

  const handleToggleReminder = async (id: number) => {
    try {
      await api.completeReminder(id);
      loadDashboardData();
    } catch {
      // Ignore
    }
  };

  const handleDeleteReminder = async (id: number) => {
    try {
      await api.deleteReminder(id);
      loadDashboardData();
    } catch {
      // Ignore
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Metric Cards */}
      <MetricCards
        weeklyData={weeklyComparison}
        budgets={budgets}
        todaySpent={todaySpent}
        monthlySpent={monthlySpent}
        currencySymbol={currencySymbol}
      />

      {/* AI Financial Insights Banner */}
      <FinancialInsightBanner insight={insight} currencySymbol={currencySymbol} />

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <WeeklySpendingChart expenses={expenses} currencySymbol={currencySymbol} />
        </div>
        <div>
          <CategoryBreakdownChart data={breakdown} currencySymbol={currencySymbol} />
        </div>
      </div>

      {/* Secondary Row: Daily Activity & Budget Utilization */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <DailySpendingBarChart expenses={expenses} currencySymbol={currencySymbol} />
        </div>
        <div className="space-y-6">
          <WeatherWidget weather={weather} />
          <BudgetProgressMeter budgets={budgets} currencySymbol={currencySymbol} />
        </div>
      </div>

      {/* Heatmap & Today's Reminders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SpendingHeatmap expenses={expenses} currencySymbol={currencySymbol} />

        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Today's Priority Reminders</h3>
              <p className="text-xs text-slate-500">Scheduled deadlines for today</p>
            </div>
            <button
              onClick={loadDashboardData}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
              title="Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <ReminderList
            reminders={reminders.slice(0, 4)}
            onToggleComplete={handleToggleReminder}
            onDeleteReminder={handleDeleteReminder}
          />
        </div>
      </div>
    </div>
  );
};
