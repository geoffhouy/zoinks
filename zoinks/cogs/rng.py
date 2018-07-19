import zoinks.bot

import discord
from discord.ext import commands

import asyncio
import logging
import re
import random


logger = logging.getLogger(__name__)

ZOINKS_EMOJI = '<:ZOINKS:463062621134782474>'

with open('zoinks/resources/text/mad_libs.txt', 'r', encoding='utf8') as file:
    mad_libs = [line.rstrip() for line in file if not line.startswith('#')]

with open('zoinks/resources/text/quotes.txt', 'r', encoding='utf8') as file:
    quotes = [line.rstrip().replace('|', '\n') for line in file]

responses = (
    'It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes - definitely.', 'You may rely on it.',
    'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.',
    'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.',
    'Concentrate and ask again.',
    'Don\'t count on it.', 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtful.')


class RNG:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.command(aliases=['madlib'])
    async def madlibs(self, ctx):
        """Starts a game of Mad Libs."""
        timeout = 30
        regex = re.compile(r'`(.+?)`+?')

        embed = discord.Embed(title='📓 Mad Libs', color=zoinks.bot.color)

        embed.description = f'The game will begin shortly.\n\nYou have {timeout} seconds to respond with each word.'
        await ctx.send(embed=embed)
        await asyncio.sleep(3)

        mad_lib = random.choice(mad_libs)
        blanks = regex.findall(mad_lib)
        answers = []

        def check(message):
            return message.channel == ctx.channel and not message.author.bot

        for blank in blanks:
            grammar = 'n' if blank.lower().startswith(('a', 'e', 'i', 'o', 'u')) else ''
            embed.description = f'I need a{grammar} `{blank}`.'
            await ctx.send(embed=embed, delete_after=timeout)

            try:
                answer = await ctx.bot.wait_for('message', check=check, timeout=timeout)
            except asyncio.TimeoutError:
                embed.description = 'Nobody responded in time.\n\nThis game has been cancelled.'
                return await ctx.send(embed=embed)
            else:
                answers.append(answer.content)

            await asyncio.sleep(1)

        mad_lib = regex.sub(lambda replace: str(answers.pop(0)), mad_lib)

        embed.description = f'The Mad Lib is complete!\n\n{mad_lib}'
        await ctx.send(embed=embed)

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
        """Starts a scrambled word puzzle."""
        timeout = 30

        embed = discord.Embed(title='📚 Scrambled Word Puzzle', color=zoinks.bot.color)

        async with self.bot.session.post(url='http://watchout4snakes.com/wo4snakes/Random/RandomWord') as response:
            if response.status >= 400:
                embed.description = 'Unable to connect to the word generator. Please try again later.'
                return await ctx.send(embed=embed)
            else:
                word = await response.text()

        scrambled_word = ''.join(random.sample(word, len(word)))

        embed.description = (f'The scrambled word is `{scrambled_word}`.\n\n' 
                             f'You have {timeout} seconds to respond with the unscrambled word.')
        await ctx.send(embed=embed)

        def check(message):
            return message.content == word and message.channel == ctx.channel

        try:
            answer = await ctx.bot.wait_for('message', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            embed.description = f'Nobody solved the puzzle.\n\nThe word was `{word}`.'
            await ctx.send(embed=embed)
        else:
            embed.description = f'{answer.author.name} solved the puzzle!\n\nThe word was `{word}`.'
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RNG(bot))
