import random

from otree.api import *

from utils.live import live_page
from utils.rnd import bernoulli

class C(BaseConstants):
    NAME_IN_URL = "multistage"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ["ODD", "EVEN", "MIXED"]

    NUM_TRIALS = 10  # total number of trials to generate
    MAX_FAILURES = 5  # num of failures to abort the game

    PAGE_TIMEOUT = 600  # total time limit for tasks page (seconds)
    FEEDBACK_DELAY = 2000  # time (ms) to show feedback before next trial

    PROB_COMPLETE = 0.5  # probability of completing trial after a response

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


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)
    # status fields
    status = models.StringField(choices=["NEW", "LOADED", "COMPLETED"], initial="NEW")
    success = models.BooleanField(initial=None)
    score = models.IntegerField(initial=0)
    # task fields
    expression = models.StringField()
    solution = models.IntegerField()
    # response fields
    response_time = models.IntegerField()
    answer = models.IntegerField()
    confidence = models.IntegerField()
    difficulty = models.IntegerField()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player, subsession.session.config)


def init_player(player: Player, config: dict):
    player.condition = random.choice(C.CONDITIONS)
    if "condition" in config and config["condition"] != "random":
        assert config["condition"] in C.CONDITIONS
        player.condition = config["condition"]

    for i in range(C.NUM_TRIALS):
        generate_trial(player, i + 1)


def set_payoff(player: Player):
    """calculate final payoff"""
    player.payoff = (
        player.total_score * player.session.config["real_world_currency_per_point"]
    )


def generate_trial(player: Player, iteration: int):
    """generate single trial of the task"""

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

def evaluate_answer(trial: Trial, response: dict):
    """
    evaluate response, update score
    randomly decide if next stages follow
    return feedback
    """
    assert response["iteration"] == trial.iteration
    assert isinstance(response["answer"], int)

    trial.answer = response["answer"]
    trial.success = trial.answer == trial.solution
    trial.score = C.SCORE_SUCCESS if trial.success else C.SCORE_FAILURE

    if bernoulli(C.PROB_COMPLETE):
        trial.status = "COMPLETED"
        next_stage = None
    else:
        next_stage = random.choice(['C', 'D'])

    return {
        "completed": trial.status == "COMPLETED",
        "success": trial.success,
        "score": trial.score,
        "next": next_stage
    }


def evaluate_response_2(trial: Trial, response: dict):
    """
    evaluate second response
    randomly decide if next stages follow
    return feedback
    """
    assert response["iteration"] == trial.iteration
    assert isinstance(response["confidence"], int)

    trial.confidence = response["confidence"]

    if bernoulli(C.PROB_COMPLETE):
        trial.status = "COMPLETED"
        next_stage = None
    else:
        next_stage = 'D'

    return {
        "completed": trial.status == "COMPLETED",
        "success": trial.success,
        "score": trial.score,
        "next": next_stage
    }


def evaluate_response_3(trial: Trial, response: dict):
    """
    evaluate third response
    always complete trial
    return feedback
    """
    assert response["iteration"] == trial.iteration
    assert isinstance(response["difficulty"], int)

    trial.difficulty = response["difficulty"]

    trial.status = "COMPLETED"

    return {
        "completed": True,
        "success": trial.success,
        "score": trial.score,
    }


def update_progress(player: Player, feedback: dict):
    """update players progress using last feedback"""
    player.total_score += feedback["score"]
    player.total_score = max(0, player.total_score)

    player.trials_completed += 1
    if not feedback["success"]:
        player.trials_failed += 1
    player.terminated = (
        player.trials_completed == C.NUM_TRIALS
        or player.trials_failed >= C.MAX_FAILURES
    )


def current_trial(player: Player):
    """retrieve current trial"""
    trials = Trial.filter(player=player, iteration=player.trials_completed + 1)
    return trials[0] if trials else None


#### FORMAT ####

def output_progress(player: Player, trial: Trial):
    return {
        "total": C.NUM_TRIALS,
        "completed": player.trials_completed,
        "current": trial.iteration,
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
class Main(Page):
    """Live page with series of trials"""

    timeout_seconds = C.PAGE_TIMEOUT

    @staticmethod
    def is_displayed(player: Player):
        return not player.terminated

    @staticmethod
    def js_vars(player: Player):
        return {"C": dict(vars(C))}

    @staticmethod
    def live_iter(player: Player, _):
        """retrieve current progress and trial"""
        trial = current_trial(player)
        assert trial is not None

        # detect reloading incomplete tasks
        # if trial.status == "LOADED":
        #     raise RuntimeError("Page reloading is prohibited")
        trial.status = "LOADED"

        yield "progress", output_progress(player, trial)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_answer(player: Player, payload: dict):
        """handle response from player"""
        trial = current_trial(player)
        assert trial is not None and trial.status == 'LOADED'

        trial.response_time = payload["time"]
        feedback = evaluate_answer(trial, payload)
        yield "feedback", feedback

        if trial.status == 'COMPLETED':
            update_progress(player, feedback)
            yield "progress", output_progress(player, trial)

    @staticmethod
    def live_confidence(player: Player, payload: dict):
        """handle second response from player"""
        trial = current_trial(player)
        assert trial is not None and trial.status == 'LOADED'

        feedback = evaluate_response_2(trial, payload)
        yield "feedback", feedback

        if trial.status == 'COMPLETED':
            update_progress(player, feedback)
            yield "progress", output_progress(player, trial)

    @staticmethod
    def live_difficulty(player: Player, payload: dict):
        """handle second response from player"""
        trial = current_trial(player)
        assert trial is not None and trial.status == 'LOADED'

        feedback = evaluate_response_3(trial, payload)
        yield "feedback", feedback

        # NB: always complete now
        update_progress(player, feedback)
        yield "progress", output_progress(player, trial)


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
        "trial.confidence",
        "trial.difficulty",
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
                trial.confidence,
                trial.difficulty,
                trial.success,
                trial.score,
            ]
