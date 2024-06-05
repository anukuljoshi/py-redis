import socket
import threading

from app.commands import Command
from parser.parser import RESPParser


def handle_request(connection, parser):
    args_string = connection.recv(1024)

    commands = parser.decode(args_string)

    command = commands[0]
    args = commands[1:]

    # TODO: remove after testing
    print("command", command)
    print("args", args)

    func = Command.get_action(command)
    response = func(parser, *args)

    connection.sendall(response)


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    resp_parser = RESPParser()

    while True:
        connection, _ = server_socket.accept()
        threading.Thread(target=lambda: handle_request(connection, resp_parser)).start()


if __name__ == "__main__":
    main()
