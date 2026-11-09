import React, { useState, useEffect } from 'react';
import { PipelineCard, api } from '../lib/api/client';

interface PipelineViewProps {
  onSelectJob?: (jobId: string) => void;
}

export const PipelineView: React.FC<PipelineViewProps> = ({ onSelectJob }) => {
  const [cards, setCards] = useState<PipelineCard[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const stages: Array<{ id: PipelineCard['stage']; label: string; color: string }> = [
    { id: 'drafted', label: 'Drafted', color: 'border-slate-700' },
    { id: 'submitted', label: 'Submitted', color: 'border-sky-500/40 text-sky-400' },
    { id: 'viewed', label: 'Client Viewed', color: 'border-indigo-500/40 text-indigo-400' },
    { id: 'replied', label: 'Client Replied', color: 'border-amber-500/40 text-amber-400' },
    { id: 'interview', label: 'Interview Hold', color: 'border-purple-500/40 text-purple-400' },
    { id: 'hired', label: 'Contract Won! 🎉', color: 'border-emerald-500/40 text-emerald-400' },
    { id: 'lost', label: 'Closed / Lost', color: 'border-rose-500/40 text-rose-400' },
  ];

  useEffect(() => {
    const fetchPipeline = async () => {
      try {
        const res = await api.getPipeline();
        setCards(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchPipeline();
  }, []);

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 animate-fadeIn">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Proposal & Contract Pipeline</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Full lifecycle tracking: from drafted proposals to client interviews and contract wins.
          </p>
        </div>

        <span className="text-xs font-mono text-emerald-400 font-semibold px-3 py-1 bg-slate-900 border border-slate-800 rounded-xl">
          {cards.filter((c) => c.stage === 'hired').length} Active Contracts Won
        </span>
      </div>

      {isLoading ? (
        <div className="text-center py-20 text-slate-500 text-sm animate-pulse">
          Loading pipeline cards...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-7 gap-3.5 overflow-x-auto pb-4">
          {stages.map((st) => {
            const stageCards = cards.filter((c) => c.stage === st.id);

            return (
              <div key={st.id} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-3 flex flex-col min-w-[200px]">
                {/* Column Header */}
                <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800 text-xs font-bold">
                  <span className={st.color}>{st.label}</span>
                  <span className="text-[11px] font-mono px-1.5 py-0.5 bg-slate-800 rounded text-slate-300">
                    {stageCards.length}
                  </span>
                </div>

                {/* Cards List */}
                <div className="space-y-2.5 flex-1">
                  {stageCards.length === 0 ? (
                    <div className="text-center py-8 text-[11px] text-slate-600">No proposals</div>
                  ) : (
                    stageCards.map((card) => (
                      <div
                        key={card.card_id}
                        onClick={() => onSelectJob && onSelectJob(card.job_id)}
                        title="Click to inspect job detail & evidence matrix"
                        className="bg-slate-950/80 hover:bg-slate-950 border border-slate-800/80 rounded-xl p-3 text-xs shadow-sm hover:border-emerald-500/50 hover:shadow-lg transition-all cursor-pointer group"
                      >
                        <h4 className="font-semibold text-slate-200 group-hover:text-emerald-400 transition-colors line-clamp-2 mb-1.5">
                          {card.title}
                        </h4>
                        <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono">
                          <span>${card.bid_amount}</span>
                          <span className="text-slate-500">⚡ {card.connects_spent} conn</span>
                        </div>
                        <div className="mt-2 text-[10px] text-slate-500 truncate">
                          Client: {card.client_id}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

