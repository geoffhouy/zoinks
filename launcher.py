import config
from zoinks.bot import ZOINKS

import logging
import sys


def _setup_logging():
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        stream=sys.stdout)


if __name__ == '__main__':
    _setup_logging()
    bot = ZOINKS()
    bot.run(config.DISCORD_TOKEN, reconnect=True)
