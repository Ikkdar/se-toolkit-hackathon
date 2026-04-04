import { useEffect, useState } from "react";
import { getSubjects } from "../api/subjectsApi";
import { createTask, deleteTask, getTasks, updateTask } from "../api/tasksApi";
import { useAuth } from "../context/AuthContext";

export default function TasksPage() {
  const [items, setItems] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [form, setForm] = useState({ subject_id: "", title: "", due_date: "", status: "todo" });
  const [error, setError] = useState("");
  const { token } = useAuth();

  const load = async () => {
    const [tasks, subjectList] = await Promise.all([getTasks(token), getSubjects(token)]);
    setItems(tasks);
    setSubjects(subjectList);
    if (!form.subject_id && subjectList.length > 0) {
      setForm((prev) => ({ ...prev, subject_id: String(subjectList[0].id) }));
    }
  };

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  const onCreate = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await createTask(token, { ...form, subject_id: Number(form.subject_id) });
      setForm((prev) => ({ ...prev, title: "", due_date: "", status: "todo" }));
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const onToggleStatus = async (task) => {
    const nextStatus = task.status === "todo" ? "done" : "todo";
    try {
      await updateTask(token, task.id, {
        subject_id: task.subject_id,
        title: task.title,
        due_date: task.due_date,
        status: nextStatus,
      });
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const onDelete = async (taskId) => {
    setError("");
    try {
      await deleteTask(token, taskId);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="card">
      <h2>Tasks</h2>
      <form className="inline-form" onSubmit={onCreate}>
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
        <input
          required
          value={form.title}
          placeholder="Task title"
          onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))}
        />
        <input
          required
          type="date"
          value={form.due_date}
          onChange={(event) => setForm((prev) => ({ ...prev, due_date: event.target.value }))}
        />
        <button className="btn primary" type="submit">
          Add
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <ul>
        {items.map((task) => (
          <li key={task.id} className="list-row">
            <span>
              {task.title} — {task.due_date} — <strong>{task.status}</strong>
            </span>
            <div className="row-actions">
              <button className="btn" onClick={() => onToggleStatus(task)}>
                Toggle status
              </button>
              <button className="btn danger" onClick={() => onDelete(task.id)}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
      {items.length === 0 && <p>No tasks yet.</p>}
    </div>
  );
}
