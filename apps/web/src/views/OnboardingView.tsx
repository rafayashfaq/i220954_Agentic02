import React, { useState } from 'react';
import { UserProfile, api } from '../lib/api/client';

interface OnboardingViewProps {
  user: UserProfile | null;
  onComplete: (user: UserProfile) => void;
}

export const OnboardingView: React.FC<OnboardingViewProps> = ({ user, onComplete }) => {
  const [personaKey, setPersonaKey] = useState(user?.persona_key || 'ai_engineer');
  const [displayName, setDisplayName] = useState(user?.display_name || 'Alex Morgan');
  const [hourlyRate, setHourlyRate] = useState(user?.hourly_rate || 65);
  const [minBudget, setMinBudget] = useState(user?.min_budget || 500);
  const [connectsBudget, setConnectsBudget] = useState(user?.weekly_connects_budget || 80);
  const [marketplaceMode, setMarketplaceMode] = useState(user?.marketplace_mode || 'gigsim');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const updated = await api.onboarding({
        persona_key: personaKey,
        display_name: displayName,
        hourly_rate: Number(hourlyRate),
        min_budget: Number(minBudget),
        weekly_connects_budget: Number(connectsBudget),
        marketplace_mode: marketplaceMode
      });
      onComplete(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-10 px-4 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
        <div className="text-center mb-8">
          <div className="inline-flex w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 items-center justify-center text-3xl mb-3 shadow-inner">
            🚀
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Welcome to GigBid</h1>
          <p className="text-sm text-slate-400 mt-1">
            Configure your freelancer profile, portfolio rules, and marketplace connection.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Persona Selection */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Select Freelancer Persona
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { key: 'ai_engineer', title: 'AI/ML Engineer', desc: 'LangGraph, RAG, PyTorch', icon: '🤖' },
                { key: 'fullstack_dev', title: 'Full-Stack Dev', desc: 'Next.js, FastAPI, Docker', icon: '💻' },
                { key: 'data_analyst', title: 'Data Analyst', desc: 'dbt, Snowflake, Tableau', icon: '📊' }
              ].map((p) => (
                <div
                  key={p.key}
                  onClick={() => setPersonaKey(p.key)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    personaKey === p.key
                      ? 'bg-emerald-500/10 border-emerald-500 text-white shadow-md'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="text-2xl mb-1.5">{p.icon}</div>
                  <div className="font-semibold text-sm text-slate-200">{p.title}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{p.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Name & Headline */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Freelancer Name</label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Hourly Rate ($ USD)</label>
              <input
                type="number"
                value={hourlyRate}
                onChange={(e) => setHourlyRate(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                required
              />
            </div>
          </div>

          {/* Budget Floor & Connects Budget */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Minimum Project Budget Floor ($)</label>
              <input
                type="number"
                value={minBudget}
                onChange={(e) => setMinBudget(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Weekly Connects Budget</label>
              <input
                type="number"
                value={connectsBudget}
                onChange={(e) => setConnectsBudget(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                required
              />
            </div>
          </div>

          {/* Marketplace Connection */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Marketplace Adapter Connection
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label
                className={`p-3.5 rounded-xl border flex items-center gap-3 cursor-pointer ${
                  marketplaceMode === 'gigsim'
                    ? 'bg-emerald-500/10 border-emerald-500 text-white'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400'
                }`}
              >
                <input
                  type="radio"
                  name="market"
                  value="gigsim"
                  checked={marketplaceMode === 'gigsim'}
                  onChange={() => setMarketplaceMode('gigsim')}
                  className="accent-emerald-500"
                />
                <div>
                  <div className="text-sm font-semibold text-slate-200">GigSim Simulator (Default)</div>
                  <div className="text-xs text-slate-400">Deterministic local simulator for grading</div>
                </div>
              </label>

              <label
                className={`p-3.5 rounded-xl border flex items-center gap-3 cursor-pointer ${
                  marketplaceMode === 'upwork_live'
                    ? 'bg-emerald-500/10 border-emerald-500 text-white'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400'
                }`}
              >
                <input
                  type="radio"
                  name="market"
                  value="upwork_live"
                  checked={marketplaceMode === 'upwork_live'}
                  onChange={() => setMarketplaceMode('upwork_live')}
                  className="accent-emerald-500"
                />
                <div>
                  <div className="text-sm font-semibold text-slate-200">Upwork Official MCP</div>
                  <div className="text-xs text-slate-400">OAuth 2.1 Streamable HTTP live drafts</div>
                </div>
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-xl shadow-emerald-600/30 transition-all flex items-center justify-center gap-2"
          >
            {isSubmitting ? 'Saving Configuration...' : 'Save & Open Job Inbox →'}
          </button>
        </form>
      </div>
    </div>
  );
};

