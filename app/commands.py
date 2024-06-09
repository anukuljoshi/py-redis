import time

from app.config import Config

STORE = dict()


def get_current_time_ms():
    return time.time() * 1000


class CommandAction:
    """
    defines different action corresponding to commands
    """

    parser = Config.get(Config.PARSER)

    @staticmethod
    def ping_action():
        return CommandAction.parser.encode("PONG")

    @staticmethod
    def echo_action(*args):
        if len(args) != 1:
            return CommandAction.parser.encode("ECHO takes in 1 argument")
        message = args[0]
        return CommandAction.parser.encode(message)

    @staticmethod
    def set_action(*args):
        key = args[0]
        value = args[1]

        expiry = 0
        if len(args) > 2:
            format = args[2]
            if not args[3].isdigit():
                return CommandAction.parser.encode(
                    "Expiry time must be a number"
                )

            expiry = int(args[3])
            if format.lower() == "ex":
                # expiry is in seconds
                expiry *= 1000

        if type(key) is not type(""):
            return CommandAction.parser.encode("Key must be a string")

        STORE[key] = {
            "value": value,
            "set_time": get_current_time_ms(),
            "expiry": expiry
        }
        return CommandAction.parser.encode("OK")

    @staticmethod
    def get_action(*args):
        key = args[0]

        if type(key) is not type(""):
            return CommandAction.parser.encode("Key must be a string")

        data = STORE.get(key, None)

        # key not found
        if data is None:
            return CommandAction.parser.encode(None)

        # check for expiry
        if data.get("expiry", 0) == 0:
            value = data.get("value", None)
            return CommandAction.parser.encode(value)

        expiry = data.get("expiry", 0)
        set_time = data.get("set_time", 0)
        current_time = get_current_time_ms()

        if current_time >= set_time + expiry:
            # key expired
            del STORE[key]
            return CommandAction.parser.encode(None)

        value = data.get("value")
        return CommandAction.parser.encode(value)

    @staticmethod
    def exists_action(*args):
        keys = args

        count = 0
        for key in keys:
            if key in STORE:
                count += 1

        return CommandAction.parser.encode(count)

    @staticmethod
    def info_action(*args):
        if len(args) != 1:
            return CommandAction.parser.encode("INFO takes in one argument")

        if args[0].lower() != "replication":
            return CommandAction.parser.encode(
                "argument must be 'replication'"
            )

        response = "# Replication\nrole:master"
        return CommandAction.parser.encode(response)

    @staticmethod
    def unknown_action(*args):
        _ = args
        return CommandAction.parser.encode("Unknown Command")


class Command:
    PING = "ping"
    ECHO = "echo"
    SET = "set"
    GET = "get"
    EXISTS = "exists"
    INFO = "info"
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
        elif command.lower() == Command.INFO:
            return CommandAction.info_action
        else:
            return CommandAction.unknown_action
