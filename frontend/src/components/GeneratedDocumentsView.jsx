import { Trash2, X } from "./FontAwesomeIcons";
import { useEffect, useState } from "react";
import { DownloadMenu } from "./DownloadMenu";
import { IconButton } from "./IconButton";

const INSTRUCTIONS_PREVIEW_LENGTH = 120;

function attachedDocumentNames(document) {
  const attachedDocuments = Array.isArray(document.attached_documents) ? document.attached_documents : [];
  return attachedDocuments
    .map((attachedDocument) => attachedDocument.name ?? attachedDocument.file_name)
    .filter(Boolean);
}

function settingsSummary(document) {
  if (document.settings_summary) return document.settings_summary;
  if (document.settings?.llm) {
    const temperature = document.settings.temperature ?? 0;
    return `${document.settings.llm} | Temp ${temperature}`;
  }
  return document.settings_id ? `Settings #${document.settings_id}` : "Session defaults";
}

function settingsInstructions(document) {
  return String(document.settings?.instructions ?? "").trim();
}

export function GeneratedDocumentsView({
  documents = [],
  selectedDocumentId,
  isLoading = false,
  onClose,
  onSelect,
  onDownload,
  onRemove,
}) {
  const [expandedInstructionIds, setExpandedInstructionIds] = useState(() => new Set());

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose?.();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  function toggleInstructions(documentId) {
    setExpandedInstructionIds((current) => {
      const next = new Set(current);
      const normalizedId = String(documentId);
      if (next.has(normalizedId)) {
        next.delete(normalizedId);
      } else {
        next.add(normalizedId);
      }
      return next;
    });
  }

  return (
    <div className="generated-documents-shell" role="presentation" onClick={onClose}>
      <section
        className="generated-documents-view"
        role="dialog"
        aria-modal="true"
        aria-labelledby="generated-documents-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header>
          <div>
            <span>Generated documents</span>
            <h2 id="generated-documents-title">Files</h2>
          </div>
          <IconButton label="Close generated documents" onClick={onClose}>
            <X size={18} />
          </IconButton>
        </header>

        <div className="generated-documents-table-wrap">
          <table className="generated-documents-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Status</th>
                <th>Attached documents</th>
                <th>Settings</th>
                <th>Last modified</th>
                <th>Download/Remove</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan="6">
                    <div className="sidebar-loading-dots" role="status" aria-label="Loading generated documents">
                      <span />
                      <span />
                      <span />
                    </div>
                  </td>
                </tr>
              ) : null}
              {!isLoading && documents.length === 0 ? (
                <tr>
                  <td colSpan="6" className="generated-documents-empty">
                    No generated documents yet.
                  </td>
                </tr>
              ) : null}
              {documents.map((document) => {
                const documentName = document.name ?? document.file_name ?? "Untitled";
                const attachedNames = attachedDocumentNames(document);
                const isSelected = String(document.id) === String(selectedDocumentId);
                const instructions = settingsInstructions(document);
                const isInstructionsExpanded = expandedInstructionIds.has(String(document.id));
                const hasLongInstructions = instructions.length > INSTRUCTIONS_PREVIEW_LENGTH;
                const displayedInstructions =
                  hasLongInstructions && !isInstructionsExpanded
                    ? `${instructions.slice(0, INSTRUCTIONS_PREVIEW_LENGTH).trim()}...`
                    : instructions;

                return (
                  <tr className={isSelected ? "selected" : ""} key={document.id ?? documentName}>
                    <td>
                      <button type="button" className="generated-documents-name" onClick={() => onSelect?.(document)}>
                        <span>{documentName}</span>
                        <small>{document.ai_architecture ?? "base"}</small>
                      </button>
                    </td>
                    <td>
                      <span className={`status-pill status-${document.status ?? "unknown"}`}>{document.status ?? "unknown"}</span>
                    </td>
                    <td>
                      {attachedNames.length ? (
                        <div className="attached-documents-cell" title={attachedNames.join(", ")}>
                          {attachedNames.slice(0, 3).map((name) => (
                            <span key={name}>{name}</span>
                          ))}
                          {attachedNames.length > 3 ? <strong>+{attachedNames.length - 3}</strong> : null}
                        </div>
                      ) : (
                        <span className="table-muted">None</span>
                      )}
                    </td>
                    <td>
                      <div className="settings-cell">
                        <span className="settings-summary" title={settingsSummary(document)}>
                          {settingsSummary(document)}
                        </span>
                        {instructions ? (
                          <p className="settings-instructions" title={instructions}>
                            <strong>Instructions:</strong> {displayedInstructions}
                            {hasLongInstructions ? (
                              <button type="button" onClick={() => toggleInstructions(document.id)}>
                                {isInstructionsExpanded ? "less" : "more"}
                              </button>
                            ) : null}
                          </p>
                        ) : (
                          <span className="settings-instructions-empty">No instructions</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <time>{document.last_modified ?? document.date ?? ""}</time>
                    </td>
                    <td>
                      <div className="generated-document-actions">
                        <DownloadMenu label={`Download ${documentName}`} menuAlign="right" onDownload={(format) => onDownload?.(document, format)} />
                        <IconButton label={`Remove ${documentName}`} onClick={() => onRemove?.(document)}>
                          <Trash2 size={17} />
                        </IconButton>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
