"use client";

import { useState } from "react";
import { ArrowRight, Loader2, X, Plus, TrendingDown } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useFoodSwap } from "@/hooks/useFeatures678";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { motion, AnimatePresence } from "framer-motion";

function FoodSwapPageContent() {
  const { user } = useAuth();
  const { result, isLoading, getSwaps, reset } = useFoodSwap();
  const [foodItem, setFoodItem] = useState("");
  const [restriction, setRestriction] = useState("");
  const [restrictions, setRestrictions] = useState<string[]>([]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!foodItem.trim() || !user) return;
    getSwaps({ food_item: foodItem.trim(), user_id: user.id, dietary_restrictions: restrictions });
  }

  function addRestriction() {
    const val = restriction.trim();
    if (val && !restrictions.includes(val)) {
      setRestrictions((prev) => [...prev, val]);
      setRestriction("");
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Healthy Food Swap</h1>
          <p className="text-gray-400 text-sm mt-1">
            Enter any food — get 3 healthier alternatives with nutritional explanations
          </p>
        </div>
        {result && (
          <button onClick={() => { reset(); setFoodItem(""); }} className="btn-secondary text-sm">
            Try another
          </button>
        )}
      </div>

      {!result && (
        <form onSubmit={handleSubmit} className="card space-y-4">
          <div>
            <label className="label">Food item</label>
            <input
              type="text"
              value={foodItem}
              onChange={(e) => setFoodItem(e.target.value)}
              className="input-field"
              placeholder="e.g. Pizza, Fried chicken, Chocolate cake…"
            />
          </div>

          <div>
            <label className="label">Dietary restrictions (optional)</label>
            <div className="flex gap-2 mb-2 flex-wrap">
              {restrictions.map((r) => (
                <span key={r} className="flex items-center gap-1 text-xs bg-gray-800 border border-gray-700 rounded-full px-3 py-1 text-gray-300">
                  {r}
                  <button type="button" onClick={() => setRestrictions((p) => p.filter((x) => x !== r))}>
                    <X size={11} className="text-gray-500 hover:text-red-400" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={restriction}
                onChange={(e) => setRestriction(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addRestriction(); } }}
                className="input-field flex-1"
                placeholder="e.g. vegan, gluten-free"
              />
              <button type="button" onClick={addRestriction} className="btn-secondary px-3">
                <Plus size={16} />
              </button>
            </div>
          </div>

          <button type="submit" disabled={!foodItem.trim() || isLoading} className="btn-primary w-full flex items-center justify-center gap-2">
            {isLoading ? <><Loader2 size={16} className="animate-spin" /> Finding swaps…</> : "Find Healthier Swaps"}
          </button>
        </form>
      )}

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            <div className="rounded-xl bg-gray-900 border border-brand-800 p-4 space-y-1">
              <p className="text-xs font-medium text-brand-400 uppercase tracking-wide">General Advice</p>
              <p className="text-sm text-gray-300">{result.general_advice}</p>
            </div>

            {result.swaps.map((swap, i) => (
              <div key={i} className="card space-y-3">
                <div className="flex items-center gap-3 text-sm font-medium">
                  <span className="text-red-400">{swap.original}</span>
                  <ArrowRight size={14} className="text-gray-600 flex-shrink-0" />
                  <span className="text-green-400">{swap.healthier_option}</span>
                </div>

                <div className="flex items-center gap-1 text-xs text-green-400">
                  <TrendingDown size={12} />
                  <span>Save ~{swap.calorie_reduction} kcal per serving</span>
                </div>

                <div className="flex flex-wrap gap-1.5">
                  {swap.benefits.map((b) => (
                    <span key={b} className="text-xs px-2 py-0.5 rounded-md bg-gray-800 border border-gray-700 text-gray-300">{b}</span>
                  ))}
                </div>

                <div className="rounded-lg bg-gray-900 border border-gray-800 p-3 space-y-1.5">
                  <p className="text-xs text-gray-400"><span className="font-medium text-white">Tip: </span>{swap.preparation_tip}</p>
                  <p className="text-xs text-brand-400"><span className="font-medium">Why: </span>{swap.explanation}</p>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function FoodSwapPage() {
  return <ProtectedRoute><FoodSwapPageContent /></ProtectedRoute>;
}
