"use client";

import { useState } from "react";
import { format, startOfWeek, addWeeks, subWeeks, isSameDay, parseISO } from "date-fns";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Droplet,
  Scale,
  Star,
  PlusCircle,
  TrendingUp,
  Smile,
  Calendar,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useAuth } from "@/hooks/useAuth";
import {
  useDashboard,
  useLogMeal,
  useLogWater,
  useLogWeight,
  useLogFeedback,
} from "@/hooks/useFeatures678";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

const CHART_TOOLTIP_STYLE = {
  contentStyle: { background: "#111827", border: "1px solid #374151", borderRadius: 8, fontSize: 12 },
  labelStyle: { color: "#f9fafb" },
  itemStyle: { color: "#9ca3af" },
};

function StatCard({ label, value, unit, color, icon: Icon }: { label: string; value: string; unit: string; color: string; icon?: LucideIcon }) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      className="card relative overflow-hidden bg-gray-900/60 backdrop-blur-md border-gray-800 hover:border-gray-700/80 transition-all duration-300"
    >
      <div className="flex justify-between items-start">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold">{label}</p>
          <p className={clsx("text-3xl font-extrabold mt-2 tracking-tight", color)}>
            {value}
            <span className="text-xs text-gray-500 font-normal ml-1.5">{unit}</span>
          </p>
        </div>
        {Icon && (
          <div className={clsx("p-2 rounded-lg bg-white/5 border border-white/5", color)}>
            <Icon size={16} />
          </div>
        )}
      </div>
    </motion.div>
  );
}

function DashboardContent() {
  const { user } = useAuth();
  const [currentWeekStart, setCurrentWeekStart] = useState<Date>(() =>
    startOfWeek(new Date(), { weekStartsOn: 1 })
  );
  const [selectedDate, setSelectedDate] = useState<Date>(() => new Date());
  const [activeTab, setActiveTab] = useState<"meal" | "water" | "weight" | "feedback">("meal");

  // Meal Form State
  const [mealType, setMealType] = useState<"breakfast" | "lunch" | "dinner" | "snack">("breakfast");
  const [mealName, setMealName] = useState("");
  const [mealCalories, setMealCalories] = useState("");
  const [mealProtein, setMealProtein] = useState("");

  // Water Custom State
  const [customWater, setCustomWater] = useState("");

  // Weight State
  const [weightInput, setWeightInput] = useState("");

  // Feedback State
  const [rating, setRating] = useState(5);
  const [hoverRating, setHoverRating] = useState<number | null>(null);
  const [feedbackComment, setFeedbackComment] = useState("");

  const weekStartStr = format(currentWeekStart, "yyyy-MM-dd");
  const selectedDateStr = format(selectedDate, "yyyy-MM-dd");

  const { data: dashboard, isLoading, isError } = useDashboard(user?.id ?? "", weekStartStr);

  // Mutations
  const logMealMutation = useLogMeal(user?.id ?? "", weekStartStr);
  const logWaterMutation = useLogWater(user?.id ?? "", weekStartStr);
  const logWeightMutation = useLogWeight(user?.id ?? "", weekStartStr);
  const logFeedbackMutation = useLogFeedback(user?.id ?? "", weekStartStr);

  function prevWeek() {
    setCurrentWeekStart((d) => subWeeks(d, 1));
  }
  function nextWeek() {
    setCurrentWeekStart((d) => addWeeks(d, 1));
  }

  const isCurrentWeek = weekStartStr === format(startOfWeek(new Date(), { weekStartsOn: 1 }), "yyyy-MM-dd");

  // Find the selected day's entry
  const selectedEntry = dashboard?.daily_entries.find((e) => e.date === selectedDateStr) || {
    date: selectedDateStr,
    calories_consumed: 0,
    protein_g: 0,
    water_ml: 0,
    weight_kg: null,
    meals: [],
    feedback_rating: null,
    feedback_comment: null,
  };

  // Get goals (with fallback defaults)
  const goals = dashboard?.goals || {
    calorie_target: 2000,
    protein_target_g: 80,
    water_target_ml: 2500,
  };

  // Progress metrics for selected date
  const caloriePercent = Math.min(100, Math.round((selectedEntry.calories_consumed / goals.calorie_target) * 100));
  const proteinPercent = Math.min(100, Math.round((selectedEntry.protein_g / goals.protein_target_g) * 100));
  const waterPercent = Math.min(100, Math.round((selectedEntry.water_ml / goals.water_target_ml) * 100));

  // Quick-log handlers
  async function handleAddMeal(e: React.FormEvent) {
    e.preventDefault();
    if (!mealName.trim() || !mealCalories || !mealProtein) return;
    await logMealMutation.mutateAsync({
      date: selectedDateStr,
      type: mealType,
      name: mealName.trim(),
      calories: parseInt(mealCalories),
      protein_g: parseFloat(mealProtein),
    });
    setMealName("");
    setMealCalories("");
    setMealProtein("");
  }

  async function handleAddWater(amount: number) {
    await logWaterMutation.mutateAsync({
      date: selectedDateStr,
      amount_ml: amount,
    });
  }

  async function handleCustomWater(e: React.FormEvent) {
    e.preventDefault();
    if (!customWater) return;
    await logWaterMutation.mutateAsync({
      date: selectedDateStr,
      amount_ml: parseInt(customWater),
    });
    setCustomWater("");
  }

  async function handleAddWeight(e: React.FormEvent) {
    e.preventDefault();
    if (!weightInput) return;
    await logWeightMutation.mutateAsync({
      date: selectedDateStr,
      weight_kg: parseFloat(weightInput),
    });
    setWeightInput("");
  }

  async function handleAddFeedback(e: React.FormEvent) {
    e.preventDefault();
    await logFeedbackMutation.mutateAsync({
      date: selectedDateStr,
      rating,
      comment: feedbackComment.trim() || null,
    });
    setFeedbackComment("");
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 font-sans">
      {/* 1. Header with Week Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent flex items-center gap-2">
            Weekly Dashboard
          </h1>
          <p className="text-gray-400 text-sm mt-1 flex items-center gap-1.5 font-light">
            <Calendar size={14} className="text-brand-400" />
            {format(currentWeekStart, "MMM d")} – {format(addWeeks(currentWeekStart, 1), "MMM d, yyyy")}
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-center">
          <button onClick={prevWeek} className="btn-secondary p-2.5 rounded-xl hover:bg-gray-800 transition-colors">
            <ChevronLeft size={16} />
          </button>
          <button
            onClick={nextWeek}
            disabled={isCurrentWeek}
            className="btn-secondary p-2.5 rounded-xl disabled:opacity-30 disabled:cursor-not-allowed hover:bg-gray-800 transition-colors"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="flex flex-col items-center justify-center py-32 text-gray-400 space-y-4">
          <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <p className="animate-pulse text-sm font-light">Compiling your nutrition insights...</p>
        </div>
      )}

      {isError && (
        <div className="card text-center py-16 text-gray-400 border border-red-500/20 bg-red-500/5">
          <p className="font-medium text-white mb-2">Could not retrieve dashboard data.</p>
          <p className="text-sm text-gray-500">Please double check your credentials and network connection.</p>
        </div>
      )}

      {dashboard && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Dashboard Panel */}
          <div className="lg:col-span-2 space-y-8">
            {/* 7-day Averages Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Avg Calories" value={dashboard.summary.avg_calories.toFixed(0)} unit="kcal" color="text-yellow-400" icon={TrendingUp} />
              <StatCard label="Avg Protein" value={dashboard.summary.avg_protein_g.toFixed(1)} unit="g" color="text-blue-400" icon={PlusCircle} />
              <StatCard label="Avg Water" value={(dashboard.summary.avg_water_ml / 1000).toFixed(1)} unit="L" color="text-cyan-400" icon={Droplet} />
              <StatCard
                label="Weight Change"
                value={dashboard.summary.weight_change_kg != null ? (dashboard.summary.weight_change_kg >= 0 ? `+${dashboard.summary.weight_change_kg}` : `${dashboard.summary.weight_change_kg}`) : "–"}
                unit="kg"
                color={dashboard.summary.weight_change_kg != null && dashboard.summary.weight_change_kg < 0 ? "text-emerald-400" : "text-orange-400"}
                icon={Scale}
              />
            </div>

            {/* Weekly Progress Tracker (Pill Selector for Dates) */}
            <div className="card bg-gray-900/40 backdrop-blur-md space-y-4">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Select Day to Log & View</h3>
              <div className="grid grid-cols-7 gap-2">
                {dashboard.daily_entries.map((entry) => {
                  const entryDate = parseISO(entry.date);
                  const isSelected = isSameDay(entryDate, selectedDate);
                  const isToday = isSameDay(entryDate, new Date());
                  return (
                    <button
                      key={entry.date}
                      onClick={() => setSelectedDate(entryDate)}
                      className={clsx(
                        "flex flex-col items-center py-2.5 rounded-xl border transition-all duration-300 hover:scale-[1.03]",
                        isSelected
                          ? "bg-brand-600/20 border-brand-500 text-brand-400 shadow-lg shadow-brand-900/10"
                          : "bg-gray-800/40 border-gray-800 hover:border-gray-700 text-gray-400",
                        isToday && !isSelected && "border-emerald-500/30 text-emerald-400"
                      )}
                    >
                      <span className="text-[10px] uppercase font-bold tracking-wider">{format(entryDate, "EEE")}</span>
                      <span className="text-lg font-extrabold mt-1">{format(entryDate, "d")}</span>
                      <div className="w-1.5 h-1.5 rounded-full mt-2 bg-yellow-400/80" style={{ opacity: entry.calories_consumed > 0 ? 1 : 0 }} />
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Calories */}
              <div className="card bg-gray-900/40 backdrop-blur-md">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center justify-between">
                  <span>Daily Calories</span>
                  <span className="text-[10px] text-yellow-400 uppercase tracking-widest font-bold">Goal: {goals.calorie_target} kcal</span>
                </h3>
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={dashboard.charts_data.calories}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => format(parseISO(v), "EEE")} />
                    <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} />
                    <Tooltip {...CHART_TOOLTIP_STYLE} />
                    <Bar dataKey="value" fill="#facc15" radius={[4, 4, 0, 0]} name="kcal" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Protein */}
              <div className="card bg-gray-900/40 backdrop-blur-md">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center justify-between">
                  <span>Daily Protein</span>
                  <span className="text-[10px] text-blue-400 uppercase tracking-widest font-bold">Goal: {goals.protein_target_g}g</span>
                </h3>
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={dashboard.charts_data.protein}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => format(parseISO(v), "EEE")} />
                    <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} />
                    <Tooltip {...CHART_TOOLTIP_STYLE} />
                    <Line type="monotone" dataKey="value" stroke="#60a5fa" strokeWidth={2.5} dot={{ fill: "#60a5fa" }} name="g" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Water */}
              <div className="card bg-gray-900/40 backdrop-blur-md">
                <h3 className="text-sm font-semibold text-white mb-4 flex items-center justify-between">
                  <span>Daily Water Intake</span>
                  <span className="text-[10px] text-cyan-400 uppercase tracking-widest font-bold">Goal: {(goals.water_target_ml / 1000).toFixed(1)}L</span>
                </h3>
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={dashboard.charts_data.water}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => format(parseISO(v), "EEE")} />
                    <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} />
                    <Tooltip {...CHART_TOOLTIP_STYLE} />
                    <Bar dataKey="value" fill="#22d3ee" radius={[4, 4, 0, 0]} name="L" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Weight */}
              <div className="card bg-gray-900/40 backdrop-blur-md">
                <h3 className="text-sm font-semibold text-white mb-4">Weight Trend</h3>
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={dashboard.charts_data.weight}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} tickFormatter={(v) => format(parseISO(v), "EEE")} />
                    <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} domain={["auto", "auto"]} />
                    <Tooltip {...CHART_TOOLTIP_STYLE} />
                    <Line type="monotone" dataKey="value" stroke="#4ade80" strokeWidth={2.5} dot={{ fill: "#4ade80" }} name="kg" connectNulls />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Selected Day's Log Summary */}
            <div className="card bg-gray-900/40 backdrop-blur-md space-y-4">
              <h3 className="text-base font-bold text-white flex justify-between items-center">
                <span>Logs for {format(selectedDate, "MMMM d, yyyy")}</span>
                {selectedEntry.feedback_rating && (
                  <span className="flex items-center gap-1 bg-yellow-400/10 text-yellow-400 text-xs px-2.5 py-1 rounded-full border border-yellow-400/20 font-semibold">
                    <Star size={12} fill="currentColor" /> {selectedEntry.feedback_rating} Star Day
                  </span>
                )}
              </h3>

              {selectedEntry.meals && selectedEntry.meals.length > 0 ? (
                <div className="divide-y divide-gray-800/80">
                  {selectedEntry.meals.map((meal, idx) => (
                    <div key={idx} className="py-3 flex justify-between items-center">
                      <div>
                        <p className="text-sm font-bold text-white capitalize">{meal.type}</p>
                        <p className="text-xs text-gray-500 font-light mt-0.5">{meal.name}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-yellow-400">{meal.calories} kcal</p>
                        <p className="text-xs text-blue-400 font-light mt-0.5">{meal.protein_g}g Protein</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500 italic py-2">No meals logged for this date.</p>
              )}

              {selectedEntry.feedback_comment && (
                <div className="bg-gray-800/30 rounded-xl p-3 border border-gray-800/50 mt-4">
                  <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold mb-1 flex items-center gap-1.5">
                    <Smile size={12} className="text-yellow-400" /> Day Summary Note
                  </p>
                  <p className="text-sm text-gray-300 font-light italic">&quot;{selectedEntry.feedback_comment}&quot;</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar Tracking Section */}
          <div className="space-y-8">
            {/* 2. Goal Progress Section */}
            <div className="card bg-gray-900/60 backdrop-blur-md space-y-6">
              <h2 className="text-lg font-bold text-white border-b border-gray-800 pb-3 flex items-center justify-between">
                <span>Goal Progress</span>
                <span className="text-xs text-gray-500 font-normal">For {format(selectedDate, "EEE")}</span>
              </h2>

              {/* Calories Progress */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-gray-400">Calories</span>
                  <span className="text-yellow-400">{selectedEntry.calories_consumed} / {goals.calorie_target} kcal</span>
                </div>
                <div className="h-2.5 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-yellow-500 to-amber-400 rounded-full transition-all duration-500"
                    style={{ width: `${caloriePercent}%` }}
                  />
                </div>
              </div>

              {/* Protein Progress */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-gray-400">Protein</span>
                  <span className="text-blue-400">{selectedEntry.protein_g.toFixed(1)} / {goals.protein_target_g}g</span>
                </div>
                <div className="h-2.5 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-400 rounded-full transition-all duration-500"
                    style={{ width: `${proteinPercent}%` }}
                  />
                </div>
              </div>

              {/* Water Progress */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-gray-400">Water</span>
                  <span className="text-cyan-400">{selectedEntry.water_ml} / {goals.water_target_ml}ml</span>
                </div>
                <div className="h-2.5 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-400 rounded-full transition-all duration-500"
                    style={{ width: `${waterPercent}%` }}
                  />
                </div>
              </div>
            </div>

            {/* 3. Quick Action Log Panel */}
            <div className="card bg-gray-900/60 backdrop-blur-md flex flex-col">
              {/* Tab Selector */}
              <div className="grid grid-cols-4 gap-1 p-1 bg-gray-950 border border-gray-800/80 rounded-xl mb-6">
                {(["meal", "water", "weight", "feedback"] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={clsx(
                      "text-[10px] font-bold uppercase py-2 rounded-lg transition-all capitalize tracking-wider",
                      activeTab === tab
                        ? "bg-brand-600 text-white shadow-md"
                        : "text-gray-500 hover:text-gray-300"
                    )}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="flex-1">
                <AnimatePresence mode="wait">
                  {activeTab === "meal" && (
                    <motion.form
                      key="meal"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      onSubmit={handleAddMeal}
                      className="space-y-4"
                    >
                      <div>
                        <label className="label">Meal Type</label>
                        <div className="grid grid-cols-4 gap-1 bg-gray-950 p-0.5 rounded-lg border border-gray-800">
                          {(["breakfast", "lunch", "dinner", "snack"] as const).map((type) => (
                            <button
                              key={type}
                              type="button"
                              onClick={() => setMealType(type)}
                              className={clsx(
                                "text-[10px] font-bold uppercase py-1.5 rounded-md transition-all capitalize",
                                mealType === type ? "bg-gray-800 text-white" : "text-gray-500"
                              )}
                            >
                              {type}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div>
                        <label className="label">Meal Description</label>
                        <input
                          type="text"
                          required
                          value={mealName}
                          onChange={(e) => setMealName(e.target.value)}
                          placeholder="e.g. Avocado Toast with Egg"
                          className="input-field text-sm"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="label">Calories (kcal)</label>
                          <input
                            type="number"
                            required
                            min="0"
                            value={mealCalories}
                            onChange={(e) => setMealCalories(e.target.value)}
                            placeholder="350"
                            className="input-field text-sm"
                          />
                        </div>
                        <div>
                          <label className="label">Protein (g)</label>
                          <input
                            type="number"
                            step="0.1"
                            required
                            min="0"
                            value={mealProtein}
                            onChange={(e) => setMealProtein(e.target.value)}
                            placeholder="12.5"
                            className="input-field text-sm"
                          />
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={logMealMutation.isPending}
                        className="w-full btn-primary py-3 font-semibold rounded-xl flex items-center justify-center gap-1.5 shadow-lg shadow-brand-900/10 text-sm hover:scale-[1.01] active:scale-[0.99] transition-all"
                      >
                        <Plus size={16} /> Log Meal
                      </button>
                    </motion.form>
                  )}

                  {activeTab === "water" && (
                    <motion.div
                      key="water"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      className="space-y-6"
                    >
                      <div>
                        <label className="label mb-3">Quick Hydrate</label>
                        <div className="grid grid-cols-2 gap-3">
                          {[
                            { label: "Glass (+250ml)", val: 250 },
                            { label: "Bottle (+500ml)", val: 500 },
                            { label: "Carafe (+750ml)", val: 750 },
                            { label: "Flask (+1000ml)", val: 1000 },
                          ].map((item) => (
                            <button
                              key={item.val}
                              type="button"
                              onClick={() => handleAddWater(item.val)}
                              disabled={logWaterMutation.isPending}
                              className="py-3 bg-cyan-950/20 hover:bg-cyan-950/40 border border-cyan-800/20 text-cyan-400 font-bold rounded-xl text-xs flex flex-col items-center gap-1.5 hover:scale-[1.02] active:scale-[0.98] transition-all"
                            >
                              <Droplet size={14} className="fill-current" />
                              {item.label}
                            </button>
                          ))}
                        </div>
                      </div>

                      <form onSubmit={handleCustomWater} className="space-y-4 pt-4 border-t border-gray-800/80">
                        <div>
                          <label className="label">Custom Amount (ml)</label>
                          <div className="flex gap-2">
                            <input
                              type="number"
                              required
                              min="1"
                              placeholder="300"
                              value={customWater}
                              onChange={(e) => setCustomWater(e.target.value)}
                              className="input-field text-sm"
                            />
                            <button
                              type="submit"
                              disabled={logWaterMutation.isPending}
                              className="btn-primary px-5 rounded-xl text-sm font-semibold flex items-center justify-center"
                            >
                              Log
                            </button>
                          </div>
                        </div>
                      </form>
                    </motion.div>
                  )}

                  {activeTab === "weight" && (
                    <motion.form
                      key="weight"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      onSubmit={handleAddWeight}
                      className="space-y-4"
                    >
                      <div>
                        <label className="label">Current Weight (kg)</label>
                        <input
                          type="number"
                          step="0.01"
                          required
                          min="1"
                          placeholder="72.5"
                          value={weightInput}
                          onChange={(e) => setWeightInput(e.target.value)}
                          className="input-field text-sm"
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={logWeightMutation.isPending}
                        className="w-full btn-primary py-3 font-semibold rounded-xl flex items-center justify-center gap-1.5 shadow-lg shadow-brand-900/10 text-sm hover:scale-[1.01] active:scale-[0.99] transition-all"
                      >
                        <Scale size={16} /> Log Weight
                      </button>
                    </motion.form>
                  )}

                  {activeTab === "feedback" && (
                    <motion.form
                      key="feedback"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      onSubmit={handleAddFeedback}
                      className="space-y-4"
                    >
                      <div>
                        <label className="label mb-3">Daily Energy & Health Rating</label>
                        <div className="flex items-center gap-2">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <button
                              key={star}
                              type="button"
                              onMouseEnter={() => setHoverRating(star)}
                              onMouseLeave={() => setHoverRating(null)}
                              onClick={() => setRating(star)}
                              className="text-2xl hover:scale-120 active:scale-95 transition-all text-gray-600"
                            >
                              <Star
                                size={28}
                                className={clsx(
                                  "transition-colors duration-200",
                                  star <= (hoverRating ?? rating)
                                    ? "text-yellow-400 fill-current"
                                    : "text-gray-700"
                                )}
                              />
                            </button>
                          ))}
                        </div>
                      </div>

                      <div>
                        <label className="label">Daily Notes / Feeling</label>
                        <textarea
                          placeholder="Felt strong during my workout today! Meal plan kept me full."
                          rows={3}
                          value={feedbackComment}
                          onChange={(e) => setFeedbackComment(e.target.value)}
                          className="input-field text-sm resize-none"
                        />
                      </div>

                      <button
                        type="submit"
                        disabled={logFeedbackMutation.isPending}
                        className="w-full btn-primary py-3 font-semibold rounded-xl flex items-center justify-center gap-1.5 shadow-lg shadow-brand-900/10 text-sm hover:scale-[1.01] active:scale-[0.99] transition-all"
                      >
                        Submit Feedback
                      </button>
                    </motion.form>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

