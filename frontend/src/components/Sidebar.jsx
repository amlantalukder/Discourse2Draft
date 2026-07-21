import { ChevronDown, ChevronLeft, ChevronRight, FileLines, FilePlus2, Maximize2, Search, Trash2 } from "./FontAwesomeIcons";
import { useEffect, useRef, useState } from "react";
import { DownloadMenu } from "./DownloadMenu";
import { FileUploadControl } from "./FileUploadControl";
import { IconButton } from "./IconButton";

const healthItems = [
  ["backend", "Backend"],
  ["ai_model", "AI"],
  ["chroma_db", "Chroma"],
  ["postgres", "Postgres"],
];

const SEARCH_MIN_ITEMS = 6;
const SLOW_RENAME_MIN_MS = 450;
const SLOW_RENAME_MAX_MS = 1800;

function itemMatchesSearch(item, query, fields) {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) return true;

  return fields.some((field) =>
    String(item?.[field] ?? "")
      .toLowerCase()
      .includes(normalizedQuery),
  );
}

function renameItemKey(type, item, currentName) {
  return `${type}:${item?.id ?? item?.name ?? currentName}`;
}

function normalizedFileName(value) {
  return String(value ?? "").trim().toLowerCase();
}

function normalizedTemplateFileName(value) {
  const rawName = String(value ?? "").trim();
  if (!rawName) return "";

  const hasAllowedSuffix = /\.(md|docx)$/i.test(rawName);
  const nameWithSuffix = hasAllowedSuffix ? rawName : `${rawName}.md`;
  const suffix = nameWithSuffix.match(/\.(md|docx)$/i)?.[0] ?? ".md";
  const stem = nameWithSuffix.slice(0, -suffix.length).replace(/[^a-zA-Z0-9_-]+/g, "_").replace(/^_+|_+$/g, "");
  return stem ? `${stem}.md`.toLowerCase() : "";
}

function healthStatus(check, isLoading) {
  if (isLoading && !check) return "checking";
  return check?.status ?? "unknown";
}

function SystemHealthStatus({ health, isHealthLoading = false }) {
  return (
    <footer className="sidebar-health-footer">
      <span className="sidebar-health-title">System status</span>
      <div className="health-checks sidebar-health-checks" aria-label="System health">
        {healthItems.map(([key, label]) => {
          const check = health?.checks?.[key];
          const status = healthStatus(check, isHealthLoading);
          return (
            <span className={`health-check health-${status}`} title={check?.message ?? "Health has not been checked yet."} key={key}>
              <i aria-hidden="true" />
              <span>{label}</span>
            </span>
          );
        })}
      </div>
    </footer>
  );
}

export function Sidebar({
  generatedDocuments = [],
  selectedGeneratedDocumentId,
  onGeneratedDocumentSelect,
  onGeneratedDocumentsExpand,
  onGeneratedDocumentDownload,
  onGeneratedDocumentDelete,
  onGeneratedDocumentRename,
  isLoadingGeneratedDocuments = false,
  uploadedDocuments = [],
  isLoadingUploadedDocuments = false,
  onUploadedDocumentsUpload,
  onUploadedDocumentDelete,
  onUploadedDocumentRename,
  isUploadingDocuments = false,
  onAttachUploadedDocuments,
  isAttachingUploadedDocuments = false,
  uploadedTemplates = [],
  isLoadingUploadedTemplates = false,
  onUploadedTemplatesUpload,
  onUploadedTemplateEdit,
  onUploadedTemplateDelete,
  onUploadedTemplateRename,
  isUploadingTemplates = false,
  canUploadTemplates = false,
  health,
  isHealthLoading = false,
  isCollapsed = false,
  onToggleCollapse,
  onStatusMessage,
}) {
  const [uploadFiles, setUploadFiles] = useState([]);
  const [uploadTemplateFiles, setUploadTemplateFiles] = useState([]);
  const [selectedUploadedDocumentIds, setSelectedUploadedDocumentIds] = useState([]);
  const [generatedSearch, setGeneratedSearch] = useState("");
  const [uploadedDocumentSearch, setUploadedDocumentSearch] = useState("");
  const [uploadedTemplateSearch, setUploadedTemplateSearch] = useState("");
  const [isGeneratedDocumentsExpanded, setIsGeneratedDocumentsExpanded] = useState(true);
  const [isUploadedDocumentsExpanded, setIsUploadedDocumentsExpanded] = useState(true);
  const [isUploadedTemplatesExpanded, setIsUploadedTemplatesExpanded] = useState(true);
  const [editingName, setEditingName] = useState(null);
  const [editingNameValue, setEditingNameValue] = useState("");
  const lastNameClickRef = useRef({ key: "", time: 0 });
  const renameCommitInFlightRef = useRef(false);
  const selectedUploadedDocuments = uploadedDocuments.filter((document) => selectedUploadedDocumentIds.includes(String(document.id)));

  useEffect(() => {
    const availableIds = new Set(uploadedDocuments.map((document) => String(document.id)));
    setSelectedUploadedDocumentIds((current) => current.filter((id) => availableIds.has(id)));
  }, [uploadedDocuments]);

  async function handleUploadFiles(nextFiles) {
    const selectedFiles = Array.isArray(nextFiles) ? nextFiles : nextFiles ? [nextFiles] : [];
    setUploadFiles(selectedFiles);
    if (!selectedFiles.length) return;

    const shouldClear = await onUploadedDocumentsUpload?.(selectedFiles);
    if (shouldClear !== false) {
      setUploadFiles([]);
    }
  }

  async function handleUploadTemplates(nextFiles) {
    const selectedFiles = Array.isArray(nextFiles) ? nextFiles : nextFiles ? [nextFiles] : [];
    setUploadTemplateFiles(selectedFiles);
    if (!selectedFiles.length) return;

    const shouldClear = await onUploadedTemplatesUpload?.(selectedFiles);
    if (shouldClear !== false) {
      setUploadTemplateFiles([]);
    }
  }

  function toggleUploadedDocument(documentId, checked) {
    const normalizedId = String(documentId);
    setSelectedUploadedDocumentIds((current) => (checked ? [...new Set([...current, normalizedId])] : current.filter((id) => id !== normalizedId)));
  }

  function toggleAllUploadedDocuments(checked) {
    setSelectedUploadedDocumentIds(checked ? uploadedDocuments.map((document) => String(document.id)) : []);
  }

  async function handleAttachUploadedDocuments() {
    const shouldClear = await onAttachUploadedDocuments?.(selectedUploadedDocuments);
    if (shouldClear !== false) {
      setSelectedUploadedDocumentIds([]);
    }
  }

  function startInlineRename(type, item, currentName) {
    lastNameClickRef.current = { key: "", time: 0 };
    setEditingName({ type, item, key: renameItemKey(type, item, currentName), currentName: currentName ?? "" });
    setEditingNameValue(currentName ?? "");
  }

  function handleSlowRenameClick(event, type, item, currentName) {
    const now = Date.now();
    const key = `${type}:${item?.id ?? item?.name ?? currentName}`;
    const previousClick = lastNameClickRef.current;
    const elapsedMs = previousClick.key === key ? now - previousClick.time : Number.POSITIVE_INFINITY;

    lastNameClickRef.current = { key, time: now };

    if (elapsedMs >= SLOW_RENAME_MIN_MS && elapsedMs <= SLOW_RENAME_MAX_MS) {
      event.stopPropagation();
      startInlineRename(type, item, currentName);
    }
  }

  function closeInlineRename() {
    setEditingName(null);
    setEditingNameValue("");
  }

  function duplicateNameMessage(type, item, nextName) {
    const currentKey = renameItemKey(type, item, editingName?.currentName);

    if (type === "generated") {
      const candidate = normalizedFileName(nextName);
      const hasDuplicate = generatedDocuments.some((document) => renameItemKey(type, document, document.name ?? document.file_name) !== currentKey && normalizedFileName(document.name ?? document.file_name) === candidate);
      return hasDuplicate ? "A generated document with that name already exists." : "";
    }

    if (type === "uploaded") {
      const candidate = normalizedFileName(nextName);
      const hasDuplicate = uploadedDocuments.some((document) => renameItemKey(type, document, document.name ?? document.file_name) !== currentKey && normalizedFileName(document.name ?? document.file_name) === candidate);
      return hasDuplicate ? "An uploaded document with that name already exists." : "";
    }

    const candidate = normalizedTemplateFileName(nextName);
    const hasDuplicate = uploadedTemplates.some((template) => renameItemKey(type, template, template.file_name ?? template.name) !== currentKey && normalizedTemplateFileName(template.file_name ?? `${template.name}.md`) === candidate);
    return hasDuplicate ? "An uploaded template with that name already exists." : "";
  }

  async function commitInlineRename() {
    if (!editingName || renameCommitInFlightRef.current) return;

    const nextName = editingNameValue.trim();
    if (!nextName) {
      onStatusMessage?.("File name cannot be empty.");
      return;
    }

    const duplicateMessage = duplicateNameMessage(editingName.type, editingName.item, nextName);
    if (duplicateMessage) {
      onStatusMessage?.(duplicateMessage);
      return;
    }

    const currentComparable = editingName.type === "template" ? normalizedTemplateFileName(editingName.currentName) : normalizedFileName(editingName.currentName);
    const nextComparable = editingName.type === "template" ? normalizedTemplateFileName(nextName) : normalizedFileName(nextName);
    if (currentComparable === nextComparable) {
      closeInlineRename();
      return;
    }

    renameCommitInFlightRef.current = true;
    let shouldClose = true;
    try {
      if (editingName.type === "generated") {
        shouldClose = await onGeneratedDocumentRename?.(editingName.item, nextName);
      } else if (editingName.type === "uploaded") {
        shouldClose = await onUploadedDocumentRename?.(editingName.item, nextName);
      } else if (editingName.type === "template") {
        shouldClose = await onUploadedTemplateRename?.(editingName.item, nextName);
      }
    } catch {
      shouldClose = false;
    } finally {
      renameCommitInFlightRef.current = false;
    }

    if (shouldClose !== false) {
      closeInlineRename();
    } else {
      onStatusMessage?.("Could not rename this file. Please try another name.");
    }
  }

  function renderInlineName({ type, item, displayName, editName, className }) {
    const currentName = editName ?? displayName;
    const key = renameItemKey(type, item, currentName);
    if (editingName?.key === key) {
      return (
        <span className="sidebar-inline-rename" onClick={(event) => event.stopPropagation()}>
          <input
            autoFocus
            value={editingNameValue}
            onBlur={commitInlineRename}
            onChange={(event) => setEditingNameValue(event.target.value)}
            onKeyDown={(event) => {
              event.stopPropagation();
              if (event.key === "Enter") {
                event.preventDefault();
                event.currentTarget.blur();
              }
              if (event.key === "Escape") {
                event.preventDefault();
                closeInlineRename();
              }
            }}
            aria-label={`Rename ${displayName}`}
          />
        </span>
      );
    }

    return (
      <button type="button" className={className} title={`Slow double-click to rename ${displayName}`} onClick={(event) => handleSlowRenameClick(event, type, item, currentName)}>
        {displayName}
      </button>
    );
  }

  const hasUploadedDocuments = uploadedDocuments.length > 0;
  const isAllUploadedSelected = hasUploadedDocuments && selectedUploadedDocumentIds.length === uploadedDocuments.length;
  const showGeneratedSearch = generatedDocuments.length >= SEARCH_MIN_ITEMS;
  const showUploadedDocumentSearch = uploadedDocuments.length >= SEARCH_MIN_ITEMS;
  const showUploadedTemplateSearch = uploadedTemplates.length >= SEARCH_MIN_ITEMS;
  const filteredGeneratedDocuments = showGeneratedSearch ? generatedDocuments.filter((document) => itemMatchesSearch(document, generatedSearch, ["name", "file_name", "status"])) : generatedDocuments;
  const filteredUploadedDocuments = showUploadedDocumentSearch ? uploadedDocuments.filter((document) => itemMatchesSearch(document, uploadedDocumentSearch, ["name", "file_name", "type"])) : uploadedDocuments;
  const filteredUploadedTemplates = showUploadedTemplateSearch ? uploadedTemplates.filter((template) => itemMatchesSearch(template, uploadedTemplateSearch, ["name", "label", "file_name"])) : uploadedTemplates;

  return (
    <aside className={`sidebar ${isCollapsed ? "sidebar-collapsed" : ""}`}>
      <button className="collapse-handle" type="button" aria-label={isCollapsed ? "Show sidebar" : "Hide sidebar"} title={isCollapsed ? "Show sidebar" : "Hide sidebar"} onClick={onToggleCollapse}>
        {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </button>

      <div className="sidebar-content">
        <section className={`side-section ${isGeneratedDocumentsExpanded ? "" : "is-collapsed"}`}>
          <header>
            <button className="side-section-toggle" type="button" aria-expanded={isGeneratedDocumentsExpanded} onClick={() => setIsGeneratedDocumentsExpanded((current) => !current)}>
              <span>Generated documents</span>
            </button>
            <div className="side-section-actions">
              <IconButton label="Expand generated documents" type="button" onClick={onGeneratedDocumentsExpand}>
                <Maximize2 size={15} />
              </IconButton>
              <button className="section-collapse-button" type="button" aria-label={isGeneratedDocumentsExpanded ? "Collapse generated documents" : "Expand generated documents"} aria-expanded={isGeneratedDocumentsExpanded} onClick={() => setIsGeneratedDocumentsExpanded((current) => !current)}>
                <ChevronDown size={17} />
              </button>
            </div>
          </header>
          {isGeneratedDocumentsExpanded ? (
            <div className="generated-list side-section-body">
              {showGeneratedSearch ? (
                <label className="search-field">
                  <Search size={16} />
                  <input placeholder="Search generated documents" value={generatedSearch} onChange={(event) => setGeneratedSearch(event.target.value)} />
                </label>
              ) : null}
              {filteredGeneratedDocuments.length ? (
                filteredGeneratedDocuments.map((document) => {
                  const documentName = document.name ?? document.file_name ?? "Untitled";

                  return (
                    <div className={`document-row ${String(document.id) === String(selectedGeneratedDocumentId) ? "active" : ""}`} key={document.id ?? documentName + document.date} title={documentName} onClick={() => onGeneratedDocumentSelect?.(document)}>
                      <div>
                        {renderInlineName({ type: "generated", item: document, displayName: documentName, editName: documentName, className: "document-link" })}
                        <time>{document.date}</time>
                      </div>
                      <div onClick={(event) => event.stopPropagation()}>
                        <DownloadMenu label={`Download ${documentName}`} menuAlign="right" onDownload={(format) => onGeneratedDocumentDownload?.(document, format)} />
                      </div>
                      <IconButton
                        label={`Delete ${documentName}`}
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          onGeneratedDocumentDelete?.(document);
                        }}
                      >
                        <Trash2 size={18} />
                      </IconButton>
                    </div>
                  );
                })
              ) : generatedDocuments.length ? (
                <p className="empty-panel-message">No matching generated documents.</p>
              ) : (
                <p className="empty-panel-message">No generated documents yet.</p>
              )}
              {isLoadingGeneratedDocuments ? (
                <div className="sidebar-loading-dots" role="status" aria-label="Loading generated documents">
                  <span />
                  <span />
                  <span />
                </div>
              ) : null}
            </div>
          ) : null}
        </section>

        <section className={`side-section uploaded ${isUploadedDocumentsExpanded ? "" : "is-collapsed"}`}>
          <header>
            <button className="side-section-toggle" type="button" aria-expanded={isUploadedDocumentsExpanded} onClick={() => setIsUploadedDocumentsExpanded((current) => !current)}>
              <span>Uploaded documents</span>
            </button>
            <button className="section-collapse-button" type="button" aria-label={isUploadedDocumentsExpanded ? "Collapse uploaded documents" : "Expand uploaded documents"} aria-expanded={isUploadedDocumentsExpanded} onClick={() => setIsUploadedDocumentsExpanded((current) => !current)}>
              <ChevronDown size={17} />
            </button>
          </header>
          {isUploadedDocumentsExpanded ? (
            <div className="side-section-body uploaded-documents-body">
              <div className="upload-controls">
                <FileUploadControl label="Choose documents" accept=".txt,.pdf,.doc,.docx" multiple files={uploadFiles} onFilesChange={handleUploadFiles} disabled={isUploadingDocuments} />
              </div>
              {showUploadedDocumentSearch ? (
                <label className="search-field">
                  <Search size={16} />
                  <input placeholder="Search uploaded documents" value={uploadedDocumentSearch} onChange={(event) => setUploadedDocumentSearch(event.target.value)} />
                </label>
              ) : null}
              {uploadedDocuments.length >= 2 ? (
                <label className="check-row">
                  <input type="checkbox" checked={isAllUploadedSelected} disabled={!hasUploadedDocuments} onChange={(event) => toggleAllUploadedDocuments(event.target.checked)} />
                  <span>Select all documents</span>
                </label>
              ) : null}
              <div className="uploaded-list">
                {filteredUploadedDocuments.length ? (
                  filteredUploadedDocuments.map(({ id, name, date, type }) => (
                    <div className="uploaded-row" key={id ?? name} title={name}>
                      <input type="checkbox" checked={selectedUploadedDocumentIds.includes(String(id))} onChange={(event) => toggleUploadedDocument(id, event.target.checked)} />
                      <span className={`file-chip ${type}`}>{type}</span>
                      <div>
                        {renderInlineName({ type: "uploaded", item: { id, name, date, type }, displayName: name, editName: name, className: "sidebar-name-button" })}
                        <time>{date}</time>
                      </div>
                      <IconButton label={`Delete ${name}`} type="button" onClick={() => onUploadedDocumentDelete?.({ id, name, date, type })}>
                        <Trash2 size={18} />
                      </IconButton>
                    </div>
                  ))
                ) : uploadedDocuments.length ? (
                  <p className="empty-panel-message">No matching uploaded documents.</p>
                ) : (
                  <p className="empty-panel-message">No uploaded documents yet.</p>
                )}
                {isLoadingUploadedDocuments || isUploadingDocuments ? (
                  <div className="sidebar-loading-dots" role="status" aria-label={isUploadingDocuments ? "Uploading documents" : "Loading uploaded documents"}>
                    <span />
                    <span />
                    <span />
                  </div>
                ) : null}
              </div>
              {selectedUploadedDocuments.length ? (
                <div className="uploaded-documents-action-control">
                  <div className="attach-files-row">
                    <button className="tool-button primary" type="button" onClick={handleAttachUploadedDocuments} disabled={isAttachingUploadedDocuments}>
                      <FilePlus2 size={14} />
                      <span>{isAttachingUploadedDocuments ? "Attaching" : "Attach files"}</span>
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}
        </section>

        <section className={`side-section uploaded-templates ${isUploadedTemplatesExpanded ? "" : "is-collapsed"}`}>
          <header>
            <button className="side-section-toggle" type="button" aria-expanded={isUploadedTemplatesExpanded} onClick={() => setIsUploadedTemplatesExpanded((current) => !current)}>
              <span>Uploaded outline templates</span>
            </button>
            <button className="section-collapse-button" type="button" aria-label={isUploadedTemplatesExpanded ? "Collapse uploaded templates" : "Expand uploaded templates"} aria-expanded={isUploadedTemplatesExpanded} onClick={() => setIsUploadedTemplatesExpanded((current) => !current)}>
              <ChevronDown size={17} />
            </button>
          </header>
          {isUploadedTemplatesExpanded ? (
            <div className="side-section-body uploaded-templates-body">
              <div className="upload-controls">
                <FileUploadControl label="Choose templates" accept=".md,.docx" multiple files={uploadTemplateFiles} onFilesChange={handleUploadTemplates} disabled={!canUploadTemplates || isUploadingTemplates} />
              </div>
              {showUploadedTemplateSearch ? (
                <label className="search-field">
                  <Search size={16} />
                  <input placeholder="Search uploaded templates" value={uploadedTemplateSearch} onChange={(event) => setUploadedTemplateSearch(event.target.value)} />
                </label>
              ) : null}
              <div className="uploaded-template-list">
                {!canUploadTemplates ? <p className="empty-panel-message">Start a workspace session to upload outline templates.</p> : null}
                {canUploadTemplates && filteredUploadedTemplates.length
                  ? filteredUploadedTemplates.map((template) => (
                      <div className="uploaded-template-row" key={template.name} title={template.file_name ?? template.label ?? template.name}>
                        <span className="file-chip md">md</span>
                        <div>
                          {renderInlineName({ type: "template", item: template, displayName: template.label || template.name, editName: template.file_name ?? `${template.name}.md`, className: "sidebar-name-button" })}
                          {template.file_name ? <time>{template.file_name}</time> : null}
                        </div>
                        <IconButton label={`Edit ${template.label || template.name}`} type="button" onClick={() => onUploadedTemplateEdit?.(template)}>
                          <FileLines size={16} />
                        </IconButton>
                        <IconButton label={`Remove ${template.label || template.name}`} type="button" onClick={() => onUploadedTemplateDelete?.(template)}>
                          <Trash2 size={16} />
                        </IconButton>
                      </div>
                    ))
                  : null}
                {canUploadTemplates && uploadedTemplates.length && !filteredUploadedTemplates.length ? <p className="empty-panel-message">No matching uploaded templates.</p> : null}
                {canUploadTemplates && !uploadedTemplates.length && !isLoadingUploadedTemplates && !isUploadingTemplates ? <p className="empty-panel-message">No uploaded templates yet.</p> : null}
                {isLoadingUploadedTemplates || isUploadingTemplates ? (
                  <div className="sidebar-loading-dots" role="status" aria-label={isUploadingTemplates ? "Uploading templates" : "Loading uploaded templates"}>
                    <span />
                    <span />
                    <span />
                  </div>
                ) : null}
              </div>
            </div>
          ) : null}
        </section>
      </div>

      <SystemHealthStatus health={health} isHealthLoading={isHealthLoading} />
    </aside>
  );
}
