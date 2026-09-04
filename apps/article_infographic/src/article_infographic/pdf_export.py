"""Optional PDF export of the rendered poster through a headless Chromium."""

from __future__ import annotations

from pathlib import Path


def html_to_pdf(html_path: Path, pdf_path: Path, page_format: str = "A3") -> Path:
    """Print the HTML poster to PDF with Playwright (``pip install playwright``)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "PDF export needs Playwright: pip install playwright && playwright install chromium. "
            "Alternatively open the HTML in a browser and use Print > Save as PDF."
        ) from exc
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri())
        page.emulate_media(media="print")
        page.pdf(
            path=str(pdf_path),
            format=page_format,
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"},
        )
        browser.close()
    return pdf_path
