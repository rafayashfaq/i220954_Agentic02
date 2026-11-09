import React, { useState } from 'react';
import { ClaimEvidence } from '../lib/api/client';

interface EvidenceHoverProps {
  claim: ClaimEvidence;
}

export const EvidenceHover: React.FC<EvidenceHoverProps> = ({ claim }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isPinned, setIsPinned] = useState(false);

  const statusColors = {
    supported: 'border-b-2 border-emerald-500/80 hover:bg-emerald-500/10 text-emerald-100',
    partly_supported: 'border-b-2 border-amber-500/80 hover:bg-amber-500/10 text-amber-100',
    unsupported: 'border-b-2 border-rose-500/80 hover:bg-rose-500/10 text-rose-100'
  };

  const showTooltip = isHovered || isPinned;

  return (
    <span
      className="relative inline-block my-0.5 cursor-pointer cursor-help"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => setIsPinned((prev) => !prev)}
      title="Click or hover to inspect cited portfolio evidence"
    >
      <span className={`transition-colors rounded px-1 py-0.5 ${statusColors[claim.status]} ${isPinned ? 'ring-1 ring-emerald-400 bg-emerald-500/20' : ''}`}>
        {claim.claim_text}
      </span>

      {showTooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-80 p-3.5 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 text-left text-xs animate-fadeIn">
          <div className="flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
            <span className="font-semibold text-emerald-400 font-mono">
              [{claim.evidence_id}]
            </span>
            <div className="flex items-center gap-1.5">
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                claim.status === 'supported' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
              }`}>
                {claim.status.replace('_', ' ')}
              </span>
              {isPinned && <span className="text-[10px] text-slate-400 font-mono">(pinned)</span>}
            </div>
          </div>

          <p className="font-medium text-slate-200 mb-1">{claim.evidence_title}</p>
          <p className="text-slate-400 mb-2 leading-relaxed">{claim.evidence_summary}</p>

          <div className="pt-1.5 border-t border-slate-800/80 text-[11px] text-emerald-400/90 font-medium flex items-center gap-1">
            <span>✓ Verified Outcome:</span>
            <span>{claim.proven_outcome}</span>
          </div>
        </div>
      )}
    </span>
  );
};

