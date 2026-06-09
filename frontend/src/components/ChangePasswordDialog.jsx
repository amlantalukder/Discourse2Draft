import { Eye, EyeOff, KeyRound, X } from "./FontAwesomeIcons";
import { useState } from "react";
import { postJSON } from "../api/client";
import { IconButton } from "./IconButton";

const PASSWORD_RULE = 'Password must contain at least 8 characters, with at least one letter, one number, and one special character (!_@#$%^&*(),.?"{}[]|<>).';

const EMPTY_FORM = {
  current_password: "",
  password: "",
  confirm_password: "",
};

function PasswordField({ label, value, onChange, autoComplete }) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <label className="change-password-field">
      <span>{label}</span>
      <span className="password-input-wrap">
        <input type={isVisible ? "text" : "password"} autoComplete={autoComplete} required value={value} onChange={onChange} />
        <button
          aria-label={isVisible ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`}
          className="password-toggle"
          onClick={() => setIsVisible((current) => !current)}
          title={isVisible ? "Hide password" : "Show password"}
          type="button"
        >
          {isVisible ? <EyeOff size={16} /> : <Eye size={16} />}
        </button>
      </span>
    </label>
  );
}

export function ChangePasswordDialog({ email, onClose, onChanged }) {
  const [form, setForm] = useState({ ...EMPTY_FORM });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField(field) {
    return (event) => {
      setForm((current) => ({ ...current, [field]: event.target.value }));
    };
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    if (form.password !== form.confirm_password) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = await postJSON("/api/auth/change-password", {
        email,
        ...form,
      });
      setForm({ ...EMPTY_FORM });
      setMessage(payload.message ?? "Password changed successfully.");
      onChanged?.(payload);
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="change-password-shell" role="presentation" onClick={onClose}>
      <form className="change-password-dialog" role="dialog" aria-modal="true" aria-labelledby="change-password-title" onClick={(event) => event.stopPropagation()} onSubmit={handleSubmit}>
        <header>
          <div className="change-password-title">
            <span aria-hidden="true">
              <KeyRound size={18} />
            </span>
            <h2 id="change-password-title">Change Password</h2>
          </div>
          <IconButton label="Close change password" onClick={onClose}>
            <X size={17} />
          </IconButton>
        </header>

        <div className="change-password-body">
          <p className="change-password-account">{email}</p>
          {message ? <p className="change-password-feedback">{message}</p> : null}
          {error ? <p className="change-password-feedback change-password-feedback-error">{error}</p> : null}

          <PasswordField label="Current password" autoComplete="current-password" value={form.current_password} onChange={updateField("current_password")} />
          <PasswordField label="New password" autoComplete="new-password" value={form.password} onChange={updateField("password")} />
          <PasswordField label="Confirm new password" autoComplete="new-password" value={form.confirm_password} onChange={updateField("confirm_password")} />
          <p className="change-password-note">{PASSWORD_RULE}</p>
        </div>

        <footer>
          <button className="tool-button" type="button" onClick={onClose}>
            Cancel
          </button>
          <button className="tool-button primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Changing" : "Change Password"}
          </button>
        </footer>
      </form>
    </div>
  );
}
