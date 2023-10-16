import random

from otree.api import *

from utils.live_utils import live_page
from utils import image_utils

class C(BaseConstants):
    NAME_IN_URL = "drawing"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = 10  # total number of trials to generate
    MAX_FAILURES = 3  # num of failures to abort the game
    TASKS_TIMEOUT = 600  # total time limit for tasks (seconds)
    TRIAL_DELAY = 2000  # pause (ms) after trial
    RETRY_DELAY = 1000  # pause (ms) before retry
    SCORE_SUCCESS = +10
    SCORE_FAILURE = -10

    CANVAS_SIZE = (256, 256)
    CANVAS_FEATHER = 4


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    trials_completed = models.IntegerField(initial=0)
    trials_solved = models.IntegerField(initial=0)
    trials_failed = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)
    terminated = models.BooleanField(initial=False)


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)

    # task fields
    expression = models.StringField()
    solution = models.IntegerField()

    # response fields
    response_image = models.StringField()
    response_time = models.IntegerField()

    # status fields
    completed = models.BooleanField()
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


def generate_trials(player: Player):
    return [generate_trial(player, i) for i in range(1, 1 + C.NUM_TRIALS)]


def evaluate_response(trial: Trial, drawing: str):
    """evaluate response and update trial status and score, return feedback"""
    trial.response_image = drawing

    # analyzing painted area
    image = image_utils.decode(drawing)
    area = image.size[0] * image.size[1]
    side = (image.size[0] + image.size[1]) // 2

    hist = image.getchannel('A').histogram()
    drawn = area - hist[0]
    lines = drawn / C.CANVAS_FEATHER  # ~~ length of drawn lines

    if lines < side:  # too few
        return {
            'success': False,
            'completed': False,
        }

    trial.score = int((drawn / area) * 100) # percentage
    trial.success = True
    trial.completed = True

    return {
        "solution": trial.solution,
        "success": trial.success,
        "score": trial.score,
        "completed": trial.completed,
    }


def update_progress(player: Player, trial: Trial):
    """update players progress using last completed trial"""
    assert trial.completed

    player.trials_completed += 1
    player.total_score += trial.score
    player.total_score = max(0, player.total_score)

    player.terminated = player.trials_completed == C.NUM_TRIALS


def current_trial(player: Player):
    """retrieve current trial"""
    assert player.trials_completed < C.NUM_TRIALS
    [trial] = Trial.filter(player=player, iteration=player.trials_completed + 1)
    return trial


#### INIT ####


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player)


def init_player(player: Player):
    generate_trials(player)


def set_payoff(player: Player):
    """calculate final payoff"""
    player.payoff = player.total_score * player.session.config["real_world_currency_per_point"]


#### FORMAT ####


def output_progress(player: Player):
    return {
        "total": C.NUM_TRIALS,
        "completed": player.trials_completed,
        "score": player.total_score,
        "terminated": player.terminated,
    }


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "expression": trial.expression,
    }

#### PAGES ####


class Intro(Page):
    pass


@live_page
class Tasks(Page):
    """Live page with series of trials"""

    timeout_seconds = C.TASKS_TIMEOUT

    @staticmethod
    def js_vars(player: Player):
        return { 'C': dict(vars(C)) }

    @staticmethod
    def live_iter(player: Player, data):
        """retrieve current progress and trial"""

        yield "progress", output_progress(player)

        if not player.terminated:
            trial = current_trial(player)
            yield "trial", output_trial(trial)

    @staticmethod
    def live_response(player: Player, data: dict):
        """handle response from player"""

        assert not player.terminated

        trial = current_trial(player)

        assert data["iteration"] == trial.iteration

        trial.response_time = data["time"]

        feedback = evaluate_response(trial, data["drawing"])
        yield "feedback", feedback

        if trial.completed:
            update_progress(player, trial)
            yield "progress", output_progress(player)


    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.terminated = True
        set_payoff(player)


class Results(Page):
    pass


page_sequence = [
    Intro,
    Tasks,
    Results,
]


def custom_export(players: list[Player]):
    yield [
        "session.code",
        "participant.code",
        #
        "player.trials_completed",
        "player.trials_solved",
        "player.trials_failed",
        "player.total_score",
        #
        "trial.iteration",
        "trial.expression",
        "trial.solution",
        "trial.response_time",
        "trial.response_image",
        "trial.success",
        "trial.score",
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            #
            player.trials_completed,
            player.trials_solved,
            player.trials_failed,
            player.total_score,
        ]
        for trial in Trial.filter(player=player):
            yield player_fields + [
                trial.iteration,
                trial.expression,
                trial.solution,
                trial.response_time,
                trial.response_image,
                trial.success,
                trial.score,
            ]
