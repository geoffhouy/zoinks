import discord

import asyncio
import json
import logging
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class Webhook:
    """Represents a basic webhook using Discord's endpoint URL.

    Used to check websites for new news articles and POST them to Discord automatically.

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
        self.endpoint = f'https://discordapp.com/api/webhooks/{endpoint}'
        self.source = kwargs.get('source', None)
        self.navigate_html = kwargs.get('navigate_html', None)
        self.poll_delay = kwargs.get('poll_delay', 3600)
        self.title = kwargs.get('title', None)
        self.icon_url = kwargs.get('icon_url', '')
        self.color = kwargs.get('color', 0x000000)
        self.is_running = True
        self._headers = ({'Content-Type': 'application/json'}, {'User-Agent': 'Mozilla/5.0'})

    async def poll(self):
        last_post_url = ''
        while self.is_running:
            post_url = self.find()
            if post_url == last_post_url:
                pass
            else:
                embed = self.get(post_url)
                if embed is not None:
                    self.post(embed)
                    last_post_url = post_url
            await asyncio.sleep(self.poll_delay)

    def find(self):
        try:
            response = requests.get(url=self.source, headers=self._headers[1])
        except requests.exceptions.RequestException as e:
            logger.warning(f'{e}')
            return None
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            post_url = self.navigate_html(soup)
            return post_url

    def get(self, post_url):
        try:
            response = requests.get(url=post_url, headers=self._headers[1])
        except requests.exceptions.RequestException as e:
            logger.warning(f'{e}')
            return None
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            description = soup.find('meta', property='og:description').get('content')
            if len(description) > 300:
                description = f'{description[:303]}...'
            embed = discord.Embed(
                title=soup.find('meta', property='og:title').get('content'),
                url=post_url,
                description=description,
                color=self.color)
            embed.set_thumbnail(url=soup.find('meta', property='og:image').get('content'))
            embed.set_footer(text=self.title, icon_url=self.icon_url)
            return embed.to_dict()

    def post(self, embed):
        title = embed.get('title')
        payload = {'embeds': [embed]}
        payload = json.dumps(payload, indent=4)
        response = requests.post(self.endpoint, data=payload, headers=self._headers[0])
        if response.status_code == 400:
            logger.info(f'"{title}" failed to POST: {response.status_code}')
        else:
            logger.info(f'POST "{title}"')
