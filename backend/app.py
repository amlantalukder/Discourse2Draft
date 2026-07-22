import importlib
import logging
from pathlib import Path
import sys
import types
from typing import Any

import app_utils
from fastapi import FastAPI, File, Form, Header, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from src.auth import (
    AzureSessionRequest,
    ChangePasswordRequest,
    CreateAccountRequest,
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    VerifyResetCodeRequest,
)
from src.utils import Config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(f"{Config.APP_NAME_AS_PREFIX}.api")


def _install_runtime_compatibility() -> None:
    module_aliases = {
        "langchain.output_parsers": "langchain_classic.output_parsers",
        "langchain.output_parsers.fix": "langchain_classic.output_parsers.fix",
        "langchain.chains": "langchain_classic.chains",
        "langchain.chains.combine_documents": "langchain_classic.chains.combine_documents",
        "langchain.chains.summarize": "langchain_classic.chains.summarize",
    }
    for alias, target in module_aliases.items():
        try:
            sys.modules.setdefault(alias, importlib.import_module(target))
        except Exception:
            logger.debug("Could not install module alias %s -> %s", alias, target, exc_info=True)

    if "shiny.express" not in sys.modules:
        shiny_module = types.ModuleType("shiny")
        shiny_express_module = types.ModuleType("shiny.express")
        shiny_express_module.ui = types.SimpleNamespace()
        shiny_module.express = shiny_express_module
        sys.modules.setdefault("shiny", shiny_module)
        sys.modules.setdefault("shiny.express", shiny_express_module)


_install_runtime_compatibility()

app = FastAPI(title=f"{Config.APP_NAME} API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------------------------------------------
# Health and bootstrap
# ---------------------------------------------------------------------------------------------------------------

@app.get("/api/health")
async def health() -> dict[str, Any]:
    return await app_utils._handle_health()


# ---------------------------------------------------------------------------------------------------------------
# Outline templates
# ---------------------------------------------------------------------------------------------------------------

@app.get("/api/outline-templates")
async def outline_templates() -> dict[str, Any]:
    return await app_utils._handle_outline_templates()


@app.get("/api/outline-templates/{template_name}")
async def outline_template(template_name: str) -> dict[str, Any]:
    return await app_utils._handle_outline_template(template_name)


@app.get("/api/uploaded-outline-templates")
async def uploaded_outline_templates(credentials_id: int | None = Query(None)) -> dict[str, Any]:
    return await app_utils._handle_uploaded_outline_templates(credentials_id)


@app.post("/api/uploaded-outline-templates")
async def upload_outline_templates(
    files: list[UploadFile] = File(...),
    credentials_id: int | None = Form(None),
) -> dict[str, Any]:
    return await app_utils._handle_upload_outline_templates(files, credentials_id)


@app.get("/api/uploaded-outline-templates/{template_name}")
async def uploaded_outline_template(template_name: str, credentials_id: int | None = Query(None)) -> dict[str, Any]:
    return await app_utils._handle_uploaded_outline_template(template_name, credentials_id)


@app.patch("/api/uploaded-outline-templates/{template_name}")
async def update_uploaded_outline_template(template_name: str, request: app_utils.UploadedOutlineTemplateUpdateRequest) -> dict[str, Any]:
    return await app_utils._handle_update_uploaded_outline_template(template_name, request)


@app.patch("/api/uploaded-outline-templates/{template_name}/rename")
async def rename_uploaded_outline_template(template_name: str, request: app_utils.UploadedOutlineTemplateRenameRequest) -> dict[str, Any]:
    return await app_utils._handle_rename_uploaded_outline_template(template_name, request)


@app.delete("/api/uploaded-outline-templates/{template_name}")
async def delete_uploaded_outline_template(template_name: str, credentials_id: int | None = Query(None)) -> dict[str, Any]:
    return await app_utils._handle_delete_uploaded_outline_template(template_name, credentials_id)


# ---------------------------------------------------------------------------------------------------------------
# Workspace bootstrap
# ---------------------------------------------------------------------------------------------------------------

@app.get("/api/workspace")
async def workspace_data() -> dict[str, Any]:
    return await app_utils._handle_workspace_data()


# ---------------------------------------------------------------------------------------------------------------
# Maintainer tools
# ---------------------------------------------------------------------------------------------------------------

@app.get("/api/maintainer/logs")
async def maintainer_logs(
    email: str | None = Query(None),
    session: str | None = Query(None),
    x_maintainer_token: str | None = Header(None),
    search: str | None = Query(None),
    status: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    sort_by: app_utils.LogSortField = Query("date"),
    sort_dir: app_utils.SortDirection = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=10, le=100),
) -> dict[str, Any]:
    return await app_utils._handle_maintainer_logs(email, session, x_maintainer_token, search, status, date_from, date_to, sort_by, sort_dir, page, page_size)


@app.post("/api/maintainer/logs/clear")
async def clear_maintainer_logs(
    request: app_utils.MaintainerLogClearRequest,
    x_maintainer_token: str | None = Header(None),
) -> dict[str, Any]:
    return await app_utils._handle_clear_maintainer_logs(request, x_maintainer_token)


# ---------------------------------------------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------------------------------------------

@app.post("/api/auth/login")
async def login(request: LoginRequest) -> dict[str, Any]:
    return await app_utils._handle_login(request)


@app.get("/api/auth/azure/login")
async def azure_login(request: Request) -> RedirectResponse:
    return await app_utils._handle_azure_login(request)


@app.get("/api/auth/azure/status")
async def azure_status() -> dict[str, Any]:
    return await app_utils._handle_azure_status()


@app.get("/api/auth/azure/callback")
async def azure_auth_callback(
    request: Request,
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
) -> RedirectResponse:
    return await app_utils._handle_azure_auth_callback(request, code, state, error)


@app.post("/api/auth/azure/session")
async def azure_session(http_request: Request, request: AzureSessionRequest) -> dict[str, Any]:
    return await app_utils._handle_azure_session(http_request, request)


@app.post("/api/auth/create-account")
async def create_account(request: CreateAccountRequest) -> dict[str, Any]:
    return await app_utils._handle_create_account(request)


@app.post("/api/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest) -> dict[str, Any]:
    return await app_utils._handle_forgot_password(request)


@app.post("/api/auth/verify-reset-code")
async def verify_reset_code(request: VerifyResetCodeRequest) -> dict[str, Any]:
    return await app_utils._handle_verify_reset_code(request)


@app.post("/api/auth/reset-password")
async def reset_password(request: ResetPasswordRequest) -> dict[str, Any]:
    return await app_utils._handle_reset_password(request)


@app.post("/api/auth/change-password")
async def change_password(request: ChangePasswordRequest) -> dict[str, Any]:
    return await app_utils._handle_change_password(request)


# ---------------------------------------------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------------------------------------------

@app.get("/api/settings/default")
async def default_settings(session: str | None = Query(None)) -> dict[str, Any]:
    return await app_utils._handle_default_settings(session)


@app.get("/api/settings/{settings_id}")
async def get_settings(
    settings_id: int,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    return await app_utils._handle_get_settings(settings_id, email, session)


@app.patch("/api/settings/{settings_id}")
async def update_settings(
    settings_id: int,
    request: app_utils.SettingsUpdateRequest,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    return await app_utils._handle_update_settings(settings_id, request, email, session)


# ---------------------------------------------------------------------------------------------------------------
# Generated files and manuscripts
# ---------------------------------------------------------------------------------------------------------------

@app.get("/api/generated-files")
async def generated_files(
    email: str | None = Query(None),
    session: str | None = Query(None),
    limit: int = Query(1000, ge=1, le=1000),
) -> dict[str, Any]:
    return await app_utils._handle_generated_files(email, session, limit)


@app.post("/api/generated-files")
async def create_generated_file(request: app_utils.GeneratedFileRequest) -> dict[str, Any]:
    return await app_utils._handle_create_generated_file(request)


@app.patch("/api/generated-files/{generated_file_id}")
async def update_generated_file(generated_file_id: int, request: app_utils.GeneratedFileUpdateRequest) -> dict[str, Any]:
    return await app_utils._handle_update_generated_file(generated_file_id, request)


@app.delete("/api/generated-files/{generated_file_id}")
async def delete_generated_file(
    generated_file_id: int,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    return await app_utils._handle_delete_generated_file(generated_file_id, email, session)


@app.get("/api/generated-files/{generated_file_id}/manuscript")
async def generated_file_manuscript(
    generated_file_id: int,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    return await app_utils._handle_generated_file_manuscript(generated_file_id, email, session)


@app.patch("/api/generated-files/{generated_file_id}/paragraph")
async def update_generated_file_paragraph(
    generated_file_id: int,
    request: app_utils.GeneratedFileParagraphUpdateRequest,
) -> dict[str, Any]:
    return await app_utils._handle_update_generated_file_paragraph(generated_file_id, request)


@app.patch("/api/generated-files/{generated_file_id}/section-content")
async def update_generated_file_section_content(
    generated_file_id: int,
    request: app_utils.GeneratedFileSectionContentUpdateRequest,
) -> dict[str, Any]:
    return await app_utils._handle_update_generated_file_section_content(generated_file_id, request)


@app.get("/api/generated-files/{generated_file_id}/download")
async def download_generated_file(
    generated_file_id: int,
    download_format: app_utils.DownloadFormat = Query("md", alias="format"),
    email: str | None = Query(None),
    session: str | None = Query(None),
):
    return await app_utils._handle_download_generated_file(generated_file_id, download_format, email, session)


@app.post("/api/generated-files/{generated_file_id}/literature-search")
async def enable_generated_file_literature_search(
    generated_file_id: int,
    request: app_utils.GeneratedFileLiteratureSearchRequest,
) -> dict[str, Any]:
    return await app_utils._handle_enable_generated_file_literature_search(generated_file_id, request)


@app.delete("/api/generated-files/{generated_file_id}/literature-search")
async def disable_generated_file_literature_search(
    generated_file_id: int,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    return await app_utils._handle_disable_generated_file_literature_search(generated_file_id, email, session)


@app.post("/api/generated-files/{generated_file_id}/uploaded-files/attach")
async def attach_uploaded_files_to_generated_file(
    generated_file_id: int,
    request: app_utils.GeneratedFileAttachUploadedFilesRequest,
) -> dict[str, Any]:
    return await app_utils._handle_attach_uploaded_files_to_generated_file(generated_file_id, request)


@app.delete("/api/generated-files/{generated_file_id}/uploaded-files/{uploaded_file_id}/attach")
async def remove_uploaded_file_attachment(
    generated_file_id: int,
    uploaded_file_id: int,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    return await app_utils._handle_remove_uploaded_file_attachment(generated_file_id, uploaded_file_id, email, session)


@app.get("/api/generated-files/{generated_file_id}/concept-map")
async def generated_file_concept_map(
    generated_file_id: int,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    return await app_utils._handle_generated_file_concept_map(generated_file_id, email, session)


@app.post("/api/generated-files/{generated_file_id}/generate")
async def generate_generated_file(
    generated_file_id: int,
    request: app_utils.GeneratedFileGenerateRequest,
) -> dict[str, Any]:
    return await app_utils._handle_generate_generated_file(generated_file_id, request)


# ---------------------------------------------------------------------------------------------------------------
# Generation jobs
# ---------------------------------------------------------------------------------------------------------------

@app.get("/api/generation-jobs/{job_id}")
async def generation_job(job_id: str) -> dict[str, Any]:
    return await app_utils._handle_generation_job(job_id)


@app.post("/api/generation-jobs/{job_id}/pause")
async def pause_generation_job(job_id: str) -> dict[str, Any]:
    return await app_utils._handle_pause_generation_job(job_id)


# ---------------------------------------------------------------------------------------------------------------
# Uploaded documents
# ---------------------------------------------------------------------------------------------------------------

@app.get("/api/uploaded-files")
async def uploaded_files(
    email: str | None = Query(None),
    session: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    return await app_utils._handle_uploaded_files(email, session, limit)


@app.post("/api/uploaded-files")
async def upload_uploaded_files(
    files: list[UploadFile] = File(...),
    email: str | None = Form(None),
    session: str | None = Form(None),
    replace: bool = Form(False),
) -> dict[str, Any]:
    return await app_utils._handle_upload_uploaded_files(files, email, session, replace)


@app.patch("/api/uploaded-files/{uploaded_file_id}")
async def update_uploaded_file(uploaded_file_id: int, request: app_utils.UploadedFileUpdateRequest) -> dict[str, Any]:
    return await app_utils._handle_update_uploaded_file(uploaded_file_id, request)


@app.delete("/api/uploaded-files/{uploaded_file_id}")
async def delete_uploaded_file(
    uploaded_file_id: int,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    return await app_utils._handle_delete_uploaded_file(uploaded_file_id, email, session)


# ---------------------------------------------------------------------------------------------------------------
# AI outline utilities
# ---------------------------------------------------------------------------------------------------------------

@app.post("/api/ai/outline")
async def create_outline(request: Request) -> dict[str, Any]:
    return await app_utils._handle_create_outline(request)


@app.post("/api/ai/outline/import")
async def import_outline(file: UploadFile = File(...), credentials_id: int | None = Form(None)) -> dict[str, Any]:
    return await app_utils._handle_import_outline(file, credentials_id)


@app.post("/api/ai/outline/format")
async def format_outline(request: app_utils.OutlineFormatRequest) -> dict[str, Any]:
    return await app_utils._handle_format_outline(request)


frontend_dist_paths = [
    Config.DIR_HOME / "dist",
    Path(__file__).resolve().parents[1] / "frontend" / "dist",
]
frontend_dist = next((path for path in frontend_dist_paths if path.exists()), None)
if frontend_dist is not None:
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8012, reload=True)
