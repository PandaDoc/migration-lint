from enum import Enum


class ColorCode(Enum):
    blue = "\x1b[1;34m"
    grey = "\x1b[38;21m"
    green = "\x1b[1;32m"
    red = "\x1b[31;21m"
    yellow = "\x1b[33;21m"
    reset = "\x1b[0m"


def colorize(color: ColorCode, msg: str) -> str:
    return f"{color.value}{msg}{ColorCode.reset.value}"


def grey(msg: str) -> str:
    return colorize(ColorCode.grey, msg)


def green(msg: str) -> str:
    return colorize(ColorCode.green, msg)


def yellow(msg: str) -> str:
    return colorize(ColorCode.yellow, msg)


def red(msg: str) -> str:
    return colorize(ColorCode.red, msg)


def blue(msg: str) -> str:
    return colorize(ColorCode.blue, msg)
