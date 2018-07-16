import zoinks.bot
from zoinks.bot import ZOINKS

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)

COOLSVILLE_GUILD_ID = 0
COOLSVILLE_RULES_CHANNEL_ID = 0
COOLSVILLE_NOTIFICATIONS_CHANNEL_ID = 0
COOLSVILLE_GUEST_ROLE_ID = 0
COOLSVILLE_CONTENT_CREATOR_ROLE_ID = 0
COOLSVILLE_PIN_DISABLED_CHANNEL_IDS = (0, 1)


def message_from_video_embed(video_embed: dict, member: discord.Member):
    """Builds a message from the specified embedded video.

    :param video_embed: The embedded video in the original message.
    :param member: The member who sent the original message.
    :type video_embed: dict
    :type member: discord.Member
    :return: The new message with content and an embed.
    :rtype: tuple
    """
    provider = video_embed.get('provider').get('name')

    embed = discord.Embed(
        title=video_embed.get('title') if provider == 'YouTube' else video_embed.get('description'),
        description=video_embed.get('description') if provider == 'YouTube' else '',
        url=video_embed.get('url'),
        color=0xFF0000 if provider == 'YouTube' else 0x6441A4)

    embed.set_author(
        name=video_embed.get('author').get('name') if provider == 'YouTube' else video_embed.get('title').split('-')[0],
        url=video_embed.get('author').get('url') if provider == 'YouTube' else video_embed.get('url'))

    embed.set_image(
        url=video_embed.get('thumbnail').get('url'))

    content = f'Hey @everyone, {member.mention}'
    if provider == 'YouTube':
        content = f'{content} uploaded a new YouTube video!'
    else:
        content = f'{content} is now live on Twitch!'

    return content, embed


class Coolsville:
    """Represents a cog for a Discord bot.

    This cog provides utilities exclusively for the Coolsville server. The above module constants dictate which
    guild, channels, and roles will be used.
    """
    def __init__(self, bot: ZOINKS):
        """Constructs a new Coolsville object.

        :param bot: The currently running Discord bot.
        :type bot: ZOINKS
        """
        self.bot = bot
        self.pin_threshold = 10
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_member_join(self, member):
        """Automates the new member experience.

        1. Assigns the 'Guest' role to the new member.
        2. Sends the new member a message suggesting to read the '#rules' channel.

        Note: In Coolsville, the 'Guest' role can only read and write in the '#rules' channel.

        :param member: The member that joined the guild.
        :type member: discord.Member
        :return: None
        """
        if member.guild.id != COOLSVILLE_GUILD_ID:
            return

        if member.bot:
            return

        await member.add_roles(discord.Object(id=COOLSVILLE_GUEST_ROLE_ID))
        rules_channel = self.bot.get_guild(id=COOLSVILLE_GUILD_ID).get_channel(channel_id=COOLSVILLE_RULES_CHANNEL_ID)
        await member.send(embed=discord.Embed(
            title='👋 Welcome',
            description=f'Like, welcome to {member.guild}!\n\nPlease remember to read over '
                        f'{rules_channel.mention} to familiarize yourself with what\'s allowed in '
                        f'{member.guild}.\n\n If you have any comments, questions, or concerns, '
                        'please contact an Administrator or a Moderator.\n\nEnjoy your stay!',
            color=zoinks.bot.color))
        logger.info(f'{member} joined {member.guild}')

    async def on_member_update(self, before, after):
        """Notifies guild members that a 'Content Creator' just started streaming on Twitch.

        :param before: The member before being updated.
        :param after: The member after being updated.
        :type before: discord.Member
        :type after: discord.Member
        :return: None
        """
        if after.guild.id != COOLSVILLE_GUILD_ID:
            return

        if COOLSVILLE_CONTENT_CREATOR_ROLE_ID not in [role.id for role in after.roles]:
            return

        if (isinstance(after.activity, discord.Streaming) and
                after.activity.twitch_name is not None and
                not isinstance(before.activity, discord.Streaming)):
            notifications_channel = self.bot.get_guild(
                id=COOLSVILLE_GUILD_ID).get_channel(
                id=COOLSVILLE_NOTIFICATIONS_CHANNEL_ID)
            await notifications_channel.send(
                content=f'Hey @everyone, {after.mention} is now live on Twitch!',
                embed=discord.Embed(
                    title=f'🎥 Twitch',
                    description=f'@everyone, {after.activity.name} is playing `{after.activity.details}`!',
                    url=f'https://www.twitch.tv/{after.activity.twitch_name}',
                    color=0x6441A4))

    async def on_message(self, message):
        """Notifies guild members that a 'Content Creator' just uploaded a YouTube video or started streaming on Twitch.

        When a direct message containing a link to the YouTube video, the Twitch stream, or any combination of either
        is received from a 'Content Creator', the bot will highlight all guild members in the specified
        '#notifications' channel.

        :param message: The message being processed.
        :type message: discord.Message
        :return: None
        """
        if not isinstance(message.channel, discord.DMChannel):
            return

        guild = self.bot.get_guild(id=COOLSVILLE_GUILD_ID)

        if message.author not in guild.members:
            return

        member = guild.get_member(user_id=message.author.id)

        if COOLSVILLE_CONTENT_CREATOR_ROLE_ID not in [role.id for role in member.roles]:
            return

        if not message.embeds:
            return

        notifications_channel = guild.get_channel(channel_id=COOLSVILLE_NOTIFICATIONS_CHANNEL_ID)

        for video_embed in message.embeds:
            video_embed = video_embed.to_dict()

            provider = video_embed.get('provider')
            if provider is None or (provider.get('name') != 'Twitch' and provider.get('name') != 'YouTube'):
                continue

            content, embed = message_from_video_embed(video_embed, member)
            await notifications_channel.send(content=content, embed=embed)

    async def on_raw_reaction_add(self, payload):
        """Pins a message after receiving (self.pin_threshold) pins of the same emoji.

        :param payload: The details of the reaction.
        :type payload: discord.RawReactionActionEvent
        :return: None
        """
        if payload.guild_id != COOLSVILLE_GUILD_ID:
            return

        if payload.channel_id in COOLSVILLE_PIN_DISABLED_CHANNEL_IDS:
            return

        channel = self.bot.get_channel(id=payload.channel_id)

        if len(await channel.pins()) == 50:
            return

        message = await channel.get_message(id=payload.message_id)

        if message.pinned:
            return

        reaction = next((reaction for reaction in message.reactions if reaction.count >= self.pin_threshold), None)
        reactor = self.bot.get_guild(COOLSVILLE_GUILD_ID).get_member(user_id=payload.user_id)
        if reaction is not None:
            await message.pin()
            await channel.send(embed=discord.Embed(
                title='📌 Pin',
                description=f'Congratulations {message.author.mention}, '
                            f'your message has been pinned after receiving a {reaction.emoji} from {reactor.mention}!',
                color=zoinks.bot.color
            ))

    @commands.command(hidden=True)
    @commands.has_role(name='Guest')
    @commands.check(lambda ctx:
                    ctx.guild and
                    ctx.guild.id == COOLSVILLE_GUILD_ID and
                    ctx.channel.id == COOLSVILLE_RULES_CHANNEL_ID)
    async def verify(self, ctx):
        """Grants basic access to guests."""
        await ctx.author.remove_roles(discord.Object(id=COOLSVILLE_GUEST_ROLE_ID))
        await ctx.author.send(embed=discord.Embed(
            title='✅ Verified', description=f'You\'ve been verified in {ctx.guild}!', color=zoinks.bot.color))
        await ctx.message.delete()
        logger.info(f'{ctx.author} verified in {ctx.guild}')


def setup(bot):
    bot.add_cog(Coolsville(bot))
