from zoinks.bot import ZOINKS

import asyncio
import json
import logging
import os
from bs4 import BeautifulSoup
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

logger = logging.getLogger(__name__)

SESSION_GET_HEADERS = {'User-Agent': 'Mozilla/5.0'}
SESSION_POST_HEADERS = {'Content-Type': 'application/json'}


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


def merge_nested_dicts(dict1: dict, dict2: dict):
    merged_dict = defaultdict(dict)

    merged_dict.update(dict1)
    for key, nested_dict in dict2.items():
        if merged_dict.get(key) is None:
            merged_dict[key].update(nested_dict)
        else:
            for nested_key, value in nested_dict.items():
                new = merged_dict.get(key).get(nested_key, 0)
                old = nested_dict.get(nested_key, 0)
                diff = abs(new - old)
                if diff > 0:
                    merged_dict[key][nested_key] = old + diff

    return merged_dict


def new_json_file(file_dir: str, file_name: str, init_dict: dict):
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)

    path = os.path.join(file_dir, file_name)
    if not os.path.isfile(path):
        with open(path, 'w') as file:
            json.dump(init_dict, file, indent=4)


def datetime_to_time_ago_string(dt):
    days = dt.days
    hours, remainder = divmod(dt.seconds, 3600)
    if days > 0:
        text = '{0} days ago'.format(days)
    else:
        if hours > 1:
            text = '{0} hours ago'.format(hours)
        else:
            text = 'Less than one hour ago'
    return text
