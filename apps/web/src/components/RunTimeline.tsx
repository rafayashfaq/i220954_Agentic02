import React from 'react';

export interface TimelineEvent {
  node: string;
  message: string;
  timestamp?: string;
  status?: 'active' | 'completed' | 'paused' | 'error';
}

interface RunTimelineProps {
  events: TimelineEvent[];
  activeNode: string | null;
  isStreaming: boolean;
}

export const RunTimeline: React.FC<RunTimelineProps> = ({ events, activeNode, isStreaming }) => {
  const nodesOrder = [
    { id: 'scout', label: 'Scout' },
    { id: 'analyst', label: 'Job Analyst (Parallel)' },
    { id: 'risk_assessor', label: 'Risk Assessor (Parallel)' },
    { id: 'fit_matcher', label: 'Fit Matcher (Parallel)' },
    { id: 'decision_node', label: 'Decision Node' },
    { id: 'pricing', label: 'Pricing Strategist' },
    { id: 'writer', label: 'Proposal Writer' },
    { id: 'verifier', label: 'Claim Verifier' },
    { id: 'critic', label: 'Critic Audit' },
    { id: 'compliance', label: 'Compliance Guard' },
    { id: 'prepare_approval', label: 'Approval Gate' },
    { id: 'human_approval', label: 'Human Review' },
    { id: 'submit', label: 'Marketplace Submission' }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
        <div>
          <h3 className="font-semibold text-slate-100 flex items-center gap-2">
            <span>⚡ Live LangGraph Stream</span>
            {isStreaming && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-mono animate-pulse">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                Streaming SSE
              </span>
            )}
          </h3>
          <p className="text-xs text-slate-400">Node-by-node execution streamed in real-time from the bid graph.</p>
        </div>
      </div>

      {/* Progress Track */}
      <div className="space-y-3">
        {events.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">
            Click &quot;Run Live Stream&quot; to execute and trace the multi-agent graph in real-time.
          </div>
        ) : (
          events.map((evt, idx) => {
            const isLatest = idx === events.length - 1;
            const isPaused = evt.node === 'human_approval' || evt.node === 'prepare_approval';

            return (
              <div
                key={idx}
                className={`p-3 rounded-xl border text-xs transition-all flex items-start gap-3 ${
                  isLatest && isStreaming
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200 animate-fadeIn'
                    : isPaused
                    ? 'bg-amber-500/10 border-amber-500/30 text-amber-200'
                    : 'bg-slate-950/60 border-slate-800/80 text-slate-300'
                }`}
              >
                <div className="mt-0.5 font-mono text-emerald-400 font-bold">
                  {idx + 1}.
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="font-bold text-slate-100 uppercase tracking-wider text-[11px] font-mono">
                      {evt.node}
                    </span>
                    {isLatest && isStreaming && (
                      <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono animate-pulse">
                        RUNNING
                      </span>
                    )}
                    {isPaused && (
                      <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-mono">
                        AWAITING APPROVAL
                      </span>
                    )}
                  </div>
                  <p className="text-slate-300 text-xs leading-relaxed">{evt.message}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

