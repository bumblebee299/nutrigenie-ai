"use client";

import type { DailyNutritionSummary } from "@/services/types/meal_plan";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface NutritionSummaryCardProps {
  summary: DailyNutritionSummary;
  targetCalories: number;
}

function StatRow({
  label,
  value,
  unit,
  color,
}: {
  label: string;
  value: number;
  unit: string;
  color: string;
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex items-center gap-2">
        <span className={`w-2.5 h-2.5 rounded-full ${color}`} />
        <span className="text-sm text-gray-300">{label}</span>
      </div>
      <span className="text-sm font-semibold text-white">
        {typeof value === "number" ? value.toFixed(1) : value}
        <span className="text-xs text-gray-500 ml-1 font-normal">{unit}</span>
      </span>
    </div>
  );
}

export function NutritionSummaryCard({ summary, targetCalories }: NutritionSummaryCardProps) {
  const pct = Math.min(100, Math.round((summary.total_calories / targetCalories) * 100));

  const chartData = [
    { name: "Protein", value: summary.protein_g, fill: "#60a5fa" },
    { name: "Carbs", value: summary.carbs_g, fill: "#4ade80" },
    { name: "Fat", value: summary.fat_g, fill: "#fb923c" },
  ];

  return (
    <div className="card space-y-5">
      <h3 className="font-semibold text-white">Daily Nutrition Summary</h3>

      {/* Radial chart — macros */}
      <div className="flex items-center gap-4">
        <div className="w-32 h-32 flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="40%"
              outerRadius="90%"
              data={chartData}
              startAngle={90}
              endAngle={-270}
            >
              <RadialBar dataKey="value" background={{ fill: "#1f2937" }} />
              <Tooltip
                contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
                labelStyle={{ color: "#f9fafb" }}
              />
            </RadialBarChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="flex flex-col gap-1.5 text-xs">
          {chartData.map((d) => (
            <div key={d.name} className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ background: d.fill }} />
              <span className="text-gray-400">{d.name}</span>
              <span className="text-white font-medium">{d.value.toFixed(1)}g</span>
            </div>
          ))}
        </div>
      </div>

      {/* Calorie target */}
      <div className="rounded-xl bg-gray-900 border border-gray-800 p-4">
        <div className="flex items-end justify-between mb-2">
          <span className="text-sm text-gray-400">Total Calories</span>
          <span className="text-sm text-gray-500">{pct}% of target</span>
        </div>
        <div className="flex items-end gap-1 mb-2">
          <span className="text-3xl font-bold text-yellow-400">{summary.total_calories}</span>
          <span className="text-gray-500 mb-0.5">/ {targetCalories} kcal</span>
        </div>
        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-yellow-400 rounded-full transition-all duration-700"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Stats list */}
      <div>
        <StatRow label="Protein" value={summary.protein_g} unit="g" color="bg-blue-400" />
        <StatRow label="Carbohydrates" value={summary.carbs_g} unit="g" color="bg-green-400" />
        <StatRow label="Fat" value={summary.fat_g} unit="g" color="bg-orange-400" />
        <StatRow label="Fibre" value={summary.fiber_g} unit="g" color="bg-purple-400" />
        <StatRow label="Water" value={summary.water_ml / 1000} unit="L" color="bg-cyan-400" />
      </div>
    </div>
  );
}
