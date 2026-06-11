import { useEffect, useMemo, useRef, useState } from "react";

const STREAM_DELAY_MS = 50;

function nextWordChunk(text) {
  const match = text.match(/^\s*\S+\s*/);
  return match?.[0] ?? text.slice(0, 1);
}

function normalizeHeadingLevel(value, fallback = 2) {
  const level = Number.parseInt(value, 10);
  if (Number.isNaN(level)) return fallback;
  return Math.max(1, Math.min(6, level));
}

function headingLooksLikeAbstract(heading) {
  const normalized = String(heading ?? "")
    .toLowerCase()
    .replace(/[^a-z]+/g, " ")
    .trim();
  return normalized === "abstract" || normalized === "summary" || normalized === "executive summary" || normalized.startsWith("abstract ");
}

function isAbstractSection(section) {
  if (typeof section.is_abstract === "boolean") return section.is_abstract;
  if (typeof section.isAbstract === "boolean") return section.isAbstract;
  return headingLooksLikeAbstract(section.heading ?? section.title ?? section.header ?? section.section);
}

function normalizeSections(sections) {
  return sections.map((section, index) => {
    const fallbackLevel = index === 0 ? 1 : 2;
    return {
      ...section,
      heading: section.heading ?? section.title ?? section.header ?? section.section ?? "",
      level: normalizeHeadingLevel(section.level ?? section.depth ?? section.heading_level, fallbackLevel),
      body: section.body ?? section.content ?? section.text ?? "",
      rawBody: section.raw_body ?? section.rawBody ?? section.body ?? section.content ?? section.text ?? "",
      path: Array.isArray(section.path) ? section.path : [],
      isAbstract: isAbstractSection(section),
    };
  });
}

function alignStreamedSections(currentSections, targetSections) {
  return targetSections.map((section, index) => {
    const current = currentSections[index];
    const targetBody = section.body ?? "";
    const currentBody = current?.heading === section.heading && current?.level === section.level ? (current.body ?? "") : "";

    return {
      ...section,
      body: targetBody.startsWith(currentBody) ? currentBody : "",
    };
  });
}

function advanceOneWord(currentSections, targetSections) {
  const nextSections = alignStreamedSections(currentSections, targetSections);
  const sectionIndex = nextSections.findIndex((section, index) => section.body !== (targetSections[index]?.body ?? ""));

  if (sectionIndex === -1) {
    return { sections: nextSections, hasMore: false };
  }

  const targetBody = targetSections[sectionIndex]?.body ?? "";
  const currentBody = nextSections[sectionIndex].body ?? "";
  const remainingText = targetBody.slice(currentBody.length);
  const chunk = nextWordChunk(remainingText);
  nextSections[sectionIndex] = {
    ...nextSections[sectionIndex],
    body: targetBody.slice(0, currentBody.length + chunk.length),
  };

  return {
    sections: nextSections,
    hasMore: nextSections.some((section, index) => section.body !== (targetSections[index]?.body ?? "")),
  };
}

function sameHeading(left, right) {
  return String(left ?? "").trim().toLowerCase() === String(right ?? "").trim().toLowerCase();
}

function hasStreamingDelta(currentSections, targetSections) {
  return alignStreamedSections(currentSections, targetSections).some((section, index) => section.body !== (targetSections[index]?.body ?? ""));
}

function shouldShowLoadingDots({ index, section, targetSection, currentWritingSection, isActiveStreamingSection }) {
  if (index === 0) return false;

  const visibleBody = section.body ?? "";
  const targetBody = targetSection?.body ?? "";
  const isWaitingForBackend = !targetBody.trim();
  const isStreamingToTarget = Boolean(targetBody) && visibleBody !== targetBody;

  if (currentWritingSection) {
    if (!sameHeading(section.heading, currentWritingSection)) return false;
    return isWaitingForBackend || isStreamingToTarget;
  }

  return isActiveStreamingSection && isStreamingToTarget;
}

function LoadingDots({ inline = false }) {
  const Tag = inline ? "span" : "div";
  return (
    <Tag className="manuscript-loading-dots" role="status" aria-label="Writing section">
      <span />
      <span />
      <span />
    </Tag>
  );
}

function ManuscriptHeading({ level, children }) {
  const Tag = `h${normalizeHeadingLevel(level)}`;
  return <Tag>{children}</Tag>;
}

function splitBodyIntoParagraphs(body) {
  const text = String(body ?? "").replace(/\r\n/g, "\n").trim();
  if (!text) return [];

  const blocks = text.split(/\n\s*\n+/).map((block) => block.trim()).filter(Boolean);
  if (blocks.length > 1) return blocks;

  return text
    .split(/\n+/)
    .map((block) => block.trim())
    .filter(Boolean);
}

function paragraphId(section, sectionIndex, paragraphIndex) {
  return `${section.heading}-${section.level}-${sectionIndex}-${paragraphIndex}`;
}

function selectParagraphContents(element) {
  const selection = window.getSelection?.();
  if (!selection) return;

  const range = document.createRange();
  range.selectNodeContents(element);
  selection.removeAllRanges();
  selection.addRange(range);
}

function clearDocumentSelection() {
  window.getSelection?.()?.removeAllRanges();
}

function renderParagraphContent(paragraph) {
  const text = String(paragraph ?? "");
  const citationPattern = /<a\s+href="#:~:text=References">([^<]+)<\/a>/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = citationPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    parts.push(
      <a href="#References" className="manuscript-citation" key={`${match.index}-${match[1]}`}>
        {match[1]}
      </a>,
    );
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length ? parts : text;
}

function renderReference(reference) {
  const text = String(reference ?? "");
  const urlPattern = /https?:\/\/[^\s)\]}>,;]+/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = urlPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    const url = match[0];
    parts.push(
      <a className="manuscript-reference-link" href={url} key={`${match.index}-${url}`} target="_blank" rel="noreferrer">
        {url}
      </a>,
    );
    lastIndex = match.index + url.length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length ? parts : text;
}

export function Manuscript({
  manuscript = [],
  refList = [],
  generatedContent,
  isGenerating = false,
  currentWritingSection = "",
  selectedParagraphId = "",
  syncVersion = 0,
  updatingParagraphId = "",
  onParagraphSelectionChange,
}) {
  const sections = useMemo(() => {
    if (!generatedContent) return normalizeSections(manuscript);
    return normalizeSections([
      ...manuscript.slice(0, 2),
      {
        heading: "Generated Section",
        level: 2,
        body: generatedContent,
      },
      ...manuscript.slice(2),
    ]);
  }, [generatedContent, manuscript]);

  const streamedSectionsRef = useRef(sections);
  const streamGenerationChangesRef = useRef(false);
  const lastSyncVersionRef = useRef(syncVersion);
  const [streamedSections, setStreamedSections] = useState(sections);

  useEffect(() => {
    if (syncVersion !== lastSyncVersionRef.current) {
      lastSyncVersionRef.current = syncVersion;
      streamGenerationChangesRef.current = false;
      streamedSectionsRef.current = sections;
      setStreamedSections(sections);
      return undefined;
    }

    if (!isGenerating) {
      streamGenerationChangesRef.current = false;
      streamedSectionsRef.current = sections;
      setStreamedSections(sections);
      return undefined;
    }

    if (isGenerating) {
      streamGenerationChangesRef.current = true;
    }

    const shouldStream = streamGenerationChangesRef.current;
    const alignedSections = alignStreamedSections(streamedSectionsRef.current, sections);
    const hasPendingStream = hasStreamingDelta(streamedSectionsRef.current, sections);

    if (!shouldStream || !hasPendingStream) {
      streamGenerationChangesRef.current = false;
      streamedSectionsRef.current = sections;
      setStreamedSections(sections);
      return undefined;
    }

    let timeoutId;
    streamedSectionsRef.current = alignedSections;
    setStreamedSections(alignedSections);

    function streamNextWord() {
      const result = advanceOneWord(streamedSectionsRef.current, sections);
      streamedSectionsRef.current = result.sections;
      setStreamedSections(result.sections);

      if (result.hasMore) {
        timeoutId = window.setTimeout(streamNextWord, STREAM_DELAY_MS);
      } else {
        streamGenerationChangesRef.current = false;
      }
    }

    timeoutId = window.setTimeout(streamNextWord, STREAM_DELAY_MS);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [isGenerating, sections, syncVersion]);

  const visibleSections = streamedSections;
  const activeStreamingIndex = visibleSections.findIndex((section, index) => section.body !== (sections[index]?.body ?? ""));

  function handleParagraphClick(event, section, sectionIndex, paragraph, paragraphIndex) {
    event.stopPropagation();
    const id = paragraphId(section, sectionIndex, paragraphIndex);
    const rawParagraphs = splitBodyIntoParagraphs(section.rawBody);
    const rawParagraph = rawParagraphs[paragraphIndex] ?? paragraph;
    selectParagraphContents(event.currentTarget);
    onParagraphSelectionChange?.({
      id,
      text: paragraph,
      rawText: rawParagraph,
      heading: section.heading ?? "",
      level: section.level,
      path: section.path ?? [],
      index: sectionIndex,
      paragraphIndex,
      sectionBody: section.body ?? "",
      rawSectionBody: section.rawBody ?? section.body ?? "",
    });
  }

  function handleShellClick(event) {
    if (event.target.closest?.(".manuscript-paragraph")) return;
    clearDocumentSelection();
    onParagraphSelectionChange?.(null);
  }

  return (
    <div className="manuscript-shell" onClick={handleShellClick}>
      <article className="manuscript" id="preview">
        {visibleSections.map((section, index) => {
          const paragraphs = splitBodyIntoParagraphs(section.body);
          const showLoadingDots = shouldShowLoadingDots({
            index,
            section,
            targetSection: sections[index],
            currentWritingSection,
            isActiveStreamingSection: index === activeStreamingIndex,
          });

          return (
            <section key={`${section.heading}-${section.level}-${index}`} className={section.isAbstract ? "abstract-block" : ""}>
              {section.heading ? <ManuscriptHeading level={section.level}>{section.heading}</ManuscriptHeading> : null}
              {paragraphs.map((paragraph, paragraphIndex) => {
                const id = paragraphId(section, index, paragraphIndex);
                const isUpdatingParagraph = updatingParagraphId === id;

                return (
                  <p
                    className={`manuscript-paragraph ${selectedParagraphId === id ? "manuscript-paragraph-selected" : ""} ${isUpdatingParagraph ? "manuscript-paragraph-updating" : ""}`.trim()}
                    key={id}
                    onClick={(event) => handleParagraphClick(event, section, index, paragraph, paragraphIndex)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        handleParagraphClick(event, section, index, paragraph, paragraphIndex);
                      }
                    }}
                    role="button"
                    tabIndex={0}
                    aria-pressed={selectedParagraphId === id}
                  >
                    {isUpdatingParagraph ? <LoadingDots inline /> : renderParagraphContent(paragraph)}
                  </p>
                );
              })}
              {showLoadingDots ? <LoadingDots /> : null}
            </section>
          );
        })}
      </article>
      {refList.length ? (
        <section className="manuscript-references-panel" id="References" aria-labelledby="manuscript-references-title">
          <h2 id="manuscript-references-title">References</h2>
          <ol>
            {refList.map((reference, index) => (
              <li key={`${index}-${reference}`}>{renderReference(reference)}</li>
            ))}
          </ol>
        </section>
      ) : null}
    </div>
  );
}
