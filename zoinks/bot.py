from discord.ext import commands


command_prefix = '!'
description = 'Like ZOINKS Scoob!'


class ZOINKS(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(command_prefix), description=description, pm_help=None)
