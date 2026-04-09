import { request } from "./client";

export function generateRevisionPlan(token, payload) {
  return request("/ai/revision-plan", { method: "POST", token, body: payload });
}

export function getRevisionPlans(token) {
  return request("/ai/plans", { token });
}

export function deleteRevisionPlan(token, planId) {
  return request(`/ai/plans/${planId}`, { method: "DELETE", token });
}

export function updateRevisionPlanItem(token, planId, itemIndex, payload) {
  return request(`/ai/plans/${planId}/items/${itemIndex}`, {
    method: "PATCH",
    token,
    body: payload,
  });
}
