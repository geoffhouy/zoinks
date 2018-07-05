import discord

import logging
import os


logger = logging.getLogger(__name__)


class Berry:

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
    file_path = 'zoinks/data/'
    file_name = 'berry.txt'
    joined_path = os.path.join(file_path, file_name)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        with open(joined_path, 'w+') as file:
            count = 1
            file.write(str(count))
    else:
        with open(joined_path, 'r+') as file:
            count = int(file.read())
            file.seek(0)
            count = count + 1
            file.write(str(count))
    return count


async def _send_berry_message(message, berry_count):
    embed = discord.Embed(
        title='🍓 Thanks',
        description=f'Like, thanks for feeding Scoob a berry!\n\nScoob has now eaten {berry_count}. Berry nice!',
        color=0x4D9C5F)
    embed.set_thumbnail(url='https://media.giphy.com/media/T825g5mLEUqE8/giphy.gif')
    await message.channel.send(embed=embed)
