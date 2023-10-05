from otree.api import *

from utils.live_utils import live_page


class C(BaseConstants):
    NAME_IN_URL = "multiplayer_screener"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    SCREENER_TIMEOUT = 60

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gender = models.StringField(
        choices=[('M', 'Male'), ('F', "Female"), ("N", "Other")],
        widget=widgets.RadioSelectHorizontal,
    )
    nickname = models.StringField()

    timeouted = models.BooleanField(initial=False)


def creating_session(subsession: Subsession):
    pass


#### PAGES

class Screener(Page):
    form_model = "player"
    form_fields = ["gender", "nickname"]

    timeout_seconds = C.SCREENER_TIMEOUT

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.timeouted = timeout_happened


class Dropout(Page):
    """A page to display to players who left browser and reached game timeout"""
    @staticmethod
    def is_displayed(player: Player):
        return player.timeouted


page_sequence = [
    Screener,
    Dropout,
]