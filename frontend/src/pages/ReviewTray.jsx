import { useEffect, useState } from 'react';
import { api } from '../api';
import { Check, X, AlertOctagon } from 'lucide-react';

export default function ReviewTray() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await api.getReviewTray();
      setItems(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleAction = async (id, action) => {
    try {
      if (action === 'approve') await api.approveUpdate(id, 'Priya');
      else await api.rejectUpdate(id, 'Priya');
      loadData(); // Refresh tray
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  if (loading) return <div className="text-gray-400">Loading review tray...</div>;

  return (
    <div>
      <h2 className="text-3xl font-bold text-white mb-2">Manager Review Tray</h2>
      <p className="text-gray-400 mb-8">Updates requiring human verification before schedule commitment.</p>

      {items.length === 0 ? (
        <div className="bg-forge-panel border border-forge-border p-12 rounded-xl text-center text-gray-500">
          <CheckCircle className="mx-auto mb-4 text-emerald-500" size={48} />
          <p className="text-lg">Inbox Zero. All field updates are reconciled.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {items.map(item => (
            <div key={item.ingestion_id} className="bg-forge-panel border border-forge-border rounded-xl overflow-hidden shadow-lg">
              <div className="p-6 border-b border-forge-border flex justify-between items-start">
                <div>
                  <span className="px-2 py-1 bg-amber-500/20 text-amber-400 text-xs font-bold rounded uppercase tracking-wider">
                    {item.status.replace('_', ' ')}
                  </span>
                  <h3 className="text-xl font-semibold text-white mt-3">
                    {item.match.task_name || 'Unmatched Update'}
                  </h3>
                  <p className="text-sm text-gray-400 font-mono">{item.ingestion_id}</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-white">{item.confidence.score}<span className="text-lg text-gray-500">%</span></div>
                  <p className="text-xs text-gray-400">Confidence</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-forge-border">
                <div className="p-6">
                  <h4 className="text-sm font-bold text-gray-400 uppercase mb-3">Raw Field Input</h4>
                  <p className="text-gray-200 italic mb-4">"{item.extraction.raw_text}"</p>
                  
                  <h4 className="text-sm font-bold text-gray-400 uppercase mb-3">Extracted Data</h4>
                  <ul className="text-sm space-y-1 text-gray-300">
                    <li><span className="text-gray-500">Zone:</span> {item.extraction.spatial_zone}</li>
                    <li><span className="text-gray-500">Component:</span> {item.extraction.component}</li>
                    <li><span className="text-gray-500">Progress:</span> {item.extraction.percent_complete}%</li>
                  </ul>
                </div>

                <div className="p-6 bg-slate-800/50">
                  <h4 className="text-sm font-bold text-gray-400 uppercase mb-3">AI Explanation</h4>
                  <ul className="text-sm space-y-2 text-gray-300">
                    {item.confidence.explanation.map((exp, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-blue-400">•</span> {exp}
                      </li>
                    ))}
                    {item.review_message && (
                      <li className="flex gap-2 text-red-400 font-semibold mt-4">
                        <AlertOctagon size={16} className="mt-0.5" /> {item.review_message}
                      </li>
                    )}
                  </ul>
                </div>
              </div>

              <div className="p-4 bg-slate-900/50 flex justify-end gap-3 border-t border-forge-border">
                <button 
                  onClick={() => handleAction(item.ingestion_id, 'reject')}
                  className="px-4 py-2 bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30 rounded-lg font-medium transition flex items-center gap-2"
                >
                  <X size={18} /> Reject
                </button>
                <button 
                  onClick={() => handleAction(item.ingestion_id, 'approve')}
                  className="px-4 py-2 bg-emerald-500 text-white hover:bg-emerald-600 rounded-lg font-medium transition flex items-center gap-2 shadow-lg shadow-emerald-500/20"
                >
                  <Check size={18} /> Approve & Commit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}