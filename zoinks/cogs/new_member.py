import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


async def _in_correct_channel(ctx):
    return ctx.guild and ctx.guild == NewMember.guild and ctx.message.channel == NewMember.channel


class NewMember:
    """Represents a cog for a Discord bot.

    This cog extends the default on_ready event function to set its class variables for usage
    in the _in_correct_channel verify command check. It must be done this way because
    the commands.check() will refuse self.

    This cog also extends the default on_member_join event function.
    It handles the new member experience for the specified guild.*
    Whenever a new member joins the specified guild, the bot will send him/her a welcoming direct message and
    give him/her the Guest role**. The Guest role is limited to reading/sending text messages
    into a single #rules (specified) channel. Once the new member who still has the Guest role
    types the verify command, the bot will remove the Guest role allowing the new member
    to have all the permissions of the @everyone role.

    *The channel and guild are specified at the time of creation of the bot. See its config attribute.

    Attributes
    ----------
    bot: ZOINKS
        The currently running ZOINKS Discord bot.
    """
    guild = None
    channel = None
    role = None

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_ready(self):
        self.__class__.guild = self.bot.config.guild
        self.__class__.channel = self.bot.config.rules_channel
        self.__class__.role = discord.utils.get(self.bot.config.guild.roles, name='Guest')

    async def on_member_join(self, member):
        if member.guild == self.bot.config.guild:
            await member.add_roles(self.__class__.role)
            await member.send(embed=discord.Embed(
                title='👋 Welcome',
                description=f'Like, welcome to {self.bot.config.guild}!\n\nPlease remember to read over '
                            f'{self.bot.config.rules_channel.mention} to familiarize yourself with what\'s allowed in '
                            f'{self.bot.config.guild}.\n\n If you have any comments, questions, or concerns, '
                            'please contact an Administrator or a Moderator.\n\nEnjoy your stay!',
                color=0x4D9C5F))
            logger.info(f'{member} joined')

    @commands.command(name='verify', hidden=True)
    @commands.has_role(name='Guest')
    @commands.check(_in_correct_channel)
    async def verify(self, ctx):
        await ctx.author.remove_roles(self.__class__.role)
        await ctx.message.delete()
        logger.info(f'{ctx.author} verified')


def setup(bot):
    bot.add_cog(NewMember(bot))
