import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Expense } from '../types';
import { ExpenseTable } from '../components/expenses/ExpenseTable';
import { AddExpenseModal } from '../components/expenses/AddExpenseModal';
import { Plus, RefreshCw } from 'lucide-react';

interface ExpensesPageProps {
  isAddModalOpen: boolean;
  setIsAddModalOpen: (val: boolean) => void;
  currencySymbol?: string;
}

export const ExpensesPage: React.FC<ExpensesPageProps> = ({
  isAddModalOpen,
  setIsAddModalOpen,
  currencySymbol = '₹',
}) => {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      const data = await api.getExpenses({ limit: 100 });
      setExpenses(data);
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  const handleDeleteExpense = async (id: number) => {
    try {
      await api.deleteExpense(id);
      fetchExpenses();
    } catch {
      // Ignore
    }
  };

  const totalSpent = expenses.reduce((sum, e) => sum + e.amount, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">Recorded Expenses</h3>
          <p className="text-xs text-slate-500">
            Total of {expenses.length} transaction(s) amounting to{' '}
            <span className="font-bold text-brand-600 dark:text-brand-400">
              {currencySymbol}{totalSpent.toLocaleString()}
            </span>
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={fetchExpenses}
            className="p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all hover:scale-[1.02]"
          >
            <Plus className="w-4 h-4" />
            <span>Add Expense</span>
          </button>
        </div>
      </div>

      <ExpenseTable
        expenses={expenses}
        onDeleteExpense={handleDeleteExpense}
        currencySymbol={currencySymbol}
      />

      <AddExpenseModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onExpenseAdded={fetchExpenses}
        currencySymbol={currencySymbol}
      />
    </div>
  );
};
