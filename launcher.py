import config
from zoinks.bot import ZOINKS


if __name__ == '__main__':
    bot = ZOINKS()
    bot.run(config.DISCORD_TOKEN)
