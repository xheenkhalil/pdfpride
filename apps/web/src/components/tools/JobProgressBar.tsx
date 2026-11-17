import { FaSpinner, FaCheck, FaCircleExclamation } from "@/components/ui/icons";

interface JobProgressBarProps {
  progress: number;
  stageMessage: string;
  status: "QUEUED" | "PROCESSING" | "VALIDATING" | "COMPLETED" | "FAILED" | "CANCELLED";
  errorMessage?: string;
}

export function JobProgressBar({ progress, stageMessage, status, errorMessage }: JobProgressBarProps) {
  const isFailed = status === "FAILED";
  const isCompleted = status === "COMPLETED";

  return (
    <div className="w-full border-2 border-black bg-white p-6 shadow-flat">
      <div className="flex items-center justify-between mb-3 border-b-2 border-black pb-3">
        <div className="flex items-center gap-2.5">
          {isCompleted ? (
            <div className="flex h-6 w-6 items-center justify-center bg-black text-white">
              <FaCheck className="h-3.5 w-3.5" />
            </div>
          ) : isFailed ? (
            <div className="flex h-6 w-6 items-center justify-center bg-major-red text-white">
              <FaCircleExclamation className="h-3.5 w-3.5" />
            </div>
          ) : (
            <div className="flex h-6 w-6 items-center justify-center bg-black text-white">
              <FaSpinner className="h-3.5 w-3.5" />
            </div>
          )}
          <span className="text-xs font-black uppercase tracking-widest text-black">
            {isFailed ? "Operation Failed" : isCompleted ? "Operation Complete" : "Processing Document..."}
          </span>
        </div>
        <span className="text-sm font-mono font-black text-black">
          {isFailed ? "ERR" : `${Math.min(100, Math.max(0, progress))}%`}
        </span>
      </div>

      {/* Flat Progress Track */}
      <div className="h-4 w-full border-2 border-black bg-neutral-100 p-0.5">
        <div
          className={`h-full transition-all duration-200 ${
            isFailed
              ? "bg-major-red"
              : isCompleted
              ? "bg-black"
              : "bg-major-blue"
          }`}
          style={{ width: `${isFailed ? 100 : Math.min(100, Math.max(5, progress))}%` }}
        />
      </div>

      <div className="mt-4 flex items-center justify-between text-xs font-mono font-bold text-neutral-800">
        <span>{isFailed ? errorMessage || "Error processing document. Please try again." : stageMessage}</span>
        <span className="bg-black text-white px-2 py-0.5 text-[10px] uppercase tracking-wider">{status}</span>
      </div>
    </div>
  );
}
