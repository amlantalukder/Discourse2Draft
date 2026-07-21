export function IconButton({ label, children, className = "", showLabel = false, ...props }) {
  const classes = ["icon-button", showLabel ? "icon-button-with-label" : "", className].filter(Boolean).join(" ");

  return (
    <button className={classes} type="button" aria-label={label} title={label} {...props}>
      {children}
      {showLabel ? <span className="icon-button-text">{label}</span> : null}
    </button>
  );
}
