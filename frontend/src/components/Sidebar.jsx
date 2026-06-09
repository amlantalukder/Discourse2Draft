import { ChevronDown, ChevronLeft, ChevronRight, FilePlus2, Maximize2, Search, Trash2 } from "./FontAwesomeIcons";
import { useEffect, useState } from "react";
import { DownloadMenu } from "./DownloadMenu";
import { FileUploadControl } from "./FileUploadControl";
import { IconButton } from "./IconButton";

const healthItems = [
  ["backend", "Backend"],
  ["ai_model", "AI"],
  ["chroma_db", "Chroma"],
  ["postgres", "Postgres"],
];

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
  isLoadingGeneratedDocuments = false,
  uploadedDocuments = [],
  isLoadingUploadedDocuments = false,
  onUploadedDocumentsUpload,
  onUploadedDocumentDelete,
  isUploadingDocuments = false,
  onAttachUploadedDocuments,
  isAttachingUploadedDocuments = false,
  health,
  isHealthLoading = false,
  isCollapsed = false,
  onToggleCollapse,
}) {
  const [uploadFiles, setUploadFiles] = useState([]);
  const [selectedUploadedDocumentIds, setSelectedUploadedDocumentIds] = useState([]);
  const [isGeneratedDocumentsExpanded, setIsGeneratedDocumentsExpanded] = useState(true);
  const [isUploadedDocumentsExpanded, setIsUploadedDocumentsExpanded] = useState(true);
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

  const hasUploadedDocuments = uploadedDocuments.length > 0;
  const isAllUploadedSelected = hasUploadedDocuments && selectedUploadedDocumentIds.length === uploadedDocuments.length;

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
            <div className="generated-list">
              {generatedDocuments.length ? (
                generatedDocuments.map((document) => {
                  const documentName = document.name ?? document.file_name ?? "Untitled";

                  return (
                    <div className={`document-row ${String(document.id) === String(selectedGeneratedDocumentId) ? "active" : ""}`} key={document.id ?? documentName + document.date} title={documentName}>
                      <div>
                        <button type="button" className="document-link" title={documentName} onClick={() => onGeneratedDocumentSelect?.(document)}>
                          {documentName}
                        </button>
                        <time>{document.date}</time>
                      </div>
                      <DownloadMenu label={`Download ${documentName}`} menuAlign="right" onDownload={(format) => onGeneratedDocumentDownload?.(document, format)} />
                      <IconButton label={`Delete ${documentName}`} type="button" onClick={() => onGeneratedDocumentDelete?.(document)}>
                        <Trash2 size={18} />
                      </IconButton>
                    </div>
                  );
                })
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
            <>
              <div className="upload-controls">
                <FileUploadControl label="Choose documents" accept=".txt,.pdf,.doc,.docx" multiple files={uploadFiles} onFilesChange={handleUploadFiles} disabled={isUploadingDocuments} />
              </div>
              <label className="search-field">
                <Search size={16} />
                <input placeholder="Search" />
              </label>
              <label className="check-row">
                <input type="checkbox" checked={isAllUploadedSelected} disabled={!hasUploadedDocuments} onChange={(event) => toggleAllUploadedDocuments(event.target.checked)} />
                <span>Select all documents</span>
              </label>
              <div className="uploaded-list">
                {uploadedDocuments.length ? (
                  uploadedDocuments.map(({ id, name, date, type }) => (
                    <div className="uploaded-row" key={id ?? name} title={name}>
                      <input type="checkbox" checked={selectedUploadedDocumentIds.includes(String(id))} onChange={(event) => toggleUploadedDocument(id, event.target.checked)} />
                      <span className={`file-chip ${type}`}>{type}</span>
                      <div>
                        <span title={name}>{name}</span>
                        <time>{date}</time>
                      </div>
                      <IconButton label={`Delete ${name}`} type="button" onClick={() => onUploadedDocumentDelete?.({ id, name, date, type })}>
                        <Trash2 size={18} />
                      </IconButton>
                    </div>
                  ))
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
                <div className="attach-files-row">
                  <button className="tool-button primary" type="button" onClick={handleAttachUploadedDocuments} disabled={isAttachingUploadedDocuments}>
                    <FilePlus2 size={14} />
                    <span>{isAttachingUploadedDocuments ? "Attaching" : "Attach files"}</span>
                  </button>
                </div>
              ) : null}
            </>
          ) : null}
        </section>
      </div>

      <SystemHealthStatus health={health} isHealthLoading={isHealthLoading} />
    </aside>
  );
}
