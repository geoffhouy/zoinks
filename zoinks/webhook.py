from zoinks.bot import ZOINKS
from zoinks.utils import web

import discord

import json
import logging


logger = logging.getLogger(__name__)


class Webhook:
    """Represents a basic webhook that outputs to the specified Discord endpoint URL.

    Used to post a plain text message, a rich discord.Embed message, or a combination of the two
    into the specified Discord channel.

    In the Discord server settings, create a new webhook to retrieve its endpoint URL. During creation,
    its output channel, username, and avatar image will all be specified.
    """
    BASE_ENDPOINT_URL = 'https://discordapp.com/api/webhooks/'

    def __init__(self, bot: ZOINKS, endpoint_url: str, username: str=None, avatar_url: str=None):
        """Initializes a webhook for Discord.

        :param bot: The currently running ZOINKS Discord bot.
            Used for its session attribute.
        :param endpoint_url: The Discord webhook endpoint URL.
            Pass either the entire URL or all content after '/webhooks/'.
        :param username: The Discord webhook username.
            Used to override the current webhook name.
        :param avatar_url: The Discord webhook avatar image URL.
            Used to override the current webhook image.
        """
        self.bot = bot
        self.endpoint_url = endpoint_url
        self.username = username
        self.avatar_url = avatar_url

    @property
    def endpoint_url(self):
        return self.endpoint_url

    @endpoint_url.setter
    def endpoint_url(self, endpoint_url):
        if self.BASE_ENDPOINT_URL not in endpoint_url:
            self.endpoint_url = f'{self.BASE_ENDPOINT_URL}{endpoint_url}'
        else:
            self.endpoint_url = endpoint_url

    async def post(self, content: str=None, embed: discord.Embed=None, embeds: list=None):
        payload = {}

        if content:
            payload['content'] = content
        if embed:
            payload['embeds'] = [embed.to_dict()]
        if embeds:
            payload['embeds'] = [embed.to_dict() for embed in embeds if isinstance(embed, discord.Embed)]

        if not payload:
            logger.warning('POST Error: Payload must have content, at least one embed, or both')
            return None

        if self.username:
            payload['username'] = self.username
        if self.avatar_url:
            payload['avatar_url'] = self.avatar_url

        async with self.bot.session.post(url=self.endpoint_url,
                                         data=json.dumps(payload, indent=4),
                                         headers=web.SESSION_POST_HEADERS) as response:
            if response.status >= 400:
                logger.info('POST Failed')
                return False
            else:
                logger.info('POST Succeeded')
                return True
