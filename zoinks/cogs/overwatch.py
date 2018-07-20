import logging


logger = logging.getLogger(__name__)


class Overwatch:

    def __init__(self, bot):
        self.bot = bot
        logger.info(f'{self.__class__.__name__} loaded')

    # TODO: Riot Games API Integration


def setup(bot):
    bot.add_cog(Overwatch(bot))
