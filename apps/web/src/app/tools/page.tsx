"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import toolsData from "@/data/tools.json";
import categoriesData from "@/data/categories.json";
import { ToolDefinition } from "@/types";
import { 
  FaLayerGroup, 
  FaScissors, 
  FaCompress, 
  FaImage, 
  FaFilePdf, 
  FaArrowRight,
  FaShieldHalved,
  FaFolder,
  FaGear
} from "@/components/ui/icons";

export default function ToolsDirectoryPage() {
  const allTools = toolsData as any[];
  const categories = categoriesData;

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

  const filteredTools = useMemo(() => {
    return allTools.filter((tool) => {
      const matchesSearch = 
        tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.badge.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.slug.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory = selectedCategory === null || tool.category_id === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [allTools, searchQuery, selectedCategory]);

  // Group tools by category for clean, non-cluttered display
  const groupedTools = useMemo(() => {
    const groups: Record<string, { id: number; name: string; tools: any[] }> = {};
    filteredTools.forEach((tool) => {
      const catName = tool.category;
      if (!groups[catName]) {
        groups[catName] = {
          id: tool.category_id,
          name: catName,
          tools: [],
        };
      }
      groups[catName].tools.push(tool);
    });
    return Object.values(groups);
  }, [filteredTools]);

  const getToolIcon = (slug: string, catId: number) => {
    if (slug.includes("merge")) return FaLayerGroup;
    if (slug.includes("split") || slug.includes("extract")) return FaScissors;
    if (slug.includes("compress")) return FaCompress;
    if (slug.includes("image") || slug.includes("favicon") || catId === 8) return FaImage;
    if (slug.includes("protect") || slug.includes("unlock") || catId === 5) return FaShieldHalved;
    if (slug.includes("workspace") || catId === 15) return FaFolder;
    return FaFilePdf;
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 space-y-12">
      {/* Top Header */}
      <div className="border-4 border-black bg-white p-6 sm:p-10 shadow-flat">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-2 border-black pb-6 mb-6">
          <div>
            <div className="inline-block bg-black text-white px-3 py-1 text-xs font-mono font-black uppercase tracking-widest mb-3">
              ALL 440 TOOLS • 20 CATEGORIES
            </div>
            <h1 className="text-3xl sm:text-5xl font-black uppercase tracking-tight text-black">
              Document Tools Directory
            </h1>
            <p className="mt-2 text-xs font-mono uppercase text-neutral-600">
              Browse, search, and launch any of our 440 document tools instantly.
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono font-bold text-black shrink-0">
            <div className="border-2 border-black px-4 py-2 bg-neutral-100">
              <span className="text-neutral-500">AVAILABLE:</span> {filteredTools.length}
            </div>
            <div className="border-2 border-black px-4 py-2 bg-neutral-100">
              <span className="text-neutral-500">CATEGORIES:</span> {categories.length}
            </div>
          </div>
        </div>

        {/* Real-time Search Box */}
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="SEARCH TOOLS BY NAME, BADGE (E.G. #001, #073), OR FORMAT..."
            className="w-full border-2 border-black bg-white px-5 py-3 text-xs sm:text-sm font-mono font-bold text-black uppercase tracking-wider placeholder:text-neutral-400 focus:outline-none focus:bg-neutral-50 shadow-flat"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-4 top-3 text-xs font-mono font-bold text-major-red hover:underline uppercase"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Category Filter Chips Bar */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs font-mono font-black uppercase tracking-widest text-black">
          <span>Filter by Category</span>
          {selectedCategory !== null && (
            <button
              onClick={() => setSelectedCategory(null)}
              className="text-major-red hover:underline"
            >
              Show All Disciplines
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`border-2 border-black px-3.5 py-1.5 text-xs font-mono font-bold uppercase transition-all ${
              selectedCategory === null
                ? "bg-black text-white shadow-flat"
                : "bg-white text-black hover:bg-neutral-100"
            }`}
          >
            All Disciplines ({allTools.length})
          </button>
          {categories.slice(0, 12).map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(selectedCategory === cat.id ? null : cat.id)}
              className={`border-2 border-black px-3 py-1.5 text-xs font-mono font-bold uppercase transition-all ${
                selectedCategory === cat.id
                  ? "bg-major-red text-white border-major-red shadow-flat"
                  : "bg-white text-black hover:bg-neutral-100"
              }`}
            >
              {String(cat.id).padStart(2, "0")}. {cat.name}
            </button>
          ))}
        </div>
      </div>

      {/* Clean Grouped Sections (Prevents Dirty/Crowded Layout) */}
      <div className="space-y-16">
        {groupedTools.map((group) => (
          <section key={group.name} className="space-y-6">
            <div className="border-b-4 border-black pb-3 flex items-baseline justify-between">
              <div className="flex items-center gap-3">
                <span className="bg-black text-white px-2.5 py-0.5 text-xs font-mono font-black">
                  {String(group.id).padStart(2, "0")}
                </span>
                <h2 className="text-xl sm:text-2xl font-black uppercase tracking-tight text-black">
                  {group.name}
                </h2>
              </div>
              <span className="text-xs font-mono font-bold text-neutral-600">
                {group.tools.length} TOOLS
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {group.tools.map((tool) => {
                const Icon = getToolIcon(tool.slug, tool.category_id);
                const isSpecial = tool.slug === "image-to-favicon" || tool.badge === "WEB-DEV";

                return (
                  <Link
                    key={tool.id}
                    href={`/tools/${tool.slug}`}
                    className={`group flex flex-col justify-between border-2 border-black bg-white p-6 shadow-flat transition-all ${
                      isSpecial 
                        ? "border-major-blue hover:shadow-flat" 
                        : "hover:border-major-red hover:shadow-flatHover"
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <div className={`flex h-10 w-10 items-center justify-center text-white ${
                          isSpecial ? "bg-major-blue" : "bg-black group-hover:bg-major-red"
                        } transition-colors`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <span className={`border border-black px-2 py-0.5 text-[10px] font-mono font-black uppercase ${
                          isSpecial ? "bg-major-blue text-white" : "bg-neutral-100 text-black"
                        }`}>
                          {tool.badge}
                        </span>
                      </div>

                      <h3 className="text-base font-black uppercase tracking-tight text-black group-hover:text-major-red transition-colors">
                        {tool.name}
                      </h3>
                      <p className="mt-2 text-xs text-neutral-700 font-medium leading-relaxed">
                        {tool.description}
                      </p>
                    </div>

                    <div className="mt-6 pt-3 border-t-2 border-neutral-100 flex items-center justify-between text-xs font-black uppercase tracking-wider text-black">
                      <span className="text-[10px] font-mono text-neutral-500 uppercase">
                        {tool.accepted_extensions.slice(0, 3).join(" ")}
                      </span>
                      <span className="flex items-center gap-1.5 group-hover:translate-x-1 transition-transform">
                        Launch <FaArrowRight className="h-3 w-3" />
                      </span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </section>
        ))}

        {groupedTools.length === 0 && (
          <div className="border-2 border-black bg-white p-12 text-center shadow-flat space-y-4">
            <h3 className="text-lg font-black uppercase text-black">No Operations Found</h3>
            <p className="text-xs font-mono text-neutral-600">
              No registered tool matched your query "{searchQuery}".
            </p>
            <button
              onClick={() => {
                setSearchQuery("");
                setSelectedCategory(null);
              }}
              className="border-2 border-black bg-black px-4 py-2 text-xs font-black uppercase text-white hover:bg-major-red transition-colors"
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
