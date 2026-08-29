import { useEffect, useState } from 'react';
import { api } from '../api';
import { CheckCircle, AlertTriangle, Clock } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({ tasks: 0, pending: 0, completed: 0 });

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [tasks, tray] = await Promise.all([
          api.getTasks(),
          api.getReviewTray()
        ]);
        setStats({
          tasks: tasks.length,
          pending: tray.length,
          completed: tasks.filter(t => t.status === 'completed').length
        });
      } catch (err) {
        console.error(err);
      }
    };
    loadStats();
  }, []);

  const cards = [
    { label: 'Active Schedule Tasks', value: stats.tasks, icon: Clock, color: 'text-blue-400' },
    { label: 'Completed Tasks', value: stats.completed, icon: CheckCircle, color: 'text-emerald-400' },
    { label: 'Pending Review', value: stats.pending, icon: AlertTriangle, color: 'text-amber-400' },
  ];

  return (
    <div>
      <h2 className="text-3xl font-bold text-white mb-8">Project Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((card, i) => (
          <div key={i} className="bg-forge-panel border border-forge-border p-6 rounded-xl shadow-lg">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-400 text-sm font-medium">{card.label}</p>
                <p className="text-4xl font-bold text-white mt-2">{card.value}</p>
              </div>
              <card.icon className={card.color} size={32} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}