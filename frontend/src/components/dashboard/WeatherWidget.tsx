import React from 'react';
import { CloudRain, Sun, Cloud, Wind, Droplets, Umbrella } from 'lucide-react';
import { WeatherData } from '../../types';

interface WeatherWidgetProps {
  weather?: WeatherData | null;
}

export const WeatherWidget: React.FC<WeatherWidgetProps> = ({ weather }) => {
  if (!weather) {
    return (
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">Local Weather Forecast</h4>
          <p className="text-xs text-slate-500 mt-0.5">Connect to Open-Meteo for live updates</p>
        </div>
        <Cloud className="w-8 h-8 text-slate-300 dark:text-slate-700" />
      </div>
    );
  }

  const isRaining = weather.rain_expected;

  return (
    <div className="p-6 rounded-2xl bg-gradient-to-br from-white to-slate-50/50 dark:from-slate-900 dark:to-slate-950 border border-slate-200/80 dark:border-slate-800 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Live Forecast</span>
          <h4 className="text-base font-bold text-slate-900 dark:text-white mt-0.5">{weather.location}</h4>
        </div>
        <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center">
          {isRaining ? <CloudRain className="w-6 h-6 animate-bounce" /> : <Sun className="w-6 h-6 text-amber-500" />}
        </div>
      </div>

      <div className="flex items-baseline space-x-3 mb-4">
        <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
          {weather.temperature_celsius}°C
        </span>
        <span className="text-xs font-medium text-slate-600 dark:text-slate-300">{weather.conditions}</span>
      </div>

      {/* Rain / Umbrella Advisory Badge */}
      <div
        className={`p-3 rounded-xl text-xs font-medium flex items-center space-x-2.5 ${
          isRaining
            ? 'bg-rose-500/10 border border-rose-500/20 text-rose-700 dark:text-rose-300'
            : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-300'
        }`}
      >
        <Umbrella className="w-4 h-4 flex-shrink-0" />
        <span>
          {isRaining
            ? 'Rain is currently recorded or expected today — carry an umbrella!'
            : 'No rain expected today. Clear weather for outdoor activities.'}
        </span>
      </div>
    </div>
  );
};
