import logging


logger = logging.getLogger(__name__)


class Fortnite:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    # TODO: Fortnite Masters Integration


def setup(bot):
    bot.add_cog(Fortnite(bot))
