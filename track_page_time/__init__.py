from time import time

from otree.api import *

from utils import pagetime


class C(BaseConstants):
    NAME_IN_URL = "track_page_time"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    fld = models.StringField()
    time_page1 = models.IntegerField()
    time_page2 = models.IntegerField()
    time_total = models.IntegerField()


def fld_error_message(player, value):
    if len(value) < 3:
        return 'need 3 or more chars'


@pagetime.track
class Page1(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.time_page1 = pagetime.last(player.participant)


@pagetime.track
class Page2(Page):
    form_model = 'player'
    form_fields = ['fld']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.time_page2 = pagetime.last(player.participant)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        player.time_total = pagetime.total(player.participant)
        return {}

page_sequence = [
    Page1,
    Page2,
    Results,
]
