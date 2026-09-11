const API_BASE = "/api";

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, options);

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      data?.message ||
      `Request failed with status ${response.status}`
    );
  }

  return data;
}

export function login(username, password) {
  return request("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      username,
      password
    })
  });
}

export function registerUser(userData) {
  return request("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(userData)
  });
}

export function getCategories() {
  return request("/inspection/categories");
}

export function inspectImage(file, category, token) {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("category", category);

  return request("/inspection/inspect", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: formData
  });
}

export function getStatistics() {
  return request("/analytics/statistics");
}

export function getTrend() {
  return request("/analytics/trend");
}

export function getDefectDistribution() {
  return request("/analytics/defect-distribution");
}

export function getSeverityDistribution() {
  return request("/analytics/severity-distribution");
}

export function getHistory(limit = 50) {
  return request(`/analytics/history?limit=${limit}`);
}

export function getExportUrl(type) {
  return `${API_BASE}/analytics/export/${type}`;
}