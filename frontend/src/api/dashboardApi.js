import { request } from "./client";

export function getDashboard(token) {
  return request("/dashboard", { token });
}
