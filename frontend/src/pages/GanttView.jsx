// Replace: frontend/src/pages/GanttView.jsx
import { useState, useEffect } from 'react';

export default function GanttView() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cpmAlert, setCpmAlert] = useState(null);

  const fetchTasks = () => {
    fetch('/api/schedule/tasks')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch schedule');
        return res.json();
      })
      .then(data => {
        setTasks(data.tasks || []);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleMarkComplete = async (taskId, taskName) => {
    setCpmAlert(null);
    try {
      const res = await fetch('/api/schedule/update_actuals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_id: taskId,
          percent_complete: 100,
          ingestion_id: 'demo-simulation',
          approved_by: 'site_supervisor'
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        // CPM Guard Triggered!
        setCpmAlert({
          type: 'error',
          message: `CPM GUARD BLOCKED: ${errData.detail}`
        });
        setTimeout(() => setCpmAlert(null), 8000);
        return;
      }
      
      // Success
      setCpmAlert({
        type: 'success',
        message: `Schedule Updated: ${taskName} marked 100% complete. Audit hash generated.`
      });
      setTimeout(() => setCpmAlert(null), 5000);
      fetchTasks(); // Refresh Gantt
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="p-8 font-mono text-sm text-gray-500">Parsing MS Project XML...</div>;
  if (error) return <div className="p-8 font-mono text-sm text-rose-600">Error: {error}</div>;

  const allDates = tasks.flatMap(t => [
    t.planned_start ? new Date(t.planned_start) : null, 
    t.planned_finish ? new Date(t.planned_finish) : null,
    t.actual_start ? new Date(t.actual_start) : null,
    t.actual_finish ? new Date(t.actual_finish) : null
  ]).filter(Boolean);

  if (allDates.length === 0) return <div className="p-8 font-mono text-sm text-gray-500">Tasks found, but no valid dates provided.</div>;

  const minDate = new Date(Math.min(...allDates));
  const maxDate = new Date(Math.max(...allDates));
  minDate.setDate(minDate.getDate() - 2);
  maxDate.setDate(maxDate.getDate() + 2);

  const totalDays = Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24));
  const dayWidth = 14; 
  
  const getOffset = (dateStr) => {
    if (!dateStr) return 0;
    const date = new Date(dateStr);
    return Math.ceil((date - minDate) / (1000 * 60 * 60 * 24));
  };

  const getWidth = (startStr, endStr) => {
    if (!startStr || !endStr) return 0;
    const start = new Date(startStr);
    const end = new Date(endStr);
    return Math.max(1, Math.ceil((end - start) / (1000 * 60 * 60 * 24)));
  };

  return (
    <div className="p-6 bg-white min-h-screen">
      <h1 className="text-xl font-bold text-gray-900 mb-1">Schedule Dashboard</h1>
      <p className="text-xs font-mono text-gray-500 mb-6 uppercase tracking-widest">
        Planned vs Actual Progress • Dynamic MS Project XML Source
      </p>

      {cpmAlert && (
        <div className={`mb-4 p-3 border font-mono text-xs ${
          cpmAlert.type === 'error' 
            ? 'bg-rose-50 border-rose-200 text-[#E11D48]' 
            : 'bg-green-50 border-green-200 text-green-700'
        }`}>
          {cpmAlert.message}
        </div>
      )}

      <div className="border border-gray-200 bg-white overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="p-3 text-[11px] font-mono uppercase tracking-wider text-gray-500 w-64">WBS / Task Name</th>
              <th className="p-3 text-[11px] font-mono uppercase tracking-wider text-gray-500 w-24">Status</th>
              <th className="p-3 text-[11px] font-mono uppercase tracking-wider text-gray-500 w-32">Action</th>
              <th className="p-3 text-[11px] font-mono uppercase tracking-wider text-gray-500 min-w-[600px]">
                Timeline ({minDate.toLocaleDateString()} - {maxDate.toLocaleDateString()})
              </th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => {
              const plannedOffset = getOffset(task.planned_start);
              const plannedWidth = getWidth(task.planned_start, task.planned_finish);
              
              const actualOffset = getOffset(task.actual_start || task.planned_start);
              const actualWidth = getWidth(
                task.actual_start || task.planned_start, 
                task.actual_finish || task.planned_finish
              );

              const isDelayed = task.actual_finish && new Date(task.actual_finish) > new Date(task.planned_finish);

              return (
                <tr key={task.task_id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="p-3 align-top">
                    <div className="font-mono text-[11px] text-gray-400">{task.wbs_code || task.task_id}</div>
                    <div className="text-sm font-medium text-gray-900 mt-0.5">{task.task_name}</div>
                  </td>
                  <td className="p-3 align-top">
                    <span className={`inline-block px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider rounded-sm ${
                      task.status === 'Completed' ? 'bg-green-50 text-green-700 border border-green-200' : 
                      isDelayed ? 'bg-rose-50 text-rose-700 border border-rose-200' : 
                      'bg-gray-50 text-gray-600 border border-gray-200'
                    }`}>
                      {task.status || 'Active'}
                    </span>
                  </td>
                  <td className="p-3 align-top">
                    {task.percent_complete < 100 && (
                      <button 
                        onClick={() => handleMarkComplete(task.task_id, task.task_name)}
                        className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider border border-gray-300 hover:border-[#E11D48] hover:text-[#E11D48] transition-colors"
                      >
                        Mark 100%
                      </button>
                    )}
                  </td>
                  <td className="p-3 align-middle">
                    <div className="relative h-10 bg-gray-50 rounded-sm border border-gray-100" style={{ width: `${totalDays * dayWidth}px` }}>
                      {/* Planned Bar (Gray) */}
                      <div 
                        className="absolute top-1.5 h-3 bg-gray-300 rounded-sm"
                        style={{ 
                          left: `${plannedOffset * dayWidth}px`, 
                          width: `${plannedWidth * dayWidth}px` 
                        }}
                        title={`Planned: ${task.planned_start} to ${task.planned_finish}`}
                      />
                      
                      {/* Actual Bar (Swiss Red #E11D48 if delayed, Green if on track) */}
                      {(task.actual_start || task.percent_complete > 0) && (
                        <div 
                          className={`absolute top-5 h-3 rounded-sm ${isDelayed ? 'bg-[#E11D48]' : 'bg-green-500'}`}
                          style={{ 
                            left: `${actualOffset * dayWidth}px`, 
                            width: `${actualWidth * dayWidth}px` 
                          }}
                          title={`Actual: ${task.actual_start || task.planned_start} to ${task.actual_finish || 'Ongoing'}`}
                        />
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}