class ParserException(Exception):
    def __init__(self, message: str, index: int) -> None:
        super().__init__(message)
        self.index = index

    def __str__(self) -> str:
        return f"ParserException at {self.index}: {super().__str__()}"
