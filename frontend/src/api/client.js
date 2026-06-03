const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

function formatErrorDetail(detail, fallback) {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (!item || typeof item !== "object") return String(item);

        const location = Array.isArray(item.loc) ? item.loc.filter((part) => part !== "body").join(".") : "";
        const message = item.msg ?? item.message ?? JSON.stringify(item);
        return location ? `${location}: ${message}` : message;
      })
      .join("; ");
  }

  if (typeof detail === "object") {
    return detail.msg ?? detail.message ?? JSON.stringify(detail);
  }

  return String(detail);
}

async function fetchJSON(path, options) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, options);
  } catch (error) {
    throw new Error("Backend is not reachable. Start the backend server and try again.");
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(formatErrorDetail(payload.detail, `Request failed with ${response.status}`));
  }

  return payload;
}

export async function getJSON(path) {
  return fetchJSON(path);
}

export async function postJSON(path, body) {
  return fetchJSON(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function patchJSON(path, body) {
  return fetchJSON(path, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
