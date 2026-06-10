import { useRef, useState } from "react";
import { ConfirmDialog } from "./ConfirmDialog";
import { File, FileCode, FileCsv, FileLines, FilePdf, FileWord, FileZipper } from "./FontAwesomeIcons";

function selectedFileLabel(files) {
  if (!files.length) return "No file selected";
  if (files.length === 1) return files[0].name;

  return "Selected files";
}

const MAX_VISIBLE_FILE_NAMES = 3;
const MAX_SHORT_FILE_NAME_LENGTH = 26;

function fileExtension(fileName = "") {
  const lastDot = fileName.lastIndexOf(".");
  if (lastDot <= 0 || lastDot === fileName.length - 1) return "";
  return fileName.slice(lastDot + 1).toLowerCase();
}

function shortFileName(fileName = "") {
  if (fileName.length <= MAX_SHORT_FILE_NAME_LENGTH) return fileName;

  const extension = fileExtension(fileName);
  const suffix = extension ? `.${extension}` : "";
  const baseName = suffix ? fileName.slice(0, -suffix.length) : fileName;
  const availableBaseLength = Math.max(9, MAX_SHORT_FILE_NAME_LENGTH - suffix.length - 1);

  return `${baseName.slice(0, availableBaseLength)}...${suffix}`;
}

function fileIconFor(fileName = "") {
  const extension = fileExtension(fileName);
  if (extension === "pdf") return { Icon: FilePdf, kind: "pdf", label: "PDF file" };
  if (["doc", "docx"].includes(extension)) return { Icon: FileWord, kind: "word", label: "Word file" };
  if (["csv", "tsv"].includes(extension)) return { Icon: FileCsv, kind: "csv", label: "Spreadsheet file" };
  if (["txt", "md", "markdown"].includes(extension)) return { Icon: FileLines, kind: "text", label: "Text file" };
  if (["tex", "bib", "json", "xml", "html"].includes(extension)) return { Icon: FileCode, kind: "code", label: "Code file" };
  if (["zip", "gz", "tar"].includes(extension)) return { Icon: FileZipper, kind: "archive", label: "Archive file" };
  return { Icon: File, kind: "default", label: "File" };
}

export function FileUploadControl({ label, accept, multiple = true, files = [], onFilesChange, disabled = false }) {
  const inputRef = useRef(null);
  const [isFileListOpen, setIsFileListOpen] = useState(false);
  const selectedFiles = Array.isArray(files) ? files : files ? [files] : [];
  const selectedLabel = selectedFileLabel(selectedFiles);
  const visibleFiles = selectedFiles.slice(0, MAX_VISIBLE_FILE_NAMES);
  const hiddenFileCount = Math.max(0, selectedFiles.length - visibleFiles.length);

  function handleChange(event) {
    if (disabled) return;
    const nextFiles = Array.from(event.target.files ?? []);
    onFilesChange?.(multiple ? nextFiles : (nextFiles[0] ?? null));
    event.target.value = "";
  }

  return (
    <div className="file-upload-control">
      <span className="file-upload-label">{label}</span>
      <div className="file-control">
        <button type="button" onClick={() => inputRef.current?.click()} disabled={disabled}>
          Browse...
        </button>
        <span title={selectedLabel}>{selectedLabel}</span>
        <input ref={inputRef} type="file" accept={accept} multiple={multiple} onChange={handleChange} disabled={disabled} />
      </div>
      {selectedFiles.length ? (
        <div className="selected-file-list" aria-label="Selected files">
          {visibleFiles.map((file, index) => (
            <SelectedFileName file={file} key={`${file.name ?? "file"}-${index}`} />
          ))}
          {hiddenFileCount ? (
            <button className="selected-file-more" type="button" onClick={() => setIsFileListOpen(true)}>
              View all ({selectedFiles.length})
            </button>
          ) : null}
        </div>
      ) : null}
      <ConfirmDialog
        isOpen={isFileListOpen}
        title="Selected files"
        dialogId="selected-files-dialog"
        onClose={() => setIsFileListOpen(false)}
        actions={[
          {
            label: "Close",
            onClick: () => setIsFileListOpen(false),
            autoFocus: true,
          },
        ]}
      >
        <ul className="selected-file-dialog-list">
          {selectedFiles.map((file, index) => (
            <li key={`${file.name ?? "file"}-${index}`}>{file.name ?? "Untitled file"}</li>
          ))}
        </ul>
      </ConfirmDialog>
    </div>
  );
}

function SelectedFileName({ file }) {
  const fileName = file.name ?? "Untitled file";
  const { Icon, kind, label } = fileIconFor(fileName);

  return (
    <span className="selected-file-name" title={fileName}>
      <Icon className={`selected-file-icon selected-file-icon-${kind}`} size={12} aria-label={label} />
      <span className="selected-file-short-name">{shortFileName(fileName)}</span>
    </span>
  );
}
