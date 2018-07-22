import zoinks.bot
from zoinks.riot_games_api import RiotGamesAPI, REGION

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


class LeagueOfLegends:

    def __init__(self, bot):
        self.bot = bot
        self.api = RiotGamesAPI(self.bot)
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.command()
    async def regions(self, ctx):
        embed = discord.Embed(title='🌎 League of Legends Regions',
                              description='Below is a list of available regions for League of Legends commands.',
                              color=zoinks.bot.color)
        embed.add_field(name='Region Name', value='\n'.join([REGION[key]['name'] for key in REGION.keys()]))
        embed.add_field(name='Usage in Commands', value='\n'.join(REGION.keys()))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LeagueOfLegends(bot))
