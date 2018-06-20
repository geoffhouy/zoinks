import discord

import asyncio
import json
import logging
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class Webhook:
    """Represents a basic webhook using Discord's endpoint URL.

    Used to post a simple text message.

    Attributes
    ----------
    endpoint: str
        The Discord webhook endpoint URL contents after '/api/webhooks/'.
    content: str
        The content of the message to POST.
    """
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
    """Represents a basic webhook using Discord's endpoint URL.

    Used to post a rich Discord embed message.

    Attributes
    ----------
    endpoint: str
        The Discord webhook endpoint URL contents after '/api/webhooks/'.
    embed: str
        The Discord embed to POST.
    """
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
    color: int
        The color of the embed to POST.
    footer: tuple
        The footer text and footer icon of the embed to POST.
    """
    def __init__(self, endpoint, **kwargs):
        super().__init__(endpoint)
        self.source = kwargs.get('source')
        self.navigate_html = kwargs.get('navigate_html')
        self.poll_delay = kwargs.get('poll_delay', 3600)
        self.color = kwargs.get('color')
        self.footer = kwargs.get('footer', (None, None))
        self.is_running = True

    def find_article(self):
        try:
            response = requests.get(url=self.source, headers=self._headers[1])
        except requests.exceptions.RequestException as e:
            logger.warning(f'{e}')
            return None
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            article = self.navigate_html(soup)
            return article

    def build_embed(self, article):
        try:
            response = requests.get(url=article, headers=self._headers[1])
        except requests.exceptions.RequestException as e:
            logger.warning(f'{e}')
            return None
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('meta', property='og:title')
            title = title.get('content') if title else ''
            description = soup.find('meta', property='og:description')
            description = description.get('content') if description else ' '
            description = f'{description[:253]}...' if len(description) > 250 else description
            embed = discord.Embed(
                title=title,
                url=article,
                description=description,
                color=self.color)
            thumbnail_url = soup.find('meta', property='og:image')
            thumbnail_url = thumbnail_url.get('content') if thumbnail_url else ''
            embed.set_thumbnail(url=thumbnail_url)
            text, icon_url = self.footer
            if text or icon_url:
                if text is None:
                    text = 'Untitled'
                if icon_url is None:
                    icon_url = ''
                embed.set_footer(text=text, icon_url=icon_url)
            return embed

    async def poll(self):
        last_article = ''
        while self.is_running:
            article = self.find_article()
            if article and article != last_article:
                embed = self.build_embed(article)
                if embed:
                    embed = self.format(embed)
                    self.post(embed)
                    last_article = article
            await asyncio.sleep(self.poll_delay)
