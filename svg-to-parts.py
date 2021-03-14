#!/usr/bin/python
import xml.etree.ElementTree as ET
import sys
from os import listdir
from os.path import isfile, join
import unicodedata
import emojis.db as emojis

args = sys.argv
args.pop(0)

ET.register_namespace("","http://www.w3.org/2000/svg")

main_dir = "assets/svg"
out_dir = "assets/emoji-parts"

svg_files = [f for f in listdir(main_dir) if isfile(join(main_dir, f))]

def is_filtered(info, emoji_name: str):
    if len(args) != 0:
        for name in args:
            if name.upper() not in emoji_name.replace(" ", "-").upper():
                return True
            return False

    if info is None:
        return True
    if "SMILEYS" not in info.category.upper():
        return True
    if "FACE" not in emoji_name.upper() and "POO" not in emoji_name.upper():
        return True

for file in svg_files:
    try:
        unicode = r"\U{0}".format("{0:0>8}".format(file[0:-4]))
        emoji = eval(f"'{unicode}'")
        name = unicodedata.name(emoji)
        info = emojis.get_emoji_by_code(emoji)
    except:
        continue

    if is_filtered(info, name):
        continue

    print(emoji, name, info)
    file_path = join(main_dir, file)
    tree = ET.parse(file_path)
    root = tree.getroot()
    for child in root:
        out_file_path = join(out_dir, f"{file[0:-4]}_{child.__hash__()}.svg")

        template_tree = ET.parse("assets/template.svg")
        root = template_tree.getroot()

        root.append(child)
        template_tree.write(out_file_path)
