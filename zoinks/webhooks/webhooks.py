from zoinks.bot import ZOINKS

import discord

import json
import logging


logger = logging.getLogger(__name__)


class Webhook:
    """Represents a basic webhook using Discord's endpoint URL.

    Used to post a plain text message, a rich discord.Embed message, or a combination of the two
    into the specified Discord channel.

    In the Discord server settings, create a new webhook to retrieve its endpoint URL. During creation,
    its output channel, username, and avatar image will all be specified.

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
    """
    BASE_URL = 'https://discordapp.com/api/webhooks/'

    def __init__(self, bot: ZOINKS, endpoint_url: str, **kwargs):
        self.bot = bot

        if self.BASE_URL not in endpoint_url:
            self.endpoint_url = f'{self.BASE_URL}{endpoint_url}'
        else:
            self.endpoint_url = endpoint_url

        self.username = kwargs.get('username')
        self.avatar_url = kwargs.get('avatar_url')

    async def post(self, content: str=None, embed: discord.Embed=None):
        payload = {}

        if content:
            payload['content'] = content
        if embed:
            payload['embeds'] = [embed]

        if not payload:
            raise ValueError('No information received to create payload')

        title = embed.get('title')

        if self.username:
            payload['username'] = self.username
        if self.avatar_url:
            payload['avatar_url'] = self.avatar_url

        async with self.bot.session.post(url=self.endpoint_url,
                                         data=json.dumps(payload, indent=4),
                                         headers={'Content-Type': 'application/json'}) as response:
            if response.status >= 400:
                logger.info(f'Failed to POST: {response.status}')
            else:
                logger.info(f'POST "{title}"')

