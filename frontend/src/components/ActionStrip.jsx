import { ChevronDown, Paperclip, Play, Trash2, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { IconButton } from "./IconButton";

const actions = ["Expand", "Rephrase", "Remove"];

export function ActionStrip({ action, setAction, onWrite, isWriting, onOpenConceptMap, hasSelectedFile, isLiteratureSearchEnabled, isConfiguringLiteratureSearch, onLiteratureSearchChange, attachedFiles = [], onRemoveAttachedFile, hasSelectedParagraphText = false }) {
  const [isAttachedFilesOpen, setIsAttachedFilesOpen] = useState(false);
  const attachedFilesRef = useRef(null);

  useEffect(() => {
    function closeOnOutsideClick(event) {
      if (attachedFilesRef.current && !attachedFilesRef.current.contains(event.target)) {
        setIsAttachedFilesOpen(false);
      }
    }

    document.addEventListener("mousedown", closeOnOutsideClick);
    return () => document.removeEventListener("mousedown", closeOnOutsideClick);
  }, []);

  useEffect(() => {
    if (!hasSelectedFile) {
      setIsAttachedFilesOpen(false);
    }
  }, [hasSelectedFile]);

  const isAttachedFilesMenuOpen = hasSelectedFile && isAttachedFilesOpen;

  return (
    <section className={`action-strip ${hasSelectedParagraphText ? "" : "action-strip-no-selection"}`}>
      <span>Content starts below ...</span>
      {hasSelectedParagraphText ? (
        <div className="inline-actions">
          {actions.map((label) => (
            <label key={label}>
              <input checked={action === label} onChange={() => setAction(label)} name="edit-action" type="radio" />
              <span>{label}</span>
            </label>
          ))}
          <IconButton label="Clear action">
            <Trash2 size={16} />
          </IconButton>
          <IconButton
            label="Run action"
            onClick={(event) => {
              event.preventDefault();
              onWrite?.();
            }}
            disabled={isWriting}
          >
            <Play size={16} fill="currentColor" />
          </IconButton>
        </div>
      ) : null}
      <label className="toggle-row">
        <input type="checkbox" checked={isLiteratureSearchEnabled} disabled={!hasSelectedFile || isConfiguringLiteratureSearch} onChange={(event) => onLiteratureSearchChange?.(event.target.checked)} />
        <span>{isConfiguringLiteratureSearch ? "Setting up Literature Search" : "Literature Search"}</span>
      </label>
      <div className="attached-files-list" aria-label="Attached files" ref={attachedFilesRef}>
        <button
          className="attached-files-trigger"
          type="button"
          onClick={() => setIsAttachedFilesOpen((isOpen) => !isOpen)}
          aria-expanded={isAttachedFilesMenuOpen}
          disabled={!hasSelectedFile}
        >
          <Paperclip size={13} />
          <span>Attached files</span>
          <strong>{attachedFiles.length}</strong>
          <ChevronDown size={13} />
        </button>
        {isAttachedFilesMenuOpen ? (
          <div className="attached-files-popover">
            {attachedFiles.length ? (
              attachedFiles.map((file) => {
                const fileName = file.name ?? file.file_name ?? "Untitled";
                return (
                  <div className="attached-file-row" key={file.id ?? fileName} title={fileName}>
                    <span>{fileName}</span>
                    <button type="button" aria-label={`Remove ${fileName}`} onClick={() => onRemoveAttachedFile?.(file)}>
                      <X size={13} />
                    </button>
                  </div>
                );
              })
            ) : (
              <span className="attached-files-empty">No attached files.</span>
            )}
          </div>
        ) : null}
      </div>
      <button className="concept-button" type="button" onClick={onOpenConceptMap} disabled={!hasSelectedFile}>
        Concept map
      </button>
    </section>
  );
}
