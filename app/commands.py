from typing import Any

from parser.parser import RESPParser


class CommandAction:
    """
    defines different action corresponding to commands
    """

    @staticmethod
    def ping_action(parser: RESPParser):
        return parser.encode("PONG")

    @staticmethod
    def echo_action(parser: RESPParser, message: Any):
        return parser.encode(message)

    @staticmethod
    def unknown_action(parser: RESPParser):
        return parser.encode("Unknown Command")


class Command:
    PING = "ping"
    ECHO = "echo"
    UNKNOWN = "unknown"

    @staticmethod
    def get_action(command: str):
        if command.lower() == Command.PING:
            return CommandAction.ping_action
        elif command.lower() == Command.ECHO:
            return CommandAction.echo_action
        else:
            return CommandAction.unknown_action
