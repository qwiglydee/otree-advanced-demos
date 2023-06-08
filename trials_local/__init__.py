import json
import random

from otree.api import *

from utils.live_utils import live_page, live_method
from utils import pagetime


class C(BaseConstants):
    NAME_IN_URL = "trials_local"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = 5
    TRIAL_DELAY = 500
    SCORE_SUCCESS = +1
    SCORE_FAILURE = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    responses_json = models.LongStringField()
    trials_completed = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)
    total_time = models.IntegerField()

    @property
    def current_iter(self):
        return self.trials_completed + 1


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)

    # task fields
    expression = models.StringField()
    solution = models.IntegerField()

    # response fields
    response = models.StringField()

    # status fields
    success = models.BooleanField()
    score = models.IntegerField(initial=0)


def generate_trial(player: Player, iteration: int):
    """generate single trial of the task"""
    a = random.randint(11, 99)
    b = random.randint(11, 99)
    expr = f"{a} + {b}"
    solution = a + b

    return Trial.create(
        player=player,
        iteration=iteration,
        expression=expr,
        solution=solution,
    )


def generate_trials(player):
    """generate all trials for a player"""
    return [generate_trial(player, i + 1) for i in range(C.NUM_TRIALS)]


def evaluate_trial(trial: Trial, response: dict):
    """evaluate trial success and score from response"""
    trial.response = response

    trial.success = trial.response == trial.solution

    if trial.success:
        trial.score = C.SCORE_SUCCESS
    else:
        trial.score = C.SCORE_FAILURE


def evaluate_trials(player: Player):
    """evaluate all trials for player from its responses"""
    trials = Trial.filter(player=player)

    responses = json.loads(player.responses_json)
    player.trials_completed = len(responses)
    if player.trials_completed != len(trials):
        raise RuntimeError("Invalid number of responses")

    for trial, answer in zip(trials, responses):
        evaluate_trial(trial, answer)

    player.total_score = sum(t.score for t in trials)


def calculate_payoff(player):
    """calculate final payoff"""
    player.payoff = player.total_score * player.session.config["real_world_currency_per_point"]


#### INIT ####


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        trials = generate_trials(player)
        if len(trials) != C.NUM_TRIALS:
            raise RuntimeError("Failed to generate trials", player)


#### FORMAT ####


def format_trial(trial: Trial):
    return {
        "expression": trial.expression,
    }


def format_trials(trials):
    return {t.iteration: format_trial(t) for t in trials}


#### PAGES ####


class Intro(Page):
    pass


@pagetime.track
class Tasks(Page):
    form_model = "player"
    form_fields = ["responses_json"]

    @staticmethod
    def js_vars(player: Player):
        trials = Trial.filter(player=player)
        return {
            "trial_delay": C.TRIAL_DELAY,
            "trials": format_trials(trials),
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.total_time = pagetime.last(player.participant)
        evaluate_trials(player)
        calculate_payoff(player)


class Results(Page):
    pass


page_sequence = [
    Intro,
    Tasks,
    Results,
]


def custom_export(players: list[Player]):
    yield [
        "session",
        "participant",
        "completed_trials",
        "total_score",
        "total_time",
        #
        "iteration",
        "expression",
        "solution",
        "response",
        "success",
        "score",
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            player.trials_completed,
            player.total_score,
            player.total_time,
        ]
        for trial in Trial.filter(player=player):
            yield player_fields + [
                trial.iteration,
                trial.expression,
                trial.solution,
                trial.response,
                trial.success,
                trial.score,
            ]
