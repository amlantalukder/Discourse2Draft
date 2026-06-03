import { ChevronDown, ChevronLeft, Download, Search, Trash2 } from "lucide-react";
import { useState } from "react";
import { FileUploadControl } from "./FileUploadControl";
import { IconButton } from "./IconButton";

export function Sidebar({
  generatedDocuments = [],
  selectedGeneratedDocumentId,
  onGeneratedDocumentSelect,
  uploadedDocuments = [],
}) {
  const [uploadFiles, setUploadFiles] = useState([]);

  return (
    <aside className="sidebar">
      <div className="collapse-handle">
        <ChevronLeft size={18} />
      </div>

      <section className="side-section">
        <header>
          <span>Generated documents</span>
          <ChevronDown size={17} />
        </header>
        <div className="generated-list">
          {generatedDocuments.length ? (
            generatedDocuments.map((document) => {
              const documentName = document.name ?? document.file_name ?? "Untitled";

              return (
                <div
                  className={`document-row ${String(document.id) === String(selectedGeneratedDocumentId) ? "active" : ""}`}
                  key={document.id ?? documentName + document.date}
                >
                  <div>
                    <button type="button" className="document-link" onClick={() => onGeneratedDocumentSelect?.(document)}>
                      {documentName}
                    </button>
                    <time>{document.date}</time>
                  </div>
                  <IconButton label={`Download ${documentName}`}>
                    <Download size={18} />
                  </IconButton>
                  <IconButton label={`Delete ${documentName}`}>
                    <Trash2 size={18} />
                  </IconButton>
                </div>
              );
            })
          ) : (
            <p className="empty-panel-message">No generated documents yet.</p>
          )}
        </div>
      </section>

      <section className="side-section uploaded">
        <header>
          <span>Uploaded documents</span>
          <ChevronDown size={17} />
        </header>
        <div className="upload-controls">
          <FileUploadControl
            label="Choose documents"
            accept=".txt,.pdf,.doc,.docx"
            multiple
            files={uploadFiles}
            onFilesChange={setUploadFiles}
          />
        </div>
        <label className="search-field">
          <Search size={16} />
          <input placeholder="Search" />
        </label>
        <label className="check-row">
          <input type="checkbox" />
          <span>Select all documents</span>
        </label>
        <div className="uploaded-list">
          {uploadedDocuments.length ? (
            uploadedDocuments.map(({ id, name, date, type }) => (
              <div className="uploaded-row" key={id ?? name}>
                <input type="checkbox" />
                <span className={`file-chip ${type}`}>{type}</span>
                <div>
                  <span>{name}</span>
                  <time>{date}</time>
                </div>
                <IconButton label={`Delete ${name}`}>
                  <Trash2 size={18} />
                </IconButton>
              </div>
            ))
          ) : (
            <p className="empty-panel-message">No uploaded documents yet.</p>
          )}
        </div>
      </section>
    </aside>
  );
}
