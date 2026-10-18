export const API = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const error = new Error(body?.error?.message || `Request failed: ${response.status}`);
    error.code = body?.error?.code || "HTTP_ERROR";
    error.requestId = body?.request_id;
    throw error;
  }
  return body;
}

export const api = {
  health: () => request("/ready"),
  createIncident: (payload, key) => request("/api/v1/incidents", { method: "POST", body: JSON.stringify(payload), headers: { "Idempotency-Key": key } }),
  investigate: (incidentId, key) => request(`/api/v1/incidents/${incidentId}/investigate`, { method: "POST", headers: { "Idempotency-Key": key } }),
  getInvestigation: (incidentId, investigationId) => request(`/api/v1/incidents/${incidentId}/investigation/${investigationId}`),
};
