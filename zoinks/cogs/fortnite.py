import zoinks.bot
from zoinks.utils import web
from zoinks.web_scraper import WebScraper

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)

OUTPUT_CHANNEL_ID = 450344550289113100


class FortniteWebScraper(WebScraper):

    BASE_URL = 'https://www.epicgames.com'

    def __init__(self, bot):
        super().__init__(bot,
                         output_channel_id=OUTPUT_CHANNEL_ID,
                         source_url=f'{self.BASE_URL}/fortnite/en-US/news/category/patch%20notes',
                         navigate_html=lambda soup: soup.find(class_='top-featured-activity').find('a').get('href'),
                         use_browser=True,
                         delay=60 * 60 * 24,
                         color=0x342353,
                         thumbnail_url='https://i.imgur.com/ICluMYQ.png')

    async def build_embed(self, url):
        soup = await web.fetch_soup_with_browser(self.bot, f'{self.BASE_URL}{url}')

        if soup is None:
            return None

        content = soup.find(class_='patch-notes-header section container-fluid')

        if content is None:
            return None

        title = content.find('h1').get_text(strip=True)

        description = soup.find('div', class_='col-xs-12 col-sm-11 col-lg-8').find('h1').get_text(strip=True)

        url = f'{self.BASE_URL}{url}'

        embed=discord.Embed(
            title=title,
            description=description,
            url=url,
            color=self.color)

        image_url = content.find(class_='background-image').get('style')
        image_url = image_url[image_url.find('(') + 1:image_url.find(')')]
        embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        embed.set_author(name='Fortnite', url=self.BASE_URL)

        return embed


class Fortnite:

    def __init__(self, bot):
        self.bot = bot
        self.web_scraper = FortniteWebScraper(self.bot)
        self.bot.loop.create_task(self.web_scraper.poll())
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.group(name='fn')
    async def fn(self, ctx):
        if ctx.invoked_subcommand is None:
            print('no sub')

    @fn.command(name='toggle')
    async def _toggle(self, ctx):
        self.web_scraper.is_running = not self.web_scraper.is_running
        status = 'on' if self.web_scraper.is_running else 'off'
        await ctx.send(embed=discord.Embed(
            title='📰 Web Scraper Update',
            description=f'The Fortnite patch notes web scraper has been turned {status}.',
            color=zoinks.bot.color))


def setup(bot):
    bot.add_cog(Fortnite(bot))
