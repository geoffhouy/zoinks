from zoinks.webhooks import SteamWebhook

import logging


logger = logging.getLogger(__name__)


class RealmRoyale:

    def __init__(self, bot):
        self.bot = bot
        self.steam_webhook = SteamWebhook(
            endpoint='457588791062822912/CY8BuF3M8r944g-y4-3svTTI-GOEc9LIACCMnrWkaz-tJAwBURuFpabGUzusUzdsT2Fi',
            source='https://steamcommunity.com/games/813820/rss/',
            poll_delay=900,
            footer=('Realm Royale', 'https://steamcdn-a.akamaihd.net/steam/apps/813820/capsule_184x69.jpg'),
            color=0x9D69F4)
        self.bot.loop.create_task(self.steam_webhook.poll())
        logger.info(f'{self.__class__.__name__} loaded')


def setup(bot):
    bot.add_cog(RealmRoyale(bot))
