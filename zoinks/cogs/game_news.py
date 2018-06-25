from zoinks.webhooks import ScrapingWebhook, SteamWebhook

import discord
from discord.ext import commands

import logging


endpoint = '457588791062822912/CY8BuF3M8r944g-y4-3svTTI-GOEc9LIACCMnrWkaz-tJAwBURuFpabGUzusUzdsT2Fi'

webhook_config = {
    'realm_royale': {
        'name': ('realm royale', 'realm', 'rr'),
        'class': SteamWebhook,
        'kwargs': {
            'source': 'https://steamcommunity.com/games/813820/rss/',
            'poll_delay': 60 * 60 * 24,  # 1 day
            'footer': ('Realm Royale',
                       'https://steamcdn-a.akamaihd.net/steam/apps/813820/capsule_184x69.jpg'),
            'color': 0x9D69F4
        }
    },
    'league_of_legends': {
        'name': ('league of legends', 'league', 'lol'),
        'class': ScrapingWebhook,
        'kwargs': {
            'source': 'https://na.leagueoflegends.com/en/news/game-updates/patch',
            'base_url': 'https://na.leagueoflegends.com',
            'navigate_html': lambda soup: soup.find(
                class_='views-row views-row-1 views-row-odd views-row-first').find(
                class_='lol-core-file-formatter').get('href'),
            'poll_delay': 60 * 60 * 24,  # 1 day
            'footer': ('League of Legends',
                       'https://cdn.leagueoflegends.com/riotbar/prod/1.6.154/images/navigation/icon-game-lol.png'),
            'color': 0x96692A
        }
    }
}

logger = logging.getLogger(__name__)


class GameNews:

    __slots__ = ('bot', 'realm_royale')  # , 'league_of_legends')

    def __init__(self, bot):
        self.bot = bot

        for slot in self.__slots__:
            if slot == 'bot':
                continue
            setattr(self, slot, None)

        self._init_webhooks()
        logger.info(f'{self.__class__.__name__} loaded')

    def _init_webhooks(self):
        for slot in self.__slots__:
            if slot == 'bot':
                continue
            cls = webhook_config[slot]['class']
            kwargs = webhook_config[slot]['kwargs']
            setattr(self, slot, cls(endpoint, **kwargs))
            self.bot.loop.create_task(getattr(self, slot).poll())


def setup(bot):
    bot.add_cog(GameNews(bot))
