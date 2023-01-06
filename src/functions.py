import requests
from bs4 import BeautifulSoup

from sql_variables import tournament_id_name_dict, season_id_period_tourn_dict, country_full_short_name_dict

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }


def get_tournamentId_by_name(tournament_name):
    """
    Заменяет название трунира на его id
    :param tournament_name:название турнира
    :return: id турнира
    """
    if tournament_id_name_dict.get(tournament_name):
        return tournament_id_name_dict.get(tournament_name)
    return


def get_id_season(period, tournament_id):
    """
    Возвращает id сезона по году и названию турнира, либо не находит и возвращает None
    :param period: год
    :param tournament_id: id турнира
    :return: id сезона или None
    """
    if season_id_period_tourn_dict.get(period):
        for tourn_id, season_id in season_id_period_tourn_dict.get(period):
            if tourn_id == tournament_id:
                return season_id
        return


def get_search_list_fbref():
    """Функция для получения и сохранения файла с игроками, по которому осуществляется поиск на фбреф"""
    url = 'https://fbref.com/short/inc/players_search_list.csv'
    res = requests.get(url=url)
    with open('player_search_list', 'w', encoding="utf-8") as psl:
        psl.write(res.text)

    with open('player_search_list', 'r', encoding="utf-8") as psl:
        psl = psl.read()


    psl = psl.split('\n')
    search_list = [inf_str.split(',') for inf_str in psl if inf_str != '']  # Вложенный список из строк с информацией :[['d70ce98e', 'Lionel Messi..], ]
    return search_list


def get_player_link_fb(name, country, search_dict):
    """
    Проверки наличия игрока на ФБрефе по имени и стране рождения, создает список с подходящими игроками
    :param name: имя
    :param country: страна
    :param search_dict: словарь с игроками
    :return: список подходящих по имени и национальности игроков из поиска по fbref
    """
    links = []
    name = name.lower()
    player_country = country_full_short_name_dict.get(country)
    if name in search_dict:
        if search_dict.get(name)[1] == player_country:
                link = f'{search_dict.get(name)[0]}/{"-".join(name.split())}'
                links.append(link)
    return links


def get_player_link_tm(name, country, search_depth=6):
    """
    Функция возвращающая список ссылок игроков на ТМ,подходящих по имени и стране
    :param name: имя
    :param country: страна
    :param search_depth: номер строки до которой мы доходим при поиске на transfermarkt
    :return: список подходящих по имени и национальности игроков из поиска по fbref
    """
    result = []  # Результирующий список с сылками на игроков ТМ
    name = '+'.join(name.split())

    url_search = f'https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={name}'
    re = requests.get(url_search, headers=headers)
    soup = BeautifulSoup(re.text, 'lxml')
    links = soup.find_all('td', class_="hauptlink")  # Получаем всех игроков с первой страницы поиска

    if len(links) > 0:  # проверяем есть ли такой игрок на ТМ вообще
        for url in links:
            if len(result) < search_depth:
                try:
                    link = url.contents[0].attrs['href']
                    url_player = f'https://www.transfermarkt.com{link}'
                    res = requests.get(url_player, headers=headers)
                    soup_player = BeautifulSoup(res.text, 'lxml')
                    citizenship = soup_player.find('span', itemprop="nationality", class_="data-header__content").contents[1].next_element.strip()
                    if citizenship == country:
                        result.append(link)
                except:
                    continue
            else:
                return result
        return result


def get_correct_search_list(search_list):
    """Заменяет закодированные буквы в именах игроков из передаваемого списка на нормальные"""
    symbols_dict = {'Ä': 'c', 'Ã©': 'e', 'Ã¼': 'ü', 'Ã': 'a', 'Ä°': 'I', 'Ä': 'g', 'Ã«': 'ë', 'Å¡': 's', 'Å¾': 'z',
                    'Ã´': 'o', 'Ã³': 'o', r'Ä\x8d': 'c', 'Ãº': 'u', 'Ã¡': 'a', r'Ã\xad': 'i', 'Ã¨': 'e', r'Ã\x89': 'e',
                    r'Ã\xa0': 'a', 'Ã¤': 'Ö'}

    for row in search_list:
        for s in symbols_dict:
            if row[1].find(s) != -1:
                row[1] = row[1].replace(s, symbols_dict[s])

    return search_list


def get_positions(positions_list):
    """
    Функция для получения словаря с позициями игрока c сайта хускорд
    :param positions_list: список позиций игрока, который мы получаем с whoscored
    :return: словарь с позициями игрока
    """
    positions = {}
    for row in positions_list:
        positions[row.contents[1].contents[0].strip()] = 1
    return positions


def get_full_table(table, period):
    """
    Функция для заполнения пустых полей в таблицах со статистикой
    :param table: таблица с определенным типом статистики с fbref
    :param period: год в формате "2022-2023"
    :return: таблицу со статистикой с полностью заполненными полями
    """
    for i in range(len(table) - 1, 0, -1):
        if table[i].contents[0].contents[0] not in [period]:
            break
        else:
            for row in table[i]:
                if len(row.contents) == 0:
                    row.contents.append(None)
    return table

#
# def correct_price(value):
#     if value[-1] == 'm':
#         a = float(value[1:-1]) * 1000000
#         return int(a)
#     elif value[-3:] == 'Th.':
#         a = float(value[1:-3]) * 1000
#         return int(a)
#
#
# def currency_name(value):
#     if value == '€':
#         return 'EUR'


def get_index_of_word(soup_obj, string):
    """Функция для поиска слова в обьекте класса BeautifullSoup"""
    counter = 0
    for i in soup_obj:
        if string not in i.contents[0]:
            counter += 1
        else:
            return counter
