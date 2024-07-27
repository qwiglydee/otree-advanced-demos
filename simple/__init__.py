import random

from otree.api import *

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "simple"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ["ODD", "EVEN", "MIXED"]

    NUM_TRIALS = 10  # total number of trials to generate
    MAX_FAILURES = 5  # num of failures to abort the game

    PAGE_TIMEOUT = 600  # total time limit for tasks page (seconds)
    FEEDBACK_DELAY = 2000  # time (ms) to show feedback before next trial

    SCORE_SUCCESS = +10
    SCORE_FAILURE = -1


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

    def init(player, config: dict):
        if "condition" in config and config["condition"] != "random":
            assert config["condition"] in C.CONDITIONS
            player.condition = config["condition"]
        else:
            player.condition = random.choice(C.CONDITIONS)


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField()
    status = models.StringField(choices=["NEW", "LOADED", "COMPLETED", "DROPPED"], initial="NEW")

    # task fields
    expression = models.StringField()
    solution = models.IntegerField()

    # response fields
    response_time = models.IntegerField()
    answer = models.IntegerField()

    # result fields
    success = models.BooleanField(initial=None)
    score = models.IntegerField(initial=0)

    @classmethod
    def generate(cls, config: dict, player: Player, iteration: int):
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

        return cls.create(
            player=player,
            iteration=iteration,
            expression=expr,
            solution=solution,
        )

    @classmethod
    def pregenerate(cls, config: dict, player: Player, count: int):
        return [cls.generate(config, player, i) for i in range(1, 1 + count)]

    @classmethod
    def next(cls, player: Player):
        "retrieves next pre-generated trial to load for a player, None if no more trials"
        return cls.objects_filter(player=player, status="NEW").order_by("id").first()

    @classmethod
    def current(cls, player: Player):
        "retrieves a trial currently loaded for a player, None if not loaded"
        return cls.objects_filter(player=player, status="LOADED").order_by("id").first()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        player.init(subsession.session.config)
        Trial.pregenerate(subsession.session.config, player, C.NUM_TRIALS)


def set_payoff(player: Player):
    player.payoff = max(0, player.total_score) * player.session.config["real_world_currency_per_point"]


#### I/O logic


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "expression": trial.expression,
    }


def evaluate_response(trial: Trial, response: dict):
    assert isinstance(response.get("answer"), int)

    answer = response["answer"]

    trial.answer = answer
    trial.success = trial.answer == trial.solution
    trial.score = C.SCORE_SUCCESS if trial.success else C.SCORE_FAILURE

    trial.status = "COMPLETED"

    # feedback
    return {
        "completed": True,
        "success": trial.success,
        "score": trial.score,
    }


def update_progress(player: Player, trial: Trial, feedback: dict):
    assert trial.status == "COMPLETED"

    player.total_score += trial.score

    player.trials_completed += 1
    if not trial.success:
        player.trials_failed += 1

    player.terminated = player.trials_completed == C.NUM_TRIALS or player.trials_failed >= C.MAX_FAILURES


def current_progress(player: Player, current: Trial = None):
    return {
        "total": C.NUM_TRIALS,
        "completed": player.trials_completed,
        "current": current.iteration if current else None,
        "score": player.total_score,
        "terminated": player.terminated,
    }


#### PAGES ####


class Intro(Page):
    pass


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
        trial = Trial.current(player)
        if trial:
            raise Warning("Page reloading is prohibited")

        trial = Trial.next(player)
        trial.status = "LOADED"

        yield "progress", current_progress(player, trial)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_response(player: Player, response: dict):
        trial = Trial.current(player)
        assert trial is not None
        assert response["iteration"] == trial.iteration

        feedback = evaluate_response(trial, response)
        yield "feedback", feedback

        if feedback["completed"]:
            trial.response_time = response["time"]
            update_progress(player, trial, feedback)
            yield "progress", current_progress(player)

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
