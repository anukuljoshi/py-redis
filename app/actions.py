import time
from typing import Any

from app.commands import Command
from app.config import Config, Info

STORE = dict()


def get_current_time_ms():
    return time.time() * 1000


def get_type_string(value: Any):
    if type(value) is type(1):
        # int
        return "int"
    elif type(value) is type(True):
        # boolean
        return "bool"
    elif type(value) is type(""):
        return "string"
    elif type(value) is type([]):
        # list
        return "array"
    elif type(value) is type(None):
        return "none"
    return "unknown"


class Action:
    """
    defines different actions corresponding to commands
    """

    parser = Config.get(Config.Keys.PARSER)

    @staticmethod
    def ping_action():
        return Action.parser.encode("PONG")

    @staticmethod
    def echo_action(*args):
        if len(args) != 1:
            return Action.parser.encode("ECHO takes in 1 argument")
        message = args[0]
        return Action.parser.encode(message)

    @staticmethod
    def set_action(*args):
        key = args[0]
        value = args[1]

        expiry = 0
        if len(args) > 2:
            format = args[2]
            if not args[3].isdigit():
                return Action.parser.encode(
                    "Expiry time must be a number"
                )

            expiry = int(args[3])
            if format.lower() == "ex":
                # expiry is in seconds
                expiry *= 1000

        if type(key) is not type(""):
            return Action.parser.encode("Key must be a string")

        STORE[key] = {
            "value": value,
            "set_time": get_current_time_ms(),
            "expiry": expiry
        }
        return Action.parser.encode("OK")

    @staticmethod
    def get_action(*args):
        key = args[0]

        if type(key) is not type(""):
            return Action.parser.encode("Key must be a string")

        data = STORE.get(key, None)

        # key not found
        if data is None:
            return Action.parser.encode(None)

        # check for expiry
        if data.get("expiry", 0) == 0:
            value = data.get("value", None)
            return Action.parser.encode(value)

        expiry = data.get("expiry", 0)
        set_time = data.get("set_time", 0)
        current_time = get_current_time_ms()

        if current_time >= set_time + expiry:
            # key expired
            del STORE[key]
            return Action.parser.encode(None)

        value = data.get("value")
        return Action.parser.encode(value)

    @staticmethod
    def exists_action(*args):
        keys = args

        count = 0
        for key in keys:
            if key in STORE:
                count += 1

        return Action.parser.encode(count)

    @staticmethod
    def info_action(*args):
        if len(args) != 1:
            return Action.parser.encode("INFO takes in one argument")

        if args[0].lower() != "replication":
            return Action.parser.encode(
                "argument must be 'replication'"
            )

        response = ["# Replication"]
        items = Info.get_info()
        for key, value in items.items():
            response.append(f"{key}:{value}")

        return Action.parser.encode("\n".join(response))

    @staticmethod
    def unknown_action(*args):
        _ = args
        return Action.parser.encode("Unknown Command")

    @staticmethod
    def type_action(*args):
        if len(args) != 1:
            return Action.parser.encode("TYPE takes in one argument")

        key = args[0]
        value_obj = STORE.get(key, None)
        if value_obj is None:
            return Action.parser.encode("none")

        value = value_obj["value"]
        value_type = get_type_string(value)
        return Action.parser.encode(value_type)


class ActionGenerator:
    @staticmethod
    def get_action(command: str):
        if command.lower() == Command.PING:
            return Action.ping_action
        elif command.lower() == Command.ECHO:
            return Action.echo_action
        elif command.lower() == Command.GET:
            return Action.get_action
        elif command.lower() == Command.SET:
            return Action.set_action
        elif command.lower() == Command.EXISTS:
            return Action.exists_action
        elif command.lower() == Command.INFO:
            return Action.info_action
        elif command.lower() == Command.TYPE:
            return Action.type_action
        else:
            return Action.unknown_action
