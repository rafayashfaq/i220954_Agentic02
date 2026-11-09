import React, { useState, useEffect } from 'react';
import { UserProfile, api } from './lib/api/client';
import { Navbar } from './components/Navbar';
import { DegradedModeBanner } from './components/DegradedModeBanner';
import { OnboardingView } from './views/OnboardingView';
import { InboxView } from './views/InboxView';
import { JobDetailView } from './views/JobDetailView';
import { ProposalStudioView } from './views/ProposalStudioView';
import { PipelineView } from './views/PipelineView';
import { MessagesView } from './views/MessagesView';
import { RunViewerView } from './views/RunViewerView';
import { AnalyticsView } from './views/AnalyticsView';
import { SettingsView } from './views/SettingsView';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('inbox');
  const [selectedJobId, setSelectedJobId] = useState<string>('sample-job-001');
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isDegraded, setIsDegraded] = useState(false);
  const [hasOnboarded, setHasOnboarded] = useState(true);

  // Initial health and user check
  useEffect(() => {
    const initApp = async () => {
      try {
        const u = await api.getCurrentUser();
        setUser(u);
      } catch (err) {
        console.warn('Backend loading or starting:', err);
      }
    };
    initApp();
  }, []);

  const handleSwitchPersona = async (personaKey: string) => {
    try {
      const updated = await api.switchPersona(personaKey);
      setUser(updated);
    } catch (err) {
      console.error(err);
    }
  };

  const toggleDegradedMode = () => {
    setIsDegraded((prev) => !prev);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-slate-950">
      {/* Degraded Mode Banner (Displays when marketplace server is killed or simulated 503) */}
      <DegradedModeBanner
        isDegraded={isDegraded}
        onRecover={() => setIsDegraded(false)}
      />

      {/* Main Navbar */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        user={user}
        onSwitchPersona={handleSwitchPersona}
        isDegraded={isDegraded}
        toggleDegraded={toggleDegraded}
      />

      {/* Active Screen View */}
      <main className="flex-1">
        {currentTab === 'onboarding' && (
          <OnboardingView
            user={user}
            onComplete={(updated) => {
              setUser(updated);
              setCurrentTab('inbox');
            }}
          />
        )}

        {currentTab === 'inbox' && (
          <InboxView
            onSelectJob={(id) => {
              setSelectedJobId(id);
              setCurrentTab('detail');
            }}
            onOpenStudio={(id) => {
              setSelectedJobId(id);
              setCurrentTab('studio');
            }}
          />
        )}

        {currentTab === 'detail' && (
          <JobDetailView
            jobId={selectedJobId}
            onBack={() => setCurrentTab('inbox')}
            onOpenStudio={(id) => {
              setSelectedJobId(id);
              setCurrentTab('studio');
            }}
            onStartStream={(id) => {
              setSelectedJobId(id);
              setCurrentTab('runs');
            }}
          />
        )}

        {currentTab === 'studio' && (
          <ProposalStudioView
            jobId={selectedJobId}
            onBack={() => setCurrentTab('detail')}
            onSubmissionSuccess={() => setCurrentTab('pipeline')}
          />
        )}

        {currentTab === 'pipeline' && <PipelineView />}

        {currentTab === 'messages' && <MessagesView />}

        {currentTab === 'runs' && <RunViewerView initialJobId={selectedJobId} />}

        {currentTab === 'analytics' && <AnalyticsView />}

        {currentTab === 'settings' && <SettingsView />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500">
        <p>GigBid AI-4016 R&D Project · LangGraph Multi-Agent Architecture · FAST-NUCES Islamabad</p>
      </footer>
    </div>
  );
};

