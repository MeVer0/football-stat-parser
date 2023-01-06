from datetime import datetime
import time
import json
from bs4 import BeautifulSoup

from driver import driver
from database import cursor, connection
from functions import get_index_of_word, get_player_link_fb, get_player_link_tm, get_correct_search_list, \
    get_search_list_fbref
from sql_variables import teams_id_ws, country_name_id_dict, players_id_teamId_dict, player_id_teamId_parse_source

search_list_fbref = get_correct_search_list(get_search_list_fbref())  # получаем список игроков с фбреф
search_dict_fbref = {name: [player_id, country] for name, player_id, country
                     in [[row[1].lower(), row[0], row[4]] for row
                         in search_list_fbref]}


def insert_player_and_pps():
    for team_id, team_whoscored_id in teams_id_ws:
        ws_url = f'https://www.whoscored.com/StatisticsFeed/1/GetPlayerStatistics?category=summary&subcategory=' \
                 f'all&statsAccumulationType=0&isCurrent=true&playerId=&teamIds={team_whoscored_id}&matchId=&stageId=&tournament' \
                 f'Options=2&sortBy=Rating&sortAscending=&age=&ageComparisonType=&appearances=&appearancesComparisonType=' \
                 f'&field=Overall&nationality=&positionOptions=&timeOfTheGameEnd=&timeOfTheGameStart=&isMinApp=false&page=' \
                 f'&includeZeroValues=true&numberOfPlayersToPick='

        driver.get(ws_url)
        team_page_html = driver.page_source[25: -15]
        whoscored_player_table_stats = json.loads(team_page_html)

        for player in whoscored_player_table_stats['playerTableStats']:
            player_id = player['playerId']
            name = player['name']
            weight = player['weight']
            height = player['height']

            player_ws_url = f"https://www.whoscored.com/Players/{player_id}/Show/{name.replace(' ', '')}"
            time.sleep(1)
            driver.get(player_ws_url)
            pl_html = driver.page_source
            soup = BeautifulSoup(pl_html, 'lxml')
            pl_html_soup = soup.findAll('span', class_="info-label")

            age_index = get_index_of_word(pl_html_soup, 'Age')
            birth = pl_html_soup[age_index].parent.contents[3].contents[0].split('-')
            string_birth = str(f'{birth[-1]}-{birth[1]}-{birth[0]}')
            date_formater = "%Y-%m-%d"
            birth = datetime.strptime(string_birth, date_formater).date()

            if get_index_of_word(pl_html_soup, 'Shirt') is not None:
                shirt_index = get_index_of_word(pl_html_soup, 'Shirt')
                shirt_number = pl_html_soup[shirt_index].parent.contents[2].strip()
            else:
                shirt_number = None
                player_withouth_shirt = f'У игрока{name}/{player_ws_url} нет номера футболки' + '\n'
                with open('players_without_shirt', 'a', encoding='utf-8') as players_without_shirt:
                    players_without_shirt.write(player_withouth_shirt)

            if get_index_of_word(pl_html_soup, 'Nationality') is not None:
                nationality_index = get_index_of_word(pl_html_soup, 'Nationality')
                nationality = pl_html_soup[nationality_index].parent.contents[3].contents[0].strip()
            else:
                players_without_nationality = f'У игрока {name}/{player_ws_url} не указана национальность' + '\n'
                with open('players_without_nationality', 'a', encoding='utf-8') as players_without_nationality:
                    players_without_nationality.write(str(players_without_nationality))

            if country_name_id_dict.get(nationality):
                nationality_id = country_name_id_dict.get(nationality)
            else:
                links_fbref = f'У игрока с именем: {name} нет страны в бд' + '\n'
                with open('players_without_nationality_id', 'a', encoding='utf-8') as players_without_nationality_id:
                    players_without_nationality_id.writelines(links_fbref)

            if not players_id_teamId_dict.get(player_id):
                inserting_player = 'INSERT INTO player(id_player, id_team, name, id_country, img, shirt_number, weight, height, birth)' \
                                   ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                val = (player_id, int(team_id), name, nationality_id, name, shirt_number, weight, height, birth)
                cursor.execute(inserting_player, val)
                connection.commit()
                print(f'Игрок {name} добавлен в таблицу player')
            elif players_id_teamId_dict.get(player_id) != team_id:
                update_team_id = 'UPDATE player SET id_team = %s, shirt_number=%s'
                val = (team_id, shirt_number)
                cursor.execute(update_team_id, val)
                connection.commit()

            list_links_fbref = get_player_link_fb(name, nationality, search_dict_fbref)  # Получаем список ссылок на фбреф
            list_links_tm = get_player_link_tm(name, nationality)  # Получаем список ссылок на трансфермаркет

            try:
                if len(list_links_fbref) > 1:
                    print(
                        f'Игроков с именем: {name} несколько, нужно будет добавить правильного самому из списка list_links_fbref')
                    exception = f'Игроков с именем: {name} несколько,добавьте нужного из списка {list_links_fbref}' + '\n'
                    with open('same_players_fb', 'a', encoding='utf-8') as same_players_fb:
                        same_players_fb.writelines(exception)

                elif len(list_links_tm) > 1:
                    print(
                        f'Игроков с именем: {name} несколько, нужно будет добавить правильного самому из списка list_links_tm')
                    exception = f'Игроков с именем: {name} несколько,добавьте нужного из списка {list_links_tm}' + '\n'
                    with open('same_players_tm', 'a', encoding='utf-8') as same_players_tm:
                        same_players_tm.writelines(exception)

                elif len(list_links_tm) < 1 or len(list_links_fbref) < 1:
                    not_found_player = f'{name} не найден, {str(list_links_tm)} - ссылка TM , {str(list_links_fbref)} - ссылка на ФБ' + '\n'
                    print(not_found_player.strip())
                    with open('players_not_found', 'a', encoding='utf-8') as players_not_found:
                        players_not_found.writelines(not_found_player)

                elif len(list_links_tm) == 1 and len(
                        list_links_fbref) == 1 and player_id not in player_id_teamId_parse_source:
                    insert_player_pars_sourse = 'INSERT INTO player_parse_source(id_player, whoscored, fbref, transfermarkt) VALUES (%s, %s, %s, %s)'
                    val = (player_id, player_ws_url, list_links_fbref[0], list_links_tm[0])
                    cursor.execute(insert_player_pars_sourse, val)
                    connection.commit()
                    print(f"{name}/{player_ws_url} добавлен в таблицу player_pars_sours 😃😻!")
            except:
                continue