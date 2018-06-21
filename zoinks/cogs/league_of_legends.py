from zoinks.webhooks import ScrapingWebhook

import discord

import logging
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

webhook_args = {'endpoint': '457588791062822912/CY8BuF3M8r944g-y4-3svTTI-GOEc9LIACCMnrWkaz-tJAwBURuFpabGUzusUzdsT2Fi',
                'source': 'https://na.leagueoflegends.com/en/news/game-updates/patch',
                'base_url': 'https://na.leagueoflegends.com',
                'navigate_html': lambda soup: soup.find(
                    class_='views-row views-row-1 views-row-odd views-row-first').find(
                    class_='lol-core-file-formatter').get('href'),
                'poll_delay': 60* 60 * 24,  # 1 day
                'footer': (
                    'League of Legends',
                    'https://cdn.leagueoflegends.com/riotbar/prod/1.6.154/images/navigation/icon-game-lol.png'),
                'color': 0x96692A}


class LeagueOfLegends:

    def __init__(self, bot):
        self.bot = bot
        self.webhook = LeagueOfLegendsWebhook(**webhook_args)
        self.bot.loop.create_task(self.webhook.poll())
        logger.info(f'{self.__class__.__name__} loaded')


class LeagueOfLegendsWebhook(ScrapingWebhook):
    """Represents a basic webhook using Discord's endpoint URL.

    Used to check the League of Legends homepage for new patch notes and POST them
    to Discord automatically.
    Requires a separate webhook because article contents can't be read from the metadata.

    Attributes
    ----------
    endpoint: str
        The Discord webhook endpoint URL contents after '/api/webhooks/'.
    source: str
        The source URL of the content.
    base_url: str
        The homepage URL to build other URLs.
    navigate_html: function
        The BeautifulSoup function chain to find new content from the source.
    poll_delay: int
        The downtime between finding new content to POST.
    color: int
        The color of the embed to POST.
    footer: tuple
        The footer text and footer icon of the embed to POST.
    """
    def __init__(self, endpoint, **kwargs):
        super().__init__(endpoint, **kwargs)
        self.base_url = kwargs.get('base_url')

    def build_embed(self, article):
        try:
            response = requests.get(url=self.source, headers=self._headers[1])
        except requests.exceptions.RequestException as e:
            logger.warning(f'{e}')
            return None
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find(class_='views-row views-row-1 views-row-odd views-row-first')
            title = content.find(class_='lol-core-file-formatter').get('title')
            url = f'{self.base_url}{article}'
            description = content.find(class_='teaser-content').find('div').get_text(strip=True)
            if len(description) > 250:
                description = f'{description[:253]}'
            embed = discord.Embed(
                title=title,
                url=url,
                description=description,
                color=self.color)
            thumbnail_url = content.find(class_='lol-core-file-formatter').find('img').get('src')
            thumbnail_url = f'{self.base_url}{thumbnail_url}'
            embed.set_thumbnail(url=thumbnail_url)
            if self.footer:
                text, icon_url = self.footer
                if text is None:
                    text = 'Untitled'
                if icon_url is None:
                    icon_url = ''
                embed.set_footer(text=text, icon_url=icon_url)
            return embed.to_dict()


def setup(bot):
    bot.add_cog(LeagueOfLegends(bot))
