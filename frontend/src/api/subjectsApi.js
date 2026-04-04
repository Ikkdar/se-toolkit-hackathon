import { request } from "./client";

export function getSubjects(token) {
  return request("/subjects", { token });
}

export function createSubject(token, payload) {
  return request("/subjects", { method: "POST", token, body: payload });
}

export function deleteSubject(token, subjectId) {
  return request(`/subjects/${subjectId}`, { method: "DELETE", token });
}
