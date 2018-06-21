from zoinks.webhooks import SteamWebhook

import logging


logger = logging.getLogger(__name__)

webhook_args = {'endpoint': '457588791062822912/CY8BuF3M8r944g-y4-3svTTI-GOEc9LIACCMnrWkaz-tJAwBURuFpabGUzusUzdsT2Fi',
        'source': 'https://steamcommunity.com/games/813820/rss/',
        'poll_delay': 60 * 60 * 24,  # 1 day
        'footer': ('Realm Royale', 'https://steamcdn-a.akamaihd.net/steam/apps/813820/capsule_184x69.jpg'),
        'color': 0x9D69F4}


class RealmRoyale:

    def __init__(self, bot):
        self.bot = bot
        self.webhook = SteamWebhook(**webhook_args)
        self.bot.loop.create_task(self.webhook.poll())
        logger.info(f'{self.__class__.__name__} loaded')


def setup(bot):
    bot.add_cog(RealmRoyale(bot))
