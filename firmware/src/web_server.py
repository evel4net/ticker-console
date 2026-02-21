import asyncio
import json

from src.session_manager import SessionManager, UnauthorizedAccessException
from src.task import Task
from src.repository import Repository
from src.config_private import IP, PORT, SERVER_PRIV_PATH, SERVER_PUB_PATH
import src.utilities as utilities
from src.cipher import Cipher

class WebServer(object):
    def __init__(self, repository: Repository) -> None:
        self.__repository = repository
        self.__server = None
        self.__session_manager = SessionManager()
        self.__cipher = Cipher(SERVER_PRIV_PATH, SERVER_PUB_PATH)

        self.__handlers = {("POST", "/task"): self.handle_add_task, ("PATCH", "/task"): self.handle_update_task,
                    ("DELETE", "/task"): self.handle_delete_task, ("GET", "/task"): self.handle_get_task,
                    ("GET", "/tasks"): self.handle_get_tasks, ("GET", "/tasks/day"): self.handle_get_tasks_by_day,
                    ("POST", "/login"): self.handle_login, ("DELETE", "/signout"): self.handle_signout}

    """ ---------- SERVER ---------- """
    # - create socket, accept connection, receive request, decrypt body, get handler to execute from ROUTER, send response encrypted back to client

    async def start_server(self) -> None:
        print("Web server starting...")

        self.__server = await asyncio.start_server(self.manage_client, IP, PORT)

        print("Waiting for clients...")

    async def stop_server(self): # TODO shutdown server when pressing shutdown button (to add)
        print("Server stopping...")

        self.__server.close()
        await self.__server.wait_closed()

    async def manage_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        request_line, headers, request_body = await self.receive_request(reader)
        print(request_line)

        request_args = request_line.split(" ")
        method = request_args[0]
        path = request_args[1].split(IP)[1].strip()

        print(method, path, request_body)
        is_signout_request = True
        session_id = ""

        try:
            handler = self.route(method, path)
            is_login_request = True

            token = ""
            if handler != self.handle_login:
                is_login_request = False

                found_token = False
                found_session_id = False
                for header in headers:
                    if header.lower().startswith("x-pico-token:"):
                        token = header.split(":", 1)[1].strip()
                        self.__session_manager.validate_token(token)
                        found_token = True

                    if header.lower().startswith("x-session-id:"):
                        session_id = header.split(":", 1)[1].strip()
                        found_session_id = True

                    if found_token and found_session_id:
                        break

            if handler != self.handle_signout:
                is_signout_request = False

            body, session_id = self.__cipher.decrypt_request(request_body, session_id, is_login_request)

            status, response, rotate_token = handler(body)
            custom_headers = None

            if rotate_token:
                custom_headers = {"X-Pico-Token": self.__session_manager.rotate_token(token)}

            if handler == self.handle_login:
                response["session"] = session_id
        except UnauthorizedAccessException as e:
            status = 401
            response = {"status": str(e)}
            custom_headers = None
        except Exception as e:
            is_signout_request = False
            status = 404
            response = {"error": str(e)}
            custom_headers = None

        await self.send_response(writer, status, self.__cipher.encrypt_response(response, session_id, is_signout_request), custom_headers)

    async def receive_request(self, reader: asyncio.StreamReader) -> tuple[str, list[str], dict]:
        data = b""

        # --- receive request line and headers until "\r\n\r\n" received
        while b"\r\n\r\n" not in data:
            chunk = await reader.read(1024)

            if not chunk:
                break

            data += chunk

        # --- find length of content/body
        request_line_and_headers, body = data.split(b"\r\n\r\n", 1)
        request_line_and_headers = request_line_and_headers.decode().split("\r\n", 1)

        request_line = request_line_and_headers[0]
        headers = request_line_and_headers[1].split("\r\n")

        body_length = 0

        for header in headers:
            if header.lower().startswith("content-length:"):
                body_length = int(header.split(":", 1)[1])
                break

        # --- receive the rest of the body
        while len(body) < body_length:
            body += await reader.readexactly(body_length - len(body))

        if len(body) == 0:
            body = "{}"
        else:
            body = body.decode()

        return request_line, headers, json.loads(body)

    async def send_response(self, writer: asyncio.StreamWriter, status: int, response: dict, custom_headers: dict = None) -> None:
        response_str = json.dumps(response)

        response_msg = (f"HTTP/1.1 {status} OK\r\n"
                "Server: RaspberryPi Pico 2W\r\n")

        if custom_headers:
            for header, value in custom_headers.items():
                response_msg += f"{header}: {value}\r\n"

        response_msg += (f"Content-Length: {len(response_str)}\r\n"
                "Content-Type: application/json\r\n"
                "Connection: close\r\n"
                "\r\n")

        writer.write(response_msg.encode())
        writer.write(response_str.encode())

        await writer.drain()
        await writer.wait_closed()

        print("Response sent. Connection closed.")

    """ ---------- ROUTER ---------- """
    # - receive method and path, return corresponding handler to server

    def route(self, method, path) -> str:
        if (method, path) in self.__handlers:
            return self.__handlers.get((method, path))

        raise Exception("Request not found.")

    """ ---------- HANDLERS ---------- """
    # - method for login, sign-out, get, add, update, delete, validate input and return status and object

    """ POST /login """
    def handle_login(self, request_body: dict):
        # body: {"username": "encrypted username", "password": "encrypted password"}

        token = self.__session_manager.create_session(request_body["username"], request_body["password"])

        return 200, {"token":  token}, False

    """ DELETE /signout """
    def handle_signout(self, request_body: dict):
        return 200, {"status": "Sign out successful."}, False

    """ POST /task """
    def handle_add_task(self, request_body: str):
        # body: {"description": "description", "start_date": "dd_mm_yyyyy", "end_date": "dd_mm_yyyyy"}

        new_task = Task(request_body["description"], utilities.date_str_to_tuple(request_body["start_date"]), utilities.date_str_to_tuple(request_body["end_date"]))
        self.__repository.add_task(new_task)

        return 201, {"status": "Task added."}, True

    """ PATCH /task """
    def handle_update_task(self, request_body: dict):
        # body: {"id": "id", "?description": "new description", "?start_date": "dd_mm_yyyyy", "?end_date": "dd_mm_yyyyy"}

        task_id = request_body["id"]

        new_description = request_body.get("description")

        new_start_date = request_body.get("start_date")
        if new_start_date is not None:
            new_start_date = utilities.date_str_to_tuple(new_start_date)

        new_end_date = request_body.get("end_date")
        if new_end_date is not None:
            new_end_date = utilities.date_str_to_tuple(new_end_date)

        self.__repository.update_task(task_id, new_description, new_start_date, new_end_date)

        return 200, {"status": "Task updated."}, True

    """ DELETE /task """
    def handle_delete_task(self, request_body: dict):
        # body: {"id": "id"}

        task_id = request_body["id"]
        self.__repository.remove_task(task_id)

        return 200, {"status": "Task deleted."}, True

    """ GET /task """
    def handle_get_task(self, request_body: dict):
        # body: {"id": "id"}

        id = request_body["id"]
        task = self.__repository.get_task(id)

        return 200, task.to_json(), True

    """ GET /tasks """
    def handle_get_tasks(self, request_body: dict):
        # body: {}
        # response: {"task_id": {task_json}} -- return all tasks in memory, without the status

        tasks = self.__repository.get_all_tasks()
        tasks_json = {}

        for id, task in tasks.items():
            tasks_json[id] = task.to_json()

        return 200, tasks_json, True

    """ GET /tasks/day """
    def handle_get_tasks_by_day(self, request_body: dict):
        # body: {"day": "dd_mm_yyyy"}
        # response: {"id": {task json, "is_finished": bool}} -- return all tasks by date, with the status

        tasks = self.__repository.get_all_tasks_by_day(utilities.date_str_to_tuple(request_body["day"]))
        tasks_json = {}

        for task, is_finished in tasks:
            task_json = task.to_json()
            task_json["is_finished"] = is_finished

            tasks_json[task.id] = task_json

        return 200, tasks_json, True