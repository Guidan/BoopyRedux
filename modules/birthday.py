import logging
import json
from dateutil.parser import parse


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


async def main(message, content):
    if len(content) < 2:
        userid = message.author
        date = False
    else:
        args = content.pop(0)
        args = " ".join(args)
        if is_date(args):

            date = True
        else:
            date = False
            if args.startswith("<@"):
                userid = args[2:-1]
            else:
                await message.channel.send("Hello! To use the birthday function, use either of these syntaxes"
                                           "\n'!birthday @User' to check that Users birthday (if it exists in DB"
                                           "\n'!birthday MM/DD' to save your birthday to the DB")
                return

        if date:



