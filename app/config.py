from parser.parser import RESPParser


class Config:
    PARSER = "parser"
    ROLE = "role"

    __conf = {
        "parser": RESPParser(),
        "role": "master",
    }
    __setters = ["role"]

    @staticmethod
    def get(name):
        if name in Config.__conf:
            return Config.__conf[name]
        raise NameError(f"Key: {name} does not exists")

    @staticmethod
    def set(name, value):
        if name in Config.__setters:
            Config.__conf[name] = value
        else:
            raise NameError(f"Key: {name} not accepted in set() method")
