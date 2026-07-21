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

function friendlyStatusMessage(status) {
  if (status === 400) return "That request could not be completed. Please check the information and try again.";
  if (status === 401) return "Please log in or continue as guest before trying again.";
  if (status === 403) return "You do not have permission to do that.";
  if (status === 404) return "I could not find the requested item. It may have been moved or removed.";
  if (status === 409) return "That action conflicts with the current state. Please refresh and try again.";
  if (status === 413) return "That upload is too large. Please choose a smaller file.";
  if (status === 422) return "Some required information is missing or invalid. Please check the form and try again.";
  if (status === 429) return "Too many requests were sent at once. Please wait a moment and try again.";
  if (status >= 500) return "The server had trouble completing that request. Please try again in a moment.";
  return "Something went wrong while processing your request. Please try again.";
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

export function apiUrl(path) {
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

async function fetchJSON(path, options = {}) {
  let response;
  const { timeoutMs, ...fetchOptions } = options ?? {};
  let timeoutId;
  if (timeoutMs) {
    const controller = new AbortController();
    fetchOptions.signal = controller.signal;
    timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
  }

  try {
    response = await fetch(apiUrl(path), fetchOptions);
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error("The backend is taking too long to finish signing you in. Please try again.");
    }
    throw new Error("Backend is not reachable. Start the backend server and try again.");
  } finally {
    if (timeoutId) {
      window.clearTimeout(timeoutId);
    }
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(formatErrorDetail(payload.detail, friendlyStatusMessage(response.status)));
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
      const error = new Error(formatErrorDetail(payload.detail, friendlyStatusMessage(response.status)));
      error.status = response.status;
      error.detail = payload.detail;
      throw error;
    }

    const message = await response.text().catch(() => "");
    throw new Error(friendlyMessage(message, friendlyStatusMessage(response.status)));
  }

  return response.blob();
}

export async function getJSON(path, options = {}) {
  return fetchJSON(path, options);
}

export async function postJSON(path, body, options = {}) {
  const { headers = {}, ...fetchOptions } = options;
  return fetchJSON(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
    ...fetchOptions,
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
