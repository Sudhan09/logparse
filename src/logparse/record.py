from enum import Enum


class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogRecord:
    def __init__(
        self, timestamp: str, level: LogLevel, component: str, message: str
    ) -> None:
        self.timestamp = timestamp
        self.level = level
        self.component = component
        self.message = message

    def _key(self) -> tuple[str, LogLevel, str, str]:
        return (self.timestamp, self.level, self.component, self.message)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LogRecord):
            return NotImplemented
        return self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    def __repr__(self) -> str:
        return (
            f"LogRecord({self.timestamp!r}, {self.level}, "
            f"{self.component!r}, {self.message!r})"
        )

    def __str__(self) -> str:
        return f"{self.level.name} {self.component}: {self.message}"


def parse_line(line: str) -> LogRecord:
    timestamp, level, rest = line.split(" ", 2)
    component, message = rest.split(": ", 1)
    return LogRecord(timestamp, LogLevel[level], component, message)
