import React from 'react';
import { Sun, Moon, Mic, Plus, Sparkles, Bell } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface HeaderProps {
  title: string;
  subtitle?: string;
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
  openChat: () => void;
  onQuickAddExpense: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  darkMode,
  setDarkMode,
  openChat,
  onQuickAddExpense,
}) => {
  const { user } = useAuth();
  const currencySymbol = user?.currency_pref === 'USD' ? '$' : user?.currency_pref === 'EUR' ? '€' : '₹';

  return (
    <header className="h-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800/80 px-8 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 dark:text-white tracking-tight">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-3">
        {/* Quick Voice Prompt Trigger */}
        <button
          onClick={openChat}
          className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-slate-700/60 text-slate-700 dark:text-slate-300 text-xs font-semibold border border-slate-200 dark:border-slate-700 transition-colors"
          title="Click to speak or chat with FastMCP"
        >
          <Mic className="w-4 h-4 text-brand-600 dark:text-brand-400" />
          <span>Voice Prompt</span>
        </button>

        {/* Quick Add Expense Modal Trigger */}
        <button
          onClick={onQuickAddExpense}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all hover:scale-[1.02]"
        >
          <Plus className="w-4 h-4" />
          <span>Add Expense</span>
        </button>

        <div className="h-6 w-px bg-slate-200 dark:bg-slate-800 mx-1" />

        {/* Dark/Light Mode Toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 rounded-xl text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {darkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5" />}
        </button>
      </div>
    </header>
  );
};
