"""Command-line interface.

Examples::

    article-infographic build paper.pdf                       # heuristic, Portuguese
    article-infographic build paper.pdf --backend ollama --model qwen3:8b
    article-infographic build paper.pdf --backend anthropic --lang en --pdf
    article-infographic render paper.infographic.json -o poster.html
    article-infographic serve --port 8765
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from article_infographic.synthesis.base import BACKENDS


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--backend", choices=BACKENDS, default="heuristic", help="content synthesizer"
    )
    parser.add_argument("--model", help="model name for ollama/anthropic backends")
    parser.add_argument("--host", help="Ollama host, e.g. http://jetson:11434")
    parser.add_argument(
        "--lang",
        default="pt",
        choices=["pt", "en", "es"],
        help="language of the poster text",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="article-infographic",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser(
        "build",
        help="convert an article (PDF/DOCX/HTML/MD/Docling JSON) into an infographic",
    )
    build.add_argument("source", type=Path)
    build.add_argument("-o", "--output-dir", type=Path, default=Path("infographics"))
    build.add_argument(
        "--pdf", action="store_true", help="also export a PDF (requires playwright)"
    )
    build.add_argument(
        "--no-extraction", action="store_true", help="do not keep the extraction JSON"
    )
    _add_common(build)

    render = sub.add_parser("render", help="re-render an edited infographic JSON spec")
    render.add_argument("spec", type=Path)
    render.add_argument("-o", "--output", type=Path, required=True)
    render.add_argument("--pdf", action="store_true")

    serve = sub.add_parser("serve", help="run the local web app")
    serve.add_argument("--host-bind", default="127.0.0.1", dest="bind")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("-o", "--output-dir", type=Path, default=Path("infographics"))
    _add_common(serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.command == "build":
        from article_infographic.pipeline import build_infographic

        result = build_infographic(
            args.source,
            args.output_dir,
            backend=args.backend,
            model=args.model,
            host=args.host,
            language=args.lang,
            keep_extraction=not args.no_extraction,
        )
        print(f"HTML : {result.html_path}")
        print(f"Spec : {result.spec_path}")
        if result.extraction_path:
            print(f"Extr.: {result.extraction_path}")
        for warning in result.spec.warnings:
            print(f"warning: {warning}", file=sys.stderr)
        if args.pdf:
            _export_pdf(result.html_path)
        return 0

    if args.command == "render":
        from article_infographic.pipeline import render_from_spec

        html_path = render_from_spec(args.spec, args.output)
        print(f"HTML : {html_path}")
        if args.pdf:
            _export_pdf(html_path)
        return 0

    if args.command == "serve":
        from article_infographic.server import serve

        serve(
            bind=args.bind,
            port=args.port,
            output_dir=args.output_dir,
            backend=args.backend,
            model=args.model,
            host=args.host,
            language=args.lang,
        )
        return 0
    return 1


def _export_pdf(html_path: Path) -> None:
    from article_infographic.pdf_export import html_to_pdf

    pdf_path = html_path.with_suffix(".pdf")
    try:
        html_to_pdf(html_path, pdf_path)
        print(f"PDF  : {pdf_path}")
    except RuntimeError as exc:
        print(f"warning: {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
