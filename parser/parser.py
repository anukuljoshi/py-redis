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


class Value:
    def __init__(
        self,
        typ: str,
        integer: int,
        string: str,
        array: List,
        null: bool
    ) -> None:
        self.typ = typ
        self.integer = integer
        self.string = string
        self.array = array
        self.null = null


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

    def __decode_array(self) -> List[Any]:
        """
        helper function to decode array
        """
        # start of length integer
        length = ""
        while self.char != "\r":
            length += self.char
            self.readChar()

        self.readChar()

        length = int(length)
        result = [None]*length

        # i = 0
        # while i < length:
        #     result[i] = self.decode()
        #     i += 1

        return result

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
            if not self.char.isdigit():
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
        helper function to decode string

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

    def decode(self):
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
            # start of length integer
            self.readChar()
            result = self.__decode_array()
        elif self.char == "\r" and self.peekNextChar() == "\n":
            # skip two character \r\n
            self.readChar()
            self.readChar()

        return result


class RESPParser:
    def encode(self, commands: List[Any]) -> str:
        """encode a list of command

            supported types: int, bool, str, list
        Args:
            commands: list of command strings

        Returns:
            RESP encoded string
        """
        response = [f"{TYPE_PREFIX.ARRAY.value}{len(commands)}\r\n"]

        for command in commands:
            if type(command) is type(""):
                response.append(
                    f"{TYPE_PREFIX.BULK_STRING.value}{len(command)}\r\n"
                )
                response.append(f"{command}\r\n")
                # # divide into simple and bulk string
                # if "\r" in command or "\n" in command:
                #     response.append(
                #         f"{TYPE_PREFIX.BULK_STRING.value}{len(command)}\r\n"
                #     )
                #     response.append(f"{command}\r\n")
                # else:
                #     response.append(
                #         f"{TYPE_PREFIX.SIMPLE_STRING.value}{command}\r\n"
                #     )
            elif type(command) is type(1):
                response.append(
                    f"{TYPE_PREFIX.INTEGERS.value}{command}\r\n"
                )
            elif type(command) is type(True):
                response.append(
                    f"{TYPE_PREFIX.BOOLEAN.value}{'t' if command else 'f'}\r\n"
                )
            elif type(command) is type([]):
                response.append(self.encode(command))

        return "".join(response)

    def decode(self, string: str):
        decoder = Decoder(string)
        return decoder.decode()
