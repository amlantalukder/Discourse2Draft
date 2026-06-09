import { Download } from "./FontAwesomeIcons";
import { useEffect, useRef, useState } from "react";
import { IconButton } from "./IconButton";

const downloadOptions = [
  { format: "md", label: "Markdown", extension: ".md", group: "Main text" },
  { format: "docx", label: "Word document", extension: ".docx", group: "Main text" },
  { format: "latex", label: "LaTeX package", extension: ".zip", group: "Main text + bibliography" },
];

export function DownloadMenu({ label = "Download", disabled = false, onDownload, menuAlign = "right" }) {
  const [isOpen, setIsOpen] = useState(false);
  const [menuStyle, setMenuStyle] = useState({});
  const menuRef = useRef(null);

  function updateMenuPosition() {
    const button = menuRef.current?.querySelector(".icon-button");
    if (!button) return;

    const rect = button.getBoundingClientRect();
    const menuWidth = 208;
    const menuHeight = 170;
    const pagePadding = 12;
    const preferredLeft = menuAlign === "left" ? rect.left : rect.right - menuWidth;
    const left = Math.min(Math.max(preferredLeft, pagePadding), window.innerWidth - menuWidth - pagePadding);
    const opensDown = rect.bottom + 8 + menuHeight < window.innerHeight;
    const top = opensDown ? rect.bottom + 8 : Math.max(pagePadding, rect.top - menuHeight - 8);

    setMenuStyle({ left: `${left}px`, top: `${top}px` });
  }

  useEffect(() => {
    function closeMenu(event) {
      if (!menuRef.current || menuRef.current.contains(event.target)) return;
      setIsOpen(false);
    }

    document.addEventListener("mousedown", closeMenu);
    return () => document.removeEventListener("mousedown", closeMenu);
  }, []);

  useEffect(() => {
    if (!isOpen) return undefined;

    updateMenuPosition();

    function handleKeyDown(event) {
      if (event.key === "Escape") setIsOpen(false);
    }

    window.addEventListener("resize", updateMenuPosition);
    window.addEventListener("scroll", updateMenuPosition, true);
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("resize", updateMenuPosition);
      window.removeEventListener("scroll", updateMenuPosition, true);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, menuAlign]);

  function selectFormat(format) {
    if (disabled) return;
    setIsOpen(false);
    onDownload?.(format);
  }

  return (
    <div className={`download-menu download-menu-${menuAlign}`} ref={menuRef}>
      <IconButton label={label} type="button" disabled={disabled} onClick={() => setIsOpen((current) => !current)}>
        <Download size={18} />
      </IconButton>
      {isOpen && !disabled ? (
        <div className="download-options" role="menu" aria-label="Download options" style={menuStyle}>
          {downloadOptions.map((option, index) => (
            <div className="download-option-group" key={option.format}>
              {index === 0 || downloadOptions[index - 1].group !== option.group ? <span>{option.group}</span> : null}
              <button type="button" role="menuitem" onClick={() => selectFormat(option.format)}>
                <strong>{option.extension}</strong>
                <span>{option.label}</span>
              </button>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
