from zoinks.utils import web
from zoinks.bot import ZOINKS

import discord

import asyncio
import logging


logger = logging.getLogger(__name__)


class WebScraper:
    """Represents a basic web scraper that builds from the specified URL and displays the built
    discord.Embed message in the specified Discord text channel.
    """
    def __init__(self, bot: ZOINKS, output_channel_id: int, source_url: str, navigate_html,
                 delay: int=60 * 60 * 24, color: int=0x4D9C5F, thumbnail_url: str=''):
        """Constructs a new web scraper.

        :param bot: The currently running ZOINKS Discord bot.
            Used for its session attribute.
        :param output_channel_id: The Discord text channel to display the messages in.
        :param source_url: The homepage URL of the content to post.
        :param navigate_html: The BeautifulSoup function chain to find
            the URL of the latest content from the source URL.
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
        self.delay = delay

        self.color = color
        self.thumbnail_url = thumbnail_url

        self.is_running = True
        self.last_embed = None

    async def find_url_from_source(self):
        soup = await web.fetch_soup(self.bot, self.source_url)
        try:
            url = self.navigate_html(soup)
        except AttributeError as e:
            logger.warning(e)
            return None
        else:
            return url

    async def build_embed(self, url):
        soup = await web.fetch_soup(self.bot, url)

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
                    logger.info(f'Posted article "{embed.title}"')
                    self.last_embed = embed
                prev_url = url

            await asyncio.sleep(self.delay)
