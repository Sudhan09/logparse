import argparse
import json
import sys

from logparse.config import ParserConfig
from logparse.filters import timed
from logparse.pipeline import run

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def build_parser():
    parser = argparse.ArgumentParser(prog="logparse")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--level", choices=LEVELS)
    parser.add_argument("--pattern")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timing", action="store_true")
    return parser


def make_config(args):
    levels = [args.level] if args.level else None
    patterns = [args.pattern] if args.pattern else None
    return ParserConfig.from_lists(levels=levels, patterns=patterns)


def main(argv=None):
    args = build_parser().parse_args(argv)
    config = make_config(args)
    do_run = timed(run) if args.timing else run
    report = do_run(args.paths, config)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0


def print_report(report):
    print(f"total    {report['total']}")
    for level, count in report["by_level"].items():
        print(f"{level:<8} {count}")
    print(f"errors   {report['error_count']}")


if __name__ == "__main__":
    sys.exit(main())
