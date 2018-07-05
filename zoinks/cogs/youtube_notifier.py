import discord

import logging


logger = logging.getLogger(__name__)


class YouTubeNotifier:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            member = self.bot.config.guild.get_member(message.author.id)
            if member and 'content creator' in [role.name.lower() for role in member.roles]:
                if 'youtube' in message.content or 'youtu.be' in message.content and message.embeds:
                    await _send_notification_message(self.bot.config.notification_channel, message)
                    logger.info(f'YouTube notification displayed for {message.author.display_name}')


def setup(bot):
    bot.add_cog(YouTubeNotifier(bot))


async def _send_notification_message(channel, message):
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
