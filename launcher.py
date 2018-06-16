import config
from zoinks.bot import ZOINKS

import logging
import sys


if __name__ == '__main__':
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        stream=sys.stdout)
    bot = ZOINKS()
    bot.run(config.DISCORD_TOKEN)
