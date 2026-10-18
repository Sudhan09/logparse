import itertools
import json
import sys
from collections import Counter
from contextlib import ExitStack, suppress

from logparse.errors import ParseError
from logparse.files import open_log
from logparse.filters import all_of, matches
from logparse.record import parse_line


def read_lines(path):
    if path == "-":
        for line in sys.stdin:
            yield line.rstrip("\n")
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")


def lines_from(f):
    for line in f:
        yield line.rstrip("\n")


def parse(lines, errors=None, file="-"):
    for line_no, line in enumerate(lines, start=1):
        try:
            record = parse_line(line)
        except ParseError as exc:
            if errors is not None:
                errors.append(
                    {
                        "file": file,
                        "line_no": line_no,
                        "error": type(exc).__name__,
                        "cause": str(exc.__cause__),
                    }
                )
        else:
            yield record


def keep(records, pred):
    for r in records:
        if pred(r):
            yield r


def jsonl_chunks(records, size=1000):
    for batch in itertools.batched(records, size, strict=False):
        lines = []
        for r in batch:
            row = {
                "timestamp": r.timestamp,
                "level": r.level.name,
                "component": r.component,
                "message": r.message,
            }
            lines.append(json.dumps(row))
        yield "\n".join(lines)


def run(paths, config, head=None, max_errors=1000):
    errors = CappedList(max_errors)
    with ExitStack() as stack:
        streams = []
        sources = {}
        for p in paths:
            f = sys.stdin if p == "-" else stack.enter_context(open_log(p))
            streams.append(parse(lines_from(f), errors, p))
            source = read_source(p) if p != "-" else None
            if source is not None:
                sources[p] = source
        records = itertools.chain.from_iterable(streams)
        preds = [lambda r: r.level in config.levels]

        preds += [matches(p) for p in config.patterns]
        kept = keep(records, all_of(*preds))
        if head is not None:
            kept = itertools.islice(kept, head)

        by_level = Counter()
        per_minute = {}
        for minute, group in itertools.groupby(kept, key=lambda r: r.timestamp[:16]):
            count = 0
            for r in group:
                by_level[r.level.name] += 1
                count += 1
            per_minute[minute] = per_minute.get(minute, 0) + count
        report = {
            "total": sum(by_level.values()),
            "by_level": dict(by_level),
            "per_minute": per_minute,
            "error_count": errors.count,
            "errors": errors.items,
        }
        if sources:
            report["sources"] = sources
        return report


def read_source(path):
    with suppress(FileNotFoundError):
        with open(f"{path}.meta.json", encoding="utf-8") as f:
            return json.load(f)["source"]
    return None


class CappedList:
    def __init__(self, limit):
        self.limit = limit
        self.items = []
        self.count = 0

    def append(self, item):
        self.count += 1
        if len(self.items) < self.limit:
            self.items.append(item)
