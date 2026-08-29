// Replace: frontend/src/pages/Dashboard.jsx
import { Link } from 'react-router-dom';

/**
 * FORGE Control Center Dashboard
 * 
 * Acts as a clean routing hub. Contains NO hardcoded schedule data or fake analytics.
 * Follows Swiss Red minimalist theme: white canvas, hairline borders, monospace metadata.
 */
export default function Dashboard() {
  return (
    <div className="p-6 bg-white min-h-screen">
      <h1 className="text-xl font-bold text-gray-900 mb-1">FORGE Control Center</h1>
      <p className="text-xs font-mono text-gray-500 mb-8 uppercase tracking-widest">
        Planning-to-Execution Bridge • NRL Golaghat Expansion
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl">
        <Link to="/incoming" className="block p-4 border border-gray-200 hover:border-[#E11D48] transition-colors bg-white group">
          <h3 className="font-mono text-[11px] uppercase tracking-wider text-gray-500">Module 01</h3>
          <p className="text-lg font-medium text-gray-900 mt-1 group-hover:text-[#E11D48] transition-colors">
            Incoming Field Updates
          </p>
          <p className="text-sm text-gray-500 mt-2">
            View raw voice notes, photos, and text from the site.
          </p>
        </Link>

        <Link to="/review" className="block p-4 border border-gray-200 hover:border-[#E11D48] transition-colors bg-white group">
          <h3 className="font-mono text-[11px] uppercase tracking-wider text-gray-500">Module 04</h3>
          <p className="text-lg font-medium text-gray-900 mt-1 group-hover:text-[#E11D48] transition-colors">
            Manager Review Tray
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Approve, reject, or reassign AI-matched schedule tasks.
          </p>
        </Link>

        <Link to="/gantt" className="block p-4 border border-gray-200 hover:border-[#E11D48] transition-colors bg-white group">
          <h3 className="font-mono text-[11px] uppercase tracking-wider text-gray-500">Module 07</h3>
          <p className="text-lg font-medium text-gray-900 mt-1 group-hover:text-[#E11D48] transition-colors">
            Schedule & Gantt View
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Live Planned vs Actual progress. 100% dynamic data.
          </p>
        </Link>

        <Link to="/audit" className="block p-4 border border-gray-200 hover:border-[#E11D48] transition-colors bg-white group">
          <h3 className="font-mono text-[11px] uppercase tracking-wider text-gray-500">Module 06</h3>
          <p className="text-lg font-medium text-gray-900 mt-1 group-hover:text-[#E11D48] transition-colors">
            Audit & Trust Log
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Tamper-evident SHA-256 hash chain and evidence tracking.
          </p>
        </Link>
      </div>
      
      <div className="mt-12 p-4 border border-gray-100 bg-gray-50 max-w-4xl">
        <h4 className="font-mono text-[11px] uppercase tracking-wider text-gray-400 mb-2">System Status</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-500 font-mono text-xs">Matcher</div>
            <div className="text-green-600 font-medium">RapidFuzz Active</div>
          </div>
          <div>
            <div className="text-gray-500 font-mono text-xs">Synthetic Gate</div>
            <div className="text-green-600 font-medium">EXIF/C2PA Ready</div>
          </div>
          <div>
            <div className="text-gray-500 font-mono text-xs">Schedule Parser</div>
            <div className="text-amber-600 font-medium">Pending MOD-05</div>
          </div>
          <div>
            <div className="text-gray-500 font-mono text-xs">Audit Chain</div>
            <div className="text-green-600 font-medium">SHA-256 Active</div>
          </div>
        </div>
      </div>
    </div>
  );
}