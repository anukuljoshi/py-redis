from typing import Any

from parser.parser import RESPParser

STORE = dict()


class CommandAction:
    """
    defines different action corresponding to commands
    """

    @staticmethod
    def ping_action(parser: RESPParser):
        return parser.encode("PONG")

    @staticmethod
    def echo_action(parser: RESPParser, *args):
        if len(args) != 1:
            return parser.encode("ECHO takes in 1 argument")
        message = args[0]
        return parser.encode(message)

    @staticmethod
    def set_action(parser: RESPParser, key: Any, value):
        if type(key) is not type(""):
            return parser.encode("Key must be a string")
        STORE[key] = value
        return parser.encode("OK")

    @staticmethod
    def get_action(parser: RESPParser, key: str):
        if type(key) is not type(""):
            return parser.encode("Key must be a string")

        value = STORE.get(key, None)
        if value is None:
            return parser.encode(None)
        return parser.encode(value)

    @staticmethod
    def unknown_action(parser: RESPParser):
        return parser.encode("Unknown Command")


class Command:
    PING = "ping"
    ECHO = "echo"
    SET = "set"
    GET = "get"
    UNKNOWN = "unknown"

    @staticmethod
    def get_action(command: str):
        if command.lower() == Command.PING:
            return CommandAction.ping_action
        elif command.lower() == Command.ECHO:
            return CommandAction.echo_action
        elif command.lower() == Command.GET:
            return CommandAction.get_action
        elif command.lower() == Command.SET:
            return CommandAction.set_action
        else:
            return CommandAction.unknown_action
