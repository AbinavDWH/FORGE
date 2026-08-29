import { useEffect, useState } from 'react';
import { api } from '../api';

export default function ReviewTray() {
  const [items, setItems] = useState([]);
  const [allTasks, setAllTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [drafts, setDrafts] = useState({});

  const loadData = async () => {
    setLoading(true);
    try {
      const [trayData, tasksData] = await Promise.all([
        api.getReviewTray(),
        api.getTasks()
      ]);
      setItems(trayData);
      setAllTasks(tasksData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const startEdit = (item) => {
    setEditingId(item.ingestion_id);
    setDrafts(prev => ({
      ...prev,
      [item.ingestion_id]: {
        extraction: { ...item.extraction },
        task_id: item.match.matched_task_id || ''
      }
    }));
  };

  const updateDraftField = (id, field, value) => {
    setDrafts(prev => ({
      ...prev,
      [id]: { ...prev[id], extraction: { ...prev[id].extraction, [field]: value } }
    }));
  };

  const updateDraftTask = (id, taskId) => {
    setDrafts(prev => ({ ...prev, [id]: { ...prev[id], task_id: taskId } }));
  };

  const handleAction = async (item, action) => {
    const isEditing = editingId === item.ingestion_id;
    try {
      if (action === 'approve') {
        const payload = { approved_by: 'Priya' };
        if (isEditing && drafts[item.ingestion_id]) {
          payload.corrected_extraction = drafts[item.ingestion_id].extraction;
          payload.overridden_task_id = drafts[item.ingestion_id].task_id;
        }
        await api.approveUpdate(item.ingestion_id, payload);
      } else {
        await api.rejectUpdate(item.ingestion_id, 'Priya');
      }
      setEditingId(null);
      loadData();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  if (loading) return (
    <div className="px-10 py-20 text-center text-forge-muted text-sm">Loading review tray…</div>
  );

  return (
    <div className="min-h-full">
      {/* Header */}
      <header className="px-10 py-8 border-b border-forge-border">
        <div className="label mb-2">Approvals</div>
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-semibold tracking-tightest">Manager Review Tray</h1>
            <p className="text-sm text-forge-muted mt-2 max-w-xl">
              Verify, correct, and commit field updates to the master schedule.
            </p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-light tracking-tightest">{items.length}</div>
            <div className="label mt-1">Pending</div>
          </div>
        </div>
      </header>

      <section className="px-10 py-10">
        {items.length === 0 ? (
          <div className="hairline p-20 text-center">
            <div className="swiss-dot mx-auto mb-4"></div>
            <div className="text-sm text-forge-muted">Inbox Zero. All field updates reconciled.</div>
          </div>
        ) : (
          <div className="space-y-6">
            {items.map(item => (
              <article key={item.ingestion_id} className="hairline">
                {/* Item Header */}
                <header className="px-6 py-4 border-b border-forge-border bg-forge-soft flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-2 h-2 bg-forge-accent"></div>
                    <span className="font-mono text-xs text-forge-fg">{item.ingestion_id}</span>
                    <span className="text-xs text-forge-muted">·</span>
                    <span className="text-xs uppercase tracking-wider text-forge-muted">{item.status.replace('_', ' ')}</span>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <div className="label mb-0.5">Confidence</div>
                      <div className={`text-lg font-light tabular-nums ${item.confidence.score >= 85 ? '' : 'text-forge-accent'}`}>
                        {item.confidence.score}<span className="text-xs text-forge-muted">%</span>
                      </div>
                    </div>
                    <button
                      onClick={() => editingId === item.ingestion_id ? setEditingId(null) : startEdit(item)}
                      className="text-xs uppercase tracking-wider hover:text-forge-accent transition-colors px-3 py-1.5 border border-forge-border hover:border-forge-accent"
                    >
                      {editingId === item.ingestion_id ? 'Cancel' : 'Edit'}
                    </button>
                  </div>
                </header>

                {/* Synthetic Media Alert */}
                {item.ai_generation_risk === 'high' && (
                  <div className="px-6 py-3 border-b border-forge-accent bg-forge-accent/5 flex items-center gap-3">
                    <div className="w-2 h-2 bg-forge-accent"></div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-forge-accent">
                      Synthetic Media Detected · Evidence Blocked · Manual Review Required
                    </span>
                  </div>
                )}

                {/* Body: Two-column layout */}
                <div className="grid grid-cols-12">
                  {/* Left: Evidence */}
                  <div className="col-span-5 p-6 border-r border-forge-border">
                    <div className="label mb-3">Evidence</div>

                    {item.evidence_url ? (
                      <div className="mb-4">
                        <img
                          src={`http://127.0.0.1:8000${item.evidence_url}`}
                          alt="Field evidence"
                          className="w-full h-48 object-cover border border-forge-border"
                        />
                        <div className="flex items-center gap-2 mt-2 text-[10px] uppercase tracking-wider text-forge-muted">
                          <span>{item.media_type}</span>
                          <span>·</span>
                          <span className="font-mono">{item.ingestion_id}</span>
                        </div>
                      </div>
                    ) : (
                      <div className="h-48 border border-dashed border-forge-border flex items-center justify-center mb-4">
                        <span className="text-xs text-forge-muted uppercase tracking-wider">No Media</span>
                      </div>
                    )}

                    <div className="label mb-2">Raw Input</div>
                    <p className="text-sm leading-relaxed text-forge-fg">
                      "{item.extraction.raw_text || <span className="text-forge-muted">No text extracted</span>}"
                    </p>

                    {item.extraction.language_hint && (
                      <div className="mt-4 text-[10px] uppercase tracking-wider text-forge-muted">
                        Language: <span className="text-forge-fg">{item.extraction.language_hint}</span>
                      </div>
                    )}
                  </div>

                  {/* Right: Extracted Data */}
                  <div className="col-span-7 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="label">Extracted Fields</div>
                      <div className="text-[10px] uppercase tracking-wider text-forge-muted">
                        {editingId === item.ingestion_id ? 'Edit Mode' : 'Read Only'}
                      </div>
                    </div>

                    {editingId === item.ingestion_id ? (
                      <div className="space-y-4">
                        <div>
                          <label className="label block mb-1">Spatial Zone</label>
                          <input
                            className="w-full px-3 py-2 text-sm border border-forge-border focus:border-forge-accent outline-none"
                            value={drafts[item.ingestion_id].extraction.spatial_zone || ''}
                            onChange={e => updateDraftField(item.ingestion_id, 'spatial_zone', e.target.value)}
                            placeholder="Zone B"
                          />
                        </div>
                        <div>
                          <label className="label block mb-1">Component</label>
                          <input
                            className="w-full px-3 py-2 text-sm border border-forge-border focus:border-forge-accent outline-none"
                            value={drafts[item.ingestion_id].extraction.component || ''}
                            onChange={e => updateDraftField(item.ingestion_id, 'component', e.target.value)}
                            placeholder="Pier 14"
                          />
                        </div>
                        <div>
                          <label className="label block mb-1">Action</label>
                          <input
                            className="w-full px-3 py-2 text-sm border border-forge-border focus:border-forge-accent outline-none"
                            value={drafts[item.ingestion_id].extraction.action || ''}
                            onChange={e => updateDraftField(item.ingestion_id, 'action', e.target.value)}
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="label block mb-1">Status</label>
                            <select
                              className="w-full px-3 py-2 text-sm border border-forge-border focus:border-forge-accent outline-none bg-white"
                              value={drafts[item.ingestion_id].extraction.status || ''}
                              onChange={e => updateDraftField(item.ingestion_id, 'status', e.target.value)}
                            >
                              <option value="">—</option>
                              <option value="In Progress">In Progress</option>
                              <option value="Completed">Completed</option>
                            </select>
                          </div>
                          <div>
                            <label className="label block mb-1">% Complete</label>
                            <input
                              type="number"
                              className="w-full px-3 py-2 text-sm border border-forge-border focus:border-forge-accent outline-none tabular-nums"
                              value={drafts[item.ingestion_id].extraction.percent_complete || 0}
                              onChange={e => updateDraftField(item.ingestion_id, 'percent_complete', parseInt(e.target.value) || 0)}
                            />
                          </div>
                        </div>
                        <div className="pt-4 border-t border-forge-border">
                          <label className="label block mb-1">Target Schedule Task</label>
                          <select
                            className="w-full px-3 py-2 text-sm border border-forge-border focus:border-forge-accent outline-none bg-white font-mono"
                            value={drafts[item.ingestion_id].task_id || ''}
                            onChange={e => updateDraftTask(item.ingestion_id, e.target.value)}
                          >
                            <option value="">— select —</option>
                            {allTasks.map(t => (
                              <option key={t.activity_id} value={t.activity_id}>
                                {t.activity_id} — {t.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="grid grid-cols-2 gap-y-4 gap-x-6">
                          {[
                            { label: 'Zone', value: item.extraction.spatial_zone },
                            { label: 'Discipline', value: item.extraction.discipline },
                            { label: 'Component', value: item.extraction.component },
                            { label: 'Action', value: item.extraction.action },
                            { label: 'Status', value: item.extraction.status },
                            { label: '% Complete', value: item.extraction.percent_complete, mono: true },
                          ].map((f, i) => (
                            <div key={i} className="swiss-rule pt-3">
                              <div className="label mb-1">{f.label}</div>
                              <div className={`text-sm ${f.mono ? 'font-mono' : ''} ${!f.value ? 'text-forge-muted italic' : ''}`}>
                                {f.value ?? '—'}
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="mt-5 pt-5 border-t border-forge-border">
                          <div className="label mb-2">Matched Task</div>
                          <div className="flex items-center gap-2">
                            <span className="swiss-dot"></span>
                            <span className="font-mono text-sm">
                              {item.match.matched_task_id || <span className="text-forge-muted italic">no match</span>}
                            </span>
                            <span className="text-xs text-forge-muted">·</span>
                            <span className="text-sm">{item.match.task_name || '—'}</span>
                          </div>
                          <div className="text-xs text-forge-muted mt-1">{item.match.match_reason}</div>
                        </div>

                        <div className="mt-5 pt-5 border-t border-forge-border">
                          <div className="label mb-2">Explanation</div>
                          <ul className="space-y-1">
                            {item.confidence.explanation.map((exp, i) => (
                              <li
                                key={i}
                                className={`text-xs flex gap-2 ${
                                  exp.includes('synthetic') || exp.includes('blocked')
                                    ? 'text-forge-accent font-semibold'
                                    : 'text-forge-muted'
                                }`}
                              >
                                <span className="text-forge-accent">→</span>
                                <span>{exp}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Footer Actions */}
                <footer className="px-6 py-4 border-t border-forge-border bg-forge-soft flex items-center justify-end gap-3">
                  <button
                    onClick={() => handleAction(item, 'reject')}
                    className="px-5 py-2 text-xs uppercase tracking-wider border border-forge-border hover:border-forge-accent hover:text-forge-accent transition-colors"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleAction(item, 'approve')}
                    disabled={item.ai_generation_risk === 'high'}
                    className="px-5 py-2 text-xs uppercase tracking-wider bg-forge-accent text-white hover:bg-rose-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed disabled:bg-forge-muted"
                  >
                    {editingId === item.ingestion_id ? 'Commit Correction →' : 'Approve & Commit →'}
                  </button>
                </footer>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}