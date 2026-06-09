import { Plus, Save, SlidersHorizontal } from "./FontAwesomeIcons";
import { IconButton } from "./IconButton";

export function WorkspaceHeader({ fileName, setFileName, onSave, onNewDocument, isSaving = false, settings, onOpenSettings }) {
  return (
    <section className="workspace-header">
      <div className="document-control">
        <label>
          <span>File Name</span>
          <input value={fileName} onChange={(event) => setFileName(event.target.value)} />
        </label>
        <button className="tool-button" type="button" onClick={onSave} disabled={isSaving}>
          <Save size={15} />
          <span>{isSaving ? "Saving" : "Save"}</span>
        </button>
        <IconButton label="New document" type="button" onClick={onNewDocument}>
          <Plus size={19} />
        </IconButton>
      </div>

      <button className="model-status" type="button" aria-label="Open model settings" onClick={onOpenSettings}>
        <SlidersHorizontal size={15} />
        <span>LLM</span>
        <strong>{settings?.llm ?? "Not set"}</strong>
        <span>Temperature</span>
        <strong>{Number(settings?.temperature ?? 0).toFixed(1)}</strong>
      </button>
    </section>
  );
}
