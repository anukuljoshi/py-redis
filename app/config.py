from parser.parser import RESPParser


class Info:
    class Keys:
        ROLE = "role"

    __info = {
        "role": "master"
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
