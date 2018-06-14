import config
from zoinks.bot import ZOINKS


bot = ZOINKS()

bot.run(config.DISCORD_TOKEN)
