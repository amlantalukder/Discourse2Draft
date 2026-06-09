import { Save, X } from "./FontAwesomeIcons";
import { useEffect, useState } from "react";
import { IconButton } from "./IconButton";

export function SettingsPanel({ settings, modelOptions = [], isOpen, isSaving, onClose, onSave }) {
  const [draft, setDraft] = useState({
    llm: "",
    temperature: 0,
    instructions: "",
  });

  useEffect(() => {
    setDraft({
      llm: settings?.llm ?? "",
      temperature: settings?.temperature ?? 0,
      instructions: settings?.instructions ?? "",
    });
  }, [settings, isOpen]);

  if (!isOpen) return null;

  function updateDraft(field) {
    return (event) => {
      const value = field === "temperature" ? Number(event.target.value) : event.target.value;
      setDraft((current) => ({ ...current, [field]: value }));
    };
  }

  function handleSubmit(event) {
    event.preventDefault();
    onSave(draft);
  }

  const options = modelOptions.length ? modelOptions : [{ provider: "Available", value: draft.llm, label: draft.llm }];
  const groupedOptions = options.reduce((groups, option) => {
    const provider = option.provider || "Available";
    return {
      ...groups,
      [provider]: [...(groups[provider] ?? []), option],
    };
  }, {});

  return (
    <div className="settings-panel-shell" role="presentation">
      <form className="settings-panel" onSubmit={handleSubmit}>
        <header>
          <h2>Settings</h2>
          <IconButton label="Close settings" type="button" onClick={onClose}>
            <X size={17} />
          </IconButton>
        </header>

        <div className="settings-panel-body">
          <label className="settings-field">
            <span>LLM</span>
            <select value={draft.llm} onChange={updateDraft("llm")}>
              {Object.entries(groupedOptions).map(([provider, providerOptions]) => (
                <optgroup key={provider} label={provider}>
                  {providerOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>

          <label className="settings-field">
            <span>Temperature</span>
            <div className="temperature-control">
              <input min="0" max="2" step="0.1" type="range" value={draft.temperature} onChange={updateDraft("temperature")} />
              <input min="0" max="2" step="0.1" type="number" value={draft.temperature} onChange={updateDraft("temperature")} />
            </div>
          </label>

          <label className="settings-field">
            <span>Instructions</span>
            <textarea value={draft.instructions} onChange={updateDraft("instructions")} />
          </label>
        </div>

        <footer>
          <button className="tool-button" type="submit" disabled={isSaving}>
            <Save size={15} />
            <span>{isSaving ? "Saving" : "Save"}</span>
          </button>
        </footer>
      </form>
    </div>
  );
}
