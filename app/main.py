import socket
import threading
from argparse import ArgumentParser
from typing import Any, List

from app.commands import ActionGenerator
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


def handle_request(connection: socket.SocketType):
    args_string = connection.recv(1024)

    # get parser object from config
    parser = Config.get(Config.Keys.PARSER)

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
    parser.add_argument(
        "--replicaof",
        dest="replicaof",
        type=str,
        help="Address and port of the master server",
        default=""
    )
    args = parser.parse_args()

    PORT = args.port
    replicaof = args.replicaof

    if replicaof != "":
        Info.set(Info.Keys.ROLE, "slave")

    # TODO: remove after testing
    print(f"Starting {Info.get(Info.Keys.ROLE)} Server at localhost:{PORT}")

    server_socket = socket.create_server(("localhost", PORT), reuse_port=True)

    while True:
        connection, _ = server_socket.accept()
        threading.Thread(
            target=lambda: handle_request(connection)
        ).start()


if __name__ == "__main__":
    main()
