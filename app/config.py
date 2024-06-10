from random import choice
from string import ascii_lowercase, digits

from parser.parser import RESPParser


def generate_random_string(size: int) -> str:
    return "".join(choice(ascii_lowercase+digits) for _ in range(size))


class Info:
    class Keys:
        ROLE = "role"
        MASTER_REPL_ID = "master_replid"
        MASTER_REPL_OFFSET = "master_repl_offset"

    __info = {
        "role": "master",
        "master_replid": generate_random_string(40),
        "master_repl_offset": 0,
    }
    __setters = ["role"]

    @staticmethod
    def get(name):
        if name in Info.__info:
            return Info.__info[name]
        raise NameError(f"Key: {name} does not exists")

    @staticmethod
    def set(name, value):
        if name in Info.__setters:
            Info.__info[name] = value
        else:
            raise NameError(f"Key: {name} not accepted in set() method")

    @staticmethod
    def get_info():
        return Info.__info


class Config:
    class Keys:
        PARSER = "parser"

    __config = {
        "parser": RESPParser(),
    }
    __setters = []

    @staticmethod
    def get(name):
        if name in Config.__config:
            return Config.__config[name]
        raise NameError(f"Key: {name} does not exists")

    @staticmethod
    def set(name, value):
        if name in Config.__setters:
            Config.__config[name] = value
        else:
            raise NameError(f"Key: {name} not accepted in set() method")
