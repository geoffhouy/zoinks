import zoinks.bot

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)

COOLSVILLE_GUILD_ID = 462995863539679242
COOLSVILLE_RULES_CHANNEL_ID = 462996375794221066
COOLSVILLE_NOTIFICATIONS_CHANNEL_ID = 462996435839877130
COOLSVILLE_GUEST_ROLE_ID = 463013242021871617
COOLSVILLE_CONTENT_CREATOR_ROLE_ID = 462999726250262538
COOLSVILLE_PIN_DISABLED_CHANNEL_IDS = (462996078430781441, 462996375794221066, 462996408216059914, 462996435839877130)


def message_from_video_embed(video_embed, member):
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

    def __init__(self, bot):
        self.bot = bot
        self.pin_threshold = 10
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_member_join(self, member):
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
        if after.guild.id != COOLSVILLE_GUILD_ID:
            return

        if COOLSVILLE_CONTENT_CREATOR_ROLE_ID not in [role.id for role in after.roles]:
            return

        if (isinstance(after.activity, discord.Streaming) and
                after.activity.twitch_name is not None and
                not isinstance(before.activity, discord.Streaming)):
            notifications_channel = self.bot.get_channel(channel_id=COOLSVILLE_NOTIFICATIONS_CHANNEL_ID)
            await notifications_channel.send(
                content=f'Hey @everyone, {after.mention} is now live on Twitch!',
                embed=discord.Embed(
                    title=f'🎥 Twitch',
                    description=f'@everyone, {after.activity.name} is playing `{after.activity.details}`!',
                    url=f'https://www.twitch.tv/{after.activity.twitch_name}',
                    color=0x6441A4))

    async def on_message(self, message):
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
        await ctx.author.remove_roles(discord.Object(id=COOLSVILLE_GUEST_ROLE_ID))
        await ctx.author.send(embed=discord.Embed(
            title='✅ Verified', description=f'You\'ve been verified in {ctx.guild}!', color=zoinks.bot.color))
        await ctx.message.delete()
        logger.info(f'{ctx.author} verified in {ctx.guild}')


def setup(bot):
    bot.add_cog(Coolsville(bot))
