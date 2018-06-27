import discord

import asyncio
import json
import logging
import re
from bs4 import BeautifulSoup


get_headers = {'User-Agent': 'Mozilla/5.0'}
post_headers = {'Content-Type': 'application/json'}

logger = logging.getLogger(__name__)


class Webhook:
    """Represents a basic webhook using Discord's endpoint URL*.

    Used to post a simple text message into the specified Discord channel**.

    *The endpoint URL can be retrieved by creating one for a Discord server in its settings.
    **The endpoint URL will dictate which channel the message will be displayed in.

    Attributes
    ----------
    bot: commands.Bot
        The currently running Discord bot. Used for its session.
    endpoint: str
        The Discord webhook endpoint URL. Pass all content after '.../api/webhooks/'.
    content: str
        The message to post.
    """
    def __init__(self, bot, endpoint, **kwargs):
        self.bot = bot
        self.endpoint = f'https://discordapp.com/api/webhooks/{endpoint}'
        self.__content = kwargs.get('content')

    async def post(self, content=None):
        if self.__content is None and content is None:
            raise ValueError('Content must be set before posting')
        post_content = None
        if self.__content:
            post_content = self.__content
        if content:
            post_content = content
        payload = {'content': post_content}
        async with self.bot.session.post(url=self.endpoint,
                                     data=payload,
                                     headers=post_headers) as response:
            print(response)


class RichWebhook(Webhook):
    """Represents a rich webhook using Discord's endpoint URL.

    Used to post a rich, embedded Discord message into the specified Discord channel.

    Attributes
    ----------
    bot: commands.Bot
        The currently running Discord bot. Used for its session.
    endpoint: str
        The Discord webhook endpoint URL. Pass all content after '.../api/webhooks/'.
    embed: discord.Embed
        The rich, embedded message to post.
    """
    def __init__(self, bot, endpoint, **kwargs):
        super().__init__(bot, endpoint, **kwargs)
        self.__embed = kwargs.get('embed')

    async def post(self, embed=None):
        if self.__embed is None and embed is None:
            raise ValueError('Embed must be set before posting')
        if not isinstance(self.__embed, discord.Embed) and not isinstance(embed, discord.Embed):
            raise ValueError('Embed must be of type discord.Embed')
        post_embed = None
        if self.__embed:
            post_embed = self.__embed
        if embed:
            post_embed = embed
        post_embed = post_embed.to_dict()
        title = post_embed.get('title')
        payload = {'embeds': [post_embed]}
        async with self.bot.session.post(url=self.endpoint,
                                     data=json.dumps(payload, indent=4),
                                     headers=post_headers) as response:
            if response.status == 400:
                logger.info(f'Failed to POST {title}: {response.status}')
            else:
                logger.info(f'POST {title}')


class URLWebhook(RichWebhook):
    """Represents a URL-scraping webhook using Discord's endpoint URL.

    Used to post a rich, embedded Discord message built from the source URL's
    news articles into the specified Discord channel.

    Attributes
    ----------
    bot: commands.Bot
        The currently running Discord bot. Used for its session.
    endpoint: str
        The Discord webhook endpoint URL. Pass all content after '.../api/webhooks/'.
    source: str
        The source URL of the content to post.
    navigate_html: lambda function
        The BeautifulSoup function chain to find new articles within the source URL's HTML.
    poll_delay: int
        The downtime between checking for new articles to post.
    color: int
        The color of the discord.Embed to post.
    footer: tuple
        The footer text and footer icon of the discord.Embed to post.
    """
    def __init__(self, bot, endpoint, **kwargs):
        super().__init__(bot, endpoint, **kwargs)
        self.source = kwargs.get('source')
        self.navigate_html = kwargs.get('navigate_html')
        self.poll_delay = kwargs.get('poll_delay')
        self.color = kwargs.get('color', 0x000000)
        self.footer = kwargs.get('footer', (None, None))
        self.is_running = True

    async def _fetch(self, url):
        async with self.bot.session.get(url=url, headers=get_headers) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            return soup

    async def _find(self):
        soup = await self._fetch(self.source)
        url = self.navigate_html(soup)
        return url

    async def _build(self, url):
        content = await self._fetch(url)

        title = content.find(property='og:title')
        title = title.get('content') if title else ''

        description = content.find(property='og:description')
        description = description.get('content') if description else ''
        if len(description) > 250:
            description = f'{description[:253]}...'

        embed = discord.Embed(
            title=title,
            description=description,
            url=url,
            color=self.color
        )

        thumbnail = content.find(property='og:image')
        thumbnail = thumbnail.get('content') if thumbnail else ''
        embed.set_thumbnail(url=thumbnail)

        text, icon_url = self.footer
        if text is None:
            text = ''
        if icon_url is None:
            icon_url = ''
        embed.set_footer(text=text, icon_url=icon_url)

        return embed

    async def poll(self):
        await self.bot.wait_until_ready()
        last_post = ''
        while self.is_running:
            post = await self._find()
            if post and post != last_post:
                embed = await self._build(post)
                if embed:
                    await self.post(embed)
                last_post = post
            await asyncio.sleep(self.poll_delay)


class SteamRSSWebhook(URLWebhook):
    """Represents a Steam RSS, URL-scraping webhook using Discord's endpoint URL.

    Used to post a rich, embedded Discord message built from the source URL's
    Steam RSS feed into the specified Discord channel.

    Attributes
    ----------
    bot: commands.Bot
        The currently running Discord bot. Used for its session.
    endpoint: str
        The Discord webhook endpoint URL. Pass all content after '.../api/webhooks/'.
    source: str
        The source URL of the content to post.
    poll_delay: int
        The downtime between checking for new articles to post.
    color: int
        The color of the discord.Embed to post.
    footer: tuple
        The footer text and footer icon of the discord.Embed to post.
    """
    def __init__(self, bot, endpoint, **kwargs):
        super().__init__(bot, endpoint, **kwargs)

    async def _find(self):
        soup = await self._fetch(self.source)
        item = soup.select_one('item')
        return item

    async def _build(self, item):
        title = item.find('title').get_text(strip=True)

        url = item.find('guid').get_text(strip=True)

        description = item.find('description').get_text(strip=True)
        description = re.sub('<[^<]+?>', '', description)
        if len(description) > 250:
            description = f'{description[:253]}...'

        embed = discord.Embed(
            title=title,
            url=url,
            description=description,
            color=self.color)

        image = item.find('description').get_text(strip=True)
        image = re.search('<img src=\"(.*\.(?:png|jpg|gif))\"\s+>', image).group(1)
        if image:
            embed.set_image(url=image)

        text, icon_url = self.footer
        if text is None:
            text = 'Untitled'
        if icon_url is None:
            icon_url = ''
        embed.set_footer(text=text, icon_url=icon_url)

        return embed
