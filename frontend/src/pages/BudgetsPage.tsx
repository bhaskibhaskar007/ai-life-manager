import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Budget } from '../types';
import { BudgetList } from '../components/budgets/BudgetList';
import { AddBudgetModal } from '../components/budgets/AddBudgetModal';

interface BudgetsPageProps {
  currencySymbol?: string;
}

export const BudgetsPage: React.FC<BudgetsPageProps> = ({ currencySymbol = '₹' }) => {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchBudgets = async () => {
    setLoading(true);
    try {
      const data = await api.getBudgets();
      setBudgets(data);
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgets();
  }, []);

  return (
    <div className="space-y-6">
      <BudgetList
        budgets={budgets}
        onOpenAddModal={() => setIsAddModalOpen(true)}
        currencySymbol={currencySymbol}
      />

      <AddBudgetModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onBudgetSaved={fetchBudgets}
        currencySymbol={currencySymbol}
      />
    </div>
  );
};
