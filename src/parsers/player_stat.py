import time

import requests
from bs4 import BeautifulSoup

from database import connection, cursor
from driver import driver
from functions import get_positions, get_tournamentId_by_name, get_id_season, get_full_table
from serializers import Standart_stat, Dribble, Shooting, Passes, Defencive, GoalShotCreation, AeralDuels, \
    StandartStatGK, GoalKeeping
from sql_variables import player_id_teamId_parse_source


def insert_player_stat(period: str):
    for player_id, player_team, player_whoscored, player_fbref in player_id_teamId_parse_source:
        driver.get(player_whoscored)
        html = driver.page_source
        time.sleep(1)
        soup = BeautifulSoup(html, 'lxml')
        positions_with_rating = soup.find('div', id="pp-statistics",
                                          class_="col12-lg-7 col12-m-8 col12-s-12 col12-xs-12").find('tbody').find_all('tr')

        rating = positions_with_rating[0].contents[9].contents[0]  # Получаем рейтинг игрока с хускорд
        positions = get_positions(positions_with_rating)

        if 'GK' not in positions.keys():
            player_fbref_id, player_name = player_fbref.split('/')[0], player_fbref.split('/')[1]  # Заходим на фрбреф за основной статистикой
            fbref_html = requests.get(f'https://fbref.com/en/players/{player_fbref_id}/all_comps/{player_name}-Stats---All-Competitions')
            soup = BeautifulSoup(fbref_html.text, 'lxml')

            standart_stat_not_full = soup.find("table", id="stats_standard_expanded").find('tbody').find_all('tr')  # Генерируем коллекции с информацией из которых будем брать информацию
            dribble_stat_not_full = soup.find('table', id="stats_possession_expanded").find('tbody').find_all('tr')
            shooting_stat_not_full = soup.find('table', id="stats_shooting_expanded").find('tbody').find_all('tr')
            passing_stat_not_full = soup.find('table', id="stats_passing_expanded").find('tbody').find_all('tr')
            defencive_stat_not_full = soup.find('table', id="stats_defense_expanded").find('tbody').find_all('tr')
            goal_shot_stat_not_full = soup.find('table', id="stats_gca_expanded").find('tbody').find_all('tr')
            aeral_duel_stat_not_full = soup.find('table', id="stats_misc_expanded").find('tbody').find_all('tr')

            diff1, diff2, diff3, diff4, diff5, diff6 = len(standart_stat_not_full) - len(dribble_stat_not_full), len(
                standart_stat_not_full) - len(shooting_stat_not_full), len(standart_stat_not_full) - len(
                passing_stat_not_full), len(standart_stat_not_full) - len(defencive_stat_not_full), len(
                standart_stat_not_full) - len(goal_shot_stat_not_full), len(standart_stat_not_full) - len(
                aeral_duel_stat_not_full)  # Узнаю разницу в длинне таблиц, чтобы не выпадать в IndexError.Длины списка разные, т.к разное кол-во турниров отмечено в таблицах со статистикой.

            try:
                for index in range((len(standart_stat_not_full) - 1), 0, -1):  # Цикл в котором мы создаем классы с информацией и делаем инсерт в БД
                    if standart_stat_not_full[index].contents[0].contents[0] != period:
                        break
                    try:
                        tournament_name = standart_stat_not_full[index].contents[4].contents[2].contents[0]  # Получаем название турнира.Используем try, т.к у разных турниров отличается местонахождение имени в таблице
                    except IndexError:
                        tournament_name = standart_stat_not_full[index].contents[0].contents[0]

                    tournament_id = get_tournamentId_by_name(tournament_name)
                    id_season = get_id_season(period, tournament_id)

                    if id_season is None:
                        continue

                    standart_stat_full = get_full_table(standart_stat_not_full, period)
                    dribble_stat_full = get_full_table(dribble_stat_not_full, period)
                    passes_stat_full = get_full_table(passing_stat_not_full, period)
                    defencive_stat_full = get_full_table(defencive_stat_not_full, period)
                    goal_shot_stat_full = get_full_table(goal_shot_stat_not_full, period)
                    aeral_duel_stat_full = get_full_table(aeral_duel_stat_not_full, period)
                    shooting_stat_full = get_full_table(shooting_stat_not_full, period)

                    standart_stat = Standart_stat(standart_stat_full[index])
                    dribble_stat = Dribble(dribble_stat_full[index - diff1])
                    shooting_stat = Shooting(shooting_stat_full[index - diff2])
                    passes_stat = Passes(passes_stat_full[index - diff3])
                    defencive_stat = Defencive(defencive_stat_full[index - diff4])
                    goal_shot_stat = GoalShotCreation(goal_shot_stat_full[index - diff5])
                    aeral_duel_stat = AeralDuels(aeral_duel_stat_full[index - diff6])

                    insert_player_stat = 'INSERT INTO `player_stat`(`id_player`, `id_season`, `id_team`, `_90s`, `rating`, `game_started`, `minutes`, `yellow_card`, ' \
                                         '`red_card`, `goals`, `assists`, `expected_goals`, `expected_assists`, `expected_non_penalty_goals`, `dribbles_pg_succ`, ' \
                                         '`dribbles_perc_succ`, `shots_pg`, `shots_in_target_pg`, `shots_acc_perc`, `passes_pg`, `passes_to_target_pg`, `passes_acc_perc`, ' \
                                         '`shot_creating_actions`, `goal_creating_actions`, `aerial_won_pg`, `aerial_won_perc`, `tackles_pg`, `interceptions_pg`, `blocked_shots_pg`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

                    '''Считаем значения с "пометкой за 90 минут"'''
                    dribbles_pg_succ = dribble_stat.dribbles / standart_stat.minutes_90 if dribble_stat.dribbles != 0 and standart_stat.minutes_90 != 0 else 0
                    passes_pg = passes_stat.passes_att / standart_stat.minutes_90 if passes_stat.passes_att != 0 and standart_stat.minutes_90 != 0 else 0
                    tackles_pg = defencive_stat.takles / standart_stat.minutes_90 if defencive_stat.takles != 0 and standart_stat.minutes_90 != 0 else 0
                    interceptions_pg = defencive_stat.interceptions / standart_stat.minutes_90 if defencive_stat.interceptions != 0 and standart_stat.minutes_90 != 0 else 0
                    blocked_shots_pg = defencive_stat.blocked_shots / standart_stat.minutes_90 if defencive_stat.blocked_shots != 0 and standart_stat.minutes_90 != 0 else 0
                    aerial_won_pg = aeral_duel_stat.aerial_won / standart_stat.minutes_90 if aeral_duel_stat.aerial_won != 0 and standart_stat.minutes_90 != 0 else 0

                    values = (
                        player_id, id_season, player_team, standart_stat.minutes_90, rating, standart_stat.games_start,
                        standart_stat.minutes, standart_stat.card_yellow, standart_stat.card_red, standart_stat.goals,
                        standart_stat.assist, standart_stat.exp_goals, standart_stat.exp_assist,
                        standart_stat.np_exp_goals, dribbles_pg_succ, dribble_stat.dribbles_com_pct,
                        shooting_stat.shots_pg, shooting_stat.shots_on_target, \
                        shooting_stat.shots_acc_perc, passes_pg, passes_stat.passes_comp,
                        passes_stat.passes_pct, goal_shot_stat.shot_creating_actions,
                        goal_shot_stat.goal_creating_actions, aerial_won_pg,
                        aeral_duel_stat.aerial_won_perc,
                        tackles_pg, interceptions_pg,
                        blocked_shots_pg)

                    cursor.execute(insert_player_stat, values)
                    connection.commit()
                    print(f'Игрок {player_name} добавлен в таблицу Player_stat')
                else:
                    player_fbref_id, player_name = player_fbref.split('/')[0], player_fbref.split('/')[1]
                    driver.get(
                        f'https://fbref.com/en/players/{player_fbref_id}/all_comps/{player_fbref_id}-Stats---All-Competitions')
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'lxml')

                    standart_st_gk = soup.find('div', id="switcher_stats_standard", class_="switcher_content").find('tbody').find_all('tr')
                    goalkeeping = soup.find('div', id="switcher_stats_keeper", class_="switcher_content").find('tbody').find_all('tr')

                    standart_stat_gk = get_full_table(standart_st_gk)
                    goalkeeping_stat = get_full_table(goalkeeping)

                    standart_gk = StandartStatGK(standart_stat_gk)
                    goalkeeping = GoalKeeping(goalkeeping_stat)
            except:
                continue
