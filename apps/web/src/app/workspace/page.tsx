"use client";

import { useState } from "react";
import { 
  FaFilePdf, 
  FaFolder, 
  FaStar, 
  FaTrashCan, 
  FaDownload, 
  FaShieldHalved 
} from "@/components/ui/icons";

export default function WorkspacePage() {
  const [activeTab, setActiveTab] = useState<"files" | "history">("files");

  const sampleFiles = [
    {
      id: "f-1",
      name: "Q3_Financial_Report_Compressed.pdf",
      size: "2.4 MB",
      date: "2026-11-16",
      starred: true,
      operation: "Compressed (64% savings)",
    },
    {
      id: "f-2",
      name: "Legal_Contracts_Merged.pdf",
      size: "8.1 MB",
      date: "2026-11-15",
      starred: false,
      operation: "Merged (4 documents)",
    },
    {
      id: "f-3",
      name: "Product_Catalog_Page_1-10.pdf",
      size: "3.7 MB",
      date: "2026-11-14",
      starred: true,
      operation: "Split (Pages 1-10)",
    },
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 space-y-8">
      {/* Top Banner & Storage Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 border-2 border-black bg-white p-6 sm:p-8 shadow-flat">
        <div>
          <span className="bg-black text-white px-2.5 py-0.5 text-[10px] font-mono font-black uppercase tracking-widest">
            CLOUD WORKSPACE
          </span>
          <h1 className="mt-2 text-2xl font-black uppercase tracking-tight text-black">
            Document Workspace
          </h1>
          <p className="mt-1 text-xs font-mono uppercase text-neutral-600">
            Organize, store, and access your processed files anywhere
          </p>
        </div>

        <div className="w-full sm:w-80 border-2 border-black bg-neutral-50 p-4">
          <div className="flex items-center justify-between text-xs font-black uppercase tracking-wider text-black mb-2">
            <span>Quota Used</span>
            <span className="font-mono">14.2 MB / 2.0 GB</span>
          </div>
          <div className="h-3 w-full border border-black bg-white p-0.5">
            <div className="h-full bg-major-blue" style={{ width: "2%" }} />
          </div>
        </div>
      </div>

      {/* Tabs & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b-2 border-black pb-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("files")}
            className={`border-2 border-black px-4 py-2 text-xs font-black uppercase tracking-wider transition-colors ${
              activeTab === "files"
                ? "bg-black text-white shadow-flat"
                : "bg-white text-black hover:bg-neutral-100"
            }`}
          >
            My Documents
          </button>
          <button
            onClick={() => setActiveTab("history")}
            className={`border-2 border-black px-4 py-2 text-xs font-black uppercase tracking-wider transition-colors ${
              activeTab === "history"
                ? "bg-black text-white shadow-flat"
                : "bg-white text-black hover:bg-neutral-100"
            }`}
          >
            Execution History
          </button>
        </div>

        <div className="w-full sm:w-64">
          <input
            type="text"
            placeholder="FILTER DOCUMENTS..."
            className="w-full border-2 border-black bg-white px-3.5 py-2 text-xs font-mono font-bold text-black focus:outline-none focus:bg-neutral-50 uppercase"
          />
        </div>
      </div>

      {/* Documents Flat Table */}
      <div className="border-2 border-black bg-white shadow-flat overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-black text-white font-black uppercase tracking-widest text-[11px]">
            <tr>
              <th className="px-6 py-3.5">Document File</th>
              <th className="px-6 py-3.5">Operation</th>
              <th className="px-6 py-3.5">Size</th>
              <th className="px-6 py-3.5">Date</th>
              <th className="px-6 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y-2 divide-neutral-100 font-medium">
            {sampleFiles.map((file) => (
              <tr key={file.id} className="hover:bg-neutral-50 transition-colors">
                <td className="px-6 py-4 font-bold text-black flex items-center gap-3">
                  <div className="h-6 w-6 bg-black text-white flex items-center justify-center shrink-0">
                    <FaFilePdf className="h-3.5 w-3.5" />
                  </div>
                  <span className="truncate max-w-xs">{file.name}</span>
                </td>
                <td className="px-6 py-4 text-neutral-800 font-mono text-[11px]">{file.operation}</td>
                <td className="px-6 py-4 text-neutral-600 font-mono text-xs">{file.size}</td>
                <td className="px-6 py-4 text-neutral-600 font-mono text-xs">{file.date}</td>
                <td className="px-6 py-4 text-right space-x-2">
                  <button className="border border-black p-1 text-black hover:bg-black hover:text-white transition-colors" title="Download">
                    <FaDownload className="h-3.5 w-3.5" />
                  </button>
                  <button className="border border-black p-1 text-black hover:bg-major-yellow hover:text-black transition-colors" title="Star">
                    <FaStar className={`h-3.5 w-3.5 ${file.starred ? "text-major-yellow fill-major-yellow" : ""}`} />
                  </button>
                  <button className="border border-black p-1 text-black hover:bg-major-red hover:text-white hover:border-major-red transition-colors" title="Delete">
                    <FaTrashCan className="h-3.5 w-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
