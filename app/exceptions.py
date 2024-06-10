class CommandLineException(Exception):
    def __init__(self, message: str, flag: str) -> None:
        super().__init__(message)
        self.flag = flag

    def __str__(self) -> str:
        return f"CommandLineException for {self.flag}: {super().__str__()}"


class CommandException(Exception):
    def __init__(self, message: str, command: str) -> None:
        super().__init__(message)
        self.command = command

    def __str__(self) -> str:
        return f"CommandException for {self.command}: {super().__str__()}"
