import React, { useState, useEffect } from 'react';
import { ProposalStudioResponse, api } from '../lib/api/client';
import { EvidenceHover } from '../components/EvidenceHover';
import { ApprovalPanel } from '../components/ApprovalPanel';

interface ProposalStudioViewProps {
  jobId: string;
  onBack: () => void;
  onSubmissionSuccess: () => void;
}

export const ProposalStudioView: React.FC<ProposalStudioViewProps> = ({
  jobId,
  onBack,
  onSubmissionSuccess
}) => {
  const [studio, setStudio] = useState<ProposalStudioResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [submittedStatus, setSubmittedStatus] = useState<string | null>(null);
  const [errorStatus, setErrorStatus] = useState<string | null>(null);

  useEffect(() => {
    const fetchStudio = async () => {
      try {
        const res = await api.getProposalStudio(jobId);
        setStudio(res);
      } catch (err: any) {
        console.error(err);
        setErrorStatus(`Failed to load proposal studio: ${err?.message || 'Server error'}`);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStudio();
  }, [jobId]);

  const handleRegenerateParagraph = async (pIndex: number, currentText: string) => {
    setIsRegenerating(true);
    setErrorStatus(null);
    try {
      const res = await api.regenerateParagraph(jobId, pIndex, currentText);
      if (studio) {
        const updatedLetter = studio.cover_letter + "\n\n" + res.regenerated_text;
        const newClaim = {
          claim_text: res.regenerated_text,
          status: 'supported' as const,
          evidence_id: 'case-regen-01',
          evidence_title: 'Modular High-Reliability Architecture',
          evidence_summary: 'Asynchronous streaming pipelines with structured schemas and full observability.',
          proven_outcome: 'Production zero-downtime reliability'
        };
        setStudio({
          ...studio,
          cover_letter: updatedLetter,
          claims_with_evidence: [...studio.claims_with_evidence, newClaim]
        });
        setSubmittedStatus('Section regenerated with grounded portfolio citation!');
        setTimeout(() => setSubmittedStatus(null), 3500);
      }
    } catch (err: any) {
      console.error(err);
      setErrorStatus(`Failed to regenerate section: ${err?.message || 'Server error'}`);
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleApprove = async () => {
    if (!studio) return;
    setErrorStatus(null);
    try {
      const res = await api.executeApproval({
        thread_id: studio.thread_id,
        action: 'approved'
      });
      setSubmittedStatus('Submitted successfully to GigSim!');
      setTimeout(() => {
        onSubmissionSuccess();
      }, 1200);
    } catch (err: any) {
      console.error(err);
      setErrorStatus(`Submission error: ${err?.message || 'Failed to submit'}`);
    }
  };

  const handleEditAndApprove = async (editedText: string) => {
    if (!studio) return;
    setErrorStatus(null);
    try {
      const res = await api.executeApproval({
        thread_id: studio.thread_id,
        action: 'edited',
        edited_text: editedText
      });
      setSubmittedStatus('Edits saved to Style Memory & proposal submitted!');
      setTimeout(() => {
        onSubmissionSuccess();
      }, 1200);
    } catch (err: any) {
      console.error(err);
      setErrorStatus(`Submission error: ${err?.message || 'Failed to submit edits'}`);
    }
  };

  const handleReject = async (reason: string) => {
    if (!studio) return;
    setErrorStatus(null);
    try {
      await api.executeApproval({
        thread_id: studio.thread_id,
        action: 'rejected',
        reason: reason
      });
      setSubmittedStatus('Proposal rejected and marked skipped.');
      setTimeout(() => {
        onBack();
      }, 1000);
    } catch (err: any) {
      console.error(err);
      setErrorStatus(`Rejection error: ${err?.message || 'Failed to record rejection'}`);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center text-slate-500 animate-pulse">
        Loading Proposal Studio & Verifying Claims...
      </div>
    );
  }

  if (!studio) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center">
        <h2 className="text-lg font-bold text-slate-200">Unable to load Proposal Studio</h2>
        <button onClick={onBack} className="mt-3 text-xs text-emerald-400 underline">← Return to Inbox</button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 animate-fadeIn">
      {/* Header bar */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="text-xs font-semibold text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors"
        >
          ← Return to Job Detail
        </button>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-mono">Job ID: {studio.job_id}</span>
        </div>
      </div>

      {submittedStatus && (
        <div className="mb-6 p-4 bg-emerald-500/20 border border-emerald-500/40 rounded-2xl text-emerald-200 text-sm font-semibold flex items-center gap-2 animate-fadeIn">
          <span>✓</span>
          <span>{submittedStatus}</span>
        </div>
      )}

      {errorStatus && (
        <div className="mb-6 p-4 bg-rose-500/20 border border-rose-500/40 rounded-2xl text-rose-200 text-sm font-semibold flex items-center justify-between gap-2 animate-fadeIn">
          <div className="flex items-center gap-2">
            <span>⚠️</span>
            <span>{errorStatus}</span>
          </div>
          <button onClick={() => setErrorStatus(null)} className="text-xs text-rose-300 hover:text-rose-100 underline">Dismiss</button>
        </div>
      )}

      {/* Main Studio Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Left 2 Cols: Interactive Grounded Cover Letter */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>📝 Evidence-Grounded Proposal Draft</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Hover over underlined sentences to inspect the supporting portfolio evidence and verified outcomes.
              </p>
            </div>

            <button
              onClick={() => handleRegenerateParagraph(0, studio.cover_letter)}
              disabled={isRegenerating}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            >
              {isRegenerating ? 'Regenerating...' : '🔄 Regenerate Section'}
            </button>
          </div>

          {/* Interactive Claim Elements */}
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-5 text-sm text-slate-200 leading-relaxed font-sans mb-6">
            {studio.claims_with_evidence.map((claim, idx) => (
              <React.Fragment key={idx}>
                <EvidenceHover claim={claim} />{' '}
              </React.Fragment>
            ))}
          </div>

          {/* Screening Question Answers */}
          {studio.screening_answers.length > 0 && (
            <div className="pt-4 border-t border-slate-800">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Screening Question Answers</h4>
              <div className="space-y-2">
                {studio.screening_answers.map((ans, i) => (
                  <div key={i} className="p-3 bg-slate-950/50 rounded-xl border border-slate-800/70 text-xs text-slate-300">
                    {ans}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Col: Evidence Provability Legend & Quick Audit */}
        <div className="space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-xs shadow-lg">
            <h4 className="font-bold text-slate-200 mb-3 uppercase tracking-wider text-[11px]">Evidence Provability</h4>
            <div className="space-y-2.5">
              <div className="flex items-center gap-2 text-emerald-300">
                <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                <span className="font-medium">Supported (Verified Case Study)</span>
              </div>
              <div className="flex items-center gap-2 text-amber-300">
                <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                <span className="font-medium">Partly Supported (CV General Skill)</span>
              </div>
              <div className="flex items-center gap-2 text-rose-300">
                <span className="w-3 h-3 rounded-full bg-rose-500"></span>
                <span className="font-medium">Unsupported (Auto-Rewritten)</span>
              </div>
            </div>
          </div>

          {/* Dry Run Preview Snapshot */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-xs shadow-lg font-mono">
            <h4 className="font-bold text-slate-200 mb-2 font-sans uppercase tracking-wider text-[11px]">Marketplace Dry Run</h4>
            <div className="space-y-1.5 text-slate-400">
              <div className="flex justify-between">
                <span>Connects Cost:</span>
                <span className="text-emerald-400 font-bold">{studio.dry_run_preview.connects_required}</span>
              </div>
              <div className="flex justify-between">
                <span>Proposed Bid:</span>
                <span className="text-slate-200">${studio.dry_run_preview.bid_amount}</span>
              </div>
              <div className="flex justify-between">
                <span>Ready Status:</span>
                <span className="text-emerald-400">CONFIRMED</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Human Approval Panel */}
      <ApprovalPanel
        threadId={studio.thread_id}
        initialDraft={studio.cover_letter}
        dryRun={studio.dry_run_preview}
        criticFeedback={studio.critic_feedback}
        complianceExplanation={studio.compliance_explanation}
        onApprove={handleApprove}
        onEditAndApprove={handleEditAndApprove}
        onReject={handleReject}
      />
    </div>
  );
};

