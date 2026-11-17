export interface ToolDefinition {
  id: string;
  number?: number;
  slug: string;
  name: string;
  category: string;
  category_id?: number;
  description: string;
  icon: string;
  badge?: string;
  accepted_mimes: string[];
  accepted_extensions: string[];
  min_files: number;
  max_files: number;
  operation: string;
  is_featured: boolean;
  options_schema: {
    type: string;
    properties: Record<string, any>;
  };
}

export interface UploadedFileMeta {
  id: string;
  original_name: string;
  storage_key: string;
  mime_type: string;
  extension: string;
  size_bytes: number;
  checksum_sha256: string;
  download_url?: string;
}

export interface OutputFileInfo {
  original_name: string;
  storage_key: string;
  size_bytes: number;
  checksum_sha256: string;
  download_url: string;
}

export interface JobState {
  id: string;
  operation: string;
  status: "QUEUED" | "PROCESSING" | "VALIDATING" | "COMPLETED" | "FAILED" | "CANCELLED";
  progress: number;
  stage_message: string;
  options: Record<string, any>;
  error_message?: string;
  output_files: OutputFileInfo[];
  created_at?: string;
  completed_at?: string;
}
