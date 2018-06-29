from zoinks.bot import ZOINKS

import discord

import asyncio
import json
import logging
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class Webhook:
    """Represents a basic webhook that outputs to the specified Discord endpoint URL.

    Used to post a plain text message, a rich discord.Embed message, or a combination of the two
    into the specified Discord channel.

    In the Discord server settings, create a new webhook to retrieve its endpoint URL. During creation,
    its output channel, username, and avatar image will all be specified.

    Attributes
    ----------
    bot: ZOINKS
        The currently running ZOINKS Discord bot. Used for its session attribute.
    endpoint_url: str
        The Discord webhook endpoint URL. Pass either the entire URL or all content after '/webhooks/'.
    username: str
        The Discord webhook username. Used to override the current webhook name.
    avatar_url: str
        The Discord webhook avatar image URL. Used to override the current webhook image.
    """
    BASE_URL = 'https://discordapp.com/api/webhooks/'

    def __init__(self, bot: ZOINKS, endpoint_url: str, **kwargs):
        self.bot = bot

        if self.BASE_URL not in endpoint_url:
            self.endpoint_url = f'{self.BASE_URL}{endpoint_url}'
        else:
            self.endpoint_url = endpoint_url

        self.username = kwargs.get('username')
        self.avatar_url = kwargs.get('avatar_url')

    async def post(self, content: str=None, embed: discord.Embed=None):
        payload = {}

        if content:
            payload['content'] = content
        if embed:
            payload['embeds'] = [embed.to_dict()]

        if not payload:
            raise ValueError('Payload must have either content, an embed, or both')

        if self.username:
            payload['username'] = self.username
        if self.avatar_url:
            payload['avatar_url'] = self.avatar_url

        async with self.bot.session.post(url=self.endpoint_url,
                                         data=json.dumps(payload, indent=4),
                                         headers={'Content-Type': 'application/json'}) as response:
            if response.status >= 400:
                logger.info(f'Failed to POST: {response.status}')
            else:
                logger.info(f'POST "{embed.title}"')


class ScrapingWebhook(Webhook):
    """Represents a URL-scraping webhook that outputs to the specified Discord endpoint URL.

    Used to scrape the specified URL then build and post a rich discord.Embed message
    into the specified Discord channel.

    Attributes
    ----------
    bot: ZOINKS
        The currently running ZOINKS Discord bot. Used for its session attribute.
    endpoint_url: str
        The Discord webhook endpoint URL. Pass either the entire URL or all content after '/webhooks/'.
    username: str
        The Discord webhook username. Used to override the current webhook name.
    avatar_url: str
        The Discord webhook avatar image URL. Used to override the current webhook image.
    source_url: str
        The source URL of the content to post.
    navigate_html: function
        The BeautifulSoup function chain to find the URL of the latest article from the source URL.
    delay: int
        The time in seconds between checking for new content to post.
    color: int
        The color of the discord.Embed to post. Typically matched with the homepage color scheme.
    thumbnail_url: str
        The thumbnail URL of the discord.Embed to post. Typically used for logos.
    """
    def __init__(self, bot: ZOINKS, endpoint_url: str, **kwargs):
        super().__init__(bot=bot, endpoint_url=endpoint_url, **kwargs)

        self.source_url = kwargs.get('source_url')
        if self.source_url is None:
            raise ValueError('Source URL must be set')

        self.navigate_html = kwargs.get('navigate_html')
        self.delay = kwargs.get('delay', 60 * 60 * 24)
        self.color = kwargs.get('color', 0xFFFFFF)
        self.thumbnail_url = kwargs.get('thumbnail_url')

        self.is_running = True

    async def fetch_soup(self, url):
        async with self.bot.session.get(url=url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
            if response.status >= 400:
                logger.info(f'Failed to GET: {response.status}')
                return None
            else:
                content = await response.text()
                return BeautifulSoup(content, 'html.parser')

    async def find_url(self):
        soup = await self.fetch_soup(self.source_url)
        try:
            url = self.navigate_html(soup)
        except AttributeError as e:
            logger.warning(e)
            return None
        else:
            return url

    async def build_embed(self, url):
        soup = await self.fetch_soup(url)

        title = soup.find(property='og:title')
        if title:
            title = title.get('content')

        description = soup.find(property='og:description')
        if description:
            description = description.get('content')
            if len(description) > 250:
                description = f'{description[:247]}...'

        embed = discord.Embed(
            title=title,
            description=description,
            url=url,
            color=self.color)

        image_url = soup.find(property='og:image')
        if image_url:
            image_url = image_url.get('content')
            if 'share_steam_logo' not in image_url:
                embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        return embed

    async def poll(self):
        await self.bot.wait_until_ready()
        prev_url = ''
        while self.is_running:
            url = await self.find_url()
            if url and url != prev_url:
                embed = await self.build_embed(url)
                if embed:
                    await self.post(embed=embed)
                prev_url = url
            await asyncio.sleep(self.delay)
