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
    let minDate = new Date(8640000000000000);
    let maxDate = new Date(-8640000000000000);

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

    minDate.setDate(minDate.getDate() - 2);
    maxDate.setDate(maxDate.getDate() + 2);
    const totalDays = Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24));
    setTimeline({ min: minDate, max: maxDate, totalDays });
  };

  const getBarStyle = (start, end) => {
    if (!start) return { display: 'none' };
    const s = new Date(start);
    const e = end ? new Date(end) : new Date();
    const offset = Math.ceil((s - timeline.min) / (1000 * 60 * 60 * 24));
    const dur = Math.max(1, Math.ceil((e - s) / (1000 * 60 * 60 * 24)));
    return {
      left: `${(offset / timeline.totalDays) * 100}%`,
      width: `${(dur / timeline.totalDays) * 100}%`
    };
  };

  const fmt = (d) => new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });

  if (!timeline.min) return <div className="px-10 py-20 text-center text-forge-muted text-sm">Loading schedule…</div>;

  return (
    <div className="min-h-full">
      <header className="px-10 py-8 border-b border-forge-border">
        <div className="label mb-2">Master Schedule</div>
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-semibold tracking-tightest">Schedule Reconciliation</h1>
            <p className="text-sm text-forge-muted mt-2">
              Baseline vs Actual. Rendered from <span className="font-mono">/api/schedule/tasks</span>.
            </p>
          </div>
          <div className="flex gap-8 text-xs">
            <div>
              <div className="label mb-1">Start</div>
              <div className="font-mono">{fmt(timeline.min)}</div>
            </div>
            <div>
              <div className="label mb-1">End</div>
              <div className="font-mono">{fmt(timeline.max)}</div>
            </div>
            <div>
              <div className="label mb-1">Duration</div>
              <div className="font-mono tabular-nums">{timeline.totalDays}d</div>
            </div>
          </div>
        </div>
      </header>

      <section className="px-10 py-10">
        <div className="hairline">
          {/* Header row */}
          <div className="grid grid-cols-12 bg-forge-soft border-b border-forge-border">
            <div className="col-span-4 px-5 py-3 border-r border-forge-border">
              <div className="label-wide">Activity / WBS</div>
            </div>
            <div className="col-span-8 px-5 py-3 flex justify-between">
              <div className="label-wide">Timeline</div>
              <div className="flex gap-8 text-[10px] uppercase tracking-wider text-forge-muted">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-0.5 bg-forge-muted"></div> Baseline
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-1.5 bg-forge-accent"></div> Actual
                </div>
              </div>
            </div>
          </div>

          {/* Task rows */}
          {tasks.map((task, i) => (
            <div
              key={task.activity_id}
              className={`grid grid-cols-12 border-b border-forge-border last:border-b-0 hover:bg-forge-soft transition-colors ${i % 2 === 1 ? 'bg-forge-soft/40' : ''}`}
            >
              <div className="col-span-4 px-5 py-4 border-r border-forge-border">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{task.name}</div>
                    <div className="text-[10px] uppercase tracking-wider text-forge-muted mt-1 font-mono">
                      {task.wbs_code}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className={`text-sm font-light tabular-nums ${task.percent_complete === 100 ? 'text-forge-accent' : ''}`}>
                      {task.percent_complete}<span className="text-[10px] text-forge-muted">%</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3 mt-2 text-[10px] text-forge-muted">
                  <span>{task.zone}</span>
                  <span>·</span>
                  <span>{task.discipline}</span>
                  <span>·</span>
                  <span className="uppercase tracking-wider">{task.status}</span>
                </div>
              </div>

              <div className="col-span-8 px-5 py-4 relative h-20 flex items-center">
                {/* Baseline bar */}
                <div
                  className="absolute h-[3px] bg-forge-muted/40"
                  style={getBarStyle(task.planned_start, task.planned_finish)}
                />
                {/* Actual bar */}
                {task.actual_start && (
                  <div
                    className={`absolute h-2 ${task.status === 'completed' ? 'bg-forge-accent' : 'bg-forge-accent/60'}`}
                    style={getBarStyle(task.actual_start, task.actual_finish)}
                  >
                    <div className="absolute -top-4 left-0 text-[10px] font-mono text-forge-accent whitespace-nowrap">
                      {task.actual_finish ? fmt(task.actual_finish) : 'ongoing'}
                    </div>
                  </div>
                )}
                {/* Planned dates */}
                <div className="absolute top-1 left-5 text-[10px] font-mono text-forge-muted">
                  {fmt(task.planned_start)} → {fmt(task.planned_finish)}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex items-center gap-8 text-[10px] uppercase tracking-wider text-forge-muted">
          <span>Rendered: {new Date().toLocaleTimeString()}</span>
          <span>·</span>
          <span>{tasks.length} activities</span>
          <span>·</span>
          <span>{tasks.filter(t => t.status === 'completed').length} complete</span>
        </div>
      </section>
    </div>
  );
}