import socket
import json

from src.task import Task
from src.repository import Repository
from src.config_private import IP, PORT
import src.utilities as utilities

class WebServer(object):
    def __init__(self, repository: Repository) -> None:
        self.__repository = repository
        self.__clients = []

        self.__handlers = {("POST", "/tasks/add"): self.handle_add_task, ("PATCH", "/tasks/update"): self.handle_update_task,
                    ("DELETE", "/tasks/delete"): self.handle_delete_task, ("GET", "/tasks"): self.handle_get_tasks,
                    ("GET", "/tasks/get"): self.handle_get_task}

    # SERVER - create socket, accept connection, receive request, get handler to execute from ROUTER, send response back to client

    def start_server(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((IP, PORT))
        server_socket.listen(1)

        print("Waiting for clients...")
        # while True:
        client_socket, client_address = server_socket.accept()
        print(f"New client from: {client_address}")

        self.__clients.append(client_socket)

        self.manage_client(client_socket)

        self.stop_server(server_socket)


    def stop_server(self, server_socket: socket.socket):
        print("Server stopping...")
        server_socket.close()

    def manage_client(self, client_socket: socket.socket) -> None:
        request_line, headers, body = self.receive_request(client_socket)

        request_args = request_line.split(" ")
        method = request_args[0]
        path = request_args[1]

        print(method, path, body)
        try:
            handler = self.route(method, path)

            status, response = handler(body)
        except Exception as e:
            status = 404
            response = {"error": str(e)}

        self.send_response(client_socket, status, response)

        client_socket.close()

    def receive_request(self, client_socket: socket.socket) -> tuple[str, str, str]:
        data = b""

        # --- receive request line and headers until "\r\n\r\n" received
        while b"\r\n\r\n" not in data:
            chunk = client_socket.recv(1024)

            if not chunk:
                break

            data += chunk

        # --- find length of content/body
        request_line_and_headers, body = data.split(b"\r\n\r\n", 1)
        request_line_and_headers = request_line_and_headers.decode().split("\r\n", 1)

        request_line = request_line_and_headers[0]
        headers = request_line_and_headers[1]

        header_lines = headers.split("\r\n")
        body_length = 0

        for header in header_lines:
            if header.lower().startswith("content-length:"):
                body_length = int(header.split(":", 1)[1])
                break

        # --- receive the rest of the body
        while len(body) < body_length:
            chunk = client_socket.recv(1024)

            if not chunk:
                break

            body += chunk

        body = body.decode()

        return request_line, headers, body

    def send_response(self, client_socket: socket.socket, status, response) -> None:
        response_json = json.dumps(response)

        client_socket.send(f"HTTP/1.1 {status} OK\r\n")
        client_socket.send("Server: RaspberryPi Pico 2W\r\n")
        client_socket.send(f"Content-Length: {len(response_json)}\r\n")
        client_socket.send("Content-Type: application/json\r\n")
        client_socket.send("Connection: close\r\n")
        client_socket.send("\r\n")

        client_socket.send(response_json)

        print("Response sent")

    # ROUTER - receive method and path, return corresponding handler to server

    def route(self, method, path) -> str:
        if (method, path) in self.__handlers:
            return self.__handlers.get((method, path))

        raise Exception("Request not found")

    # HANDLERS - method for get, add, update, delete, validate input and return status and object

    def handle_add_task(self, request_body: str):     # POST /tasks/add --> 201
        # body: {"description": "description", "start_date": "dd_mm_yyyyy", "end_date": "dd_mm_yyyyy"}

        add_data = json.loads(request_body)

        print(f"Add task: {add_data}")
        return 200, {"status": "received request"}

        try:
            new_task = Task(add_data["description"], add_data["start_date"], add_data["end_date"])
            self.__repository.add_task(new_task)
        except KeyError:
            raise Exception("Invalid arguments")

        return 201, {"status": "task added"}

    def handle_update_task(self, request_body):  # PATCH /tasks/update
        # body: {"id": "id", "?description": "new description", "?start_date": "dd_mm_yyyyy", "?end_date": "dd_mm_yyyyy"}

        update_data = json.loads(request_body)

        print(f"Update task: {update_data}")
        return 200, {"status": "received request"}

        try:
            id = update_data["id"]
            task = self.__repository.get_task(id)

            if "description" in update_data:
                task.description = update_data["description"]
            if "start_date" in update_data:
                # TODO repo method for update
                task.start_date = utilities.date_str_to_tuple(update_data["start_date"])
            if "end_date" in update_data:
                # TODO repo method for update
                task.end_date = utilities.date_str_to_tuple(update_data["end_date"])
        except KeyError:
            raise Exception("Task not found")

        return 200, {"status": "task updated"}

    def handle_delete_task(self, request_body):  # DELETE /tasks/delete
        # body: {"id": "id"}
        # validate body, check object exists -> else exception
        delete_data = json.loads(request_body)

        print(f"Delete task: {delete_data}")
        return 200, {"status": "received request"}

        try:
            id = delete_data["id"]
            # TODO repo method for delete
        except KeyError:
            raise Exception("Task not found")

        return 200, {"status": "task deleted"}

    def handle_get_tasks(self, request_body):    # GET /tasks
        task_data = json.loads(request_body)

        print(f"Get tasks: {task_data}")
        return 200, {"status": "received request"}

        self.__repository.get_all_tasks() # TODO all tasks or all tasks by day

        return 200, {}

    def handle_get_task(self, request_body):     # GET /tasks/get
        # body: {"id": "id"}

        get_data = json.loads(request_body)

        print(f"Get task: {get_data}")
        return 200, {"status": "received request"}

        try:
            id = get_data["id"]
            self.__repository.get_task(id)
        except KeyError:
            raise Exception("Task not found")

        return 200, {}