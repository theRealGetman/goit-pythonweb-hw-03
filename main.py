from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import pathlib
import urllib.parse
from jinja2 import Environment, FileSystemLoader


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("./pages/index.html")
        elif pr_url.path == "/message":
            self.send_html_file("./pages/message.html")
        elif pr_url.path == "/read":
            self.send_messages_page()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("./pages/error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        self.append_messages(data_dict)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def append_messages(self, message):
        file_path = "storage/data.json"

        with open(file_path, "r") as file:
            messages = json.load(file)
            print(messages)

        print(message)
        messages[str(datetime.now())] = message
        print(messages)

        with open(file_path, "w") as file:
            json.dump(messages, file, indent=4)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def send_messages_page(self):
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("./templates/read.html")
        with open("storage/data.json", "r") as file:
            messages = json.load(file)
        output = template.render(messages=messages)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(output.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
