"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import type { FileRejection } from "react-dropzone";
import { Upload, X, Image as ImageIcon, Loader2 } from "lucide-react";
import clsx from "clsx";


interface ImageDropzoneProps {
  onFileSelected: (file: File) => void;
  isLoading: boolean;
  preview: string | null;
  onClear: () => void;
}

const ACCEPTED = { "image/jpeg": [], "image/png": [], "image/webp": [] };
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

export function ImageDropzone({ onFileSelected, isLoading, preview, onClear }: ImageDropzoneProps) {
  const [dragError, setDragError] = useState<string | null>(null);

  const onDrop = useCallback(
    (accepted: File[], rejected: FileRejection[]) => {
      setDragError(null);
      if (rejected.length > 0) {
        const msg = rejected[0]?.errors[0]?.message ?? "Invalid file.";
        setDragError(msg);
        return;
      }
      if (accepted[0]) onFileSelected(accepted[0]);
    },
    [onFileSelected]
  );


  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: MAX_SIZE,
    multiple: false,
    disabled: isLoading,
  });

  if (preview) {
    return (
      <div className="relative rounded-xl overflow-hidden border border-gray-700 bg-gray-900">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={preview} alt="Food preview" className="w-full max-h-64 object-cover" />
        {!isLoading && (
          <button
            onClick={onClear}
            className="absolute top-2 right-2 w-7 h-7 bg-gray-900/80 backdrop-blur rounded-full flex items-center justify-center text-gray-300 hover:text-red-400 transition-colors"
            aria-label="Remove image"
          >
            <X size={14} />
          </button>
        )}
        {isLoading && (
          <div className="absolute inset-0 bg-gray-950/70 backdrop-blur-sm flex items-center justify-center">
            <div className="flex flex-col items-center gap-2 text-white">
              <Loader2 size={32} className="animate-spin text-brand-400" />
              <span className="text-sm">Analysing with IBM Granite…</span>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={clsx(
        "border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center gap-3 cursor-pointer transition-colors",
        isDragActive
          ? "border-brand-400 bg-brand-900/10"
          : "border-gray-700 bg-gray-900/50 hover:border-gray-500 hover:bg-gray-900"
      )}
    >
      <input {...getInputProps()} />
      <div className="w-12 h-12 rounded-xl bg-gray-800 border border-gray-700 flex items-center justify-center">
        {isDragActive ? (
          <ImageIcon size={24} className="text-brand-400" />
        ) : (
          <Upload size={24} className="text-gray-400" />
        )}
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-gray-300">
          {isDragActive ? "Drop your food photo here" : "Drag & drop a food photo"}
        </p>
        <p className="text-xs text-gray-500 mt-1">or click to browse · JPEG, PNG, WebP · max 10 MB</p>
      </div>
      {dragError && <p className="text-xs text-red-400 mt-1">{dragError}</p>}
    </div>
  );
}
