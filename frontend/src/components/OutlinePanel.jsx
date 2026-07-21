import { ChevronLeft, Eraser, PanelTopClose, PanelTopOpen, Pause, Pencil, Play, RefreshCw } from "./FontAwesomeIcons";
import { useEffect, useState } from "react";
import { DownloadMenu } from "./DownloadMenu";
import { IconButton } from "./IconButton";
import { OutlineEditor } from "./OutlineEditor";
import { OutlineRulesTooltip } from "./OutlineRulesTooltip";

export function OutlinePanel({ outline, setOutline, onRun, onRegenerate, onPause, onDownload, onBack, onStartOver, isRunning, hasSelectedFile = false, hasGeneratedContent = false, resetSignal = 0 }) {
  const isLocked = !hasSelectedFile;
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isOutlineEditorOpen, setIsOutlineEditorOpen] = useState(false);
  const hasOutlineText = outline.trim().length > 0;

  useEffect(() => {
    setIsCollapsed(false);
    setIsOutlineEditorOpen(false);
  }, [resetSignal]);

  function openOutlineEditor() {
    if (isLocked || !hasOutlineText) return;
    setIsOutlineEditorOpen(true);
  }

  function saveEditedOutline(nextOutline) {
    setOutline(nextOutline);
    setIsOutlineEditorOpen(false);
  }

  return (
    <section className={`outline-panel ${isCollapsed ? "outline-panel-collapsed" : ""}`}>
      <div className="outline-editor-row">
        {!isCollapsed ? (
          <div className="outline-content-stack">
            <div className="outline-field">
              <span className="outline-field-heading">
                <span>Structured outline</span>
                <OutlineRulesTooltip id="structured-outline-rules" />
              </span>
              <textarea value={outline} onChange={(event) => setOutline(event.target.value)} spellCheck="false" aria-label="Structured outline" />
            </div>
          </div>
        ) : null}

        <div className="outline-panel-tools">
          <div className="outline-tool-group outline-tool-group-toggle">
            <IconButton label={isCollapsed ? "Show outline panel" : "Hide outline panel"} onClick={() => setIsCollapsed((current) => !current)} showLabel>
              {isCollapsed ? <PanelTopOpen size={18} /> : <PanelTopClose size={18} />}
            </IconButton>
          </div>
          <div className="outline-tool-group">
            <IconButton label="Back" onClick={onBack} disabled={isRunning} showLabel>
              <ChevronLeft size={18} />
            </IconButton>
            <IconButton label="Start over" onClick={onStartOver} disabled={isRunning} showLabel>
              <Eraser size={18} />
            </IconButton>
          </div>
          <div className="outline-tool-group">
            <IconButton label={hasGeneratedContent ? "Restart" : "Start"} onClick={hasGeneratedContent ? onRegenerate : () => onRun?.()} disabled={isLocked || isRunning || !hasOutlineText} showLabel>
              {hasGeneratedContent ? <RefreshCw size={18} /> : <Play size={18} fill="currentColor" />}
            </IconButton>
            {isRunning ? (
              <IconButton label="Pause" onClick={onPause} disabled={isLocked} showLabel>
                <Pause size={18} fill="currentColor" />
              </IconButton>
            ) : (
              <IconButton label="Resume" onClick={() => onRun?.()} disabled={isLocked || !hasOutlineText || !hasGeneratedContent} showLabel>
                <Play size={18} fill="currentColor" />
              </IconButton>
            )}
            <IconButton label="Edit outline" onClick={openOutlineEditor} disabled={isLocked || isRunning || !hasOutlineText} showLabel>
              <Pencil size={18} />
            </IconButton>
            <DownloadMenu label="Download" disabled={isLocked} onDownload={onDownload} showLabel />
          </div>
        </div>
      </div>
      <OutlineEditor outline={outline} isOpen={isOutlineEditorOpen} onClose={() => setIsOutlineEditorOpen(false)} onSave={saveEditedOutline} />
    </section>
  );
}
