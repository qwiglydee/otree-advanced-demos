import random

from otree.api import *

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "timers"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ["ODD", "EVEN", "MIXED"]

    MAX_FAILURES = 5  # num of failures to abort the game

    PAGE_TIMEOUT = 30  # (seconds) total time limit for tasks page
    RESPONSE_TIMEOUT = 5  # (seconds) time limit for single trial
    FEEDBACK_DELAY = 2000  # (ms) time to show feedback before next trial

    SCORE_SUCCESS = +10
    SCORE_FAILURE = -1
    SCORE_TIMEOUT = 0


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    trials_completed = models.IntegerField(initial=0)
    trials_failed = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)
    terminated = models.BooleanField(initial=False)


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)
    # status fields
    status = models.StringField(choices=["NEW", "LOADED", "TIMEOUTED", "COMPLETED"], initial="NEW")
    success = models.BooleanField(initial=None)
    score = models.IntegerField(initial=0)
    # task fields
    expression = models.StringField()
    solution = models.IntegerField()
    # response fields
    response_time = models.IntegerField()
    answer = models.IntegerField()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player, subsession.session.config)


def init_player(player: Player, config: dict):
    player.condition = random.choice(C.CONDITIONS)
    if "condition" in config and config["condition"] != "random":
        assert config["condition"] in C.CONDITIONS
        player.condition = config["condition"]


def generate_trial(player: Player, iteration: int):
    if player.condition == "MIXED":
        a = random.randint(10, 99)
        b = random.randint(10, 99)
    elif player.condition == "ODD":
        a = random.randint(5, 49) * 2 + 1
        b = random.randint(5, 49) * 2 + 1
    elif player.condition == "EVEN":
        a = random.randint(5, 49) * 2
        b = random.randint(5, 49) * 2

    expr = f"{a} + {b}"
    solution = a + b

    return Trial.create(
        player=player,
        iteration=iteration,
        expression=expr,
        solution=solution,
    )


def current_trial(player: Player):
    trials = Trial.filter(player=player, iteration=player.trials_completed + 1)
    return trials[0] if trials else None


def next_trial(player: Player):
    return generate_trial(player, player.trials_completed + 1)


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "expression": trial.expression,
    }


def evaluate_response(trial: Trial, response: dict):
    assert response["iteration"] == trial.iteration
    assert isinstance(response["answer"], int)

    answer = response["answer"]

    trial.answer = answer
    trial.success = trial.answer == trial.solution
    trial.score = C.SCORE_SUCCESS if trial.success else C.SCORE_FAILURE

    trial.status = "COMPLETED"

    return {
        "completed": True,
        "success": trial.success,
        "score": trial.score,
    }


def evaluate_timeout(trial: Trial, response: dict):
    assert response["iteration"] == trial.iteration

    trial.success = False
    trial.score = C.SCORE_TIMEOUT

    trial.status = "TIMEOUTED"

    return {
        "completed": True,
        "success": trial.success,
        "score": trial.score,
        "timeouted": True,
    }


def update_progress(player: Player, trial: Trial, feedback: dict):
    assert trial.status in ("COMPLETED", "TIMEOUTED")

    player.trials_completed += 1
    if not trial.success:
        player.trials_failed += 1

    player.terminated = player.trials_failed >= C.MAX_FAILURES

    player.total_score += trial.score

    return {
        "completed": player.trials_completed,
        "terminated": player.terminated,
        "score": player.total_score,
    }


def output_progress(player: Player, trial: Trial):
    return {
        "completed": player.trials_completed,
        "current": trial.iteration,
        "score": player.total_score,
        "terminated": player.terminated,
    }


def set_payoff(player: Player):
    player.payoff = max(0, player.total_score) * player.session.config["real_world_currency_per_point"]


#### PAGES ####


class Intro(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {"response_time_s": C.RESPONSE_TIMEOUT / 1000}


@live_page
class Main(Page):
    timeout_seconds = C.PAGE_TIMEOUT

    @staticmethod
    def is_displayed(player: Player):
        return not player.terminated

    @staticmethod
    def js_vars(player: Player):
        return {"C": dict(vars(C))}

    @staticmethod
    def live_next(player: Player, _):
        assert not player.terminated

        trial = current_trial(player)
        if trial is not None and trial.status == "LOADED":
            raise Warning("Page reloading is prohibited")

        trial = next_trial(player)
        trial.status = "LOADED"

        yield "progress", output_progress(player, trial)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_response(player: Player, payload: dict):
        trial = current_trial(player)
        assert trial is not None and trial.status == "LOADED"

        feedback = evaluate_response(trial, payload)
        yield "feedback", feedback

        if feedback["completed"]:
            trial.response_time = payload["time"]
            progress = update_progress(player, trial, feedback)
            yield "progress", progress

    @staticmethod
    def live_timeout(player: Player, payload: dict):
        trial = current_trial(player)
        assert trial is not None and trial.status == "LOADED"

        feedback = evaluate_timeout(trial, payload)
        yield "feedback", feedback

        if feedback["completed"]:
            trial.response_time = payload["time"]
            progress = update_progress(player, trial, feedback)
            yield "progress", progress

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.terminated = True
        set_payoff(player)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {
            "completed": player.trials_completed,
            "solved": len(Trial.filter(player=player, success=True)),
            "failed": len(Trial.filter(player=player, success=False)),
        }


page_sequence = [
    Intro,
    Main,
    Results,
]


def custom_export(players: list[Player]):
    yield [
        "session.code",
        "participant.code",
        #
        "player.condition",
        "player.trials_completed",
        "player.total_score",
        #
        "trial.iteration",
        "trial.status",
        "trial.expression",
        "trial.solution",
        "trial.response_time",
        "trial.answer",
        "trial.success",
        "trial.score",
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            #
            player.condition,
            player.trials_completed,
            player.total_score,
        ]
        for trial in Trial.filter(player=player):
            yield player_fields + [
                trial.iteration,
                trial.status,
                trial.expression,
                trial.solution,
                trial.response_time,
                trial.answer,
                trial.success,
                trial.score,
            ]
