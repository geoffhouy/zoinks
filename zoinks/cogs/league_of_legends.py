import zoinks.bot
from zoinks.utils import web
from zoinks.web_scraper import WebScraper

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)

OUTPUT_CHANNEL_ID = 450344550289113100


class LOLWebScraper(WebScraper):

    BASE_URL = 'https://na.leagueoflegends.com'

    def __init__(self, bot):
        super().__init__(bot,
                         output_channel_id=OUTPUT_CHANNEL_ID,
                         source_url=f'{self.BASE_URL}/en/news/game-updates/patch',
                         navigate_html=lambda soup: soup.find(
                             class_='views-row views-row-1 views-row-odd views-row-first').find(
                             class_='lol-core-file-formatter').get('href'),
                         delay=60 * 60 * 24,
                         color=0x96692A,
                         thumbnail_url='https://i.imgur.com/FaQI0Mw.png')

    async def build_embed(self, url):
        soup = await web.fetch_soup(self.bot, self.source_url)

        if soup is None:
            return None

        content = soup.find(class_='views-row views-row-1 views-row-odd views-row-first')

        if content is None:
            return None

        title = content.find(class_='lol-core-file-formatter').get('title')

        description = content.find(class_='teaser-content').find('div').get_text(strip=True)

        url = f'{self.BASE_URL}{url}'

        embed = discord.Embed(
            title=title,
            description=description,
            url=url,
            color=self.color)

        image_url = content.find(class_='lol-core-file-formatter').find('img').get('src')
        image_url = f'{self.BASE_URL}{image_url}'
        embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        embed.set_author(name='League of Legends', url=self.BASE_URL)

        return embed


class LeagueOfLegends:

    def __init__(self, bot):
        self.bot = bot
        self.web_scraper = LOLWebScraper(self.bot)
        self.bot.loop.create_task(self.web_scraper.poll())
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.group(name='lol')
    async def lol(self, ctx):
        if ctx.invoked_subcommand is None:
            print('No subcommand')

    @lol.command(name='toggle')
    async def _toggle(self, ctx):
        is_running = self.web_scraper.is_running
        is_running = not is_running
        status = 'on' if is_running else 'off'
        await ctx.send(embed=discord.Embed(
            title='📰 Web Scraper Update',
            description=f'The League of Legends patch notes web scraper has been turned {status}.',
            color=zoinks.bot.color))


def setup(bot):
    bot.add_cog(LeagueOfLegends(bot))
