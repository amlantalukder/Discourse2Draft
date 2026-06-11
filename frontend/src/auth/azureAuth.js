import { apiUrl, getJSON, postJSON } from "../api/client";

const AZURE_AUTH_CODE_PARAM = "azure_auth_code";
const AZURE_AUTH_STATE_PARAM = "azure_auth_state";
const AZURE_AUTH_ERROR_PARAM = "azure_auth_error";
let azureSignInPromise = null;
let azureSignInKey = "";
let azureSignInCleanupTimer = null;

export function azureSignInUrl() {
  const url = new URL(apiUrl("/api/auth/azure/login"), window.location.href);
  url.searchParams.set("return_url", window.location.href);
  return url.href;
}

export async function getAzureAuthStatus() {
  return getJSON("/api/auth/azure/status");
}

export function readAzureAuthCallback() {
  const params = new URLSearchParams(window.location.search);
  const code = params.get(AZURE_AUTH_CODE_PARAM);
  const state = params.get(AZURE_AUTH_STATE_PARAM);
  const error = params.get(AZURE_AUTH_ERROR_PARAM);
  if (!code && !error) return null;

  return { code, state, error };
}

export function clearAzureAuthCallback() {
  const params = new URLSearchParams(window.location.search);
  params.delete(AZURE_AUTH_CODE_PARAM);
  params.delete(AZURE_AUTH_STATE_PARAM);
  params.delete(AZURE_AUTH_ERROR_PARAM);
  const nextSearch = params.toString();
  const nextUrl = `${window.location.pathname}${nextSearch ? `?${nextSearch}` : ""}${window.location.hash}`;
  window.history.replaceState({}, document.title, nextUrl);
}

export async function completeAzureSignIn(code, state) {
  const nextKey = `${code || ""}:${state || ""}`;
  if (!azureSignInPromise || azureSignInKey !== nextKey) {
    if (azureSignInCleanupTimer) {
      window.clearTimeout(azureSignInCleanupTimer);
      azureSignInCleanupTimer = null;
    }

    azureSignInKey = nextKey;
    azureSignInPromise = postJSON("/api/auth/azure/session", { code, state }, { timeoutMs: 30000 }).finally(() => {
      azureSignInCleanupTimer = window.setTimeout(() => {
        azureSignInKey = "";
        azureSignInPromise = null;
        azureSignInCleanupTimer = null;
      }, 5000);
    });
  }
  return azureSignInPromise;
}
