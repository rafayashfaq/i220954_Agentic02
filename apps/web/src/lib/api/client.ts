/**
 * Strongly-Typed TypeScript API Client generated from FastAPI OpenAPI Schema.
 * Do not hand-edit. Generated from apps/api/openapi.json.
 */

export interface UserProfile {
  user_id: string;
  persona_key: string;
  display_name: string;
  headline: string;
  hourly_rate: number;
  min_budget: number;
  weekly_connects_budget: number;
  marketplace_mode: string;
}

export interface OnboardingRequest {
  persona_key: string;
  display_name: string;
  hourly_rate: number;
  min_budget: number;
  weekly_connects_budget: number;
  marketplace_mode: string;
}

export interface JobSummary {
  job_id: string;
  title: string;
  description: string;
  required_skills: string[];
  budget_min: number;
  budget_max: number;
  connects_cost: number;
  fit_score: number;
  risk_score: number;
  recommended_action: 'bid' | 'skip' | 'watch';
  warning_signals: string[];
  has_injection: boolean;
}

export interface RequirementEvidenceItem {
  requirement: string;
  evidence_id: string;
  evidence_title: string;
  proven_outcome: string;
  confidence: string;
}

export interface JobDetailResponse {
  job_id: string;
  title: string;
  description: string;
  deliverables: string[];
  required_skills: string[];
  implied_skills: string[];
  budget_min: number;
  budget_max: number;
  connects_cost: number;
  fit_score: number;
  risk_score: number;
  recommended_action: string;
  bid_or_skip_reason: string;
  price_rationale: string;
  proposed_bid: number;
  warning_signals: string[];
  requirement_evidence_matrix: RequirementEvidenceItem[];
}

export interface ClaimEvidence {
  claim_text: string;
  status: 'supported' | 'partly_supported' | 'unsupported';
  evidence_id: string;
  evidence_title: string;
  evidence_summary: string;
  proven_outcome: string;
}

export interface DryRunPreview {
  draft_id: string;
  job_id: string;
  bid_amount: number;
  connects_required: number;
  user_balance_after: number;
  cover_letter_preview: string;
  evidence_ids: string[];
  dry_run: boolean;
  ready_for_submission: boolean;
}

export interface ProposalStudioResponse {
  thread_id: string;
  job_id: string;
  cover_letter: string;
  claims_with_evidence: ClaimEvidence[];
  screening_answers: string[];
  critic_feedback: string;
  compliance_explanation: string;
  is_compliant: boolean;
  dry_run_preview: DryRunPreview;
  approval_status: string;
}

export interface ApprovalActionRequest {
  thread_id: string;
  action: 'approved' | 'edited' | 'rejected';
  edited_text?: string;
  reason?: string;
}

export interface MessageItem {
  sender: 'client' | 'freelancer';
  body: string;
  timestamp: string;
  proposed_slots?: string[];
}

export interface MessageThread {
  thread_id: string;
  client_id: string;
  messages: MessageItem[];
  suggested_reply?: string;
  suggested_interview_slots: string[];
  status: string;
}

export interface PipelineCard {
  card_id: string;
  job_id: string;
  title: string;
  client_id: string;
  stage: 'drafted' | 'submitted' | 'viewed' | 'replied' | 'interview' | 'hired' | 'lost';
  bid_amount: number;
  connects_spent: number;
  updated_at: string;
}

export interface AnalyticsOverview {
  total_jobs_scouted: number;
  total_proposals_submitted: number;
  reply_rate_percentage: number;
  hire_rate_percentage: number;
  connects_spent_total: number;
  average_cost_per_proposal_usd: number;
  p95_latency_ms: number;
  rejection_taxonomy: Array<{ category: string; count: number; percentage: number }>;
  outcomes_by_category: Array<{ category: string; reply_rate: number; hire_rate: number; avg_contract: number }>;
}

export interface SettingsResponse {
  autonomy_level: string;
  weekly_budget: number;
  saved_searches: string[];
  connected_accounts: Array<{ platform: string; status: string; type: string }>;
  style_memory_rules: Array<{ id: string; rule: string; learned_from?: string }>;
}

const API_BASE = typeof window !== 'undefined' && window.location.port === '3000'
  ? ''
  : 'http://127.0.0.1:8000';


async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {})
    }
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error [${res.status}]: ${errorText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Auth
  getCurrentUser: () => fetchJson<UserProfile>('/auth/me'),
  onboarding: (data: OnboardingRequest) => fetchJson<UserProfile>('/auth/onboarding', { method: 'POST', body: JSON.stringify(data) }),
  switchPersona: (personaKey: string) => fetchJson<UserProfile>(`/auth/switch_persona/${personaKey}`, { method: 'POST' }),

  // Jobs
  getJobs: (query = '', filterAction = '', limit = 40) => {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (filterAction) params.append('filter_action', filterAction);
    params.append('limit', limit.toString());
    return fetchJson<JobSummary[]>(`/jobs?${params.toString()}`);
  },
  getJobDetail: (jobId: string) => fetchJson<JobDetailResponse>(`/jobs/${jobId}`),

  // Proposals
  getProposalStudio: (jobId: string) => fetchJson<ProposalStudioResponse>(`/proposals/studio/${jobId}`),
  regenerateParagraph: (jobId: string, paragraphIndex: number, currentText: string) =>
    fetchJson<{ paragraph_index: number; regenerated_text: string }>(`/proposals/studio/${jobId}/regenerate_paragraph`, {
      method: 'POST',
      body: JSON.stringify({ paragraph_index: paragraphIndex, current_text: currentText })
    }),

  // Approvals
  getPendingApprovals: () => fetchJson<any[]>('/approvals'),
  executeApproval: (data: ApprovalActionRequest) =>
    fetchJson<{ status: string; submission_id?: string; reason?: string }>('/approvals/action', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Messages
  getThreads: () => fetchJson<MessageThread[]>('/messages'),
  getThread: (threadId: string) => fetchJson<MessageThread>(`/messages/${threadId}`),
  sendReply: (threadId: string, clientId: string, body: string, proposedSlots: string[] = []) =>
    fetchJson<{ status: string }>(`/messages/${threadId}/send`, {
      method: 'POST',
      body: JSON.stringify({ client_id: clientId, body, proposed_slots: proposedSlots })
    }),

  // Analytics
  getAnalytics: () => fetchJson<AnalyticsOverview>('/analytics/overview'),
  getPipeline: () => fetchJson<PipelineCard[]>('/analytics/pipeline'),

  // Settings
  getSettings: () => fetchJson<SettingsResponse>('/settings'),
  updateSettings: (autonomyLevel: string, weeklyBudget: number) =>
    fetchJson<{ status: string }>('/settings', {
      method: 'POST',
      body: JSON.stringify({ autonomy_level: autonomyLevel, weekly_budget: weeklyBudget })
    }),
  deleteMemoryRule: (ruleId: string) => fetchJson<{ status: string }>(`/settings/memory/${ruleId}`, { method: 'DELETE' }),

  // Health
  checkHealth: () => fetchJson<{ status: string; marketplace_mode: string }>('/health')
};

