import discord
from discord.ext import commands

import aiohttp
import logging
import os


command_prefix = '!'
description = 'Like ZOINKS Scoob!'

logger = logging.getLogger(__name__)


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

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name=f'ZOINKS! | {self.command_prefix}help'))
        logger.info(f'{self.user} logged in')

    async def on_command_error(self, ctx, error):
        pass

    def load_extensions(self, extensions: set=()):
        if len(extensions) > 0:
            for extension in extensions:
                try:
                    self.load_extension(extension)
                except ModuleNotFoundError as e:
                    logger.warning(e)
