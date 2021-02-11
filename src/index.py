import discord
import io
import random
import unicodedata
import cairosvg
import emojis.db as emojis
import xml.etree.ElementTree as ET
from discord.ext import commands
from os import listdir, environ
from os.path import isfile, join
from dotenv import load_dotenv

load_dotenv()
token = environ.get("TOKEN")

main_dir = "assets/usable_parts"

categories = ["background", "face", "other","eyes"]

get_files_in_category = lambda category: [f for f in listdir(join(main_dir, category)) if isfile(join(main_dir, category, f))]

def get_emoji_unicode(file_name):
    split = file_name.split("_")
    name = split.pop(0)
    return name if name != "full" else split.pop(0)

def get_info(unicode):
    unicode = r"\U{0}".format("{0:0>8}".format(unicode))
    emoji = eval(f"'{unicode}'")
    name = unicodedata.name(emoji)
    info = emojis.get_emoji_by_code(emoji)
    return {
        "emoji": emoji,
        "name": name,
        "info": info,
    }

files = [ get_files_in_category(category) for category in categories ]

bot = commands.Bot(command_prefix='>')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def emoji(ctx):
    choices = [ random.choice(category_files) for category_files in files]

    emoji_unicode = [ get_emoji_unicode(choice) for choice in choices]

    emojis = [ get_info(unicode[0:-4])["emoji"] for unicode in emoji_unicode ]

    template_tree = ET.parse("assets/template.svg")
    root = template_tree.getroot()

    for index, choice in enumerate(choices):
        file_path = join(main_dir, categories[index], choice)
        choice_tree = ET.parse(file_path)
        for child in choice_tree.getroot():
            root.append(child)

    svg_bytes = io.BytesIO()
    template_tree.write(svg_bytes)
    svg_bytes.seek(0)

    png_bytes = io.BytesIO()
    cairosvg.svg2png(bytestring=svg_bytes.getvalue(), write_to=png_bytes)
    png_bytes.seek(0)

    file = discord.File(png_bytes, "emojo.png")

    await ctx.send(" + ".join(emojis) + " =", file=file)

bot.run(token)
