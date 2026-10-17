import itertools
import json
import sys
from collections import Counter

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


def parse(lines):
    for line in lines:
        try:
            yield parse_line(line)
        except ValueError, KeyError:
            continue


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


def run(paths, config, head=None):
    lines = itertools.chain.from_iterable(read_lines(p) for p in paths)
    preds = [lambda r: r.level in config.levels]
    preds += [matches(p) for p in config.patterns]
    kept = keep(parse(lines), all_of(*preds))
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

    return {
        "total": sum(by_level.values()),
        "by_level": dict(by_level),
        "per_minute": per_minute,
    }
