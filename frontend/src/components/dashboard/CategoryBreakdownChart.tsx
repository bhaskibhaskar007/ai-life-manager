import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { CategoryBreakdownItem } from '../../types';

interface CategoryBreakdownChartProps {
  data: CategoryBreakdownItem[];
  currencySymbol?: string;
}

const COLORS = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#06b6d4', '#64748b'];

export const CategoryBreakdownChart: React.FC<CategoryBreakdownChartProps> = ({
  data,
  currencySymbol = '₹',
}) => {
  const chartData = data && data.length > 0 ? data : [{ category: 'No Expenses', total: 1, percentage_of_total: 100 }];

  return (
    <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col">
      <div className="mb-2">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white">Category Allocation</h3>
        <p className="text-xs text-slate-500">Distribution of spending across budget categories</p>
      </div>

      <div className="h-64 w-full flex-1 flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={4}
              dataKey="total"
              nameKey="category"
            >
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: any, name: any) => [`${currencySymbol}${Number(value).toLocaleString()}`, name]}
              contentStyle={{
                backgroundColor: '#1e293b',
                border: 'none',
                borderRadius: '0.75rem',
                color: '#fff',
                fontSize: '12px',
              }}
            />
            <Legend
              layout="horizontal"
              verticalAlign="bottom"
              align="center"
              wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
