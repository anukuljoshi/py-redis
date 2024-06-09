import time

from parser.parser import RESPParser

STORE = dict()


def get_current_time_ms():
    return time.time() * 1000


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
    def set_action(parser: RESPParser, *args):
        key = args[0]
        value = args[1]

        expiry = 0
        if len(args) > 2:
            format = args[2]
            if not args[3].isdigit():
                return parser.encode("Expiry time must be a number")

            expiry = int(args[3])
            if format.lower() == "ex":
                # expiry is in seconds
                expiry *= 1000

        if type(key) is not type(""):
            return parser.encode("Key must be a string")

        STORE[key] = {
            "value": value,
            "set_time": get_current_time_ms(),
            "expiry": expiry
        }
        return parser.encode("OK")

    @staticmethod
    def get_action(parser: RESPParser, *args):
        key = args[0]

        if type(key) is not type(""):
            return parser.encode("Key must be a string")

        data = STORE.get(key, None)

        # key not found
        if data is None:
            return parser.encode(None)

        # check for expiry
        if data.get("expiry", 0) == 0:
            value = data.get("value", None)
            return parser.encode(value)

        expiry = data.get("expiry", 0)
        set_time = data.get("set_time", 0)
        current_time = get_current_time_ms()

        if current_time >= set_time + expiry:
            # key expired
            del STORE[key]
            return parser.encode(None)

        value = data.get("value")
        return parser.encode(value)

    @staticmethod
    def exists_action(parser: RESPParser, *args):
        keys = args

        count = 0
        for key in keys:
            if key in STORE:
                count += 1

        return parser.encode(count)

    @staticmethod
    def unknown_action(parser: RESPParser, *args):
        _ = args
        return parser.encode("Unknown Command")


class Command:
    PING = "ping"
    ECHO = "echo"
    SET = "set"
    GET = "get"
    EXISTS = "exists"
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
        elif command.lower() == Command.EXISTS:
            return CommandAction.exists_action
        else:
            return CommandAction.unknown_action