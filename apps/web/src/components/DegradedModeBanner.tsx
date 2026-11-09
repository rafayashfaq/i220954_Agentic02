import React from 'react';

interface DegradedModeBannerProps {
  isDegraded: boolean;
  onRecover: () => void;
}

export const DegradedModeBanner: React.FC<DegradedModeBannerProps> = ({ isDegraded, onRecover }) => {
  if (!isDegraded) return null;

  return (
    <div className="bg-amber-500/10 border-b border-amber-500/30 text-amber-200 px-4 py-2.5 text-xs sm:text-sm font-medium flex items-center justify-between animate-fadeIn">
      <div className="flex items-center gap-2.5">
        <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
        <span>
          <strong>Marketplace Degraded Mode Active:</strong> Marketplace server is currently unreachable or experiencing 503 limits.
          External proposals and messages are queued idempotently and will be automatically delivered upon recovery.
        </span>
      </div>
      <button
        onClick={onRecover}
        className="px-2.5 py-1 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 rounded text-amber-100 text-xs font-semibold whitespace-nowrap ml-3"
      >
        Restore Normal Service
      </button>
    </div>
  );
};

