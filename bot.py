import config
import discord
import functools
import operator
import asyncio
import random
import time
import lib.emoji_mashup as emoji_mashup


from io import BytesIO
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from typing import Optional
from lib.emoji_utility import CATEGORIES, Categories


EMOJI_NAME = "emoji_mashup"


def pick_emoji(emojis):
    emoji = random.choice(emojis)
    if EMOJI_NAME in emoji.name.lower():
        return emoji
    else:
        return pick_emoji(emojis)


def flat(list_to_flat):
    return functools.reduce(operator.iconcat, list_to_flat, [])


bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

last_call = 0
call_cooldown = 10

guilds = []

limited_guilds = [714868972549570653]
channels = [809381683899400222]

manage_emojis_guilds = []


supported_decorator_options = [
    {
        "name": "category",
        "description": "The category you want to see the supported emojis for",
        "type": 3,
        "required": False,
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


async def create_emoji(ctx: SlashContext, background=None, face=None, eyes=None, other=None):
    global last_call

    if time.time() - last_call > call_cooldown:
        guild_info = config.GUILDS_INFO.get(
            ctx.guild_id) if ctx.guild_id else None
        if ctx.guild:
            print(f"Called from {ctx.guild.id}:{ctx.guild.name} by {ctx.author_id}:{ctx.author.display_name}")
            if guild_info:
                if ctx.channel and ctx.channel_id not in guild_info["whitelisted_channels"]:
                    return
        else:
            print(f"Called by {ctx.author_id}:{ctx.author.display_name}")

        emoji_bytes = BytesIO()
        try:
            emojis = emoji_mashup.create_emoji(
                emoji_bytes,
                background, face, eyes, other)
        except Exception as e:
            await ctx.send(str(e))
            return

        emoji_bytes.seek(0)

        file = discord.File(emoji_bytes, "emojo.png")

        message_emojis = f"{' + '.join(flat(emojis))} ="
        await ctx.send(message_emojis)
        message = await ctx.send(file=file)

        last_call = time.time()

        if guild_info and guild_info.get("manage_emojis"):
            await message.add_reaction('👍')
            await message.add_reaction('👎')

            await asyncio.sleep(5 * 60)
            message = await message.channel.fetch_message(message.id)
            # default values
            positive = 0
            negative = 0
            for reaction in message.reactions:
                if reaction.emoji == '👍':
                    positive = reaction.count - 1
                if reaction.emoji == '👎':
                    negative = reaction.count - 1

            print(positive, negative)
            if positive > negative:
                print(len(ctx.guild.emojis), ctx.guild.emoji_limit)
                while len(ctx.guild.emojis) >= ctx.guild.emoji_limit:
                    print("REACHED {0}".format(ctx.guild.emoji_limit))
                    await pick_emoji(ctx.guild.emojis).delete()

                emoji = await ctx.guild.create_custom_emoji(
                    name="emoji_mashup",
                    image=emoji_bytes.getvalue()
                )
                await message.channel.send(f"Created emoji {emoji}")
            else:
                await message.edit(content=f"Voting ended, emoji not added.\n{message_emojis}")
    else:
        await ctx.send(f"Global cooldown. {'{:.2f}'.format(call_cooldown - (time.time() - last_call))} sec left.")


@slash.slash(name="emoji", description="generates random emojis", guild_ids=config.GUILDS)
async def _emoji(ctx: SlashContext, background=None, face=None, eyes=None, other=None):
    await create_emoji(ctx, background, face, eyes, other)


async def create_supported(ctx: SlashContext, choice: Optional[Categories]):

    embed = discord.Embed()

    if choice:
        embed.add_field(name=f"Supported {choice}", value=" , ".join(emoji_mashup.get_supported(choice)))
    else:
        for category in CATEGORIES:
            embed.add_field(name=f"Supported {category}", value=" , ".join(emoji_mashup.get_supported(category)))

    await ctx.send(embed=embed)


@slash.slash(
    name="supported",
    description="prints the supported emojis by the bot right now.",
    guild_ids=config.GUILDS,
    options=supported_decorator_options)
async def _supported(ctx: SlashContext, choice=None):
    await create_supported(ctx, choice)


bot.run(config.TOKEN)
