"""Locate test fixtures whether the package lives inside the docling repository
or has been extracted somewhere else (e.g. unpacked on a Jetson)."""

from pathlib import Path

DATA = Path(__file__).parent / "data"
TRIAL = DATA / "sertraline_trial.md"

_DOCLAYNET_NAME = "2206.01062.json"


def _docling_article() -> Path:
    """A real Docling export of a PDF article, bundled or taken from the repo."""
    bundled = DATA / _DOCLAYNET_NAME
    if bundled.is_file():
        return bundled
    return (
        Path(__file__).resolve().parents[3]
        / "tests"
        / "data"
        / "pdf"
        / "groundtruth"
        / _DOCLAYNET_NAME
    )


DOCLING_ARTICLE = _docling_article()
