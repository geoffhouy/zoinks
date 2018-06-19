import discord

import asyncio
import json
import logging
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class Webhook:

    def __init__(self, endpoint, **kwargs):
        self.endpoint = f'https://discordapp.com/api/webhooks/{endpoint}'
        self.content = kwargs.get('content')
        self._headers = ({'Content-Type': 'application/json'}, {'User-Agent': 'Mozilla/5.0'})

    def format(self, payload):
        raise NotImplementedError

    def post(self, content: None):
        if self.content is None and content is None:
            logger.warning('Failed to POST: No content')
            return
        content = content if content else self.content
        payload = {'content': content}
        response = requests.post(self.endpoint, data=json.dumps(payload, indent=4), headers=self._headers[0])
        if response.status_code == 400:
            logger.info(f'Failed to POST {content}: {response.status_code}')
        else:
            logger.info(f'POST {content}')


class RichWebhook(Webhook):

    def __init__(self, endpoint, **kwargs):
        super().__init__(endpoint)
        self.embed = kwargs.get('embed')

    def format(self, payload: discord.Embed):
        return payload.to_dict()

    def post(self, embed: None):
        if self.embed is None and embed is None:
            logger.warning('Failed to POST: No embed')
            return
        if isinstance(embed, discord.Embed):
            embed = self.format(embed)
        embed = embed if embed else self.embed
        title = embed.get('title')
        payload = {'embeds': [embed]}
        response = requests.post(self.endpoint, data=json.dumps(payload, indent=4), headers=self._headers[0])
        if response.status_code == 400:
            logger.info(f'Failed to POST {title}: {response.status_code}')
        else:
            logger.info(f'POST {title}')


class ScrapingWebhook(RichWebhook):
    """Represents a basic webhook using Discord's endpoint URL.

    Used to check websites for new news articles and POST them to Discord automatically.
    Formats news article information into an rich embedded message.

    Attributes
    ----------
    endpoint: str
        The Discord webhook endpoint URL contents after '/api/webhooks/'.
    source: str
        The source URL of the content.
    navigate_html: function
        The BeautifulSoup function chain to find new content from the source.
    poll_delay: int
        The downtime between finding new content to POST.
    title: str
        The footer title of the embed to POST.
    icon_url: str
        The footer icon of the embed to POST.
    color: int
        The color of the embed to POST.
    """
    def __init__(self, endpoint, **kwargs):
        super().__init__(endpoint)
        self.source = kwargs.get('source')
        self.navigate_html = kwargs.get('navigate_html')
        self.poll_delay = kwargs.get('poll_delay', 3600)
        self.title = kwargs.get('title')
        self.icon_url = kwargs.get('icon_url', '')
        self.color = kwargs.get('color', 0x000000)
        self.is_running = True

    def _find_article(self):
        try:
            response = requests.get(url=self.source, headers=self._headers[1])
        except requests.exceptions.RequestException as e:
            logger.warning(f'{e}')
            return None
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            article = self.navigate_html(soup)
            return article

    def _build_embed(self, post_url):
        try:
            response = requests.get(url=post_url, headers=self._headers[1])
        except requests.exceptions.RequestException as e:
            logger.warning(f'{e}')
            return None
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            description = soup.find('meta', property='og:description').get('content')
            if len(description) > 250:
                description = f'{description[:253]}...'
            embed = discord.Embed(
                title=soup.find('meta', property='og:title').get('content'),
                url=post_url,
                description=description,
                color=self.color)
            embed.set_thumbnail(url=soup.find('meta', property='og:image').get('content'))
            embed.set_footer(text=self.title, icon_url=self.icon_url)
            return self.format(embed)

    async def poll(self):
        last_article = ''
        while self.is_running:
            article = self._find_article()
            if article == last_article:
                pass
            else:
                embed = self._build_embed(article)
                if embed is not None:
                    self.post(embed)
                    last_article = article
            await asyncio.sleep(self.poll_delay)
