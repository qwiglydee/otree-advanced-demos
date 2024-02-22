import string
from pathlib import Path
import random

from otree.api import *

from utils.live import live_page
from utils import images


class C(BaseConstants):
    NAME_IN_URL = "captcha"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = 10  # total number of trials to generate
    MAX_FAILURES = 5  # num of failures to abort the game

    PAGE_TIMEOUT = 600  # total time limit for tasks page (seconds)
    FEEDBACK_DELAY = 2000  # time (ms) to show feedback before next trial

    SCORE_SUCCESS = +10
    SCORE_FAILURE = -1

    SYMBOLS = string.ascii_uppercase
    LENGTH = 5

    TEXT_SIZE = 128
    TEXT_BGCOLOR = "#FFFFFF"
    TEXT_COLOR = "#000000"


APPDIR = Path(__file__).parent
FONT = images.font(APPDIR / "assets" / "FreeSerifBold.otf", C.TEXT_SIZE)


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
    text = models.StringField()
    image = models.LongStringField()
    # response fields
    response_time = models.IntegerField()
    answer = models.IntegerField()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player, subsession.session.config)
        generate_trials(player, subsession.session.config)


def init_player(player: Player, config: dict):
    pass


def generate_trials(player: Player, config: dict):
    for i in range(C.NUM_TRIALS):
        generate_trial(player, i + 1)


def generate_trial(player: Player, iteration: int):
    text = "".join(random.sample(C.SYMBOLS, k=C.LENGTH))
    image = images.text(
        text,
        FONT,
        size=C.TEXT_SIZE,
        padding=C.TEXT_SIZE // 2,
        color=C.TEXT_COLOR,
        bgcolor=C.TEXT_BGCOLOR,
    )
    image = images.distort(image)
    image_data = images.encode(image)

    return Trial.create(
        player=player,
        iteration=iteration,
        text=text,
        image=image_data,
    )


def current_trial(player: Player):
    trials = Trial.filter(player=player, iteration=player.trials_completed + 1)
    return trials[0] if trials else None


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "image": trial.image,
    }


def evaluate_response(trial: Trial, response: dict):
    assert response["iteration"] == trial.iteration

    answer = response["answer"].upper()

    trial.answer = answer
    trial.success = trial.answer == trial.text
    trial.score = C.SCORE_SUCCESS if trial.success else C.SCORE_FAILURE

    trial.status = "COMPLETED"

    return {
        "completed": True,
        "success": trial.success,
        "score": trial.score,
    }


def update_progress(player: Player, feedback: dict):
    assert feedback["completed"]

    player.trials_completed += 1
    if not feedback["success"]:
        player.trials_failed += 1

    player.terminated = (
        player.trials_completed == C.NUM_TRIALS
        or player.trials_failed >= C.MAX_FAILURES
    )

    player.total_score += feedback["score"]

    return {
        "completed": player.trials_completed,
        "terminated": player.terminated,
        "score": player.total_score,
    }


def current_progress(player: Player, trial: Trial):
    return {
        "total": C.NUM_TRIALS,
        "completed": player.trials_completed,
        "current": trial.iteration,
        "score": player.total_score,
        "terminated": player.terminated,
    }


def set_payoff(player: Player):
    player.payoff = (
        player.total_score * player.session.config["real_world_currency_per_point"]
    )


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
        assert not player.terminated

        trial = current_trial(player)
        if trial is not None and trial.status == "LOADED":
            raise Warning("Page reloading is prohibited")
        trial.status = "LOADED"

        yield "progress", current_progress(player, trial)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_response(player: Player, payload: dict):
        trial = current_trial(player)
        assert trial is not None and trial.status == 'LOADED' and trial.status == 'LOADED'

        feedback = evaluate_response(trial, payload)
        yield "feedback", feedback

        if feedback['completed']:
            trial.response_time = payload["time"]
            progress = update_progress(player, feedback)
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
        "trial.text",
        "trial.image",
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
                trial.text,
                trial.image,
                trial.response_time,
                trial.answer,
                trial.success,
                trial.score,
            ]
