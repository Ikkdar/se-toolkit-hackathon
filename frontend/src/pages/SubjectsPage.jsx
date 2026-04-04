import { useEffect, useState } from "react";
import { createSubject, deleteSubject, getSubjects } from "../api/subjectsApi";
import { useAuth } from "../context/AuthContext";

export default function SubjectsPage() {
  const [items, setItems] = useState([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const { token } = useAuth();

  const load = async () => {
    const data = await getSubjects(token);
    setItems(data);
  };

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  const onCreate = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await createSubject(token, { name });
      setName("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  const onDelete = async (subjectId) => {
    setError("");
    try {
      await deleteSubject(token, subjectId);
      await load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="card">
      <h2>Subjects</h2>
      <form className="inline-form" onSubmit={onCreate}>
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Subject name" required />
        <button className="btn primary" type="submit">
          Add
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <ul>
        {items.map((subject) => (
          <li key={subject.id} className="list-row">
            <span>{subject.name}</span>
            <button className="btn danger" onClick={() => onDelete(subject.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
      {items.length === 0 && <p>No subjects yet.</p>}
    </div>
  );
}
