from zoinks.bot import ZOINKS

import asyncio
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


SESSION_GET_HEADERS = {'User-Agent': 'Mozilla/5.0'}
SESSION_POST_HEADERS = {'Content-Type': 'application/json'}

logger = logging.getLogger(__name__)


async def fetch_soup(bot: ZOINKS, url: str):
    async with bot.session.get(url=url, headers=SESSION_GET_HEADERS) as response:
        logger.debug(f'CODE {response.status}: {url}')
        if response.status >= 400:
            return None
        else:
            content = await response.text()
            return BeautifulSoup(content, 'html.parser')


@asyncio.coroutine
def fetch_soup_with_browser(bot: ZOINKS, url: str):
    options = Options()
    options.headless = True

    browser = webdriver.Firefox(
            executable_path='D:\\Utilities\\geckodriver\\geckodriver.exe',
            firefox_options=options,
            log_path='D:\\Utilities\\geckodriver\\geckodriver.log')
    browser.implicitly_wait(10)

    try:
        future = bot.loop.run_in_executor(None, browser.get, url)
        yield from future
        content = browser.page_source
        browser.quit()
    except Exception as e:
        logger.warning(e)
        return None
    else:
        return BeautifulSoup(content, 'html.parser')
