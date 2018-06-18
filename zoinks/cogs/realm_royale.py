from zoinks.webhook import Webhook

import logging


logger = logging.getLogger(__name__)


class RealmRoyale:

    def __init__(self, bot):
        self.bot = bot
        self.webhook = Webhook(
            endpoint='457588791062822912/CY8BuF3M8r944g-y4-3svTTI-GOEc9LIACCMnrWkaz-tJAwBURuFpabGUzusUzdsT2Fi',
            source='https://store.steampowered.com/news/?appids=813820',
            navigate_html=lambda soup: soup.find(
                'div', {'class': 'newsPostBlock steam_community_announcements'}).find('a').get('href'),
            poll_delay=900,
            title='Realm Royale',
            icon_url='https://steamcdn-a.akamaihd.net/steam/apps/813820/capsule_184x69.jpg',
            color=0x9D69F4
        )
        self.bot.loop.create_task(self.webhook.poll())
        logger.info(f'{self.__class__.__name__} loaded')


def setup(bot):
    bot.add_cog(RealmRoyale(bot))
