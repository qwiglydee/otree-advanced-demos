from otree.api import *

class C(BaseConstants):
    NAME_IN_URL = 'forms'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = 5
    TRIAL_DELAY = 500;


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    responses = models.StringField()


# PAGES
class Main(Page):
    form_model = "player"
    form_fields = ["responses"]

    @staticmethod
    def js_vars(player: Player):
        return {"C": dict(vars(C))}

class Results(Page):
    pass


page_sequence = [Main, Results]
