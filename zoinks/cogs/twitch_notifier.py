import discord

import logging


logger = logging.getLogger(__name__)


class TwitchNotifier:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_member_update(self, before, after):
        if after.guild == self.bot.guild:
            if ('content creator' in [role.name.lower() for role in after.roles]
                    and after.activity
                    and isinstance(after.activity, discord.Streaming)
                    and after.activity.twitch_name is not None
                    and not isinstance(before.activity, discord.Streaming)):
                await _send_notification_message(self.bot.notification_channel, after)
                logger.info(f'Live notification displayed for {after}')


def setup(bot):
    bot.add_cog(TwitchNotifier(bot))


async def _send_notification_message(channel, member):
    embed = discord.Embed(
        title=member.activity.name,
        description=f'Playing {member.activity.details}',
        url=f'https://www.twitch.tv/{member.activity.twitch_name}',
        color=0x6441A4)
    embed.set_author(name=member.activity.twitch_name,
                     url=f'https://www.twitch.tv/{member.activity.twitch_name}',
                     icon_url=member.avatar_url)
    await channel.send(f'Hey @everyone, {member.mention} is now live on Twitch!', embed=embed)
