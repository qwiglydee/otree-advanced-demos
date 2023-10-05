from otree.api import *

from utils.live_utils import live_page

import multiplayer_screener as screener_app


class C(BaseConstants):
    NAME_IN_URL = "multiplayer_game"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    GAME_TIMEOUT = 10
    WAIT_TIMEOUT = 20

    BONUS_FUND = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    has_dropout = models.BooleanField() # indicates some players had dropped out (and others left)


class Player(BasePlayer):
    gender = models.StringField() # from screener
    nickname = models.StringField() # from screener
    response = models.StringField()
    timeouted = models.BooleanField(initial=False) # indicates that timeout happened on the game page
    completed = models.BooleanField(initial=False) # indicates that player has reached next waiting page


def creating_session(subsession: Subsession):
    pass


def group_by_arrival_time_method(subsession, waiting_players):
    """grouping paerticipants by arrival (from screener app)"""
    if len(waiting_players) >= C.PLAYERS_PER_GROUP:
        grouped = waiting_players[:C.PLAYERS_PER_GROUP]
        for player in grouped:
            init_player(player)
        return grouped


def init_player(player: Player):
    """initializing player from corresponding player of screener app"""
    screener_player = screener_app.Player.objects_get(participant=player.participant)
    player.gender = screener_player.gender
    player.nickname = screener_player.nickname


def count_total_players(group: Group):
    return group.player_set.count()


def count_completed_players(group: Group):
    return group.player_set.filter_by(completed=True).count()


def set_payoff(player: Player):
    """calculating payoff, for completed players only"""
    assert player.completed
    player.payoff = C.BONUS_FUND / count_completed_players(player.group)


#### PAGES

class GatherPlayers(WaitPage):
    group_by_arrival_time = True
    group_by_arrival_time_method = group_by_arrival_time


class Intro(Page):
    pass

class Game(Page):
    form_model = "player"
    form_fields = ["response"]
    timeout_seconds = C.GAME_TIMEOUT

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.group.has_dropout = True
            player.timeouted = True


class Dropout(Page):
    """A page to display to players who left browser and reached game timeout"""
    @staticmethod
    def is_displayed(player: Player):
        return player.timeouted


@live_page
class WaitPlayers(Page):
    """A page to collect players who haven't left or timeouted"""
    timeout_seconds = C.WAIT_TIMEOUT

    @staticmethod
    def is_displayed(player: Player):
        return not player.timeouted

    @staticmethod
    def live_join(player: Player, data):
        player.completed = True

        total = count_total_players(player.group)
        completed = count_completed_players(player.group)

        if completed == total:
            yield "all", "complete"
        else:
            yield "wait"

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.group.has_dropout = True
        set_payoff(player)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'completed': count_completed_players(player.group)
        }


page_sequence = [
    GatherPlayers,
    Intro,
    Game,
    Dropout,
    WaitPlayers,
    Results,
]