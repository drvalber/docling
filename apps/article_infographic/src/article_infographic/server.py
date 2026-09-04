"""Minimal local web app (standard library only).

``GET /``            upload form
``POST /build``      multipart upload -> runs the pipeline -> redirects to the poster
``GET /out/<file>``  serves generated files (HTML, JSON, PDF)
``GET /api/list``    JSON list of generated infographics
"""

from __future__ import annotations

import html
import json
import logging
import re
import threading
from email.parser import BytesParser
from email.policy import default as default_policy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from article_infographic.synthesis.base import BACKENDS

_log = logging.getLogger(__name__)

_ALLOWED_SUFFIXES = {".pdf", ".docx", ".html", ".htm", ".md", ".json", ".pptx", ".xlsx"}

_FORM = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Article Infographic</title>
<style>
body{{font-family:system-ui,sans-serif;background:#f4f4f1;color:#0b0b0b;margin:0}}
main{{max-width:720px;margin:40px auto;padding:0 20px}}
.card{{background:#fcfcfb;border:1px solid rgba(11,11,11,.1);border-radius:14px;padding:24px}}
h1{{margin:0 0 6px;font-size:26px}} p.lead{{color:#52514e;margin-top:0}}
label{{display:block;font-size:13px;color:#52514e;margin:14px 0 4px}}
input,select{{font:inherit;padding:8px 10px;border:1px solid #c3c2b7;border-radius:8px;width:100%;background:#fff}}
button{{font:inherit;margin-top:18px;padding:10px 18px;border-radius:999px;border:0;background:#2a78d6;color:#fff;cursor:pointer}}
.row{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
ul{{padding-left:18px}} li{{margin:4px 0}} small{{color:#898781}}
#busy{{display:none;margin-top:14px;color:#52514e}}
</style></head><body><main>
<div class="card">
<h1>Artigo científico → Infográfico</h1>
<p class="lead">Envie um PDF (ou DOCX/HTML/Markdown/JSON Docling). O Docling extrai a estrutura, o sintetizador escolhido resume e o pôster é gerado em HTML.</p>
<form method="post" action="/build" enctype="multipart/form-data" onsubmit="document.getElementById('busy').style.display='block'">
<label>Arquivo do artigo</label><input type="file" name="file" required accept=".pdf,.docx,.html,.htm,.md,.json">
<div class="row">
<div><label>Sintetizador</label><select name="backend">{backend_options}</select></div>
<div><label>Idioma</label><select name="lang"><option value="pt" {pt}>Português</option><option value="en" {en}>English</option><option value="es" {es}>Español</option></select></div>
</div>
<div class="row">
<div><label>Modelo (opcional)</label><input name="model" placeholder="{model_placeholder}"></div>
<div><label>Host Ollama (opcional)</label><input name="host" placeholder="http://localhost:11434"></div>
</div>
<button type="submit">Gerar infográfico</button>
<div id="busy">Processando… a conversão de um PDF com os modelos de layout pode levar de 30 s a alguns minutos.</div>
</form>
</div>
<div class="card" style="margin-top:16px"><h2 style="font-size:16px;margin:0 0 8px">Infográficos gerados</h2>{listing}</div>
</main></body></html>"""


class InfographicHandler(BaseHTTPRequestHandler):
    output_dir: Path = Path("infographics")
    defaults: dict = {
        "backend": "heuristic",
        "model": None,
        "host": None,
        "language": "pt",
    }
    lock = threading.Lock()

    def log_message(self, fmt, *args):  # route to logging instead of stderr
        _log.info("%s - %s", self.address_string(), fmt % args)

    # -- GET -----------------------------------------------------------------
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(self._form())
        elif parsed.path == "/api/list":
            self._send_json(self._generated())
        elif parsed.path.startswith("/out/"):
            self._serve_output(parsed.path[len("/out/") :])
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    # -- POST ----------------------------------------------------------------
    def do_POST(self) -> None:
        if urlparse(self.path).path != "/build":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        content_type = self.headers.get("Content-Type", "")
        message = BytesParser(policy=default_policy).parsebytes(
            b"Content-Type: "
            + content_type.encode()
            + b"\r\nMIME-Version: 1.0\r\n\r\n"
            + body
        )
        fields: dict[str, str] = {}
        upload_name, upload_bytes = "", b""
        for part in message.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if name == "file":
                upload_name = part.get_filename() or "upload.pdf"
                upload_bytes = part.get_payload(decode=True) or b""
            elif name:
                fields[name] = (
                    (part.get_payload(decode=True) or b"")
                    .decode("utf-8", "replace")
                    .strip()
                )
        if not upload_bytes:
            self.send_error(HTTPStatus.BAD_REQUEST, "no file uploaded")
            return
        safe_name = re.sub(r"[^\w.\-]+", "_", Path(upload_name).name)
        if Path(safe_name).suffix.lower() not in _ALLOWED_SUFFIXES:
            self.send_error(HTTPStatus.BAD_REQUEST, "unsupported file type")
            return
        upload_dir = self.output_dir / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        source = upload_dir / safe_name
        source.write_bytes(upload_bytes)

        from article_infographic.pipeline import build_infographic

        backend = fields.get("backend") or self.defaults["backend"]
        if backend not in BACKENDS:
            self.send_error(HTTPStatus.BAD_REQUEST, "unknown backend")
            return
        try:
            with (
                self.lock
            ):  # Docling models are not meant to run concurrently in one process
                result = build_infographic(
                    source,
                    self.output_dir,
                    backend=backend,
                    model=fields.get("model") or self.defaults["model"],
                    host=fields.get("host") or self.defaults["host"],
                    language=fields.get("lang") or self.defaults["language"],
                )
        except Exception as exc:  # surface the failure in the browser
            _log.exception("build failed")
            self._send_html(
                f"<h1>Falha na geração</h1><pre>{html.escape(str(exc))}</pre><a href='/'>voltar</a>",
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", f"/out/{result.html_path.name}")
        self.end_headers()

    # -- helpers -------------------------------------------------------------
    def _generated(self) -> list[dict[str, str]]:
        items = []
        for path in sorted(
            self.output_dir.glob("*.infographic.html"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        ):
            items.append(
                {
                    "name": path.name,
                    "html": f"/out/{path.name}",
                    "spec": f"/out/{path.with_suffix('.json').name}",
                }
            )
        return items

    def _form(self) -> str:
        options = "".join(
            f'<option value="{b}" {"selected" if b == self.defaults["backend"] else ""}>{b}</option>'
            for b in BACKENDS
        )
        listing = "".join(
            f'<li><a href="{i["html"]}">{html.escape(i["name"])}</a> <small>(<a href="{i["spec"]}">json</a>)</small></li>'
            for i in self._generated()
        )
        lang = self.defaults["language"]
        return _FORM.format(
            backend_options=options,
            listing=f"<ul>{listing}</ul>" if listing else "<small>nenhum ainda</small>",
            model_placeholder="qwen3:8b · claude-opus-5",
            pt="selected" if lang == "pt" else "",
            en="selected" if lang == "en" else "",
            es="selected" if lang == "es" else "",
        )

    def _serve_output(self, name: str) -> None:
        safe = Path(name).name
        path = self.output_dir / safe
        if not path.is_file() or path.suffix not in {".html", ".json", ".pdf"}:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".json": "application/json",
            ".pdf": "application/pdf",
        }[path.suffix]
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self, content: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def make_server(
    bind: str,
    port: int,
    output_dir: Path,
    backend: str = "heuristic",
    model: str | None = None,
    host: str | None = None,
    language: str = "pt",
) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (InfographicHandler,), {})
    handler.output_dir = output_dir
    handler.defaults = {
        "backend": backend,
        "model": model,
        "host": host,
        "language": language,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    return ThreadingHTTPServer((bind, port), handler)


def serve(
    bind: str = "127.0.0.1",
    port: int = 8765,
    output_dir: Path = Path("infographics"),
    **defaults,
) -> None:
    server = make_server(bind, port, output_dir, **defaults)
    _log.info(
        "Article Infographic web app on http://%s:%d (outputs in %s)",
        bind,
        port,
        output_dir,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
