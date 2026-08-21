import React from 'react';
import { Reminder } from '../../types';
import { CheckCircle2, Circle, Clock, Trash2, Calendar, AlertCircle, RefreshCw } from 'lucide-react';

interface ReminderListProps {
  reminders: Reminder[];
  onToggleComplete: (id: number) => void;
  onDeleteReminder: (id: number) => void;
}

export const ReminderList: React.FC<ReminderListProps> = ({
  reminders,
  onToggleComplete,
  onDeleteReminder,
}) => {
  const getPriorityBadge = (p: string) => {
    if (p === 'high') {
      return (
        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
          High
        </span>
      );
    }
    if (p === 'low') {
      return (
        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
          Low
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
        Medium
      </span>
    );
  };

  if (reminders.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800">
        <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">No Reminders in this view</h4>
        <p className="text-xs text-slate-500 mt-1">
          Say "Remind me to submit assignment tomorrow at 6 PM" or click Add Reminder.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
      {reminders.map((r) => {
        const isCompleted = r.status === 'completed';
        return (
          <div
            key={r.id}
            className={`p-4 rounded-2xl border transition-all flex items-start justify-between gap-3 group ${
              isCompleted
                ? 'bg-slate-50/60 dark:bg-slate-900/40 border-slate-200/60 dark:border-slate-800/60 opacity-60'
                : r.is_overdue
                ? 'bg-rose-500/5 dark:bg-rose-950/20 border-rose-500/30'
                : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800 hover:border-brand-500/40 shadow-sm'
            }`}
          >
            <div className="flex items-start space-x-3">
              <button
                onClick={() => onToggleComplete(r.id)}
                className="mt-0.5 text-slate-400 hover:text-emerald-500 transition-colors"
                title={isCompleted ? 'Completed' : 'Mark as complete'}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                ) : (
                  <Circle className="w-5 h-5" />
                )}
              </button>

              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h4
                    className={`text-xs font-bold ${
                      isCompleted
                        ? 'line-through text-slate-400 dark:text-slate-500'
                        : 'text-slate-900 dark:text-white'
                    }`}
                  >
                    {r.title}
                  </h4>
                  {getPriorityBadge(r.priority)}
                </div>

                {r.description && <p className="text-[11px] text-slate-500">{r.description}</p>}

                <div className="flex items-center space-x-3 text-[10px] text-slate-400 pt-1">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{r.due_date}</span>
                  </span>
                  {r.due_time && (
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{r.due_time}</span>
                    </span>
                  )}
                  {r.recurrence !== 'none' && (
                    <span className="flex items-center space-x-1 font-semibold text-brand-500">
                      <RefreshCw className="w-3 h-3" />
                      <span className="capitalize">{r.recurrence}</span>
                    </span>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={() => onDeleteReminder(r.id)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30 opacity-0 group-hover:opacity-100 transition-opacity"
              title="Delete Reminder"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
