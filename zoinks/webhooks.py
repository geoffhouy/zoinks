import discord

import asyncio
import json
import logging
import re
from bs4 import BeautifulSoup


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
                                         headers={'Content-Type': 'application/json'}) as response:
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
                                         headers={'Content-Type': 'application/json'}) as response:
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
    thumbnail: str
        The image URL of the discord.Embed thumbnail to post.
    """
    def __init__(self, bot, endpoint, **kwargs):
        super().__init__(bot, endpoint, **kwargs)
        self.source = kwargs.get('source')
        self.navigate_html = kwargs.get('navigate_html')
        self.poll_delay = kwargs.get('poll_delay')
        self.color = kwargs.get('color', 0x000000)
        self.thumbnail = kwargs.get('thumbnail', None)
        self.is_running = True

    async def _fetch(self, url):
        async with self.bot.session.get(url=url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            return soup

    async def _find(self):
        soup = await self._fetch(self.source)
        url = self.navigate_html(soup)
        return url

    async def _build(self, url):
        soup = await self._fetch(url)

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

        image = soup.find(property='og:image')
        if image:
            image = image.get('content')
            if 'share_steam_logo' not in image:
                embed.set_image(url=image)

        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)

        return embed

    async def poll(self):
        await self.bot.wait_until_ready()
        previous_content = ''
        while self.is_running:
            content = await self._find()
            if content and content != previous_content:
                embed = await self._build(content)
                if embed:
                    await self.post(embed)
                previous_content = content
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
    thumbnail: str
        The image URL of the discord.Embed thumbnail to post.
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
        image = re.search('<img src=\"(.*\.(?:png|jpg|gif))\"\s+>', image)
        if image:
            image = image.group(1)
            embed.set_image(url=image)

        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)

        return embed


class LeagueOfLegendsWebhook(URLWebhook):
    """Represents a URL-scraping webhook tailored to the League of Legends site using Discord's endpoint URL.

    Used to post a rich, embedded Discord message built from the source URL's
    patch notes into the specified Discord channel.

    Attributes
    ----------
    bot: commands.Bot
        The currently running Discord bot. Used for its session.
    endpoint: str
        The Discord webhook endpoint URL. Pass all content after '.../api/webhooks/'.
    source: str
        The source URL of the content to post.
    base_url: str
        The base of the URL. Used to build links found in the HTML.
    poll_delay: int
        The downtime between checking for new articles to post.
    color: int
        The color of the discord.Embed to post.
    thumbnail: str
        The image URL of the discord.Embed thumbnail to post.
    """
    def __init__(self, bot, endpoint, **kwargs):
        super().__init__(bot, endpoint, **kwargs)
        self.base_url = kwargs.get('base_url')

    async def _build(self, url):
        soup = await self._fetch(self.source)
        content = soup.find(class_='views-row views-row-1 views-row-odd views-row-first')

        title = content.find(class_='lol-core-file-formatter').get('title')

        description = content.find(class_='teaser-content').find('div').get_text(strip=True)

        url = f'{self.base_url}{url}'

        embed = discord.Embed(
            title=title,
            description=description,
            url=url,
            color=self.color)

        image = content.find(class_='lol-core-file-formatter').find('img').get('src')
        image = f'{self.base_url}{image}'
        embed.set_image(url=image)

        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)

        return embed
