const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

const TECHNICAL_ERROR_PATTERNS = [
  /sql:/i,
  /\bselect\b[\s\S]+\bfrom\b/i,
  /\binsert\b[\s\S]+\binto\b/i,
  /\bupdate\b[\s\S]+\bset\b/i,
  /\bdelete\b[\s\S]+\bfrom\b/i,
  /parameters:/i,
  /psycopg/i,
  /sqlalchemy/i,
  /databaseerror/i,
  /operationalerror/i,
  /dbapierror/i,
  /traceback/i,
  /background on this error/i,
];

function friendlyMessage(message, fallback) {
  const text = String(message || fallback || "Something went wrong. Please try again.");
  if (TECHNICAL_ERROR_PATTERNS.some((pattern) => pattern.test(text))) {
    return "The database is temporarily unavailable. Please try again in a moment.";
  }
  return text;
}

function formatErrorDetail(detail, fallback) {
  if (!detail) return friendlyMessage(fallback);
  if (typeof detail === "string") return friendlyMessage(detail, fallback);

  if (Array.isArray(detail)) {
    const message = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (!item || typeof item !== "object") return String(item);

        const location = Array.isArray(item.loc) ? item.loc.filter((part) => part !== "body").join(".") : "";
        const message = item.msg ?? item.message ?? JSON.stringify(item);
        return location ? `${location}: ${message}` : message;
      })
      .join("; ");
    return friendlyMessage(message, fallback);
  }

  if (typeof detail === "object") {
    return friendlyMessage(detail.msg ?? detail.message ?? JSON.stringify(detail), fallback);
  }

  return friendlyMessage(detail, fallback);
}

function apiUrl(path) {
  if (/^https?:\/\//i.test(path)) return path;

  const normalizedPath = path.startsWith("/") ? path.slice(1) : path;
  if (API_BASE) {
    const normalizedBase = API_BASE.endsWith("/") ? API_BASE : `${API_BASE}/`;
    return `${normalizedBase}${normalizedPath}`;
  }

  const baseUrl = import.meta.env.BASE_URL || "./";
  const normalizedBase = baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;
  return `${normalizedBase}${normalizedPath}`;
}

async function fetchJSON(path, options) {
  let response;
  try {
    response = await fetch(apiUrl(path), options);
  } catch (error) {
    throw new Error("Backend is not reachable. Start the backend server and try again.");
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(formatErrorDetail(payload.detail, `Request failed with ${response.status}`));
    error.status = response.status;
    error.detail = payload.detail;
    throw error;
  }

  return payload;
}

export async function getBlob(path) {
  let response;
  try {
    response = await fetch(apiUrl(path));
  } catch (error) {
    throw new Error("Backend is not reachable. Start the backend server and try again.");
  }

  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      const payload = await response.json().catch(() => ({}));
      const error = new Error(formatErrorDetail(payload.detail, `Request failed with ${response.status}`));
      error.status = response.status;
      error.detail = payload.detail;
      throw error;
    }

    const message = await response.text().catch(() => "");
    throw new Error(friendlyMessage(message, `Request failed with ${response.status}`));
  }

  return response.blob();
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

export async function postForm(path, body) {
  return fetchJSON(path, {
    method: "POST",
    body,
  });
}

export async function patchJSON(path, body) {
  return fetchJSON(path, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function deleteJSON(path) {
  return fetchJSON(path, {
    method: "DELETE",
  });
}
