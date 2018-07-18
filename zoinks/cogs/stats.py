import zoinks.bot
import zoinks.utils.files as file_utils

import discord
from discord.ext import commands

import asyncio
import json
import logging
import os
import random
import time
from collections import defaultdict


logger = logging.getLogger(__name__)

FILE_DIR = 'zoinks/data/'
FILE_NAME = f'{__name__}.json'
FILE_PATH = os.path.join(FILE_DIR, FILE_NAME)

if not os.path.isfile(FILE_PATH):
    file_utils.new_json_file(
        file_dir=FILE_DIR,
        file_name=FILE_NAME,
        init_dict={'messages_read_in': {}, 'commands_used_in': {}, 'berries_consumed_in': {}})


def merge_nested_dicts(dict1: dict, dict2: dict):
    merged_dict = defaultdict(dict)

    merged_dict.update(dict1)
    for key, nested_dict in dict2.items():
        if merged_dict.get(key) is None:
            merged_dict[key].update(nested_dict)
        else:
            for nested_key, value in nested_dict.items():
                merged_dict[key][nested_key] = merged_dict.get(key).get(nested_key, 0) + nested_dict.get(nested_key, 0)

    return merged_dict


class Stats:

    def __init__(self, bot):
        self.bot = bot

        self.messages_read_in = {}
        self.commands_used_in = {}
        self.berries_consumed_in = {}

        self.load()
        self.bot.loop.create_task(self.save_every(60 * 10))

        logger.info(f'{self.__class__.__name__} loaded')

    def load(self):
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)

        self.messages_read_in = data.get('messages_read_in', {})
        self.commands_used_in = data.get('commands_used_in', {})
        self.berries_consumed_in = data.get('berries_consumed_in', {})

    async def save(self):
        data = {'messages_read_in': self.messages_read_in,
                'commands_used_in': self.commands_used_in,
                'berries_consumed_in': self.berries_consumed_in}

        with open(FILE_PATH, 'r+') as file:
            file_data = json.load(file)
            if file_data != data:
                file.seek(0)
                file.truncate()
                json.dump(merge_nested_dicts(data, file_data), file, indent=4)
                logger.info('Saved data')

    async def save_every(self, delay: int = 60 * 5):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.save()
            await asyncio.sleep(delay)

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        guild_id = str(message.guild.id)

        self.messages_read_in[guild_id] = self.messages_read_in.get(guild_id, 0) + 1

        if 'berry' in message.content.lower() or 'berry' == message.content.lower():
            self.berries_consumed_in[guild_id] = self.berries_consumed_in.get(guild_id, 0) + 1

            grammar = 'ies' if self.berries_consumed_in[guild_id] != 1 else 'y'
            descriptor = random.choice(['nice', 'cool', 'groovy', 'spooky'])
            embed = discord.Embed(
                title='🍓 Thanks',
                description='Like, thanks for feeding Scoob!\n\n'
                            f'Scoob has now eaten {self.berries_consumed_in[guild_id]} berr{grammar}. '
                            f'Berry {descriptor}!',
                color=zoinks.bot.color)
            embed.set_thumbnail(url='https://media.giphy.com/media/T825g5mLEUqE8/giphy.gif')

            await message.channel.send(embed=embed)

    async def on_command_completion(self, ctx):
        if ctx.guild is None:
            return

        self.commands_used_in[str(ctx.guild.id)] = self.commands_used_in.get(str(ctx.guild.id), 0) + 1

    @commands.command(aliases=['save'], hidden=True)
    @commands.is_owner()
    async def manualsave(self, ctx):
        await self.save()
        await ctx.author.send(embed=discord.Embed(
            title='✅ Manual Save',
            description=f'{self.__class__.__name__} data has been successfully saved.',
            color=zoinks.bot.color))

    @commands.command()
    async def uptime(self, ctx):
        uptime = time.time() - self.bot.start_time
        m, s = divmod(uptime, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        fmt = f'{int(d):02d}:{int(h):02d}:{int(m):02d}:{s:05.2f}'
        await ctx.send(embed=discord.Embed(
            title='⏱ Uptime',
            description=f'{self.bot.__class__.__name__} has been online for {fmt}.',
            color=zoinks.bot.color))


def setup(bot):
    bot.add_cog(Stats(bot))
