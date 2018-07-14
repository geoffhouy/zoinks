import zoinks.bot
import zoinks.utils.checks as checks

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


class NewMember:
    """Represents a cog for a Discord bot.

    This cog extends the default on_member_join event function.
    --> Whenever a new member joins a guild, the bot will assign the member a 'Guest' role, provided it exists.
        Then, the bot will send a welcome message suggesting the new member reads the 'rules' channel,
        provided it exists.

    In my guild, the 'Guest' role can ONLY read and write in the 'rules' channel which makes the 'verify' command
    required for the user to gain further access from the bot.

    Attributes
    ----------
    bot: ZOINKS
        The currently running ZOINKS Discord bot.
    """
    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_member_join(self, member):
        guest_role = discord.utils.get(member.guild.roles, name='Guest')
        if guest_role is not None:
            await member.add_roles(guest_role)

        rules_channel = discord.utils.get(member.guild.channels, name='rules')
        if rules_channel is not None:
            await member.send(embed=discord.Embed(
                title='👋 Welcome',
                description=f'Like, welcome to {member.guild}!\n\nPlease remember to read over '
                            f'{rules_channel.mention} to familiarize yourself with what\'s allowed in '
                            f'{member.guild}.\n\n If you have any comments, questions, or concerns, '
                            'please contact an Administrator or a Moderator.\n\nEnjoy your stay!',
                color=zoinks.bot.color))

        logger.info(f'{member} joined {member.guild}')

    @commands.command(hidden=True)
    @commands.has_role(name='Guest')
    @commands.check(checks.in_rules_channel)
    async def verify(self, ctx):
        guest_role = discord.utils.get(ctx.author.roles, name='Guest')
        await ctx.author.remove_roles(guest_role)
        await ctx.author.send(embed=discord.Embed(
            title='✅ Verified', description=f'You\'ve been verified in {ctx.guild}!', color=zoinks.bot.color))
        await ctx.message.delete()
        logger.info(f'{ctx.author} verified in {ctx.guild}')


def setup(bot):
    bot.add_cog(NewMember(bot))
