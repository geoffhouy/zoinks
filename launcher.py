import config

from discord.ext import commands


bot = commands.Bot(command_prefix='!')

bot.run(config.DISCORD_TOKEN)
