import React from 'react';
import { DayPlanView } from '../components/planner/DayPlanView';

interface PlannerPageProps {
  currencySymbol?: string;
}

export const PlannerPage: React.FC<PlannerPageProps> = ({ currencySymbol = '₹' }) => {
  return (
    <div className="space-y-6">
      <DayPlanView currencySymbol={currencySymbol} />
    </div>
  );
};
