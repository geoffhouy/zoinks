import zoinks.bot

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


class Fortnite:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.group(name='fn')
    async def fn(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(
                title='⚠ Error',
                description='The Fortnite command needs an argument.'),
                color=zoinks.bot.color)


def setup(bot):
    bot.add_cog(Fortnite(bot))
