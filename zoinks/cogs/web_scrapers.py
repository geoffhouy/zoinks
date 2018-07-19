import zoinks.bot
from zoinks.utils import web
from zoinks.web_scraper import WebScraper, SteamScraper

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
                         author=('League of Legends', self.BASE_URL),
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

        if self.author:
            embed.set_author(name=self.author[0], url=self.author[1])

        return embed


class FortniteWebScraper(WebScraper):

    BASE_URL = 'https://www.epicgames.com'

    def __init__(self, bot):
        super().__init__(bot,
                         output_channel_id=OUTPUT_CHANNEL_ID,
                         source_url=f'{self.BASE_URL}/fortnite/en-US/news/category/patch%20notes',
                         navigate_html=lambda soup: soup.find(class_='top-featured-activity').find('a').get('href'),
                         use_browser=True,
                         delay=60 * 60 * 24,
                         author=('Fortnite', self.BASE_URL),
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

        if self.author:
            embed.set_author(name=self.author[0], url=self.author[1])

        return embed


class RealmRoyaleScraper(SteamScraper):

    def __init__(self, bot):
        super().__init__(
            bot,
            output_channel_id=OUTPUT_CHANNEL_ID,
            steam_app_id=813820,
            delay=60 * 60 * 24,
            author=('Realm Royale', ''),
            color=0x9D69F4,
            thumbnail_url='https://steamcdn-a.akamaihd.net/steam/apps/813820/capsule_184x69.jpg')


class DarkestDungeonScraper(SteamScraper):

    def __init__(self, bot):
        super().__init__(
            bot,
            output_channel_id=OUTPUT_CHANNEL_ID,
            steam_app_id=262060,
            delay=60 * 60 * 24,
            author=('Darkest Dungeon', ''),
            color=0xFB3512,
            thumbnail_url='https://steamcdn-a.akamaihd.net/steam/apps/262060/header.jpg')


class WebScrapers:

    __slots__ = ('bot', 'lol_scraper', 'fn_scraper', 'rr_scraper', 'dd_scraper')

    def __init__(self, bot):
        self.bot = bot

        self.lol_scraper = LOLWebScraper(self.bot)
        self.fn_scraper = FortniteWebScraper(self.bot)
        self.rr_scraper = RealmRoyaleScraper(self.bot)
        self.dd_scraper = DarkestDungeonScraper(self.bot)
        self.start_scrapers()

        logger.info(f'{self.__class__.__name__} loaded')

    def start_scrapers(self):
        for slot in self.__slots__:
            if slot == 'bot':
                continue
            self.bot.loop.create_task(getattr(self, slot).poll())

    @commands.group(name='toggle')
    async def toggle(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(
                title='⚠ Error',
                description='The `toggle` command needs an argument.'),
                color=zoinks.bot.color)

    def _toggle(self, name):
        if name == 'bot' or name not in self.__slots__:
            raise ValueError('Invalid web scraper name')
        scraper = getattr(self, name)
        scraper.is_running = not scraper.is_running
        return scraper.is_running

    @staticmethod
    def _error_embed(name, status):
        status = 'on' if status else 'off'
        embed = discord.Embed(title='📰 Web Scraper Update',
                              description=f'The {name} web scraper has been turned {status}.',
                              color=zoinks.bot.color)
        return embed

    @toggle.command(name='league', aliases=['lol'])
    async def league(self, ctx):
        status = self._toggle('lol_scraper')
        await ctx.send(embed=self._error_embed('League of Legends patch notes', status))

    @toggle.command(name='fortnite', aliases=['fn'])
    async def fortnite(self, ctx):
        status = self._toggle('fn_scraper')
        await ctx.send(embed=self._error_embed('Fortnite patch notes', status))

    @toggle.command(name='realm', aliases=['rr'])
    async def realm(self, ctx):
        status = self._toggle('rr_scraper')
        await ctx.send(embed=self._error_embed('Realm Royale patch notes', status))

    @toggle.command(name='darkest', aliases=['dd'])
    async def darkest(self, ctx):
        status = self._toggle('dd_scraper')
        await ctx.send(embed=self._error_embed('Darkest Dungeon patch notes', status))


def setup(bot):
    bot.add_cog(WebScrapers(bot))
