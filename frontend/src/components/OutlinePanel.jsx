import { PanelTopClose, PanelTopOpen, Pause, Pencil, Play, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { DownloadMenu } from "./DownloadMenu";
import { FileUploadControl } from "./FileUploadControl";
import { IconButton } from "./IconButton";
import { OutlineEditor } from "./OutlineEditor";

export function OutlinePanel({ mode, setMode, query, setQuery, referenceDocument, setReferenceDocument, outline, setOutline, useExample, setUseExample, onGenerate, onFormat, onRun, onRegenerate, onPause, onDownload, isRunning, status, hasSelectedFile = false, resetSignal = 0 }) {
  const isQueryMode = mode === "query";
  const isLocked = !hasSelectedFile;
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isOutlineEditorOpen, setIsOutlineEditorOpen] = useState(false);

  useEffect(() => {
    setIsCollapsed(false);
    setIsOutlineEditorOpen(false);
  }, [resetSignal]);

  function openOutlineEditor() {
    if (isLocked) return;
    setMode("outline");
    setIsOutlineEditorOpen(true);
  }

  function saveEditedOutline(nextOutline) {
    setOutline(nextOutline);
    setMode("outline");
    setIsOutlineEditorOpen(false);
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
            <label className={`use-example ${isLocked ? "use-example-disabled" : ""}`}>
              <input checked={useExample} onChange={(event) => setUseExample(event.target.checked)} type="checkbox" disabled={isLocked} />
              <span>Use example</span>
            </label>
          )}
        </>
      ) : null}
      <div className="outline-editor-row" role="tabpanel">
        {!isCollapsed ? (
          isQueryMode ? (
            <div className="query-input-stack">
              <textarea value={query} onChange={(event) => setQuery(event.target.value)} placeholder={'Write a query.\n\nYou could start with something like "Write me a draft on quantum computing and its applications"'} spellCheck="false" />
              <FileUploadControl label="Choose a reference document (optional)" accept=".txt,.pdf,.doc,.docx" files={referenceDocument} onFilesChange={setReferenceDocument} disabled={isLocked} />
            </div>
          ) : (
            <textarea value={outline} onChange={(event) => setOutline(event.target.value)} spellCheck="false" />
          )
        ) : null}

        <div className="outline-panel-tools">
          <IconButton label={isCollapsed ? "Show outline panel" : "Hide outline panel"} onClick={() => setIsCollapsed((current) => !current)}>
            {isCollapsed ? <PanelTopOpen size={18} /> : <PanelTopClose size={18} />}
          </IconButton>
          <IconButton label="Edit outline" onClick={openOutlineEditor} disabled={isLocked || isRunning}>
            <Pencil size={18} />
          </IconButton>
          <IconButton label="Regenerate" onClick={onRegenerate} disabled={isLocked || isQueryMode || isRunning}>
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
      <OutlineEditor outline={outline} isOpen={isOutlineEditorOpen} onClose={() => setIsOutlineEditorOpen(false)} onSave={saveEditedOutline} />
    </section>
  );
}
