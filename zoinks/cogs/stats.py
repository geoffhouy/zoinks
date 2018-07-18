import zoinks.bot
import zoinks.utils.file as file_utils

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
FILE_NAME = 'stats.json'
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
                new = merged_dict.get(key).get(nested_key, 0)
                old = nested_dict.get(nested_key, 0)
                diff = abs(new - old)
                if diff > 0:
                    merged_dict[key][nested_key] = old + diff

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

    async def save(self, manual=False):
        data = {'messages_read_in': self.messages_read_in,
                'commands_used_in': self.commands_used_in,
                'berries_consumed_in': self.berries_consumed_in}

        with open(FILE_PATH, 'r+') as file:
            file_data = json.load(file)
            if file_data != data:
                file.seek(0)
                file.truncate()
                json.dump(merge_nested_dicts(data, file_data), file, indent=4)
                if manual:
                    logger.info(f'Manually saved {self.__class__.__name__} data')
                else:
                    logger.info(f'Saved {self.__class__.__name__} data')

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
        await self.save(manual=True)
        await ctx.author.send(embed=discord.Embed(
            title='✅ Manual Save',
            description=f'{self.__class__.__name__} data has been saved successfully.',
            color=zoinks.bot.color))

    def bot_uptime(self):
        uptime = time.time() - self.bot.start_time

        minutes, seconds = divmod(uptime, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        fmt = f'{int(hours):01d} hours, {int(minutes):01d} minutes, {seconds:01.2f} seconds'
        if days > 0:
            fmt = f'{int(days):01d} days, {fmt}'

        return fmt

    @commands.command()
    async def uptime(self, ctx):
        await ctx.send(embed=discord.Embed(
            title='⏱ Uptime',
            description=f'{self.bot.user.mention} has been online for {self.bot_uptime()}.',
            color=zoinks.bot.color))

    @commands.command(aliases=['about', 'info', 'zoinks'])
    @commands.check(lambda ctx: ctx.guild)
    async def stats(self, ctx):
        embed = discord.Embed(
            title=f'<:ZOINKS:463062621134782474> {str(self.bot.user.name)} Bot',
            description=f'{self.bot.user.mention} is an open-source bot. View the latest changes '
                        'by clicking [here](https://github.com/geoffhouy/zoinks/commits/master).',
            color=zoinks.bot.color)

        owner = (await self.bot.application_info()).owner
        embed.set_author(name=owner.display_name,
                         icon_url=owner.avatar_url,
                         url='https://github.com/geoffhouy')

        embed.add_field(name='⏱ Uptime',
                        value=f'{self.bot.user.mention} has been online for {self.bot_uptime()}.',
                        inline=False)

        members = set(self.bot.get_all_members())
        members_online = sum(1 for member in members if member.status != discord.Status.offline)
        embed.add_field(name='🚶 Members',
                        value=f'{len(members)} ({members_online} online)')

        channels = [channel for channel in self.bot.get_all_channels()]
        text_channels = sum(1 for channel in channels if type(channel) == discord.channel.TextChannel)
        embed.add_field(name='📺 Channels',
                        value=f'{len(channels)} ({text_channels} text channels)')

        embed.add_field(name='🖥 Guilds',
                        value=str(len(self.bot.guilds)))

        messages_read = self.messages_read_in.get(str(ctx.guild.id), 0)
        total_messages_read = sum(self.messages_read_in.values())
        embed.add_field(name='📥 Messages Read',
                        value=f'{total_messages_read} ({messages_read} here)')

        commands_used = self.commands_used_in.get(str(ctx.guild.id), 0)
        total_commands_used = sum(self.commands_used_in.values())
        embed.add_field(name='📤 Commands Used',
                        value=f'{total_commands_used} ({commands_used} here)')

        berries_consumed = self.berries_consumed_in.get(str(ctx.guild.id), 0)
        total_berries_consumed = sum(self.berries_consumed_in.values())
        embed.add_field(name='🍓 Berries Fed To Scoob',
                        value=f'{total_berries_consumed} ({berries_consumed} here)')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
