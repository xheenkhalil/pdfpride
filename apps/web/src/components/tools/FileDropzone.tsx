"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { FaCloudArrowUp, FaFilePdf, FaXmark, FaCircleExclamation } from "@/components/ui/icons";

interface FileDropzoneProps {
  acceptedExtensions: string[];
  acceptedMimes?: string[];
  maxFiles: number;
  files: File[];
  onFilesChange: (files: File[]) => void;
  disabled?: boolean;
}

export function FileDropzone({
  acceptedExtensions,
  acceptedMimes = [],
  maxFiles,
  files,
  onFilesChange,
  disabled = false,
}: FileDropzoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const normalizedExtensions = acceptedExtensions.map((e) => e.toLowerCase());
  const acceptString = Array.from(new Set([...acceptedExtensions, ...acceptedMimes])).join(",");

  const validateAndAdd = (newFiles: FileList | null) => {
    if (!newFiles || newFiles.length === 0) return;
    setError(null);

    const validFiles: File[] = [];
    for (let i = 0; i < newFiles.length; i++) {
      const file = newFiles[i];
      const ext = `.${file.name.split(".").pop()?.toLowerCase()}`;
      if (normalizedExtensions.length > 0 && !normalizedExtensions.includes(ext) && !normalizedExtensions.includes(".*") && !normalizedExtensions.includes("*/*")) {
        setError(`Invalid format: ${file.name}. Allowed: ${acceptedExtensions.join(", ")}`);
        continue;
      }
      validFiles.push(file);
    }

    const merged = maxFiles === 1 ? validFiles.slice(0, 1) : [...files, ...validFiles].slice(0, maxFiles);
    onFilesChange(merged);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (disabled) return;
    validateAndAdd(e.dataTransfer.files);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    validateAndAdd(e.target.files);
    if (inputRef.current) inputRef.current.value = "";
  };

  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  return (
    <div className="w-full space-y-4">
      {/* Flat Drop Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => {
          if (!disabled) inputRef.current?.click();
        }}
        className={`relative flex flex-col items-center justify-center border-2 border-black p-8 sm:p-12 text-center cursor-pointer transition-all ${
          disabled
            ? "bg-neutral-100 cursor-not-allowed opacity-50"
            : isDragOver
            ? "bg-neutral-100 border-major-red"
            : "bg-white hover:bg-neutral-50 shadow-flat hover:shadow-flatHover"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple={maxFiles > 1}
          accept={acceptString}
          onChange={handleFileChange}
          disabled={disabled}
          className="hidden"
        />

        <div className="flex h-12 w-12 items-center justify-center bg-black text-white mb-4">
          <FaCloudArrowUp className="h-6 w-6" />
        </div>

        <h3 className="text-base font-black uppercase tracking-wider text-black">
          Select Documents or Drag & Drop Here
        </h3>
        <p className="mt-1 text-xs font-mono text-neutral-600">
          FORMATS: {acceptedExtensions.join("  ").toUpperCase()} (MAX 100 MB PER FILE)
        </p>

        <button
          type="button"
          disabled={disabled}
          className="mt-6 inline-flex items-center border-2 border-black bg-major-red px-5 py-2 text-xs font-black uppercase tracking-widest text-white shadow-flat hover:bg-black transition-colors"
        >
          Browse Files
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 border-2 border-major-red bg-white p-3 text-xs font-bold text-major-red shadow-flatRed">
          <FaCircleExclamation className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Selected Files Flat Table */}
      {files.length > 0 && (
        <div className="border-2 border-black bg-white shadow-flat">
          <div className="px-4 py-2 bg-black text-white text-[11px] font-black uppercase tracking-widest flex justify-between">
            <span>Selected Files ({files.length})</span>
            <span>Size</span>
          </div>
          <div className="divide-y-2 divide-neutral-100">
            {files.map((file, idx) => (
              <div key={idx} className="flex items-center justify-between px-4 py-3 text-xs">
                <div className="flex items-center gap-3 min-w-0 pr-4">
                  <div className="p-1 bg-black text-white shrink-0">
                    <FaFilePdf className="h-3.5 w-3.5" />
                  </div>
                  <span className="font-bold text-black truncate">{file.name}</span>
                </div>
                <div className="flex items-center gap-4 shrink-0">
                  <span className="text-neutral-600 font-mono text-xs">{formatSize(file.size)}</span>
                  {!disabled && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeFile(idx);
                      }}
                      className="border border-black p-1 text-black hover:bg-major-red hover:text-white hover:border-major-red transition-colors"
                    >
                      <FaXmark className="h-3 w-3" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
