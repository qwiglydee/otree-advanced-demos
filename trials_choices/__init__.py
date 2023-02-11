""" Simple demo app

Trials are numeric expressions like "NN + NN".
An answer is selected from randomized choices..
Score is calculated as number of correct answers. 

Tials are pregenerated and embedded into page via js_vars.
Iteration runs on-page.
Answers are accumulated into hidden form field.
Correct answers are not revieled onto page in any way, no feedback given.
"""

import random
from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'trials_choices'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NUM_TRIALS = 5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    answers = models.StringField()  # semicolon-joined answers
    expected = models.StringField()  # semicolon-joined correct answers
    total_score = models.IntegerField()
    total_time = models.IntegerField()


class Trial(ExtraModel):
    player = models.Link(Player)
    question = models.StringField()
    solution = models.IntegerField()
    choices = models.StringField()  # |-joined answer options

    @classmethod
    def generate(cls, player: Player):
        """create single trial with random numbers and answer options"""
        number_a = random.randint(11, 99)
        number_b = random.randint(11, 99)
        result = number_a + number_b

        options = [result, result-10, result+10]
        random.shuffle(options)

        return Trial.create(
            player=player,
            question=f"{number_a} + {number_b}",
            solution=result,
            choices="|".join(map(str, options))
        )

    @classmethod
    def select(cls, player: Player, **kwargs):
        "select all trials for the player"
        return cls.filter(player=player, **kwargs)



def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        trials = generate_trials(player)
        player.expected = ";".join(str(t.solution) for t in trials)


def generate_trials(player: Player):
    """pregenerate all trials for the player"""
    return [Trial.generate(player) for i in range(C.NUM_TRIALS)]


def calc_results(player):
    """calculate player score"""
    given = map(int, player.answers.split(";"))
    correct = map(int, player.expected.split(";"))
    player.total_score = sum(a == b for a, b in zip(given, correct))  # compare pairs and summarie 'true' values


def format_trial(trial):
    """convert the trial into data for a page"""
    # only return question and choices
    return dict(
        question=trial.question,
        choices=list(map(int, trial.choices.split('|')))
    )

# PAGES


class Intro(Page):
    pass


class Main(Page):
    form_model = "player"
    form_fields = ["answers", "total_time"]

    @staticmethod
    def js_vars(player: Player):
        return dict(
            trials=[format_trial(t) for t in Trial.select(player)],
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        calc_results(player)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            total_trials=C.NUM_TRIALS,
            total_time=player.total_time / 1000,
        )


page_sequence = [Intro, Main, Results]
