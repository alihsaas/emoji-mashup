from io import BufferedIOBase, BytesIO
from cairosvg import svg2png
from typing import Dict, List, Union

import random
import lib.emoji_utility as emoji_utility
import xml.etree.ElementTree as ET

from os.path import join


def add_part(root, file, contains_full, category):
    file_name = file
    if contains_full and category == "face":
        file_name = "full_" + file

    file_path = join(emoji_utility.USABLES_DIRECTORY,
                     category, file_name) + ".svg"
    choice_tree = ET.parse(file_path)
    for child in choice_tree.getroot():
        root.append(child)


def create_emoji(
        path: Union[BufferedIOBase, str],
        background: str = None,
        face: str = None,
        eyes: str = None,
        other: str = None,
        size: int = 128) -> List[str]:
    args: Dict[emoji_utility.Categories, Union[str, None]] = {
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
            input_emojis = input_emojis.strip().split(" ")

            emoji_unicodes: List[str] = []

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
        if type(unicode) == list:
            emojis_info.append([emoji_utility.get_info(emoji)
                                for emoji in unicode])
        else:
            emojis_info.append(emoji_utility.get_info(unicode))

    emojis = []

    for emoji_info in emojis_info:
        if type(emoji_info) == list:
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
        if type(choice) == list:
            for emoji_choice in choice:
                add_part(root, emoji_choice, contains_full, category)
        else:
            add_part(root, choice, contains_full, category)

    svg_bytes = BytesIO()
    template_tree.write(svg_bytes)
    svg_bytes.seek(0)

    svg2png(
        bytestring=svg_bytes.getvalue(),
        write_to=path,
        output_width=size,
        output_height=size,
    )

    return emojis


def get_supported(category: emoji_utility.Categories) -> List[str]:
    emoji_files = emoji_utility.FILES[emoji_utility.CATEGORIES.index(category)]

    emoji_unicode = [emoji_utility.get_unicode_from_file_name(
        file[0:-4]) for file in emoji_files]

    emojis = [emoji_utility.get_info(unicode)["emoji"]
              for unicode in emoji_unicode]

    return emojis


if __name__ == "__main__":
    import argparse
    import sys

    from typing import Text, Optional

    class EmojiAction(argparse.Action):
        def __call__(self,
                     parser: argparse.ArgumentParser,
                     namespace: argparse.Namespace,
                     values: Text, option_string: Optional[Text]) -> None:
            try:
                info = emoji_utility.get_info(values)
                setattr(namespace, self.dest, info["emoji"])
            except:
                sys.exit(f"Invalid emoji at {self.dest}")

    parser = argparse.ArgumentParser(description="Generate Random Emojis")

    parser.add_argument("--size", type=int,
                        help="The height and width of the final image")

    for category in emoji_utility.CATEGORIES:
        parser.add_argument(f"--{category}", type=str, action=EmojiAction)

    parser.add_argument(
        "--path", type=str, help="The path to the file where the emoji will be exported")
    parser.add_argument("-", dest="stdout", action="store_true")

    parsed_args = parser.parse_args()
    path = parsed_args.path

    if path and not path.endswith(".png"):
        exit("only png format is supported")

    emoji_bytes = BytesIO()
    try:
        emojis = create_emoji(emoji_bytes,
                              background=parsed_args.background,
                              face=parsed_args.face,
                              eyes=parsed_args.eyes,
                              other=parsed_args.other,
                              size=parsed_args.size
                              )
    except Exception as e:
        exit(e)
    emoji_bytes.seek(0)

    if path:
        with open(path, "wb") as f:
            f.write(emoji_bytes.getvalue())

    if parsed_args.stdout:
        sys.stdout.buffer.write(emoji_bytes.getvalue())
