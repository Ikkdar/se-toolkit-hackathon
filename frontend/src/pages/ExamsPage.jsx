import { useEffect, useState } from "react";
import { createExam, deleteExam, getExams } from "../api/examsApi";
import { getSubjects } from "../api/subjectsApi";
import { useAuth } from "../context/AuthContext";

export default function ExamsPage() {
  const [items, setItems] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [form, setForm] = useState({ subject_id: "", title: "", exam_date: "" });
  const [error, setError] = useState("");
  const { token } = useAuth();

  const load = async () => {
    const [exams, subjectList] = await Promise.all([getExams(token), getSubjects(token)]);
    setItems(exams);
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
      await createExam(token, { ...form, subject_id: Number(form.subject_id) });
      setForm((prev) => ({ ...prev, title: "", exam_date: "" }));
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const onDelete = async (examId) => {
    setError("");
    try {
      await deleteExam(token, examId);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="card">
      <h2>Exams</h2>
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
          placeholder="Exam title"
          onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))}
        />
        <input
          required
          type="date"
          value={form.exam_date}
          onChange={(event) => setForm((prev) => ({ ...prev, exam_date: event.target.value }))}
        />
        <button className="btn primary" type="submit">
          Add
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <ul>
        {items.map((exam) => (
          <li key={exam.id} className="list-row">
            <span>
              {exam.title} — {exam.exam_date}
            </span>
            <button className="btn danger" onClick={() => onDelete(exam.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
      {items.length === 0 && <p>No exams yet.</p>}
    </div>
  );
}
