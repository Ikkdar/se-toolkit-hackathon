import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getSubjectDetail } from "../api/subjectsApi";
import { useAuth } from "../context/AuthContext";

export default function SubjectDetailPage() {
  const { subjectId } = useParams();
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      setError("");
      try {
        const response = await getSubjectDetail(token, subjectId);
        setData(response);
      } catch (err) {
        setError(err.message);
      }
    };
    load();
  }, [subjectId, token]);

  if (error) {
    return <p className="error">{error}</p>;
  }

  if (!data) {
    return <p>Loading subject...</p>;
  }

  return (
    <div className="space-y">
      <div className="card">
        <h2>{data.subject.name}</h2>
        <p>
          Progress: <strong>{data.stats.completion_rate_percent}%</strong> ({data.stats.done_tasks}/{data.stats.total_tasks} tasks)
        </p>
        <p>Upcoming exams: {data.stats.upcoming_exams_count}</p>
        <Link to="/subjects" className="link-btn">
          ← Back to subjects
        </Link>
      </div>

      <div className="grid-two">
        <section className="card">
          <h3>Exams</h3>
          <ul>
            {data.exams.map((exam) => (
              <li key={exam.id}>
                {exam.title} — {exam.exam_date}
              </li>
            ))}
          </ul>
          {data.exams.length === 0 && <p>No exams for this subject yet.</p>}
        </section>

        <section className="card">
          <h3>Homeworks / Tasks</h3>
          <ul>
            {data.tasks.map((task) => (
              <li key={task.id}>
                {task.title} — {task.due_date} — <strong>{task.status}</strong>
              </li>
            ))}
          </ul>
          {data.tasks.length === 0 && <p>No tasks for this subject yet.</p>}
        </section>
      </div>
    </div>
  );
}
