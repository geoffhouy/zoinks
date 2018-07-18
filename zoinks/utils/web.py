from zoinks.bot import ZOINKS

import logging
from bs4 import BeautifulSoup


SESSION_GET_HEADERS = {'User-Agent': 'Mozilla/5.0'}
SESSION_POST_HEADERS = {'Content-Type': 'application/json'}

logger = logging.getLogger(__name__)


async def fetch_soup(bot: ZOINKS, url: str):
    async with bot.session.get(url=url, headers=SESSION_GET_HEADERS) as response:
        logger.info(f'CODE {response.status}: {url}')
        if response.status >= 400:
            return None
        else:
            content = await response.text()
            return BeautifulSoup(content, 'html.parser')
