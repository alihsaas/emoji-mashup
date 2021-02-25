#!/usr/bin/python
import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join

ET.register_namespace("","http://www.w3.org/2000/svg")

main_dir = "assets/category"
out_dir = "assets/usable_parts"

categories = ["face", "eyes", "background", "other"]

svg_files = [f for f in listdir(main_dir) if isfile(join(main_dir, f))]
svg_files.sort()
to_be_merged = {}

for file in svg_files:
    split = file.split("_")
    is_merge = "merge" in split
    split.remove("merge") if is_merge else None
    first_arg = split.pop(0)
    emoji_unicode = split.pop(0)
    out_file_path = join(out_dir, first_arg, emoji_unicode)

    if "full" == emoji_unicode:
        continue
    if first_arg not in categories:
        continue
    if is_merge:
        to_be_merged[emoji_unicode] = to_be_merged.get(emoji_unicode) or {
            "categories": { category: [] for category in categories }
        }
        to_be_merged[emoji_unicode]["categories"][first_arg].append(file)
        continue


    element_tree = ET.parse(join(main_dir, file))
    root_element = element_tree.getroot()
    child = next(iter(root_element))

    template_tree = ET.parse("assets/template.svg")
    root = template_tree.getroot()

    root.append(child)
    template_tree.write("{0}.svg".format(out_file_path))

for unicode in to_be_merged:
    for category in to_be_merged[unicode]["categories"]:
        if len(to_be_merged[unicode]["categories"][category]) == 0:
            continue

        template_tree = ET.parse("assets/template.svg")
        root = template_tree.getroot()

        out_file_path = join(out_dir, category, unicode)

        for file in to_be_merged[unicode]["categories"][category]:
                element_tree = ET.parse(join(main_dir, file))
                root_element = element_tree.getroot()
                child = next(iter(root_element))
                root.append(child)

        template_tree.write("{0}.svg".format(out_file_path))

