"use client";

import { useState, useCallback } from "react";
import { RefreshCw } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useImageAnalysis } from "@/hooks/useImageAnalysis";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { ImageDropzone } from "@/components/image-analysis/ImageDropzone";
import { AnalysisResultCard } from "@/components/image-analysis/AnalysisResultCard";

function ImageAnalysisPageContent() {
  const { user } = useAuth();
  const { result, isLoading, analyse, reset } = useImageAnalysis();
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileSelected = useCallback(
    (file: File) => {
      const url = URL.createObjectURL(file);
      setPreview(url);
      if (user) analyse(file, user.id);
    },
    [user, analyse]
  );

  function handleReset() {
    reset();
    if (preview) {
      URL.revokeObjectURL(preview);
      setPreview(null);
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Food Image Analysis</h1>
          <p className="text-gray-400 text-sm mt-1">
            Upload a food photo — AI identifies items, estimates calories, and suggests swaps
          </p>
        </div>
        {result && (
          <button onClick={handleReset} className="btn-secondary flex items-center gap-2 text-sm">
            <RefreshCw size={14} />
            New Photo
          </button>
        )}
      </div>

      {/* Upload zone */}
      <ImageDropzone
        onFileSelected={handleFileSelected}
        isLoading={isLoading}
        preview={preview}
        onClear={handleReset}
      />

      {/* Results */}
      {result && <AnalysisResultCard result={result} />}
    </div>
  );
}

export default function ImageAnalysisPage() {
  return (
    <ProtectedRoute>
      <ImageAnalysisPageContent />
    </ProtectedRoute>
  );
}
