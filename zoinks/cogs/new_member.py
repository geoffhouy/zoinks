import discord
from discord.ext import commands

import logging


COOLSVILLE_GUILD_ID = 462995863539679242
RULES_CHANNEL_ID = 462996375794221066
GUEST_ROLE = 'Guest'

logger = logging.getLogger(__name__)


async def in_correct_channel(ctx):
    return (ctx.guild is not None and
            ctx.guild.id == COOLSVILLE_GUILD_ID and
            ctx.message.channel.id == RULES_CHANNEL_ID)


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
    guild:
        The Discord guild to perform actions on new members.
    rules_channel:
        The Discord channel to direct new members towards.
    guest_role:
        The new member Discord role.
    """
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.rules_channel = None
        self.guest_role = None
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_ready(self):
        self.guild = self.bot.get_guild(COOLSVILLE_GUILD_ID)
        self.rules_channel = self.bot.get_channel(RULES_CHANNEL_ID)
        self.guest_role = discord.utils.get(self.guild.roles, name=GUEST_ROLE)

    async def on_member_join(self, member):
        if member.guild == self.guild:
            await member.add_roles(self.guest_role)
            await member.send(embed=discord.Embed(
                title='👋 Welcome',
                description=f'Like, welcome to {self.guild}!\n\nPlease remember to read over '
                            f'{self.rules_channel.mention} to familiarize yourself with what\'s allowed in '
                            f'{self.guild}.\n\n If you have any comments, questions, or concerns, '
                            'please contact an Administrator or a Moderator.\n\nEnjoy your stay!',
                color=0x4D9C5F))
            logger.info(f'{member} joined')

    @commands.command(name='verify', hidden=True)
    @commands.has_role(name='Guest')
    @commands.check(in_correct_channel)
    async def verify(self, ctx):
        await ctx.author.remove_roles(self.guest_role)
        await ctx.message.delete()
        logger.info(f'{ctx.author} verified')


def setup(bot):
    bot.add_cog(NewMember(bot))
