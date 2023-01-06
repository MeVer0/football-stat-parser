from database import cursor, Error


def get_procedure_without_params(procedure_name):
    """
    Для получение списка значений из запроса SQL-процедуры
    :param procedure_name: имя процедуры
    :return: список значений из запроса SQL-процедуры
    """
    try:
        # cursor = connection.cursor()
        cursor.callproc(procedure_name)
        for result in cursor.stored_results():
            return result.fetchall()

    except Error as e:
        print(e)


teams_id_ws = get_procedure_without_params('get_team_id_ws')

player_id_teamId_parse_source = get_procedure_without_params('get_player_id_teamId_parse_source')

players_id_teamId = get_procedure_without_params('get_players_id_teamId')
players_id_teamId_dict = dict(players_id_teamId)

country_id_name_code = get_procedure_without_params('get_country_id_name_code')

country_full_short_name = get_procedure_without_params('get_country_full_short_name')
country_full_short_name_dict = dict(country_full_short_name)

country_name_id = get_procedure_without_params('get_country_name_id')
country_name_id_dict = dict(country_name_id)

season_id_period_tourn = get_procedure_without_params('get_season_id_period_tourn')
season_id_period_tourn_dict = {value[1]: [(value[2], value[0]) for value in season_id_period_tourn] for value in
                               season_id_period_tourn}

tournament_id_name_dict = dict(get_procedure_without_params('get_tournament_id_name'))

player_name_countryCode = get_procedure_without_params('get_player_name_countryCode')
