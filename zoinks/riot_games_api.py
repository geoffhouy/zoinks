import config


REGION = {
    'br': {
        'name': 'Brazil',
        'platform': 'BR1'
    },
    'eune': {
        'name': 'Europe Nordic & East',
        'platform:': 'EUN1'
    },
    'euw': {
        'name': 'Europe West',
        'platform': 'EUW1'
    },
    'jp': {
        'name': 'Japan',
        'platform': 'JP1'
    },
    'kr': {
        'name': 'Korea',
        'platform': 'KR'
    },
    'lan': {
        'name': 'Latin America North',
        'platform': 'LA1'
    },
    'las': {
        'name': 'Latin America South',
        'platform': 'LA2'
    },
    'na': {
        'name': 'North America',
        'platform': 'NA1'
    },
    'oce': {
        'name': 'Oceania',
        'platform': 'OC1'
    },
    'ru': {
        'name': 'Russia',
        'platform': 'RU'
    },
    'tr': {
        'name': 'Turkey',
        'platform': 'TR1'
    }
}

URL = {
    'base': 'https://{platform}.api.riotgames.com/lol/{url}',
    'champion': 'platform/v{version}/champions',
    'champion_mastery_by_summoner': 'champion-mastery/v{version}/champion-masteries/by-summoner/{summoner_id}',
    'league_by_summoner': 'league/v{version}/positions/by-summoner/{summoner_id}',
    'lol_status': 'status/v{version}/shard-data',
    'masteries_by_summoner': 'platform/v{version}/masteries/by-summoner/{summoner_id}',
    'match_by_account': 'match/v{version}/matchlists/by-account/{account_id}',
    'match_by_match': 'match/v{version}/matches/{match_id}',
    'runes_by_summoner': 'platform/v{version}/runes/by-summoner/{summoner_id}',
    'spectator_by_summoner': 'spectator/v{version}/active-games/by-summoner/{summoner_id}',
    'static_data': 'static-data/v{version}/{category}',
    'summoner_by_name': 'summoner/v{version}/summoners/by-name/{name}'
}

VERSION = {
    'champion': 3,
    'champion_mastery': 3,
    'league': 3,
    'lol_status': 3,
    'masteries': 3,
    'match': 3,
    'runes': 3,
    'spectator': 3,
    'static_data': 3,
    'summoner': 3
}


class RiotGamesAPI:

    def __init__(self, bot):
        self._api_key = config.RIOT_GAMES_API_KEY
        self._region = 'na'
        self.bot = bot

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, region: str):
        if region not in REGION:
            raise ValueError(f'Invalid region: {region}')
        self._region = region

    async def _request(self, url: str, **kwargs):
        params = {'api_key': self._api_key}
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value

        url = URL['base'].format(platform=REGION[self.region]['platform'], url=url)

        async with self.bot.session.get(url=url, params=params) as response:
            return await response.json() if response.status == 200 else None

    async def get_summoner_by_name(self, name):
        return await self._request(url=URL['summoner_by_name'].format(version=VERSION['summoner'], name=name))
