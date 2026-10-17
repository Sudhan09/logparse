from dataclasses import dataclass

from logparse.record import LogLevel


@dataclass(frozen=True, slots=True)
class ParserConfig:
    levels: frozenset[LogLevel] = frozenset(LogLevel)
    patterns: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "patterns", tuple(self.patterns))
        object.__setattr__(self, "levels", frozenset(self.levels))

    @classmethod
    def from_lists(cls, levels=None, patterns=None):
        if levels is None:
            level_set = frozenset(LogLevel)
        else:
            level_set = frozenset(LogLevel[name] for name in levels)
        if patterns is None:
            patterns = ()
        return cls(levels=level_set, patterns=tuple(patterns))

    def merge(self, other):
        levels = self.levels & other.levels
        patterns = tuple(dict.fromkeys(self.patterns + other.patterns))
        return ParserConfig(levels=levels, patterns=patterns)
