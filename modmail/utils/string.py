import typing as t

import discord

ORDINAL_ENDINGS = {"1": "st", "2": "nd", "3": "rd"}


def list_of(items: list, sep: t.Optional[str] = "and") -> str:
    if len(items) > 2:
        return "{}, {} {}".format(", ".join(items[:-1]), sep, items[-1])
    else:
        return f" {sep} ".join(items)


def ordinal(number: int) -> str:
    if str(number)[-2:] not in ("11", "12", "13"):
        return f"{number:,}{ORDINAL_ENDINGS.get(str(number)[-1], 'th')}"
    else:
        return f"{number:,}th"
