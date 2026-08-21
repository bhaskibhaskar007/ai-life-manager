import React, { useEffect, useState } from 'react';
import {
  Calendar,
  Clock,
  CloudSun,
  ShieldCheck,
  Sparkles,
  Umbrella,
  CheckCircle,
  RefreshCw,
} from 'lucide-react';
import { api } from '../../services/api';
import { DayPlan } from '../../types';

interface DayPlanViewProps {
  currencySymbol?: string;
}

export const DayPlanView: React.FC<DayPlanViewProps> = ({ currencySymbol = '₹' }) => {
  const [plan, setPlan] = useState<DayPlan | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [city, setCity] = useState('Bengaluru');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDayPlan(selectedDate, city);
      setPlan(data);
    } catch (err: any) {
      setError(err.message || 'Failed to generate day plan');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, [selectedDate, city]);

  return (
    <div className="space-y-6">
      {/* Header controls */}
      <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">AI Context-Aware Day Planner</h3>
            <p className="text-xs text-slate-500">
              Harmonizes active reminders, weather forecasts, and daily safe spend limits
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-xs font-semibold text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500"
          />
          <input
            type="text"
            placeholder="City"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-32 px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-xs font-semibold text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500"
          />
          <button
            onClick={fetchPlan}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 text-slate-600 dark:text-slate-300 transition-colors"
            title="Refresh Plan"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-center space-x-2 text-slate-500 text-xs">
          <RefreshCw className="w-4 h-4 animate-spin text-brand-600" />
          <span>Generating verified daily schedule...</span>
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs font-semibold">
          {error}
        </div>
      ) : plan ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Schedule Column (2/3) */}
          <div className="lg:col-span-2 space-y-5">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">Structured Daily Schedule</h4>

            <div className="space-y-4">
              {plan.schedule_blocks.map((block, idx) => (
                <div
                  key={idx}
                  className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm"
                >
                  <div className="flex items-center space-x-2 mb-3">
                    <Clock className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                    <h5 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                      {block.period}
                    </h5>
                  </div>

                  <div className="space-y-2">
                    {block.items.map((item, itemIdx) => (
                      <div
                        key={itemIdx}
                        className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center space-x-3">
                          {item.time && (
                            <span className="font-mono font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/60 px-2 py-0.5 rounded">
                              {item.time}
                            </span>
                          )}
                          <span className="font-semibold text-slate-800 dark:text-slate-200">{item.title}</span>
                        </div>
                        {item.priority && (
                          <span className="text-[10px] uppercase font-bold text-slate-400">{item.priority}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Context Advisory Sidebar (1/3) */}
          <div className="space-y-5">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">Context & Advisory</h4>

            {/* Weather Card */}
            {plan.weather && (
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 dark:text-white">Weather Forecast</span>
                  <CloudSun className="w-4 h-4 text-amber-500" />
                </div>
                <div className="text-2xl font-black text-slate-900 dark:text-white">
                  {plan.weather.temperature_celsius}°C
                </div>
                <p className="text-xs text-slate-500">{plan.weather.conditions}</p>
                <div
                  className={`p-2.5 rounded-xl text-[11px] font-medium flex items-center space-x-2 ${
                    plan.weather.rain_expected
                      ? 'bg-rose-500/10 text-rose-700 dark:text-rose-300'
                      : 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
                  }`}
                >
                  <Umbrella className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>
                    {plan.weather.rain_expected
                      ? 'Precipitation expected — remember your umbrella.'
                      : 'Clear outdoor conditions expected.'}
                  </span>
                </div>
              </div>
            )}

            {/* Safe Spending Guideline */}
            {plan.safe_spend_guidance ? (
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 dark:text-white">Safe Daily Spending</span>
                  <ShieldCheck className="w-4 h-4 text-emerald-500" />
                </div>
                <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                  {currencySymbol}{plan.safe_spend_guidance.recommended_daily_limit}
                  <span className="text-xs font-normal text-slate-400 ml-1">/ day</span>
                </div>
                <p className="text-xs text-slate-500">
                  Calculated from {currencySymbol}{plan.safe_spend_guidance.remaining_budget} remaining budget across{' '}
                  {plan.safe_spend_guidance.days_remaining_in_month} days.
                </p>
              </div>
            ) : (
              <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm text-xs text-slate-500">
                Set a monthly budget to unlock automated safe daily spending recommendations.
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
