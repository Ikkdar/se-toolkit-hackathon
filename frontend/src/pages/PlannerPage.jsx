import { useEffect, useState } from "react";
import { generateRevisionPlan } from "../api/aiApi";
import { getSubjects } from "../api/subjectsApi";
import { useAuth } from "../context/AuthContext";

export default function PlannerPage() {
  const { token } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    subject_id: "",
    request_text: "Repeat formulas, solve 2 variants, revise weak topics",
  });

  useEffect(() => {
    const load = async () => {
      const data = await getSubjects(token);
      setSubjects(data);
      if (data.length > 0) {
        setForm((prev) => ({ ...prev, subject_id: String(data[0].id) }));
      }
    };
    load().catch((err) => setError(err.message));
  }, [token]);

  const onGenerate = async (event) => {
    event.preventDefault();
    setError("");
    setResult(null);
    try {
      const response = await generateRevisionPlan(token, {
        subject_id: Number(form.subject_id),
        request_text: form.request_text,
      });
      setResult(response);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="space-y">
      <section className="card">
        <h2>AI Revision Planner (V2)</h2>
        <p className="muted">Describe what you want to study. Generated tasks will be saved automatically.</p>
        <form onSubmit={onGenerate}>
          <select
            value={form.subject_id}
            onChange={(event) => setForm((prev) => ({ ...prev, subject_id: event.target.value }))}
            required
          >
            <option value="">Select subject</option>
            {subjects.map((subject) => (
              <option key={subject.id} value={subject.id}>
                {subject.name}
              </option>
            ))}
          </select>
          <textarea
            className="textarea"
            value={form.request_text}
            onChange={(event) => setForm((prev) => ({ ...prev, request_text: event.target.value }))}
            rows={4}
            required
          />
          <button className="btn primary" type="submit">
            Generate plan
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      {result && (
        <section className="card">
          <h3>Generated plan</h3>
          <ul>
            {result.generated_tasks.map((task) => (
              <li key={task.id}>
                {task.title} — {task.due_date}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
