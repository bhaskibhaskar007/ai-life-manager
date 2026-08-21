import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { AIAssistantDrawer } from './components/chat/AIAssistantDrawer';
import { DashboardPage } from './pages/DashboardPage';
import { ExpensesPage } from './pages/ExpensesPage';
import { RemindersPage } from './pages/RemindersPage';
import { BudgetsPage } from './pages/BudgetsPage';
import { PlannerPage } from './pages/PlannerPage';
import { SettingsPage } from './pages/SettingsPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { AddExpenseModal } from './components/expenses/AddExpenseModal';
import { Bot } from 'lucide-react';

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isAddExpenseModalOpen, setIsAddExpenseModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('theme') === 'dark' || window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  const currencySymbol = user?.currency_pref === 'USD' ? '$' : user?.currency_pref === 'EUR' ? '€' : '₹';

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center text-slate-500 text-sm">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <span className="font-semibold text-xs text-slate-600 dark:text-slate-400">Loading AI Life Manager...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return authView === 'login' ? (
      <LoginPage onSwitchToRegister={() => setAuthView('register')} />
    ) : (
      <RegisterPage onSwitchToLogin={() => setAuthView('login')} />
    );
  }

  const tabTitles: Record<string, { title: string; subtitle: string }> = {
    dashboard: {
      title: 'Financial & Productivity Overview',
      subtitle: 'Real-time metrics, predictive spending trends, and active context',
    },
    expenses: {
      title: 'Expense Management',
      subtitle: 'Audit, search, and categorize all personal transactions',
    },
    reminders: {
      title: 'Reminders & Tasks',
      subtitle: 'FastMCP scheduled priority reminders and deadlines',
    },
    budgets: {
      title: 'Budget Controls',
      subtitle: 'Category-specific spending limits with automated overspending alerts',
    },
    planner: {
      title: 'AI Context-Aware Day Planner',
      subtitle: 'Structured schedules synthesizing active tasks, weather forecasts, and safe spending limits',
    },
    settings: {
      title: 'Settings & Preferences',
      subtitle: 'Customize currency format, voice response behavior, and persistent preferences',
    },
  };

  const currentHeaderInfo = tabTitles[currentTab] || {
    title: 'AI Life Manager',
    subtitle: 'FastMCP Personal Assistant',
  };

  const handleDataChanged = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        openChat={() => setIsChatOpen(true)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header
          title={currentHeaderInfo.title}
          subtitle={currentHeaderInfo.subtitle}
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          openChat={() => setIsChatOpen(true)}
          onQuickAddExpense={() => setIsAddExpenseModalOpen(true)}
        />

        <main className="flex-1 overflow-y-auto p-8 bg-slate-50/60 dark:bg-slate-950/60">
          <div className="max-w-7xl mx-auto pb-12" key={refreshKey}>
            {currentTab === 'dashboard' && (
              <DashboardPage
                onOpenAddExpense={() => setIsAddExpenseModalOpen(true)}
                currencySymbol={currencySymbol}
              />
            )}
            {currentTab === 'expenses' && (
              <ExpensesPage
                isAddModalOpen={isAddExpenseModalOpen}
                setIsAddModalOpen={setIsAddExpenseModalOpen}
                currencySymbol={currencySymbol}
              />
            )}
            {currentTab === 'reminders' && <RemindersPage />}
            {currentTab === 'budgets' && <BudgetsPage currencySymbol={currencySymbol} />}
            {currentTab === 'planner' && <PlannerPage currencySymbol={currencySymbol} />}
            {currentTab === 'settings' && <SettingsPage />}
          </div>
        </main>
      </div>

      {/* Floating Action Button for AI Assistant */}
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 p-4 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white shadow-2xl shadow-brand-500/40 hover:scale-105 active:scale-95 transition-transform flex items-center justify-center z-40 group"
        title="Open AI Life Assistant"
      >
        <Bot className="w-6 h-6 group-hover:animate-bounce" />
        <span className="max-w-0 overflow-hidden whitespace-nowrap group-hover:max-w-xs transition-all duration-300 ease-in-out font-bold text-xs pl-0 group-hover:pl-2">
          Chat / Voice Assistant
        </span>
      </button>

      {/* AI Assistant Drawer */}
      <AIAssistantDrawer
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        onDataChanged={handleDataChanged}
      />

      {/* Quick Add Expense Modal */}
      <AddExpenseModal
        isOpen={isAddExpenseModalOpen}
        onClose={() => setIsAddExpenseModalOpen(false)}
        onExpenseAdded={handleDataChanged}
        currencySymbol={currencySymbol}
      />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
