import { useMemo } from "react";

export function Manuscript({ manuscript = [], generatedContent }) {
  const sections = useMemo(() => {
    if (!generatedContent) return manuscript;
    return [
      ...manuscript.slice(0, 2),
      {
        heading: "Generated Section",
        body: generatedContent,
      },
      ...manuscript.slice(2),
    ];
  }, [generatedContent]);

  return (
    <article className="manuscript" id="preview">
      {sections.map((section, index) => (
        <section key={`${section.heading}-${index}`} className={index === 1 ? "abstract-block" : ""}>
          <h1>{index === 0 ? section.heading : null}</h1>
          {index > 0 ? <h2>{section.heading}</h2> : null}
          {section.body ? <p>{section.body}</p> : null}
        </section>
      ))}
    </article>
  );
}
