import React, { useState, useEffect } from 'react';
import { SettingsResponse, api } from '../lib/api/client';

export const SettingsView: React.FC = () => {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [autonomyLevel, setAutonomyLevel] = useState('auto_skip_only');
  const [weeklyBudget, setWeeklyBudget] = useState(80);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const fetchSettings = async () => {
    try {
      const res = await api.getSettings();
      setSettings(res);
      setAutonomyLevel(res.autonomy_level);
      setWeeklyBudget(res.weekly_budget);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async () => {
    try {
      await api.updateSettings(autonomyLevel, weeklyBudget);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    try {
      await api.deleteMemoryRule(ruleId);
      if (settings) {
        setSettings({
          ...settings,
          style_memory_rules: settings.style_memory_rules.filter((r) => r.id !== ruleId)
        });
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center text-slate-500 animate-pulse">
        Loading settings & long-term memory...
      </div>
    );
  }

  if (!settings) return null;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 animate-fadeIn">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">System Settings & Memory</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Configure autonomy thresholds, Connects limits, and inspect what GigBid has learned from your edits.
        </p>
      </div>

      {saveSuccess && (
        <div className="mb-4 p-3 bg-emerald-500/20 border border-emerald-500/40 rounded-xl text-emerald-200 text-xs font-semibold animate-fadeIn">
          ✓ Settings saved successfully.
        </div>
      )}

      {/* Autonomy & Budgets Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl mb-6">
        <h3 className="text-base font-bold text-white mb-4">Autonomy & Connects Safety</h3>

        <div className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Autonomy Level
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label
                className={`p-3.5 rounded-xl border flex items-start gap-3 cursor-pointer ${
                  autonomyLevel === 'auto_skip_only'
                    ? 'bg-emerald-500/10 border-emerald-500 text-white'
                    : 'bg-slate-950 border-slate-800 text-slate-400'
                }`}
              >
                <input
                  type="radio"
                  name="autonomy"
                  value="auto_skip_only"
                  checked={autonomyLevel === 'auto_skip_only'}
                  onChange={() => setAutonomyLevel('auto_skip_only')}
                  className="mt-1 accent-emerald-500"
                />
                <div>
                  <div className="font-semibold text-xs text-slate-100">Auto-Skip Low-Fit (Recommended)</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Automatically filters scams and low-fit jobs; ALWAYS pauses for human approval before sending proposals.
                  </div>
                </div>
              </label>

              <label
                className={`p-3.5 rounded-xl border flex items-start gap-3 cursor-pointer ${
                  autonomyLevel === 'manual_review'
                    ? 'bg-emerald-500/10 border-emerald-500 text-white'
                    : 'bg-slate-950 border-slate-800 text-slate-400'
                }`}
              >
                <input
                  type="radio"
                  name="autonomy"
                  value="manual_review"
                  checked={autonomyLevel === 'manual_review'}
                  onChange={() => setAutonomyLevel('manual_review')}
                  className="mt-1 accent-emerald-500"
                />
                <div>
                  <div className="font-semibold text-xs text-slate-100">Manual Review All</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">
                    Surfaces every job in inbox, requiring explicit human skip or bid confirmation.
                  </div>
                </div>
              </label>
            </div>
          </div>

          <div className="max-w-xs">
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Weekly Connects Budget</label>
            <input
              type="number"
              value={weeklyBudget}
              onChange={(e) => setWeeklyBudget(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <button
            onClick={handleSave}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/20"
          >
            Save Settings
          </button>
        </div>
      </div>

      {/* Memory Viewer Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>🧠 Style Memory Viewer</span>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                {settings.style_memory_rules.length} Rules Learned
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Knowledge promoted from your human edits. Inspect or delete rules you want to unlearn.
            </p>
          </div>
        </div>

        <div className="space-y-2.5">
          {settings.style_memory_rules.length === 0 ? (
            <div className="text-center py-6 text-xs text-slate-500">
              No style rules recorded yet. As you edit proposal drafts in the studio, writing preferences are automatically learned.
            </div>
          ) : (
            settings.style_memory_rules.map((rule) => (
              <div
                key={rule.id}
                className="flex items-center justify-between p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-xs text-slate-200"
              >
                <div className="flex items-center gap-2.5">
                  <span className="font-mono text-emerald-400 font-bold">[{rule.id}]</span>
                  <span className="font-medium">{rule.rule}</span>
                </div>

                <button
                  onClick={() => handleDeleteRule(rule.id)}
                  title="Delete learned style rule"
                  className="text-xs font-semibold text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 px-2 py-1 rounded transition-colors"
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

