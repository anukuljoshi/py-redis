import socket
import threading
from argparse import ArgumentParser
from typing import Any, List

from app.actions import STORE, ActionGenerator
from app.config import Config, Info


def handle_command_action(commands: List[Any]):
    """
    helper function to generate response for a command
    """

    command = commands[0]
    args = commands[1:]

    # TODO: remove after testing
    print("command", command)
    print("args", args)

    func = ActionGenerator.get_action(command)
    response = func(*args)
    return response


def handle_request(connection: socket.socket):

    # get parser object from config
    parser = Config.get(Config.Keys.PARSER)

    with connection:
        connected = True
        while connected:
            args_string = connection.recv(1024)
            connected = bool(args_string)
            if not connected:
                break

            commands = parser.decode_command(args_string)
            response = handle_command_action(commands)

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

    Config.set(Config.Keys.PORT, args.port)

    # TODO: remove after testing
    print(f"Starting {Info.get(Info.Keys.ROLE)} Server at localhost:{Config.get(Config.Keys.PORT)}")

    server_socket = socket.create_server(
        (
            "localhost",
            Config.get(Config.Keys.PORT)
        ),
        reuse_port=True
    )

    while True:
        connection, _ = server_socket.accept()
        threading.Thread(
            target=lambda: handle_request(connection)
        ).start()


if __name__ == "__main__":
    main()
