import { useEffect, useState } from 'react';
import { api } from '../api';

export default function ScheduleGantt() {
  const [tasks, setTasks] = useState([]);
  const [timeline, setTimeline] = useState({ min: null, max: null, totalDays: 0 });

  useEffect(() => {
    api.getTasks().then(data => {
      setTasks(data);
      calculateTimeline(data);
    });
  }, []);

  const calculateTimeline = (tasks) => {
    let minDate = new Date(8640000000000000); // Max date
    let maxDate = new Date(-8640000000000000); // Min date

    tasks.forEach(t => {
      const dates = [
        t.planned_start, t.planned_finish, 
        t.actual_start, t.actual_finish
      ].filter(Boolean).map(d => new Date(d));

      dates.forEach(d => {
        if (d < minDate) minDate = d;
        if (d > maxDate) maxDate = d;
      });
    });

    // Add 2 days padding
    minDate.setDate(minDate.getDate() - 2);
    maxDate.setDate(maxDate.getDate() + 2);

    const totalDays = Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24));
    setTimeline({ min: minDate, max: maxDate, totalDays });
  };

  const getBarStyle = (start, end) => {
    if (!start) return { display: 'none' };
    const startDate = new Date(start);
    const endDate = end ? new Date(end) : new Date(); // If in progress, draw to today
    
    const startOffset = Math.ceil((startDate - timeline.min) / (1000 * 60 * 60 * 24));
    const duration = Math.max(1, Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)));

    return {
      left: `${(startOffset / timeline.totalDays) * 100}%`,
      width: `${(duration / timeline.totalDays) * 100}%`
    };
  };

  if (!timeline.min) return <div className="text-gray-400">Loading schedule...</div>;

  return (
    <div>
      <h2 className="text-3xl font-bold text-white mb-2">Schedule Reconciliation</h2>
      <p className="text-gray-400 mb-8">Baseline (Gray) vs Actual (Blue/Green) progress mapped directly from API.</p>

      <div className="bg-forge-panel border border-forge-border rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <div className="min-w-[1000px]">
            {/* Header */}
            <div className="grid grid-cols-12 border-b border-forge-border bg-slate-800/50 text-xs font-bold text-gray-400 uppercase tracking-wider">
              <div className="col-span-3 p-4 border-r border-forge-border">Activity / WBS</div>
              <div className="col-span-9 p-4 relative h-10">
                <div className="absolute inset-0 flex justify-between px-4 text-gray-500">
                  <span>{timeline.min.toLocaleDateString()}</span>
                  <span>{timeline.max.toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            {/* Rows */}
            {tasks.map(task => (
              <div key={task.activity_id} className="grid grid-cols-12 border-b border-forge-border hover:bg-slate-800/30 transition-colors group">
                <div className="col-span-3 p-4 border-r border-forge-border">
                  <div className="font-semibold text-white text-sm">{task.name}</div>
                  <div className="text-xs text-gray-500 font-mono">{task.wbs_code}</div>
                  <div className="text-xs text-gray-400 mt-1">{task.percent_complete}% Complete</div>
                </div>
                
                <div className="col-span-9 p-4 relative h-20 flex items-center">
                  {/* Baseline Bar (Gray) */}
                  <div 
                    className="absolute h-4 bg-gray-600/50 border border-gray-500 rounded-sm z-10"
                    style={getBarStyle(task.planned_start, task.planned_finish)}
                    title={`Baseline: ${task.planned_start} to ${task.planned_finish}`}
                  />
                  
                  {/* Actual Bar (Blue/Green) */}
                  {task.actual_start && (
                    <div 
                      className={`absolute h-6 rounded-md shadow-md z-20 flex items-center px-2 text-xs font-bold text-white ${
                        task.status === 'completed' ? 'bg-emerald-500' : 'bg-blue-500'
                      }`}
                      style={getBarStyle(task.actual_start, task.actual_finish)}
                      title={`Actual: ${task.actual_start} to ${task.actual_finish || 'Ongoing'}`}
                    >
                      {task.percent_complete}%
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="mt-4 flex gap-6 text-sm text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-4 h-3 bg-gray-600/50 border border-gray-500 rounded-sm"></div>
          <span>Baseline Plan</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded-sm"></div>
          <span>Actual Progress (In Progress)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-emerald-500 rounded-sm"></div>
          <span>Actual Progress (Completed)</span>
        </div>
      </div>
    </div>
  );
}