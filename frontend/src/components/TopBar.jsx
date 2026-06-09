import { Github, HelpCircle, KeyRound, LogIn, LogOut, Pencil, User } from "./FontAwesomeIcons";
import { useState } from "react";
import { IconButton } from "./IconButton";

const GITHUB_URL = "https://github.com/amlantalukder/Discourse2Draft";

export function TopBar({ accountLabel = "Anonymous", isGuest = false, isLoginPage = false, onChangePassword, onHelp, onLogout }) {
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false);
  const AccountActionIcon = isGuest ? LogIn : LogOut;
  const accountActionLabel = isGuest ? "Login" : "Logout";

  function handleAccountAction() {
    setIsAccountMenuOpen(false);
    onLogout?.();
  }

  function handleChangePassword() {
    setIsAccountMenuOpen(false);
    onChangePassword?.();
  }

  return (
    <header className="topbar">
      <div className="brand">
        <Pencil size={22} />
        <span>Discourse2Draft</span>
        <Pencil size={22} />
        <small>(Beta)</small>
      </div>
      <nav className="top-icons" aria-label="Application controls">
        {!isLoginPage ? (
          <div className="account-menu">
            <IconButton label="Account" aria-expanded={isAccountMenuOpen} aria-haspopup="menu" onClick={() => setIsAccountMenuOpen((isOpen) => !isOpen)}>
              <User size={18} />
            </IconButton>
            {isAccountMenuOpen ? (
              <div className="account-popover" role="menu">
                <span>{accountLabel}</span>
                {!isGuest ? (
                  <button className="account-menu-button" type="button" role="menuitem" onClick={handleChangePassword}>
                    <KeyRound size={15} />
                    <span>Change Password</span>
                  </button>
                ) : null}
                <button className="account-menu-button account-menu-danger" type="button" role="menuitem" onClick={handleAccountAction}>
                  <AccountActionIcon size={15} />
                  <span>{accountActionLabel}</span>
                </button>
              </div>
            ) : null}
          </div>
        ) : null}
        <IconButton label="Help" onClick={onHelp}>
          <HelpCircle size={18} />
        </IconButton>
        <IconButton label="GitHub" onClick={() => window.open(GITHUB_URL, "_blank", "noopener,noreferrer")}>
          <Github size={18} />
        </IconButton>
      </nav>
    </header>
  );
}
