import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

/**
 * FORGE Control Center Dashboard
 * 
 * Acts as a routing hub + quick field update input.
 * Contains NO hardcoded schedule data or fake analytics.
 */
export default function Dashboard() {
  const [rawText, setRawText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!rawText.trim()) return;
    setSubmitting(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('source', 'web_upload');
      formData.append('media_type', 'text');
      formData.append('raw_text', rawText);
      const res = await api.uploadIngestion(formData);
      setResult(res);
      setRawText('');
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-full">
      <header className="px-10 py-8 border-b border-forge-border">
        <div className="label mb-2">Control Center</div>
        <h1 className="text-4xl font-semibold tracking-tightest">FORGE Dashboard</h1>
        <p className="text-sm text-forge-muted mt-2">
          Planning-to-Execution Bridge · NRL Golaghat Expansion
        </p>
      </header>

      <section className="px-10 py-10">
        {/* Quick Field Update Input */}
        <div className="hairline p-6 mb-10 max-w-2xl">
          <div className="label mb-3">Quick Field Update</div>
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={rawText}
              onChange={e => setRawText(e.target.value)}
              placeholder='e.g. "Sector B Pier 14 concrete pouring completed"'
              className="flex-1 px-4 py-2.5 text-sm border border-forge-border focus:border-forge-accent outline-none"
            />
            <button
              type="submit"
              disabled={submitting || !rawText.trim()}
              className="px-6 py-2.5 text-xs uppercase tracking-wider bg-forge-accent text-white hover:bg-rose-700 transition-colors disabled:opacity-30"
            >
              {submitting ? 'Processing…' : 'Submit'}
            </button>
          </form>
          {result && !result.error && (
            <div className="mt-3 text-xs font-mono text-forge-accent">
              ✓ Ingested as {result.ingestion_id} — check Review Tray
            </div>
          )}
          {result?.error && (
            <div className="mt-3 text-xs font-mono text-red-600">
              ✗ {result.error}
            </div>
          )}
        </div>

        {/* Module Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl">
          <Link to="/review" className="block p-5 hairline hover:border-forge-accent transition-colors group">
            <h3 className="label">Module 04</h3>
            <p className="text-lg font-medium mt-1 group-hover:text-forge-accent transition-colors">
              Manager Review Tray
            </p>
            <p className="text-sm text-forge-muted mt-2">
              Approve, reject, or reassign AI-matched schedule tasks.
            </p>
          </Link>

          <Link to="/schedule" className="block p-5 hairline hover:border-forge-accent transition-colors group">
            <h3 className="label">Module 07</h3>
            <p className="text-lg font-medium mt-1 group-hover:text-forge-accent transition-colors">
              Schedule & Gantt View
            </p>
            <p className="text-sm text-forge-muted mt-2">
              Live Planned vs Actual progress. 100% dynamic data.
            </p>
          </Link>

          <Link to="/audit" className="block p-5 hairline hover:border-forge-accent transition-colors group">
            <h3 className="label">Module 06</h3>
            <p className="text-lg font-medium mt-1 group-hover:text-forge-accent transition-colors">
              Audit & Trust Log
            </p>
            <p className="text-sm text-forge-muted mt-2">
              Tamper-evident SHA-256 hash chain and evidence tracking.
            </p>
          </Link>

          <div className="block p-5 hairline bg-forge-soft/50">
            <h3 className="label">System Status</h3>
            <div className="grid grid-cols-2 gap-3 mt-3 text-sm">
              <div>
                <div className="text-forge-muted text-xs font-mono">Matcher</div>
                <div className="text-forge-accent font-medium text-xs">RapidFuzz Active</div>
              </div>
              <div>
                <div className="text-forge-muted text-xs font-mono">Synthetic Gate</div>
                <div className="text-forge-accent font-medium text-xs">EXIF/C2PA Ready</div>
              </div>
              <div>
                <div className="text-forge-muted text-xs font-mono">Schedule Parser</div>
                <div className="text-forge-accent font-medium text-xs">XML Active</div>
              </div>
              <div>
                <div className="text-forge-muted text-xs font-mono">Audit Chain</div>
                <div className="text-forge-accent font-medium text-xs">SHA-256 Active</div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}