import zoinks.bot

import discord
from discord.ext import commands

import logging
import random


logger = logging.getLogger(__name__)

ZOINKS_EMOJI = '<:ZOINKS:463062621134782474>'

with open('zoinks/resources/text/quotes.txt', 'r') as quotes_file:
    quotes = [line.rstrip().replace('|', '\n') for line in quotes_file]


class Random:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quote(self, ctx):
        quote = random.choice(quotes)
        await ctx.send(
            embed=discord.Embed(title=f'{ZOINKS_EMOJI} Quote', description=quote, color=zoinks.bot.color))

    @commands.command()
    async def roll(self, ctx):
        roll = random.randint(1, 6)
        await ctx.send(
            embed=discord.Embed(title='🎲 Roll', description=f'You rolled a {roll}.', color=zoinks.bot.color))


def setup(bot):
    bot.add_cog(Random(bot))
