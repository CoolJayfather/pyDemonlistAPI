import sys
import logging
import requests
from countryflag import getflag
from typing import Literal, get_args

API_URL = 'https://api.demonlist.org'

class StateError: pass

DisplayMode = Literal['default', 'list']
ListType = Literal['classic', 'future']
RecordsType = Literal['all', 'main', 'basic', 'extended', 'beyond', 'verified', 'progress']
CountriesType = Literal['main', 'advanced']
OrderBy = Literal['newest', 'oldest', 'place']
LogLevel = Literal['info', 'error']

logger = logging.getLogger('Demonlist API')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def demonlist_log_level(log_level: LogLevel = 'error'):
    if log_level == 'error':
        logger.setLevel(logging.ERROR)
    elif log_level == 'info':
        logger.setLevel(logging.INFO)
    else:
        raise ValueError('"log_level" must be "error" or "info"')

def _connector(url, params = None):
    response = requests.get(url, params)
    response.raise_for_status()

    return response.json()['data']

def players_ranking(offset = 0, limit = 0, country = 'any', display_mode: DisplayMode = 'default'):
    """Retrieves a slice of the top players leaderboard.

        :param offset: The starting index for the player list.
        :type offset: int
        :param limit: The maximum number of players to return.
        :type limit: int
        :param country: A country code to filter the leaderboard.
        :type country: str
        :param display_mode: Defines the output format. Use 'list' to get a list
        of player objects, or 'default' for a formatted string.
        :type display_mode: str
        :return: A list of players or a formatted string, depending on the display_mode.
        :rtype: list | str
    """
    try:
        if not isinstance(offset, int): raise TypeError('"offset" value must be an integer')
        if not isinstance(limit, int): raise TypeError('"limit" value must be an integer')
        if not isinstance(country, str): raise TypeError('"country" value must be an string')
        if display_mode not in get_args(DisplayMode): raise ValueError('"display_mode" must be "default" or "list"')
        if limit > 50:
            limit = 50
            logger.warning('Player ranking: The "limit" parameter exceeds the maximum of 50 and has been capped at 50.')
        country = country.replace(' ', '-')

        url = f'{API_URL}/users/top'
        params = { "limit": limit, "offset": offset }
        if country != 'any': params |= { "country": country }

        data = _connector(url, params)
        logger.info('Player ranking: Receiving data successfully.')

        if display_mode == 'default':
            top = 'Player rankings:\n'
            for player in data:
                place = player['place']
                name = player['username']
                score = player['score']
                flag = getflag(player['country']) if player['country'] != 'Unknown' else ''

                top += f'{place}. {flag}{name} | Score: {score}\n'
            
            return top
        elif display_mode == 'list':
            top = []
            for player in data:
                new_player = {
                    "place": player['place'],
                    "name": player['username'],
                    "score": player['score'],
                    "flag": getflag(player['country']) if player['country'] != 'Unknown' else '' }
                top.append(new_player)

            return top
    except Exception as e:
        logger.error(f'Player ranking: {type(e).__name__}: {e}')

def level_list(offset = 0, limit = 0, list_type: ListType = 'classic', as_names = False, display_mode: DisplayMode = 'default'):
    """Retrieves a slice of the level leaderboard.

        :param offset: The starting offset for the leaderboard slice.
        :type offset: int
        :param limit: The maximum number of levels to retrieve.
        :type limit: int
        :param list_type: The type of leaderboard to query ('classic' or 'future').
        :type list_type: str
        :param as_names: If True, returns only the names of the levels.
        :type as_names: bool
        :param display_mode: Defines the output format. Use 'list' to get a list of levels objects, or 'default' for a formatted string. This parameter is ignored if 'as_names' is True.
        :type display_mode: str
        :return: A list of level data or a formatted string, depending on the 'display_mode' and 'as_names' flags.
        :rtype: list | str
    """
    try:
        if not isinstance(offset, int): raise TypeError('"offset" value must be an integer')
        if not isinstance(limit, int): raise TypeError('"limit" value must be an integer')
        if display_mode not in get_args(DisplayMode): raise ValueError('"display_mode" must be "default" or "list"')
        if not isinstance(list_type, str): raise TypeError('"list_type" value must be an string')
        if not isinstance(as_names, bool): raise TypeError('"as_names" value must be an boolean')

        params = { "limit": limit, "offset": offset }
        if list_type in get_args(ListType):
            url = f'{API_URL}/levels/{list_type}'
        else:
            raise ValueError('Unknown list type.\n Use "classic" or "future"')
        
        data = _connector(url, params)
        logger.info('Level list: Receiving data successfully.')

        if as_names:
            top = []
            for level in data: top.append(level['name'])
            return top
        elif list_type == 'classic':
            if display_mode == 'list':
                top = []
                for level in data:
                    new_level = {
                        "id": level['level_id'],
                        "name": level['name'],
                        "pos": level['place'],
                        "verifier": level['verifier'],
                        "video": level['video'],
                        "creator": level['creator'],
                        "list_percent": level['minimal_percent'],
                        "score": level['score']
                    }
                    top.append(new_level)
                
                return top
            elif display_mode == 'default':
                top = ''
                for level in data:
                    new_level = f"{level['place']}. {level['name']} verified by {level['verifier']}\n"
                    top += new_level
                
                return top
            else:
                raise ValueError('Unknown display_mode type. Use "default" or "list"')
        elif list_type == 'future':
            if display_mode == 'list':
                top = []
                for level in data:
                    new_lvl = {
                        "name": level['name'],
                        "verifier": level['verifier'],
                        "record": f'{level['record']}%',
                        "status": _status(level['status'])
                    }
                    top.append(new_lvl)
                
                return top
            elif display_mode == 'default' or display_mode == None:
                top = ''
                for level in data:
                    top += f'{level['name']} | Status: {_status(level['status'])}\n'
                
                return top
    except Exception as e:
        logger.error(f'Level list: {type(e).__name__}: {e}')

class Player:
    def __init__(self, user):
        if isinstance(user, int): self._data = self._get_by_id(user)
        elif isinstance(user, str):
            url = "https://api.demonlist.org/users/top"
            params = { "limit": 1, "offset": 0, "username_search": user }

            try:
                user_id = _connector(url, params)[0]['id']
                self._data = self._get_by_id(user_id)
            except requests.exceptions.RequestException as e:
                logger.error(f'API request failed: {e}')
                raise ConnectionError(f'Failed to connect to Demonlist API for user {user}') from e
            except IndexError:
                logger.error(f'Player "{user}" not found.')
                raise ValueError(f'Player not found: {user}')
        else:
            raise TypeError('"user" must be integer or string.')
        logger.info(f'Player ({user}): Receiving data successfully.')
        
        data = self._data
        self.id = data['id']
        self.place = data['place']
        self.score = data['score']
        self.username = data['username']
        self.country = data['country']
        self.flag = getflag(self.country) if self.country != 'Unknown' else ''
        self.badge = data['badge']
        self.hardest = [data['hardest']['level_name'],
                        data['hardest']['level_id'],
                        data['hardest']['place'],
                        data['hardest']['video']]

    def _get_by_id(self, user_id: int):
        url = "https://api.demonlist.org/users"
        params = { "id": user_id }

        try:
            data = _connector(url, params)
            return data
        except Exception as e:
            logger.error(f'Get By ID: {type(e).__name__}: {e}')
    
    def records(self, offset = 0, limit = 0, records_type: RecordsType = 'all', display_mode: DisplayMode = 'default'):
        """Retrieves a slice of the levels completions.

        :param offset: The starting offset for the records slice.
        :type offset: int
        :param limit: The maximum number of records to retrieve.
        :type limit: int
        :param records_type: The type of records to query ('all', 'main', 'basic', 'extended', 'beyond', 'verified' or 'progress').
        :type records_type: str
        :param display_mode: Defines the output format. Use 'list' to get a list of records, or 'default' for a formatted string. This parameter is ignored if 'as_names' is True.
        :type display_mode: str
        :return: A list of records data or a formatted string, depending on the 'display_mode' flag.
        :rtype: list | str
    """
        if not isinstance(offset, int): raise TypeError('"offset" value must be an integer')
        if not isinstance(limit, int): raise TypeError('"limit" value must be an integer')
        if records_type not in get_args(RecordsType): raise ValueError('"records_type" must be "all", "main", "basic", "extended", "beyond", "verified" or "progress"')
        if display_mode not in get_args(DisplayMode): raise ValueError('"display_mode" must be "default" or "list"')
        if limit == 0: limit = -1

        records = self._data['records']

        if records_type in ['main', 'basic', 'extended', 'beyond', 'verified', 'progress']:
            levels = records[records_type]
        elif records_type == 'all':
            levels = records['main'] + records['basic'] + records['extended'] + records['beyond']
        
        if display_mode == 'list':
            records_list = []
            for level in levels[offset:limit]:
                record = {
                    "name": level['level_name'],
                    "id": level['level_id'],
                    "place": level['place'],
                    "video": level['video']
                }
                if records_type == 'progress':
                    record['percent'] = level['percent']
                records_list.append(record)

            return records_list
        elif display_mode == 'default':
            records_list = ''
            for level in levels[offset:limit]:
                if records_type == 'progress':
                    records_list += f'{level['place']}. {level['level_name']} ({level['level_id']}) - {level['video']}'
            return records_list

class Country:
    def __init__(self, name: str):
        url = f'{API_URL}/countries/top/main'
        self._name = name.replace(' ', '-')
        try:
            self._data = _connector(url)
            self.flag = getflag(self._name) if self._name != 'Unknown' else ''

            for country in self._data:
                if country["country"] == self._name:
                    self.score = country['score']
                    self.place = country['place']
        except Exception as e:
            logger.error(f'Country: {type(e).__name__}: {e}')
    
    def players(self, offset = 0, limit = 0, display_mode: DisplayMode = 'default'):
        """Retrieves all country's players.

        :param offset: The starting offset for the players slice.
        :type offset: int
        :param limit: The maximum number of players to retrieve.
        :type limit: int
        :param display_mode: Defines the output format. Use 'list' to get a list of players, or 'default' for a formatted string.
        :type display_mode: str
        :return: A list of players data or a formatted string, depending on the 'display_mode' flag.
        :rtype: list | str
        """
        if not isinstance(offset, int): raise TypeError('"offset" value must be an integer')
        if not isinstance(limit, int): raise TypeError('"limit" value must be an integer')
        if display_mode not in get_args(DisplayMode): raise ValueError('"display_mode" must be "default" or "list"')
        if limit > 50:
            limit = 50
            logger.warning('Country: The "limit" parameter exceeds the maximum of 50 and has been capped at 50.')

        url = f'{API_URL}/countries/main'
        params = { "country": self._name }

        try:
            data = _connector(url, params)
            logger.info('Country: Receiving data successfully.')

            if display_mode == 'default':
                players = ''
                for i, player in enumerate(data):
                    if i+1 < offset: continue
                    players += f'{i+1}. {player['username']} - {player['score']}\n'
                    if i+1 == limit: break
                
                return players
            elif display_mode == 'list':
                return data
        except Exception as e:
            logger.error(f'Country players: {type(e).__name__}: {e}')

class Level:
    def __init__(self, name, list_type: ListType = 'classic'):
        self._list_type = list_type
        self.name = None
        self.level_id = None

        if isinstance(name, str):
            self.name = name
            url = f'{API_URL}/levels/{list_type}'
            params = { "search": name }
        elif isinstance(name, int):
            self.level_id = name
            url = f'{API_URL}/levels/{list_type}'
            params = { "level_id": name }
        else:
            raise ValueError('"name" must be integer or string')

        try:
            data = _connector(url, params)[0]
            logger.info(f'Level ({name}): Receiving data successfully.')

            self.video = data['video']
            self.verifier = data['verifier']

            if list_type == 'classic':
                self.level_id = data['level_id'] if not self.level_id else self.level_id
                self.name = data['name'] if not self.name else self.name
                self._id = data['id']
                self.place = data['place']
                self.song = data['song']
                self.creator = data['creator']
                self.holder = data['holder']
                self.list_percent = data['minimal_percent']
                self.score = data['score']
                self.length = data['length']
                self.history = data['history']
            else:
                self.status = _status(data['status'])
                self.record = data['record']
                self.category = data['category']
        
        except Exception as e:
            logger.error(f'Level: {type(e).__name__}: {e}')

    def level_history(self, display_mode: DisplayMode = 'default'):
        """Retrieves the complete history for a given level.

        :param display_mode: Defines the output format. Use 'list' to get a list of changes, or 'default' for a formatted string.
        :type display_mode: str
        :return: A list of changes data or a formatted string, depending on the 'display_mode' flag.
        :rtype: list | str
        """
        if self._list_type == 'future': raise StateError('The "history" method cannot be used with "future" type levels.')
        if display_mode not in get_args(DisplayMode): raise ValueError('"display_mode" must be "default" or "list"')

        try:
            if display_mode == 'default':
                changes = ''
                for element in self.history:
                    changes += f'Position: {element['place']}, type: {element['type']}, date: {element['date_created']}'
                return changes
            elif display_mode == 'list':
                changes = []
                for element in self.history:
                    new_change = {
                        "pos": element['place'],
                        "type": element['type'],
                        "details": element['args'],
                        "date": element['date_created']
                    }
                    changes.append(new_change)
                return changes
        except Exception as e:
            logger.error(f'Level history: {type(e).__name__}: {e}')
    
    def records(self, offset = 0, amount = False, order_by: OrderBy = 'newest', display_mode: DisplayMode = 'default'):
        """Retrieves the level's completions.

        :param offset: The starting offset for the players slice.
        :type offset: int
        :param amount: If True, returns the level's completions with total count, else only level's completions.
        :type amount: bool
        :param order_by: Specifies the sorting criteria for completions: 'place', 'newest', or 'oldest'.
        :type order_by: str
        :param display_mode: Defines the output format. Use 'list' to get a list of completions, or 'default' for a formatted string.
        :type display_mode: str
        :return: A list of completions or a formatted string, depending on the 'display_mode' flag.
        :rtype: list | str
        """
        if not isinstance(offset, int): raise TypeError('"offset" value must be an integer')
        if not isinstance(amount, bool): raise TypeError('"amount" value must be an boolean')
        if display_mode not in get_args(DisplayMode): raise ValueError('"display_mode" must be "default" or "list"')

        url = f'{API_URL}/records'
        params = { "level_id": self.id, f"order_by_{order_by}": "true", "status": 1, "without_verifiers": "true", "offset": offset }

        try:
            data = _connector(url, params)
            records_data = data['records']
            if amount: count = data['total_count']

            if display_mode == 'default':
                players = ''
                for compl in records_data:
                    players += f'{compl['username']} = {compl['percent']}% on {self.name}\n'
                if amount: players += f'\nTotal records: {count}'

                return players
            elif display_mode == 'list':
                players = []
                for compl in records_data:
                    new_compl = {
                        "player": compl['username'],
                        "flag": getflag(compl['country']) if compl['country'] != 'Unknown' else '',
                        "video": compl['video'],
                        "percent": compl['percent'],
                        "level_id": compl['level_id'],
                        "name": self._name
                    }
                    players.append(new_compl)

                if amount: return players, count
                else: return players
        except Exception as e:
            logger.error(f'Level records: {type(e).__name__}: {e}')
    
def _status(status: int):
    if status == 0: return 'Unknown'
    elif status == 1: return 'Not finished'
    elif status == 2: return 'Verifying'
    elif status == 3: return 'Open verification'
    elif status == 4: return 'Finished'
    else: return 'Unknown'