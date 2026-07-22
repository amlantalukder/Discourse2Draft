from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.common import rawCiteContent  # noqa: E402


def testRawCiteContentConvertsCitationRange():

    content = 'Generated text [<a href="#:~:text=References">1-3</a>].'
    attached_references_db = {
        "ref_alpha": "Reference Alpha",
        "ref_beta": "Reference Beta",
        "ref_gamma": "Reference Gamma",
    }
    attached_reference_list_from_content = [
        "Reference Alpha",
        "Reference Beta",
        "Reference Gamma",
    ]

    raw_content = rawCiteContent(
        content,
        attached_reference_list_from_content,
        attached_references_db,
    )

    assert raw_content == "Generated text [CITE(ref_alpha), CITE(ref_beta), CITE(ref_gamma)]."


def testRawCiteContentConvertsSingleAndGroupedCitations():

    content = (
        'Generated text [<a href="#:~:text=References">1</a>] '
        'with related work [<a href="#:~:text=References">1, 3</a>].'
    )
    attached_references_db = {
        "ref_alpha": "Reference Alpha",
        "ref_beta": "Reference Beta",
        "ref_gamma": "Reference Gamma",
    }
    attached_reference_list_from_content = [
        "Reference Alpha",
        "Reference Beta",
        "Reference Gamma",
    ]

    raw_content = rawCiteContent(
        content,
        attached_reference_list_from_content,
        attached_references_db,
    )

    assert raw_content == (
        "Generated text [CITE(ref_alpha)] "
        "with related work [CITE(ref_alpha), CITE(ref_gamma)]."
    )
