import { useEffect, useState } from "react";
import { X } from "./FontAwesomeIcons";
import aboutMarkdown from "../../docs/README.md?raw";
import { IconButton } from "./IconButton";

const figureAssets = import.meta.glob("../../docs/figures/*.{gif,jpeg,jpg,png,webp}", {
  eager: true,
  import: "default",
  query: "?url",
});

function cleanText(value) {
  return value
    .replace(/\\emph\{([^}]+)\}/g, "_$1_")
    .replace(/\\citep\{[^}]+\}/g, "")
    .replace(/\\#/g, "#")
    .replace(/\\</g, "<")
    .replace(/\\>/g, ">")
    .replace(/``/g, '"')
    .replace(/''/g, '"')
    .replace(/&nbsp;/g, " ")
    .replace(/<\/?strong>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function renderInline(text) {
  const parts = [];
  const pattern = /(\*\*[^*]+\*\*|_[^_]+_)/g;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    const token = match[0];
    const content = token.slice(2, -2);
    if (token.startsWith("**")) {
      parts.push(<strong key={`${match.index}-strong`}>{content}</strong>);
    } else {
      parts.push(<em key={`${match.index}-em`}>{token.slice(1, -1)}</em>);
    }

    lastIndex = match.index + token.length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts;
}

function parseAboutMarkdown(source) {
  const blocks = [];
  const paragraph = [];

  function flushParagraph() {
    const text = paragraph.join(" ").trim();
    if (text) {
      blocks.push({ type: "paragraph", text });
    }
    paragraph.length = 0;
  }

  source.split(/\r?\n/).forEach((rawLine) => {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph();
      return;
    }

    const divText = line.match(/^<div[^>]*>(.*?)<\/div>$/);
    if (divText) {
      const text = cleanText(divText[1]);
      if (text) paragraph.push(text);
      return;
    }

    if (/^<\/?div/.test(line)) {
      flushParagraph();
      return;
    }

    const image = line.match(/^<img\s+[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>/);
    if (image) {
      flushParagraph();
      blocks.push({ type: "figure", source: image[1], alt: cleanText(image[2]) });
      return;
    }

    if (/^<strong>Figure/.test(line)) {
      flushParagraph();
      blocks.push({ type: "caption", text: cleanText(line) });
      return;
    }

    const email = line.match(/^<([^@\s<>]+@[^<>]+)>$/);
    if (email) {
      paragraph.push(email[1]);
      return;
    }

    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      blocks.push({ type: "heading", depth: heading[1].length, text: cleanText(heading[2]) });
      return;
    }

    paragraph.push(cleanText(line));
  });

  flushParagraph();
  return blocks;
}

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function addHeadingIds(blocks) {
  const seen = new Map();

  return blocks.map((block) => {
    if (block.type !== "heading") {
      return block;
    }

    const baseId = slugify(block.text) || "section";
    const count = seen.get(baseId) ?? 0;
    seen.set(baseId, count + 1);

    return {
      ...block,
      id: count ? `${baseId}-${count + 1}` : baseId,
    };
  });
}

const aboutBlocks = addHeadingIds(parseAboutMarkdown(aboutMarkdown));
const tableOfContents = aboutBlocks.filter((block) => block.type === "heading");

function resolveFigureSource(source) {
  const normalizedSource = source
    .replace(/^\.\//, "")
    .replace(/^\.\.\/www\/assets\//, "figures/");
  const assetKey = `../../docs/${normalizedSource}`;

  return figureAssets[assetKey] ?? source;
}

function AboutFigure({ source, alt }) {
  const resolvedSource = resolveFigureSource(source);
  const [showImage, setShowImage] = useState(Boolean(resolvedSource));

  return (
    <figure className="about-figure">
      {showImage ? (
        <img src={resolvedSource} alt={alt || "About page figure"} onError={() => setShowImage(false)} />
      ) : (
        <div className="about-figure-placeholder">
          <span>{alt || "Figure"}</span>
        </div>
      )}
    </figure>
  );
}

function renderBlock(block, index) {
  if (block.type === "heading") {
    const Tag = block.depth === 1 ? "h2" : block.depth === 2 ? "h3" : "h4";
    return (
      <Tag id={block.id} key={index}>
        {renderInline(block.text)}
      </Tag>
    );
  }

  if (block.type === "figure") {
    return <AboutFigure key={index} source={block.source} alt={block.alt} />;
  }

  if (block.type === "caption") {
    return (
      <p className="about-caption" key={index}>
        {renderInline(block.text)}
      </p>
    );
  }

  return <p key={index}>{renderInline(block.text)}</p>;
}

export function AboutPage({ onClose }) {
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  function handleTocClick(event, id) {
    event.preventDefault();
    document.getElementById(id)?.scrollIntoView({ block: "start" });
  }

  return (
    <div className="about-page-shell" role="dialog" aria-modal="true" aria-labelledby="about-page-title">
      <section className="about-page">
        <header>
          <div>
            <span>Help</span>
            <h1 id="about-page-title">About Discourse2Draft</h1>
          </div>
          <IconButton label="Close About Page" onClick={onClose}>
            <X size={18} />
          </IconButton>
        </header>

        <div className="about-layout">
          <aside className="about-toc" aria-label="Table of contents">
            <span>Contents</span>
            <nav>
              {tableOfContents.map((item) => (
                <a className={`about-toc-depth-${item.depth}`} href={`#${item.id}`} key={item.id} onClick={(event) => handleTocClick(event, item.id)}>
                  {item.text}
                </a>
              ))}
            </nav>
          </aside>

          <div className="about-content">{aboutBlocks.map(renderBlock)}</div>
        </div>
      </section>
    </div>
  );
}
