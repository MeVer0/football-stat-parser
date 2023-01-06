from parsers import player_and_player_ps, player_stat


def main():
    player_and_player_ps.insert_player_and_pps()
    player_stat.insert_player_stat('2022-2023')


if __name__ == '__main__':
    main()
