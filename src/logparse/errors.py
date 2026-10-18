class ParseError(ValueError):
    transient = False


class MalformedLineError(ParseError):
    pass


class UnknownLevelError(ParseError):
    pass
