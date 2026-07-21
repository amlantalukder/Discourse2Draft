import { AlertTriangle, X } from "./FontAwesomeIcons";

const ERROR_STATUS_PATTERN = /(^enter\b|^tell me\b|^save this\b|^add or generate\b|^log in\b|^start a workspace\b|^select\b|unable|failed|error|invalid|input should|not reachable|could not|cancelled|was not|not available|already exists|passwords do not match)/i;

export function getStatusTone(message, tone) {
  if (tone) return tone;
  return ERROR_STATUS_PATTERN.test(String(message ?? "").trim()) ? "error" : "info";
}

export function StatusBar({ message, tone, variant = "file", className = "", onDismiss }) {
  const text = String(message ?? "").trim();
  if (!text) return null;

  const resolvedTone = getStatusTone(text, tone);
  const isError = resolvedTone === "error";
  const classes = ["status-bar", `status-bar-${variant}`, `status-bar-${resolvedTone}`, className].filter(Boolean).join(" ");

  return (
    <div className={classes} role={isError ? "alert" : "status"} aria-live={isError ? "assertive" : "polite"}>
      {isError ? (
        <span className="status-bar-icon" aria-hidden="true">
          <AlertTriangle size={14} />
        </span>
      ) : null}
      <span className="status-bar-message">{text}</span>
      {onDismiss ? (
        <button className="status-bar-dismiss" type="button" onClick={onDismiss} aria-label="Hide status message" title="Hide">
          <X size={13} />
        </button>
      ) : null}
    </div>
  );
}
