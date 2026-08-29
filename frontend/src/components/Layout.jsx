import { Outlet, NavLink } from 'react-router-dom';
import { LayoutDashboard, Inbox, GanttChart, ScrollText } from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/review', label: 'Review Tray', icon: Inbox },
  { path: '/schedule', label: 'Schedule', icon: GanttChart },
  { path: '/audit', label: 'Audit', icon: ScrollText },
];

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-forge-bg text-forge-fg">
      {/* Sidebar */}
      <aside className="w-60 border-r border-forge-border flex flex-col bg-forge-bg">
        <div className="px-6 py-5 border-b border-forge-border flex items-center gap-2">
          <div className="w-3 h-3 bg-forge-accent"></div>
          <span className="text-sm font-semibold tracking-tight">FORGE</span>
          <span className="text-[10px] uppercase tracking-wider text-forge-muted ml-auto">v0.3</span>
        </div>

        <nav className="flex-1 py-3">
          <div className="px-6 py-2 label">Navigation</div>
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `group flex items-center gap-3 px-6 py-2.5 text-sm transition-colors border-l-2 ${
                  isActive
                    ? 'text-forge-fg border-forge-accent bg-forge-soft'
                    : 'text-forge-muted border-transparent hover:text-forge-fg hover:bg-forge-soft'
                }`
              }
            >
              <Icon size={14} strokeWidth={1.5} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="px-6 py-4 border-t border-forge-border">
          <div className="label mb-1">Operator</div>
          <div className="text-sm font-medium">Priya Sharma</div>
          <div className="text-xs text-forge-muted mt-0.5">Planning Lead · NRL</div>
        </div>

        <div className="px-6 py-3 border-t border-forge-border flex items-center gap-2 text-[10px] uppercase tracking-wider text-forge-muted">
          <div className="w-1.5 h-1.5 bg-forge-accent"></div>
          System Nominal
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}