import discord

import logging
import os


logger = logging.getLogger(__name__)

file_dir = 'zoinks/data/'
file_path = os.path.join(file_dir, 'berry.txt')


def _create_file():
    with open(file_path, 'w+') as file:
        file.write(str(0))
        logger.info(f'{file_path} created')


if not os.path.exists(file_dir):
    os.makedirs(file_dir)
    _create_file()


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
        if _berry_in_message(message) and _in_valid_text_channel(self.bot, message):
            berry_count = _count_berry()
            await _send_berry_message(message=message, berry_count=berry_count)
            logger.info(f'Berry fed to Scoob ({berry_count})')


def setup(bot):
    bot.add_cog(Berry(bot))


def _berry_in_message(message):
    return 'berry' == message.content or 'berry' in message.content.lower()


def _in_valid_text_channel(bot, message):
    return (message.guild is not None and
            message.guild == bot.config.guild and
            message.channel.id not in bot.config.disabled_channels)


def _count_berry():
    with open(file_path, 'r+') as file:
        count = int(file.read())
        file.seek(0)
        count = count + 1
        file.write(str(count))
        return count


async def _send_berry_message(message, berry_count):
    grammar = 'berries' if berry_count != 1 else 'berry'
    embed = discord.Embed(
        title='🍓 Thanks',
        description='Like, thanks for feeding Scoob!\n\n'
                    f'Scoob has now eaten {berry_count} {grammar}. Berry nice!',
        color=0x4D9C5F)
    embed.set_thumbnail(url='https://media.giphy.com/media/T825g5mLEUqE8/giphy.gif')
    await message.channel.send(embed=embed)
