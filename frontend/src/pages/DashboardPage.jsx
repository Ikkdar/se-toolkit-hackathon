import { useEffect, useState } from "react";
import { getDashboard } from "../api/dashboardApi";
import { useAuth } from "../context/AuthContext";

export default function DashboardPage() {
  const [data, setData] = useState({ upcoming_exams: [], todays_tasks: [] });
  const [error, setError] = useState("");
  const { token } = useAuth();

  useEffect(() => {
    const load = async () => {
      setError("");
      try {
        const response = await getDashboard(token);
        setData(response);
      } catch (err) {
        setError(err.message);
      }
    };

    load();
  }, [token]);

  return (
    <div className="grid-two">
      <section className="card">
        <h2>Upcoming exams</h2>
        {error && <p className="error">{error}</p>}
        <ul>
          {data.upcoming_exams.map((exam) => (
            <li key={exam.id}>
              {exam.title} — {exam.exam_date}
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
              {task.title} — <strong>{task.status}</strong>
            </li>
          ))}
        </ul>
        {data.todays_tasks.length === 0 && <p>No tasks for today.</p>}
      </section>
    </div>
  );
}
