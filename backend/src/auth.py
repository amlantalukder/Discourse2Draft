from __future__ import annotations

import asyncio
from datetime import datetime
import logging
import re
import secrets
import threading
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from .utils import Config


logger = logging.getLogger(f"{Config.APP_NAME_AS_PREFIX}.auth")

PASSWORD_RESET_CODE_TTL_SECONDS = 15 * 60
PASSWORD_RESET_CODE_MAX_ATTEMPTS = 5
_password_reset_codes: dict[str, dict[str, Any]] = {}
_password_reset_lock = threading.Lock()


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateAccountRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class VerifyResetCodeRequest(BaseModel):
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    password: str
    confirm_password: str


class ChangePasswordRequest(BaseModel):
    email: str
    current_password: str
    password: str
    confirm_password: str


class AzureSessionRequest(BaseModel):
    code: str
    state: str


def _records_from_dataframe(df: Any) -> list[dict[str, Any]]:
    df = df.drop(columns=["_sa_instance_state"], errors="ignore")
    return df.to_dict(orient="records")


def _required_default_model() -> str:
    model_name = Config.env_config.get("DEFAULT_AI_MODEL")
    if not model_name:
        raise HTTPException(
            status_code=503,
            detail="DEFAULT_AI_MODEL is not configured. Add DEFAULT_AI_MODEL to backend/.env and restart the backend.",
        )
    return model_name


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_email(email: str) -> str:
    normalized = normalize_email(email)
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", normalized):
        raise HTTPException(status_code=400, detail="A valid email is required.")
    return normalized


def validate_password(password: str, confirm_password: str | None = None) -> None:
    special_chars = set('!_@#$%^&*(),.?"{}[]|<>')
    if confirm_password is not None and password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must contain at least 8 characters.")
    if not any(char.isalpha() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one letter.")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number.")
    if not any(char in special_chars for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")


def _normalize_reset_code(code: str) -> str:
    normalized = code.strip()
    if not re.fullmatch(r"\d{6}", normalized):
        raise HTTPException(status_code=400, detail="Enter the 6-digit activation code.")
    return normalized


def _store_password_reset_code(email: str, code: str) -> None:
    expires_at = datetime.now().timestamp() + PASSWORD_RESET_CODE_TTL_SECONDS
    with _password_reset_lock:
        _password_reset_codes[email] = {
            "code": code,
            "expires_at": expires_at,
            "attempts": 0,
        }


def _validate_password_reset_code(email: str, code: str, consume: bool = False) -> None:
    normalized_code = _normalize_reset_code(code)
    with _password_reset_lock:
        record = _password_reset_codes.get(email)
        if record is None:
            raise HTTPException(status_code=400, detail="Request a new activation code before continuing.")
        if datetime.now().timestamp() > float(record.get("expires_at", 0)):
            _password_reset_codes.pop(email, None)
            raise HTTPException(status_code=400, detail="That activation code has expired. Request a new code.")
        if int(record.get("attempts", 0)) >= PASSWORD_RESET_CODE_MAX_ATTEMPTS:
            _password_reset_codes.pop(email, None)
            raise HTTPException(status_code=400, detail="Too many incorrect attempts. Request a new activation code.")
        if not secrets.compare_digest(str(record.get("code", "")), normalized_code):
            record["attempts"] = int(record.get("attempts", 0)) + 1
            raise HTTPException(status_code=400, detail="That activation code is not valid.")
        if consume:
            _password_reset_codes.pop(email, None)


def credential_by_email(email: str) -> dict[str, Any] | None:
    from . import db

    df = db.selectFromDB(table_name="credentials", field_names=["email"], field_values=[[email]], limit=1)
    records = _records_from_dataframe(df)
    return records[0] if records else None


def credential_by_id(credentials_id: int) -> dict[str, Any] | None:
    from . import db

    df = db.selectFromDB(table_name="credentials", field_names=["id"], field_values=[[credentials_id]], limit=1)
    records = _records_from_dataframe(df)
    return records[0] if records else None


def public_user(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "email": record.get("email"),
        "first_name": record.get("first_name"),
        "last_name": record.get("last_name"),
    }


def credential_for_azure_user(user: dict[str, str]) -> dict[str, Any]:
    from . import db

    email = validate_email(user["email"])
    existing = credential_by_email(email)
    if existing is not None:
        return existing

    now = datetime.now()
    inserted_ids = db.insertIntoDB(
        table_name="credentials",
        field_names=["email", "first_name", "last_name", "password", "create_date", "update_date"],
        field_values=[
            [email],
            [user.get("first_name") or "Azure"],
            [user.get("last_name") or "User"],
            [db.encryptPassword(uuid4().hex)],
            [now],
            [now],
        ],
    )
    return {
        "id": int(inserted_ids[0]) if inserted_ids else None,
        "email": email,
        "first_name": user.get("first_name") or "Azure",
        "last_name": user.get("last_name") or "User",
        "create_date": now,
        "update_date": now,
    }


def create_default_settings(email: str, session_id: str | None = None) -> dict[str, Any]:
    from . import db

    now = datetime.now()
    session_id = session_id or uuid4().hex
    llm = _required_default_model()
    temperature = 0.0
    instructions = ""

    inserted_ids = db.insertIntoDB(
        table_name="settings",
        field_names=["email", "session", "llm", "temperature", "instructions", "create_date", "update_date"],
        field_values=[
            [email],
            [session_id],
            [llm],
            [temperature],
            [instructions],
            [now],
            [now],
        ],
    )
    return {
        "id": inserted_ids[0] if inserted_ids else None,
        "email": email,
        "session": session_id,
        "llm": llm,
        "temperature": temperature,
        "instructions": instructions,
    }


def auth_payload(credential: dict[str, Any]) -> dict[str, Any]:
    settings = create_default_settings(str(credential["email"]))
    return {
        "user": public_user(credential),
        "session": settings["session"],
        "settings": settings,
    }


def create_guest_auth_payload(session: str | None = None) -> dict[str, Any]:
    from . import db

    now = datetime.now()
    guest_token = uuid4().hex
    guest_email = f"guest_{guest_token}@guest.{Config.APP_NAME_AS_PREFIX}.local"
    inserted_ids = db.insertIntoDB(
        table_name="credentials",
        field_names=["email", "first_name", "last_name", "password", "create_date", "update_date"],
        field_values=[
            [guest_email],
            ["Guest"],
            ["User"],
            [db.encryptPassword(uuid4().hex)],
            [now],
            [now],
        ],
    )
    credential = {
        "id": int(inserted_ids[0]) if inserted_ids else None,
        "email": guest_email,
        "first_name": "Guest",
        "last_name": "User",
        "create_date": now,
        "update_date": now,
    }
    settings = create_default_settings(guest_email, session_id=session)
    return {
        "status": "anonymous",
        "user": {
            "id": credential["id"],
            "email": None,
            "first_name": "Guest",
            "last_name": "User",
        },
        "session": settings["session"],
        "settings": settings,
    }


def authenticate_user(email: str, password: str) -> dict[str, Any]:
    from . import db

    email = validate_email(email)
    credential = credential_by_email(email)
    if credential is None or credential.get("password") != db.encryptPassword(password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {"status": "authenticated", **auth_payload(credential)}


def azure_login(request: Request) -> RedirectResponse:
    from .azure_auth import azure_login_redirect

    return azure_login_redirect(request)


def azure_status() -> dict[str, Any]:
    from .azure_auth import azure_auth_status

    return azure_auth_status()


def azure_callback(
    request: Request,
    code: str | None,
    state: str | None,
    error: str | None = None,
) -> RedirectResponse:
    from .azure_auth import azure_callback_redirect

    return azure_callback_redirect(request, code=code, state=state, error=error)


def authenticate_azure_session(request: Request, code: str, state: str) -> dict[str, Any]:
    from .azure_auth import exchange_code_for_claims_from_state, user_from_claims

    logger.info("Completing Azure login session exchange")
    claims = exchange_code_for_claims_from_state(request, code, state)
    credential = credential_for_azure_user(user_from_claims(claims))
    logger.info("Azure login session completed for %s", credential.get("email"))
    return {"status": "authenticated", "auth_provider": "azure", **auth_payload(credential)}


def create_account(request: CreateAccountRequest) -> dict[str, Any]:
    from . import db

    email = validate_email(request.email)
    first_name = request.first_name.strip()
    last_name = request.last_name.strip()
    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="First name and last name are required.")
    validate_password(request.password, request.confirm_password)

    if credential_by_email(email) is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    now = datetime.now()
    inserted_ids = db.insertIntoDB(
        table_name="credentials",
        field_names=["email", "first_name", "last_name", "password", "create_date", "update_date"],
        field_values=[
            [email],
            [first_name],
            [last_name],
            [db.encryptPassword(request.password)],
            [now],
            [now],
        ],
    )
    user = {
        "id": inserted_ids[0] if inserted_ids else None,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
    }
    return {"status": "created", **auth_payload(user)}


async def send_password_reset_code(email: str) -> dict[str, Any]:
    email = validate_email(email)
    credential = credential_by_email(email)
    if credential is None:
        raise HTTPException(status_code=404, detail="No account was found for that email.")

    code = f"{secrets.randbelow(1_000_000):06d}"
    mailgun_domain = Config.env_config.get("MAILGUN_DOMAIN")
    mailgun_api_key = Config.env_config.get("MAILGUN_API_KEY")
    if not mailgun_domain or not mailgun_api_key:
        raise HTTPException(
            status_code=503,
            detail="Email delivery is not configured. Add Mailgun settings and restart the backend.",
        )

    def send_activation_code():
        import requests

        return requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": f"{Config.APP_NAME} <postmaster@{mailgun_domain}>",
                "to": email,
                "subject": f"Activation code for {Config.APP_NAME}",
                "text": f"Activation code: {code}",
            },
            timeout=15,
        )

    response = await asyncio.to_thread(send_activation_code)
    if not response.ok:
        logger.error(
            "Mailgun forgot password email failed with status %s: %s",
            response.status_code,
            response.text[:300],
        )
        raise HTTPException(
            status_code=502,
            detail="Unable to send the activation code right now. Please try again later.",
        )

    _store_password_reset_code(email, code)

    return {
        "status": "code_sent",
        "email": email,
        "message": "An activation code was sent to your email.",
    }


def verify_reset_code(email: str, code: str) -> dict[str, Any]:
    email = validate_email(email)
    if credential_by_email(email) is None:
        raise HTTPException(status_code=404, detail="No account was found for that email.")

    _validate_password_reset_code(email, code)
    return {
        "status": "verified",
        "email": email,
        "message": "Code verified. You can now change your password.",
    }


def reset_password(request: ResetPasswordRequest) -> dict[str, Any]:
    from . import db

    email = validate_email(request.email)
    if credential_by_email(email) is None:
        raise HTTPException(status_code=404, detail="No account was found for that email.")
    validate_password(request.password, request.confirm_password)
    _validate_password_reset_code(email, request.code, consume=True)

    db.updateDB(
        table_name="credentials",
        update_fields=["password", "update_date"],
        update_values=[db.encryptPassword(request.password), datetime.now()],
        select_fields=["email"],
        select_values=[[email]],
    )
    return {
        "status": "password_updated",
        "email": email,
        "message": "Password updated. You can now log in with your new password.",
    }


def change_password(request: ChangePasswordRequest) -> dict[str, Any]:
    from . import db

    email = validate_email(request.email)
    credential = credential_by_email(email)
    if credential is None:
        raise HTTPException(status_code=404, detail="No account was found for that email.")

    current_password_hash = db.encryptPassword(request.current_password)
    if not secrets.compare_digest(str(credential.get("password") or ""), current_password_hash):
        raise HTTPException(status_code=401, detail="Current password is not correct.")

    validate_password(request.password, request.confirm_password)
    new_password_hash = db.encryptPassword(request.password)
    if secrets.compare_digest(current_password_hash, new_password_hash):
        raise HTTPException(status_code=400, detail="New password must be different from the current password.")

    db.updateDB(
        table_name="credentials",
        update_fields=["password", "update_date"],
        update_values=[new_password_hash, datetime.now()],
        select_fields=["email"],
        select_values=[[email]],
    )
    return {
        "status": "password_changed",
        "email": email,
        "message": "Password changed successfully.",
    }
