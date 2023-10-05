from otree.api import *
from otree.database import NoResultFound

import multiplayer_screener as screener_app


class C(BaseConstants):
    NAME_IN_URL = "multiplayer_game"
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    GAME_TIMEOUT = 20
    WAIT_TIMEOUT = GAME_TIMEOUT + 10

    BONUS_FUND = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    completed = models.IntegerField(initial=0)  # number of players checked in on checkin page
    passed = models.BooleanField(initial=False)  # the party has already passed the checkin page


class Player(BasePlayer):
    gender = models.StringField()  # from screener
    nickname = models.StringField()  # from screener
    response = models.StringField()

    timeouted = models.BooleanField(initial=False)  # indicates that the player reached timeout on the game page
    completed = models.BooleanField(initial=False)  # indicates that the player has reached checkin page


def creating_session(subsession: Subsession):
    pass


def group_by_arrival_time_method(subsession, waiting_players):
    """grouping paerticipants by arrival (from screener app)"""
    if len(waiting_players) >= C.PLAYERS_PER_GROUP:
        grouped = waiting_players[: C.PLAYERS_PER_GROUP]
        for player in grouped:
            init_player(player)
        return grouped


def init_player(player: Player):
    """initializing player from corresponding player of screener app"""
    try:
        screener_player = screener_app.Player.objects_get(participant=player.participant)
        player.gender = screener_player.gender
        player.nickname = screener_player.nickname
    except NoResultFound:
        player.gender = "N"
        player.nickname = "Anonymous"


def checkin_player(player: Player, group: Group):
    """check in a player as completed the game"""
    player.completed = True
    player.group.completed += 1


def set_payoff(player: Player):
    """calculating payoff, for completed players only, when checkin page is passed"""
    assert player.completed
    assert player.group.passed

    player.payoff = C.BONUS_FUND / player.group.completed


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
        assert not player.group.passed, "A participant is way too late"
        player.timeouted = timeout_happened


class Dropout(Page):
    """A dead-end page for players who reached game timeout"""

    @staticmethod
    def is_displayed(player: Player):
        return player.timeouted


class CheckinPlayers(Page):
    """A page to wait for all players to complete the game page"""

    timeout_seconds = C.WAIT_TIMEOUT

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        checkin_player(player, group)
        if group.completed == group.player_set.count():
            return {0: "cancel"}
        else:
            return {0: None}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.group.passed = True
        set_payoff(player)


class Results(Page):
    pass


page_sequence = [
    GatherPlayers,
    Intro,
    Game,
    Dropout,
    CheckinPlayers,
    Results,
]
