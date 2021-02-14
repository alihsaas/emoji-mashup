import discord
import io
import random
import time
import unicodedata
import cairosvg
import emojis.db as emojis
import xml.etree.ElementTree as ET
import emojis.db as emojis_db
from discord.ext import commands
from os import listdir, environ
from os.path import isfile, join
from dotenv import load_dotenv

load_dotenv()
token = environ.get("TOKEN")

main_dir = "assets/usable_parts"

categories = ["background", "face", "eyes", "other"]

emoji_name = "emoji_mashup"

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

def pick_emoji(emojis):
    emoji = random.choice(emojis)
    if (emoji_name in emoji.name.lower()):
        return emoji
    else:
        return pick_emoji(emojis)


files = [ get_files_in_category(category) for category in categories ]

bot = commands.Bot(command_prefix='>')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

last_call = 0
call_cooldown = 10

@bot.command()
async def emoji(ctx):
    global last_call
    if time.time() - last_call > call_cooldown:
        if ctx.guild and ctx.guild.id == 714868972549570653:
            if ctx.channel.id != 809381683899400222:
                return

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
        cairosvg.svg2png(
            bytestring=svg_bytes.getvalue(),
            write_to=png_bytes,
            output_width=128,
            output_height=128,
        )
        png_bytes.seek(0)

        file = discord.File(png_bytes, "emojo.png")

        index = 0
        print(len(ctx.guild.emojis), ctx.guild.emoji_limit)
        if len(ctx.guild.emojis) >= ctx.guild.emoji_limit:
            print("REACHED {0}".format(ctx.guild.emoji_limit))
            await pick_emoji(ctx.guild.emojis).delete()

        await ctx.guild.create_custom_emoji(name="emoji_mashup", image=png_bytes.getvalue())
        await ctx.send(" + ".join(emojis) + " =", file=file)

        last_call = time.time()
bot.run(token)
