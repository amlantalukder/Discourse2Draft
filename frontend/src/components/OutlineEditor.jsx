import { CornerDownRight, Pencil, Plus, Save, X } from "./FontAwesomeIcons";
import { useEffect, useState } from "react";
import { IconButton } from "./IconButton";

const CONTENT_MARKER = "[--content--]";
const INSTRUCTIONS_START = "[--instructions--]";
const INSTRUCTIONS_END = "[/--instructions--]";
const MAX_HEADING_LEVEL = 6;

let outlineSectionCounter = 0;

function createSectionId() {
  outlineSectionCounter += 1;
  return `outline-section-${Date.now()}-${outlineSectionCounter}`;
}

function normalizeLevel(value, fallback = 1) {
  const level = Number.parseInt(value, 10);
  if (Number.isNaN(level)) return fallback;
  return Math.max(1, Math.min(MAX_HEADING_LEVEL, level));
}

function createSection({ title = "New section", level = 1, instructions = "", userContent = "", userContentBefore = "", userContentAfter = "", contentAi = false } = {}) {
  const beforeText = userContentBefore || userContent;
  return {
    id: createSectionId(),
    title,
    level: normalizeLevel(level),
    hasInstructions: Boolean(instructions),
    instructions,
    hasUserContentBefore: Boolean(beforeText),
    userContentBefore: beforeText,
    contentAi,
    hasUserContentAfter: Boolean(userContentAfter),
    userContentAfter,
    children: [],
  };
}

function shiftSectionLevels(section, delta) {
  const nextLevel = normalizeLevel(section.level + delta);
  return {
    ...section,
    level: nextLevel,
    children: section.children.map((child) => shiftSectionLevels(child, delta)),
  };
}

function enforceSingleTopLevelSection(sections) {
  if (!sections.length) {
    return [createSection({ title: "Untitled outline", level: 1 })];
  }

  const [firstSection, ...extraTopLevelSections] = sections;
  const topLevelSection = shiftSectionLevels(firstSection, 1 - firstSection.level);
  const demotedExtraSections = extraTopLevelSections.map((section) => shiftSectionLevels(section, 2 - section.level));

  return [
    {
      ...topLevelSection,
      level: 1,
      children: [...topLevelSection.children, ...demotedExtraSections],
    },
  ];
}

function normalizeSectionsForHierarchy(sections, { enforceTopLevel = true } = {}) {
  const cleanedSections = sections
    .map((section, index) => {
      const title = section.title.trim();
      const isTopLevelSection = enforceTopLevel && index === 0 && section.level === 1;
      if (!title && !isTopLevelSection) return null;

      const contentAi = Boolean(section.contentAi);
      const instructions = section.instructions.trim();
      const userContentBefore = contentAi ? section.userContentBefore.trim() : "";
      const userContentAfter = contentAi ? section.userContentAfter.trim() : "";

      return {
        ...section,
        title: title || "Untitled outline",
        hasInstructions: Boolean(instructions),
        instructions,
        hasUserContentBefore: contentAi && Boolean(userContentBefore),
        userContentBefore,
        contentAi,
        hasUserContentAfter: contentAi && Boolean(userContentAfter),
        userContentAfter,
        children: normalizeSectionsForHierarchy(section.children, { enforceTopLevel: false }),
      };
    })
    .filter(Boolean);

  return enforceTopLevel ? enforceSingleTopLevelSection(cleanedSections) : cleanedSections;
}

function addText(current, nextText) {
  const next = nextText.trim();
  if (!next) return current;
  return current ? `${current}\n\n${next}` : next;
}

function parseOutline(outline) {
  const root = { level: 0, children: [] };
  const stack = [root];
  let currentSection = null;
  let userLines = [];
  let instructionLines = [];
  let isReadingInstructions = false;
  let isAfterAiContent = false;

  function ensureSection() {
    if (currentSection) return currentSection;

    currentSection = createSection({ title: "Untitled section", level: 1 });
    root.children.push(currentSection);
    stack.length = 1;
    stack.push(currentSection);
    return currentSection;
  }

  function flushInstructions() {
    if (!currentSection) return;
    const text = instructionLines.join("\n").trim();
    if (text) {
      currentSection.instructions = addText(currentSection.instructions, text);
      currentSection.hasInstructions = true;
    }
    instructionLines = [];
  }

  function flushUserContent() {
    if (!currentSection) return;
    const text = userLines.join("\n").trim();
    if (text) {
      if (isAfterAiContent) {
        currentSection.userContentAfter = addText(currentSection.userContentAfter, text);
        currentSection.hasUserContentAfter = true;
      } else {
        currentSection.userContentBefore = addText(currentSection.userContentBefore, text);
        currentSection.hasUserContentBefore = true;
      }
    }
    userLines = [];
  }

  outline.split(/\r?\n/).forEach((rawLine) => {
    const line = rawLine.trimEnd();
    const trimmedLine = line.trim();
    const heading = trimmedLine.match(/^(#{1,6})\s+(.+)$/);

    if (heading && !isReadingInstructions) {
      flushUserContent();
      flushInstructions();

      const level = normalizeLevel(heading[1].length);
      const title = heading[2].trim() || "Untitled section";
      while (stack.length > 1 && stack[stack.length - 1].level >= level) {
        stack.pop();
      }

      const parent = stack[stack.length - 1];
      currentSection = createSection({ title, level });
      isAfterAiContent = false;
      parent.children.push(currentSection);
      stack.push(currentSection);
      return;
    }

    if (!trimmedLine && !currentSection) return;
    const section = ensureSection();

    if (trimmedLine === INSTRUCTIONS_START) {
      flushUserContent();
      isReadingInstructions = true;
      return;
    }

    if (trimmedLine === INSTRUCTIONS_END) {
      flushInstructions();
      isReadingInstructions = false;
      return;
    }

    if (trimmedLine === CONTENT_MARKER && !isReadingInstructions) {
      flushUserContent();
      section.contentAi = true;
      isAfterAiContent = true;
      return;
    }

    if (isReadingInstructions) {
      instructionLines.push(line);
    } else {
      userLines.push(line);
    }
  });

  flushUserContent();
  flushInstructions();

  return enforceSingleTopLevelSection(root.children);
}

function serializeSection(section) {
  const title = section.title.trim() || "Untitled section";
  const parts = [`${"#".repeat(normalizeLevel(section.level))} ${title}`];

  if (section.hasInstructions && section.instructions.trim()) {
    parts.push(`${INSTRUCTIONS_START}\n${section.instructions.trim()}\n${INSTRUCTIONS_END}`);
  }

  if (section.contentAi && section.hasUserContentBefore && section.userContentBefore.trim()) {
    parts.push(section.userContentBefore.trim());
  }

  if (section.contentAi) {
    parts.push(CONTENT_MARKER);
  }

  if (section.hasUserContentAfter && section.userContentAfter.trim()) {
    parts.push(section.userContentAfter.trim());
  }

  section.children.forEach((child) => {
    parts.push(serializeSection(child));
  });

  return parts.filter(Boolean).join("\n\n");
}

function serializeOutline(sections) {
  return normalizeSectionsForHierarchy(sections).map(serializeSection).join("\n\n").trim();
}

function updateSection(sections, sectionId, updater) {
  return sections.map((section) => {
    if (section.id === sectionId) {
      return updater(section);
    }

    return {
      ...section,
      children: updateSection(section.children, sectionId, updater),
    };
  });
}

function insertAfterSection(sections, sectionId, nextSection) {
  const result = [];

  for (const section of sections) {
    result.push({
      ...section,
      children: insertAfterSection(section.children, sectionId, nextSection),
    });

    if (section.id === sectionId) {
      result.push(nextSection);
    }
  }

  return result;
}

function insertBeforeSection(sections, sectionId, nextSection) {
  const result = [];

  for (const section of sections) {
    if (section.id === sectionId) {
      result.push(nextSection);
    }

    result.push({
      ...section,
      children: insertBeforeSection(section.children, sectionId, nextSection),
    });
  }

  return result;
}

function deleteSection(sections, sectionId) {
  return sections
    .filter((section) => section.id !== sectionId)
    .map((section) => ({
      ...section,
      children: deleteSection(section.children, sectionId),
    }));
}

function contentLabel(type) {
  if (type === "instructions") return "Instructions for AI";
  if (type === "userContentBefore") return "Content before AI";
  if (type === "userContentAfter") return "Content after AI";
  return "Room for AI content";
}

function contentPreview(section, type) {
  if (type === "instructions") return section.instructions.trim() || "Instructions";
  if (type === "userContentBefore") return section.userContentBefore.trim() || "Content before AI";
  if (type === "userContentAfter") return section.userContentAfter.trim() || "Content after AI";
  return "[Room for AI content]";
}

function availableContentTypes(section) {
  return [section.contentAi && !section.hasInstructions ? "instructions" : null, section.contentAi && !section.hasUserContentBefore ? "userContentBefore" : null, !section.contentAi ? "contentAi" : null, section.contentAi && !section.hasUserContentAfter ? "userContentAfter" : null].filter(Boolean);
}

function addContentToSection(section, type) {
  if (type === "instructions") {
    return {
      ...section,
      hasInstructions: true,
      instructions: section.instructions || "",
    };
  }

  if (type === "userContent") {
    return {
      ...section,
      hasUserContentBefore: true,
      userContentBefore: section.userContentBefore || "",
    };
  }

  if (type === "userContentBefore") {
    return {
      ...section,
      hasUserContentBefore: true,
      userContentBefore: section.userContentBefore || "",
    };
  }

  if (type === "userContentAfter") {
    return {
      ...section,
      hasUserContentAfter: true,
      userContentAfter: section.userContentAfter || "",
    };
  }

  return {
    ...section,
    contentAi: true,
  };
}

function removeContentFromSection(section, type) {
  if (type === "instructions") {
    return {
      ...section,
      hasInstructions: false,
      instructions: "",
    };
  }

  if (type === "userContent") {
    return {
      ...section,
      hasUserContentBefore: false,
      userContentBefore: "",
    };
  }

  if (type === "userContentBefore") {
    return {
      ...section,
      hasUserContentBefore: false,
      userContentBefore: "",
    };
  }

  if (type === "userContentAfter") {
    return {
      ...section,
      hasUserContentAfter: false,
      userContentAfter: "",
    };
  }

  return {
    ...section,
    contentAi: false,
    hasInstructions: false,
    instructions: "",
    hasUserContentBefore: false,
    userContentBefore: "",
    hasUserContentAfter: false,
    userContentAfter: "",
  };
}

function updateContentValue(section, type, value) {
  if (type === "instructions") {
    return {
      ...section,
      instructions: value,
    };
  }

  if (type === "userContent") {
    return {
      ...section,
      userContentBefore: value,
    };
  }

  if (type === "userContentBefore") {
    return {
      ...section,
      userContentBefore: value,
    };
  }

  if (type === "userContentAfter") {
    return {
      ...section,
      userContentAfter: value,
    };
  }

  return section;
}

function AddMenu({ section, canAddBefore = false, canAddAfter = false, canAddChild = false, onAddBefore = () => {}, onAddAfter = () => {}, onAddChild = () => {}, onAddContent }) {
  const contentTypes = availableContentTypes(section);
  const hasOptions = canAddBefore || canAddAfter || canAddChild || contentTypes.length > 0;
  function closeMenu(event) {
    event.currentTarget.closest("details")?.removeAttribute("open");
  }

  return (
    <details className="outline-editor-add-menu">
      <summary aria-label="Add outline item" title="Add outline item">
        <Plus size={16} />
      </summary>
      <div>
        {canAddBefore ? (
          <button
            type="button"
            onClick={(event) => {
              closeMenu(event);
              onAddBefore();
            }}
          >
            Section before
          </button>
        ) : null}
        {canAddAfter ? (
          <button
            type="button"
            onClick={(event) => {
              closeMenu(event);
              onAddAfter();
            }}
          >
            Section after
          </button>
        ) : null}
        {canAddChild ? (
          <button
            type="button"
            onClick={(event) => {
              closeMenu(event);
              onAddChild();
            }}
          >
            Subsection
          </button>
        ) : null}
        {contentTypes.map((type) => (
          <button
            key={type}
            type="button"
            onClick={(event) => {
              closeMenu(event);
              onAddContent(type);
            }}
          >
            {contentLabel(type)}
          </button>
        ))}
        {!hasOptions ? <span>Nothing to add</span> : null}
      </div>
    </details>
  );
}

export function OutlineEditor({ outline, isOpen, onClose, onSave, variant = "modal", fileName = "", onFileNameRename }) {
  const [sections, setSections] = useState([]);
  const [editingTarget, setEditingTarget] = useState(null);
  const [isRenamingFileName, setIsRenamingFileName] = useState(false);
  const [draftFileName, setDraftFileName] = useState("");
  const isInline = variant === "inline";

  useEffect(() => {
    if (!isOpen) return;

    const parsedSections = parseOutline(outline);
    setSections(parsedSections);
    setEditingTarget(null);
  }, [isOpen, outline]);

  useEffect(() => {
    if (!isOpen) return;
    setDraftFileName(fileName || "");
    setIsRenamingFileName(false);
  }, [fileName, isOpen]);

  useEffect(() => {
    if (!isOpen) return undefined;

    function closeOpenMenus() {
      document.querySelectorAll(".outline-editor-add-menu[open]").forEach((menu) => {
        menu.removeAttribute("open");
      });
    }

    function handlePointerDown(event) {
      document.querySelectorAll(".outline-editor-add-menu[open]").forEach((menu) => {
        if (event.target instanceof Node && !menu.contains(event.target)) {
          menu.removeAttribute("open");
        }
      });
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        const hasOpenMenus = document.querySelector(".outline-editor-add-menu[open]");
        if (hasOpenMenus) {
          closeOpenMenus();
          event.stopPropagation();
          return;
        }
        if (!isInline) {
          onClose();
        }
      }
    }

    window.addEventListener("pointerdown", handlePointerDown);
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("pointerdown", handlePointerDown);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isInline, isOpen, onClose]);

  const hasSections = sections.length > 0;

  if (!isOpen) return null;

  function addSection() {
    const nextSection = createSection({ title: sections.length ? "New section" : "Untitled outline", level: sections.length ? 2 : 1 });
    if (!sections.length) {
      setSections([nextSection]);
      setEditingTarget({ id: nextSection.id, type: "section" });
      return;
    }

    const topLevelSection = sections[0];
    setSections((current) =>
      updateSection(current, topLevelSection.id, (section) => ({
        ...section,
        children: [...section.children, nextSection],
      })),
    );
    setEditingTarget({ id: nextSection.id, type: "section" });
  }

  function addSectionBefore(section) {
    if (!section || section.level === 1) {
      addSection();
      return;
    }

    const nextSection = createSection({ title: "New section", level: section.level });
    setSections((current) => insertBeforeSection(current, section.id, nextSection));
    setEditingTarget({ id: nextSection.id, type: "section" });
  }

  function addSectionAfter(section) {
    if (!section || section.level === 1) {
      addSection();
      return;
    }

    const nextSection = createSection({ title: "New section", level: section.level });
    setSections((current) => insertAfterSection(current, section.id, nextSection));
    setEditingTarget({ id: nextSection.id, type: "section" });
  }

  function addChildSection(section) {
    if (!section || section.level >= MAX_HEADING_LEVEL) return;

    const nextSection = createSection({ title: "New subsection", level: section.level + 1 });
    setSections((current) =>
      updateSection(current, section.id, (currentSection) => ({
        ...currentSection,
        children: [...currentSection.children, nextSection],
      })),
    );
    setEditingTarget({ id: nextSection.id, type: "section" });
  }

  function removeSection(section) {
    if (!section || section.level === 1) return;
    const nextSections = deleteSection(sections, section.id);
    const normalizedSections = enforceSingleTopLevelSection(nextSections);
    setSections(normalizedSections);
    setEditingTarget(null);
  }

  function updateCurrentSection(sectionId, updater) {
    setSections((current) => updateSection(current, sectionId, updater));
  }

  function addContent(section, type) {
    updateCurrentSection(section.id, (currentSection) => addContentToSection(currentSection, type));
    if (type !== "contentAi") {
      setEditingTarget({ id: section.id, type });
    }
  }

  function removeContent(section, type) {
    updateCurrentSection(section.id, (currentSection) => removeContentFromSection(currentSection, type));
    if (editingTarget?.id === section.id && editingTarget?.type === type) {
      setEditingTarget(null);
    }
  }

  function commitSectionEdit(section) {
    if (!section.title.trim()) {
      if (section.level === 1) {
        updateCurrentSection(section.id, (currentSection) => ({
          ...currentSection,
          title: "Untitled outline",
        }));
      } else {
        removeSection(section);
      }
    } else {
      updateCurrentSection(section.id, (currentSection) => ({
        ...currentSection,
        title: currentSection.title.trim(),
      }));
    }
    setEditingTarget(null);
  }

  function commitContentEdit(section, type) {
    const value = type === "instructions" ? section.instructions : type === "userContentAfter" ? section.userContentAfter : section.userContentBefore;
    if (!value.trim()) {
      removeContent(section, type);
      return;
    }

    updateCurrentSection(section.id, (currentSection) => updateContentValue(currentSection, type, value.trim()));
    setEditingTarget(null);
  }

  function handleSave() {
    const normalizedSections = normalizeSectionsForHierarchy(sections);
    setSections(normalizedSections);
    onSave(serializeOutline(normalizedSections));
  }

  async function commitFileNameRename() {
    const nextName = draftFileName.trim();
    if (!nextName) {
      setDraftFileName(fileName || "");
      setIsRenamingFileName(false);
      return;
    }

    if (!onFileNameRename || nextName === fileName) {
      setIsRenamingFileName(false);
      return;
    }

    const didRename = await onFileNameRename(nextName);
    if (didRename !== false) {
      setIsRenamingFileName(false);
    }
  }

  function renderContentRow(section, type) {
    const isEditing = editingTarget?.id === section.id && editingTarget?.type === type;
    const canEditText = type !== "contentAi";

    return (
      <div className={`outline-editor-content-card outline-editor-content-${type}`} key={`${section.id}-${type}`} style={{ "--depth": section.level }}>
        <div className="outline-editor-row-body">
          {isEditing && canEditText ? (
            <textarea autoFocus value={type === "instructions" ? section.instructions : type === "userContentAfter" ? section.userContentAfter : section.userContentBefore} onBlur={() => commitContentEdit(section, type)} onChange={(event) => updateCurrentSection(section.id, (currentSection) => updateContentValue(currentSection, type, event.target.value))} />
          ) : (
            <span>{contentPreview(section, type)}</span>
          )}
        </div>
        <div className="outline-editor-row-actions">
          <AddMenu section={section} canAddChild={false} onAddChild={() => {}} onAddContent={(contentType) => addContent(section, contentType)} />
          <button type="button" aria-label={`Remove ${contentLabel(type)}`} title={`Remove ${contentLabel(type)}`} onClick={() => removeContent(section, type)}>
            <X size={15} />
          </button>
          {canEditText ? (
            <button type="button" aria-label={`Edit ${contentLabel(type)}`} title={`Edit ${contentLabel(type)}`} onClick={() => setEditingTarget(isEditing ? null : { id: section.id, type })}>
              <Pencil size={15} />
            </button>
          ) : null}
        </div>
      </div>
    );
  }

  function renderSection(section) {
    const isEditing = editingTarget?.id === section.id && editingTarget?.type === "section";
    const canAddChild = section.level < MAX_HEADING_LEVEL;
    const canAddSibling = section.level > 1;
    const canDeleteSection = section.level > 1;

    return (
      <div className="outline-editor-node" key={section.id}>
        <div className={`outline-editor-section-card outline-editor-level-${section.level}`} style={{ "--depth": section.level - 1 }}>
          <div className="outline-editor-row-body">
            {isEditing ? (
              <input
                autoFocus
                type="text"
                value={section.title}
                onBlur={() => commitSectionEdit(section)}
                onChange={(event) =>
                  updateCurrentSection(section.id, (currentSection) => ({
                    ...currentSection,
                    title: event.target.value,
                  }))
                }
              />
            ) : (
              <strong>{section.title.trim() || "Untitled section"}</strong>
            )}
          </div>
          <div className="outline-editor-row-actions">
            <AddMenu section={section} canAddBefore={canAddSibling} canAddAfter={canAddSibling} canAddChild={canAddChild} onAddBefore={() => addSectionBefore(section)} onAddAfter={() => addSectionAfter(section)} onAddChild={() => addChildSection(section)} onAddContent={(type) => addContent(section, type)} />
            <button type="button" aria-label="Add sibling section" title={canAddSibling ? "Add section after" : "The top-level section cannot have a sibling"} disabled={!canAddSibling} onClick={() => addSectionAfter(section)}>
              <CornerDownRight size={15} />
            </button>
            <button type="button" aria-label="Delete section" title={canDeleteSection ? "Delete section" : "The top-level section is required"} disabled={!canDeleteSection} onClick={() => removeSection(section)}>
              <X size={15} />
            </button>
            <button type="button" aria-label="Edit section header" title="Edit section header" onClick={() => setEditingTarget(isEditing ? null : { id: section.id, type: "section" })}>
              <Pencil size={15} />
            </button>
          </div>
        </div>

        {section.hasInstructions ? renderContentRow(section, "instructions") : null}
        {section.contentAi && section.hasUserContentBefore ? renderContentRow(section, "userContentBefore") : null}
        {section.contentAi ? renderContentRow(section, "contentAi") : null}
        {section.hasUserContentAfter ? renderContentRow(section, "userContentAfter") : null}
        {section.children.map(renderSection)}
      </div>
    );
  }

  return (
    <div className={`outline-editor-shell ${isInline ? "outline-editor-shell-inline" : ""}`} role={isInline ? "region" : "dialog"} aria-modal={isInline ? undefined : "true"} aria-labelledby="outline-editor-title">
      <section className="outline-editor-window">
        <header>
          <div className="outline-editor-heading">
            <h2 id="outline-editor-title">Outline editor</h2>
            {fileName ? (
              <div className="outline-editor-file-control">
                {isRenamingFileName ? (
                  <>
                    <input
                      type="text"
                      value={draftFileName}
                      aria-label="Outline template file name"
                      onChange={(event) => setDraftFileName(event.target.value)}
                      onKeyDown={(event) => {
                        event.stopPropagation();
                        if (event.key === "Enter") {
                          event.preventDefault();
                          commitFileNameRename();
                        }
                        if (event.key === "Escape") {
                          event.preventDefault();
                          setDraftFileName(fileName || "");
                          setIsRenamingFileName(false);
                        }
                      }}
                      autoFocus
                    />
                    <button type="button" className="outline-editor-file-action" onClick={commitFileNameRename} aria-label="Save outline template name" title="Save outline template name">
                      <Save size={13} />
                    </button>
                    <button
                      type="button"
                      className="outline-editor-file-action"
                      onClick={() => {
                        setDraftFileName(fileName || "");
                        setIsRenamingFileName(false);
                      }}
                      aria-label="Cancel outline template rename"
                      title="Cancel outline template rename"
                    >
                      <X size={13} />
                    </button>
                  </>
                ) : (
                  <>
                    <strong title={fileName}>{fileName}</strong>
                    {onFileNameRename ? (
                      <button
                        type="button"
                        className="outline-editor-file-action"
                        onClick={() => {
                          setDraftFileName(fileName || "");
                          setIsRenamingFileName(true);
                        }}
                        aria-label="Rename outline template"
                        title="Rename outline template"
                      >
                        <Pencil size={13} />
                      </button>
                    ) : null}
                  </>
                )}
              </div>
            ) : null}
          </div>
          <IconButton label="Close outline editor" type="button" onClick={onClose}>
            <X size={18} />
          </IconButton>
        </header>

        <div className="outline-editor-canvas">
          <div className="outline-editor-list">{hasSections ? sections.map(renderSection) : <p className="outline-editor-empty">Add a section to start building the outline.</p>}</div>
        </div>

        <footer>
          <button className="tool-button" type="button" onClick={onClose}>
            Cancel
          </button>
          <button className="tool-button primary" type="button" onClick={handleSave} disabled={!sections.length}>
            <Save size={15} />
            <span>Save outline</span>
          </button>
        </footer>
      </section>
    </div>
  );
}
