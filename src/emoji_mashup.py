from io import BytesIO
from cairosvg import svg2png
from typing import Dict, List, Tuple

import random
import emoji_utility
import xml.etree.ElementTree as ET

from os.path import join
from emoji_utility import USABLES_DIRECTORY


def add_part(root, file, contains_full, category):
    file_name = file
    if contains_full and category == "face":
        file_name = "full_" + file

    file_path = join(USABLES_DIRECTORY, category, file_name) + ".svg"
    choice_tree = ET.parse(file_path)
    for child in choice_tree.getroot():
        root.append(child)


def create_emoji(background=None, face=None, eyes=None, other=None, width=128, height=128) -> Tuple[BytesIO, List[str]]:
    args: Dict[emoji_utility.Categories, str] = {
        "background": background,
        "face": face,
        "eyes": eyes,
        "other": other,
    }

    # Validates the input background face eyes and other
    for category, value in args.items():
        if not value:
            continue

        for emoji in value.split(" "):
            success, error = emoji_utility.validate_emoji(emoji, category)
            if success:
                continue
            else:
                raise Exception(error)

    """
        makes a list of choosen emojis, if a category in args is None, a random emoji is choosen
        the emojis in this list are represented as emojis' unicode
        """
    choices = []

    contains_full = False

    for index, category_files in enumerate(emoji_utility.FILES):
        category = emoji_utility.CATEGORIES[index]
        input_emojis = args.get(category)
        if input_emojis:
            input_emojis = input_emojis.split(" ")

            emoji_unicodes = []

            for emoji in input_emojis:
                unicode = emoji_utility.get_unicode_from_emoji(emoji)
                if unicode:
                    file_name = emoji_utility.get_file_from_unicode(
                        unicode, category)

                    contains_full = True if file_name and "full" in file_name else contains_full

                    emoji_unicodes.append(unicode)
            choices.append(emoji_unicodes)
        else:
            chosen = random.choice(category_files)[0:-4]
            unicode = emoji_utility.get_unicode_from_file_name(chosen)

            contains_full = True if "full" in chosen else contains_full

            choices.append(unicode)

    # A list of emoji_utility.EmojiInfo
    emojis_info = []

    for unicode in choices:
        if unicode is list:
            emojis_info.append([emoji_utility.get_info(emoji)
                                for emoji in unicode])
        else:
            emojis_info.append(emoji_utility.get_info(unicode))

    emojis = []

    for emoji_info in emojis_info:
        if emoji_info is list:
            emojis.append([emoji["emoji"] for emoji in emoji_info])
        else:
            emojis.append(emoji_info["emoji"])

    if contains_full:
        emojis.pop(emoji_utility.CATEGORIES.index("eyes"))

    template_tree = ET.parse("assets/template.svg")
    root = template_tree.getroot()

    for index, choice in enumerate(choices):
        category = emoji_utility.CATEGORIES[index]
        if category == "eyes" and contains_full:
            continue
        if choice is list:
            for emoji_choice in choice:
                add_part(root, emoji_choice, contains_full, category)
        else:
            add_part(root, choice, contains_full, category)

    svg_bytes = BytesIO()
    template_tree.write(svg_bytes)
    svg_bytes.seek(0)

    png_bytes = BytesIO()
    svg2png(
        bytestring=svg_bytes.getvalue(),
        write_to=png_bytes,
        output_width=width,
        output_height=height,
    )
    png_bytes.seek(0)

    return png_bytes, emojis


def get_supported(category: emoji_utility.Categories) -> List[str]:
    emoji_files = emoji_utility.FILES[emoji_utility.CATEGORIES.index(category)]

    emoji_unicode = [emoji_utility.get_unicode_from_file_name(
        file[0:-4]) for file in emoji_files]

    emojis = [emoji_utility.get_info(unicode)["emoji"]
              for unicode in emoji_unicode]

    return emojis
