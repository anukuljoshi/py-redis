from enum import Enum
from typing import Any, List

from parser.exceptions import ParserException


class TYPE_PREFIX(Enum):
    SIMPLE_STRING = "+"
    SIMPLE_ERROR = "-"
    INTEGERS = ":"
    BULK_STRING = "$"
    ARRAY = "*"
    NULL = "_"
    BOOLEAN = "#"
    DOUBLE = ","
    BIG_NUMBER = "("
    BULK_ERROR = "!"
    VERBATIM_STRING = "="
    MAP = "%"
    SET = "~"
    PUSH = ">"


class Decoder:
    def __init__(self, string: str):
        self.current = 0
        self.next = 0
        self.string = string
        self.char = ""
        self.result = []

    def readChar(self):
        if self.next >= len(self.string):
            self.char = ""
        else:
            self.char = self.string[self.next]
        self.current = self.next
        self.next += 1

    def peekNextChar(self) -> str:
        return self.string[self.next]

    def __decode_int(self) -> int:
        """
        helper function to decode integers

        Raises:
            ParserException: with unexpected char and position

        Returns:
            decoded integer value
        """

        value = ""
        while self.char != "\r":
            if not self.char.isdigit() and self.char not in ["+", "-"]:
                raise ParserException(f"Unexpected {self.char}", self.current)
            value += self.char
            self.readChar()

        return int(value)

    def __decode_bool(self) -> bool:
        """
        helper function to decode boolean

        Raises:
            ParserException: with unexpected char and position

        Returns:
            decoded boolean value
        """

        if self.char == "t":
            self.readChar()
            return True
        elif self.char == "f":
            self.readChar()
            return False

        raise ParserException(f"Unexpected {self.char}", self.current)

    def __decode_simple_string(self):
        """
        helper function to decode simple strings

        Returns:
            decoded string value
        """

        # start of length integer
        string = ""
        while self.char != "\r":
            string += self.char
            self.readChar()

        return string

    def __decode_bulk_string(self):
        """
        helper function to decode bulk strings

        Returns:
            decoded string value
        """

        # start of length integer
        length = ""
        while self.char != "\r":
            length += self.char
            self.readChar()

        self.readChar()
        self.readChar()

        length = int(length)
        result = []

        i = 0
        while i < length:
            result.append(self.char)
            self.readChar()
            i += 1

        return "".join(result)

    def __decode_array(self) -> List[Any]:
        """
        helper function to decode array

        Returns:
            decoded array value
        """
        # start of length integer
        length = ""
        while self.char != "\r":
            length += self.char
            self.readChar()

        self.readChar()
        self.readChar()

        length = int(length)
        result = []

        for _ in range(length):
            item = None
            if self.char == TYPE_PREFIX.INTEGERS.value:
                # int
                self.readChar()
                item = self.__decode_int()
                self.readChar()
                self.readChar()
            elif self.char == TYPE_PREFIX.BOOLEAN.value:
                # bool
                self.readChar()
                item = self.__decode_bool()
                self.readChar()
                self.readChar()
            elif self.char == TYPE_PREFIX.BULK_STRING.value:
                # string
                self.readChar()
                item = self.__decode_bulk_string()
                self.readChar()
                self.readChar()
            elif self.char == TYPE_PREFIX.SIMPLE_STRING.value:
                # string
                self.readChar()
                item = self.__decode_simple_string()
                self.readChar()
                self.readChar()
            elif self.char == TYPE_PREFIX.ARRAY.value:
                # list
                self.readChar()
                item = self.__decode_array()
            else:
                raise ParserException(f"Unexpected {self.char}", self.current)

            result.append(item)

        return result

    def decode(self):
        """
        general decode function
        can decode all data types
        """

        self.readChar()

        result = None

        if self.char == TYPE_PREFIX.INTEGERS.value:
            # int
            self.readChar()
            result = self.__decode_int()
            self.readChar()
            self.readChar()
        elif self.char == TYPE_PREFIX.BOOLEAN.value:
            # bool
            self.readChar()
            result = self.__decode_bool()
            self.readChar()
            self.readChar()
        elif self.char == TYPE_PREFIX.BULK_STRING.value:
            # string
            self.readChar()
            result = self.__decode_bulk_string()
            self.readChar()
            self.readChar()
        elif self.char == TYPE_PREFIX.SIMPLE_STRING.value:
            # string
            self.readChar()
            result = self.__decode_simple_string()
            self.readChar()
            self.readChar()
        elif self.char == TYPE_PREFIX.ARRAY.value:
            # list
            self.readChar()
            result = self.__decode_array()
        else:
            raise ParserException(f"Unexpected {self.char}", self.current)

        if self.current != len(self.string):
            raise ParserException(
                f"Numbers of characters did not match: {self.string}",
                self.current
            )

        return result

    def decode_command_string(self) -> List[Any]:
        """
        function to decode a command string
        can only be used to decode a string resulting in a list

        NOTE: RESP command string will always result to a list
        """

        self.readChar()
        result = None

        if self.char == TYPE_PREFIX.ARRAY.value:
            # list
            self.readChar()
            result = self.__decode_array()
        else:
            raise ParserException(f"Unexpected {self.char}", self.current)

        if self.current != len(self.string):
            raise ParserException(
                f"Numbers of characters did not match: {self.string}",
                self.current
            )

        return result


class Encoder:
    def __encode_int(self, command: int) -> str:
        return f"{TYPE_PREFIX.INTEGERS.value}{command}\r\n"

    def __encode_bool(self, command: bool) -> str:
        return f"{TYPE_PREFIX.BOOLEAN.value}{'t' if command else 'f'}\r\n"

    def __encode_simple_string(self, command: str) -> str:
        return f"{TYPE_PREFIX.SIMPLE_STRING.value}{command}\r\n"

    def __encode_bulk_string(self, command: str) -> str:
        return f"{TYPE_PREFIX.BULK_STRING.value}{len(command)}\r\n{command}\r\n"

    def __encode_null_string(self) -> str:
        return f"{TYPE_PREFIX.BULK_STRING.value}{-1}\r\n"

    def __encode_array(self, commands: List[Any]) -> str:
        result = [f"{TYPE_PREFIX.ARRAY.value}{len(commands)}\r\n"]
        for command in commands:
            result.append(self.encode(command))
        return "".join(result)

    def encode(self, command: Any) -> str:
        result = []

        if type(command) is type(1):
            # int
            result.append(self.__encode_int(command))
        elif type(command) is type(True):
            # boolean
            result.append(self.__encode_bool(command))
        elif type(command) is type(""):
            result.append(self.__encode_bulk_string(command))
            # # use both simple strings and bulk strings
            # if "\r" in command or "\n" in command:
            #     # bulk string
            #     result.append(self.__encode_bulk_string(command))
            # else:
            #     # simple string
            #     result.append(self.__encode_simple_string(command))
        elif type(command) is type([]):
            # list
            result.append(self.__encode_array(command))
        elif type(command) is type(None):
            result.append(self.__encode_null_string())

        return "".join(result)


class RESPParser:
    def encode(self, commands: Any) -> bytes:
        """encode a list of command

            supported types: int, bool, str, list
        Args:
            commands: list of command strings

        Returns:
            RESP encoded string
        """
        encoder = Encoder()
        return encoder.encode(commands).encode("utf-8")

    def decode(self, bytes_string: bytes):
        string = bytes_string.decode("utf-8")
        decoder = Decoder(string)
        return decoder.decode()

    def decode_command(self, bytes_string: bytes) -> List[Any]:
        string = bytes_string.decode("utf-8")
        decoder = Decoder(string)
        return decoder.decode_command_string()
