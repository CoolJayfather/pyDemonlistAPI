import sys

import countryflag
import requests
import logging
from countryflag import getflag
from urllib3.exceptions import HTTPError

api_url = 'https://api.demonlist.org'

logger = logging.getLogger('Demonlist API')
logger.setLevel(logging.ERROR)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(name)s - %(levelname)s\n%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# im too lazy to comment all of this go watch project-doc

def _connector(url, params=None):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise HTTPError(f'{url} gave the wrong answer: {response.status_code}. Check your internet-connection, or disable VPN/proxy')


def players_ranking(offset=0, display_mode=None):
    """
    RU: Возвращает топ игроков начиная от offset. Если offset не задан топ начинается с начала.
    Пример: offset = 300. Топ: 301-351 | offset - переменная и ни что иное
    display_mode позволяет настроить вывод топа игроков. list = лист-объект, default/None выводит позицию игрока его страну, ник и очки
    EN: Returns the top players starting from offset. If offset is not specified, the top starts from the beginning.
    Example: offset = 300. Top: 301-350 | offset must be an integer
    display_mode allows you to customize the display of the top players. list = list object, default/None displays the player's position, country, nickname and points
    """
    global api_url
    url = f"{api_url}/users/top"
    params = {
        "limit": 50,
        "offset": offset
    }
    try:
        data = _connector(url, params)
        top = ""
        if display_mode == None or display_mode == 'default':
            for player in data:
                place = player['place']
                name = player['username']
                score = player['score']
                flag = getflag(player['country']) if player['country'] != 'Unknown' else ''
                top += f'{place}. {flag}{name} | Score: {score}\n'
        elif display_mode == 'list':
            top = []
            for player in data:
                new_pl = {
                    "place": player['place'],
                    "name": player['username'],
                    "score": player['score'],
                    "flag": getflag(player['country']) if player['country'] != 'Unknown' else ''
                }
                top.append(new_pl)
        else:
            raise ValueError('Unknown display_mode type\n Use "default" or "list"')
        return top
    except HTTPError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)

def level_list(offset=0, display_mode=None, type='classic', as_names=False):
    """
    RU: Вернет топ демонов (/levels/classic) по нужному оффсету, например если оффсет 50 то будут уровни от 51 до 100
    EN: Returns demonlist (/levels/classic) by the required offset, for example, if the offset is 50, then there will be levels from 51 to 100
    """
    if not isinstance(offset, int):
        raise TypeError("'offset' value must be an integer")
    if not display_mode == None and not isinstance(display_mode, str):
        raise TypeError("'display_mode' must be a string")
    if as_names == True and not display_mode == None:
        raise TypeError("'display_mode' cannot have a value when as_names=True")

    global api_url
    url = None
    params = None
    if type == 'future':
        top = _get_futurelist(display_mode)
        return top
    elif type == 'classic':
        url = f"{api_url}/levels/classic"
        params = {
            "limit": 50,
            "offset": offset
        }
    else:
        raise ValueError('Unknown demonlist type.\n Use "classic" or "future"')
    try:
        data = _connector(url, params)
        top = None
        if as_names == True:
            top = []
            for level in data:
                top.append(level['name'])
            return top
        if display_mode == 'list':
            top = []
            for level in data:
                new_level = {
                    'id': level['level_id'],
                    'name': level['name'],
                    'pos': level['place'],
                    'verifier': level['verifier'],
                    'video': level['video'],
                    'creator': level['creator'],
                    'list_percent': level['minimal_percent'],
                    'score': level['score']
                }
                top.append(new_level)
        elif display_mode == 'default' or display_mode == None:
            top = ""
            for level in data:
                new_level = f"{level['place']}. {level['name']} verified by {level['verifier']}\n"
                top += new_level
        else:
            raise ValueError('Unknown display_mode type. Use "default" or "list"')
        return top
    except Exception as e:
        logger.error(e)


class Player:
    def __init__(self, user):
        url = None
        params = None
        if isinstance(user, int):
            self._data = self._get_by_id(user)
        elif isinstance(user, str):
            url = "https://api.demonlist.org/users/top"
            params = {
                "limit": 1,
                "offset": 0,
                "username_search": user
            }
            user = _connector(url, params)[0]['id']
            self._data = self._get_by_id(user)
        else:
            raise ValueError("You must enter an integer or string to Player class.")
        data = self._data
        self.id = data['id']
        self.place = data['place']
        self.score = data['score']
        self.username = data['username']
        self.country = data['country']
        self.flag = getflag(self.country)
        self.badge = data['badge']
        self.hardest = [data['hardest']['level_name'],
                        data['hardest']['level_id'],
                        data['hardest']['place'],
                        data['hardest']['video']]

    def _get_by_id(self, user):
        url = "https://api.demonlist.org/users"
        params = {
            "id": user
        }
        data = _connector(url, params)
        return data

    def records(self, levelType='all', limit=-1):
        records = self._data['records']
        if levelType in ['main', 'basic', 'extended', 'beyond', 'verified', 'progress']:
            levels = records[levelType]
        elif levelType == 'all':
            levels = records['main'] + records['basic'] + records['extended'] + records['beyond']
        else:
            raise ValueError(
                "Invalid 'levelType' value.\nUse 'main', 'basic', 'extended', 'beyond', 'verified', 'progress' or 'all' values")

        recordsList = []
        for level in levels[:limit]:
            record = {
                "name": level['level_name'],
                "id": level['level_id'],
                "place": level['place'],
                "video": level['video']
            }
            recordsList.append(record)
            if levelType == 'progress': recordsList[-1].insert(4, level['percent'])

        return recordsList

class Country:
    def __init__(self, name):
        global api_url
        url = f'{api_url}/countries/top/main'
        self._name = name.replace(' ', '-')
        self.flag = getflag(self._name)
        self._data = _connector(url)
        for country in self._data:
            if country["country"] == self._name:
                self.score = country['score']
                self.place = country['place']
    def players(self, offset=0, display_mode=None):
        if not isinstance(offset, int):
            raise TypeError("'offset' value must be an integer")
        if not isinstance(display_mode, str) and not display_mode == None:
            raise TypeError("'display_mode' value must be a string")
        global api_url
        url = f"{api_url}/countries/main"
        params = {
            "country": self._name
        }
        """
        RU: Возвращает всех игроков страны со счетом и позицией по топу страны
        EN: Returns all country's players with score and place in country's top
        """
        try:
            players = ""
            data = _connector(url, params)
            for index, player in enumerate(data):
                limit = offset + 50
                if index < offset:
                    continue
                elif index > limit:
                    break
                if display_mode == None or display_mode == 'default':
                    players += f'{index}. {player['username']} | Score: {player['score']}'
                elif display_mode == 'list':
                    return data
                else:
                    raise ValueError('"Unknown display_mode type"')

            return players

        except countryflag.InvalidCountryError:
            pass
        except HTTPError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)

class Level:
    def __init__(self, name):
        self._name = name
        global api_url
        url = f'{api_url}/levels/classic'
        levels = _connector(url)
        for level in levels:
            if level['name'] == self._name:
                self.place = level['place']
                self.id = level['level_id']
                self.video = level['video']
                self.verifier = level['verifier']
                self.creator = level['creator']
                self.list_percent = level['minimal_percent']
                self.score = level['score']

    def history(self, display_mode=None):
        global api_url
        url = f'{api_url}/levels/classic'
        params = {
            "place": self.place
        }
        data = _connector(url, params)[0]["history"]
        try:
            changes = None
            if display_mode == 'list':
                changes = []
                for element in data:
                    new_change = {
                        'pos': element['place'],
                        'type': element['type'],
                        'details': element['args'],
                        'date': element['date_created']
                    }
                    changes.append(new_change)
            elif display_mode == None or display_mode == 'default':
                changes = ""
                for element in data:
                    changes += f'Position: {element['place']}, type: {element['type']}, date: {element['date_created']}'
            return changes
        except Exception as e:
            logger.error(e)
    def records(self, amount=False, display_mode=None, offset=0):
        if not display_mode == None and not isinstance(display_mode, str):
            raise TypeError("'display_mode' must be a string")
        if not isinstance(offset, int):
            raise TypeError("'offset' must be an integer")
        if amount == True and not display_mode == None:
            raise TypeError("'display_mode' cannot have a value when amount=True")
        global api_url
        url = f'{api_url}/records'
        params = {
            "level_id": self.id,
            "status": 1,
            "without_verifiers": "true",
            "offset": offset
        }

        try:
            data = None
            if amount == False:
                data = _connector(url, params)["records"]
            else:
                data = _connector(url, params)
                count = data['total_count']
                return count
            victors = None
            if display_mode == 'default' or display_mode == None:
                victors = ""
                for cmpl in data:
                    victors += f'{cmpl['username']} {cmpl['percent']}% on {self._name}\n'
            elif display_mode == 'list':
                victors = []
                for cmpl in data:
                    new_cmpl = {
                        "player": cmpl['username'],
                        "flag": getflag(cmpl['country']),
                        "video": cmpl['video'],
                        "percent": cmpl['percent'],
                        "level_id": cmpl['level_id'],
                        "name": self._name
                    }
                    victors.append(new_cmpl)
            else:
                raise ValueError('Unknown display_mode type\n Use "default", "list" or "details"')
            return victors
        except Exception as e:
            logger.error(e)

def _get_futurelist(display_mode=None):
    global api_url
    url = f'{api_url}/levels/future'
    data = _connector(url)
    try:
        top = None
        statuses = {
            0: 'Unknown',
            1: 'In progress',
            2: 'Verifying',
            3: 'Open verification',
            4: 'Finished'
        }
        if display_mode == 'list':
            top = []
            for lvl in data:
                new_lvl = {
                    'name': lvl['name'],
                    'verifier': lvl['verifier'],
                    'record': f'{lvl['record']}%',
                    'status': statuses.get(lvl['status'])
                }
                top.append(new_lvl)
        elif display_mode == 'default' or display_mode == None:
            top = ""
            for lvl in data:
                top += f'{lvl['name']} | Status: {statuses.get(lvl['status'])}\n'
        else:
            raise ValueError('Unknown "display_mode" type. Try "default" or "list"')
        return top
    except Exception as e:
        logger.error(e)
