import { AlertTriangle, ChevronLeft, FilePlus2, Pencil, Play, RefreshCw, Upload } from "./FontAwesomeIcons";
import { useEffect, useRef, useState } from "react";
import { ConfirmDialog } from "./ConfirmDialog";
import { FileUploadControl } from "./FileUploadControl";
import { OutlineEditor } from "./OutlineEditor";
import { OutlineRulesTooltip } from "./OutlineRulesTooltip";

export function DraftFlowPanel({
  step,
  query,
  setQuery,
  referenceDocument,
  setReferenceDocument,
  outline,
  setOutline,
  outlineTemplates = [],
  uploadedOutlineTemplates = [],
  selectedOutlineTemplate = "",
  selectedUploadedOutlineTemplate = "",
  onOutlineTemplateChange,
  onUploadedOutlineTemplateChange,
  onGenerateOutline,
  onUploadOutline,
  onReplaceOutlineConfirm,
  onNextFromQuery,
  onBack,
  onComplete,
  isCreatingOutline = false,
  isImportingOutline = false,
  isLocked = false,
  resetSignal = 0,
}) {
  const outlineUploadInputRef = useRef(null);
  const [showTemplateControls, setShowTemplateControls] = useState(false);
  const [isCreateOutlineConfirmOpen, setIsCreateOutlineConfirmOpen] = useState(false);
  const [isGeneratedOutlineEditorOpen, setIsGeneratedOutlineEditorOpen] = useState(false);
  const hasQueryText = query.trim().length > 0;
  const hasOutlineText = outline.trim().length > 0;
  const hasTemplates = outlineTemplates.length > 0;
  const hasUploadedTemplates = uploadedOutlineTemplates.length > 0;

  useEffect(() => {
    setShowTemplateControls(false);
    setIsCreateOutlineConfirmOpen(false);
    setIsGeneratedOutlineEditorOpen(false);
  }, [resetSignal, step]);

  async function createGeneratedOutline() {
    await onGenerateOutline?.();
  }

  function requestGeneratedOutline() {
    if (isLocked || isCreatingOutline || !hasQueryText) return;
    if (hasOutlineText) {
      setIsCreateOutlineConfirmOpen(true);
      return;
    }
    createGeneratedOutline();
  }

  function confirmGeneratedOutline() {
    onReplaceOutlineConfirm?.();
    setIsCreateOutlineConfirmOpen(false);
    createGeneratedOutline();
  }

  function handleOutlineUploadChange(event) {
    const file = event.target.files?.[0] ?? null;
    if (file) {
      onUploadOutline?.(file);
    }
    event.target.value = "";
  }

  if (step === "topic") {
    return (
      <section className="draft-flow-panel draft-flow-panel-topic">
        <div className="draft-flow-main">
          <textarea value={query} onChange={(event) => setQuery(event.target.value)} placeholder="What do you want me to write about?" spellCheck="false" disabled={isLocked} />
          <div className="draft-flow-footer">
            <FileUploadControl label="Upload reference documents (Optional)" accept=".txt,.md,.markdown,.csv,.tsv,.pdf,.docx" files={referenceDocument} onFilesChange={setReferenceDocument} disabled={isLocked} showRemoveControls />
            <div>
              <button className="primary-action-button" type="button" onClick={onNextFromQuery} disabled={!hasQueryText || isLocked}>
                Next
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="draft-flow-panel draft-flow-panel-outline">
      <div className={`draft-flow-outline-layout ${isGeneratedOutlineEditorOpen ? "draft-flow-outline-layout-editor-open" : ""}`}>
        <div className="draft-flow-main">
          {hasOutlineText ? (
            <div className="draft-flow-outline-toolbar">
              <div>
                <button type="button" onClick={() => setIsGeneratedOutlineEditorOpen(true)} disabled={isLocked || isCreatingOutline || isGeneratedOutlineEditorOpen}>
                  <Pencil size={15} />
                  <span>Preview/Edit outline in Outline Editor</span>
                </button>
              </div>
            </div>
          ) : null}
          <div className="outline-field draft-flow-outline-field">
            <span className="outline-field-heading">
              <span>Do you have a preferred outline in mind?</span>
              <OutlineRulesTooltip id="draft-flow-outline-rules" />
            </span>
            <textarea value={outline} onChange={(event) => setOutline(event.target.value)} rows={20} placeholder="Do you have a preferred outline in mind?" spellCheck="false" disabled={isLocked || isCreatingOutline || isImportingOutline} aria-label="Preferred structured outline" />
          </div>
          <div className="draft-flow-actions">
            <button type="button" onClick={onBack} disabled={isLocked || isCreatingOutline || isImportingOutline}>
              <ChevronLeft size={15} />
              <span>Back</span>
            </button>
            <button type="button" onClick={() => outlineUploadInputRef.current?.click()} disabled={isLocked || isCreatingOutline || isImportingOutline}>
              {isImportingOutline ? <RefreshCw size={15} /> : <Upload size={15} />}
              <span>{isImportingOutline ? "Uploading outline" : "Upload an outline"}</span>
            </button>
            <input ref={outlineUploadInputRef} className="draft-flow-outline-upload-input" type="file" accept=".md,.docx" onChange={handleOutlineUploadChange} disabled={isLocked || isCreatingOutline || isImportingOutline} />
            <button type="button" onClick={() => setShowTemplateControls((current) => !current)} disabled={isLocked || isCreatingOutline || isImportingOutline}>
              <FilePlus2 size={15} />
              <span>Use template</span>
            </button>
            <button type="button" onClick={requestGeneratedOutline} disabled={!hasQueryText || isLocked || isCreatingOutline || isImportingOutline}>
              {isCreatingOutline ? <RefreshCw size={15} /> : <Play size={15} fill="currentColor" />}
              <span>{isCreatingOutline ? "Generating outline" : "Generate an outline for me"}</span>
            </button>
            <button className="primary-action-button" type="button" onClick={onComplete} disabled={!hasOutlineText || isLocked || isCreatingOutline || isImportingOutline}>
              Next
            </button>
          </div>
          {showTemplateControls ? (
            <div className="sample-template-controls draft-flow-template-controls">
              <select aria-label="Sample outline template" value={selectedOutlineTemplate || ""} onChange={(event) => onOutlineTemplateChange?.(event.target.value)} disabled={isLocked || isCreatingOutline || isImportingOutline || !hasTemplates}>
                <option value="">{hasTemplates ? "-- Use sample template --" : "No templates available"}</option>
                {outlineTemplates.map((template) => (
                  <option key={template.name} value={template.name}>
                    {template.label || template.name}
                  </option>
                ))}
              </select>
              <select aria-label="Uploaded outline template" value={selectedUploadedOutlineTemplate || ""} onChange={(event) => onUploadedOutlineTemplateChange?.(event.target.value)} disabled={isLocked || isCreatingOutline || isImportingOutline || !hasUploadedTemplates}>
                <option value="">{hasUploadedTemplates ? "-- Use uploaded template --" : "No uploaded templates"}</option>
                {uploadedOutlineTemplates.map((template) => (
                  <option key={template.name} value={template.name}>
                    {template.label || template.name}
                  </option>
                ))}
              </select>
            </div>
          ) : null}
        </div>
        {isGeneratedOutlineEditorOpen ? (
          <aside className="draft-flow-editor-side" aria-label="Outline editor preview">
            <OutlineEditor outline={outline} isOpen={isGeneratedOutlineEditorOpen} onClose={() => setIsGeneratedOutlineEditorOpen(false)} onSave={setOutline} variant="inline" />
          </aside>
        ) : null}
      </div>
      <ConfirmDialog
        isOpen={isCreateOutlineConfirmOpen}
        title="Create a new outline?"
        icon={<AlertTriangle size={18} />}
        dialogId="draft-flow-create-outline-confirm"
        onClose={() => setIsCreateOutlineConfirmOpen(false)}
        actions={[
          {
            label: "Keep current outline",
            onClick: () => setIsCreateOutlineConfirmOpen(false),
            autoFocus: true,
          },
          {
            label: "Create new outline",
            variant: "danger",
            onClick: confirmGeneratedOutline,
          },
        ]}
      >
        <p>Creating a new outline will reset the current manuscript and replace the outline after the generated outline is ready.</p>
      </ConfirmDialog>
    </section>
  );
}
