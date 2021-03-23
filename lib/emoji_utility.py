import unicodedata
import emojis.db as emojis

from lib.utility import get_files_in_category

from typing import List, Literal, Optional, Tuple, TypedDict, Union
from os.path import join

# Types


class EmojiInfo(TypedDict):
    emoji: str
    name: str
    info: Union[emojis.Emoji, None]


Categories = Literal["background", "face", "other", "eyes"]

# Constants

USABLES_DIRECTORY = "assets/usable_parts"

CATEGORIES: List[Categories] = ["background", "face", "other", "eyes"]

FILES = [get_files_in_category(join(USABLES_DIRECTORY, category))
         for category in CATEGORIES]


# Utility

def get_unicode_from_file_name(file_name: str) -> str:
    split = file_name.split("_")
    name = split.pop(0)
    return name if name != "full" else split.pop(0)


def get_info(unicode: str) -> EmojiInfo:
    unicode = r"\U{0}".format("{0:0>8}".format(unicode))
    emoji = eval(f"'{unicode}'")
    name = unicodedata.name(emoji)
    info = emojis.get_emoji_by_code(emoji)
    return {
        "emoji": emoji,
        "name": name,
        "info": info,
    }


def get_unicode_from_emoji(emoji: str) -> Optional[str]:
    if not emoji:
        return

    if len(emoji) != 1:
        return

    if len(str(ord(emoji))) != 6:
        return

    return "{:X}".format(ord(emoji)).lower()


def get_file_from_unicode(unicode: str, category: Categories) -> Optional[str]:
    category_files = FILES[CATEGORIES.index(category)]

    for file in category_files:
        if unicode in file:
            return file


def get_file_from_emoji(emoji: str, category: Categories) -> Optional[str]:
    unicode = get_unicode_from_emoji(emoji)
    if not unicode:
        return

    return get_file_from_unicode(unicode, category)


def validate_emoji(emoji: str, category: Categories) -> Tuple[bool, str]:
    """ Checks if `emoji` has an existing part in `category` """

    if not emoji:
        return (False, "Expected an emoji, got falsy value.")

    unicode = get_unicode_from_emoji(emoji)
    if not unicode:
        return (False, f"Invalid emoji at {category}")

    if get_file_from_unicode(unicode, category):
        return (True, "")

    return (False, f"Unimplmeneted emoji found at {category}")
