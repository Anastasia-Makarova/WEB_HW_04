from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse # маршрутизация
import mimetypes # работа с css, jpg etc.
from datetime import datetime
import pathlib
import json


BASE_DIR = pathlib.Path(__file__).resolve().parent


class HTTPHandler (BaseHTTPRequestHandler):

    def do_POST(self):
        # self.send_html("message.html")
        body = self.rfile.read(int(self.headers["Content-Length"]))
        body = urllib.parse.unquote_plus(body.decode())
        # body = body.replace("=", "")

        payload = { str(datetime.now()): {key: value for key, value in [el.split("=") for el in body.split("&")]} }
        
    
        with open(BASE_DIR.joinpath("storage/data.json"), "a", encoding="utf-8") as datafile:
            json.dump(payload, datafile, ensure_ascii=False)

        print(payload)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case "/":
                self.send_html("index.html")
            case "/message.html":
                self.send_html("message.html")
            case _:
                file = BASE_DIR/route.path[1:]
                if file.exists():
                    self.send_static(file)
                else:   
                    self.send_html("error.html", 404)
             


    def send_html(self, filename, status_code = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        filepath = BASE_DIR.joinpath(filename).resolve()

        with open (BASE_DIR.joinpath(filepath), "rb") as file:
            self.wfile.write(file.read())


    def send_static(self, filename):
        self.send_response(200)
        mime, *rest = mimetypes.guess_type(filename)
        if mime:
            self.send_header("Content-Type", mime)
        else:
            print("!!!")
            self.send_header("Content-Type", "text/plain")
        self.end_headers()

        filepath = BASE_DIR.joinpath(filename).resolve()

        with open (BASE_DIR.joinpath(filepath), "rb") as file:
            self.wfile.write(file.read())




def run(server=HTTPServer, handler=HTTPHandler):
    address = ("", 3000)
    http_server = server(address, handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()



if __name__ == "__main__":
    
    run()
    # print(BASE_DIR.joinpath("index.html"))