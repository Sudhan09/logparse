from contextlib import contextmanager


@contextmanager
def open_log(path):
    f = open(path, encoding="utf-8")
    try:
        yield f
    finally:
        f.close()
