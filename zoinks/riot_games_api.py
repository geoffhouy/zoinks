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

URL = {
    'base': 'https://{platform}.api.riotgames.com/lol/{url}',
    'champion-mastery-by-summoner-id': 'champion-mastery/v{version}/champion-masteries/by-summoner/{summoner_id}',
    'champions-by-champion-id': 'platform/v{version}/champions/{champion_id}',
    'champions': 'platform/v{version}/champions',
    'league-by-summoner-id': 'league/v{version}/positions/by-summoner/{summoner_id}',
    'lol-static-data': 'static-data/v{version}/{category}',
    'lol-status': 'status/v{version}/shard-data',
    'match-by-match-id': 'match/v{version}/matches/{match_id}',
    'match-lists-by-account-id': 'match/v{version}/matchlists/by-account/{account_id}',
    'spectator-by-summoner-id': 'spectator/v{version}/active-games/by-summoner/{summoner_id}',
    'summoner-by-name': 'summoner/v{version}/summoners/by-name/{name}',
}


class RiotGamesAPI:

    def __init__(self, bot):
        self._api_key = config.RIOT_GAMES_API_KEY
        self._default_region = 'na'
        self.bot = bot

    async def _request(self, url, region, **kwargs):
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
                summoner_id=summoner_id),
            region=region)

    async def get_champion_list(self):
        return await self._request(
            url=URL['champions'].format(
                version=VERSION['champion']
            ), region=None)

    async def get_champion_by_champion_id(self, champion_id: int):
        return await self._request(
            url=URL['champions-by-champion-id'].format(
                version=VERSION['champion'],
                champion_id=champion_id),
            region=None)

    async def get_league_by_summoner_id(self, summoner_id: int, region: str=None):
        return await self._request(
            url=URL['league-by-summoner-id'].format(
                version=VERSION['league'],
                summoner_id=summoner_id),
            region=region)

    async def get_static_champion_data(self):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category='champions'),
            region=None)

    async def get_static_champion_data_by_id(self, id_: int):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category=f'champions/{id_}'),
            region=None)

    async def get_static_item_data(self):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category='items'),
            region=None)

    async def get_static_item_data_by_id(self, id_: int):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category=f'items/{id_}'),
            region=None)

    async def get_static_map_data(self):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category='maps'),
            region=None)

    async def get_static_profile_icon_data(self):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category='profile-icons'),
            region=None)

    async def get_static_reforged_rune_data(self):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category='reforged-runes'),
            region=None)

    async def get_static_reforged_rune_data_by_id(self, id_: int):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category=f'reforged-runes/{id_}'),
            region=None)

    async def get_static_summoner_spell_data(self):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category='summoner-spells'),
            region=None)

    async def get_static_summoner_spell_data_by_id(self, id_: int):
        return await self._request(
            url=URL['lol-static-data'].format(
                version=VERSION['lol-static-data'],
                category=f'summoner-spells/{id_}'),
            region=None)

    async def get_server_status(self, region: str=None):
        return await self._request(
            url=URL['lol-status'].format(
                version=VERSION['lol-status']),
            region=region)

    async def get_match_by_match_id(self, match_id: int, region: str=None):
        return await self._request(
            url=URL['match-by-match-id'].format(
                version=VERSION['match'],
                match_id=match_id),
            region=region)

    async def get_match_list_by_account_id(self, account_id: int, region: str=None):
        return await self._request(
            url=URL['match-lists-by-account-id'].format(
                version=VERSION['match'],
                account_id=account_id),
            region=region)

    async def get_active_game_by_summoner_id(self, summoner_id: int, region: str=None):
        return await self._request(
            url=URL['spectator-by-summoner-id'].format(
                version=VERSION['spectator'],
                summoner_id=summoner_id),
            region=region)

    async def get_summoner_by_name(self, name: str, region: str=None):
        return await self._request(
            url=URL['summoner-by-name'].format(
                version=VERSION['summoner'],
                name=name),
            region=region)
