import zoinks.bot

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


class RealmRoyale:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.group(name='rr')
    async def rr(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(
                title='⚠ Error',
                description='The Realm Royale command needs an argument.'),
                color=zoinks.bot.color)


def setup(bot):
    bot.add_cog(RealmRoyale(bot))
