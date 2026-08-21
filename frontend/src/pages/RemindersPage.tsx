import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Reminder } from '../types';
import { ReminderList } from '../components/reminders/ReminderList';
import { AddReminderModal } from '../components/reminders/AddReminderModal';
import { Plus, RefreshCw, Filter } from 'lucide-react';

export const RemindersPage: React.FC = () => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [activeFilter, setActiveFilter] = useState<'all' | 'today' | 'upcoming' | 'overdue'>('all');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchReminders = async () => {
    setLoading(true);
    try {
      const data = await api.getReminders(activeFilter);
      setReminders(data);
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReminders();
  }, [activeFilter]);

  const handleToggleComplete = async (id: number) => {
    try {
      await api.completeReminder(id);
      fetchReminders();
    } catch {
      // Ignore
    }
  };

  const handleDeleteReminder = async (id: number) => {
    try {
      await api.deleteReminder(id);
      fetchReminders();
    } catch {
      // Ignore
    }
  };

  const tabs: Array<{ id: 'all' | 'today' | 'upcoming' | 'overdue'; label: string }> = [
    { id: 'all', label: 'All Reminders' },
    { id: 'today', label: 'Due Today' },
    { id: 'upcoming', label: 'Upcoming' },
    { id: 'overdue', label: 'Overdue' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">Reminders & Tasks</h3>
          <p className="text-xs text-slate-500">
            Intelligent task scheduler parsed from natural language by FastMCP
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={fetchReminders}
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
            <span>Add Reminder</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-1 p-1 rounded-xl bg-slate-200/60 dark:bg-slate-800/60 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveFilter(tab.id)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeFilter === tab.id
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <ReminderList
        reminders={reminders}
        onToggleComplete={handleToggleComplete}
        onDeleteReminder={handleDeleteReminder}
      />

      <AddReminderModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onReminderAdded={fetchReminders}
      />
    </div>
  );
};
