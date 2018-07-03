import discord
from discord.ext import commands

import aiohttp
import logging


command_prefix = '!'
description = 'Like ZOINKS Scoob!'

extensions = ('zoinks.cogs.new_member',
              'zoinks.cogs.pin_popular')
              #'zoinks.cogs.webhooks',
              #'zoinks.cogs.league_of_legends',
              #'zoinks.cogs.realm_royale')

logger = logging.getLogger(__name__)


class ZOINKS(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(command_prefix),
            description=description,
            pm_help=None)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self._load_extensions()

    def _load_extensions(self):
        for extension in extensions:
            try:
                self.load_extension(extension)
            except ModuleNotFoundError as e:
                logger.warning(e)

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name=f'ZOINKS! | {command_prefix}help'))
        logger.info(f'{self.user} logged in')

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        ignored = (commands.errors.CommandNotFound, commands.errors.DisabledCommand)
        if isinstance(error, ignored):
            return

        ignored = (commands.errors.UserInputError, commands.errors.MissingRequiredArgument,
                   commands.errors.TooManyArguments)
        if isinstance(error, ignored):
            # send help for specific command
            return

        logger.info(f'Ignoring on_command_error: {error}')
