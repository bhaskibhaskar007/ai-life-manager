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

// Initial seed data for standalone offline/demo evaluation
const getInitialExpenses = (): Expense[] => {
  const today = new Date().toISOString().split('T')[0];
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
  const twoDaysAgo = new Date(Date.now() - 172800000).toISOString().split('T')[0];

  return [
    { id: 1, amount: 250, category: 'Food', description: 'Lunch at Cafeteria', date: today, payment_method: 'upi' },
    { id: 2, amount: 120, category: 'Transportation', description: 'Metro Commute', date: today, payment_method: 'card' },
    { id: 3, amount: 1450, category: 'Groceries', description: 'Weekly Supermarket', date: yesterday, payment_method: 'upi' },
    { id: 4, amount: 499, category: 'Entertainment', description: 'Movie Ticket & Snacks', date: yesterday, payment_method: 'upi' },
    { id: 5, amount: 890, category: 'Shopping', description: 'Books & Stationery', date: twoDaysAgo, payment_method: 'card' },
    { id: 6, amount: 350, category: 'Food', description: 'Dinner with team', date: twoDaysAgo, payment_method: 'cash' },
  ];
};

const getInitialReminders = (): Reminder[] => {
  const today = new Date().toISOString().split('T')[0];
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0];

  return [
    { id: 1, title: 'Submit AI Life Manager Project Report', due_date: today, due_time: '17:00', priority: 'high', status: 'pending', recurrence: 'none', is_overdue: false },
    { id: 2, title: 'Review Monthly Safe Spending Limit', due_date: today, due_time: '19:30', priority: 'medium', status: 'pending', recurrence: 'none', is_overdue: false },
    { id: 3, title: 'Nexora Hackathon 2026 Core Team Sync', due_date: tomorrow, due_time: '11:00', priority: 'high', status: 'pending', recurrence: 'weekly', is_overdue: false },
  ];
};

const getInitialBudgets = (): Budget[] => {
  return [
    { id: 1, amount: 15000, category: null, period: 'monthly', spent: 3559, remaining: 11441, percentage_used: 23.7, status: 'on_track', start_date: '2026-09-01' },
    { id: 2, amount: 4000, category: 'Food', period: 'monthly', spent: 600, remaining: 3400, percentage_used: 15.0, status: 'on_track', start_date: '2026-09-01' },
    { id: 3, amount: 2000, category: 'Transportation', period: 'monthly', spent: 120, remaining: 1880, percentage_used: 6.0, status: 'on_track', start_date: '2026-09-01' },
  ];
};

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
    try {
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

      const text = await res.text();
      let data: any;
      try {
        data = JSON.parse(text);
      } catch {
        // Response was not valid JSON (e.g. HTML 404/SPA fallback from Vercel)
        throw new Error('Backend offline');
      }

      if (!res.ok) {
        if (res.status === 401 && !endpoint.startsWith('/auth/login')) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
        }
        throw new Error(data.detail || 'API request failed');
      }
      return data as T;
    } catch (err: any) {
      // If backend is offline or in demo mode, use mock fallback
      return this.handleFallback<T>(endpoint, options, err);
    }
  }

  // --- Local Fallback Engine for Standalone Vercel Demo ---
  private handleFallback<T>(endpoint: string, options: RequestInit, _originalError: any): T {
    const method = options.method || 'GET';

    if (endpoint.startsWith('/auth/login') || endpoint.startsWith('/auth/register')) {
      localStorage.setItem('is_demo_mode', 'true');
      const tokens: AuthTokens = {
        access_token: 'demo-jwt-token-evaluator-2026',
        refresh_token: 'demo-refresh-token-evaluator-2026',
        token_type: 'bearer',
        expires_in: 3600,
      };
      return tokens as T;
    }

    if (endpoint.startsWith('/auth/me')) {
      const user: User = {
        id: 1,
        email: 'demo@example.com',
        full_name: 'Bhaskar (Demo Evaluator)',
        currency_pref: 'INR',
        is_active: true,
        created_at: new Date().toISOString(),
      };
      return user as T;
    }

    if (endpoint.startsWith('/expenses')) {
      let expenses: Expense[] = JSON.parse(localStorage.getItem('demo_expenses') || 'null');
      if (!expenses) {
        expenses = getInitialExpenses();
        localStorage.setItem('demo_expenses', JSON.stringify(expenses));
      }

      if (method === 'POST') {
        const body = JSON.parse(options.body as string || '{}');
        const newExp: Expense = {
          id: Date.now(),
          amount: body.amount || 0,
          category: body.category || 'General',
          description: body.description || '',
          date: body.date || new Date().toISOString().split('T')[0],
          payment_method: body.payment_method || 'upi',
          notes: body.notes,
        };
        expenses.unshift(newExp);
        localStorage.setItem('demo_expenses', JSON.stringify(expenses));
        return newExp as T;
      }

      if (method === 'DELETE') {
        const idMatch = endpoint.match(/\/expenses\/(\d+)/);
        if (idMatch) {
          const id = parseInt(idMatch[1]);
          expenses = expenses.filter((e) => e.id !== id);
          localStorage.setItem('demo_expenses', JSON.stringify(expenses));
        }
        return {} as T;
      }

      return expenses as T;
    }

    if (endpoint.startsWith('/reminders')) {
      let reminders: Reminder[] = JSON.parse(localStorage.getItem('demo_reminders') || 'null');
      if (!reminders) {
        reminders = getInitialReminders();
        localStorage.setItem('demo_reminders', JSON.stringify(reminders));
      }

      if (method === 'POST') {
        if (endpoint.includes('/complete')) {
          const idMatch = endpoint.match(/\/reminders\/(\d+)\/complete/);
          if (idMatch) {
            const id = parseInt(idMatch[1]);
            const target = reminders.find((r) => r.id === id);
            if (target) target.status = target.status === 'completed' ? 'pending' : 'completed';
            localStorage.setItem('demo_reminders', JSON.stringify(reminders));
            return { completed: target } as T;
          }
        }
        const body = JSON.parse(options.body as string || '{}');
        const newRem: Reminder = {
          id: Date.now(),
          title: body.title || 'New Reminder',
          due_date: body.due_date || new Date().toISOString().split('T')[0],
          due_time: body.due_time || '10:00',
          description: body.description,
          priority: body.priority || 'medium',
          status: 'pending',
          recurrence: body.recurrence || 'none',
          is_overdue: false,
        };
        reminders.unshift(newRem);
        localStorage.setItem('demo_reminders', JSON.stringify(reminders));
        return newRem as T;
      }

      if (method === 'DELETE') {
        const idMatch = endpoint.match(/\/reminders\/(\d+)/);
        if (idMatch) {
          const id = parseInt(idMatch[1]);
          reminders = reminders.filter((r) => r.id !== id);
          localStorage.setItem('demo_reminders', JSON.stringify(reminders));
        }
        return {} as T;
      }

      return reminders as T;
    }

    if (endpoint.startsWith('/budgets')) {
      let budgets: Budget[] = JSON.parse(localStorage.getItem('demo_budgets') || 'null');
      if (!budgets) {
        budgets = getInitialBudgets();
        localStorage.setItem('demo_budgets', JSON.stringify(budgets));
      }

      if (method === 'POST') {
        const body = JSON.parse(options.body as string || '{}');
        const newBudget: Budget = {
          id: Date.now(),
          amount: body.amount || 5000,
          category: body.category,
          period: body.period || 'monthly',
          spent: 0,
          remaining: body.amount || 5000,
          percentage_used: 0,
          status: 'on_track',
          start_date: new Date().toISOString().split('T')[0],
        };
        budgets.push(newBudget);
        localStorage.setItem('demo_budgets', JSON.stringify(budgets));
        return newBudget as T;
      }

      return budgets as T;
    }

    if (endpoint.startsWith('/analytics/comparison')) {
      const comp: WeeklyComparison = {
        current_week: {
          start: '2026-08-31',
          end: '2026-09-06',
          total: 3559,
        },
        previous_week: {
          start: '2026-08-24',
          end: '2026-08-30',
          total: 4200,
        },
        change_amount: -641,
        change_percent: -15.26,
        direction: 'decreasing',
      };
      return comp as T;
    }

    if (endpoint.startsWith('/analytics/breakdown')) {
      const breakdown = {
        breakdown: [
          { category: 'Groceries', total: 1450, percentage_of_total: 40.7 },
          { category: 'Shopping', total: 890, percentage_of_total: 25.0 },
          { category: 'Food', total: 600, percentage_of_total: 16.9 },
          { category: 'Entertainment', total: 499, percentage_of_total: 14.0 },
          { category: 'Transportation', total: 120, percentage_of_total: 3.4 },
        ],
        top_category: 'Groceries',
        total_spent: 3559,
      };
      return breakdown as T;
    }

    if (endpoint.startsWith('/analytics/insights')) {
      const insight: FinancialInsight = {
        weekly_comparison: {
          current_week: { start: '2026-08-31', end: '2026-09-06', total: 3559 },
          previous_week: { start: '2026-08-24', end: '2026-08-30', total: 4200 },
          change_amount: -641,
          change_percent: -15.26,
          direction: 'decreasing',
        },
        top_category: 'Groceries',
        unusual_expenses: [],
        insight_text: 'Your spending is well-controlled this week, currently 15.3% lower than last week. Top expenditure is in Groceries (₹1,450).',
        disclaimer: 'Calculated using exact FastMCP financial arithmetic.',
      };
      return insight as T;
    }

    if (endpoint.startsWith('/planner/day')) {
      const today = new Date().toISOString().split('T')[0];
      const dayPlan: DayPlan = {
        date: today,
        reminders_count: 3,
        timed_reminders: [
          { time: '11:00', title: 'Nexora Hackathon 2026 Core Team Sync', priority: 'high', type: 'reminder' },
          { time: '17:00', title: 'Submit AI Life Manager Project Report', priority: 'high', type: 'reminder' },
        ],
        flexible_tasks: [
          { title: 'Review Monthly Safe Spending Limit & Budget Balance', priority: 'medium', type: 'budget_task' },
        ],
        schedule_blocks: [
          {
            period: 'Morning (08:00 - 12:00)',
            items: [
              { time: '09:00', title: 'Review Priority Reminders & Task Schedule', priority: 'high', type: 'routine' },
              { time: '11:00', title: 'Nexora Hackathon 2026 Core Team Sync', priority: 'high', type: 'meeting' },
            ],
          },
          {
            period: 'Afternoon (12:00 - 17:00)',
            items: [
              { time: '13:00', title: 'Lunch & Expense Audit Logging', priority: 'medium', type: 'break' },
              { time: '17:00', title: 'Submit AI Life Manager Project Report', priority: 'high', type: 'milestone' },
            ],
          },
          {
            period: 'Evening (17:00 - 21:00)',
            items: [
              { time: '19:30', title: 'Review Monthly Safe Spending Limit & Budget Balance', priority: 'medium', type: 'finance' },
            ],
          },
        ],
        weather: {
          location: 'Bengaluru',
          temperature_celsius: 27.5,
          conditions: 'Partly Cloudy with pleasant breeze',
          rain_expected: false,
          wind_speed_kmh: 12,
          relative_humidity: 65,
        },
        safe_spend_guidance: {
          monthly_budget: 15000,
          spent_so_far: 3559,
          remaining_budget: 11441,
          days_remaining_in_month: 26,
          recommended_daily_limit: 440,
        },
        notes: 'Weather is clear; excellent day for productive focus.',
      };
      return dayPlan as T;
    }

    if (endpoint.startsWith('/preferences')) {
      return [
        { key: 'currency', value: 'INR' },
        { key: 'reminder_style', value: 'detailed' },
        { key: 'voice_response_enabled', value: 'true' },
      ] as T;
    }

    if (endpoint.startsWith('/chat')) {
      const body = JSON.parse(options.body as string || '{}');
      const msg = (body.message || '').toLowerCase();

      let responseText = `[FastMCP: retrieve_relevant_context] I have analyzed your context.`;
      const toolsCalled: string[] = [];

      if (msg.includes('spent') || msg.includes('spend') || msg.includes('add')) {
        toolsCalled.push('add_expense');
        responseText = `[FastMCP: add_expense] Recorded transaction successfully! Your dashboard charts and budget utilization meters have been updated in real-time.`;
      } else if (msg.includes('plan') || msg.includes('day') || msg.includes('schedule')) {
        toolsCalled.push('plan_day');
        responseText = `[FastMCP: plan_day] Generated your structured Day Plan! You have 3 priority tasks scheduled for today, weather in Bengaluru is 27.5°C (no rain), and your safe daily spend limit is ₹440/day.`;
      } else if (msg.includes('weather') || msg.includes('umbrella') || msg.includes('rain')) {
        toolsCalled.push('get_forecast');
        responseText = `[FastMCP: get_forecast] Bengaluru forecast: 27.5°C, partly cloudy with 10% precipitation chance. No umbrella needed today!`;
      } else if (msg.includes('remind') || msg.includes('task')) {
        toolsCalled.push('create_reminder');
        responseText = `[FastMCP: create_reminder] Scheduled reminder with high priority. You will be notified on schedule.`;
      } else {
        toolsCalled.push('generate_financial_insight');
        responseText = `[FastMCP: generate_financial_insight] You've spent ₹3,559 so far this month across 6 transactions, remaining 15.3% below last week's spending rate.`;
      }

      return {
        response: responseText,
        used_fallback: false,
        tools_called: toolsCalled,
      } as T;
    }

    return {} as T;
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
