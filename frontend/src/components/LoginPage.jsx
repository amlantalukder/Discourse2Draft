import { useState } from "react";
import { Eye, EyeOff } from "./FontAwesomeIcons";
import { getJSON, postJSON } from "../api/client";
import { AboutPage } from "./AboutPage";
import { TopBar } from "./TopBar";

const PASSWORD_RULE = 'Password must contain at least 8 characters, with at least one letter, one number, and one special character (!_@#$%^&*(),.?"{}[]|<>).';
const EMPTY_FORGOT_FORM = { email: "", code: "", password: "", confirm_password: "" };

function PasswordInput({ value, onChange, autoComplete, label }) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <label className="auth-field">
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
  const [forgotForm, setForgotForm] = useState({ ...EMPTY_FORGOT_FORM });
  const [forgotStep, setForgotStep] = useState("email");
  const [authMessage, setAuthMessage] = useState("");
  const [authError, setAuthError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  function switchAuthView(nextView) {
    setAuthView(nextView);
    setAuthMessage("");
    setAuthError("");
    if (nextView === "forgot") {
      setForgotForm({ ...EMPTY_FORGOT_FORM, email: loginForm.email });
      setForgotStep("email");
    }
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

  async function sendResetCode() {
    setAuthMessage("");
    setAuthError("");
    setIsSubmitting(true);

    try {
      const payload = await postJSON("/api/auth/forgot-password", { email: forgotForm.email });
      setForgotForm((current) => ({
        ...current,
        email: payload.email ?? current.email,
        code: "",
        password: "",
        confirm_password: "",
      }));
      setForgotStep("code");
      setAuthMessage(payload.message ?? "Account found.");
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleForgotPassword(event) {
    event.preventDefault();
    await sendResetCode();
  }

  async function handleResendResetCode() {
    await sendResetCode();
  }

  async function handleVerifyResetCode(event) {
    event.preventDefault();
    setAuthMessage("");
    setAuthError("");
    setIsSubmitting(true);

    try {
      const payload = await postJSON("/api/auth/verify-reset-code", {
        email: forgotForm.email,
        code: forgotForm.code,
      });
      setForgotStep("password");
      setAuthMessage(payload.message ?? "Code verified.");
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleResetPassword(event) {
    event.preventDefault();
    setAuthMessage("");
    setAuthError("");

    if (forgotForm.password !== forgotForm.confirm_password) {
      setAuthError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = await postJSON("/api/auth/reset-password", forgotForm);
      setLoginForm({ email: payload.email ?? forgotForm.email, password: "" });
      setForgotForm({ ...EMPTY_FORGOT_FORM });
      setForgotStep("email");
      setAuthView("login");
      setAuthMessage(payload.message ?? "Password updated. You can log in with your new password.");
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

        <PasswordInput label="Password" autoComplete="current-password" value={loginForm.password} onChange={updateForm(setLoginForm, "password")} />

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

        <PasswordInput label="Password" autoComplete="new-password" value={createForm.password} onChange={updateForm(setCreateForm, "password")} />

        <PasswordInput label="Confirm password" autoComplete="new-password" value={createForm.confirm_password} onChange={updateForm(setCreateForm, "confirm_password")} />

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
    const submitHandler = forgotStep === "email" ? handleForgotPassword : forgotStep === "code" ? handleVerifyResetCode : handleResetPassword;
    const submitLabel = forgotStep === "email" ? "Send Code" : forgotStep === "code" ? "Verify Code" : "Change Password";
    const submittingLabel = forgotStep === "email" ? "Sending" : forgotStep === "code" ? "Verifying" : "Changing";

    return (
      <form className="auth-card auth-card-forgot" onSubmit={submitHandler}>
        <h1>Forgot Password</h1>
        <div className="auth-divider" />
        {renderFeedback()}

        <label className="auth-field auth-field-short">
          <span>Email</span>
          <input
            type="email"
            autoComplete="email"
            disabled={forgotStep !== "email" || isSubmitting}
            required
            value={forgotForm.email}
            onChange={updateForm(setForgotForm, "email")}
          />
        </label>

        {forgotStep !== "email" ? (
          <label className="auth-field auth-code-field">
            <span>Activation code</span>
            <span className="auth-code-input-row">
              <input
                type="text"
                autoComplete="one-time-code"
                inputMode="numeric"
                maxLength={6}
                pattern="[0-9]{6}"
                disabled={forgotStep === "password" || isSubmitting}
                required
                value={forgotForm.code}
                onChange={updateForm(setForgotForm, "code")}
              />
              <button className="tool-button auth-resend-button" type="button" disabled={isSubmitting} onClick={handleResendResetCode}>
                {isSubmitting ? "Sending" : "Resend"}
              </button>
            </span>
          </label>
        ) : null}

        {forgotStep === "password" ? (
          <>
            <PasswordInput label="New password" autoComplete="new-password" value={forgotForm.password} onChange={updateForm(setForgotForm, "password")} />
            <PasswordInput
              label="Confirm new password"
              autoComplete="new-password"
              value={forgotForm.confirm_password}
              onChange={updateForm(setForgotForm, "confirm_password")}
            />
            <p className="auth-note">{PASSWORD_RULE}</p>
          </>
        ) : null}

        <div className="auth-actions auth-actions-split">
          <button className="tool-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? submittingLabel : submitLabel}
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
