from otree.api import *


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
    pass


# PAGES
class Main(Page):
    pass


page_sequence = [Main]
