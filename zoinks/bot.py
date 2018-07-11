import discord
from discord.ext import commands

import aiohttp
import logging


command_prefix = '!'
description = 'Like ZOINKS Scoob!'

extensions = ('zoinks.cogs.berry',
              'zoinks.cogs.new_member',
              'zoinks.cogs.quote',
              'zoinks.cogs.pin_popular',
              'zoinks.cogs.twitch_notifier',
              'zoinks.cogs.youtube_notifier',
              #'zoinks.cogs.webhooks',
              'zoinks.cogs.league_of_legends')
              #'zoinks.cogs.realm_royale')

logger = logging.getLogger(__name__)


class ZOINKS(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(
            command_prefix=command_prefix,
            description=description,
            pm_help=None)
        self.session = aiohttp.ClientSession(loop=self.loop)

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

        do_nothing = (commands.errors.CommandNotFound, commands.errors.DisabledCommand)
        if isinstance(error, do_nothing):
            return

        warn = (commands.errors.BadArgument, commands.errors.MissingRequiredArgument,
                commands.errors.TooManyArguments, commands.errors.UserInputError)
        if isinstance(error, warn):
            await ctx.send(embed=discord.Embed(
                title='⚠ Error',
                description=f'{str(error)}\n\nUse `{command_prefix}help {ctx.command.name}` for more information.',
                color=0xFFCB00))
            return

        logger.info(f'{ctx.command.name} command exception ignored: {error}')
