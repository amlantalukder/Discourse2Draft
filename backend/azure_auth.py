from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import hmac
import json
import logging
import secrets
from typing import Any
from urllib.parse import urlencode, urlparse

import requests
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from src.utils import Config


logger = logging.getLogger("discourse2draft.azure_auth")

STATE_TTL_SECONDS = 10 * 60
REQUIRED_AZURE_AUTH_ENV_KEYS = (
    "AZURE_AUTH_TENANT_ID",
    "AZURE_AUTH_APPLICATION_CLIENT_ID",
    "AZURE_AUTH_CLIENT_SECRET",
)


@dataclass(frozen=True)
class AzureAuthConfig:
    tenant_id: str
    client_id: str
    client_secret: str
    scopes: str = "openid profile email"

    @property
    def authority(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0"

    @property
    def authorize_url(self) -> str:
        return f"{self.authority}/authorize"

    @property
    def token_url(self) -> str:
        return f"{self.authority}/token"


def azure_auth_config() -> AzureAuthConfig:
    tenant_id = str(Config.env_config.get("AZURE_AUTH_TENANT_ID") or "").strip()
    client_id = str(
        Config.env_config.get("AZURE_AUTH_APPLICATION_CLIENT_ID")
        or ""
    ).strip()
    client_secret = str(Config.env_config.get("AZURE_AUTH_CLIENT_SECRET") or "").strip()
    scopes = str(Config.env_config.get("AZURE_AUTH_SCOPES") or "openid profile email").strip()

    if not tenant_id or not client_id or not client_secret:
        raise HTTPException(
            status_code=503,
            detail="Azure sign-in is not configured. Add AZURE_AUTH_TENANT_ID, AZURE_AUTH_APPLICATION_CLIENT_ID, and AZURE_AUTH_CLIENT_SECRET.",
        )

    return AzureAuthConfig(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )


def azure_auth_status() -> dict[str, Any]:
    missing_keys = [
        key
        for key in REQUIRED_AZURE_AUTH_ENV_KEYS
        if not str(Config.env_config.get(key) or "").strip()
    ]
    return {
        "enabled": not missing_keys,
        "missing": missing_keys,
    }


def _utc_now() -> datetime:
    return datetime.utcnow()


def _encode_json(value: dict[str, Any]) -> str:
    raw = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _decode_json(value: str) -> dict[str, Any]:
    padded = value + "=" * (-len(value) % 4)
    return json.loads(base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8"))


def _signed_state(payload: dict[str, Any], ttl_seconds: int) -> str:
    config = azure_auth_config()
    exp = int((_utc_now() + timedelta(seconds=ttl_seconds)).timestamp())
    body = _encode_json({**payload, "exp": exp})
    signature = hmac.new(config.client_secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    return f"{body}.{base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')}"


def _verify_signed_state(token: str | None) -> dict[str, Any]:
    config = azure_auth_config()
    try:
        body, signature = str(token or "").split(".", 1)
        expected_signature = hmac.new(
            config.client_secret.encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        padded_signature = signature + "=" * (-len(signature) % 4)
        actual_signature = base64.urlsafe_b64decode(padded_signature.encode("utf-8"))
        if not hmac.compare_digest(actual_signature, expected_signature):
            raise ValueError("state signature mismatch")
        payload = _decode_json(body)
        if int(payload.get("exp") or 0) < int(_utc_now().timestamp()):
            raise ValueError("state expired")
        return payload
    except Exception as exp:
        raise HTTPException(status_code=401, detail="Azure sign-in expired. Please try again.") from exp


def _frontend_return_url(request: Request) -> str:
    return_url = str(request.query_params.get("return_url") or "").strip()
    if _is_safe_return_url(return_url):
        return return_url

    referer = request.headers.get("referer")
    if referer:
        return referer
    return str(request.base_url)


def _is_safe_return_url(return_url: str) -> bool:
    if not return_url:
        return False
    parsed = urlparse(return_url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _redirect_uri(request: Request) -> str:
    configured_redirect_uri = str(Config.env_config.get("AZURE_AUTH_REDIRECT_URI") or "").strip()
    return configured_redirect_uri or str(request.url_for("azure_auth_callback"))


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    try:
        payload_part = token.split(".")[1]
        padded_payload = payload_part + "=" * (-len(payload_part) % 4)
        decoded = base64.urlsafe_b64decode(padded_payload.encode("utf-8"))
        return json.loads(decoded.decode("utf-8"))
    except Exception as exp:
        raise HTTPException(status_code=502, detail="Azure sign-in returned an invalid identity token.") from exp


def azure_login_redirect(request: Request) -> RedirectResponse:
    config = azure_auth_config()

    nonce = secrets.token_urlsafe(32)
    state = _signed_state(
        {
            "nonce": nonce,
            "return_url": _frontend_return_url(request),
        },
        STATE_TTL_SECONDS,
    )

    params = {
        "client_id": config.client_id,
        "response_type": "code",
        "redirect_uri": _redirect_uri(request),
        "response_mode": "query",
        "scope": config.scopes,
        "state": state,
        "nonce": nonce,
    }
    return RedirectResponse(f"{config.authorize_url}?{urlencode(params)}")


def azure_callback_redirect(request: Request, code: str | None, state: str | None, error: str | None = None) -> RedirectResponse:
    try:
        state_record = _verify_signed_state(state)
    except HTTPException:
        state_record = {}

    return_url = str(state_record.get("return_url") or request.base_url)

    if error:
        return RedirectResponse(_append_query(return_url, {"azure_auth_error": "Azure sign-in was cancelled or failed."}))

    if not code or not state_record:
        return RedirectResponse(_append_query(return_url, {"azure_auth_error": "Azure sign-in expired. Please try again."}))

    return RedirectResponse(
        _append_query(
            return_url,
            {
                "azure_auth_code": code,
                "azure_auth_state": state or "",
            },
        )
    )


def exchange_code_for_claims_from_state(request: Request, code: str, state: str) -> dict[str, Any]:
    state_record = _verify_signed_state(state)
    return exchange_code_for_claims(request, code, str(state_record.get("nonce") or ""))


def exchange_code_for_claims(request: Request, code: str, expected_nonce: str) -> dict[str, Any]:
    config = azure_auth_config()
    try:
        response = requests.post(
            config.token_url,
            data={
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": _redirect_uri(request),
                "scope": config.scopes,
            },
            timeout=20,
        )
    except requests.RequestException as exp:
        logger.exception("Azure token exchange request failed")
        raise HTTPException(status_code=502, detail="Azure sign-in could not reach Microsoft. Please try again.") from exp

    if not response.ok:
        logger.error(
            "Azure token exchange failed with status %s: %s",
            response.status_code,
            response.text[:500],
        )
        raise HTTPException(status_code=502, detail="Azure sign-in could not be completed. Please try again.")

    token_payload = response.json()
    if not token_payload.get("id_token"):
        logger.error("Azure token exchange response did not include an id_token: %s", token_payload)
        raise HTTPException(status_code=502, detail="Azure sign-in did not return identity information. Please try again.")

    claims = _decode_jwt_payload(str(token_payload.get("id_token") or ""))
    if claims.get("nonce") != expected_nonce:
        raise HTTPException(status_code=401, detail="Azure sign-in could not be verified. Please try again.")

    return claims


def user_from_claims(claims: dict[str, Any]) -> dict[str, str]:
    email = str(
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("upn")
        or ""
    ).strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Azure did not provide an email address for this account.")

    full_name = str(claims.get("name") or "").strip()
    first_name = str(claims.get("given_name") or "").strip()
    last_name = str(claims.get("family_name") or "").strip()
    if not first_name and full_name:
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) or "User"

    return {
        "email": email,
        "first_name": first_name or "Azure",
        "last_name": last_name or "User",
    }


def _append_query(url: str, params: dict[str, str]) -> str:
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{urlencode(params)}"
