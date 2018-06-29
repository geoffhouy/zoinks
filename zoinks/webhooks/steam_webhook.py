from zoinks.bot import ZOINKS
from zoinks.webhooks.webhooks import ScrapingWebhook

import discord

import logging
import re


logger = logging.getLogger(__name__)


class SteamWebhook(ScrapingWebhook):
    """Represents a URL-scraping webhook that outputs to the specified Discord endpoint URL.

    Specifically used to scrape the specified Steam RSS feed then build and post a rich
    discord.Embed message into the specified Discord channel.

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
    steam_app_id: int
        The Steam app's numerical ID found in its store URL.
    delay: int
        The time in seconds between checking for new content to post.
    color: int
        The color of the discord.Embed to post. Typically matched with the homepage color scheme.
    thumbnail_url: str
        The thumbnail URL of the discord.Embed to post. Typically used for logos.
    """
    def __init__(self, bot: ZOINKS, endpoint_url: str, steam_app_id: int=None, **kwargs):
        if steam_app_id is None:
            raise ValueError('Steam app ID must be set')
        source_url = f'https://steamcommunity.com/games/{steam_app_id}/rss/'

        super().__init__(bot=bot, endpoint_url=endpoint_url, source_url=source_url, **kwargs)

    async def find_url(self):
        soup = await self.fetch_soup(self.source_url)
        try:
            item = soup.select_one('item')
        except AttributeError as e:
            logger.warning(e)
            return None
        else:
            return item

    async def build_embed(self, item):
        title = item.find('title').get_text(strip=True)

        description = item.find('description').get_text(strip=True)

        clean_description = re.sub('<[^<]+?>', '', description)
        if len(clean_description) > 250:
            clean_description = f'{clean_description[:247]}...'

        url = item.find('guid').get_text(strip=True)

        embed = discord.Embed(
            title=title,
            description=clean_description,
            url=url,
            color=self.color)

        image_url = re.search('<img src=\"(.*\.(?:png|jpg|gif))\"\s+>', description)
        if image_url:
            image_url = image_url.group(1)
            embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        return embed
