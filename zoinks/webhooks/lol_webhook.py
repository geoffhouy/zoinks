from zoinks.bot import ZOINKS
from zoinks.webhooks.webhooks import ScrapingWebhook

import discord

import logging


logger = logging.getLogger(__name__)


class LoLWebhook(ScrapingWebhook):
    """Represents a URL-scraping webhook using Discord's endpoint URL.

    Specifically used to scrape the League of Legends homepage for new patch notes then build and post a rich
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
        self.base_url = 'https://na.leagueoflegends.com'
        source_url = f'{self.base_url}/en/news/game-updates/patch'

        super().__init__(bot=bot, endpoint_url=endpoint_url, source_url=source_url, **kwargs)

    async def build_embed(self, url):
        soup = await self.fetch_soup(self.source_url)
        content = soup.find(class_='views-row views-row-1 views-row-odd views-row-first')

        if content is None:
            return None

        title = content.find(class_='lol-core-file-formatter').get('title')

        description = content.find(class_='teaser-content').find('div').get_text(strip=True)

        url = f'{self.base_url}{url}'

        embed = discord.Embed(
            title=title,
            description=description,
            url=url,
            color=self.color)

        image_url = content.find(class_='lol-core-file-formatter').find('img').get('src')
        image_url = f'{self.base_url}{image_url}'
        embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        return embed
