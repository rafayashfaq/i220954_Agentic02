import React, { useState, useEffect } from 'react';
import { MessageThread, api } from '../lib/api/client';

export const MessagesView: React.FC = () => {
  const [threads, setThreads] = useState<MessageThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [replyText, setReplyText] = useState('');
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    const fetchThreads = async () => {
      try {
        const res = await api.getThreads();
        setThreads(res);
        if (res.length > 0) {
          setActiveThreadId(res[0].thread_id);
          setReplyText(res[0].suggested_reply || '');
        }
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchThreads();
  }, []);

  const activeThread = threads.find((t) => t.thread_id === activeThreadId);

  const handleSendReply = async () => {
    if (!activeThread) return;
    setIsSending(true);
    try {
      await api.sendReply(
        activeThread.thread_id,
        activeThread.client_id,
        replyText,
        activeThread.suggested_interview_slots
      );
      // Update thread state
      setThreads((prev) =>
        prev.map((t) =>
          t.thread_id === activeThread.thread_id
            ? {
                ...t,
                messages: [
                  ...t.messages,
                  { sender: 'freelancer', body: replyText, timestamp: new Date().toISOString() }
                ],
                suggested_reply: undefined
              }
            : t
        )
      );
      setReplyText('');
    } catch (err) {
      console.error(err);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 animate-fadeIn">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white tracking-tight">Client Conversations</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Incoming client inquiries with AI-drafted replies and calendar holds. Requires human approval before sending.
        </p>
      </div>

      {isLoading ? (
        <div className="text-center py-20 text-slate-500 text-sm animate-pulse">
          Loading messages...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl min-h-[500px]">
          {/* Thread list */}
          <div className="border-r border-slate-800 pr-4 space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Active Threads</h3>
            {threads.map((t) => (
              <div
                key={t.thread_id}
                onClick={() => {
                  setActiveThreadId(t.thread_id);
                  setReplyText(t.suggested_reply || '');
                }}
                className={`p-3.5 rounded-2xl border cursor-pointer transition-all ${
                  activeThreadId === t.thread_id
                    ? 'bg-emerald-500/10 border-emerald-500 text-white shadow-md'
                    : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className="font-semibold text-xs text-slate-100 flex items-center justify-between mb-1">
                  <span>Client: {t.client_id}</span>
                  {t.suggested_reply && (
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-1">
                  {t.messages[t.messages.length - 1]?.body || 'No messages'}
                </p>
              </div>
            ))}
          </div>

          {/* Conversation & Draft Panel */}
          <div className="md:col-span-2 flex flex-col justify-between pl-2">
            {activeThread ? (
              <>
                {/* Messages stream */}
                <div className="space-y-3 mb-6 overflow-y-auto max-h-[350px] pr-2">
                  {activeThread.messages.map((m, idx) => (
                    <div
                      key={idx}
                      className={`p-3.5 rounded-2xl text-xs max-w-[85%] leading-relaxed ${
                        m.sender === 'client'
                          ? 'bg-slate-950 border border-slate-800 text-slate-200 self-start'
                          : 'bg-emerald-600/20 border border-emerald-500/30 text-emerald-100 ml-auto'
                      }`}
                    >
                      <div className="text-[10px] text-slate-400 font-mono mb-1 font-semibold">
                        {m.sender === 'client' ? 'Client' : 'Alex (GigBid Copilot)'}
                      </div>
                      <p>{m.body}</p>
                    </div>
                  ))}
                </div>

                {/* AI-drafted reply with human approval */}
                <div className="pt-4 border-t border-slate-800">
                  {activeThread.suggested_interview_slots.length > 0 && (
                    <div className="mb-3 p-2.5 bg-purple-500/10 border border-purple-500/20 rounded-xl text-xs text-purple-200">
                      <strong>📅 Workspace MCP Hold Placed:</strong> 2 tentative interview slots synced to calendar.
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                    <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <span>✍️ Suggested Reply</span>
                      <span className="text-[10px] px-1.5 py-0.2 bg-emerald-500/20 text-emerald-300 rounded font-mono">
                        Awaiting Human Approval
                      </span>
                    </span>
                  </div>

                  <textarea
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    rows={3}
                    className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500 font-sans leading-relaxed mb-3"
                    placeholder="Type or edit response..."
                  />

                  <div className="flex justify-end gap-2">
                    <button
                      onClick={handleSendReply}
                      disabled={isSending || !replyText.trim()}
                      className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/25 transition-all flex items-center gap-1.5"
                    >
                      {isSending ? 'Sending...' : '✓ Approve & Send to Client'}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-20 text-slate-500 text-xs">
                Select a thread to view client messages.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

