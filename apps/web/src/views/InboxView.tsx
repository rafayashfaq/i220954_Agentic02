import React, { useState, useEffect } from 'react';
import { JobSummary, api } from '../lib/api/client';

interface InboxViewProps {
  onSelectJob: (jobId: string) => void;
  onOpenStudio: (jobId: string) => void;
}

export const InboxView: React.FC<InboxViewProps> = ({ onSelectJob, onOpenStudio }) => {
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  const loadJobs = async () => {
    setIsLoading(true);
    try {
      const data = await api.getJobs(searchQuery, actionFilter);
      setJobs(data);
    } catch (err) {
      console.error('Failed to load inbox jobs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, [searchQuery, actionFilter]);

  const handleSkipJob = (jobId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setJobs((prev) => prev.filter((j) => j.job_id !== jobId));
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 animate-fadeIn">
      {/* Inbox Header & Search Filters */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <span>Marketplace Job Feed</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono font-medium">
              {jobs.length} jobs available
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Scouted, deduplicated, and ranked by portfolio evidence fit score.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <input
            type="text"
            placeholder="Search keywords (e.g. Python, RAG, dbt)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500 w-full sm:w-64"
          />

          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-emerald-500 cursor-pointer"
          >
            <option value="">All Actions</option>
            <option value="bid">🎯 Recommend Bid</option>
            <option value="watch">👀 Watchlist</option>
            <option value="skip">✕ Skipped / High Risk</option>
          </select>
        </div>
      </div>

      {/* Jobs Listing */}
      {isLoading ? (
        <div className="text-center py-20 text-slate-500 text-sm animate-pulse">
          Loading incoming job stream...
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/50 border border-slate-800 rounded-3xl p-8">
          <div className="text-4xl mb-3">🔍</div>
          <h3 className="font-semibold text-slate-300">No matching jobs found</h3>
          <p className="text-xs text-slate-500 mt-1">Try broadening your search query or reset filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3.5">
          {jobs.map((job) => {
            const isHighFit = job.fit_score >= 0.70;
            const isScam = job.recommended_action === 'skip' || job.risk_score >= 0.70;

            return (
              <div
                key={job.job_id}
                onClick={() => onSelectJob(job.job_id)}
                className="bg-slate-900/80 hover:bg-slate-900 border border-slate-800/90 hover:border-slate-700/90 rounded-2xl p-5 transition-all cursor-pointer shadow-md hover:shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4 group"
              >
                {/* Left: Job Meta & Skills */}
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    {/* Action Badge */}
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider ${
                      job.recommended_action === 'bid'
                        ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                        : job.recommended_action === 'watch'
                        ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                        : 'bg-rose-500/15 text-rose-300 border border-rose-500/30'
                    }`}>
                      {job.recommended_action === 'bid' ? '✓ Recommended Bid' : job.recommended_action === 'watch' ? '• Watch' : '✕ Skip'}
                    </span>

                    {/* Fit Score Badge */}
                    <span className="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700/80 text-[11px] font-mono text-slate-300">
                      Fit: <strong className={isHighFit ? 'text-emerald-400' : 'text-slate-200'}>{Math.round(job.fit_score * 100)}%</strong>
                    </span>

                    {/* Risk Badge */}
                    {job.risk_score > 0.4 && (
                      <span className="px-2 py-0.5 rounded-md bg-rose-500/10 border border-rose-500/30 text-[11px] font-bold text-rose-300 flex items-center gap-1">
                        <span>⚠️ Risk: {Math.round(job.risk_score * 100)}%</span>
                        {job.has_injection && <span className="text-[10px] bg-rose-500/20 px-1 rounded">Injection Defended</span>}
                      </span>
                    )}

                    {/* Connects cost */}
                    <span className="text-xs font-mono text-slate-400">
                      ⚡ {job.connects_cost} Connects
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors">
                    {job.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                    {job.description}
                  </p>

                  {/* Skills tags */}
                  <div className="flex flex-wrap items-center gap-1.5 mt-3">
                    {job.required_skills.slice(0, 5).map((skill, i) => (
                      <span key={i} className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[11px] font-medium text-slate-300">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Right: Budget & Action Buttons */}
                <div className="flex md:flex-col items-center md:items-end justify-between md:justify-center border-t md:border-t-0 pt-3 md:pt-0 border-slate-800 gap-2 shrink-0">
                  <div className="text-left md:text-right">
                    <div className="text-sm font-bold text-slate-100 font-mono">
                      ${job.budget_min} - ${job.budget_max}
                    </div>
                    <div className="text-[11px] text-slate-500">Fixed-price budget</div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => handleSkipJob(job.job_id, e)}
                      title="Skip job and remove from inbox"
                      className="px-2.5 py-1.5 text-xs rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                    >
                      Skip
                    </button>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenStudio(job.job_id);
                      }}
                      className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/20 transition-all"
                    >
                      Draft Proposal →
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

