"use client";

import { RefreshCw, AlertTriangle, CheckCircle, Info } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useLabelAnalysis } from "@/hooks/useFeatures678";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ImageDropzone } from "@/components/image-analysis/ImageDropzone";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useCallback } from "react";
import type { LabelWarning } from "@/services/types/tasks_678";
import clsx from "clsx";

const SEVERITY_STYLES: Record<LabelWarning["severity"], { icon: React.ReactNode; cls: string }> = {
  low: { icon: <Info size={14} />, cls: "text-blue-400 bg-blue-950 border-blue-800" },
  medium: { icon: <AlertTriangle size={14} />, cls: "text-yellow-400 bg-yellow-950 border-yellow-800" },
  high: { icon: <AlertTriangle size={14} />, cls: "text-red-400 bg-red-950 border-red-800" },
};

function NutrientRow({ name, amount, dv, assessment }: { name: string; amount: string; dv?: number | null; assessment: string }) {
  return (
    <div className="flex items-start justify-between py-2.5 border-b border-gray-800 last:border-0 gap-4">
      <div className="min-w-0">
        <p className="text-sm font-medium text-white">{name}</p>
        <p className="text-xs text-gray-500 mt-0.5">{assessment}</p>
      </div>
      <div className="text-right flex-shrink-0">
        <p className="text-sm font-semibold text-white">{amount}</p>
        {dv != null && <p className="text-xs text-gray-500">{dv}% DV</p>}
      </div>
    </div>
  );
}

function LabelReaderContent() {
  const { user } = useAuth();
  const { result, isLoading, analyse, reset } = useLabelAnalysis();
  const [preview, setPreview] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      setPreview(URL.createObjectURL(file));
      if (user) analyse(file, user.id);
    },
    [user, analyse]
  );

  function handleReset() {
    reset();
    if (preview) { URL.revokeObjectURL(preview); setPreview(null); }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Nutrition Label Reader</h1>
          <p className="text-gray-400 text-sm mt-1">Upload a label — AI explains every nutrient in plain English</p>
        </div>
        {result && (
          <button onClick={handleReset} className="btn-secondary flex items-center gap-2 text-sm">
            <RefreshCw size={14} /> New Label
          </button>
        )}
      </div>

      <ImageDropzone onFileSelected={handleFile} isLoading={isLoading} preview={preview} onClear={handleReset} />

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            {/* Header */}
            <div className="card flex items-center justify-between">
              <div>
                {result.product_name && <p className="text-xs text-gray-500 mb-0.5">{result.product_name}</p>}
                <p className="text-sm text-gray-400">Serving size: <span className="text-white font-medium">{result.serving_size}</span></p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-yellow-400">{result.calories_per_serving}</p>
                <p className="text-xs text-gray-500">kcal / serving</p>
              </div>
            </div>

            {/* Warnings */}
            {result.warnings.length > 0 && (
              <div className="space-y-2">
                {result.warnings.map((w, i) => {
                  const s = SEVERITY_STYLES[w.severity];
                  return (
                    <div key={i} className={clsx("flex items-start gap-2 rounded-lg border p-3 text-sm", s.cls)}>
                      {s.icon}<div><span className="font-medium">{w.category}: </span>{w.message}</div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Key nutrients */}
            <div className="card">
              <h3 className="font-semibold text-white mb-1">Key Nutrients</h3>
              <NutrientRow name={result.sugar.name} amount={result.sugar.amount} dv={result.sugar.daily_value_percent} assessment={result.sugar.assessment} />
              <NutrientRow name={result.fat.name} amount={result.fat.amount} dv={result.fat.daily_value_percent} assessment={result.fat.assessment} />
              <NutrientRow name={result.protein.name} amount={result.protein.amount} dv={result.protein.daily_value_percent} assessment={result.protein.assessment} />
              <NutrientRow name={result.sodium.name} amount={result.sodium.amount} dv={result.sodium.daily_value_percent} assessment={result.sodium.assessment} />
              {result.additional_nutrients.map((n, i) => (
                <NutrientRow key={i} name={n.name} amount={n.amount} dv={n.daily_value_percent} assessment={n.assessment} />
              ))}
            </div>

            {/* Assessment */}
            <div className="card space-y-1">
              <div className="flex items-center gap-1.5 mb-2">
                <CheckCircle size={14} className="text-brand-400" />
                <h3 className="font-semibold text-white text-sm">Overall Assessment</h3>
              </div>
              <p className="text-sm text-gray-300">{result.overall_assessment}</p>
              <p className="text-xs text-brand-400 pt-1">{result.explanation}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function LabelReaderPage() {
  return <ProtectedRoute><LabelReaderContent /></ProtectedRoute>;
}
