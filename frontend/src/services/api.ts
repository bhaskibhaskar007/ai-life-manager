import {
  AuthTokens,
  Budget,
  Category,
  CategoryBreakdownItem,
  DayPlan,
  Expense,
  FinancialInsight,
  Reminder,
  User,
  WeeklyComparison,
} from '../types';

const viteEnv = (import.meta as unknown as { env?: Record<string, string> })?.env;
const rawBase = viteEnv?.VITE_API_URL || '';
const API_BASE = (rawBase ? rawBase.replace(/\/$/, '') : '') + '/api/v1';

class ApiService {
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...(options.headers || {}),
      },
    });

    if (res.status === 204) {
      return {} as T;
    }

    const data = await res.json();
    if (!res.ok) {
      if (res.status === 401 && !endpoint.startsWith('/auth/login')) {
        // Clear expired token
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
      throw new Error(data.detail || 'API request failed');
    }
    return data as T;
  }

  // --- Auth ---
  async register(payload: { email: string; password: string; full_name?: string; currency_pref?: string }): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async login(payload: { email: string; password: string }): Promise<AuthTokens> {
    return this.request<AuthTokens>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // --- Expenses ---
  async getExpenses(params: { category?: string; start_date?: string; end_date?: string; limit?: number } = {}): Promise<Expense[]> {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.start_date) query.append('start_date', params.start_date);
    if (params.end_date) query.append('end_date', params.end_date);
    if (params.limit) query.append('limit', String(params.limit));
    return this.request<Expense[]>(`/expenses?${query.toString()}`);
  }

  async createExpense(payload: {
    amount: number;
    category: string;
    description?: string;
    date?: string;
    payment_method?: string;
    notes?: string;
  }): Promise<Expense> {
    return this.request<Expense>('/expenses', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async deleteExpense(id: number): Promise<void> {
    return this.request<void>(`/expenses/${id}`, { method: 'DELETE' });
  }

  async getCategories(): Promise<Category[]> {
    return this.request<Category[]>('/expenses/categories');
  }

  // --- Reminders ---
  async getReminders(when: string = 'all', status?: string): Promise<Reminder[]> {
    const query = new URLSearchParams({ when });
    if (status) query.append('status', status);
    return this.request<Reminder[]>(`/reminders?${query.toString()}`);
  }

  async createReminder(payload: {
    title: string;
    due_date: string;
    due_time?: string;
    description?: string;
    priority?: string;
    recurrence?: string;
  }): Promise<Reminder> {
    return this.request<Reminder>('/reminders', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async completeReminder(id: number): Promise<{ completed: Reminder; next_occurrence?: Reminder | null }> {
    return this.request(`/reminders/${id}/complete`, { method: 'POST' });
  }

  async deleteReminder(id: number): Promise<void> {
    return this.request<void>(`/reminders/${id}`, { method: 'DELETE' });
  }

  // --- Budgets ---
  async getBudgets(): Promise<Budget[]> {
    return this.request<Budget[]>('/budgets');
  }

  async upsertBudget(payload: { amount: number; category?: string; period?: string }): Promise<Budget> {
    return this.request<Budget>('/budgets', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- Analytics ---
  async getWeeklyComparison(): Promise<WeeklyComparison> {
    return this.request<WeeklyComparison>('/analytics/comparison');
  }

  async getCategoryBreakdown(): Promise<{ breakdown: CategoryBreakdownItem[]; top_category: string | null; total_spent: number }> {
    return this.request('/analytics/breakdown');
  }

  async getFinancialInsights(): Promise<FinancialInsight> {
    return this.request<FinancialInsight>('/analytics/insights');
  }

  async getSpendingTrend(weeks: number = 6): Promise<{ weekly_totals: Array<{ week_start: string; total: number }>; trend: string }> {
    return this.request(`/analytics/trend?weeks=${weeks}`);
  }

  // --- Planner ---
  async getDayPlan(dateStr?: string, location: string = 'Bengaluru'): Promise<DayPlan> {
    const query = new URLSearchParams({ location });
    if (dateStr) query.append('date', dateStr);
    return this.request<DayPlan>(`/planner/day?${query.toString()}`);
  }

  // --- Preferences ---
  async getPreferences(): Promise<Array<{ key: string; value: string }>> {
    return this.request<Array<{ key: string; value: string }>>('/preferences');
  }

  async savePreference(key: string, value: string): Promise<{ key: string; value: string }> {
    return this.request('/preferences', {
      method: 'POST',
      body: JSON.stringify({ key, value }),
    });
  }

  // --- Chat ---
  async sendChatMessage(message: string, conversationHistory?: any[]): Promise<{
    response: string;
    used_fallback: boolean;
    tools_called: string[];
  }> {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_history: conversationHistory }),
    });
  }
}

export const api = new ApiService();
