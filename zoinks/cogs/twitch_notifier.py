import config

import discord

import logging


logger = logging.getLogger(__name__)


class TwitchNotifier:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_member_update(self, before, after):
        if after.guild == self.bot.guild:
            if (after.activity
                    and isinstance(after.activity, discord.Streaming)
                    and after.activity.twitch_name is not None
                    and not isinstance(before.activity, discord.Streaming)):
                channel = self.bot.get_channel(self.bot.notification_channel)
                await _send_notification_message(channel, after)
                logger.info(f'Live notification displayed for {after}')


def setup(bot):
    bot.add_cog(TwitchNotifier(bot))


async def _send_notification_message(channel, member):
    embed = discord.Embed(
        title=member.activity.name,
        description=f'I\'m streaming {member.activity.details}!',
        url=f'https://www.twitch.tv/{member.activity.twitch_name}',
        color=0x4D9C5F)
    embed.set_author(name=member.display_name, icon_url=member.avatar_url)
    embed.set_footer(text='Live on Twitch')

    message = await channel.send('@everyone', embed=embed)
    embed.timestamp = message.created_at
    await message.edit(content=None, embed=embed)
