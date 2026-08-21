export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  currency_pref: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Expense {
  id: number;
  amount: number;
  category: string;
  description?: string | null;
  date: string;
  payment_method: string;
  notes?: string | null;
}

export interface Category {
  id: number;
  name: string;
  is_custom: boolean;
}

export interface Reminder {
  id: number;
  title: string;
  description?: string | null;
  due_date: string;
  due_time?: string | null;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'completed' | 'overdue' | 'cancelled';
  recurrence: 'none' | 'daily' | 'weekly' | 'monthly';
  is_overdue: boolean;
}

export interface Budget {
  id: number;
  category?: string | null;
  amount: number;
  period: 'weekly' | 'monthly' | 'yearly';
  start_date: string;
  spent?: number;
  remaining?: number;
  percentage_used?: number;
  status?: 'on_track' | 'at_risk' | 'exceeded';
}

export interface WeeklyComparison {
  current_week: {
    start: string;
    end: string;
    total: number;
  };
  previous_week: {
    start: string;
    end: string;
    total: number;
  };
  change_amount: number;
  change_percent: number | null;
  direction?: string;
}

export interface CategoryBreakdownItem {
  category: string;
  total: number;
  percentage_of_total: number;
}

export interface FinancialInsight {
  weekly_comparison: WeeklyComparison;
  top_category: string | null;
  unusual_expenses: Array<{
    expense_id: number;
    amount: number;
    category: string;
    date: string;
    typical_amount: number;
    times_higher_than_typical: number;
  }>;
  insight_text: string;
  disclaimer: string;
}

export interface WeatherData {
  location: string;
  temperature_celsius: number;
  conditions: string;
  rain_expected: boolean;
  wind_speed_kmh?: number;
  relative_humidity?: number;
}

export interface DayPlan {
  date: string;
  reminders_count: number;
  timed_reminders: Array<{ time: string; title: string; priority: string; type: string }>;
  flexible_tasks: Array<{ title: string; priority: string; type: string }>;
  schedule_blocks: Array<{
    period: string;
    items: Array<{ time?: string; title: string; priority?: string; type: string }>;
  }>;
  weather?: WeatherData | null;
  safe_spend_guidance?: {
    monthly_budget: number;
    spent_so_far: number;
    remaining_budget: number;
    days_remaining_in_month: number;
    recommended_daily_limit: number;
  } | null;
  notes: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tools_called?: string[];
  used_fallback?: boolean;
}
