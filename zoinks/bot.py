from config import Coolsville

import discord
from discord.ext import commands

import aiohttp
import logging


command_prefix = '!'
description = 'Like ZOINKS Scoob!'

extensions = ('zoinks.cogs.new_member',
              'zoinks.cogs.pin_popular',
              'zoinks.cogs.twitch_notifier',
              'zoinks.cogs.youtube_notifier')
              #'zoinks.cogs.webhooks',
              #'zoinks.cogs.league_of_legends',
              #'zoinks.cogs.realm_royale')

logger = logging.getLogger(__name__)


class ZOINKS(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(
            command_prefix=command_prefix,
            description=description,
            pm_help=None)
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.guild = None
        self.rules_channel = None
        self.notification_channel = None
        self.pin_disabled_channels = ()

        self._load_extensions()

    def _load_extensions(self):
        for extension in extensions:
            try:
                self.load_extension(extension)
            except ModuleNotFoundError as e:
                logger.warning(e)

    def _set_defaults(self):
        self.guild = self.get_guild(id=Coolsville.GUILD_ID)
        self.rules_channel = self.get_channel(id=Coolsville.RULES_CHANNEL_ID)
        self.notification_channel = self.get_channel(id=Coolsville.NOTIFICATION_CHANNEL_ID)
        self.pin_disabled_channels = Coolsville.PIN_DISABLED_CHANNELS
        logger.info(f'Defaults set for {Coolsville.__name__}')

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        self._set_defaults()
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
