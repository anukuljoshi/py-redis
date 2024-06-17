import time

from app.config import Config
from app.exceptions import CommandException


def get_current_time_ms():
    return time.time() * 1000


class Command:
    """
    create command in RESP format
    """

    parser = Config.get(Config.Keys.PARSER)

    PING = "ping"
    ECHO = "echo"
    SET = "set"
    GET = "get"
    EXISTS = "exists"
    INFO = "info"
    TYPE = "type"
    UNKNOWN = "unknown"

    @staticmethod
    def ping_command(*args):
        command = [
            Command.PING
        ]
        command.extend(args)
        return Command.parser.encode(command)

    @staticmethod
    def echo_command(*args):
        if len(args) != 1:
            raise CommandException(
                "args len must be 1",
                Command.ECHO
            )
        command = [Command.ECHO]
        command.extend(args)
        return Command.parser.encode(command)

    @staticmethod
    def set_command(*args):
        if len(args) < 2:
            raise CommandException(
                "args len must be greater than 2",
                Command.SET
            )

        key = args[0]
        if type(key) is not type(""):
            raise CommandException(
                "Key must be a string",
                Command.SET
            )

        if len(args) > 2:
            if not args[3].isdigit():
                raise CommandException(
                    "Expiry time must be a number",
                    Command.SET
                )

        command = [Command.SET]
        command.extend(args)
        return Command.parser.encode(command)

    @staticmethod
    def get_command(*args):
        if len(args) != 1:
            raise CommandException(
                "args len must be 1",
                Command.GET
            )

        key = args[0]
        if type(key) is not type(""):
            raise CommandException(
                "Key must be a string",
                Command.GET
            )

        command = [Command.GET]
        command.extend(args)
        return Command.parser.encode(command)

    @staticmethod
    def exists_command(*args):
        if len(args) < 1:
            raise CommandException(
                "args len must be greater than 1",
                Command.EXISTS
            )

        command = [Command.EXISTS]
        command.extend(args)
        return Command.parser.encode(command)

    @staticmethod
    def info_command(*args):
        if len(args) != 1:
            raise CommandException(
                "args len must be 1",
                Command.INFO
            )

        if args[0].lower() != "replication":
            raise CommandException(
                "argument must be 'replication'",
                Command.INFO
            )

        command = [Command.INFO]
        command.extend(args)
        return Command.parser.encode(command)

    @staticmethod
    def type_command(*args):
        if len(args) != 1:
            raise CommandException(
                "args len must be 1",
                Command.TYPE
            )

        command = [Command.TYPE]
        command.extend(args)
        return Command.parser.encode(command)
