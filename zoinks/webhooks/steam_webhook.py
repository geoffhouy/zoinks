from zoinks.webhooks.webhooks import ScrapingWebhook

import discord

import logging
import re


logger = logging.getLogger(__name__)


class SteamWebhook(ScrapingWebhook):

    def __init__(self, bot, endpoint_url, **kwargs):
        super().__init__(bot, endpoint_url, **kwargs)

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
