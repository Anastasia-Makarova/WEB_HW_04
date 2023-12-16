from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse # маршрутизация
import mimetypes # работа с css, jpg etc.
from datetime import datetime
from threading import Thread
import pathlib
import json
import socket


BASE_DIR = pathlib.Path(__file__).resolve().parent
UDP_IP = '127.0.0.1'
UDP_PORT = 5000


class HTTPHandler (BaseHTTPRequestHandler):



    def do_POST(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = UDP_IP, UDP_PORT

        body = self.rfile.read(int(self.headers["Content-Length"]))

        sock.sendto(body, server)
        print(f"Data sent to UDP server: {body}")

        sock.close()
        
        #redirect to main
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


def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            data = urllib.parse.unquote_plus(data.decode())
            print(f"Data received: {data}")
            payload = { str(datetime.now()): {key: value for key, value in [el.split("=") for el in data.split("&")]} } 
            
            with open(BASE_DIR.joinpath("storage/data.json"), "a", encoding="utf-8") as datafile:
                json.dump(payload, datafile, ensure_ascii=False) 

            print(f"Data received and processed: {payload}")

    except KeyboardInterrupt:
        print(f'Stop server')

    finally:
        sock.close()


def run(server=HTTPServer, handler=HTTPHandler):
    address = ("127.0.0.1", 3000)
    http_server = server(address, handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()



if __name__ == "__main__":
    
    thread_1 = Thread(target=run_server, args=(UDP_IP, UDP_PORT))
    thread_1.start()
    thread_2 = Thread(target=run, args=())
    thread_2.start()
    thread_1.join()
    thread_2.join()
