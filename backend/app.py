from datetime import datetime
from enum import Enum
import asyncio
import importlib
import ast
import json
import logging
from pathlib import Path
import re
import shutil
import sys
import tempfile
import types
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from src.utils import Config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discourse2draft.api")

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

app = FastAPI(title="Discourse2Draft API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AIRequestBase(BaseModel):
    model_name: str | None = None
    temperature: float = 0
    instructions: str = ""


class ContentRequest(AIRequestBase):
    architecture_type: Literal["base", "rag", "graphrag"] = "base"
    collection_name: str = ""
    collection_name_lit_search: str = ""
    content_pre: str = ""
    current_section: str
    content_specific_instructions: str = ""
    keyphrases: list[str] = Field(default_factory=list)
    rag_context: str = ""
    graphrag_context: dict[str, Any] = Field(default_factory=dict)
    literature_list: list[dict[str, Any]] = Field(default_factory=list)
    references: list[dict[str, Any]] = Field(default_factory=list)
    is_abstract: bool = False
    concept_map: dict[str, Any] = Field(default_factory=dict)


class OutlineRequest(AIRequestBase):
    query: str
    dir_path_ref_files: str | None = None


class OutlineFormatRequest(AIRequestBase):
    outline_unstructured: str
    query: str = ""


class AbstractDetectorRequest(AIRequestBase):
    current_section: str


class AbstractWriterRequest(AIRequestBase):
    content_pre: str = ""
    current_section: str
    content_specific_instructions: str = ""


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


class GeneratedFileRequest(BaseModel):
    email: str | None = None
    session: str
    settings_id: int | None = None
    file_name: str
    ai_architecture: Literal["base", "rag", "graphrag"] = "base"


class GeneratedFileUpdateRequest(BaseModel):
    file_name: str


class GeneratedFileOutlineRequest(BaseModel):
    outline: str
    email: str | None = None
    session: str | None = None


class GeneratedFileGenerateRequest(AIRequestBase):
    outline: str
    email: str | None = None
    session: str | None = None
    architecture_type: Literal["base", "rag", "graphrag"] | None = None
    collection_name: str = ""
    collection_name_lit_search: str = ""
    attached_references: dict[str, str] = Field(default_factory=dict)


class SettingsUpdateRequest(BaseModel):
    llm: str
    temperature: float = Field(ge=0, le=2)
    instructions: str = ""


class DBSelectRequest(BaseModel):
    table_name: str
    field_names: list[str] = Field(default_factory=list)
    field_values: list[list[Any]] = Field(default_factory=list)
    order_by_field_names: list[str] = Field(default_factory=list)
    order_by_types: list[Literal["ASC", "DESC"]] = Field(default_factory=list)
    limit: int | None = None


class DBInsertRequest(BaseModel):
    table_name: str
    field_names: list[str]
    field_values: list[list[Any]]


class DBUpdateRequest(BaseModel):
    table_name: str
    update_fields: list[str]
    update_values: list[Any]
    select_fields: list[str]
    select_values: list[list[Any]]


class VectorCollectionRequest(BaseModel):
    collection_name: str
    embedding: str = "text-embedding-3-large"
    delete_if_exists: bool = False


class VectorQueryRequest(BaseModel):
    collection_name: str
    query: str
    embedding: str = "text-embedding-3-large"
    is_graph: bool = False


class VectorPathIngestRequest(BaseModel):
    collection_name: str
    file_paths: list[str]
    embedding: str = "text-embedding-3-large"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    is_graph: bool = False


def _required_default_model() -> str:
    model_name = Config.env_config.get("DEFAULT_AI_MODEL")
    if not model_name:
        raise HTTPException(
            status_code=503,
            detail="DEFAULT_AI_MODEL is not configured. Add DEFAULT_AI_MODEL to backend/.env and restart the backend.",
        )
    return model_name


def _model_name(model_name: str | None) -> str:
    return model_name or _required_default_model()


def _api_error(action: str, exp: Exception) -> HTTPException:
    logger.exception("Unable to %s", action)
    return HTTPException(status_code=500, detail=f"Unable to {action}: {exp}")


def _jsonable(value: Any) -> Any:
    try:
        return jsonable_encoder(value)
    except Exception:
        if isinstance(value, dict):
            return {str(k): _jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [_jsonable(v) for v in value]
        if isinstance(value, datetime):
            return value.isoformat()
        return repr(value)


def _content_state(request: ContentRequest) -> dict[str, Any]:
    return {
        "content_pre": request.content_pre,
        "current_section": request.current_section,
        "content_specific_instructions": request.content_specific_instructions,
        "keyphrases": request.keyphrases,
        "rag_context": request.rag_context,
        "graphrag_context": request.graphrag_context,
        "literature_list": request.literature_list,
        "steps": [],
        "content": "",
        "content_summary": "",
        "references": request.references,
        "is_abstract": request.is_abstract,
        "concept_map": request.concept_map,
    }


def _outline_state(query: str = "", outline_unstructured: str = "") -> dict[str, Any]:
    return {
        "query": query,
        "steps": [],
        "reference_summary": "",
        "content": "",
        "outline_unstructured": outline_unstructured,
    }


def _records_from_dataframe(df: Any) -> list[dict[str, Any]]:
    df = df.drop(columns=["_sa_instance_state"], errors="ignore")
    return _jsonable(df.to_dict(orient="records"))


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _validate_email(email: str) -> str:
    normalized = _normalize_email(email)
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", normalized):
        raise HTTPException(status_code=400, detail="A valid email is required.")
    return normalized


def _validate_password(password: str, confirm_password: str | None = None) -> None:
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


def _credential_by_email(email: str) -> dict[str, Any] | None:
    from src import db

    df = db.selectFromDB(table_name="credentials", field_names=["email"], field_values=[[email]], limit=1)
    records = _records_from_dataframe(df)
    return records[0] if records else None


def _public_user(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "email": record.get("email"),
        "first_name": record.get("first_name"),
        "last_name": record.get("last_name"),
    }


def _create_default_settings(email: str) -> dict[str, Any]:
    from src import db

    now = datetime.now()
    session_id = uuid4().hex
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


def _auth_payload(credential: dict[str, Any]) -> dict[str, Any]:
    settings = _create_default_settings(str(credential["email"]))
    return {
        "user": _public_user(credential),
        "session": settings["session"],
        "settings": settings,
    }


def _settings_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "email": record.get("email"),
        "session": record.get("session"),
        "llm": record.get("llm"),
        "temperature": record.get("temperature"),
        "instructions": record.get("instructions") or "",
        "create_date": record.get("create_date"),
        "update_date": record.get("update_date"),
    }


def _default_settings() -> dict[str, Any]:
    return {
        "id": None,
        "email": None,
        "session": uuid4().hex,
        "llm": _required_default_model(),
        "temperature": 0.0,
        "instructions": "",
        "create_date": None,
        "update_date": None,
    }


def _llm_options() -> list[dict[str, str]]:
    from src.ai.llms import extractAvailableLLMs

    options = []
    default_model = _required_default_model()
    available_llms = extractAvailableLLMs()

    if isinstance(available_llms, dict):
        for provider, models in available_llms.items():
            if isinstance(models, dict):
                for value, label in models.items():
                    model_value = label if value == "Uncategorized" else value
                    options.append({"provider": provider, "value": str(model_value), "label": str(label)})
            else:
                options.append({"provider": provider, "value": str(models), "label": str(models)})
    else:
        for model in available_llms:
            options.append({"provider": "Available", "value": str(model), "label": str(model)})

    if not any(option["value"] == default_model for option in options):
        options.insert(0, {"provider": "Default", "value": default_model, "label": default_model})

    return options


def _generated_file_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "email": record.get("email"),
        "session": record.get("session"),
        "file_name": record.get("file_name"),
        "status": record.get("status"),
        "settings_id": record.get("settings_id"),
        "ai_architecture": record.get("ai_architecture"),
        "create_date": record.get("create_date"),
        "update_date": record.get("update_date"),
    }


def _generated_document(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "name": record.get("file_name"),
        "date": record.get("update_date") or record.get("create_date"),
        "status": record.get("status"),
        "session": record.get("session"),
        "settings_id": record.get("settings_id"),
        "ai_architecture": record.get("ai_architecture"),
    }


def _generated_file_by_id(
    generated_file_id: int,
    email: str | None = None,
    session: str | None = None,
) -> dict[str, Any]:
    from src import db

    field_names = ["id"]
    field_values = [[generated_file_id]]
    if email:
        field_names.append("email")
        field_values.append([_validate_email(email)])
    if session:
        field_names.append("session")
        field_values.append([session])

    df = db.selectFromDB(
        table_name="generated_files",
        field_names=field_names,
        field_values=field_values,
        limit=1,
    )
    records = _records_from_dataframe(df)
    if not records:
        raise HTTPException(status_code=404, detail="Generated file was not found.")

    return records[0]


def _uploaded_file_type(file_name: str | None) -> str:
    suffix = Path(file_name or "").suffix.lower().lstrip(".")
    if suffix in {"doc", "docx"}:
        return "doc"
    if suffix == "pdf":
        return "pdf"
    return suffix or "file"


def _uploaded_file_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "email": record.get("email"),
        "session": record.get("session"),
        "file_name": record.get("file_name"),
        "status": record.get("status"),
        "create_date": record.get("create_date"),
        "update_date": record.get("update_date"),
    }


def _uploaded_document(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "name": record.get("file_name"),
        "date": record.get("update_date") or record.get("create_date"),
        "type": _uploaded_file_type(record.get("file_name")),
        "status": record.get("status"),
        "session": record.get("session"),
    }


def _is_content_key(value: Any) -> bool:
    return str(value).strip().lower() in {"content", "[--content--]", "__content__"}


def _text_from_content_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        for key in ("body", "content", "text", "value", "generated_content"):
            if key in value:
                text = _text_from_content_value(value[key])
                if text:
                    return text
        return ""
    if isinstance(value, list):
        fragments = []
        for item in value:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                content_type = str(item[0]).strip().lower()
                if content_type in {
                    "content",
                    "body",
                    "text",
                    "generated_content",
                    "paragraph",
                    "content_user",
                    "content_ai",
                }:
                    text = _text_from_content_value(item[1])
                    if text:
                        fragments.append(text)
            elif isinstance(item, str):
                fragments.append(item.strip())
            elif isinstance(item, dict):
                text = _text_from_content_value(item)
                if text:
                    fragments.append(text)
        return "\n\n".join(fragment for fragment in fragments if fragment)
    return ""


def _section_body_from_outline_node(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if not isinstance(value, dict):
        return ""

    for key in ("body", "text", "generated_content"):
        if key in value:
            text = _text_from_content_value(value[key])
            if text:
                return text

    for key, item in value.items():
        if _is_content_key(key):
            return _text_from_content_value(item)

    return ""


def _manuscript_from_section_records(records: list[Any]) -> list[dict[str, str]]:
    sections = []
    for record in records:
        if not isinstance(record, dict):
            continue

        heading = record.get("heading") or record.get("title") or record.get("header") or record.get("section")
        if heading:
            sections.append(
                {
                    "heading": str(heading),
                    "body": _text_from_content_value(record.get("body") or record.get("content") or record.get("text")),
                }
            )

        children = record.get("children") or record.get("sections") or []
        if isinstance(children, list):
            sections.extend(_manuscript_from_section_records(children))

    return sections


def _manuscript_from_outline_tree(node: Any) -> list[dict[str, str]]:
    if isinstance(node, list):
        section_records = _manuscript_from_section_records(node)
        if section_records:
            return section_records
        return []

    if not isinstance(node, dict):
        return []

    sections = []
    for heading, value in node.items():
        if _is_content_key(heading) or str(heading).strip().lower() in {"references", "bibliography"}:
            continue

        sections.append({"heading": str(heading), "body": _section_body_from_outline_node(value)})
        sections.extend(_manuscript_from_outline_tree(value))

    return sections


def _manuscript_from_outline_file(file_id: int) -> tuple[list[dict[str, str]], bool]:
    outline_file_path = Config.DIR_CONTENTS / f"outline_{file_id}.json"
    if not outline_file_path.exists():
        return [], False

    with outline_file_path.open() as fp:
        outline_data = json.load(fp)

    if isinstance(outline_data, dict):
        if any(key in outline_data for key in ("heading", "title", "header", "section")):
            return _manuscript_from_section_records([outline_data]), True
        for key in ("manuscript", "sections"):
            if isinstance(outline_data.get(key), list):
                return _manuscript_from_section_records(outline_data[key]), True

    return _manuscript_from_outline_tree(outline_data), True


def _outline_template_content(template_name: str) -> str:
    if not re.match(r"^[a-zA-Z0-9_-]+$", template_name):
        raise HTTPException(status_code=400, detail="Invalid outline template name.")

    template_path = Path(__file__).resolve().parent / "data" / "outline_templates" / f"{template_name}.md"
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Outline template was not found.")

    return template_path.read_text()


def _un_markdown_text(text: str) -> str:
    try:
        from bs4 import BeautifulSoup
        from markdown import markdown

        return "".join(BeautifulSoup(markdown(text), features="html.parser").find_all(text=True))
    except Exception:
        return re.sub(r"[*_`#>\[\]()]", "", text)


def _process_outline(outline: str) -> dict[str, Any]:
    manage_outline_path = Path(__file__).resolve().parent / "src" / "manage_outline.py"
    source = manage_outline_path.read_text()
    module = ast.parse(source, filename=str(manage_outline_path))
    required_names = {"ContentTypes", "SpecialSectionTypes", "insertOutline", "processOutline"}
    body = [
        node
        for node in module.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in required_names
    ]
    namespace = {
        "Enum": Enum,
        "re": re,
        "unMarkdownText": _un_markdown_text,
        "print_func_name": lambda func: func,
    }
    exec(compile(ast.Module(body=body, type_ignores=[]), str(manage_outline_path), "exec"), namespace)
    return namespace["processOutline"](outline)


GENERATION_JOBS: dict[str, dict[str, Any]] = {}
OUTLINE_CONTENT_KEY = "content"
OUTLINE_IS_ABSTRACT = "is_abstract"
OUTLINE_INSTRUCTIONS = "instructions"
OUTLINE_CONTENT_USER = "content_user"
OUTLINE_CONTENT_AI = "content_ai"
OUTLINE_CONTENT_PRE_SUMMARY = "content_pre_summary"
OUTLINE_CONCEPT_MAP = "concept_map"


def _outline_file_path(generated_file_id: int) -> Path:
    return Config.DIR_CONTENTS / f"outline_{generated_file_id}.json"


def _read_outline_file(generated_file_id: int) -> dict[str, Any]:
    outline_file_path = _outline_file_path(generated_file_id)
    with outline_file_path.open() as fp:
        outline_data = json.load(fp)
    if not isinstance(outline_data, dict):
        raise ValueError("The saved outline was not a valid JSON object.")
    return outline_data


def _write_outline_file(generated_file_id: int, outline_data: dict[str, Any]) -> Path:
    outline_file_path = _outline_file_path(generated_file_id)
    outline_file_path.parent.mkdir(parents=True, exist_ok=True)
    with outline_file_path.open("w") as fp:
        json.dump(outline_data, fp, indent=2)
    return outline_file_path


def _save_processed_outline(
    generated_file_id: int,
    outline: str,
    email: str | None = None,
    session: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    from src import db

    outline = outline.strip()
    if not outline:
        raise HTTPException(status_code=400, detail="A structured outline is required before content generation can start.")

    record = _generated_file_by_id(generated_file_id, email=email, session=session)
    try:
        processed_outline = _process_outline(outline)
    except Exception as exp:
        raise HTTPException(
            status_code=400,
            detail=f"I could not understand that structured outline. Check the heading levels and [--content--] tags, then try again. Details: {exp}",
        ) from exp

    outline_file_path = _write_outline_file(generated_file_id, processed_outline)
    now = datetime.now()
    db.updateDB(
        table_name="generated_files",
        update_fields=["update_date"],
        update_values=[now],
        select_fields=["id"],
        select_values=[[generated_file_id]],
    )
    return {**record, "update_date": now}, processed_outline, outline_file_path


def _set_generated_file_status(generated_file_id: int, status: str) -> None:
    try:
        from src import db

        db.updateDB(
            table_name="generated_files",
            update_fields=["status", "update_date"],
            update_values=[status, datetime.now()],
            select_fields=["id"],
            select_values=[[generated_file_id]],
        )
    except Exception:
        logger.exception("Unable to update generated file %s status to %s", generated_file_id, status)


def _job_snapshot(job: dict[str, Any]) -> dict[str, Any]:
    public_keys = {
        "id",
        "generated_file_id",
        "status",
        "message",
        "error",
        "current_section",
        "completed_sections",
        "total_sections",
        "manuscript",
        "generated_file",
        "created_at",
        "updated_at",
    }
    return _jsonable({key: job.get(key) for key in public_keys if key in job})


def _normalize_content_item(item: Any) -> tuple[str, Any] | None:
    if isinstance(item, (list, tuple)) and len(item) >= 2:
        return str(item[0]), item[1]
    return None


def _content_items(node: dict[str, Any]) -> list[Any]:
    content = node.get(OUTLINE_CONTENT_KEY)
    return content if isinstance(content, list) else []


def _content_value(items: list[Any], content_type: str, default: Any = "") -> Any:
    for item in items:
        normalized = _normalize_content_item(item)
        if normalized and normalized[0] == content_type:
            return normalized[1]
    return default


def _truthy_content_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "abstract"}
    return bool(value)


def _set_content_value(items: list[Any], content_type: str, value: Any) -> None:
    for item in items:
        if isinstance(item, list) and item and str(item[0]) == content_type:
            if len(item) == 1:
                item.append(value)
            else:
                item[1] = value
            return
        if isinstance(item, tuple) and len(item) >= 2 and str(item[0]) == content_type:
            items[items.index(item)] = [content_type, value]
            return
    items.append([content_type, value])


def _section_needs_ai(items: list[Any]) -> bool:
    return any((_normalize_content_item(item) or ("", ""))[0] == OUTLINE_CONTENT_AI for item in items)


def _section_is_abstract(items: list[Any]) -> bool:
    return _truthy_content_flag(_content_value(items, OUTLINE_IS_ABSTRACT, False))


def _section_instructions(items: list[Any]) -> str:
    return str(_content_value(items, OUTLINE_INSTRUCTIONS, "") or "").strip()


def _section_prompt(path: list[str], items: list[Any]) -> str:
    lines = []
    for index, heading in enumerate(path):
        lines.append(f"{'#' * min(index + 1, 6)} {heading}")

    for item in items:
        normalized = _normalize_content_item(item)
        if not normalized:
            continue
        content_type, text = normalized
        if content_type == OUTLINE_CONTENT_USER and text:
            lines.append(str(text).strip())
        elif content_type == OUTLINE_CONTENT_AI:
            lines.append("[--content--]")

    return "\n\n".join(line for line in lines if line)


def _extract_generation_sections(outline_data: dict[str, Any]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []

    def walk(node: Any, path: list[str]) -> None:
        if not isinstance(node, dict):
            return

        items = _content_items(node)
        if items and _section_needs_ai(items):
            sections.append(
                {
                    "path": path.copy(),
                    "heading": path[-1] if path else "Untitled section",
                    "node": node,
                    "items": items,
                    "instructions": _section_instructions(items),
                    "is_abstract": _section_is_abstract(items),
                    "current_section": _section_prompt(path, items),
                }
            )

        for key, value in node.items():
            if key == OUTLINE_CONTENT_KEY:
                continue
            walk(value, [*path, str(key)])

    walk(outline_data, [])
    regular_sections = [section for section in sections if not section["is_abstract"]]
    abstract_sections = [section for section in sections if section["is_abstract"]]
    return regular_sections + abstract_sections


def _mark_first_abstract_section(outline_data: dict[str, Any], agent_abstract_detector: Any) -> tuple[dict[str, Any], str]:
    if not outline_data:
        return outline_data, ""

    title = next(iter(outline_data))
    title_node = outline_data.get(title)
    if not isinstance(title_node, dict):
        return outline_data, ""

    first_section_header = ""
    first_section_node: dict[str, Any] | None = None
    for key, value in title_node.items():
        if key == OUTLINE_CONTENT_KEY or not isinstance(value, dict):
            continue
        first_section_header = str(key)
        first_section_node = value
        break

    if first_section_node is None:
        return outline_data, ""

    content = first_section_node.setdefault(OUTLINE_CONTENT_KEY, [])
    if content and (_normalize_content_item(content[0]) or ("", False))[0] == OUTLINE_IS_ABSTRACT:
        return outline_data, first_section_header if _section_is_abstract(content) else ""

    response = agent_abstract_detector.invoke({"current_section": first_section_header})
    is_abstract = _truthy_content_flag(response.get(OUTLINE_IS_ABSTRACT, False)) if isinstance(response, dict) else False
    if is_abstract:
        content.insert(0, [OUTLINE_IS_ABSTRACT, True])
        return outline_data, first_section_header

    return outline_data, ""


def _safe_architecture_classes() -> tuple[Any, Any, Any]:
    _required_default_model()
    original_apply = None
    nest_asyncio_module = None
    try:
        import nest_asyncio

        nest_asyncio_module = nest_asyncio
        original_apply = nest_asyncio.apply
        nest_asyncio.apply = lambda *args, **kwargs: None
    except Exception:
        nest_asyncio_module = None

    try:
        from src.ai.architecture import (
            AbstractSectionDetectorArchitecture,
            AbstractWriterArchitecture,
            ContentWriterArchitecture,
        )

        return AbstractSectionDetectorArchitecture, AbstractWriterArchitecture, ContentWriterArchitecture
    finally:
        if nest_asyncio_module is not None and original_apply is not None:
            nest_asyncio_module.apply = original_apply


def _safe_generate_content_function() -> Any:
    try:
        _safe_architecture_classes()
        from src.generate import generateContent

        return generateContent
    except ImportError:
        logger.debug("Loading generateContent from source because src.generate has import-time dependencies.", exc_info=True)

    class ArchitecturePlaceholder:
        pass

    generate_path = Path(__file__).resolve().parent / "src" / "generate.py"
    source = generate_path.read_text()
    module = ast.parse(source, filename=str(generate_path))
    body = [
        node
        for node in module.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "generateContent"
    ]
    namespace = {
        "AbstractWriterArchitecture": ArchitecturePlaceholder,
        "ContentWriterArchitecture": ArchitecturePlaceholder,
        "dict": dict,
        "logging": logging,
        "print_func_name": lambda func: func,
        "re": re,
        "formatCitations": lambda text: text,
        "getLiteraturesFromDB": lambda literature_id_list: ([], {}),
    }
    exec(compile(ast.Module(body=body, type_ignores=[]), str(generate_path), "exec"), namespace)
    return namespace["generateContent"]


async def _generate_section_content(
    agent: Any,
    content_pre_summary: str,
    current_section: str,
    instructions: str,
    attached_references: dict[str, str],
) -> tuple[str, str, dict[str, Any], list[str], str]:
    class CachingAgent:
        def __init__(self, wrapped_agent: Any) -> None:
            self.wrapped_agent = wrapped_agent
            self.response: dict[str, Any] | None = None

        async def ainvoke(self, input: dict[str, Any]) -> dict[str, Any]:
            self.response = await self.wrapped_agent.ainvoke(input)
            return self.response

    caching_agent = CachingAgent(agent)
    try:
        generate_content = _safe_generate_content_function()
        return await generate_content(
            caching_agent,
            content_pre_summary,
            current_section,
            instructions,
            attached_references.copy(),
        )
    except Exception:
        if caching_agent.response is None:
            raise
        logger.debug("Falling back to direct generation response parsing", exc_info=True)

    response = caching_agent.response
    content = str(response.get("content") or "").strip()
    content_summary = str(response.get("content_summary") or response.get("content_pre") or content).strip()
    concept_map = response.get("concept_map", {})
    if not isinstance(concept_map, dict):
        concept_map = {}

    next_summary_parts = [part for part in (content_pre_summary.strip(), content_summary) if part]
    next_content_pre_summary = "\n\n".join(dict.fromkeys(next_summary_parts))
    sanitized_content = re.sub(r" \~([^\~])", r" \\~\1", content)
    return next_content_pre_summary, content, concept_map, [], sanitized_content


async def _run_generation_job(
    job_id: str,
    generated_file_id: int,
    request: GeneratedFileGenerateRequest,
    generated_file: dict[str, Any],
) -> None:
    job = GENERATION_JOBS[job_id]

    def update_job(**updates: Any) -> None:
        job.update(updates)
        job["updated_at"] = datetime.now().isoformat()

    try:
        from src import db

        update_job(status="running", message="Reading the saved outline...")
        _set_generated_file_status(generated_file_id, db.generated_files_status.RUNNING.value)
        outline_data = _read_outline_file(generated_file_id)

        update_job(message="Checking for an abstract section...")
        AbstractSectionDetectorArchitecture, AbstractWriterArchitecture, ContentWriterArchitecture = _safe_architecture_classes()
        detector = AbstractSectionDetectorArchitecture(
            model_name=_model_name(request.model_name),
            temperature=request.temperature,
            instructions=request.instructions,
        )
        outline_data, _ = await asyncio.to_thread(_mark_first_abstract_section, outline_data, detector)
        _write_outline_file(generated_file_id, outline_data)

        sections = _extract_generation_sections(outline_data)
        update_job(
            total_sections=len(sections),
            manuscript=_manuscript_from_outline_tree(outline_data),
        )
        if not sections:
            _set_generated_file_status(generated_file_id, db.generated_files_status.SUCCESS.value)
            update_job(
                status="completed",
                message="The structured outline was saved. No AI content sections were marked for generation.",
                current_section="",
                generated_file={**generated_file, "status": db.generated_files_status.SUCCESS.value},
            )
            return

        architecture_type = generated_file.get("ai_architecture") or request.architecture_type or "base"
        writer = ContentWriterArchitecture(
            model_name=_model_name(request.model_name),
            temperature=request.temperature,
            instructions=request.instructions,
            type=architecture_type,
            collection_name=request.collection_name,
            collection_name_lit_search=request.collection_name_lit_search,
        )
        abstract_writer = AbstractWriterArchitecture(
            model_name=_model_name(request.model_name),
            temperature=request.temperature,
            instructions=request.instructions,
        )

        content_pre_summary = ""
        attached_references = request.attached_references.copy()
        for index, section in enumerate(sections, start=1):
            section_label = section["heading"]
            update_job(
                message=f"Writing section {index} of {len(sections)}: {section_label}",
                current_section=section_label,
                completed_sections=index - 1,
                manuscript=_manuscript_from_outline_tree(outline_data),
            )
            agent = abstract_writer if section["is_abstract"] else writer
            (
                content_pre_summary,
                content_for_frontend,
                concept_map,
                _ref_list,
                sanitized_content,
            ) = await _generate_section_content(
                agent=agent,
                content_pre_summary=content_pre_summary,
                current_section=section["current_section"],
                instructions=section["instructions"],
                attached_references=attached_references,
            )
            _set_content_value(section["items"], OUTLINE_CONTENT_AI, sanitized_content or content_for_frontend)
            _set_content_value(section["items"], OUTLINE_CONTENT_PRE_SUMMARY, content_pre_summary)
            if concept_map:
                _set_content_value(section["items"], OUTLINE_CONCEPT_MAP, concept_map)
            _write_outline_file(generated_file_id, outline_data)
            update_job(
                completed_sections=index,
                manuscript=_manuscript_from_outline_tree(outline_data),
            )

        _set_generated_file_status(generated_file_id, db.generated_files_status.SUCCESS.value)
        update_job(
            status="completed",
            message="Content generation completed.",
            current_section="",
            generated_file={**generated_file, "status": db.generated_files_status.SUCCESS.value},
            manuscript=_manuscript_from_outline_tree(outline_data),
        )
    except Exception as exp:
        logger.exception("Unable to generate manuscript for generated file %s", generated_file_id)
        _set_generated_file_status(generated_file_id, "error")
        update_job(
            status="error",
            error=f"Unable to generate manuscript content: {exp}",
            message="Content generation stopped.",
            current_section="",
        )


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "default_model": Config.env_config.get("DEFAULT_AI_MODEL"),
        "chroma_host": Config.env_config.get("CHROMA_HOST"),
        "chroma_port": Config.env_config.get("CHROMA_PORT"),
    }


@app.get("/api/outline-templates/{template_name}")
async def outline_template(template_name: str) -> dict[str, Any]:
    try:
        return {"name": template_name, "content": _outline_template_content(template_name)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("load outline template", exp)


@app.get("/api/workspace")
async def workspace_data() -> dict[str, Any]:
    return {
        "outline_template": '',
        "manuscript": [],
        "generated_documents": [],
        "uploaded_documents": [],
    }


@app.post("/api/auth/login")
async def login(request: LoginRequest) -> dict[str, Any]:
    try:
        from src import db

        email = _validate_email(request.email)
        credential = _credential_by_email(email)
        if credential is None or credential.get("password") != db.encryptPassword(request.password):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        return {"status": "authenticated", **_auth_payload(credential)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("authenticate user", exp)


@app.post("/api/auth/create-account")
async def create_account(request: CreateAccountRequest) -> dict[str, Any]:
    try:
        from src import db

        email = _validate_email(request.email)
        first_name = request.first_name.strip()
        last_name = request.last_name.strip()
        if not first_name or not last_name:
            raise HTTPException(status_code=400, detail="First name and last name are required.")
        _validate_password(request.password, request.confirm_password)

        if _credential_by_email(email) is not None:
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
        return {"status": "created", **_auth_payload(user)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("create account", exp)


@app.post("/api/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest) -> dict[str, Any]:
    try:
        email = _validate_email(request.email)
        credential = _credential_by_email(email)
        if credential is None:
            raise HTTPException(status_code=404, detail="No account was found for that email.")

        return {
            "status": "account_found",
            "email": email,
            "message": "Account found. Password reset code delivery is not configured yet.",
        }
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("verify account", exp)


@app.get("/api/settings/default")
async def default_settings() -> dict[str, Any]:
    try:
        return {"settings": _default_settings(), "llm_options": _llm_options()}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("load default settings", exp)


@app.get("/api/settings/{settings_id}")
async def get_settings(
    settings_id: int,
    email: str = Query(...),
    session: str = Query(...),
) -> dict[str, Any]:
    try:
        from src import db

        normalized_email = _validate_email(email)
        df = db.selectFromDB(
            table_name="settings",
            field_names=["id", "email", "session"],
            field_values=[[settings_id], [normalized_email], [session]],
            limit=1,
        )
        records = _records_from_dataframe(df)
        if not records:
            raise HTTPException(status_code=404, detail="Settings row was not found for this session.")

        return {"settings": _settings_record(records[0]), "llm_options": _llm_options()}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("load settings", exp)


@app.patch("/api/settings/{settings_id}")
async def update_settings(
    settings_id: int,
    request: SettingsUpdateRequest,
    email: str = Query(...),
    session: str = Query(...),
) -> dict[str, Any]:
    try:
        from src import db

        normalized_email = _validate_email(email)
        df = db.selectFromDB(
            table_name="settings",
            field_names=["id", "email", "session"],
            field_values=[[settings_id], [normalized_email], [session]],
            limit=1,
        )
        if not _records_from_dataframe(df):
            raise HTTPException(status_code=404, detail="Settings row was not found for this session.")

        llm_options = _llm_options()
        valid_llms = {option["value"] for option in llm_options}
        if valid_llms and request.llm not in valid_llms:
            raise HTTPException(status_code=400, detail="Invalid LLM selection.")

        now = datetime.now()
        db.updateDB(
            table_name="settings",
            update_fields=["llm", "temperature", "instructions", "update_date"],
            update_values=[request.llm, request.temperature, request.instructions, now],
            select_fields=["id", "email", "session"],
            select_values=[[settings_id], [normalized_email], [session]],
        )
        updated = db.selectFromDB(
            table_name="settings",
            field_names=["id", "email", "session"],
            field_values=[[settings_id], [normalized_email], [session]],
            limit=1,
        )
        records = _records_from_dataframe(updated)
        return {"status": "saved", "settings": _settings_record(records[0]), "llm_options": llm_options}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("update settings", exp)


@app.get("/api/generated-files")
async def generated_files(email: str = Query(...), limit: int = Query(50, ge=1, le=200)) -> dict[str, Any]:
    try:
        from src import db

        normalized_email = _validate_email(email)
        active_statuses = [
            status.value for status in db.generated_files_status if status != db.generated_files_status.DELETED
        ]
        df = db.selectFromDB(
            table_name="generated_files",
            field_names=["email", "status"],
            field_values=[[normalized_email], active_statuses],
            order_by_field_names=["update_date"],
            order_by_types=["DESC"],
            limit=limit,
        )
        records = _records_from_dataframe(df)
        return {
            "generated_files": [_generated_file_record(record) for record in records],
            "generated_documents": [_generated_document(record) for record in records],
        }
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("load generated files", exp)


@app.get("/api/generated-files/{generated_file_id}/manuscript")
async def generated_file_manuscript(
    generated_file_id: int,
    email: str | None = Query(None),
    session: str | None = Query(None),
) -> dict[str, Any]:
    try:
        record = _generated_file_by_id(generated_file_id, email=email, session=session)
        manuscript, source_exists = _manuscript_from_outline_file(generated_file_id)
        return {
            "generated_file": _generated_file_record(record),
            "manuscript": manuscript,
            "source_exists": source_exists,
            "message": "" if source_exists else "No manuscript content has been saved for this file yet.",
        }
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("load manuscript", exp)


@app.post("/api/generated-files/{generated_file_id}/outline")
async def save_generated_file_outline(
    generated_file_id: int,
    request: GeneratedFileOutlineRequest,
) -> dict[str, Any]:
    try:
        updated_record, processed_outline, outline_file_path = _save_processed_outline(
            generated_file_id,
            request.outline,
            email=request.email,
            session=request.session,
        )
        manuscript, _ = _manuscript_from_outline_file(generated_file_id)
        return {
            "status": "saved",
            "generated_file": _generated_file_record(updated_record),
            "outline": _jsonable(processed_outline),
            "manuscript": manuscript,
            "path": str(outline_file_path),
        }
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("save structured outline", exp)


@app.post("/api/generated-files/{generated_file_id}/generate")
async def generate_generated_file(
    generated_file_id: int,
    request: GeneratedFileGenerateRequest,
) -> dict[str, Any]:
    try:
        _required_default_model()
        generated_file, processed_outline, outline_file_path = _save_processed_outline(
            generated_file_id,
            request.outline,
            email=request.email,
            session=request.session,
        )
        job_id = uuid4().hex
        manuscript = _manuscript_from_outline_tree(processed_outline)
        job = {
            "id": job_id,
            "generated_file_id": generated_file_id,
            "status": "queued",
            "message": "Structured outline saved. Content generation is queued...",
            "error": "",
            "current_section": "",
            "completed_sections": 0,
            "total_sections": 0,
            "manuscript": manuscript,
            "generated_file": _generated_file_record(generated_file),
            "outline_path": str(outline_file_path),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        GENERATION_JOBS[job_id] = job
        asyncio.create_task(_run_generation_job(job_id, generated_file_id, request, _generated_file_record(generated_file)))
        return {"status": "queued", "job": _job_snapshot(job)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("start content generation", exp)


@app.get("/api/generation-jobs/{job_id}")
async def generation_job(job_id: str) -> dict[str, Any]:
    job = GENERATION_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="That generation job was not found. Start generation again to create a new job.")
    return {"job": _job_snapshot(job)}


@app.get("/api/uploaded-files")
async def uploaded_files(email: str = Query(...), limit: int = Query(50, ge=1, le=200)) -> dict[str, Any]:
    try:
        from src import db

        normalized_email = _validate_email(email)
        active_statuses = [
            status.value for status in db.uploaded_files_status if status != db.uploaded_files_status.DELETED
        ]
        df = db.selectFromDB(
            table_name="uploaded_files",
            field_names=["email", "status"],
            field_values=[[normalized_email], active_statuses],
            order_by_field_names=["update_date"],
            order_by_types=["DESC"],
            limit=limit,
        )
        records = _records_from_dataframe(df)
        return {
            "uploaded_files": [_uploaded_file_record(record) for record in records],
            "uploaded_documents": [_uploaded_document(record) for record in records],
        }
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("load uploaded files", exp)


@app.post("/api/generated-files")
async def create_generated_file(request: GeneratedFileRequest) -> dict[str, Any]:
    try:
        from src import db

        email = _validate_email(request.email) if request.email else ""
        session = request.session.strip()
        if not session:
            raise HTTPException(status_code=400, detail="A session is required to save a file.")
        file_name = request.file_name.strip()
        if not file_name:
            raise HTTPException(status_code=400, detail="File name is required.")

        if email:
            if request.settings_id is None:
                raise HTTPException(status_code=400, detail="Settings id is required for signed-in users.")
            settings = db.selectFromDB(
                table_name="settings",
                field_names=["id", "email", "session"],
                field_values=[[request.settings_id], [email], [session]],
                limit=1,
            )
            if not _records_from_dataframe(settings):
                raise HTTPException(status_code=404, detail="Settings row was not found for this session.")

        valid_architectures = {item.value for item in db.generated_files_ai_architecture}
        if request.ai_architecture not in valid_architectures:
            raise HTTPException(status_code=400, detail="Invalid AI architecture.")

        now = datetime.now()
        inserted_ids = db.insertIntoDB(
            table_name="generated_files",
            field_names=[
                "email",
                "session",
                "file_name",
                "status",
                "settings_id",
                "ai_architecture",
                "create_date",
                "update_date",
            ],
            field_values=[
                [email],
                [session],
                [file_name],
                [db.generated_files_status.CREATED.value],
                [request.settings_id],
                [request.ai_architecture],
                [now],
                [now],
            ],
        )
        generated_file = {
            "id": inserted_ids[0] if inserted_ids else None,
            "email": email,
            "session": session,
            "file_name": file_name,
            "status": db.generated_files_status.CREATED.value,
            "settings_id": request.settings_id,
            "ai_architecture": request.ai_architecture,
            "create_date": now,
            "update_date": now,
        }
        return {"status": "saved", "generated_file": _jsonable(generated_file)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("save generated file", exp)


@app.patch("/api/generated-files/{generated_file_id}")
async def update_generated_file(generated_file_id: int, request: GeneratedFileUpdateRequest) -> dict[str, Any]:
    try:
        from src import db

        file_name = request.file_name.strip()
        if not file_name:
            raise HTTPException(status_code=400, detail="File name is required.")

        existing = db.selectFromDB(
            table_name="generated_files",
            field_names=["id"],
            field_values=[[generated_file_id]],
            limit=1,
        )
        if not _records_from_dataframe(existing):
            raise HTTPException(status_code=404, detail="Generated file was not found.")

        now = datetime.now()
        db.updateDB(
            table_name="generated_files",
            update_fields=["file_name", "update_date"],
            update_values=[file_name, now],
            select_fields=["id"],
            select_values=[[generated_file_id]],
        )
        updated = db.selectFromDB(
            table_name="generated_files",
            field_names=["id"],
            field_values=[[generated_file_id]],
            limit=1,
        )
        records = _records_from_dataframe(updated)
        return {"status": "saved", "generated_file": _generated_file_record(records[0])}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("update generated file", exp)


@app.get("/api/ai/models")
async def ai_models() -> dict[str, Any]:
    try:
        from src.ai.llms import extractAvailableLLMs

        default_model = _required_default_model()
        models = extractAvailableLLMs()
        return {"models": _jsonable(models), "default_model": default_model}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("load AI models", exp)


@app.post("/api/ai/outline")
async def create_outline(request: OutlineRequest) -> dict[str, Any]:
    try:
        from src.ai.architecture import OutlineCreatorArchitecture

        ref_dir = Path(request.dir_path_ref_files) if request.dir_path_ref_files else None
        architecture = OutlineCreatorArchitecture(
            model_name=_model_name(request.model_name),
            temperature=request.temperature,
            instructions=request.instructions,
            dir_path_ref_files=ref_dir,
        )
        response = await architecture.ainvoke(_outline_state(query=request.query))
        return {"result": _jsonable(response)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("create outline", exp)


@app.post("/api/ai/outline/format")
async def format_outline(request: OutlineFormatRequest) -> dict[str, Any]:
    try:
        from src.ai.architecture import OutlineFormatterArchitecture

        architecture = OutlineFormatterArchitecture(
            model_name=_model_name(request.model_name),
            temperature=request.temperature,
            instructions=request.instructions,
        )
        response = await architecture.ainvoke(
            _outline_state(query=request.query, outline_unstructured=request.outline_unstructured)
        )
        return {"result": _jsonable(response)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("format outline", exp)


@app.post("/api/ai/content")
async def write_content(request: ContentRequest) -> dict[str, Any]:
    try:
        from src.ai.architecture import ContentWriterArchitecture

        architecture = ContentWriterArchitecture(
            model_name=_model_name(request.model_name),
            temperature=request.temperature,
            instructions=request.instructions,
            type=request.architecture_type,
            collection_name=request.collection_name,
            collection_name_lit_search=request.collection_name_lit_search,
        )
        response = await architecture.ainvoke(_content_state(request))
        return {"result": _jsonable(response)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("write content", exp)


@app.post("/api/ai/abstract/detect")
async def detect_abstract(request: AbstractDetectorRequest) -> dict[str, Any]:
    try:
        from src.ai.architecture import AbstractSectionDetectorArchitecture

        architecture = AbstractSectionDetectorArchitecture(
            model_name=_model_name(request.model_name),
            temperature=request.temperature,
            instructions=request.instructions,
        )
        state = _content_state(ContentRequest(current_section=request.current_section))
        response = await architecture.ainvoke(state)
        return {"result": _jsonable(response)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("detect abstract section", exp)


@app.post("/api/ai/abstract/write")
async def write_abstract(request: AbstractWriterRequest) -> dict[str, Any]:
    try:
        from src.ai.architecture import AbstractWriterArchitecture

        architecture = AbstractWriterArchitecture(
            model_name=_model_name(request.model_name),
            temperature=request.temperature,
            instructions=request.instructions,
        )
        state = _content_state(
            ContentRequest(
                current_section=request.current_section,
                content_pre=request.content_pre,
                content_specific_instructions=request.content_specific_instructions,
            )
        )
        response = await architecture.ainvoke(state)
        return {"result": _jsonable(response)}
    except HTTPException:
        raise
    except Exception as exp:
        raise _api_error("write abstract", exp)


@app.get("/api/db/tables")
async def db_tables() -> dict[str, Any]:
    try:
        from src import db

        return {"tables": sorted(db.tables.keys())}
    except Exception as exp:
        raise _api_error("load database tables", exp)


@app.post("/api/db/select")
async def select_from_db(request: DBSelectRequest) -> dict[str, Any]:
    try:
        from src import db

        df = db.selectFromDB(
            table_name=request.table_name,
            field_names=request.field_names,
            field_values=request.field_values,
            order_by_field_names=request.order_by_field_names,
            order_by_types=request.order_by_types,
            limit=request.limit,
        )
        return {"rows": _records_from_dataframe(df)}
    except Exception as exp:
        raise _api_error("select from database", exp)


@app.post("/api/db/insert")
async def insert_into_db(request: DBInsertRequest) -> dict[str, Any]:
    try:
        from src import db

        inserted_ids = db.insertIntoDB(
            table_name=request.table_name,
            field_names=request.field_names,
            field_values=request.field_values,
        )
        return {"inserted_ids": _jsonable(inserted_ids)}
    except Exception as exp:
        raise _api_error("insert into database", exp)


@app.patch("/api/db/update")
async def update_db(request: DBUpdateRequest) -> dict[str, str]:
    try:
        from src import db

        db.updateDB(
            table_name=request.table_name,
            update_fields=request.update_fields,
            update_values=request.update_values,
            select_fields=request.select_fields,
            select_values=request.select_values,
        )
        return {"status": "updated"}
    except Exception as exp:
        raise _api_error("update database", exp)


@app.post("/api/vector-db/collections")
async def create_vector_collection(request: VectorCollectionRequest) -> dict[str, str]:
    try:
        from src.vectordb import ChromaDB

        vector_db = ChromaDB(embedding=request.embedding)
        vector_db.create(request.collection_name, delete_if_exists=request.delete_if_exists)
        return {"status": "created", "collection_name": request.collection_name}
    except Exception as exp:
        raise _api_error("create vector collection", exp)


@app.delete("/api/vector-db/collections/{collection_name}")
async def delete_vector_collection(collection_name: str) -> dict[str, str]:
    try:
        from src.vectordb import deleteCollection

        deleteCollection(collection_name)
        return {"status": "deleted", "collection_name": collection_name}
    except Exception as exp:
        raise _api_error("delete vector collection", exp)


@app.post("/api/vector-db/query")
async def query_vector_collection(request: VectorQueryRequest) -> dict[str, Any]:
    try:
        from src.vectordb import ChromaDB

        vector_db = ChromaDB(embedding=request.embedding)
        vector_db.get(request.collection_name, is_graph=request.is_graph)
        documents = vector_db.invoke(request.query)
        return {"documents": _jsonable(documents)}
    except Exception as exp:
        raise _api_error("query vector collection", exp)


@app.post("/api/vector-db/ingest-paths")
async def ingest_vector_paths(request: VectorPathIngestRequest) -> dict[str, Any]:
    try:
        from src.vectordb import ChromaDB, getLoader

        vector_db = ChromaDB(embedding=request.embedding)
        vector_db.create(request.collection_name)
        docs = []
        for file_path in request.file_paths:
            docs.extend(list(getLoader(Path(file_path))))
        vector_db.add(
            docs,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            is_graph=request.is_graph,
        )
        return {"status": "ingested", "documents_loaded": len(docs)}
    except Exception as exp:
        raise _api_error("ingest vector paths", exp)


@app.post("/api/vector-db/collections/{collection_name}/documents")
async def ingest_uploaded_documents(
    collection_name: str,
    files: list[UploadFile] = File(...),
    embedding: str = Query("text-embedding-3-large"),
    chunk_size: int = Query(1000, ge=1),
    chunk_overlap: int = Query(200, ge=0),
    is_graph: bool = Query(False),
) -> dict[str, Any]:
    try:
        from src.vectordb import ChromaDB, getLoader

        vector_db = ChromaDB(embedding=embedding)
        vector_db.create(collection_name)
        docs = []
        with tempfile.TemporaryDirectory(prefix="discourse2draft-upload-") as temp_dir:
            temp_path = Path(temp_dir)
            for upload in files:
                file_path = temp_path / Path(upload.filename or "document").name
                with file_path.open("wb") as output:
                    shutil.copyfileobj(upload.file, output)
                docs.extend(list(getLoader(file_path)))
        vector_db.add(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap, is_graph=is_graph)
        return {"status": "ingested", "documents_loaded": len(docs), "collection_name": collection_name}
    except Exception as exp:
        raise _api_error("ingest uploaded documents", exp)


frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8012, reload=True)
