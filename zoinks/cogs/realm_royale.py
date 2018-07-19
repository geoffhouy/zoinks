import zoinks.bot
from zoinks.web_scraper import SteamScraper

import discord
from discord.ext import commands

import logging


logger = logging.getLogger(__name__)

OUTPUT_CHANNEL_ID = 450344550289113100


class RealmRoyale:

    def __init__(self, bot):
        self.bot = bot
        self.web_scraper = SteamScraper(
            self.bot,
            output_channel_id=OUTPUT_CHANNEL_ID,
            steam_app_id=813820,
            delay=60 * 60 * 24,
            author=('Realm Royale', ''),
            color=0x9D69F4,
            thumbnail_url='https://steamcdn-a.akamaihd.net/steam/apps/813820/capsule_184x69.jpg')
        self.bot.loop.create_task(self.web_scraper.poll())
        logger.info(f'{self.__class__.__name__} loaded')

    @commands.group(name='rr')
    async def rr(self, ctx):
        if ctx.invoked_subcommand is None:
            print('no sub')

    @rr.command(name='toggle')
    async def _toggle(self, ctx):
        self.web_scraper.is_running = not self.web_scraper.is_running
        status = 'on' if self.web_scraper.is_running else 'off'
        await ctx.send(embed=discord.Embed(
            title='📰 Web Scraper Update',
            description=f'The Realm Royale patch notes web scraper has been turned {status}.',
            color=zoinks.bot.color))


def setup(bot):
    bot.add_cog(RealmRoyale(bot))
