import { useRef } from "react";

function selectedFileLabel(files) {
  if (!files.length) return "No file selected";
  if (files.length === 1) return files[0].name;

  return `${files.length} files selected`;
}

export function FileUploadControl({ label, accept, multiple = false, files = [], onFilesChange }) {
  const inputRef = useRef(null);
  const selectedFiles = Array.isArray(files) ? files : files ? [files] : [];
  const selectedLabel = selectedFileLabel(selectedFiles);

  function handleChange(event) {
    const nextFiles = Array.from(event.target.files ?? []);
    onFilesChange?.(multiple ? nextFiles : (nextFiles[0] ?? null));
  }

  return (
    <div className="file-upload-control">
      <span className="file-upload-label">{label}</span>
      <div className="file-control">
        <button type="button" onClick={() => inputRef.current?.click()}>
          Browse...
        </button>
        <span title={selectedLabel}>{selectedLabel}</span>
        <input ref={inputRef} type="file" accept={accept} multiple={multiple} onChange={handleChange} />
      </div>
    </div>
  );
}
