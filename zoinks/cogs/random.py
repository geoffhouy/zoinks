import zoinks.bot

import discord
from discord.ext import commands

import asyncio
import logging
import random


logger = logging.getLogger(__name__)

ZOINKS_EMOJI = '<:ZOINKS:463062621134782474>'

with open('zoinks/resources/text/quotes.txt', 'r') as quotes_file:
    quotes = [line.rstrip().replace('|', '\n') for line in quotes_file]

responses = (
    'It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes - definitely.', 'You may rely on it.',
    'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.',
    'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.',
    'Concentrate and ask again.',
    'Don\'t count on it.', 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtful.')


class Random:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball'])
    async def magic8ball(self, ctx):
        """Turns the Magic 8-Ball upwards for a response."""
        response = random.choice(responses)
        await ctx.send(embed=discord.Embed(title=f'🎱 Magic 8-Ball',
                                           description=response,
                                           color=zoinks.bot.color))

    @commands.command()
    async def quote(self, ctx):
        """Displays a random Shaggy quote."""
        quote = random.choice(quotes)
        await ctx.send(embed=discord.Embed(title=f'{ZOINKS_EMOJI} Shaggy Quote',
                                           description=quote,
                                           color=zoinks.bot.color))

    @commands.command()
    async def roll(self, ctx):
        """Rolls a 6-sided die."""
        roll = random.randint(1, 6)
        await ctx.send(embed=discord.Embed(title='🎲 Roll',
                                           description=f'You rolled a {roll}.',
                                           color=zoinks.bot.color))

    @commands.command()
    async def scramble(self, ctx):
        """Allows the user to play a word scramble with the bot."""
        embed = discord.Embed(title='📚 Scrambled Word Puzzle', color=zoinks.bot.color)

        async with self.bot.session.post(url='http://watchout4snakes.com/wo4snakes/Random/RandomWord') as response:
            if response.status >= 400:
                embed.description = 'Unable to connect to the word generator. Please try again later.'
                return await ctx.send(embed=embed)
            else:
                word = await response.text()

        scrambled_word = ''.join(random.sample(word, len(word)))

        embed.description = f'The scrambled word is `{scrambled_word}`.\n\nYou have 30 seconds to unscramble the word.'
        await ctx.send(embed=embed)

        def check(message):
            return message.content == word and message.channel == ctx.channel

        try:
            answer = await ctx.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            embed.description = f'Nobody solved the puzzle.\n\nThe word was `{word}`.'
            await ctx.send(embed=embed)
        else:
            embed.description = f'{answer.author.name} solved the puzzle!\n\nThe word was `{word}`.'
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Random(bot))
