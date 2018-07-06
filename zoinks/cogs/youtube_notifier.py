import discord

import logging


COOLSVILLE_GUILD_ID = 462995863539679242
NOTIFICATIONS_CHANNEL = 462996435839877130
CONTENT_CREATOR_ROLE = 'content creator'

logger = logging.getLogger(__name__)


async def valid_youtube_url(message):
    return 'youtube' in message.content.lower() or 'youtu.be' in message.content.lower() and message.embeds


async def send_notification_message(channel, message):
    video_embed = None
    for embed in message.embeds:
        embed = embed.to_dict()
        if embed.get('type') == 'video':
            video_embed = embed
            break
    embed = discord.Embed(title=video_embed.get('title'),
                          description=video_embed.get('description'),
                          url=video_embed.get('url'),
                          color=0xFF0000)
    embed.set_author(name=video_embed.get('author').get('name'),
                     url=video_embed.get('author').get('url'),
                     icon_url=message.author.avatar_url)
    embed.set_image(url=video_embed.get('thumbnail').get('url'))
    await channel.send(content=f'Hey @everyone, {message.author.mention} uploaded a new YouTube video!', embed=embed)


class YouTubeNotifier:
    """Represents a cog for a Discord bot.

    This cog extends the default on_message event function.
    It checks its direct message channels for YouTube URLs from a Content Creator, a specified role in
    a specified guild, then notifies the specified channel in said guild that the message sender
    has uploaded/shared a new YouTube video.

    *The channel and guild are specified at the time of creation of the bot. See its config attribute.

    Attributes
    ----------
    bot: ZOINKS
        The currently running ZOINKS Discord bot.
    guild:
        The placeholder for the current guild object.
    """
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            if self.guild is None:
                self.guild = self.bot.get_guild(COOLSVILLE_GUILD_ID)

            member = self.guild.get_member(message.author.id)

            if (member is not None and
                    CONTENT_CREATOR_ROLE in [role.name.lower() for role in member.roles] and
                    valid_youtube_url(message=message)):
                await send_notification_message(channel=self.bot.get_channel(NOTIFICATIONS_CHANNEL),
                                                message=message)
                logger.info(f'YouTube notification displayed for {message.author.display_name}')


def setup(bot):
    bot.add_cog(YouTubeNotifier(bot))
