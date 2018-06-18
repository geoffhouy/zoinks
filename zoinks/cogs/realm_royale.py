import logging


logger = logging.getLogger(__name__)


class RealmRoyale:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')


def setup(bot):
    bot.add_cog(RealmRoyale(bot))
