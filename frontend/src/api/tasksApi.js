import { request } from "./client";

export function getTasks(token) {
  return request("/tasks", { token });
}

export function createTask(token, payload) {
  return request("/tasks", { method: "POST", token, body: payload });
}

export function updateTask(token, taskId, payload) {
  return request(`/tasks/${taskId}`, { method: "PUT", token, body: payload });
}

export function deleteTask(token, taskId) {
  return request(`/tasks/${taskId}`, { method: "DELETE", token });
}
