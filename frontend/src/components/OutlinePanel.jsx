import { Download, EyeOff, FolderUp, PanelRightOpen, Pencil, Play, RefreshCw } from "lucide-react";
import { FileUploadControl } from "./FileUploadControl";
import { IconButton } from "./IconButton";

export function OutlinePanel({ mode, setMode, query, setQuery, referenceDocument, setReferenceDocument, outline, setOutline, useExample, setUseExample, onGenerate, onFormat, onRun, isRunning, status }) {
  const isQueryMode = mode === "query";

  return (
    <section className="outline-panel">
      <div className="mode-tabs" role="tablist" aria-label="Outline input mode">
        <button className={isQueryMode ? "active" : ""} type="button" role="tab" aria-selected={isQueryMode} onClick={() => setMode("query")}>
          Query
        </button>
        <button className={!isQueryMode ? "active" : ""} type="button" role="tab" aria-selected={!isQueryMode} onClick={() => setMode("outline")}>
          Structured Outline
        </button>
      </div>
      {!isQueryMode && (
        <label className="use-example">
          <input checked={useExample} onChange={(event) => setUseExample(event.target.checked)} type="checkbox" />
          <span>Use example</span>
        </label>
      )}
      <div className="outline-editor-row" role="tabpanel">
        {isQueryMode ? (
          <div className="query-input-stack">
            <textarea value={query} onChange={(event) => setQuery(event.target.value)} placeholder={'Write a query.\n\nYou could start with something like "Write me a draft on quantum computing and its applications"'} spellCheck="false" />
            <FileUploadControl label="Choose a reference document (optional)" accept=".txt,.pdf,.doc,.docx" files={referenceDocument} onFilesChange={setReferenceDocument} />
          </div>
        ) : (
          <textarea value={outline} onChange={(event) => setOutline(event.target.value)} spellCheck="false" />
        )}

        <div className="outline-panel-tools">
          <IconButton label="Edit outline">
            <Pencil size={18} />
          </IconButton>
          <IconButton label="Hide outline panel">
            <EyeOff size={18} />
          </IconButton>
          <IconButton label="Regenerate">
            <RefreshCw size={18} />
          </IconButton>
          <IconButton label="Generate" onClick={onRun} disabled={isQueryMode || isRunning}>
            <Play size={18} fill="currentColor" />
          </IconButton>
          <IconButton label="Download">
            <Download size={18} />
          </IconButton>
        </div>
      </div>
      {status ? (
        <div className="outline-status" role="status">
          {status}
        </div>
      ) : null}
    </section>
  );
}
