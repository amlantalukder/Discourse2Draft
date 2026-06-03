import { useState } from "react";
import { getJSON, postJSON } from "../api/client";
import { AboutPage } from "./AboutPage";
import { TopBar } from "./TopBar";

const PASSWORD_RULE = 'Password must contain at least 8 characters, with at least one letter, one number, and one special character (!_@#$%^&*(),.?"{}[]|<>).';

export function LoginPage({ onContinue }) {
  const [authView, setAuthView] = useState("login");
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [createForm, setCreateForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [forgotForm, setForgotForm] = useState({ email: "" });
  const [authMessage, setAuthMessage] = useState("");
  const [authError, setAuthError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  function switchAuthView(nextView) {
    setAuthView(nextView);
    setAuthMessage("");
    setAuthError("");
  }

  function updateForm(setForm, field) {
    return (event) => {
      setForm((current) => ({ ...current, [field]: event.target.value }));
    };
  }

  async function handleLogin(event) {
    event.preventDefault();
    setAuthMessage("");
    setAuthError("");
    setIsSubmitting(true);

    try {
      const payload = await postJSON("/api/auth/login", loginForm);
      onContinue(payload);
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCreateAccount(event) {
    event.preventDefault();
    setAuthMessage("");
    setAuthError("");

    if (createForm.password !== createForm.confirm_password) {
      setAuthError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = await postJSON("/api/auth/create-account", createForm);
      onContinue(payload);
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleForgotPassword(event) {
    event.preventDefault();
    setAuthMessage("");
    setAuthError("");
    setIsSubmitting(true);

    try {
      const payload = await postJSON("/api/auth/forgot-password", forgotForm);
      setAuthMessage(payload.message ?? "Account found.");
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleContinueWithoutLogin() {
    setAuthMessage("");
    setAuthError("");
    setIsSubmitting(true);

    try {
      const payload = await getJSON("/api/settings/default");
      onContinue({
        status: "anonymous",
        session: payload.settings?.session,
        settings: payload.settings,
        llm_options: payload.llm_options ?? [],
      });
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function renderFeedback() {
    if (!authMessage && !authError) return null;

    return <p className={`auth-feedback ${authError ? "auth-feedback-error" : ""}`}>{authError || authMessage}</p>;
  }

  function renderLogin() {
    return (
      <form className="auth-card auth-card-login" onSubmit={handleLogin}>
        <h1>Login</h1>
        <div className="auth-divider" />
        {renderFeedback()}

        <label className="auth-field auth-field-short">
          <span>Email</span>
          <input type="email" autoComplete="email" required value={loginForm.email} onChange={updateForm(setLoginForm, "email")} />
        </label>

        <label className="auth-field">
          <span>Password</span>
          <input type="password" autoComplete="current-password" required value={loginForm.password} onChange={updateForm(setLoginForm, "password")} />
        </label>

        <div className="auth-actions auth-actions-login">
          <button className="tool-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Logging in" : "Login"}
          </button>
          <button className="tool-button" type="button" onClick={() => switchAuthView("create")}>
            Create Account
          </button>
          <button className="tool-button" type="button" onClick={() => switchAuthView("forgot")}>
            Forgot Password
          </button>
        </div>

        <button className="auth-link" type="button" onClick={handleContinueWithoutLogin} disabled={isSubmitting}>
          {isSubmitting ? "Loading Settings" : "Continue Without Login"}
        </button>
      </form>
    );
  }

  function renderCreateAccount() {
    return (
      <form className="auth-card auth-card-create" onSubmit={handleCreateAccount}>
        <h1>Create account</h1>
        <div className="auth-divider" />
        {renderFeedback()}

        <div className="auth-grid">
          <label className="auth-field">
            <span>First name</span>
            <input type="text" autoComplete="given-name" required value={createForm.first_name} onChange={updateForm(setCreateForm, "first_name")} />
          </label>

          <label className="auth-field">
            <span>Last name</span>
            <input type="text" autoComplete="family-name" required value={createForm.last_name} onChange={updateForm(setCreateForm, "last_name")} />
          </label>
        </div>

        <label className="auth-field auth-field-short">
          <span>Email</span>
          <input type="email" autoComplete="email" required value={createForm.email} onChange={updateForm(setCreateForm, "email")} />
        </label>

        <label className="auth-field">
          <span>Password</span>
          <input type="password" autoComplete="new-password" required value={createForm.password} onChange={updateForm(setCreateForm, "password")} />
        </label>

        <label className="auth-field">
          <span>Confirm password</span>
          <input type="password" autoComplete="new-password" required value={createForm.confirm_password} onChange={updateForm(setCreateForm, "confirm_password")} />
        </label>

        <p className="auth-note">{PASSWORD_RULE}</p>

        <div className="auth-actions auth-actions-split">
          <button className="tool-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating" : "Create account"}
          </button>
          <button className="tool-button" type="button" onClick={() => switchAuthView("login")}>
            Back to Login
          </button>
        </div>
      </form>
    );
  }

  function renderForgotPassword() {
    return (
      <form className="auth-card auth-card-forgot" onSubmit={handleForgotPassword}>
        <h1>Forgot Password</h1>
        <div className="auth-divider" />
        {renderFeedback()}

        <label className="auth-field auth-field-short">
          <span>Email</span>
          <input type="email" autoComplete="email" required value={forgotForm.email} onChange={updateForm(setForgotForm, "email")} />
        </label>

        <div className="auth-actions auth-actions-split">
          <button className="tool-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Sending" : "Send Code"}
          </button>
          <button className="tool-button" type="button" onClick={() => switchAuthView("login")}>
            Back to Login
          </button>
        </div>
      </form>
    );
  }

  return (
    <div className="app-window" data-view="login">
      <TopBar isLoginPage={true} onHelp={() => setIsAboutOpen(true)} />

      <main className="auth-main">
        {authView === "login" ? renderLogin() : null}
        {authView === "create" ? renderCreateAccount() : null}
        {authView === "forgot" ? renderForgotPassword() : null}
      </main>
      {isAboutOpen ? <AboutPage onClose={() => setIsAboutOpen(false)} /> : null}
    </div>
  );
}
