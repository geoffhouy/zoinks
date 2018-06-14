import discord
from discord.ext import commands


command_prefix = '!'
description = 'Like ZOINKS Scoob!'


class ZOINKS(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(command_prefix), description=description, pm_help=None)

    async def on_ready(self):
        print(f'{self.user} ({self.user.id}) has logged in')
