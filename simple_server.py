from http.server import BaseHTTPRequestHandler, HTTPServer
from text_editor import TextEditor
from database_strategy import PostgreSQLDatabaseStrategy


class SimpleRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        if self.path == '/open_file':
            self.handle_open_file(post_data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def handle_open_file(self, post_data):
        try:
            file_path = post_data.split('=')[1]
            editor.open_file_by_path(file_path)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'File opened successfully')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode('utf-8'))


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleRequestHandler)
    print(f'Starting server on port {port}')
    httpd.serve_forever()


if __name__ == "__main__":
    db_strategy = PostgreSQLDatabaseStrategy()
    editor = TextEditor()
    editor.set_database_strategy(db_strategy)

    run_server()
