import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from Dialogue.trace import get_events_since, trace_enabled


HTML_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>World Dialogue Trace Viewer</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 16px; background: #0f172a; color: #e2e8f0; }
      h1 { font-size: 18px; margin-bottom: 12px; }
      .event { background: #1e293b; border: 1px solid #334155; padding: 12px; margin-bottom: 12px; border-radius: 8px; }
      .node { font-weight: bold; color: #38bdf8; }
      .time { color: #94a3b8; font-size: 12px; }
      pre { white-space: pre-wrap; word-break: break-word; background: #0b1220; padding: 8px; border-radius: 6px; }
      .state-key { color: #facc15; }
    </style>
  </head>
  <body>
    <h1>World Dialogue Trace Viewer</h1>
    <div id="events"></div>
    <script>
      let lastId = 0;
      const eventsEl = document.getElementById("events");

      function renderEvent(event) {
        const wrapper = document.createElement("div");
        wrapper.className = "event";
        const time = new Date(event.timestamp * 1000).toLocaleTimeString();
        wrapper.innerHTML = `
          <div class="node">${event.node}</div>
          <div class="time">${time}</div>
          <pre>${JSON.stringify(event.state, null, 2)}</pre>
        `;
        eventsEl.prepend(wrapper);
      }

      async function poll() {
        const resp = await fetch(`/events?since=${lastId}`);
        const data = await resp.json();
        data.events.forEach(renderEvent);
        lastId = data.next_id;
        setTimeout(poll, 1000);
      }

      poll();
    </script>
  </body>
</html>
"""


class TraceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/events"):
            if not trace_enabled():
                self._send_json({"events": [], "next_id": 0})
                return
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            since = int(params.get("since", ["0"])[0])
            events, next_id = get_events_since(since)
            self._send_json({"events": events, "next_id": next_id})
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def log_message(self, format, *args):  # noqa: N802
        return

    def _send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_trace_server(port: int = 8765) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", port), TraceHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
