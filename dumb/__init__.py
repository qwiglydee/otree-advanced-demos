import time
from otree.api import *

from utils.pagetime import tracktime

doc = """
Dumb app for testing
"""


class C(BaseConstants):
    NAME_IN_URL = 'dumb'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    foo = models.IntegerField(min=1)
    bar = models.IntegerField(min=1)


def foo_error_message(player, value):
    if value % 2:
        return "Enter even number"


def create_session(subsession: Subsession):
    pass


# PAGES


@tracktime
class Page1(Page):
    form_model = "player"
    form_fields = ['foo']

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool, time_spent: int):
        print("Page1 time", time_spent)


@tracktime
class Page2(Page):
    form_model = "player"
    form_fields = ['bar']

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool, time_spent: int):
        print("Page2 time", time_spent)


class Results(Page):
    pass


page_sequence = [
    Page1,
    Page2,
    Results
]


def custom_export(players):
    data = pagetimes.load_data()

    for r in data:
        print(repr(r))

    yield [
        "session",
        "participant"
    ]

    for player in players:
        yield [
            player.session.code,
            player.participant.code
        ]