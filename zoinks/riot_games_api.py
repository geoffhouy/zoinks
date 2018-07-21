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
    'champion-mastery-by-summoner-id': 'champion-mastery/v{version}/champion-masteries/by-summoner/{summoner_id}',
    'champions-by-champion-id': 'platform/v{version}/champions/{champion_id}',
    'champions': 'platform/v{version}/champions',
    'league-by-summoner-id': 'league/v{version}/positions/by-summoner/{summoner_id}',
    'lol-static-data': 'static-data/v{version}/{category}',
    'lol-status': 'status/v{version}/shard-data',
    'match-by-match-id': 'match/v{version}/matches/{match_id}',
    'matchlists-by-account-id': 'match/v{version}/matchlists/by-account/{account_id}',
    'spectator-by-summoner-id': 'spectator/v{version}/active-games/by-summoner/{summoner_id}',
    'summoner-by-name': 'summoner/v{version}/summoners/by-name/{name}',
}

VERSION = {
    'champion-mastery': 3,
    'champion': 3,
    'league': 3,
    'lol-static-data': 3,
    'lol-status': 3,
    'match': 3,
    'spectator': 3,
    'summoner': 3,
    'tournament-stub': 3,
    'tournament': 3
}


class RiotGamesAPI:

    def __init__(self, bot):
        self._api_key = config.RIOT_GAMES_API_KEY
        self._default_region = 'na'
        self.bot = bot

    async def _request(self, url: str, region: str, **kwargs):
        params = {'api_key': self._api_key}
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value

        if region is None:
            region = self._default_region
        elif region not in REGION:
            raise ValueError(f'Invalid region: {region}')

        url = URL['base'].format(platform=REGION[region]['platform'], url=url)

        async with self.bot.session.get(url=url, params=params) as response:
            return await response.json() if response.status == 200 else None

    async def get_champion_mastery_by_summoner_id(self, summoner_id: int, region: str=None):
        return await self._request(
            url=URL['champion-mastery-by-summoner-id'].format(
                version=VERSION['champion-mastery'],
                summoner_id=summoner_id
            ),
            region=region)

    async def get_summoner_by_name(self, name: str, region: str=None):
        return await self._request(
            url=URL['summoner-by-name'].format(
                version=VERSION['summoner'],
                name=name),
            region=region)
