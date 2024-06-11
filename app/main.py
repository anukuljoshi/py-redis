import socket
import threading
from argparse import ArgumentParser
from typing import Any, List

from app.actions import ActionGenerator
from app.commands import Command
from app.config import Config, Info
from app.exceptions import CommandLineException


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
        master_addr = replicaof.split(" ")
        if len(master_addr) != 2:
            raise CommandLineException(
                "Usage - 'hostname port'",
                flag="replicaof"
            )
        master_host = master_addr[0]
        master_port = int(master_addr[1])
        master_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        master_sock.connect((master_host, master_port))

        # handshake
        # step 1: ping
        master_sock.sendall(Command.ping_command())
        response = master_sock.recv(1024).decode()
        # TODO: remove after testing
        print("step 1 ping: ", response)
        if "PONG" not in response:
            raise RuntimeError(
                "handshake error: ping failed"
            )

        # step 2: replconf twice
        master_sock.send(
            Command.replconf_command("listening-port", str(args.port))
        )
        response = master_sock.recv(1024).decode()
        # TODO: remove after testing
        print("step 2:1 replconf: ", response)
        if "OK" not in response:
            raise RuntimeError(
                "handshake error: first replconf failed"
            )
        master_sock.send(Command.replconf_command("capa", "psync2"))
        response = master_sock.recv(1024).decode()
        # TODO: remove after testing
        print("step 2:2 replconf: ", response)
        if "OK" not in response:
            raise RuntimeError(
                "handshake error: second replconf failed"
            )

        # step 3: psync command
        master_sock.send(
            Command.psync_command("?", "-1")
        )
        response = master_sock.recv(1024).decode()
        # TODO: remove after testing
        print("step 3: psync: ", response)

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
