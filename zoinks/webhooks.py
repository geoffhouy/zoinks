import discord

import asyncio
import json
import logging
import re
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

    def post(self, content=None):
        if self.content is None and content is None:
            raise ValueError('Content must be set before posting')

        content_to_post = None
        if self.content:
            content_to_post = self.content
        if content:
            content_to_post = content

        payload = {'content': content_to_post}
        response = requests.post(self.endpoint,
                                 data=json.dumps(payload, indent=4),
                                 headers={'Content-Type': 'application/json'})
        if response.status_code == 400:
            logger.info(f'Failed to POST {content_to_post}: {response.status_code}')
        else:
            logger.info(f'POST {content_to_post}')


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

    def post(self, embed=None):
        if self.embed is None and embed is None:
            raise ValueError('Embed must be set before posting')

        if not isinstance(self.embed, discord.Embed) and not isinstance(embed, discord.Embed):
            raise ValueError('Embed must be of type discord.Embed')

        embed_to_post = None
        if self.embed:
            embed_to_post = self.embed
        if embed:
            embed_to_post = embed
        embed_to_post = embed_to_post.to_dict()

        title = embed_to_post.get('title')
        payload = {'embeds': [embed_to_post]}
        response = requests.post(self.endpoint,
                                 data=json.dumps(payload, indent=4),
                                 headers={'Content-Type': 'application/json'})
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
        The BeautifulSoup function chain to find new articles from the source URL.
    poll_delay: int
        The downtime between checking for new information to POST.
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
        soup = fetch_soup(self.source)
        if soup is None:
            return None
        article_url = self.navigate_html(soup)
        return article_url

    def build_embed(self, article_url):
        article = fetch_soup(article_url)

        if article is None:
            return None

        title = article.find(property='og:title')
        if title:
            title = title.get('content')
        else:
            title = ''

        description = article.find(property='og:description')
        if description:
            description = description.get('content')
            if len(description) > 250:
                description = f'{description[:253]}'
        else:
            description = ''

        embed = discord.Embed(
            title=title,
            description=description,
            url=article_url,
            color=self.color)

        thumbnail_url = article.find(property='og:image')
        if thumbnail_url:
            thumbnail_url = thumbnail_url.get('content')
        else:
            thumbnail_url = ''
        embed.set_thumbnail(url=thumbnail_url)

        if self.footer:
            text, icon_url = self.footer
            if text is None:
                text = ''
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
                    self.post(embed)
                last_article = article
            await asyncio.sleep(self.poll_delay)


class SteamWebhook(ScrapingWebhook):
    """Represents a basic webhook using Discord's endpoint URL.

    Used to check a Steam game's RSS feed for new updates and POST them to Discord automatically.

    Attributes
    ----------
    endpoint: str
        The Discord webhook endpoint URL contents after '/api/webhooks/'.
    source: str
        The source URL of the content.
    poll_delay: int
        The downtime between checking for new information to POST.
    color: int
        The color of the embed to POST.
    footer: tuple
        The footer text and footer icon of the embed to POST.
    """
    def __init__(self, endpoint, **kwargs):
        super().__init__(endpoint, **kwargs)

    def find_article(self):
        soup = fetch_soup(self.source)
        if soup is None:
            return None
        item = soup.select_one('item')
        return item

    def build_embed(self, item):
        title = item.find('title').get_text(strip=True)

        article_url = item.find('guid').get_text(strip=True)

        description = item.find('description').get_text(strip=True)
        description = re.sub('<[^<]+?>', '', description)
        if len(description) > 250:
            description = f'{description[:253]}...'

        embed = discord.Embed(
            title=title,
            url=article_url,
            description=description,
            color=self.color)

        thumbnail_url = item.find('description').get_text(strip=True)
        thumbnail_url = re.search('<img src=\"(.*\.(?:png|jpg))\"\s+>', thumbnail_url).group(1)
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        if self.footer:
            text, icon_url = self.footer
            if text is None:
                text = 'Untitled'
            if icon_url is None:
                icon_url = ''
            embed.set_footer(text=text, icon_url=icon_url)

        return embed


def fetch_soup(url):
    try:
        response = requests.get(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    except requests.exceptions.RequestException as e:
        logger.warning(f'{e}')
        return None
    else:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
