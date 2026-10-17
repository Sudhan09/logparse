from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass(frozen=True, slots=True)
class LogRecord:
    timestamp: str
    level: LogLevel
    component: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.name} {self.component}: {self.message}"


def parse_line(line: str) -> LogRecord:
    timestamp, level, rest = line.split(" ", 2)
    component, message = rest.split(": ", 1)
    return LogRecord(timestamp, LogLevel[level], component, message)
