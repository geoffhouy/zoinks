import discord
from discord.ext import commands


command_prefix = '!'
description = 'Like ZOINKS Scoob!'


class ZOINKS(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(command_prefix),
            description=description,
            pm_help=None)

    async def on_ready(self):
        await self.change_presence(game=discord.Game(name=f'ZOINKS! | {command_prefix}help'))

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_error(self, error, context):
        if isinstance(error, commands.errors.CommandNotFound):
            pass
