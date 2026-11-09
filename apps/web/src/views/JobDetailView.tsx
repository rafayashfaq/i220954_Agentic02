import React, { useState, useEffect } from 'react';
import { JobDetailResponse, api } from '../lib/api/client';

interface JobDetailViewProps {
  jobId: string;
  onBack: () => void;
  onOpenStudio: (jobId: string) => void;
  onStartStream: (jobId: string) => void;
}

export const JobDetailView: React.FC<JobDetailViewProps> = ({
  jobId,
  onBack,
  onOpenStudio,
  onStartStream
}) => {
  const [detail, setDetail] = useState<JobDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const res = await api.getJobDetail(jobId);
        setDetail(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDetail();
  }, [jobId]);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center text-slate-500 animate-pulse">
        Loading Job Analysis and Evidence Matrix...
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center">
        <h2 className="text-lg font-bold text-slate-200">Job Not Found</h2>
        <button onClick={onBack} className="mt-3 text-xs text-emerald-400 underline">← Return to Inbox</button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 animate-fadeIn">
      {/* Header Bar */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="text-xs font-semibold text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors"
        >
          ← Back to Job Feed
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onStartStream(jobId)}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-1.5 transition-colors"
          >
            <span>⚡ Run Live Agent Stream</span>
          </button>

          <button
            onClick={() => onOpenStudio(jobId)}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 transition-all"
          >
            Open Proposal Studio →
          </button>
        </div>
      </div>

      {/* Main Job Overview Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl mb-6">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
            detail.recommended_action === 'bid'
              ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
              : 'bg-rose-500/15 text-rose-300 border border-rose-500/30'
          }`}>
            {detail.recommended_action === 'bid' ? '✓ Recommended Bid' : '✕ Recommended Skip'}
          </span>

          <span className="px-2.5 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300">
            Fit: <strong className="text-emerald-400">{Math.round(detail.fit_score * 100)}%</strong>
          </span>

          <span className="px-2.5 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300">
            Risk: <strong className={detail.risk_score > 0.4 ? 'text-rose-400' : 'text-slate-400'}>{Math.round(detail.risk_score * 100)}%</strong>
          </span>

          <span className="text-xs font-mono text-slate-400">⚡ {detail.connects_cost} Connects</span>
        </div>

        <h1 className="text-2xl font-bold text-white mb-3">{detail.title}</h1>
        <p className="text-sm text-slate-300 leading-relaxed mb-6">{detail.description}</p>

        {/* Deliverables & Budget Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-6 border-t border-slate-800">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Extracted Deliverables</h4>
            <ul className="space-y-1.5 text-xs text-slate-300">
              {detail.deliverables.map((d, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{d}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Pricing Strategy</h4>
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 text-xs">
              <div className="flex justify-between items-center mb-1">
                <span className="text-slate-400">Proposed Contract Bid:</span>
                <span className="font-mono text-emerald-400 font-bold text-sm">${detail.proposed_bid}</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-slate-400">Client Ceiling:</span>
                <span className="font-mono text-slate-300">${detail.budget_max}</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal border-t border-slate-800/80 pt-2">
                {detail.price_rationale}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Requirement-to-Evidence Matrix */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>📋 Requirement-to-Evidence Matrix</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Every job deliverable is mapped to verified portfolio case studies and measurable outcomes before drafting.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Job Requirement</th>
                <th className="py-2.5 px-3">Cited Portfolio Evidence</th>
                <th className="py-2.5 px-3">Measured Outcome</th>
                <th className="py-2.5 px-3">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70 text-slate-300">
              {detail.requirement_evidence_matrix.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-950/40 transition-colors">
                  <td className="py-3 px-3 font-medium text-slate-100">{row.requirement}</td>
                  <td className="py-3 px-3">
                    <span className="font-mono text-emerald-400 font-bold mr-1">[{row.evidence_id}]</span>
                    <span>{row.evidence_title}</span>
                  </td>
                  <td className="py-3 px-3 text-slate-400">{row.proven_outcome}</td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-bold text-[10px]">
                      {row.confidence}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

