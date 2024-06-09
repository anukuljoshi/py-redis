import socket
import threading
from argparse import ArgumentParser
from typing import Any, List

from app.commands import Command
from parser.parser import RESPParser


def handle_command_action(parser: RESPParser, commands: List[Any]):
    """
    helper function to generate response for a command
    """

    command = commands[0]
    args = commands[1:]

    # TODO: remove after testing
    print("command", command)
    print("args", args)

    func = Command.get_action(command)
    response = func(parser, *args)
    return response


def handle_request(connection: socket.SocketType, parser: RESPParser):
    args_string = connection.recv(1024)

    commands = parser.decode_command(args_string)
    response = handle_command_action(
        parser, commands
    )

    connection.sendall(response)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        type=int,
        help="Port Number",
        default=6379
    )
    args = parser.parse_args()

    PORT = args.port

    # TODO: remove after testing
    print(f"Starting Server at localhost:{PORT}")

    server_socket = socket.create_server(("localhost", PORT), reuse_port=True)
    resp_parser = RESPParser()

    while True:
        connection, _ = server_socket.accept()
        threading.Thread(
            target=lambda: handle_request(connection, resp_parser)
        ).start()


if __name__ == "__main__":
    main()
