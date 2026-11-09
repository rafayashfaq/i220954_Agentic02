import React, { useState } from 'react';
import { DryRunPreview } from '../lib/api/client';

interface ApprovalPanelProps {
  threadId: string;
  initialDraft: string;
  dryRun: DryRunPreview;
  criticFeedback: string;
  complianceExplanation: string;
  onApprove: () => void;
  onEditAndApprove: (editedText: string) => void;
  onReject: (reason: string) => void;
}

export const ApprovalPanel: React.FC<ApprovalPanelProps> = ({
  threadId,
  initialDraft,
  dryRun,
  criticFeedback,
  complianceExplanation,
  onApprove,
  onEditAndApprove,
  onReject
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(initialDraft);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);

  const hasEdits = editedText.trim() !== initialDraft.trim();

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
        <div>
          <h3 className="font-semibold text-slate-100 flex items-center gap-2">
            <span>🛡️ Human-in-the-Loop Approval Gate</span>
            <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              Thread Paused
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Nothing reaches the marketplace or spends Connects without your explicit confirmation.
          </p>
        </div>

        {/* Cost & Dry Run Badge */}
        <div className="text-right">
          <div className="text-xs font-mono text-emerald-400 font-bold">
            -${dryRun.connects_required} Connects Required
          </div>
          <div className="text-[11px] text-slate-400">
            Balance after: {dryRun.user_balance_after}
          </div>
        </div>
      </div>

      {/* Inline Critic & Compliance Badges */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 text-xs">
          <div className="font-semibold text-slate-300 flex items-center gap-1.5 mb-1">
            <span>🔍 Critic Review:</span>
            <span className="text-emerald-400">Passed</span>
          </div>
          <p className="text-slate-400">{criticFeedback}</p>
        </div>

        <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 text-xs">
          <div className="font-semibold text-slate-300 flex items-center gap-1.5 mb-1">
            <span>⚖️ Compliance Guard:</span>
            <span className="text-emerald-400">Sanitized & Compliant</span>
          </div>
          <p className="text-slate-400">{complianceExplanation}</p>
        </div>
      </div>

      {/* Editable proposal body */}
      {isEditing ? (
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
            <span>Edit proposal directly (edits will be diffed and saved to Style Memory):</span>
            {hasEdits && (
              <span className="text-amber-400 font-medium">Modified from AI draft</span>
            )}
          </div>
          <textarea
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            rows={6}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500 font-mono leading-relaxed"
          />
        </div>
      ) : null}

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-2">
        <div className="flex items-center gap-2">
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
            >
              ✏️ Edit Draft
            </button>
          ) : (
            <button
              onClick={() => {
                setEditedText(initialDraft);
                setIsEditing(false);
              }}
              className="px-3 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200"
            >
              Cancel Edits
            </button>
          )}

          <button
            onClick={() => setShowRejectModal(true)}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 transition-colors"
          >
            ✕ Reject Bid
          </button>
        </div>

        <button
          onClick={() => {
            if (isEditing && hasEdits) {
              onEditAndApprove(editedText);
            } else {
              onApprove();
            }
          }}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/25 transition-all flex items-center gap-1.5"
        >
          <span>✓</span>
          <span>{isEditing && hasEdits ? 'Save Edits & Submit to GigSim' : 'Approve & Submit to GigSim'}</span>
        </button>
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-5 shadow-2xl">
            <h4 className="font-semibold text-slate-100 mb-2">Reject Proposal Submission</h4>
            <p className="text-xs text-slate-400 mb-3">
              Provide an optional reason. GigBid learns from rejection reasons to tune future fit matching.
            </p>
            <textarea
              placeholder="e.g. Budget too low for scope, or client has poor reviews..."
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={3}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-rose-500 mb-4"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowRejectModal(false)}
                className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  onReject(rejectReason);
                }}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

