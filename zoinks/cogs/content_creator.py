import discord

import logging


logger = logging.getLogger(__name__)

COOLSVILLE_GUILD = 462995863539679242


def now_streaming_on_twitch(before, after):
    return (not isinstance(before.activity, discord.Streaming) and
            isinstance(after.activity, discord.Streaming) and
            after.activity.twitch_name is not None)


class ContentCreator:

    def __init__(self, bot):
        self.bot = bot

    async def on_member_update(self, before, after):
        if 'content creator' in [role.name.lower() for role in after.roles] and now_streaming_on_twitch(before, after):
            channel = discord.utils.get(after.guild.channels, name='notifications')
            await channel.send(
                content='Hey @everyone, {after.mention} is now live on Twitch!',
                embed=discord.Embed(
                    title=f'🎥 Twitch',
                    description=f'@everyone, {after.activity.name} is playing `{after.activity.details}`!',
                    url=f'https://www.twitch.tv/{after.activity.twitch_name}',
                    color=0x6441A4))

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            guild = self.bot.get_guild(id=COOLSVILLE_GUILD)
            if guild is not None and message.author in guild.members:
                member = guild.get_member(user_id=message.author.id)
                if 'content creator' in [role.name.lower() for role in member.roles] and message.embeds:
                    channel = discord.utils.get(guild.channels, name='notifications')

                    for video_embed in message.embeds:
                        video_embed = video_embed.to_dict()

                        provider = video_embed.get('provider').get('name')
                        if provider != 'Twitch' and provider != 'YouTube':
                            continue

                        embed = discord.Embed(url=video_embed.get('url'),
                                              color=0xFF0000 if provider == 'YouTube' else 0x6441A4)

                        content = f'Hey @everyone, {member.mention}'

                        if provider == 'YouTube':
                            embed.title = video_embed.get('title')
                            embed.description = video_embed.get('description')
                            embed.set_author(name=video_embed.get('author').get('name'),
                                             url=video_embed.get('author').get('url'))
                            content = f'{content} has uploaded a new YouTube video!'
                        else:
                            embed.title = video_embed.get('description')
                            embed.set_author(name=video_embed.get('title').split('-')[0],
                                             url=video_embed.get('url'))
                            content = f'{content} is now live on Twitch!'

                        embed.set_image(url=video_embed.get('thumbnail').get('url'))

                        await channel.send(content=content, embed=embed)


def setup(bot):
    bot.add_cog(ContentCreator(bot))
