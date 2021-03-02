import discord
import asyncio
import io
import random
import time
import unicodedata
import cairosvg
import emojis.db as emojis
import xml.etree.ElementTree as ET
from discord.ext import commands
from discord_slash import SlashCommand
from os import listdir, environ
from os.path import isfile, join
from dotenv import load_dotenv

load_dotenv()
token = environ.get("TOKEN")

main_dir = "assets/usable_parts"

categories = ["background", "face", "eyes", "other"]

emoji_name = "emoji_mashup"

def get_files_in_category(category):
    return [
        f for f in listdir(join(main_dir, category))
        if isfile(join(main_dir, category, f))
    ]


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


def get_unicode_from_emoji(emoji):
    if not emoji:
        return

    return "{:X}".format(ord(emoji)).lower()


def pick_emoji(emojis):
    emoji = random.choice(emojis)
    if (emoji_name in emoji.name.lower()):
        return emoji
    else:
        return pick_emoji(emojis)

def get_file_from_unicode(unicode, category):
    category_files = files[categories.index(category)]

    for file in category_files:
        if unicode in file:
            return file


files = [get_files_in_category(category) for category in categories]

bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

last_call = 0
call_cooldown = 10

guilds = [ 714868972549570653, 814148235098456105 ]

limited_guilds = [ 714868972549570653 ]
channels = [ 809381683899400222 ]

manage_emojis_guilds = [ 714868972549570653 ]


supported_decorator_options = [
    {
        "name": "category",
        "description": "The category you want to see the supported emojis for",
        "type": 3,
        "required": True,
        "choices": [
            {
                "name": "Faces",
                "value": "face"
            },
            {
                "name": "Backgrounds",
                "value": "background"
            },
            {
                "name": "Eyes",
                "value": "eyes"
            },
            {
                "name": "Accessories/Others",
                "value": "other"
            },
        ]
    }
]

@slash.slash(name="emoji", description="generates random emojis", guild_ids=None)
async def _emoji(ctx, background=None, face=None, eyes=None, other=None):
    global last_call
    if time.time() - last_call > call_cooldown:


        if ctx.guild:
            print(f"Called from {ctx.guild.id}:{ctx.guild.name}")
            if ctx.guild.id in limited_guilds:
                if ctx.channel.id not in channels:
                    return
            if ctx.guild.id not in guilds:
                return
        else:
            print(f"Called by {ctx.author.id}:{ctx.author.name}")

        args = {
            "background": background,
            "face": face,
            "eyes": eyes,
            "other": other,
        }

        for category, value in args.items():

            if not value:
                continue

            unicode = get_unicode_from_emoji(value)
            if not unicode:
                await ctx.send(f"Invalid emoji at {category}")
                return

            if get_file_from_unicode(unicode, category):
                continue

            await ctx.send(f"Unimplmeneted emoji found at {category}")
            return

        choices = [
            get_unicode_from_emoji(args.get(categories[index]))
            or random.choice(category_files)[0:-4]
            for index, category_files in enumerate(files)
        ]


        emoji_unicode = [get_emoji_unicode(choice) for choice in choices]

        contains_full = False

        for index, unicode in enumerate(emoji_unicode):
            file = get_file_from_unicode(unicode, categories[index])
            if "full" in file:
                contains_full = True
                break

        emojis = [get_info(unicode)["emoji"]
                  for unicode in emoji_unicode]

        if contains_full:
                    emojis.pop(categories.index("eyes"))

        template_tree = ET.parse("assets/template.svg")
        root = template_tree.getroot()

        for index, choice in enumerate(choices):
            category = categories[index]
            if category == "eyes" and contains_full:
                continue

            file_name = choice
            if contains_full and category == "face":
                file_name = "full_" + choice

            file_path = join(main_dir, categories[index], file_name) + ".svg"
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

        await ctx.respond()

        message = await ctx.send(" + ".join(emojis) + " =", file=file)

        last_call = time.time()

        if  ctx.guild and ctx.guild.id in manage_emojis_guilds:
            await message.add_reaction('👍')
            await message.add_reaction('👎')

            await asyncio.sleep(5 * 60)
            message = await message.channel.fetch_message(message.id)
            # default values
            positive = 0
            negative = 0
            for reaction in message.reactions:
                print(reaction.emoji)
                if reaction.emoji == '👍':
                    positive = reaction.count - 1
                if reaction.emoji == '👎':
                    negative = reaction.count - 1

            print(positive, negative)
            if positive - negative >= 5:
                print(len(ctx.guild.emojis), ctx.guild.emoji_limit)
                if len(ctx.guild.emojis) >= ctx.guild.emoji_limit:
                    print("REACHED {0}".format(ctx.guild.emoji_limit))
                    await pick_emoji(ctx.guild.emojis).delete()

                emoji = await ctx.guild.create_custom_emoji(
                    name="emoji_mashup",
                    image=png_bytes.getvalue()
                )
                await message.channel.send(f"Created emoji {emoji}")

@slash.slash(
    name="supported",
    description="prints the supported emojis by the bot right now.",
    guild_ids=None,
    options=supported_decorator_options)
async def _supported(ctx, choice):
        emoji_files = files[categories.index(choice)]

        emoji_unicode = [get_emoji_unicode(file[0:-4]) for file in emoji_files]

        emojis = [get_info(unicode)["emoji"]
                  for unicode in emoji_unicode]

        embed = discord.Embed(title=f'Supported {choice}', description=" , ".join(emojis))

        await ctx.send(embed=embed)

bot.run(token)
