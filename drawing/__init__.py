import random

from otree.api import *

from utils.live_utils import live_page
from utils import image_utils

class C(BaseConstants):
    NAME_IN_URL = "drawing"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = 10     # total number of trials to generate
    MAX_FAILURES = 5    # num of failures (not counting retries) to abort the game
    TASKS_TIMEOUT = 600  # total time limit for tasks (s)
    FEEDBACK_DELAY = 1000  # pause (ms) after feedback
    RETRY_DELAY = 1000  # pause (ms) after failed retry
    SCORE_SUCCESS = +1
    SCORE_FAILURE = 0

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

    @property
    def current_iter(self):
        "current iteration is always 1 forward of completed"
        return self.trials_completed + 1


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
    return [generate_trial(player, i) for i in range(1, 1+C.NUM_TRIALS)]


def current_trial(player: Player):
    """retrieve current trial"""
    trials = Trial.filter(player=player, iteration=player.current_iter)
    if len(trials) == 1:
        return trials[0]


def evaluate_trial(trial: Trial):
    """evaluate trial status and score
    using already answered trial
    """
    assert trial.response_image is not None

    # analyzing painted area
    image = image_utils.decode(trial.response_image)
    area = image.size[0] * image.size[1]
    side = (image.size[0] + image.size[1]) // 2

    hist = image.getchannel('A').histogram()
    drawn = area - hist[0]
    lines = drawn / C.CANVAS_FEATHER  # ~~ length of drawn lines

    if lines < side:  # too few
        trial.success = False
        trial.completed = False
    else:
        trial.success = True
        trial.score = int((drawn / area) * 100) # percentage
        trial.completed = True


def update_progress(player: Player, trial: Trial):
    """update players progress
    using last responded trial
    """
    assert trial.completed

    player.trials_completed += 1
    player.total_score += trial.score
    player.total_score = max(0, player.total_score)

    player.terminated = player.trials_completed == C.NUM_TRIALS


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
        "completed": player.trials_completed,
        "score": player.total_score,
    }


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "expression": trial.expression,
    }


def output_feedback(trial: Trial):
    return {
        "solution": trial.solution,
        "success": trial.success,
        "score": trial.score,
        "completed": trial.completed,
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
        return {
            "feedback_delay": C.FEEDBACK_DELAY,
            "retry_delay": C.RETRY_DELAY,
        }

    @staticmethod
    def live_next(player: Player, data):
        "send next (or current) trial"

        if player.terminated:
            yield "terminate"
            return

        yield "progress", output_progress(player)

        trial = current_trial(player)
        assert trial is not None
        yield "trial", output_trial(trial)

    @staticmethod
    def live_response(player: Player, data: dict):
        "handle response from player"

        assert not player.terminated
        assert data['iteration'] == player.current_iter

        trial = current_trial(player)
        assert trial is not None

        trial.response_time = data["time"]
        trial.response_image = data['image']

        evaluate_trial(trial)
        yield "feedback", output_feedback(trial)

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
