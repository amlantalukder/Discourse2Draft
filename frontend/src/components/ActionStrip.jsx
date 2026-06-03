import { Play, Trash2 } from "lucide-react";
import { IconButton } from "./IconButton";

const actions = ["Expand", "Rephrase", "Remove"];

export function ActionStrip({ action, setAction, onWrite, isWriting }) {
  return (
    <section className="action-strip">
      <span>Content starts below ...</span>
      <div className="inline-actions">
        {actions.map((label) => (
          <label key={label}>
            <input
              checked={action === label}
              onChange={() => setAction(label)}
              name="edit-action"
              type="radio"
            />
            <span>{label}</span>
          </label>
        ))}
        <IconButton label="Clear action">
          <Trash2 size={16} />
        </IconButton>
        <IconButton label="Run action" onClick={onWrite} disabled={isWriting}>
          <Play size={16} fill="currentColor" />
        </IconButton>
      </div>
      <label className="toggle-row">
        <input type="checkbox" defaultChecked />
        <span>Literature Search</span>
      </label>
      <a href="#context">Using context from attached documents</a>
      <button className="concept-button">Concept map</button>
    </section>
  );
}
