import { HelpCircle, LogIn, LogOut, Pencil, User } from "lucide-react";
import { useState } from "react";
import { IconButton } from "./IconButton";

export function TopBar({ accountLabel = "Anonymous", isGuest = false, isLoginPage = false, onHelp, onLogout }) {
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false);
  const AccountActionIcon = isGuest ? LogIn : LogOut;
  const accountActionLabel = isGuest ? "Login" : "Logout";

  function handleAccountAction() {
    setIsAccountMenuOpen(false);
    onLogout?.();
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
                <button type="button" role="menuitem" onClick={handleAccountAction}>
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
      </nav>
    </header>
  );
}
