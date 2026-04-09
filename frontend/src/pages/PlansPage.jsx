import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { deleteRevisionPlan, getRevisionPlans, updateRevisionPlanItem } from "../api/aiApi";
import { useAuth } from "../context/AuthContext";

function formatDateTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export default function PlansPage() {
  const { token } = useAuth();
  const [plans, setPlans] = useState([]);
  const [error, setError] = useState("");

  const loadPlans = async () => {
    setError("");
    const data = await getRevisionPlans(token);
    setPlans(data);
  };

  useEffect(() => {
    loadPlans().catch((err) => setError(err.message));
  }, [token]);

  const onDelete = async (planId) => {
    setError("");
    try {
      await deleteRevisionPlan(token, planId);
      await loadPlans();
    } catch (err) {
      setError(err.message);
    }
  };

  const onToggleItem = async (planId, itemIndex, done) => {
    setError("");
    const prev = plans;
    setPlans((current) =>
      current.map((plan) => {
        if (plan.id !== planId) {
          return plan;
        }
        const nextItems = plan.generated_tasks.map((item, idx) =>
          idx === itemIndex ? { ...item, done } : item,
        );
        return { ...plan, generated_tasks: nextItems };
      }),
    );

    try {
      const updatedPlan = await updateRevisionPlanItem(token, planId, itemIndex, { done });
      setPlans((current) => current.map((plan) => (plan.id === planId ? updatedPlan : plan)));
    } catch (err) {
      setPlans(prev);
      setError(err.message);
    }
  };

  return (
    <div className="space-y">
      <section className="card">
        <h2>Plans</h2>
        <p className="muted">All generated LLM plans appear here with subject and your original request.</p>
        <Link to="/planner" className="link-btn">
          + Generate a new plan
        </Link>
      </section>

      {error && <p className="error">{error}</p>}

      {plans.map((plan) => (
        <section key={plan.id} className="card plan-card">
          <div className="plan-card-header">
            <div>
              <h3>
                <Link to={`/subjects/${plan.subject_id}`} className="subject-link">
                  {plan.subject_name}
                </Link>
              </h3>
              <p className="muted">Created: {formatDateTime(plan.created_at)}</p>
            </div>
            <button className="btn danger" onClick={() => onDelete(plan.id)}>
              Delete
            </button>
          </div>

          <div className="plan-block">
            <p className="plan-label">Request</p>
            <p className="plan-request">{plan.request_text}</p>
          </div>

          <div className="plan-meta">
            <span>Start date: {plan.start_date}</span>
            <span>Days: {plan.days}</span>
            <span>Tasks: {plan.tasks_count}</span>
          </div>

          <div className="plan-block">
            <p className="plan-label">Generated tasks</p>
            <ul className="plan-task-list">
              {plan.generated_tasks.map((task, index) => (
                <li key={`${plan.id}-${index}`}>
                  <label className="plan-task-check">
                    <input
                      type="checkbox"
                      checked={Boolean(task.done)}
                      onChange={(event) => onToggleItem(plan.id, index, event.target.checked)}
                    />
                    <span className={task.done ? "done-text" : ""}>{task.title}</span>
                  </label>
                  <span className="muted">{task.due_date}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      ))}

      {plans.length === 0 && !error && (
        <section className="card">
          <p>No plans yet. Generate your first one in AI Planner.</p>
        </section>
      )}
    </div>
  );
}
