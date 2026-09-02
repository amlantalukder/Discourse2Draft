from typing import Any
from pathlib import Path
from uuid import uuid4
import json
import logging

from .. import db
from app_utils import (
    GeneratedFileRequest,
    _active_literature_collection,
    _active_uploaded_files_collection_record,
    _create_literature_collection,
    _generated_file_by_id,
    _handle_create_generated_file,
    _jsonable,
    _outline_file_path,
    _process_outline,
    _reset_outline_generated_content,
    _set_generated_file_status,
    _write_manuscript_content_from_outline,
    _write_outline_file,
)


# -----------------------------------------------------------------------
def _load_eval_outline(gen_outline_file_path: Path) -> dict[str, Any]:

    if gen_outline_file_path.suffix.lower() == ".json":
        with gen_outline_file_path.open() as fp:
            outline_data = json.load(fp)
        if not isinstance(outline_data, dict):
            raise ValueError(f"Expected {gen_outline_file_path} to contain a JSON object outline.")
        _reset_outline_generated_content(outline_data)
        return outline_data

    return _process_outline(gen_outline_file_path.read_text())


# -----------------------------------------------------------------------
async def _create_eval_generated_file_with_literature_collection(gen_model_name: str, gen_outline_file_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:

    eval_session = f"eval:{gen_model_name}:{gen_outline_file_path.stem}:{uuid4().hex}"
    response = await _handle_create_generated_file(
        GeneratedFileRequest(
            session=eval_session,
            file_name=gen_outline_file_path.name,
            ai_architecture=db.generated_files_ai_architecture.RAG.value,
        )
    )
    generated_file = response.get("generated_file") or {}
    if not generated_file.get("id"):
        raise RuntimeError("Could not create an eval generated file row.")
    gen_file_id = int(generated_file["id"])
    _set_generated_file_status(gen_file_id, db.generated_files_status.RUNNING.value)
    generated_file = {**generated_file, "status": db.generated_files_status.RUNNING.value}
    literature_collection = _create_literature_collection(generated_file)
    return generated_file, literature_collection


# -----------------------------------------------------------------------
async def generateContentByLitSearchAsync(
        gen_model_name: str,
        gen_outline_file_path: Path,
        gen_file_id: int | None = None
    ) -> tuple[int, int | None, int | None]:

    '''
    Runs Discourse2Draft Literature Search with the provided base model name to generated content for a provided outline file
    Arguments:
        gen_model_name: Base model name used by Discourse2Draft
        gen_outline_file_path: File path of the outline file
        gen_file_id: Existing generated file id to resume. If omitted, a new generated file is created.
    Returns: Generated file id, uploaded-files vector DB collection id, literature vector DB collection id
    '''

    gen_outline_file_path = Path(gen_outline_file_path)
    mode = "remaining"

    if gen_file_id is None:
        outline_data = _load_eval_outline(gen_outline_file_path)
        generated_file, literature_collection = await _create_eval_generated_file_with_literature_collection(
            gen_model_name,
            gen_outline_file_path,
        )
        gen_file_id = int(generated_file["id"])
        collection_name = str(literature_collection["collection_name"])
        _write_outline_file(gen_file_id, _jsonable(outline_data))
        mode = "restart"
    else:
        gen_file_id = int(gen_file_id)
        generated_file = _generated_file_by_id(gen_file_id, require_owner=False)
        literature_collection = _active_literature_collection(gen_file_id)
        if literature_collection is None:
            raise ValueError(
                f"Generated file {gen_file_id} does not have an active literature search collection to resume."
            )
        collection_name = str(literature_collection["collection_name"])

    generated_file = {
        **generated_file,
        "ai_architecture": db.generated_files_ai_architecture.RAG.value,
    }
    uploaded_files_collection = _active_uploaded_files_collection_record(gen_file_id)
    vector_db_collections_id_uploaded_files = (
        int(uploaded_files_collection["id"]) if uploaded_files_collection else None
    )
    vector_db_collections_id_literature = int(literature_collection["id"])
    output_path = _outline_file_path(gen_file_id)

    try:
        logging.info(
            "Evaluation generation %s will write to %s",
            gen_file_id,
            output_path,
        )
        await _write_manuscript_content_from_outline(
            gen_file_id,
            generated_file,
            model_name=gen_model_name,
            temperature=0,
            mode=mode,
            architecture_type=db.generated_files_ai_architecture.RAG.value,
            collection_name_lit_search=collection_name,
        )
        return gen_file_id, vector_db_collections_id_uploaded_files, vector_db_collections_id_literature
    except Exception:
        _set_generated_file_status(gen_file_id, db.generated_files_status.ERROR.value)
        raise
