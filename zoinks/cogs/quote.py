import discord
from discord.ext import commands

import logging
import random


COOLSVILLE_GUILD_ID = 462995863539679242
DISABLED_CHANNELS = (462996078430781441, 462996375794221066, 462996408216059914, 462996435839877130)

ZOINKS_EMOJI = '<:ZOINKS:463062621134782474>'

QUOTES = ('Some fishing trip this turned out to be. Like, not even a nibble!',
          'Open the mouth. Between the gums. Look out stomach, here it comes!',
          'Like no one seems to be here, Scoob. And by the looks of this pad, I don\'t blame them',
          'I\'m so scared. I wish I had a ham sandwich to calm my nerves!',
          'Well, what do you know? A ham sandwich!',
          'Man, what a pad for a scare in!',
          'I\'ll pay! I\'ll pay! How about 4 bits?',
          '`Are you alright?`\n\nYeah, just as soon as I have 6 or 7 sandwiches.',
          'Well at least you left me the olive.',
          'Sleep nothing. I\'m fixing me a super Shaggy sandwich.',
          'What a nervous night to be walking home from the movies, Scooby Doo. '
          'And all because you had to stay and see "Star: Dog Ranger of the North Woods" twice!',
          '`What\'s an empty old suit of armor doing in the driver\'s seat of this pickup?`\n\n'
          'Maybe he went out for the knight. Get it?',
          'Nobody\'s getting my beautiful hair.',
          'And the ham slice connected to the rye bread, lettuce connected to the boiled egg, '
          'mustard slapped on a salami slice, and the cheese I connected to the deviled ham.',
          '`This mystery\'s got me baffled!`\n\nWell, it\'s got me, like, hungry. When do we eat?',
          'What a close shave! That was almost a catastrophe!',
          '`C\'mon Shaggy, help me open it!`\n\nUh uh, I don\'t like surprises. Especially spooky ones.',
          'Somebody sure is a messy housekeeper.',
          'Leave it to Daphne to pick the wrong door.',
          '`What a groovy spot for a beach party!`\n\nYeah man, I can already taste those chocolate covered hotdogs!',
          'Wow! Like, this place is furnished in early Halloween!',
          '`Things are being to add up!`\n\nYou mean like 2 and 2 are 5?',
          'Velma, who do I know with long and skinny hands?',
          '`Now what do we do?`\n\nLike rest. I\'m pooped.',
          'One for the money, two for the show, three to get ready, and here I go!',
          '`You suppose that\'s the miner moaning?`\n\nLike, if I had a face like that, I\'d moan too.',
          'Lucky for you, I\'m a dog lover! Yuck!',
          'Hey! Look what I found, like, jars of chocolate syrup!\n\n'
          '`Chocolate syrup nothing! That\'s samples of crude oil!`',
          '`There\'s so many groovy things to do!`\n\n'
          'Yeah, like, swimming and eating, and, tennis and eating, and, driving and eating, and, eating and...huh?',
          'I just remembered a dental appointment back in town!',)

logger = logging.getLogger(__name__)


async def in_correct_channel(ctx):
    return (ctx.guild is not None and
            ctx.guild.id == COOLSVILLE_GUILD_ID and
            ctx.message.channel.id not in DISABLED_CHANNELS)


class Quote:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.command('quote')
    @commands.check(in_correct_channel)
    async def quote(self, ctx):
        await ctx.message.channel.send(
            embed=discord.Embed(title=f'{ZOINKS_EMOJI} Quote', description=random.choice(QUOTES), color=0x4D9C5F))
        logger.info('Quote command used')


def setup(bot):
    bot.add_cog(Quote(bot))
