import { FilePlus2, PanelTopClose, PanelTopOpen, Pause, Pencil, Play, RefreshCw } from "./FontAwesomeIcons";
import { useEffect, useState } from "react";
import { DownloadMenu } from "./DownloadMenu";
import { FileUploadControl } from "./FileUploadControl";
import { IconButton } from "./IconButton";
import { OutlineEditor } from "./OutlineEditor";

export function OutlinePanel({ mode, setMode, query, setQuery, referenceDocument, setReferenceDocument, outline, setOutline, outlineTemplates = [], selectedOutlineTemplate = "", onOutlineTemplateChange, onGenerate, onFormat, onRun, onRegenerate, onPause, onDownload, isRunning, status, hasSelectedFile = false, hasGeneratedContent = false, resetSignal = 0 }) {
  const isQueryMode = mode === "query";
  const isLocked = !hasSelectedFile;
  const hasTemplates = outlineTemplates.length > 0;
  const selectedTemplateValue = selectedOutlineTemplate || "";
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isOutlineEditorOpen, setIsOutlineEditorOpen] = useState(false);
  const [isCreatingOutline, setIsCreatingOutline] = useState(false);
  const [draftOutlineForEditor, setDraftOutlineForEditor] = useState(null);
  const hasQueryText = query.trim().length > 0;
  const hasOutlineText = outline.trim().length > 0;

  useEffect(() => {
    setIsCollapsed(false);
    setIsOutlineEditorOpen(false);
    setIsCreatingOutline(false);
    setDraftOutlineForEditor(null);
  }, [resetSignal]);

  function openOutlineEditor() {
    if (isLocked) return;
    setDraftOutlineForEditor(null);
    setMode("outline");
    setIsOutlineEditorOpen(true);
  }

  function saveEditedOutline(nextOutline) {
    setOutline(nextOutline);
    setMode("outline");
    setDraftOutlineForEditor(null);
    setIsOutlineEditorOpen(false);
  }

  function closeOutlineEditor() {
    setDraftOutlineForEditor(null);
    setIsOutlineEditorOpen(false);
  }

  async function createOutlineFromQuery() {
    if (isLocked || isRunning || isCreatingOutline || !hasQueryText) return;

    setIsCreatingOutline(true);
    try {
      const generatedOutline = await onGenerate?.();
      if (generatedOutline) {
        setDraftOutlineForEditor(generatedOutline);
        setMode("outline");
        setIsOutlineEditorOpen(true);
      }
    } finally {
      setIsCreatingOutline(false);
    }
  }

  return (
    <section className={`outline-panel ${isCollapsed ? "outline-panel-collapsed" : ""}`}>
      {!isCollapsed ? (
        <>
          <div className="mode-tabs" role="tablist" aria-label="Outline input mode">
            <button className={isQueryMode ? "active" : ""} type="button" role="tab" aria-selected={isQueryMode} onClick={() => setMode("query")} disabled={isLocked}>
              Query
            </button>
            <button className={!isQueryMode ? "active" : ""} type="button" role="tab" aria-selected={!isQueryMode} onClick={() => setMode("outline")} disabled={isLocked}>
              Structured Outline
            </button>
          </div>
          {!isQueryMode && (
            <div className={`sample-template-controls ${isLocked ? "sample-template-controls-disabled" : ""}`}>
              <select aria-label="Sample outline template" value={selectedTemplateValue} onChange={(event) => onOutlineTemplateChange?.(event.target.value)} disabled={isLocked || !hasTemplates}>
                <option value="">{hasTemplates ? "-- Use sample template --" : "No templates available"}</option>
                {outlineTemplates.map((template) => (
                  <option key={template.name} value={template.name}>
                    {template.label || template.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </>
      ) : null}
      <div className="outline-editor-row" role="tabpanel">
        {!isCollapsed ? (
          isQueryMode ? (
            <div className="query-input-stack">
              <textarea value={query} onChange={(event) => setQuery(event.target.value)} placeholder={'Write a query.\n\nYou could start with something like "Write me a draft on quantum computing and its applications"'} spellCheck="false" />
              <div className="query-input-bottom">
                <FileUploadControl label="Choose reference documents (optional)" accept=".txt,.md,.markdown,.csv,.tsv,.pdf,.docx" files={referenceDocument} onFilesChange={setReferenceDocument} disabled={isLocked || isCreatingOutline} />
              </div>
            </div>
          ) : (
            <textarea value={outline} onChange={(event) => setOutline(event.target.value)} spellCheck="false" />
          )
        ) : null}

        <div className="outline-panel-tools">
          <IconButton label={isCollapsed ? "Show outline panel" : "Hide outline panel"} onClick={() => setIsCollapsed((current) => !current)}>
            {isCollapsed ? <PanelTopOpen size={18} /> : <PanelTopClose size={18} />}
          </IconButton>
          {isQueryMode ? (
            <IconButton label={isCreatingOutline ? "Creating outline..." : "Create outline"} onClick={createOutlineFromQuery} disabled={isLocked || isRunning || isCreatingOutline || !hasQueryText}>
              <FilePlus2 size={18} />
            </IconButton>
          ) : null}
          <IconButton label="Edit outline" onClick={openOutlineEditor} disabled={isLocked || isRunning || !hasOutlineText}>
            <Pencil size={18} />
          </IconButton>
          <IconButton label="Regenerate" onClick={onRegenerate} disabled={isLocked || isQueryMode || isRunning || !hasGeneratedContent}>
            <RefreshCw size={18} />
          </IconButton>
          {isRunning ? (
            <IconButton label="Pause" onClick={onPause} disabled={isLocked}>
              <Pause size={18} fill="currentColor" />
            </IconButton>
          ) : (
            <IconButton label="Generate" onClick={() => onRun?.()} disabled={isLocked || isQueryMode}>
              <Play size={18} fill="currentColor" />
            </IconButton>
          )}
          <DownloadMenu label="Download" disabled={isLocked} onDownload={onDownload} />
        </div>
      </div>
      {!isCollapsed && status ? (
        <div className="outline-status" role="status">
          {status}
        </div>
      ) : null}
      <OutlineEditor outline={draftOutlineForEditor ?? outline} isOpen={isOutlineEditorOpen} onClose={closeOutlineEditor} onSave={saveEditedOutline} />
    </section>
  );
}
