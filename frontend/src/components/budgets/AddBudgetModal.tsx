import React, { useState } from 'react';
import { X, Plus, PiggyBank } from 'lucide-react';
import { api } from '../../services/api';

interface AddBudgetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onBudgetSaved: () => void;
  currencySymbol?: string;
}

export const AddBudgetModal: React.FC<AddBudgetModalProps> = ({
  isOpen,
  onClose,
  onBudgetSaved,
  currencySymbol = '₹',
}) => {
  const [amount, setAmount] = useState('');
  const [scope, setScope] = useState<'overall' | 'category'>('overall');
  const [category, setCategory] = useState('Food');
  const [period, setPeriod] = useState('monthly');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const categories = [
    'Food',
    'Transportation',
    'Shopping',
    'Education',
    'Entertainment',
    'Bills',
    'Healthcare',
    'Travel',
    'Subscriptions',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      setError('Please enter a valid positive budget amount.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await api.upsertBudget({
        amount: numAmount,
        category: scope === 'category' ? category : undefined,
        period,
      });
      onBudgetSaved();
      onClose();
      setAmount('');
    } catch (err: any) {
      setError(err.message || 'Failed to save budget');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <PiggyBank className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Configure Budget Limit</h3>
              <p className="text-xs text-slate-500">Automated spending risk monitoring</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs font-semibold">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Budget Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setScope('overall')}
                className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                  scope === 'overall'
                    ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-transparent hover:bg-slate-200'
                }`}
              >
                Overall Monthly Limit
              </button>
              <button
                type="button"
                onClick={() => setScope('category')}
                className={`py-2 px-3 rounded-xl text-xs font-semibold border transition-all ${
                  scope === 'category'
                    ? 'bg-brand-600 text-white border-brand-600 shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-transparent hover:bg-slate-200'
                }`}
              >
                Category Limit
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
              Target Spending Limit ({currencySymbol}) *
            </label>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-sm">
                {currencySymbol}
              </span>
              <input
                type="number"
                step="1"
                required
                placeholder="5000"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full pl-8 pr-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-slate-900 dark:text-white text-sm font-semibold focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>
          </div>

          {scope === 'category' && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-slate-900 dark:text-white text-xs font-medium focus:ring-2 focus:ring-brand-500"
              >
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Period</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-slate-900 dark:text-white text-xs font-medium focus:ring-2 focus:ring-brand-500 capitalize"
            >
              <option value="monthly">Monthly (Resets on 1st of month)</option>
              <option value="weekly">Weekly (Monday - Sunday)</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          <div className="pt-3 flex items-center justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-1.5 px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all hover:scale-[1.02] disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              <span>{loading ? 'Saving...' : 'Set Budget'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
