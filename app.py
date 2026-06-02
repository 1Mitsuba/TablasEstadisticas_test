from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from statistics_logic import calculate_frequency_table, parse_numbers


ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"


class StatisticsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/":
            self.path = "/index.html"
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/calculate":
            self.send_error(404, "Ruta no encontrada")
            return

        try:
            payload = self._read_json()
            values = parse_numbers(str(payload.get("data", "")))
            technique = str(payload.get("technique", "simple"))
            k_value = payload.get("k")
            arbitrary_k = int(k_value) if k_value not in (None, "") else None
            result = calculate_frequency_table(values, technique, arbitrary_k)
            self._send_json({"ok": True, "result": result})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=400)

    def _read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(raw_body or "{}")

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = _create_server()
    host, port = server.server_address
    print(f"Servidor iniciado en http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Servidor detenido correctamente", flush=True)
        server.server_close()


def _create_server() -> ThreadingHTTPServer:
    for port in range(8000, 8011):
        try:
            return ThreadingHTTPServer(("localhost", port), StatisticsHandler)
        except OSError:
            continue
    raise OSError("No se encontro un puerto disponible entre 8000 y 8010.")


if __name__ == "__main__":
    main()
