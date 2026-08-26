from pathlib import Path
import sys

import pytest
from fastapi.responses import RedirectResponse, Response
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import app as api_module  # noqa: E402


def _model(fields):
    return {"kind": "model", "fields": fields}


def _request(path):
    return {"kind": "request", "path": path}


def _uploads(file_names):
    return {"kind": "uploads", "file_names": file_names}


def _assert_arg_matches(actual, expected):
    if isinstance(expected, dict) and expected.get("kind") == "model":
        for field_name, field_value in expected["fields"].items():
            assert getattr(actual, field_name) == field_value
        return

    if isinstance(expected, dict) and expected.get("kind") == "request":
        assert actual.url.path == expected["path"]
        return

    if isinstance(expected, dict) and expected.get("kind") == "uploads":
        assert [upload.filename for upload in actual] == expected["file_names"]
        return

    assert actual == expected


@pytest.fixture
def client():
    return TestClient(api_module.app)


def _patch_handler(monkeypatch, handler_name, response_kind="json"):
    calls = []

    async def handler(*args):
        calls.append(args)
        if response_kind == "redirect":
            return RedirectResponse("/sso-complete")
        if response_kind == "response":
            return Response("downloaded content", media_type="text/plain")
        return {"handler": handler_name}

    monkeypatch.setattr(api_module.app_utils, handler_name, handler)
    return calls


ENDPOINT_CASES = [
    {
        "name": "health",
        "method": "GET",
        "path": "/api/health",
        "handler": "_handle_health",
        "expected_args": [],
    },
    {
        "name": "app_config",
        "method": "GET",
        "path": "/api/app-config",
        "handler": "_handle_app_config",
        "expected_args": [],
    },
    {
        "name": "outline_templates",
        "method": "GET",
        "path": "/api/outline-templates",
        "handler": "_handle_outline_templates",
        "expected_args": [],
    },
    {
        "name": "outline_template",
        "method": "GET",
        "path": "/api/outline-templates/review_article",
        "handler": "_handle_outline_template",
        "expected_args": ["review_article"],
    },
    {
        "name": "uploaded_outline_templates",
        "method": "GET",
        "path": "/api/uploaded-outline-templates",
        "query": {"credentials_id": "12"},
        "handler": "_handle_uploaded_outline_templates",
        "expected_args": [12],
    },
    {
        "name": "upload_outline_templates",
        "method": "POST",
        "path": "/api/uploaded-outline-templates",
        "data": {"credentials_id": "12"},
        "files": [
            ("files", ("review.md", b"# Review", "text/markdown")),
            ("files", ("technical.md", b"# Technical", "text/markdown")),
        ],
        "handler": "_handle_upload_outline_templates",
        "expected_args": [_uploads(["review.md", "technical.md"]), 12],
    },
    {
        "name": "uploaded_outline_template",
        "method": "GET",
        "path": "/api/uploaded-outline-templates/review",
        "query": {"credentials_id": "12"},
        "handler": "_handle_uploaded_outline_template",
        "expected_args": ["review", 12],
    },
    {
        "name": "workspace",
        "method": "GET",
        "path": "/api/workspace",
        "handler": "_handle_workspace_data",
        "expected_args": [],
    },
    {
        "name": "login",
        "method": "POST",
        "path": "/api/auth/login",
        "json": {"email": "user@example.com", "password": "secret"},
        "handler": "_handle_login",
        "expected_args": [_model({"email": "user@example.com", "password": "secret"})],
    },
    {
        "name": "azure_login",
        "method": "GET",
        "path": "/api/auth/azure/login",
        "handler": "_handle_azure_login",
        "response_kind": "redirect",
        "expected_args": [_request("/api/auth/azure/login")],
    },
    {
        "name": "azure_status",
        "method": "GET",
        "path": "/api/auth/azure/status",
        "handler": "_handle_azure_status",
        "expected_args": [],
    },
    {
        "name": "azure_callback",
        "method": "GET",
        "path": "/api/auth/azure/callback",
        "query": {"code": "code-1", "state": "state-1", "error": "none"},
        "handler": "_handle_azure_auth_callback",
        "response_kind": "redirect",
        "expected_args": [_request("/api/auth/azure/callback"), "code-1", "state-1", "none"],
    },
    {
        "name": "azure_session",
        "method": "POST",
        "path": "/api/auth/azure/session",
        "json": {"code": "code-1", "state": "state-1"},
        "handler": "_handle_azure_session",
        "expected_args": [_request("/api/auth/azure/session"), _model({"code": "code-1", "state": "state-1"})],
    },
    {
        "name": "create_account",
        "method": "POST",
        "path": "/api/auth/create-account",
        "json": {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "password": "Password1!",
            "confirm_password": "Password1!",
        },
        "handler": "_handle_create_account",
        "expected_args": [
            _model(
                {
                    "first_name": "Ada",
                    "last_name": "Lovelace",
                    "email": "ada@example.com",
                    "password": "Password1!",
                    "confirm_password": "Password1!",
                }
            )
        ],
    },
    {
        "name": "forgot_password",
        "method": "POST",
        "path": "/api/auth/forgot-password",
        "json": {"email": "ada@example.com"},
        "handler": "_handle_forgot_password",
        "expected_args": [_model({"email": "ada@example.com"})],
    },
    {
        "name": "verify_reset_code",
        "method": "POST",
        "path": "/api/auth/verify-reset-code",
        "json": {"email": "ada@example.com", "code": "123456"},
        "handler": "_handle_verify_reset_code",
        "expected_args": [_model({"email": "ada@example.com", "code": "123456"})],
    },
    {
        "name": "reset_password",
        "method": "POST",
        "path": "/api/auth/reset-password",
        "json": {
            "email": "ada@example.com",
            "code": "123456",
            "password": "Password1!",
            "confirm_password": "Password1!",
        },
        "handler": "_handle_reset_password",
        "expected_args": [
            _model(
                {
                    "email": "ada@example.com",
                    "code": "123456",
                    "password": "Password1!",
                    "confirm_password": "Password1!",
                }
            )
        ],
    },
    {
        "name": "change_password",
        "method": "POST",
        "path": "/api/auth/change-password",
        "json": {
            "email": "ada@example.com",
            "current_password": "OldPassword1!",
            "password": "Password1!",
            "confirm_password": "Password1!",
        },
        "handler": "_handle_change_password",
        "expected_args": [
            _model(
                {
                    "email": "ada@example.com",
                    "current_password": "OldPassword1!",
                    "password": "Password1!",
                    "confirm_password": "Password1!",
                }
            )
        ],
    },
    {
        "name": "default_settings",
        "method": "GET",
        "path": "/api/settings/default",
        "query": {"session": "session-1"},
        "handler": "_handle_default_settings",
        "expected_args": ["session-1"],
    },
    {
        "name": "get_settings",
        "method": "GET",
        "path": "/api/settings/3",
        "query": {"email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_get_settings",
        "expected_args": [3, "ada@example.com", "session-1"],
    },
    {
        "name": "update_settings",
        "method": "PATCH",
        "path": "/api/settings/3",
        "query": {"email": "ada@example.com", "session": "session-1"},
        "json": {"llm": "test-model", "temperature": 0.3, "instructions": "Be concise."},
        "handler": "_handle_update_settings",
        "expected_args": [
            3,
            _model({"llm": "test-model", "temperature": 0.3, "instructions": "Be concise."}),
            "ada@example.com",
            "session-1",
        ],
    },
    {
        "name": "generated_files",
        "method": "GET",
        "path": "/api/generated-files",
        "query": {"email": "ada@example.com", "session": "session-1", "limit": "25"},
        "handler": "_handle_generated_files",
        "expected_args": ["ada@example.com", "session-1", 25],
    },
    {
        "name": "create_generated_file",
        "method": "POST",
        "path": "/api/generated-files",
        "json": {
            "email": "ada@example.com",
            "session": "session-1",
            "settings_id": 3,
            "file_name": "Draft",
            "ai_architecture": "rag",
        },
        "handler": "_handle_create_generated_file",
        "expected_args": [
            _model(
                {
                    "email": "ada@example.com",
                    "session": "session-1",
                    "settings_id": 3,
                    "file_name": "Draft",
                    "ai_architecture": "rag",
                }
            )
        ],
    },
    {
        "name": "update_generated_file",
        "method": "PATCH",
        "path": "/api/generated-files/7",
        "json": {"file_name": "Updated draft"},
        "handler": "_handle_update_generated_file",
        "expected_args": [7, _model({"file_name": "Updated draft"})],
    },
    {
        "name": "delete_generated_file",
        "method": "DELETE",
        "path": "/api/generated-files/7",
        "query": {"email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_delete_generated_file",
        "expected_args": [7, "ada@example.com", "session-1"],
    },
    {
        "name": "generated_file_manuscript",
        "method": "GET",
        "path": "/api/generated-files/7/manuscript",
        "query": {"email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_generated_file_manuscript",
        "expected_args": [7, "ada@example.com", "session-1"],
    },
    {
        "name": "paragraph_action_instructions",
        "method": "GET",
        "path": "/api/paragraph-actions/instructions",
        "handler": "_handle_paragraph_action_instructions",
        "expected_args": [],
    },
    {
        "name": "update_generated_file_paragraph",
        "method": "PATCH",
        "path": "/api/generated-files/7/paragraph",
        "json": {
            "section_path": ["Title", "Introduction"],
            "section_heading": "Introduction",
            "paragraph_index": 1,
            "raw_paragraph": "Existing paragraph.",
            "action": "Expand",
            "action_instruction": "Add clinical detail.",
            "model_name": "test-model",
            "temperature": 0.1,
            "instructions": "Add detail.",
            "email": "ada@example.com",
            "session": "session-1",
        },
        "handler": "_handle_update_generated_file_paragraph",
        "expected_args": [
            7,
            _model(
                {
                    "section_path": ["Title", "Introduction"],
                    "section_heading": "Introduction",
                    "paragraph_index": 1,
                    "raw_paragraph": "Existing paragraph.",
                    "action": "Expand",
                    "action_instruction": "Add clinical detail.",
                    "model_name": "test-model",
                    "temperature": 0.1,
                    "instructions": "Add detail.",
                    "email": "ada@example.com",
                    "session": "session-1",
                }
            ),
        ],
    },
    {
        "name": "update_generated_file_section_content",
        "method": "PATCH",
        "path": "/api/generated-files/7/section-content",
        "json": {
            "section_path": ["Title", "Introduction"],
            "section_heading": "Introduction",
            "section_content": "Edited paragraph [1].",
            "attached_reference_list_from_content": ["Reference one."],
            "email": "ada@example.com",
            "session": "session-1",
        },
        "handler": "_handle_update_generated_file_section_content",
        "expected_args": [
            7,
            _model(
                {
                    "section_path": ["Title", "Introduction"],
                    "section_heading": "Introduction",
                    "section_content": "Edited paragraph [1].",
                    "attached_reference_list_from_content": ["Reference one."],
                    "email": "ada@example.com",
                    "session": "session-1",
                }
            ),
        ],
    },
    {
        "name": "download_generated_file",
        "method": "GET",
        "path": "/api/generated-files/7/download",
        "query": {"format": "latex", "email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_download_generated_file",
        "response_kind": "response",
        "expected_args": [7, "latex", "ada@example.com", "session-1"],
    },
    {
        "name": "enable_literature_search",
        "method": "POST",
        "path": "/api/generated-files/7/literature-search",
        "json": {"email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_enable_generated_file_literature_search",
        "expected_args": [7, _model({"email": "ada@example.com", "session": "session-1"})],
    },
    {
        "name": "disable_literature_search",
        "method": "DELETE",
        "path": "/api/generated-files/7/literature-search",
        "query": {"email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_disable_generated_file_literature_search",
        "expected_args": [7, "ada@example.com", "session-1"],
    },
    {
        "name": "attach_uploaded_files",
        "method": "POST",
        "path": "/api/generated-files/7/uploaded-files/attach",
        "json": {
            "uploaded_file_ids": [1, 2],
            "email": "ada@example.com",
            "session": "session-1",
            "mode": "append",
        },
        "handler": "_handle_attach_uploaded_files_to_generated_file",
        "expected_args": [
            7,
            _model(
                {
                    "uploaded_file_ids": [1, 2],
                    "email": "ada@example.com",
                    "session": "session-1",
                    "mode": "append",
                }
            ),
        ],
    },
    {
        "name": "remove_uploaded_file_attachment",
        "method": "DELETE",
        "path": "/api/generated-files/7/uploaded-files/2/attach",
        "query": {"email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_remove_uploaded_file_attachment",
        "expected_args": [7, 2, "ada@example.com", "session-1"],
    },
    {
        "name": "generated_file_concept_map",
        "method": "GET",
        "path": "/api/generated-files/7/concept-map",
        "query": {"email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_generated_file_concept_map",
        "expected_args": [7, "ada@example.com", "session-1"],
    },
    {
        "name": "generate_generated_file",
        "method": "POST",
        "path": "/api/generated-files/7/generate",
        "json": {
            "outline": "# Title",
            "email": "ada@example.com",
            "session": "session-1",
            "mode": "remaining",
            "model_name": "test-model",
            "temperature": 0.2,
            "instructions": "Write clearly.",
            "architecture_type": "base",
            "collection_name": "",
            "collection_name_lit_search": "",
            "attached_references_db": {"1": "Reference"},
        },
        "handler": "_handle_generate_generated_file",
        "expected_args": [
            7,
            _model(
                {
                    "outline": "# Title",
                    "email": "ada@example.com",
                    "session": "session-1",
                    "mode": "remaining",
                    "model_name": "test-model",
                    "temperature": 0.2,
                    "instructions": "Write clearly.",
                    "architecture_type": "base",
                    "collection_name": "",
                    "collection_name_lit_search": "",
                    "attached_references_db": {"1": "Reference"},
                }
            ),
        ],
    },
    {
        "name": "generation_job",
        "method": "GET",
        "path": "/api/generation-jobs/job-1",
        "handler": "_handle_generation_job",
        "expected_args": ["job-1"],
    },
    {
        "name": "pause_generation_job",
        "method": "POST",
        "path": "/api/generation-jobs/job-1/pause",
        "handler": "_handle_pause_generation_job",
        "expected_args": ["job-1"],
    },
    {
        "name": "uploaded_files",
        "method": "GET",
        "path": "/api/uploaded-files",
        "query": {"email": "ada@example.com", "session": "session-1", "limit": "40"},
        "handler": "_handle_uploaded_files",
        "expected_args": ["ada@example.com", "session-1", 40],
    },
    {
        "name": "upload_uploaded_files",
        "method": "POST",
        "path": "/api/uploaded-files",
        "data": {"email": "ada@example.com", "session": "session-1", "replace": "true"},
        "files": [
            ("files", ("source.pdf", b"%PDF", "application/pdf")),
            ("files", ("notes.txt", b"notes", "text/plain")),
        ],
        "handler": "_handle_upload_uploaded_files",
        "expected_args": [_uploads(["source.pdf", "notes.txt"]), "ada@example.com", "session-1", True],
    },
    {
        "name": "delete_uploaded_file",
        "method": "DELETE",
        "path": "/api/uploaded-files/2",
        "query": {"email": "ada@example.com", "session": "session-1"},
        "handler": "_handle_delete_uploaded_file",
        "expected_args": [2, "ada@example.com", "session-1"],
    },
    {
        "name": "create_outline",
        "method": "POST",
        "path": "/api/ai/outline",
        "json": {"query": "Write about quantum computing."},
        "handler": "_handle_create_outline",
        "expected_args": [_request("/api/ai/outline")],
    },
    {
        "name": "format_outline",
        "method": "POST",
        "path": "/api/ai/outline/format",
        "json": {"outline_unstructured": "Title\nIntroduction", "query": "Topic", "model_name": "test-model"},
        "handler": "_handle_format_outline",
        "expected_args": [
            _model({"outline_unstructured": "Title\nIntroduction", "query": "Topic", "model_name": "test-model"})
        ],
    },
]


@pytest.mark.parametrize("case", ENDPOINT_CASES, ids=[case["name"] for case in ENDPOINT_CASES])
def test_app_endpoint_delegates_to_handler(client, monkeypatch, case):
    calls = _patch_handler(monkeypatch, case["handler"], case.get("response_kind", "json"))

    response = client.request(
        case["method"],
        case["path"],
        params=case.get("query"),
        json=case.get("json"),
        data=case.get("data"),
        files=case.get("files"),
        follow_redirects=False,
    )

    assert response.status_code in {200, 307}
    assert len(calls) == 1
    assert len(calls[0]) == len(case["expected_args"])
    for actual, expected in zip(calls[0], case["expected_args"]):
        _assert_arg_matches(actual, expected)

    if case.get("response_kind") == "redirect":
        assert response.headers["location"] == "/sso-complete"
    elif case.get("response_kind") == "response":
        assert response.text == "downloaded content"
    else:
        assert response.json() == {"handler": case["handler"]}


def test_login_requires_password_before_handler_is_called(client, monkeypatch):
    calls = _patch_handler(monkeypatch, "_handle_login")

    response = client.post("/api/auth/login", json={"email": "user@example.com"})

    assert response.status_code == 422
    assert calls == []


def test_generated_files_limit_is_validated_before_handler_is_called(client, monkeypatch):
    calls = _patch_handler(monkeypatch, "_handle_generated_files")

    response = client.get("/api/generated-files", params={"session": "session-1", "limit": 1001})

    assert response.status_code == 422
    assert calls == []
