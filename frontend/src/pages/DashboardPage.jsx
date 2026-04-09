import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard } from "../api/dashboardApi";
import { getExams } from "../api/examsApi";
import { getStatsOverview } from "../api/statsApi";
import { getTasks } from "../api/tasksApi";
import { useAuth } from "../context/AuthContext";

export default function DashboardPage() {
  const [data, setData] = useState({ upcoming_exams: [], todays_tasks: [] });
  const [stats, setStats] = useState({ subjects: [], overall_completion_rate_percent: 0 });
  const [calendarEvents, setCalendarEvents] = useState({});
  const [error, setError] = useState("");
  const { token } = useAuth();

  const buildCalendar = (exams, tasks) => {
    const byDate = {};
    exams.forEach((exam) => {
      byDate[exam.exam_date] = byDate[exam.exam_date] || [];
      byDate[exam.exam_date].push({
        type: "exam",
        text: `${exam.title} (${exam.subject_name})`,
        subjectId: exam.subject_id,
      });
    });
    tasks.forEach((task) => {
      byDate[task.due_date] = byDate[task.due_date] || [];
      byDate[task.due_date].push({
        type: "task",
        text: `${task.title} (${task.subject_name})`,
        subjectId: task.subject_id,
      });
    });
    setCalendarEvents(byDate);
  };

  useEffect(() => {
    const load = async () => {
      setError("");
      try {
        const [dashboard, overview, exams, tasks] = await Promise.all([
          getDashboard(token),
          getStatsOverview(token),
          getExams(token),
          getTasks(token),
        ]);
        setData(dashboard);
        setStats(overview);
        buildCalendar(exams, tasks);
      } catch (err) {
        setError(err.message);
      }
    };

    load();
  }, [token]);

  const today = new Date();
  const y = today.getFullYear();
  const m = today.getMonth();
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  const monthDays = Array.from({ length: daysInMonth }, (_, i) => {
    const day = i + 1;
    const date = new Date(y, m, day);
    const dateKey = date.toISOString().slice(0, 10);
    return { day, dateKey, events: calendarEvents[dateKey] || [] };
  });

  return (
    <div className="space-y">
      <section className="card stats-row">
        <div>
          <h3>Overall progress</h3>
          <p className="metric">{data.completion_rate_percent ?? 0}%</p>
          <p className="muted">
            Completed {data.completed_tasks ?? 0} of {data.total_tasks ?? 0} tasks
          </p>
        </div>
        <div>
          <h3>Subjects</h3>
          <p className="metric">{stats.total_subjects ?? 0}</p>
          <p className="muted">Track progress by each subject below</p>
        </div>
      </section>

      <div className="grid-two">
      <section className="card">
        <h2>Upcoming exams</h2>
        {error && <p className="error">{error}</p>}
        <ul>
          {data.upcoming_exams.map((exam) => (
            <li key={exam.id}>
              {exam.title} — {exam.exam_date} —{" "}
              <Link to={`/subjects/${exam.subject_id}`} className="subject-link">
                {exam.subject_name}
              </Link>
            </li>
          ))}
        </ul>
        {data.upcoming_exams.length === 0 && <p>No upcoming exams yet.</p>}
      </section>

      <section className="card">
        <h2>Today&apos;s tasks</h2>
        <ul>
          {data.todays_tasks.map((task) => (
            <li key={task.id}>
              {task.title} — <strong>{task.status}</strong> —{" "}
              <Link to={`/subjects/${task.subject_id}`} className="subject-link">
                {task.subject_name}
              </Link>
            </li>
          ))}
        </ul>
        {data.todays_tasks.length === 0 && <p>No tasks for today.</p>}
      </section>
      </div>

      <section className="card">
        <h2>Study stats by subject</h2>
        <ul>
          {stats.subjects?.map((subject) => (
            <li key={subject.subject_id} className="list-row">
              <span>
                <Link to={`/subjects/${subject.subject_id}`} className="subject-link">
                  {subject.subject_name}
                </Link>{" "}
                — {subject.done_tasks}/{subject.total_tasks} done — {subject.completion_rate_percent}%
              </span>
            </li>
          ))}
        </ul>
        {!stats.subjects?.length && <p>No subject stats yet.</p>}
      </section>

      <section className="card">
        <h2>Calendar view (this month)</h2>
        <div className="calendar-grid">
          {monthDays.map((item) => (
            <div key={item.dateKey} className="calendar-cell">
              <div className="calendar-day">{item.day}</div>
              {item.events.slice(0, 2).map((event, idx) => (
                <div key={idx} className={`event-chip ${event.type}`}>
                  {event.subjectId ? (
                    <Link to={`/subjects/${event.subjectId}`} className="subject-link">
                      {event.text}
                    </Link>
                  ) : (
                    event.text
                  )}
                </div>
              ))}
              {item.events.length > 2 && <div className="muted">+{item.events.length - 2} more</div>}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
