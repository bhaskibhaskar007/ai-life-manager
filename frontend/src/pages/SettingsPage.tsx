import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Settings, Save, CheckCircle, Shield, Globe, Bell, Mic } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [currency, setCurrency] = useState(user?.currency_pref || 'INR');
  const [reminderStyle, setReminderStyle] = useState('detailed');
  const [voiceEnabled, setVoiceEnabled] = useState('true');
  const [notificationStyle, setNotificationStyle] = useState('push');
  const [timezone, setTimezone] = useState('Asia/Kolkata');
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const prefs = await api.getPreferences();
        prefs.forEach((p) => {
          if (p.key === 'currency') setCurrency(p.value);
          if (p.key === 'reminder_style') setReminderStyle(p.value);
          if (p.key === 'voice_response_enabled') setVoiceEnabled(p.value);
          if (p.key === 'notification_style') setNotificationStyle(p.value);
          if (p.key === 'timezone') setTimezone(p.value);
        });
      } catch {
        // Ignore
      }
    };
    loadPreferences();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);
    try {
      await Promise.all([
        api.savePreference('currency', currency),
        api.savePreference('reminder_style', reminderStyle),
        api.savePreference('voice_response_enabled', voiceEnabled),
        api.savePreference('notification_style', notificationStyle),
        api.savePreference('timezone', timezone),
      ]);
      await refreshUser();
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch {
      // Ignore
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h3 className="text-base font-bold text-slate-900 dark:text-white">User Preferences & Configuration</h3>
        <p className="text-xs text-slate-500">
          Personalize currency, voice interaction, and reminder behavior stored in FastMCP memory
        </p>
      </div>

      <form onSubmit={handleSave} className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 p-6 space-y-6 shadow-sm">
        {savedSuccess && (
          <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-300 text-xs font-semibold flex items-center space-x-2">
            <CheckCircle className="w-4 h-4" />
            <span>Preferences successfully updated and synchronized across all FastMCP tools!</span>
          </div>
        )}

        {/* Currency setting */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-2">
            <Globe className="w-4 h-4 text-brand-600 dark:text-brand-400" />
            <span>Preferred Currency Symbol</span>
          </label>
          <p className="text-[11px] text-slate-500">
            Selected currency code used for expense calculations and dashboard visualization.
          </p>
          <select
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-slate-900 dark:text-white text-xs font-semibold focus:ring-2 focus:ring-brand-500"
          >
            <option value="INR">INR (₹ — Indian Rupee)</option>
            <option value="USD">USD ($ — US Dollar)</option>
            <option value="EUR">EUR (€ — Euro)</option>
            <option value="GBP">GBP (£ — British Pound)</option>
          </select>
        </div>

        {/* Voice Response preference */}
        <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
          <label className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-2">
            <Mic className="w-4 h-4 text-brand-600 dark:text-brand-400" />
            <span>Voice Spoken Responses (Text-to-Speech)</span>
          </label>
          <p className="text-[11px] text-slate-500">
            When enabled, the assistant speaks answers aloud via browser speech synthesis.
          </p>
          <select
            value={voiceEnabled}
            onChange={(e) => setVoiceEnabled(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-slate-900 dark:text-white text-xs font-semibold focus:ring-2 focus:ring-brand-500"
          >
            <option value="true">Enabled (Speak aloud)</option>
            <option value="false">Disabled (Text only)</option>
          </select>
        </div>

        {/* Reminder Style preference */}
        <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
          <label className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-2">
            <Bell className="w-4 h-4 text-brand-600 dark:text-brand-400" />
            <span>Reminder Phrasing Style</span>
          </label>
          <p className="text-[11px] text-slate-500">
            Controls the brevity of AI generated reminder summaries.
          </p>
          <select
            value={reminderStyle}
            onChange={(e) => setReminderStyle(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 border-none text-slate-900 dark:text-white text-xs font-semibold focus:ring-2 focus:ring-brand-500"
          >
            <option value="detailed">Detailed (Includes priority, tags, and context)</option>
            <option value="brief">Brief (Concise title only)</option>
          </select>
        </div>

        {/* Security & Memory note */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800 flex items-start space-x-3 text-xs text-slate-600 dark:text-slate-400">
          <Shield className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-semibold text-slate-800 dark:text-slate-200">Security Architecture Guarantee:</span>{' '}
            Sensitive credentials and passwords are never stored in FastMCP memory. User preferences are validated against an allow-list schema before persisting.
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition-all hover:scale-[1.02] disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Preferences'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
