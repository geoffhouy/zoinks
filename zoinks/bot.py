import discord
from discord.ext import commands

import aiohttp
import logging
import os
import time


logger = logging.getLogger(__name__)

command_prefix = '!'
description = 'Like ZOINKS Scoob!'

color = 0x4D9C5F


class ZOINKS(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(
            command_prefix=command_prefix,
            description=description,
            pm_help=None)

        self.session = aiohttp.ClientSession(loop=self.loop)

        extensions = set([
            f'zoinks.cogs.{os.path.splitext(module)[0]}'
            for module in os.listdir('zoinks/cogs/')
            if module.endswith('.py') and 'init' not in module])

        self.load_extensions(extensions)

        self.start_time = time.time()

    def load_extensions(self, extensions: set=()):
        if len(extensions) > 0:
            for extension in extensions:
                try:
                    self.load_extension(extension)
                except ModuleNotFoundError as e:
                    logger.warning(e)

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name=f'ZOINKS! | {self.command_prefix}help'))
        logger.info(f'{self.user} took {(time.time() - self.start_time):.6f} seconds to login')

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_message_edit(self, before, after):
        await self.process_commands(after)

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignore = (commands.errors.CommandNotFound, commands.errors.UserInputError)
        if isinstance(error, ignore):
            return

        display = (commands.errors.DisabledCommand, commands.errors.NoPrivateMessage,
                   commands.errors.CheckFailure, commands.errors.BadArgument,
                   commands.errors.MissingRequiredArgument, commands.errors.TooManyArguments)
        if isinstance(error, display):
            return await ctx.send(embed=discord.Embed(title='⚠ Error', description=str(error), color=color))

        logger.info(f'Command exception not handled: {error}')
