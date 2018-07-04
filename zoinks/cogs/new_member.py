import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


async def _in_correct_channel(ctx):
    return ctx.guild and ctx.guild == NewMember.guild and ctx.message.channel == NewMember.channel


class NewMember:

    guild = None
    channel = None
    role = None

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_ready(self):
        self.__class__.guild = self.bot.guild
        self.__class__.channel = self.bot.rules_channel
        self.__class__.role = discord.utils.get(self.bot.guild.roles, name='Guest')

    async def on_member_join(self, member):
        if member.guild == self.bot.guild:
            await member.add_roles(self.__class__.role)
            await member.send(embed=discord.Embed(
                title='👋 Welcome',
                description=f'Like, welcome to {self.bot.guild}!\n\nPlease remember to read over '
                            f'{self.bot.rules_channel.mention} to familiarize yourself with what\'s allowed in '
                            f'{self.bot.guild}.\n\n If you have any comments, questions, or concerns, '
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
