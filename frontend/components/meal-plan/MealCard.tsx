"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Clock } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";
import type { Meal } from "@/services/types/meal_plan";

interface MealCardProps {
  title: string;
  meal: Meal;
  accentColor?: string;
}

const MACRO_COLOURS: Record<string, string> = {
  calories: "text-yellow-400",
  protein: "text-blue-400",
  carbs: "text-green-400",
  fat: "text-orange-400",
};

export function MealCard({ title, meal, accentColor = "brand" }: MealCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card space-y-3">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <span
            className={clsx(
              "text-xs font-medium uppercase tracking-widest",
              `text-${accentColor}-400`
            )}
          >
            {title}
          </span>
          <h3 className="text-base font-semibold text-white mt-0.5">{meal.name}</h3>
        </div>
        <div className="text-right flex-shrink-0">
          <span className="text-xl font-bold text-yellow-400">{meal.calories}</span>
          <span className="text-xs text-gray-500 ml-1">kcal</span>
        </div>
      </div>

      {/* Macro pills */}
      <div className="flex flex-wrap gap-2">
        {[
          { label: "Protein", value: meal.protein_g, unit: "g", key: "protein" },
          { label: "Carbs", value: meal.carbs_g, unit: "g", key: "carbs" },
          { label: "Fat", value: meal.fat_g, unit: "g", key: "fat" },
        ].map(({ label, value, unit, key }) => (
          <div key={key} className="flex items-center gap-1 text-xs bg-gray-800 rounded-full px-3 py-1">
            <span className={clsx("font-semibold", MACRO_COLOURS[key])}>
              {value.toFixed(1)}{unit}
            </span>
            <span className="text-gray-500">{label}</span>
          </div>
        ))}
        <div className="flex items-center gap-1 text-xs bg-gray-800 rounded-full px-3 py-1 text-gray-400">
          <Clock size={11} />
          <span>{meal.preparation_time_minutes} min</span>
        </div>
      </div>

      {/* Ingredients (always visible) */}
      <div className="flex flex-wrap gap-1.5">
        {meal.ingredients.map((ing) => (
          <span
            key={ing}
            className="text-xs px-2 py-0.5 rounded-md bg-gray-900 border border-gray-700 text-gray-300"
          >
            {ing}
          </span>
        ))}
      </div>

      {/* Expandable: instructions + explanation */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300 transition-colors w-full"
      >
        {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
        {expanded ? "Hide details" : "View instructions & explanation"}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-3 overflow-hidden"
          >
            <div className="rounded-lg bg-gray-900 border border-gray-800 p-3 space-y-1">
              <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                Instructions
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">{meal.instructions}</p>
            </div>
            <div className="rounded-lg bg-gray-900 border border-gray-800 p-3 space-y-1">
              <p className="text-xs font-medium text-brand-400 uppercase tracking-wide">
                Why this meal?
              </p>
              <p className="text-sm text-gray-400 leading-relaxed">{meal.explanation}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
