import { request } from "./client";

export function getStatsOverview(token) {
  return request("/stats/overview", { token });
}
