import zoinks.bot
import zoinks.utils as utils
from zoinks.bot import ZOINKS

import discord

import asyncio
import logging
import re


logger = logging.getLogger(__name__)


class WebScraper:
    """Represents a basic web scraper that builds from the specified URL and displays the built
    discord.Embed message in the specified Discord text channel.
    """
    def __init__(self, bot: ZOINKS,
                 output_channel_id: int,
                 source_url: str,
                 navigate_html,
                 use_browser: bool=False,
                 delay: int=60 * 60 * 24,
                 author: tuple=(None, None),
                 color: int=zoinks.bot.color,
                 thumbnail_url: str=''):
        """Constructs a new web scraper.

        :param bot: The currently running ZOINKS Discord bot.
            Used for its session attribute.
        :param output_channel_id: The Discord text channel to display the messages in.
        :param source_url: The homepage URL of the content to post.
        :param navigate_html: The BeautifulSoup function chain to find
            the URL of the latest content from the source URL.
        :param use_browser: Whether or not the site needs a browser for JavaScript content to load correctly.
        :param delay: The time in seconds between checking for new content to post.
        :param color: The color of the discord.Embed to post.
            Typically matched with the homepage color scheme.
        :param thumbnail_url: The thumbnail URL of the discord.Embed to post.
            Typically used for logos.
        """
        self.bot = bot
        self.output_channel_id = output_channel_id

        self.source_url = source_url
        if not source_url:
            raise ValueError('Source URL must be set')

        self.navigate_html = navigate_html
        self.use_browser = use_browser
        self.delay = delay

        self.author = author
        self.color = color
        self.thumbnail_url = thumbnail_url

        self.is_running = True
        self.last_embed = None

    async def find_url_from_source(self):
        """Finds the specified target URL from the source_url by using the navigate_html BS4 function chain.

        :return: The result of following navigate_html from source_url.
            Typically used to grab the latest URL to a new news article.
        :rtype: str
        """
        if self.use_browser:
            soup = await utils.fetch_soup_with_browser(self.bot, self.source_url)
        else:
            soup = await utils.fetch_soup(self.bot, self.source_url)
        try:
            url = self.navigate_html(soup)
        except AttributeError as e:
            logger.warning(e)
            return None
        else:
            return url

    async def build_embed(self, url):
        """Builds an embed from the HTML meta properties of the specified URL.

        Override to change behavior for sites that don't provide meta properties.

        :param url: The URL with the content to post.
        :return: The built embed to post.
        :rtype discord.Embed
        """
        if self.use_browser:
            soup = await utils.fetch_soup_with_browser(self.bot, url)
        else:
            soup = await utils.fetch_soup(self.bot, url)

        if soup is None:
            return None

        title = soup.find(property='og:title')
        if title:
            title = title.get('content')

        description = soup.find(property='og:description')
        if description:
            description = description.get('content')
            if len(description) > 250:
                description = f'{description[:247]}...'

        embed = discord.Embed(title=title, description=description, url=url, color=self.color)

        image_url = soup.find(property='og:image')
        if image_url:
            image_url = image_url.get('content')
            if 'share_steam_logo' not in image_url:
                embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.author:
            embed.set_author(name=self.author[0], url=self.author[1])

        return embed

    async def poll(self):
        """Checks for a new URL to post content from every (delay) seconds.

        :return: None
        """
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(id=self.output_channel_id)
        if channel is None:
            raise ValueError('Invalid output channel')
        prev_url = ''
        while self.is_running:
            url = await self.find_url_from_source()

            if url and url != prev_url:
                embed = await self.build_embed(url)
                if embed is not None:
                    await channel.send(embed=embed)
                    logger.info(f'Posted article "{embed.title.strip()}"')
                    self.last_embed = embed
                prev_url = url

            await asyncio.sleep(self.delay)


class SteamScraper(WebScraper):

    def __init__(self, bot, output_channel_id, steam_app_id, delay, author, color, thumbnail_url):
        source_url = f'https://steamcommunity.com/games/{steam_app_id}/rss/'
        super().__init__(bot,
                         output_channel_id=output_channel_id,
                         source_url=source_url,
                         navigate_html=None,
                         use_browser=False,
                         delay=delay,
                         author=author,
                         color=color,
                         thumbnail_url=thumbnail_url)

    async def find_url_from_source(self):
        """Selects the first item from the Steam RSS XML instead of navigating through html."""
        soup = await utils.fetch_soup(self.bot, self.source_url)
        try:
            item = soup.select_one('item')
        except AttributeError as e:
            logger.warning(e)
            return None
        else:
            return item

    async def build_embed(self, item):
        """Uses the first XML item to build an embed."""
        title = item.find('title').get_text(strip=True)

        description = item.find('description').get_text(strip=True).replace('<br>', '\n')

        clean_description = re.sub('<[^<]+?>', '', description)
        if len(clean_description) > 250:
            clean_description = f'{clean_description[:247]}...'

        url = item.find('guid').get_text(strip=True)

        embed = discord.Embed(title=title, description=clean_description, url=url, color=self.color)

        image_url = re.search('<img src=\"(.*\.(?:png|jpg|gif))\"\s+>', description)
        if image_url:
            image_url = image_url.group(1)
            embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.author:
            embed.set_author(name=self.author[0], url=self.author[1])

        return embed
