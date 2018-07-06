import discord

import logging
import os
import random


COOLSVILLE_GUILD_ID = 462995863539679242
DISABLED_CHANNELS = (462996078430781441, 462996375794221066, 462996408216059914, 462996435839877130)

logger = logging.getLogger(__name__)

FILE_DIR = 'zoinks/data/'

if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

FILE_PATH = os.path.join(FILE_DIR, 'berry.txt')


def create_file(file_path):
    with open(file_path, 'w+') as file:
        file.write(str(0))
        logger.info(f'{file_path} created')


if not os.path.isfile(FILE_PATH):
    create_file(FILE_PATH)


def berry_in_message(message):
    return 'berry' == message.content or 'berry' in message.content.lower()


def valid_text_channel(bot, message):
    return (message.guild is not None and
            message.guild == bot.get_guild(COOLSVILLE_GUILD_ID) and
            message.channel.id not in DISABLED_CHANNELS)


def count_berries():
    with open(FILE_PATH, 'r+') as file:
        count = int(file.read())
        file.seek(0)
        count = count + 1
        file.write(str(count))
        return count


async def send_berry_message(message, berry_count):
    grammar = 'ies' if berry_count != 1 else 'y'
    descriptor = random.choice('nice', 'cool', 'spooky')
    embed = discord.Embed(
        title='🍓 Thanks',
        description='Like, thanks for feeding Scoob!\n\n'
                    f'Scoob has now eaten {berry_count} berr{grammar}. Berry {descriptor}!',
        color=0x4D9C5F)
    embed.set_thumbnail(url='https://media.giphy.com/media/T825g5mLEUqE8/giphy.gif')
    await message.channel.send(embed=embed)


class Berry:
    """Represents a cog for a Discord bot.

    This cog extends the default on_message event function.
    It checks a message containing 'berry' in any valid Discord text channel, then displays
    a nice message showing the current berry count stored in the file_path above.

    Attributes
    ----------
    bot: ZOINKS
        The currently running ZOINKS Discord bot.
    """
    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_message(self, message):
        if berry_in_message(message) and valid_text_channel(self.bot, message):
            berry_count = count_berries()
            await send_berry_message(message=message, berry_count=berry_count)
            logger.info(f'Berry fed to Scoob ({berry_count})')


def setup(bot):
    bot.add_cog(Berry(bot))
