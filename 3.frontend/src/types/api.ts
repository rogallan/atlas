export type SenderType = 'user' | 'assistant' | 'system';

export interface Citation {
  chunk_id: string;
  source_title: string;
  norm_reference?: string;
  section_title?: string;
  source_url_or_path?: string;
  excerpt: string;
  relevance?: number;
}

export interface SimulationPayload {
  type: 'loan' | 'insurance' | 'consortium' | 'tariff';
  data: Record<string, any>;
  disclaimer: string;
}

export interface ActionConfirmationPayload {
  confirmation_token: string;
  customer_id: string;
  category: string;
  title: string;
  description: string;
  summary_for_human: string;
}

export interface ChatMessage {
  id: string;
  sender: SenderType;
  content: string;
  citations?: Citation[];
  simulation?: SimulationPayload;
  action_proposal?: ActionConfirmationPayload;
  timestamp: string;
  is_streaming?: boolean;
  intent?: string;
}

export interface CustomerSummary {
  id: string;
  name: string;
  segment: 'RETAIL' | 'PRIME' | 'PRIVATE' | 'CORPORATE' | 'CORPORATE_SMB' | string;
  monthly_income: number;
  credit_score: number;
  active_account: string;
}

export interface MCPMenuItem {
  id: string;
  mcpName: string;
  port: number;
  icon: string;
  title: string;
  description: string;
  sampleQueries: {
    label: string;
    prompt: string;
    description: string;
  }[];
}
