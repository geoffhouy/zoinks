import zoinks.riot_games_api as riot_games_api
import zoinks.utils as utils
from zoinks.riot_games_api import RiotGamesAPI, PROFILE_ICON_URL, REGION

import discord
from discord.ext import commands

import asyncio
import logging
import string
from datetime import datetime


logger = logging.getLogger(__name__)

color = 0x96692A


class LeagueOfLegends:

    def __init__(self, bot):
        self.bot = bot
        self.api = RiotGamesAPI(self.bot)

        self.valid_summoner_name_chars = set(string.ascii_letters + string.digits + '.' + '_' + '')

        self.static_champion_data = None
        self.static_item_data = None
        self.static_map_data = None
        self.static_profile_icon_data = None
        self.static_reforged_rune_path_data = None
        self.static_reforged_rune_data = None
        self.static_summoner_spell_data = None

        logger.info(f'{self.__class__.__name__} loaded')

    async def on_ready(self):
        self.static_champion_data = await self.api.get_static_champion_data(tags='all', data_by_id=True)
        self.static_item_data = await self.api.get_static_item_data(tags='all')
        self.static_map_data = await self.api.get_static_map_data()
        self.static_reforged_rune_path_data = await self.api.get_static_reforged_rune_path_data()
        self.static_reforged_rune_data = await self.api.get_static_reforged_rune_data()
        self.static_summoner_spell_data = await self.api.get_static_summoner_spell_data(tags='all', data_by_id=True)
        logger.info(f'Static {self.__class__.__name__} data loaded')
        await asyncio.sleep(10)

    @commands.command()
    async def regions(self, ctx):
        """Displays all available regions for League of Legends commands."""
        embed = discord.Embed(title='🌎 League of Legends Command Regions',
                              description='Below is a list of available regions for League of Legends commands.',
                              color=color)
        embed.add_field(name='Region Name', value='\n'.join([REGION[key]['name'] for key in REGION.keys()]))
        embed.add_field(name='Usage in Commands', value='\n'.join(REGION.keys()))
        await ctx.send(embed=embed)

    @staticmethod
    def _error_embed(description: str):
        return discord.Embed(title='⚠ League of Legends Command Error',
                             description=description,
                             color=0xFFC83D)

    @commands.command()
    async def profile(self, ctx, region: str, *, name: str):
        """Displays the profile of the specified summoner name."""
        region = region.lower()

        if region not in REGION:
            return await ctx.send(embed=self._error_embed(
                description='Invalid region entered. '
                            f'Use `{self.bot.command_prefix}regions` to view available regions.'))

        name = ''.join(ch for ch in name if ch in self.valid_summoner_name_chars)

        if not name or len(name) < 3 or len(name) > 16:
            return await ctx.send(embed=self._error_embed(
                description='Invalid summoner name entered.'))

        summoner = await self.api.get_summoner_by_name(name=name, region=region)
        if isinstance(summoner, int):
            if summoner == 404:
                return await ctx.send(embed=self._error_embed(
                    description=f'Invalid summoner name entered.'))
            else:
                return await ctx.send(embed=self._error_embed(
                    description=f'Something went wrong!\n\nError code: {summoner}'))

        account_id = summoner.get('accountId')
        summoner_id = summoner.get('id')

        name = summoner.get('name')
        level = summoner.get('summonerLevel')
        profile_icon = summoner.get('profileIconId')
        op_gg = f'http://{region}.op.gg/summoner/userName={name.replace(" ", "")}'

        embed = discord.Embed(title='League of Legends Profile',
                              description=f'[{name}]({op_gg})\nRegion: {REGION[region]["name"]}\nLevel: {level}',
                              color=color)
        embed.set_thumbnail(url=PROFILE_ICON_URL.format(icon_id=profile_icon))

        league = await self.api.get_league_by_summoner_id(summoner_id=summoner_id, region=region)
        if isinstance(league, list) and league:
            tier = league[0].get('tier').title()
            rank = league[0].get('rank')
            lp = league[0].get('leaguePoints')
            wins = league[0].get('wins')
            losses = league[0].get('losses')
            ratio = f'{100 * wins / (wins + losses):.1f}'

            embed.add_field(name='Ranked Stats',
                            value=f'**{tier} {rank}** ({lp} LP)\n{wins}W/{losses}L\nWinrate: **{ratio}%**')

        if self.static_champion_data is None or isinstance(self.static_champion_data, int):
            self.static_champion_data = await self.api.get_static_champion_data(tags='all', data_by_id=True)

        if isinstance(self.static_champion_data, int):
            return await ctx.send(embed=self._error_embed(
                description='Unable to fetch data at the moment. Try again later.'))

        champion_mastery = await self.api.get_champion_mastery_by_summoner_id(summoner_id=summoner_id, region=region)
        if isinstance(champion_mastery, list) and champion_mastery:
            champions_to_display = 3 if len(champion_mastery) > 3 else len(champion_mastery)

            field_text = ''
            for i in range(0, champions_to_display):
                champion_id = champion_mastery[i].get('championId')
                champion_name = self.static_champion_data['keys'][str(champion_id)]
                champion_level = champion_mastery[i].get('championLevel')
                champion_points = champion_mastery[i].get('championPoints')
                field_text = (f'{field_text}'
                              f'{i + 1}. Level **{champion_level}**: {champion_name} ({champion_points} XP)\n')
            embed.add_field(name='Champion Mastery', value=field_text)

        spectator = await self.api.get_active_game_by_summoner_id(summoner_id=summoner_id, region=region)
        if isinstance(spectator, dict) and spectator:
            champion_id = ''
            for participant in spectator['participants']:
                if participant.get('summonerId') == summoner_id:
                    champion_id = participant.get('championId')
                    break

            queue_id = spectator.get('gameQueueConfigId')
            queue_name = riot_games_api.queue_name_from_id(id_=queue_id)
            champion_name = self.static_champion_data['keys'][str(champion_id)]

            embed.add_field(name='Last Seen',
                            value=f'Now playing a {queue_name} as {champion_name}', inline=False)
        else:
            match_history = await self.api.get_match_list_by_account_id(account_id=account_id, region=region,
                                                                        end_index=1)
            if isinstance(match_history, dict) and match_history:
                match_id = match_history['matches'][0]['gameId']

                match = await self.api.get_match_by_match_id(match_id=match_id, region=region)
                if isinstance(match, dict) and match:
                    participant_id = ''
                    for participant in match.get('participantIdentities'):
                        if participant.get('player').get('summonerId') == summoner_id:
                            participant_id = participant.get('participantId')
                            break

                    player = ''
                    for participant in match.get('participants'):
                        if participant.get('participantId') == participant_id:
                            player = participant
                            break

                    queue_id = match.get('queueId')
                    queue_name = riot_games_api.queue_name_from_id(id_=queue_id)
                    time_since_game = utils.datetime_to_time_ago_string(
                        datetime.now() - datetime.fromtimestamp(match.get('gameCreation') / 1000.0))
                    champion_id = player.get('championId')
                    champion_name = self.static_champion_data['keys'][str(champion_id)]
                    kills = player.get('stats').get('kills')
                    deaths = player.get('stats').get('deaths')
                    assists = player.get('stats').get('assists')
                    cs = player.get('stats').get('totalMinionsKilled', 0)
                    won = player.get('stats').get('win')
                    won = 'won' if won else 'lost'

                    embed.add_field(name='Last Seen',
                                    value=f'{time_since_game}, {won} a {queue_name} '
                                          f'as {champion_name} with a {kills}/{deaths}/{assists} KDA and {cs} CS',
                                    inline=False)

        await ctx.send(embed=embed)

    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            if error.param.name == 'region':
                await ctx.send(embed=self._error_embed(
                    description='No region entered. '
                                f'Use `{self.bot.command_prefix}regions` to view available regions.'))
            elif error.param.name == 'name':
                await ctx.send(embed=self._error_embed(
                    description='No summoner name entered.'))


def setup(bot):
    bot.add_cog(LeagueOfLegends(bot))
