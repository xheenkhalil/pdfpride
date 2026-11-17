import { ToolDefinition, UploadedFileMeta, JobState } from "@/types";

const API_BASE_URL =
  typeof window === "undefined"
    ? (process.env.INTERNAL_API_URL || "http://api:8000/api/v1")
    : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1");

export class ApiClient {
  static async getTools(): Promise<ToolDefinition[]> {
    const res = await fetch(`${API_BASE_URL}/tools`, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error("Failed to load tools registry from server.");
    return res.json();
  }

  static async getToolBySlug(slug: string): Promise<ToolDefinition> {
    const res = await fetch(`${API_BASE_URL}/tools/${slug}`, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error(`Tool '${slug}' not found.`);
    return res.json();
  }

  static async uploadFile(file: File): Promise<UploadedFileMeta> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE_URL}/files/upload/direct`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "File upload failed on server.");
    }
    return res.json();
  }

  static async createJob(operation: string, inputFileKeys: string[], options: Record<string, any> = {}): Promise<JobState> {
    const res = await fetch(`${API_BASE_URL}/jobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        operation,
        input_file_ids: inputFileKeys,
        options,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to create processing job on server.");
    }
    return res.json();
  }

  static async pollJob(jobId: string): Promise<JobState> {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to check job progress.");
    return res.json();
  }

  static getDownloadUrl(storageKey: string): string {
    return `${API_BASE_URL}/files/download/${storageKey}`;
  }
}
