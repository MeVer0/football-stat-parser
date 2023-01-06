class Standart_stat:
    def __init__(self, row):
        self.minutes_90 = float(row.contents[8].contents[0])
        self.games = int(row.contents[5].contents[0])
        self.games_start = int(row.contents[6].contents[0])
        self.minutes = int(row.contents[7].contents[0].replace(',', ''))
        self.goals = int(row.contents[9].contents[0])
        self.assist = int(row.contents[10].contents[0])
        self.np_goals = int(row.contents[11].contents[0])
        self.card_yellow = int(row.contents[14].contents[0])
        self.card_red = int(row.contents[15].contents[0])
        self.goals_assist_per90 = float(row.contents[18].contents[0])
        self.exp_goals = float(row.contents[21].contents[0])
        self.np_exp_goals = float(row.contents[22].contents[0])
        self.exp_assist = float(row.contents[23].contents[0])
        self.exp_goal_assist = float(row.contents[24].contents[0])


class Dribble:

    def __init__(self, row):
            self.dribbles = int(row.contents[14].contents[0])
            self.dribbles_com = int(row.contents[13].contents[0])
            self.dribbles_com_pct = float(row.contents[15].contents[0])


class Shooting:
    def __init__(self, row):
        self.shots = int(row.contents[7].contents[0])
        self.shots_pg = float(row.contents[10].contents[0])
        self.shots_on_target = int(row.contents[8].contents[0])
        self.shots_acc_perc = float(row.contents[9].contents[0])


class Passes:
    def __init__(self, row):
        self.passes_att = int(row.contents[7].contents[0])
        self.passes_comp = int(row.contents[6].contents[0])
        self.passes_pct = float(row.contents[8].contents[0])


class Defencive:
    def __init__(self, row):
        self.interceptions = int(row.contents[18].contents[0])
        self.blocked_shots = int(row.contents[16].contents[0])
        self.takles = int(row.contents[6].contents[0])


class GoalShotCreation:
    def __init__(self, row):
        self.shot_creating_actions = float(row.contents[6].contents[0])
        self.goal_creating_actions = float(row.contents[14].contents[0])


class AeralDuels:
    def __init__(self, row):
        self.aerial_won= float(row.contents[19].contents[0])
        self.aerial_won_perc = float(row.contents[21].contents[0])


class StandartStatGK:
    def __init__(self, row):
        self.game_started = row.contents[6].contents[0]
        self.minutes = row.contents[8].contents[0]
        self.yellow = row.contents[14].contents[0]
        self.red = row.contents[15].contents[0]
        self.goals = row.contents[9].contents[0]
        self.assists = row.contents[10].contents[0]


class GoalKeeping:
    def __init__(self, row):
        self.goals_against = row.contents[9].contents[0]
        self.goals_against_per_90 = row.contents[10].contents[0]
        self.shots_on_target_against = row.contents[9].contents[0]
        self.save_perc = row.contents[13].contents[0]
        self.clean_sheets = row.contents[17].contents[0]
        self.clean_sheets_perc = row.contents[18].contents[0]
        self.penalty_kicks_attempted = row.contents[19].contents[0]
        self.penalty_kicks_allowed = row.contents[20].contents[0]
        self.penalty_kicks_saved = row.contents[21].contents[0]
        self.penalty_save_perc = row.contents[23].contents[0]


