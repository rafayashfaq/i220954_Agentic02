import React from 'react';
import { UserProfile } from '../lib/api/client';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  user: UserProfile | null;
  onSwitchPersona: (key: string) => void;
  isDegraded: boolean;
  toggleDegraded: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  user,
  onSwitchPersona,
  isDegraded,
  toggleDegraded
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentTab('inbox')}>
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-emerald-500 to-green-400 flex items-center justify-center font-bold text-slate-950 text-xl shadow-lg shadow-emerald-500/20">
            GB
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">GigBid</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                Copilot 2.0
              </span>
            </div>
            <p className="text-xs text-slate-400 -mt-0.5">Multi-Agent LangGraph Systems</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/80 text-sm font-medium">
          {[
            { id: 'inbox', label: 'Job Inbox' },
            { id: 'pipeline', label: 'Pipeline' },
            { id: 'messages', label: 'Messages' },
            { id: 'runs', label: 'Agent Runs' },
            { id: 'analytics', label: 'Analytics' },
            { id: 'settings', label: 'Settings' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setCurrentTab(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg transition-all ${
                currentTab === tab.id
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        {/* User Persona & Status Controls */}
        <div className="flex items-center gap-3">
          {/* Degraded mode toggle simulator */}
          <button
            onClick={toggleDegraded}
            title="Toggle degraded marketplace mode to simulate outage"
            className={`text-xs px-2.5 py-1 rounded-md border transition-colors ${
              isDegraded
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-300 animate-pulse font-semibold'
                : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:text-slate-200'
            }`}
          >
            {isDegraded ? '🔴 Degraded Mode' : '🟢 GigSim OK'}
          </button>

          {/* Connects Badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-slate-800/80 border border-slate-700/80 rounded-lg text-xs font-mono text-emerald-400">
            <span>⚡</span>
            <span>{user?.weekly_connects_budget || 72} Connects</span>
          </div>

          {/* Persona Switcher Dropdown */}
          <select
            value={user?.persona_key || 'ai_engineer'}
            onChange={(e) => onSwitchPersona(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500 font-medium cursor-pointer"
          >
            <option value="ai_engineer">🤖 AI/ML Engineer (Alex)</option>
            <option value="fullstack_dev">💻 Full-Stack Dev (Marcus)</option>
            <option value="data_analyst">📊 Data Analyst (Elena)</option>
          </select>
        </div>
      </div>
    </header>
  );
};

