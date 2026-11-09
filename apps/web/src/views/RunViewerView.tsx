import React, { useState, useEffect } from 'react';
import { RunTimeline, TimelineEvent } from '../components/RunTimeline';

interface RunViewerViewProps {
  initialJobId?: string;
}

export const RunViewerView: React.FC<RunViewerViewProps> = ({ initialJobId = 'sample-job-001' }) => {
  const [jobId, setJobId] = useState(initialJobId);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeNode, setActiveNode] = useState<string | null>(null);

  const startStreaming = () => {
    setEvents([]);
    setIsStreaming(true);
    setActiveNode('init');

    const API_BASE = 'http://127.0.0.1:8000';
    const eventSource = new EventSource(`${API_BASE}/runs/stream/${jobId}`);

    eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.event === 'node_update') {
          setActiveNode(data.node);
          setEvents((prev) => [
            ...prev,
            { node: data.node, message: data.message, status: 'completed' }
          ]);
        } else if (data.event === 'interrupt') {
          setActiveNode('human_approval');
          setEvents((prev) => [
            ...prev,
            { node: 'human_approval', message: 'Graph execution paused for human approval.', status: 'paused' }
          ]);
          setIsStreaming(false);
          eventSource.close();
        } else if (data.event === 'done') {
          setIsStreaming(false);
          eventSource.close();
        }
      } catch (err) {
        console.error('SSE parse error:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.warn('SSE stream closed or completed:', err);
      setIsStreaming(false);
      eventSource.close();
    };
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 animate-fadeIn">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Agent Run Viewer</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Inspect real-time LangGraph multi-agent execution streamed node-by-node via Server-Sent Events.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:ring-1 focus:ring-emerald-500 w-36"
            placeholder="job-stream-0001"
          />
          <button
            onClick={startStreaming}
            disabled={isStreaming}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 transition-all flex items-center gap-1.5"
          >
            <span>{isStreaming ? 'Streaming...' : '▶ Run Live Stream'}</span>
          </button>
        </div>
      </div>

      <RunTimeline events={events} activeNode={activeNode} isStreaming={isStreaming} />
    </div>
  );
};

