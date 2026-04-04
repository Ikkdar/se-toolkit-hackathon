import { request } from "./client";

export function getExams(token) {
  return request("/exams", { token });
}

export function createExam(token, payload) {
  return request("/exams", { method: "POST", token, body: payload });
}

export function deleteExam(token, examId) {
  return request(`/exams/${examId}`, { method: "DELETE", token });
}
