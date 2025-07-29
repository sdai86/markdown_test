export interface Block {
  id: string;
  type: string;
  content: string;
  raw_content?: string;
  order_index: number;
  level: number;
  parent_id?: string;
  document_id: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TOCItem {
  id: string;
  text: string;
  level: number;
  order_index: number;
}

export interface Document {
  id: string;
  title: string;
  filename?: string;
  total_blocks: number;
  created_at: string;
  updated_at: string;
}

export interface BlocksResponse {
  blocks: Block[];
  total: number;
  offset: number;
  limit: number;
}

export interface PerformanceLog {
  operation: string;
  duration_ms: number;
  timestamp: string;
  metadata: Record<string, any>;
}
