"use client";

import { useState, useEffect } from "react";
import { ToolDefinition, JobState } from "@/types";
import { FileDropzone } from "@/components/tools/FileDropzone";
import { JobProgressBar } from "@/components/tools/JobProgressBar";
import { ApiClient } from "@/lib/api-client";
import { 
  FaDownload, 
  FaRotate, 
  FaRotateLeft,
  FaRotateRight,
  FaArrowRight, 
  FaGear, 
  FaCheck,
  FaClone,
  FaSliders
} from "@/components/ui/icons";

interface UniversalToolRunnerProps {
  tool: ToolDefinition;
}

export function UniversalToolRunner({ tool }: UniversalToolRunnerProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [options, setOptions] = useState<Record<string, any>>({});
  const [jobState, setJobState] = useState<JobState | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Initialize default options from tool schema
  useEffect(() => {
    const defaults: Record<string, any> = {};
    const props = tool.options_schema?.properties || {};
    Object.keys(props).forEach((key) => {
      if (props[key].default !== undefined) {
        defaults[key] = props[key].default;
      }
    });
    setOptions(defaults);
  }, [tool]);

  // Polling effect when job is in active state
  useEffect(() => {
    if (!jobState || !["QUEUED", "PROCESSING", "VALIDATING"].includes(jobState.status)) {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await ApiClient.pollJob(jobState.id);
        setJobState(updated);
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [jobState?.id, jobState?.status]);

  const handleStartProcessing = async () => {
    if (files.length < tool.min_files) {
      setErrorMessage(`Please select at least ${tool.min_files} file(s) to continue.`);
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      // Step 1: Upload input files to Server Storage
      const uploadedFileKeys: string[] = [];
      for (const file of files) {
        const meta = await ApiClient.uploadFile(file);
        uploadedFileKeys.push(meta.storage_key);
      }

      // Step 2: Create Processing Job on Server
      const job = await ApiClient.createJob(tool.operation, uploadedFileKeys, options);
      setJobState(job);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to initiate processing job on server.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetTool = () => {
    setFiles([]);
    setJobState(null);
    setErrorMessage(null);
  };

  const isCompleted = jobState?.status === "COMPLETED";
  const isProcessing = jobState && ["QUEUED", "PROCESSING", "VALIDATING"].includes(jobState.status);

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      {/* Header Banner */}
      <div className="border-b-2 border-black pb-8 mb-8 text-left">
        <div className="flex items-center gap-3 mb-2">
          <span className="bg-black text-white px-2.5 py-0.5 text-[11px] font-black uppercase tracking-widest">
            {tool.category}
          </span>
          {tool.badge && (
            <span className="border border-black bg-neutral-100 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider text-black">
              {tool.badge}
            </span>
          )}
        </div>
        <h1 className="text-3xl font-black uppercase tracking-tight text-black sm:text-4xl">
          {tool.name}
        </h1>
        <p className="mt-2 text-sm text-neutral-700 max-w-2xl font-medium">
          {tool.description}
        </p>
      </div>

      <div className="border-2 border-black bg-white p-6 sm:p-10 shadow-flat space-y-8">
        {/* Step 1: File Upload Dropzone */}
        {!isCompleted && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs font-black uppercase tracking-widest text-black border-b border-black pb-2">
              <span>01 / Select Documents</span>
              <span>Min: {tool.min_files} — Max: {tool.max_files}</span>
            </div>

            <FileDropzone
              acceptedExtensions={tool.accepted_extensions}
              acceptedMimes={tool.accepted_mimes}
              maxFiles={tool.max_files}
              files={files}
              onFilesChange={setFiles}
              disabled={isProcessing || isSubmitting}
            />
          </div>
        )}

        {/* Step 2: Dynamic Operation Options */}
        {files.length > 0 && !isCompleted && !isProcessing && (
          <div className="border-t-2 border-black pt-6 space-y-6">
            <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-black">
              <FaGear className="h-3.5 w-3.5 text-black" />
              <span>02 / Processing Parameters & Controls</span>
            </div>

            {/* Specialized UI: Rotate PDF (4 Rotation Cycles & Page Filters) */}
            {tool.operation.includes("rotate") ? (
              <div className="space-y-5 bg-neutral-50 border-2 border-black p-5 shadow-flat">
                <div>
                  <label className="text-xs font-black uppercase tracking-wider text-black block mb-2">
                    Select Rotation Cycle (4 Directions)
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      { id: "right_90", label: "Rotate Right", sub: "90° Clockwise", icon: FaRotateRight },
                      { id: "left_90", label: "Rotate Left", sub: "90° Counter-CW", icon: FaRotateLeft },
                      { id: "flip_180", label: "Flip 180°", sub: "Upside Down", icon: FaRotate },
                      { id: "reset_0", label: "Reset 0°", sub: "Original Angle", icon: FaCheck },
                    ].map((btn) => {
                      const Icon = btn.icon;
                      const active = (options.rotation_type || "right_90") === btn.id;
                      return (
                        <button
                          key={btn.id}
                          type="button"
                          onClick={() => setOptions({ ...options, rotation_type: btn.id })}
                          className={`flex flex-col items-center justify-center p-3 border-2 border-black text-center transition-all ${
                            active
                              ? "bg-major-red text-white shadow-flat"
                              : "bg-white text-black hover:bg-neutral-100"
                          }`}
                        >
                          <Icon className="h-4 w-4 mb-1" />
                          <span className="text-xs font-black uppercase tracking-wider">{btn.label}</span>
                          <span className={`text-[10px] font-mono mt-0.5 ${active ? "text-neutral-100" : "text-neutral-600"}`}>
                            {btn.sub}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="text-xs font-black uppercase tracking-wider text-black block mb-2">
                    Apply Rotation To
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { id: "all", label: "All Pages" },
                      { id: "odd", label: "Odd Pages (1, 3, 5...)" },
                      { id: "even", label: "Even Pages (2, 4, 6...)" },
                      { id: "custom", label: "Custom Range" },
                    ].map((pill) => {
                      const active = (options.page_selection || "all") === pill.id;
                      return (
                        <button
                          key={pill.id}
                          type="button"
                          onClick={() => setOptions({ ...options, page_selection: pill.id })}
                          className={`border-2 border-black px-3.5 py-1.5 text-xs font-black uppercase tracking-wider transition-colors ${
                            active
                              ? "bg-black text-white"
                              : "bg-white text-black hover:bg-neutral-100"
                          }`}
                        >
                          {pill.label}
                        </button>
                      );
                    })}
                  </div>

                  {options.page_selection === "custom" && (
                    <div className="mt-3">
                      <input
                        type="text"
                        value={options.page_range || ""}
                        onChange={(e) => setOptions({ ...options, page_range: e.target.value })}
                        placeholder="Enter pages or ranges (e.g. 1, 3-5, 8)"
                        className="w-full border-2 border-black bg-white px-3.5 py-2 text-xs font-mono font-bold text-black focus:outline-none"
                      />
                    </div>
                  )}
                </div>
              </div>
            ) : tool.operation.includes("compress") ? (
              /* Specialized UI: Compress PDF (Quality Profiles & Target Size Mode) */
              <div className="space-y-5 bg-neutral-50 border-2 border-black p-5 shadow-flat">
                <div>
                  <label className="text-xs font-black uppercase tracking-wider text-black block mb-2">
                    Select Compression Profile
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      { id: "recommended", label: "Recommended", sub: "Balanced (~50% off)" },
                      { id: "extreme", label: "Extreme", sub: "Max (~75% off)" },
                      { id: "low", label: "Low", sub: "High Quality (~25%)" },
                      { id: "target_size", label: "Target Size", sub: "Custom Target" },
                    ].map((lvl) => {
                      const active = (options.compression_mode || "recommended") === lvl.id;
                      return (
                        <button
                          key={lvl.id}
                          type="button"
                          onClick={() => setOptions({ ...options, compression_mode: lvl.id })}
                          className={`flex flex-col items-center justify-center p-3 border-2 border-black text-center transition-all ${
                            active
                              ? "bg-major-red text-white shadow-flat"
                              : "bg-white text-black hover:bg-neutral-100"
                          }`}
                        >
                          <span className="text-xs font-black uppercase tracking-wider">{lvl.label}</span>
                          <span className={`text-[10px] font-mono mt-0.5 ${active ? "text-neutral-100" : "text-neutral-600"}`}>
                            {lvl.sub}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {options.compression_mode === "target_size" && (
                  <div className="border-t border-black pt-4 space-y-2">
                    <label className="text-xs font-black uppercase tracking-wider text-black block">
                      Target File Size (Engine will iteratively scale to fit)
                    </label>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {["500 KB", "1.0 MB", "2.0 MB", "5.0 MB"].map((chip) => (
                        <button
                          key={chip}
                          type="button"
                          onClick={() => setOptions({ ...options, target_size_mb: chip })}
                          className={`border border-black px-2.5 py-1 text-xs font-mono font-bold ${
                            options.target_size_mb === chip ? "bg-black text-white" : "bg-white text-black hover:bg-neutral-100"
                          }`}
                        >
                          {chip}
                        </button>
                      ))}
                    </div>
                    <input
                      type="text"
                      value={options.target_size_mb || "1.0 MB"}
                      onChange={(e) => setOptions({ ...options, target_size_mb: e.target.value })}
                      placeholder="e.g. 1.5 MB or 500 KB"
                      className="w-full border-2 border-black bg-white px-3.5 py-2 text-xs font-mono font-bold text-black focus:outline-none"
                    />
                  </div>
                )}
              </div>
            ) : tool.operation.includes("duplicate") ? (
              /* Specialized UI: Duplicate PDF Pages */
              <div className="space-y-4 bg-neutral-50 border-2 border-black p-5 shadow-flat">
                <div>
                  <label className="text-xs font-black uppercase tracking-wider text-black block mb-2">
                    Number of Copies per Page
                  </label>
                  <div className="flex gap-2">
                    {["2", "3", "4", "5"].map((count) => {
                      const active = (options.copies || "2") === count;
                      return (
                        <button
                          key={count}
                          type="button"
                          onClick={() => setOptions({ ...options, copies: count })}
                          className={`border-2 border-black px-4 py-2 text-xs font-black ${
                            active ? "bg-major-red text-white" : "bg-white text-black hover:bg-neutral-100"
                          }`}
                        >
                          {count}x Copies
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="text-xs font-black uppercase tracking-wider text-black block mb-2">
                    Duplication Placement
                  </label>
                  <div className="flex gap-2">
                    {[
                      { id: "consecutive", label: "Consecutive (P1, P1, P2, P2)" },
                      { id: "end", label: "End of Document (P1, P2, P1, P2)" },
                    ].map((p) => {
                      const active = (options.placement || "consecutive") === p.id;
                      return (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => setOptions({ ...options, placement: p.id })}
                          className={`border-2 border-black px-3.5 py-1.5 text-xs font-bold ${
                            active ? "bg-black text-white" : "bg-white text-black hover:bg-neutral-100"
                          }`}
                        >
                          {p.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : tool.operation.includes("reverse") ? (
              /* Specialized UI: Reverse PDF Pages */
              <div className="bg-neutral-50 border-2 border-black p-5 shadow-flat">
                <p className="text-xs font-black uppercase tracking-wider text-black">
                  Page Order Reversal Active
                </p>
                <p className="text-xs font-medium text-neutral-600 mt-1">
                  Document pages will be inverted in reverse sequence (from the last page to the first page: Page N → Page 1).
                </p>
              </div>
            ) : (
              /* Generic Options Schema Grid */
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {Object.entries(tool.options_schema?.properties || {}).map(([key, schema]: [string, any]) => (
                  <div key={key} className="space-y-1.5">
                    <label className="text-xs font-black uppercase tracking-wider text-black">
                      {schema.title || key}
                    </label>
                    {schema.enum ? (
                      <select
                        value={options[key] || schema.default}
                        onChange={(e) => setOptions({ ...options, [key]: e.target.value })}
                        className="w-full border-2 border-black bg-white px-3.5 py-2.5 text-xs font-bold uppercase tracking-wider text-black focus:outline-none focus:bg-neutral-50"
                      >
                        {schema.enum.map((opt: string) => (
                          <option key={opt} value={opt}>
                            {opt.toUpperCase()}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={options[key] || ""}
                        onChange={(e) => setOptions({ ...options, [key]: e.target.value })}
                        placeholder={schema.default || ""}
                        className="w-full border-2 border-black bg-white px-3.5 py-2.5 text-xs font-bold text-black focus:outline-none focus:bg-neutral-50 font-mono"
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 3: Trigger Button & Active Job Progress */}
        {files.length >= tool.min_files && !isCompleted && !isProcessing && (
          <div className="pt-2">
            <button
              onClick={handleStartProcessing}
              disabled={isSubmitting}
              className="w-full inline-flex items-center justify-center gap-3 border-2 border-black bg-major-red py-4 px-6 text-xs font-black uppercase tracking-widest text-white shadow-flat hover:bg-black transition-colors"
            >
              <span>Execute Transformation</span>
              <FaArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        )}

        {/* Active Progress State */}
        {jobState && !isCompleted && (
          <JobProgressBar
            progress={jobState.progress}
            stageMessage={jobState.stage_message}
            status={jobState.status}
            errorMessage={jobState.error_message}
          />
        )}

        {/* Step 4: Completion & Download Action Hub */}
        {isCompleted && (
          <div className="text-center py-6 space-y-6">
            <div className="mx-auto flex h-14 w-14 items-center justify-center bg-black text-white">
              <FaCheck className="h-6 w-6 text-white" />
            </div>

            <div>
              <h2 className="text-2xl font-black uppercase tracking-tight text-black">
                Processing Finished
              </h2>
              <p className="mt-1 text-xs font-medium text-neutral-600">
                Transformed securely inside server worker container and validated for structural compliance.
              </p>
            </div>

            {/* Generated Output Files */}
            <div className="space-y-3 max-w-md mx-auto text-left">
              {jobState.output_files.map((file, idx) => (
                <div key={idx} className="flex items-center justify-between border-2 border-black bg-white p-4 shadow-flat">
                  <div className="truncate pr-4">
                    <p className="text-xs font-black text-black uppercase truncate">{file.original_name}</p>
                    <p className="text-[11px] font-mono text-neutral-600 mt-0.5">
                      {(file.size_bytes / 1024).toFixed(1)} KB • SHA: {file.checksum_sha256.substring(0, 10)}
                    </p>
                  </div>

                  <a
                    href={ApiClient.getDownloadUrl(file.storage_key)}
                    download={file.original_name}
                    className="inline-flex items-center gap-1.5 border-2 border-black bg-black px-4 py-2 text-xs font-black uppercase tracking-widest text-white hover:bg-major-red hover:border-major-red transition-colors shrink-0"
                  >
                    <FaDownload className="h-3 w-3" />
                    Download
                  </a>
                </div>
              ))}
            </div>

            <div className="pt-4 flex items-center justify-center gap-4">
              <button
                onClick={resetTool}
                className="inline-flex items-center gap-2 text-xs font-black uppercase tracking-widest text-black hover:text-major-red transition-colors"
              >
                <FaRotate className="h-3.5 w-3.5" />
                Process Another Document
              </button>
            </div>
          </div>
        )}

        {errorMessage && (
          <div className="border-2 border-major-red bg-white p-4 text-xs font-bold text-major-red shadow-flatRed">
            {errorMessage}
          </div>
        )}
      </div>

      {/* Privacy Note */}
      <div className="mt-8 text-center text-xs font-mono uppercase tracking-wider text-neutral-500">
        100% Private • Files are cleaned up automatically after download
      </div>
    </div>
  );
}
