import { HelpCircle } from "./FontAwesomeIcons";

const outlineRules = [
  "Start with one # top-level heading.",
  "Use ##, ###, etc. for nested sections.",
  "Place [--content--] where AI should write.",
  "Wrap section instructions with [--Instructions--] and [/--Instructions--].",
];

export function OutlineRulesTooltip({ id = "outline-rules-tooltip" }) {
  return (
    <span className="outline-rules-tooltip">
      <button type="button" className="outline-rules-trigger" aria-label="Structured outline rules" aria-describedby={id}>
        <HelpCircle size={13} />
      </button>
      <span className="outline-rules-popover" id={id} role="tooltip">
        <strong>Structured outline rules</strong>
        <ul>
          {outlineRules.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
      </span>
    </span>
  );
}
