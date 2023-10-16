import random

from otree.api import *

from utils.live_utils import live_page


class C(BaseConstants):
    NAME_IN_URL = "trials_ondemand"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    MAX_TRIALS = 100    # max number of trials to run
    MAX_FAILURES = 5    # num of failures to abort the game
    TASKS_TIMEOUT = 60  # total time for tasks (s)
    TRIAL_DELAY = 1000  # pause (ms) after trial
    RETRY_DELAY = 1000  # pause (ms) before retry
    SCORE_SUCCESS = +10
    SCORE_FAILURE = -10


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
    response = models.StringField()
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


def evaluate_trial(trial: Trial):
    """evaluate trial status and score
    using already answered trial
    """
    assert trial.response is not None

    if trial.response == 0:
        # not accepting 0 and not completing
        trial.success = False
    else:
        trial.success = trial.response == trial.solution
        if trial.success:
            trial.score = C.SCORE_SUCCESS
        else:
            trial.score = C.SCORE_FAILURE
        trial.completed = True


def update_progress(player: Player, trial: Trial):
    """update players progress
    using last responded trial
    """
    assert trial.completed

    player.trials_completed += 1
    player.total_score += trial.score
    player.total_score = max(0, player.total_score)

    if trial.success:
        player.trials_solved += 1
    else:
        player.trials_failed += 1

    player.terminated = player.trials_completed >= C.MAX_TRIALS or player.trials_failed >= C.MAX_FAILURES


def current_trial(player: Player):
    """retrieve current trial"""
    assert player.trials_completed < C.MAX_TRIALS
    # it may fail if not yet generated
    trials = Trial.filter(player=player, iteration=player.trials_completed + 1)
    if len(trials) == 1:
        return trials[0]


def next_trial(player: Player):
    """generate next trial"""
    return generate_trial(player, player.trials_completed + 1)


#### INIT ####


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player)


def init_player(player: Player):
    pass


def set_payoff(player: Player):
    """calculate final payoff"""
    player.payoff = player.total_score * player.session.config["real_world_currency_per_point"]


#### FORMAT ####


def output_progress(player: Player):
    return {
        "completed": player.trials_completed,
        "score": player.total_score,
        "terminated": player.terminated,
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
        return { 'C': dict(vars(C)) }

    @staticmethod
    def live_iter(player: Player, data):
        """retrieve current progress and trial"""

        yield "progress", output_progress(player)

        if player.terminated:
            return

        trial = current_trial(player)
        if trial is None:
            trial = next_trial(player)

        yield "trial", output_trial(trial)

    @staticmethod
    def live_response(player: Player, data: dict):
        """handle response from player"""

        assert not player.terminated

        trial = current_trial(player)
        assert trial is not None and not trial.completed

        assert data["iteration"] == trial.iteration
        trial.response = data["response"]
        trial.response_time = data["time"]

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
        "trial.response",
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
                trial.response,
                trial.success,
                trial.score,
            ]
