import random

from otree.api import *

from utils.live_utils import live_page, live_method


class C(BaseConstants):
    NAME_IN_URL = "trials_infinite"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    TRIAL_DELAY = 500
    MAX_FAILURES = 5
    SCORE_SUCCESS = +1
    SCORE_FAILURE = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    trials_completed = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)

    trials_failed = models.IntegerField(initial=0)
    terminated = models.BooleanField(initial=False)

    @property
    def current_iter(self):
        "current iteration is 1 forward of completed" ""
        return self.trials_completed + 1


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


def evaluate_trial(trial: Trial, response_data: dict):
    """evaluate trial success and score from response"""
    trial.response = response_data["response"]

    trial.success = trial.response == trial.solution
    if trial.success:
        trial.score = C.SCORE_SUCCESS
    else:
        trial.score = C.SCORE_FAILURE
    trial.completed = True


def calculate_payoff(player):
    """calculate final payoff"""
    player.payoff = player.total_score * player.session.config["real_world_currency_per_point"]


#### INIT ####


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        pass


def current_trial(player: Player):
    current = Trial.filter(player=player, iteration=player.current_iter)

    if len(current) == 0:
        return None

    [current] = current

    return current


#### FORMAT ####


def format_progress(player: Player):
    return {
        "completed": player.trials_completed,
        "failed": player.trials_failed,
        "score": player.total_score,
        "terminated": player.terminated,
    }


def format_trial(trial: Trial):
    return {"expression": trial.expression}


def format_feedback(trial: Trial):
    return {"success": trial.success, "score": trial.score}


#### PAGES ####


class Intro(Page):
    pass


@live_page
class Tasks(Page):
    @staticmethod
    def js_vars(player: Player):
        return {
            "trial_delay": C.TRIAL_DELAY,
        }

    @live_method("start")
    def handle_start(player: Player, data):
        "send current state of progress and a trial"
        current = current_trial(player)
        yield "reset", {
            "progress": format_progress(player),
            "trial": format_trial(current) if current else None,
        }

    @live_method("next")
    def handle_next(player: Player, data):
        "advancing iteration"

        if player.terminated:
            raise RuntimeError("The game is already over")

        if player.trials_failed == C.MAX_FAILURES:
            player.terminated = True
            yield "progress", format_progress(player)
            return

        current = current_trial(player)
        if current is not None and not current.completed:
            raise RuntimeError("Trying to step over uncompleted trial")

        trial = generate_trial(player, player.current_iter)

        yield "trial", format_trial(trial)

    @live_method("response")
    def handle_response(player: Player, data: dict):
        trial = current_trial(player)
        if trial is None:
            raise RuntimeError("No current trial")
        if trial.completed:
            raise RuntimeError("Trial already completed")

        trial.response_time = data["time"]
        evaluate_trial(trial, data)

        yield "feedback", format_feedback(trial)

        player.trials_completed += 1
        if not trial.success:
            player.trials_failed += 1
        player.total_score += trial.score

        yield "progress", format_progress(player)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
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
        "trials_completed",
        "total_score",
        #
        "iteration",
        "expression",
        "solution",
        "response_time",
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
