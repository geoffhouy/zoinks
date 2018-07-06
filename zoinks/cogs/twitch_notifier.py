import discord

import logging


COOLSVILLE_GUILD_ID = 462995863539679242
NOTIFICATIONS_CHANNEL = 462996435839877130
CONTENT_CREATOR_ROLE = 'content creator'

logger = logging.getLogger(__name__)


def valid_status_change(before, after):
    return (CONTENT_CREATOR_ROLE in [role.name.lower() for role in after.roles] and
            isinstance(after.activity, discord.Streaming) and
            after.activity.twitch_name is not None and
            not isinstance(before.activity, discord.Streaming))


async def send_notification_message(channel, member):
    embed = discord.Embed(
        title=member.activity.name,
        description=f'Playing {member.activity.details}',
        url=f'https://www.twitch.tv/{member.activity.twitch_name}',
        color=0x6441A4)
    embed.set_author(name=member.activity.twitch_name,
                     url=f'https://www.twitch.tv/{member.activity.twitch_name}',
                     icon_url=member.avatar_url)
    await channel.send(f'Hey @everyone, {member.mention} is now live on Twitch!', embed=embed)


class TwitchNotifier:
    """Represents a cog for a Discord bot.

    This cog extends the default on_member_update event function.
    It uses Discord's built-in activities to notify the specified channel in the specified
    guild that a Content Creator, a specified role, has gone live on Twitch.*

    *The channel and guild are specified at the time of creation of the bot. See its config attribute.

    Attributes
    ----------
    bot: ZOINKS
        The currently running ZOINKS Discord bot.
    """
    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_member_update(self, before, after):
        if after.guild == self.bot.get_guild(COOLSVILLE_GUILD_ID):
            if valid_status_change(before, after):
                await send_notification_message(channel=self.bot.get_channel(NOTIFICATIONS_CHANNEL), member=after)
                logger.info(f'Live notification displayed for {after}')


def setup(bot):
    bot.add_cog(TwitchNotifier(bot))
