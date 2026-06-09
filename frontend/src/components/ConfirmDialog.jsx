import { X } from "./FontAwesomeIcons";
import { useEffect, useRef } from "react";
import { IconButton } from "./IconButton";

export function ConfirmDialog({ isOpen, title, icon, dialogId = "confirm-dialog", children, actions = [], onClose }) {
  const focusedActionRef = useRef(null);
  const focusedActionIndex = Math.max(
    0,
    actions.findIndex((action) => action.autoFocus),
  );

  useEffect(() => {
    if (!isOpen) return undefined;

    focusedActionRef.current?.focus();

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose?.();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const titleId = `${dialogId}-title`;
  const contentId = `${dialogId}-message`;

  return (
    <div className="confirm-dialog-shell" role="presentation" onClick={onClose}>
      <section
        className="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={contentId}
        onClick={(event) => event.stopPropagation()}
      >
        <header>
          <div className="confirm-dialog-title">
            {icon ? (
              <span className="confirm-dialog-icon" aria-hidden="true">
                {icon}
              </span>
            ) : null}
            <h2 id={titleId}>{title}</h2>
          </div>
          <IconButton label="Close confirmation" type="button" onClick={onClose}>
            <X size={17} />
          </IconButton>
        </header>

        <div className="confirm-dialog-content" id={contentId}>
          {children}
        </div>

        <footer>
          {actions.map((action, index) => (
            <button
              className={`tool-button ${action.variant ?? ""}`.trim()}
              type="button"
              onClick={action.onClick}
              ref={index === focusedActionIndex ? focusedActionRef : null}
              key={action.label}
            >
              {action.icon}
              <span>{action.label}</span>
            </button>
          ))}
        </footer>
      </section>
    </div>
  );
}
