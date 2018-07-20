import config
import zoinks.bot
import zoinks.utils as utils
from zoinks.web_scraper import WebScraper, SteamScraper

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)


class LeagueOfLegendsScraper(WebScraper):

    BASE_URL = 'https://na.leagueoflegends.com'

    def __init__(self, bot):
        super().__init__(bot,
                         output_channel_id=config.WEB_SCRAPER_OUTPUT_CHANNEL_ID[0],
                         source_url=f'{self.BASE_URL}/en/news/game-updates/patch',
                         navigate_html=lambda soup: soup.find(
                             class_='views-row views-row-1 views-row-odd views-row-first').find(
                             class_='lol-core-file-formatter').get('href'),
                         delay=60 * 60 * 24,
                         author=('League of Legends', self.BASE_URL),
                         color=0x96692A,
                         thumbnail_url='https://i.imgur.com/FaQI0Mw.png')

    async def build_embed(self, url):
        soup = await utils.fetch_soup(self.bot, self.source_url)

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


class DotaScraper(WebScraper):

    def __init__(self, bot):
        super().__init__(
            bot,
            output_channel_id=config.WEB_SCRAPER_OUTPUT_CHANNEL_ID[0],
            source_url='https://store.steampowered.com/news/?appids=570&appgroupname=Dota+2&feed=steam_updates',
            navigate_html=lambda soup: soup.find(class_='newsPostBlock steam_updates').find('a').get('href'),
            use_browser=False,
            delay=60 * 60 * 24,
            author=('Dota 2', ''),
            color=0xFB3512,
            thumbnail_url='https://steamcdn-a.akamaihd.net/steam/apps/570/capsule_184x69.jpg')


class OverwatchScraper(WebScraper):

    def __init__(self, bot):
        super().__init__(bot,
                         output_channel_id=config.WEB_SCRAPER_OUTPUT_CHANNEL_ID[0],
                         source_url='http://playoverwatch.com/en-us/game/patch-notes/pc/',
                         navigate_html=lambda soup: soup.find(
                             class_='column lg-3').find(class_='u-float-left').get('href'),
                         use_browser=True,
                         delay=60 * 60 * 24,
                         author=('Overwatch', 'https://playoverwatch.com/en-us/'),
                         color=0xFA9C1E,
                         thumbnail_url='https://i.imgur.com/E1CqJXn.png')

    async def build_embed(self, url):
        url = f'{self.source_url}{url}'

        soup = await utils.fetch_soup_with_browser(self.bot, url)

        if soup is None:
            return None

        content = soup.find(class_='column lg-9 patch-notes-body')

        if content is None:
            return None

        patch_number = url.split('#')[1]

        title = soup.find('a', href=f'#{patch_number}').find('h3').get_text(strip=True)

        description = content.find('p').get_text(strip=True)

        embed = discord.Embed(title=title, description=description, url=url, color=self.color)

        image_url = content.find(class_='HeadingBanner').get('style')
        image_url = image_url[image_url.find('(') + 1:image_url.find(')')]
        embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.author:
            embed.set_author(name=self.author[0], url=self.author[1])

        return embed


class FortniteScraper(WebScraper):

    BASE_URL = 'https://www.epicgames.com'

    def __init__(self, bot):
        super().__init__(bot,
                         output_channel_id=config.WEB_SCRAPER_OUTPUT_CHANNEL_ID[0],
                         source_url=f'{self.BASE_URL}/fortnite/en-US/news/category/patch%20notes',
                         navigate_html=lambda soup: soup.find(class_='top-featured-activity').find('a').get('href'),
                         use_browser=True,
                         delay=60 * 60 * 24,
                         author=('Fortnite', self.BASE_URL),
                         color=0x342353,
                         thumbnail_url='https://i.imgur.com/ICluMYQ.png')

    async def build_embed(self, url):
        soup = await utils.fetch_soup_with_browser(self.bot, f'{self.BASE_URL}{url}')

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
            output_channel_id=config.WEB_SCRAPER_OUTPUT_CHANNEL_ID[0],
            steam_app_id=813820,
            delay=60 * 60 * 24,
            author=('Realm Royale', ''),
            color=0x9D69F4,
            thumbnail_url='https://steamcdn-a.akamaihd.net/steam/apps/813820/capsule_184x69.jpg')


class RuneScapeScraper(WebScraper):

    def __init__(self, bot):
        super().__init__(
            bot,
            output_channel_id=config.WEB_SCRAPER_OUTPUT_CHANNEL_ID[0],
            source_url='https://oldschool.runescape.com/',
            navigate_html=lambda soup: soup.find(class_='news-article ').find('h3').find('a').get('href'),
            use_browser=False,
            delay=60 * 60 * 24,
            author=('RuneScape', 'https://oldschool.runescape.com/'),
            color=0x162431,
            thumbnail_url='https://i.imgur.com/6H15qI6.png'
        )

    async def build_embed(self, url):
        soup = await utils.fetch_soup(self.bot, self.source_url)

        if soup is None:
            return None

        content = soup.find(class_='news-article ')

        if content is None:
            return None

        title = content.find('h3').find('a').get_text(strip=True)

        description = content.find('figure').find('img').get('title').replace('\r', '').replace('\n', '')

        embed = discord.Embed(title=title, description=description, url=url, color=self.color)

        image_url = content.find('figure').find('img').get('src')
        embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.author:
            embed.set_author(name=self.author[0], url=self.author[1])

        return embed


class MinecraftScraper(WebScraper):

    BASE_URL = 'https://minecraft.net'

    def __init__(self, bot):
        super().__init__(
            bot,
            output_channel_id=config.WEB_SCRAPER_OUTPUT_CHANNEL_ID[0],
            source_url=f'{self.BASE_URL}/en-us/',
            navigate_html=lambda soup: soup.find(id='1-2').find('a').get('href'),
            use_browser=True,
            delay=60 * 60 * 24,
            author=('Minecraft', 'https://minecraft.net/en-us/'),
            color=0x9ECF66,
            thumbnail_url='https://minecraft.net/favicon-96x96.png'
        )

    async def build_embed(self, url):
        url = f'{self.BASE_URL}{url}'

        soup = await utils.fetch_soup(self.bot, url)

        if soup is None:
            return None

        content = soup.find(class_='site-body ')

        if content is None:
            return None

        title = content.find(class_='container article-paragraph--header').find('h1').get_text(strip=True)

        description = content.find(class_='container article-paragraph--header').find('p').get_text(strip=True)

        embed = discord.Embed(title=title, description=description, url=url, color=self.color)

        image_url = content.find(class_='article-head').find('img').get('src')
        embed.set_image(url=image_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.author:
            embed.set_author(name=self.author[0], url=self.author[1])

        return embed


class DarkestDungeonScraper(SteamScraper):

    def __init__(self, bot):
        super().__init__(
            bot,
            output_channel_id=config.WEB_SCRAPER_OUTPUT_CHANNEL_ID[0],
            steam_app_id=262060,
            delay=60 * 60 * 24,
            author=('Darkest Dungeon', ''),
            color=0xFB3512,
            thumbnail_url='https://steamcdn-a.akamaihd.net/steam/apps/262060/header.jpg')


class WebScrapers:

    __slots__ = ('bot',
                 'lol_scraper', 'd2_scraper',
                 'ow_scraper',
                 'fn_scraper', 'rr_scraper',
                 'rs_scraper',
                 'mc_scraper',
                 'dd_scraper')

    def __init__(self, bot):
        self.bot = bot

        self.lol_scraper = LeagueOfLegendsScraper(self.bot)
        self.d2_scraper = DotaScraper(self.bot)
        self.ow_scraper = OverwatchScraper(self.bot)
        self.fn_scraper = FortniteScraper(self.bot)
        self.rr_scraper = RealmRoyaleScraper(self.bot)
        self.rs_scraper = RuneScapeScraper(self.bot)
        self.mc_scraper = MinecraftScraper(self.bot)
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
        """Turns a web scraper on or off depending on its current status."""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=discord.Embed(
                title='⚠ Error',
                description='The `toggle` command needs an argument.',
                color=zoinks.bot.color))

    def _toggle(self, name):
        if name == 'bot' or name not in self.__slots__:
            raise ValueError('Invalid web scraper name')
        scraper = getattr(self, name)
        scraper.is_running = not scraper.is_running
        return scraper.is_running

    @staticmethod
    def _status_embed(name, status):
        status = 'on' if status else 'off'
        embed = discord.Embed(title='📰 Web Scraper Update',
                              description=f'The {name} web scraper has been turned {status}.',
                              color=zoinks.bot.color)
        return embed

    @toggle.command(name='league', aliases=['lol'])
    async def league(self, ctx):
        status = self._toggle('lol_scraper')
        await ctx.send(embed=self._status_embed('League of Legends patch notes', status))

    @toggle.command(name='dota', aliases=['d2'])
    async def dota(self, ctx):
        status = self._toggle('d2_scraper')
        await ctx.send(embed=self._status_embed('Dota 2 patch notes', status))

    @toggle.command(name='overwatch', aliases=['ow'])
    async def overwatch(self, ctx):
        status = self._toggle('ow_scraper')
        await ctx.send(embed=self._status_embed('Overwatch patch notes', status))

    @toggle.command(name='fortnite', aliases=['fn'])
    async def fortnite(self, ctx):
        status = self._toggle('fn_scraper')
        await ctx.send(embed=self._status_embed('Fortnite patch notes', status))

    @toggle.command(name='realm', aliases=['rr'])
    async def realm(self, ctx):
        status = self._toggle('rr_scraper')
        await ctx.send(embed=self._status_embed('Realm Royale patch notes', status))

    @toggle.command(name='runescape', aliases=['rs'])
    async def runescape(self, ctx):
        status = self._toggle('rs_scraper')
        await ctx.send(embed=self._status_embed('RuneScape patch notes', status))

    @toggle.command(name='minecraft', aliases=['mc'])
    async def minecraft(self, ctx):
        status = self._toggle('mc_scraper')
        await ctx.send(embed=self._status_embed('Minecraft news', status))

    @toggle.command(name='darkest', aliases=['dd'])
    async def darkest(self, ctx):
        status = self._toggle('dd_scraper')
        await ctx.send(embed=self._status_embed('Darkest Dungeon patch notes', status))


def setup(bot):
    bot.add_cog(WebScrapers(bot))
