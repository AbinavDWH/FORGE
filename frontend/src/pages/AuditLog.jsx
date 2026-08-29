import { useEffect, useState } from 'react';
import { api } from '../api';
import { Link2 } from 'lucide-react';

export default function AuditLog() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    api.getAuditLogs().then(setLogs);
  }, []);

  return (
    <div>
      <h2 className="text-3xl font-bold text-white mb-2">Tamper-Evident Audit Chain</h2>
      <p className="text-gray-400 mb-8">SHA-256 hash-chained records of all schedule modifications.</p>

      <div className="bg-forge-panel border border-forge-border rounded-xl overflow-hidden shadow-lg">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50 text-xs text-gray-400 uppercase tracking-wider">
            <tr>
              <th className="p-4 border-b border-forge-border">Index</th>
              <th className="p-4 border-b border-forge-border">Timestamp</th>
              <th className="p-4 border-b border-forge-border">Action / WBS</th>
              <th className="p-4 border-b border-forge-border">Actor</th>
              <th className="p-4 border-b border-forge-border">Hash Chain</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forge-border">
            {logs.map(log => (
              <tr key={log.log_index} className="hover:bg-slate-800/30 transition-colors">
                <td className="p-4 font-mono text-gray-400">#{log.log_index}</td>
                <td className="p-4 text-gray-300">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="p-4">
                  <div className="font-semibold text-white">{log.action_performed}</div>
                  <div className="text-xs text-gray-500 font-mono">{log.wbs_activity_id}</div>
                </td>
                <td className="p-4 text-blue-400 font-medium">{log.approved_by}</td>
                <td className="p-4 font-mono text-xs text-gray-500">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-gray-400">Prev:</span> 
                    <span className="truncate max-w-[150px]">{log.previous_hash}</span>
                  </div>
                  <div className="flex items-center gap-2 text-emerald-500">
                    <Link2 size={12} />
                    <span className="truncate max-w-[150px]">{log.current_hash}</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}