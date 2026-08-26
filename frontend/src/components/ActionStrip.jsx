import { ChevronDown, Paperclip, Play, Save, SlidersHorizontal, X } from "./FontAwesomeIcons";
import { useEffect, useRef, useState } from "react";
import { IconButton } from "./IconButton";

const actions = ["Expand", "Rephrase", "Edit", "Remove"];

export function ActionStrip({
  action,
  setAction,
  onWrite,
  isWriting,
  onOpenConceptMap,
  hasSelectedFile,
  isLiteratureSearchEnabled,
  isConfiguringLiteratureSearch,
  onLiteratureSearchChange,
  attachedFiles = [],
  onRemoveAttachedFile,
  hasSelectedParagraphText = false,
  isEditingParagraph = false,
  isSavingParagraphEdit = false,
  onSaveParagraphEdit,
  onDiscardParagraphEdit,
  actionInstruction = "",
  onActionInstructionChange,
}) {
  const [isAttachedFilesOpen, setIsAttachedFilesOpen] = useState(false);
  const [isActionInstructionsOpen, setIsActionInstructionsOpen] = useState(false);
  const attachedFilesRef = useRef(null);
  const actionInstructionsRef = useRef(null);
  const showActionInstruction = action === "Expand" || action === "Rephrase";

  useEffect(() => {
    function closeOnOutsideClick(event) {
      if (attachedFilesRef.current && !attachedFilesRef.current.contains(event.target)) {
        setIsAttachedFilesOpen(false);
      }
      if (actionInstructionsRef.current && !actionInstructionsRef.current.contains(event.target)) {
        setIsActionInstructionsOpen(false);
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

  useEffect(() => {
    if (!showActionInstruction || !hasSelectedParagraphText) {
      setIsActionInstructionsOpen(false);
    }
  }, [hasSelectedParagraphText, showActionInstruction]);

  const isAttachedFilesMenuOpen = hasSelectedFile && isAttachedFilesOpen;

  return (
    <section className={`action-strip ${hasSelectedParagraphText ? "" : "action-strip-no-selection"}`}>
      <span>Content starts below ...</span>
      {isEditingParagraph ? (
        <div className="inline-actions inline-edit-actions">
          <button type="button" className="inline-edit-button inline-edit-save" onClick={onSaveParagraphEdit} disabled={isSavingParagraphEdit}>
            <Save size={14} />
            <span>{isSavingParagraphEdit ? "Saving changes" : "Save changes"}</span>
          </button>
          <button type="button" className="inline-edit-button" onClick={onDiscardParagraphEdit} disabled={isSavingParagraphEdit}>
            <X size={14} />
            <span>Discard changes</span>
          </button>
        </div>
      ) : hasSelectedParagraphText ? (
        <div className="inline-actions">
          <div className="inline-action-choice-row">
            {actions.map((label) => (
              <label key={label}>
                <input checked={action === label} onChange={() => setAction(label)} name="edit-action" type="radio" />
                <span>{label}</span>
              </label>
            ))}
            {showActionInstruction ? (
              <span className="inline-action-instruction-control" ref={actionInstructionsRef}>
                <IconButton
                  label="Instructions"
                  onClick={(event) => {
                    event.preventDefault();
                    setIsActionInstructionsOpen((isOpen) => !isOpen);
                  }}
                  disabled={isWriting}
                >
                  <SlidersHorizontal size={16} />
                </IconButton>
                {isActionInstructionsOpen ? (
                  <label className="inline-action-instruction-popover">
                    <span>Instructions</span>
                    <textarea value={actionInstruction} onChange={(event) => onActionInstructionChange?.(event.target.value)} disabled={isWriting} />
                  </label>
                ) : null}
              </span>
            ) : null}
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
