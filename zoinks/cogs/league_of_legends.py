import zoinks.bot

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


class LeagueOfLegends:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.group(name='lol')
    async def lol(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(
                title='⚠ Error',
                description='The League of Legends command needs an argument.'),
                color=zoinks.bot.color)


def setup(bot):
    bot.add_cog(LeagueOfLegends(bot))
