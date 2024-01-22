from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'ultimatum_screener'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gender = models.StringField(choices=[('M', "Male"), ('F', "Female"), ('O', "Other")])
    age = models.IntegerField(min=18, max=100)


# PAGES

class Welcome(Page):
    form_model = "player"
    form_fields = ['gender', 'age']


page_sequence = [Welcome]
