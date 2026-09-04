import threading
import urllib.request
from pathlib import Path

import pytest
from article_infographic.server import make_server

TRIAL = Path(__file__).parent / "data" / "sertraline_trial.md"


@pytest.fixture
def server(tmp_path):
    srv = make_server("127.0.0.1", 0, tmp_path, backend="heuristic", language="en")
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv, f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def _multipart(
    fields: dict[str, str], filename: str, content: bytes
) -> tuple[bytes, str]:
    boundary = "----articleinfographic"
    body = b""
    for name, value in fields.items():
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
    body += (
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: text/markdown\r\n\r\n"
        ).encode()
        + content
        + f"\r\n--{boundary}--\r\n".encode()
    )
    return body, f"multipart/form-data; boundary={boundary}"


def test_upload_builds_infographic_and_serves_it(server):
    srv, base = server
    body, ctype = _multipart(
        {"backend": "heuristic", "lang": "en"}, "trial.md", TRIAL.read_bytes()
    )
    request = urllib.request.Request(
        f"{base}/build", data=body, headers={"Content-Type": ctype}, method="POST"
    )
    with urllib.request.urlopen(
        request
    ) as response:  # follows the redirect to the poster
        assert response.status == 200
        html = response.read().decode("utf-8")
    assert "Sertraline versus placebo" in html and "<svg" in html
    with urllib.request.urlopen(f"{base}/api/list") as response:
        listing = response.read().decode("utf-8")
    assert "trial.infographic.html" in listing
    with urllib.request.urlopen(f"{base}/") as response:
        assert "trial.infographic.html" in response.read().decode("utf-8")


def test_unsupported_upload_is_rejected(server):
    _, base = server
    body, ctype = _multipart({}, "evil.exe", b"MZ")
    request = urllib.request.Request(
        f"{base}/build", data=body, headers={"Content-Type": ctype}, method="POST"
    )
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        urllib.request.urlopen(request)
    assert excinfo.value.code == 400
