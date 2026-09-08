# TaskFlow — minimal sample task server (stdlib only, no dependencies).
# Run:  python3 backend/server.py    then visit  http://localhost:8000/tasks
# Returns a JSON array of sample tasks at /tasks; any other path returns 404.
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

TASKS = [
    {"id": 1, "title": "Design authentication flow", "status": "To Do"},
    {"id": 2, "title": "Build task board API", "status": "In Progress"},
    {"id": 3, "title": "Write endpoint tests", "status": "Review"},
    {"id": 4, "title": "Set up CI pipeline", "status": "Done"},
]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/tasks":
            body = json.dumps(TASKS).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not Found")


if __name__ == "__main__":
    print("Serving on http://localhost:8000/tasks")
    HTTPServer(("", 8000), Handler).serve_forever()
