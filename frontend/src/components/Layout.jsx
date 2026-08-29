import { Outlet, NavLink } from 'react-router-dom';
import { LayoutDashboard, Inbox, GanttChart, ScrollText } from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/review', label: 'Review Tray', icon: Inbox },
  { path: '/schedule', label: 'Schedule / Gantt', icon: GanttChart },
  { path: '/audit', label: 'Audit Log', icon: ScrollText },
];

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-forge-panel border-r border-forge-border flex flex-col">
        <div className="p-6 border-b border-forge-border">
          <h1 className="text-2xl font-bold text-white tracking-tight">FORGE</h1>
          <p className="text-xs text-gray-400 mt-1">Reconciliation Engine</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-forge-accent text-white font-medium' 
                    : 'text-gray-400 hover:bg-slate-700 hover:text-white'
                }`
              }
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8 bg-forge-bg">
        <Outlet />
      </main>
    </div>
  );
}