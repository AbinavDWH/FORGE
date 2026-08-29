import { useEffect, useState } from 'react';
import { api } from '../api';

export default function AuditLog() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    api.getAuditLogs().then(setLogs);
  }, []);

  return (
    <div className="min-h-full">
      <header className="px-10 py-8 border-b border-forge-border">
        <div className="label mb-2">Integrity</div>
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-semibold tracking-tightest">Audit Chain</h1>
            <p className="text-sm text-forge-muted mt-2 max-w-xl">
              SHA-256 hash-chained record of every schedule modification. Tamper-evident by construction.
            </p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-light tracking-tightest tabular-nums">{logs.length}</div>
            <div className="label mt-1">Records</div>
          </div>
        </div>
      </header>

      <section className="px-10 py-10">
        {logs.length === 0 ? (
          <div className="hairline p-20 text-center">
            <div className="swiss-dot mx-auto mb-4"></div>
            <div className="text-sm text-forge-muted">No audit records. Process a field update to begin the chain.</div>
          </div>
        ) : (
          <div className="hairline">
            {/* Header */}
            <div className="grid grid-cols-12 px-5 py-3 bg-forge-soft border-b border-forge-border">
              <div className="col-span-1 label-wide">#</div>
              <div className="col-span-2 label-wide">Timestamp</div>
              <div className="col-span-3 label-wide">Action</div>
              <div className="col-span-2 label-wide">Actor</div>
              <div className="col-span-1 label-wide">Score</div>
              <div className="col-span-3 label-wide">Chain</div>
            </div>

            {/* Rows */}
            {logs.slice().reverse().map((log, idx) => (
              <div
                key={log.log_index}
                className={`grid grid-cols-12 px-5 py-4 border-b border-forge-border last:border-b-0 hover:bg-forge-soft transition-colors ${idx % 2 === 1 ? 'bg-forge-soft/40' : ''}`}
              >
                <div className="col-span-1 font-mono text-xs tabular-nums text-forge-fg font-medium">
                  {String(log.log_index).padStart(3, '0')}
                </div>
                <div className="col-span-2">
                  <div className="text-xs font-mono">{new Date(log.timestamp).toLocaleString()}</div>
                  <div className="text-[10px] text-forge-muted mt-0.5 font-mono">{log.ingestion_id}</div>
                </div>
                <div className="col-span-3">
                  <div className="text-sm">{log.action_performed}</div>
                  <div className="text-[10px] uppercase tracking-wider text-forge-muted mt-1 font-mono">
                    {log.wbs_activity_id}
                  </div>
                </div>
                <div className="col-span-2">
                  <span className="text-xs uppercase tracking-wider">{log.approved_by}</span>
                  <div className="text-[10px] text-forge-muted mt-1">
                    cross-check: <span className="font-mono">{log.cross_check_status}</span>
                  </div>
                </div>
                <div className="col-span-1">
                  <div className="text-sm font-light tabular-nums">{log.confidence_score}<span className="text-[10px] text-forge-muted">%</span></div>
                </div>
                <div className="col-span-3 font-mono text-[10px]">
                  <div className="mb-1">
                    <span className="text-forge-muted">prev</span>{' '}
                    <span className="truncate">{log.previous_hash.slice(0, 16)}…</span>
                  </div>
                  <div className="text-forge-accent">
                    <span className="text-forge-fg">curr</span>{' '}
                    <span className="truncate">{log.current_hash.slice(0, 16)}…</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}