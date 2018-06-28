from zoinks.webhooks import LeagueOfLegendsWebhook, SteamRSSWebhook, URLWebhook

import discord
from discord.ext import commands

import logging


endpoint = '457588791062822912/CY8BuF3M8r944g-y4-3svTTI-GOEc9LIACCMnrWkaz-tJAwBURuFpabGUzusUzdsT2Fi'

webhook_config = {
    'darkest_dungeon': {
        'name': 'Darkest Dungeon',
        'tag': ('darkest dungeon', 'darkest', 'dd'),
        'emoji': '🎮',
        'class': SteamRSSWebhook,
        'kwargs': {
            'source': 'https://steamcommunity.com/games/262060/rss/',
            'poll_delay': 60 * 60 * 24,  # 1 day
            'color': 0xFB3512,
            'footer': ('Darkest Dungeon',
                       'https://steamcdn-a.akamaihd.net/steam/apps/262060/header.jpg')
        }
    },
    'dota2': {
        'name': 'Dota 2',
        'tag': ('dota2', 'dota'),
        'emoji': '🎮',
        'class': URLWebhook,
        'kwargs': {
            'source': 'https://store.steampowered.com/news/?appids=570&appgroupname=Dota+2&feed=steam_updates',
            'navigate_html': lambda soup: soup.find(class_='newsPostBlock steam_updates').find('a').get('href'),
            'poll_delay': 60 * 60 * 24,  # 1 day
            'color': 0xFB3512,
            'footer': ('Dota2',
                       'https://steamcdn-a.akamaihd.net/steam/apps/570/capsule_184x69.jpg')
        }
    },
    'league_of_legends': {
        'name': 'League of Legends',
        'tag': ('league of legends', 'league', 'lol'),
        'emoji': '🎮',
        'class': LeagueOfLegendsWebhook,
        'kwargs': {
            'source': 'https://na.leagueoflegends.com/en/news/game-updates/patch',
            'base_url': 'https://na.leagueoflegends.com',
            'navigate_html': lambda soup: soup.find(
                class_='views-row views-row-1 views-row-odd views-row-first').find(
                class_='lol-core-file-formatter').get('href'),
            'poll_delay': 60 * 60 * 24,  # 1 day
            'color': 0x96692A,
            'footer': ('League of Legends',
                       'https://cdn.leagueoflegends.com/riotbar/prod/1.6.154/images/navigation/icon-game-lol.png')
        }
    },
    'realm_royale': {
        'name': 'Realm Royale',
        'tag': ('realm royale', 'realm', 'rr'),
        'emoji': '🎮',
        'class': SteamRSSWebhook,
        'kwargs': {
            'source': 'https://steamcommunity.com/games/813820/rss/',
            'poll_delay': 60 * 60 * 24,  # 1 day
            'color': 0x9D69F4,
            'full_image': True,
            'footer': ('Realm Royale',
                       'https://steamcdn-a.akamaihd.net/steam/apps/813820/capsule_184x69.jpg')
        }
    }
}

logger = logging.getLogger(__name__)


class Webhooks:

    __slots__ = ('bot', 'darkest_dungeon', 'dota2', 'league_of_legends', 'realm_royale')

    def __init__(self, bot):
        self.bot = bot
        self._init_webhooks()
        logger.info(f'{self.__class__.__name__} loaded')

    def _init_webhooks(self):
        for slot in self.__slots__:
            if slot == 'bot':
                continue
            cls = webhook_config[slot]['class']
            kwargs = webhook_config[slot]['kwargs']
            setattr(self, slot, cls(self.bot, endpoint, **kwargs))
            self.bot.loop.create_task(getattr(self, slot).poll())

    @commands.has_permissions(administrator=True)
    @commands.command(name='status')
    async def status(self, ctx):
        """Displays a list of names and statuses for all existing URL webhooks."""
        embed = discord.Embed(title='Webhook Status',
                              description='Each URL webhook and its status is listed below.'
                                          'To change the status of a webhook, use the `toggle` command.',
                              color=0x519D6A)
        field1 = ''
        field2 = ''

        for slot in self.__slots__:
            if slot == 'bot':
                continue
            cls = getattr(self, slot)
            if hasattr(cls, 'is_running'):
                emoji = webhook_config[slot]['emoji']
                name = webhook_config[slot]['name']
                field1 += f'{emoji} {name}\n'
                field2 += '✅\n' if cls.is_running else '❎\n'

        embed.add_field(name='Name', value=field1, inline=True)
        embed.add_field(name='Status', value=field2, inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Webhooks(bot))
