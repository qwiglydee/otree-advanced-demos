import random

from otree.api import *

from utils.live_utils import live_page, live_method


class C(BaseConstants):
    NAME_IN_URL = "trials_live"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = 10
    TRIAL_DELAY = 500
    SCORE_SUCCESS = +1
    SCORE_FAILURE = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    trials_completed = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)

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


def generate_trials(player):
    """generate all trials for a player"""
    return [generate_trial(player, i + 1) for i in range(C.NUM_TRIALS)]


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
        trials = generate_trials(player)
        if len(trials) != C.NUM_TRIALS:
            raise RuntimeError("Failed to generate trials", player)


#### FORMAT ####


def format_progress(player: Player):
    return {"total": C.NUM_TRIALS, "completed": player.trials_completed, "score": player.total_score}


def format_trial(trial: Trial):
    return {"expression": trial.expression}


def format_trials(trials):
    return {t.iteration: format_trial(t) for t in trials}


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
            "trials": format_trials(Trial.filter(player=player)),
        }

    @live_method("start")
    def handle_start(player: Player, data: dict):
        yield "reset", {"progress": format_progress(player)}

    @live_method("response")
    def handle_response(player: Player, data: dict):
        if data["iteration"] != player.current_iter:
            raise RuntimeError("Iteration mismatch", player.current_iter, data["iteration"])

        [trial] = Trial.filter(player=player, iteration=player.current_iter)

        if trial.completed:
            raise RuntimeError("Trial already responded")

        trial.response_time = data["time"]
        evaluate_trial(trial, data)

        yield "feedback", format_feedback(trial)

        player.trials_completed += 1
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
