import React, { useState, useEffect } from 'react';
import { AnalyticsOverview, api } from '../lib/api/client';

export const AnalyticsView: React.FC = () => {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.getAnalytics();
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto py-20 text-center text-slate-500 animate-pulse">
        Loading analytics metrics...
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 animate-fadeIn">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">Performance Analytics & Budgets</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Empirical funnel conversion, token economics, latency distributions, and rejection taxonomy.
        </p>
      </div>

      {/* Top 4 Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="text-xs text-slate-400 font-medium">GigSim Reply Rate</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {data.reply_rate_percentage}%
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">+14.3% over naive baseline</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="text-xs text-slate-400 font-medium">Contract Hire Rate</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {data.hire_rate_percentage}%
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">36 contracts secured</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="text-xs text-slate-400 font-medium">p95 Retrieval Latency</div>
          <div className="text-2xl font-bold font-mono text-slate-200 mt-1">
            {data.p95_latency_ms} ms
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Budget limit: 100 ms</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="text-xs text-slate-400 font-medium">Avg Cost / Proposal</div>
          <div className="text-2xl font-bold font-mono text-slate-200 mt-1">
            ${data.average_cost_per_proposal_usd}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Open model profile</div>
        </div>
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Outcomes by Category */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h3 className="font-bold text-white text-sm mb-4 flex items-center justify-between">
            <span>Performance by Domain Category</span>
            <span className="text-xs font-mono text-slate-400">Reply & Hire</span>
          </h3>

          <div className="space-y-4">
            {data.outcomes_by_category.map((cat, idx) => (
              <div key={idx} className="p-3.5 bg-slate-950/60 rounded-2xl border border-slate-800/80 text-xs">
                <div className="flex justify-between items-center mb-1 font-semibold text-slate-200">
                  <span>{cat.category}</span>
                  <span className="text-emerald-400 font-mono">${cat.avg_contract} avg</span>
                </div>
                <div className="flex justify-between text-slate-400 text-[11px] mb-2">
                  <span>Reply Rate: {cat.reply_rate}%</span>
                  <span>Hire Rate: {cat.hire_rate}%</span>
                </div>
                {/* Progress bar */}
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-500 h-full rounded-full"
                    style={{ width: `${cat.reply_rate}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Rejection Taxonomy */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h3 className="font-bold text-white text-sm mb-4">Top Auto-Skip & Rejection Taxonomy</h3>
          <div className="space-y-3">
            {data.rejection_taxonomy.map((rej, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-slate-950/50 rounded-xl border border-slate-800/70 text-xs">
                <div>
                  <div className="font-medium text-slate-200">{rej.category}</div>
                  <div className="text-[11px] text-slate-500 font-mono">{rej.count} occurrences</div>
                </div>
                <span className="font-mono text-rose-300 font-bold bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
                  {rej.percentage}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

