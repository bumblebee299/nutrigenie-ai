"use client";

import { motion } from "framer-motion";
import { ArrowRight, TrendingDown } from "lucide-react";
import type { ImageAnalysisResponse } from "@/services/types/image_analysis";

interface AnalysisResultCardProps {
  result: ImageAnalysisResponse;
}

export function AnalysisResultCard({ result }: AnalysisResultCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-5"
    >
      {/* Calorie banner */}
      <div className="card flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Total Estimated Calories</p>
          <p className="text-4xl font-bold text-yellow-400 mt-1">
            {result.total_estimated_calories}
            <span className="text-base text-gray-400 font-normal ml-1">kcal</span>
          </p>
        </div>
        {result.image_url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={result.image_url}
            alt="Analysed food"
            className="w-16 h-16 rounded-xl object-cover border border-gray-700"
          />
        )}
      </div>

      {/* Detected foods */}
      <div className="card space-y-3">
        <h3 className="font-semibold text-white">Detected Foods</h3>
        <div className="divide-y divide-gray-800">
          {result.detected_foods.map((food, i) => (
            <div key={i} className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm font-medium text-white">{food.name}</p>
                <p className="text-xs text-gray-500 mt-0.5">{food.portion_size}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-yellow-400">{food.estimated_calories} kcal</p>
                <p className="text-xs text-gray-600 mt-0.5">
                  {Math.round(food.confidence * 100)}% confident
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Healthier alternatives */}
      {result.healthier_alternatives.length > 0 && (
        <div className="card space-y-3">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <TrendingDown size={16} className="text-green-400" />
            Healthier Alternatives
          </h3>
          <div className="space-y-3">
            {result.healthier_alternatives.map((swap, i) => (
              <div key={i} className="rounded-lg bg-gray-900 border border-gray-800 p-3 space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-red-400 font-medium">{swap.original}</span>
                  <ArrowRight size={14} className="text-gray-600 flex-shrink-0" />
                  <span className="text-green-400 font-medium">{swap.alternative}</span>
                </div>
                <p className="text-xs text-gray-400">{swap.reason}</p>
                <div className="flex items-center gap-1 text-xs">
                  <TrendingDown size={11} className="text-green-400" />
                  <span className="text-green-400 font-medium">
                    Save ~{swap.calorie_difference} kcal
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Nutritional notes */}
      {result.nutritional_notes && (
        <div className="card space-y-1">
          <h3 className="font-semibold text-white text-sm">Nutritional Notes</h3>
          <p className="text-sm text-gray-400 leading-relaxed">{result.nutritional_notes}</p>
        </div>
      )}

      {/* Overall explanation */}
      <div className="rounded-xl bg-gray-900 border border-brand-800 p-4 space-y-1">
        <p className="text-xs font-medium text-brand-400 uppercase tracking-wide">
          AI Recommendation
        </p>
        <p className="text-sm text-gray-300 leading-relaxed">{result.explanation}</p>
      </div>
    </motion.div>
  );
}
