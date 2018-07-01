import config

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


async def not_verified(ctx):
    return (ctx.guild and
            ctx.guild == Join.guild and
            ctx.message.channel == Join.channel and
            Join.role in ctx.author.roles)


class Join:

    guild = None
    channel = None
    role = None

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    async def on_ready(self):
        self.__class__.guild = self.bot.get_guild(config.COOLSVILLE_GUILD_ID)
        self.__class__.channel = self.bot.get_channel(config.COOLSVILLE_RULES_CHANNEL_ID)
        self.__class__.role = discord.utils.get(self.__class__.guild.roles, name='Guest')

    async def on_member_join(self, member):
        if member.guild == self.__class__.guild:
            await member.add_roles(self.__class__.role)
            embed = discord.Embed(title='👋 Welcome',
                                  description=f'Like, welcome to {self.__class__.guild}!'
                                              '\n\n'
                                              f'Please remember to read over {self.__class__.channel.mention} to '
                                              f'familiarize yourself with what\'s allowed in {self.__class__.guild}.'
                                              '\n\n'
                                              'If you have any comments, questions, or concerns, please contact '
                                              'an Administrator or a Moderator.'
                                              '\n\n'
                                              'Enjoy your stay!',
                                  color=0x4D9C5F)
            await member.send(embed=embed)
            logger.info(f'{member} joined')

    @commands.command(name='verify', hidden=True)
    @commands.check(not_verified)
    async def verify(self, ctx):
        await ctx.author.remove_roles(self.role)
        await ctx.message.delete()
        logger.info(f'{ctx.author} verified themselves')


def setup(bot):
    bot.add_cog(Join(bot))