import { ApiClient } from "@/lib/api-client";
import { UniversalToolRunner } from "@/components/tools/UniversalToolRunner";
import toolsData from "@/data/tools.json";
import { ToolDefinition } from "@/types";
import { notFound } from "next/navigation";

interface ToolPageProps {
  params: {
    slug: string;
  };
}

export function generateStaticParams() {
  return (toolsData as ToolDefinition[]).map((t) => ({
    slug: t.slug,
  }));
}

export default async function ToolPage({ params }: ToolPageProps) {
  let tool: ToolDefinition | undefined;

  try {
    tool = await ApiClient.getToolBySlug(params.slug);
  } catch (err) {
    // Fallback to bundled registry during build or offline dev
    tool = (toolsData as ToolDefinition[]).find((t) => t.slug === params.slug);
  }

  if (!tool) {
    notFound();
  }

  return <UniversalToolRunner tool={tool} />;
}
