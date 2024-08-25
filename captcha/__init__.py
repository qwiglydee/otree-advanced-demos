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

    CONDITIONS = ["A", "B"]
    NUM_TRIALS = 10  # total number of trials to generate

    PAGE_TIMEOUT = 600  # total time limit for tasks page (seconds)
    FEEDBACK_DELAY = 2  # time to show feedback before next trial

    SCORE_ENDOWMENT = 100
    SCORE_SUCCESS = +5
    SCORE_FAILURE = -5

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

    completed = models.IntegerField(initial=0)
    terminated = models.BooleanField(initial=False)
    success = models.IntegerField(initial=0)
    errors = models.IntegerField(initial=0)
    score = models.IntegerField(initial=0)

    def setup(player):
        conf = player.session.config

        if conf.get("condition", "random") != "random":
            assert conf["condition"] in C.CONDITIONS
            player.condition = conf["condition"]
        else:
            player.condition = random.choice(C.CONDITIONS)

        player.score = C.SCORE_ENDOWMENT


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)
    status = models.StringField(choices=["NEW", "LOADED", "COMPLETED"], initial="NEW")
    #
    text = models.StringField()
    image = models.LongStringField()
    #
    response_time = models.IntegerField()
    answer = models.StringField()
    success = models.BooleanField(initial=None)
    score = models.IntegerField(initial=0)

    @staticmethod
    def generate(player: Player, iteration: int):
        """generate single trial for the player and iteration"""
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

    @staticmethod
    def pregenerate(player: Player, count: int):
        for i in range(count):
            Trial.generate(player, 1 + i)

    @staticmethod
    def next(player: Player):
        "generates new trial for the player"
        assert player.completed < C.NUM_TRIALS
        return Trial.generate(player, player.completed + 1)

    @staticmethod
    def current(player: Player):
        "retrieves a trial currently loaded for a player, None if not loaded"
        return Trial.objects_filter(player=player, status="LOADED").order_by("id").first()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        player.setup()


def set_payoff(player: Player):
    player.payoff = max(0, player.score) * player.session.config["real_world_currency_per_point"]


#### script logic


def current_progress(player: Player, trial: Trial = None):
    return {
        "total": C.NUM_TRIALS,
        "completed": player.completed,
        "terminated": player.terminated,
        "current": trial.iteration if trial else None,
        #
        "success": player.success,
        "errors": player.errors,
        "score": player.score,
    }


def current_trial(player: Player, trial: Trial):
    return {
        "iteration": trial.iteration,
        "image": trial.image,
    }


def evaluate_response(player: Player, trial: Trial, response: dict):
    assert response["iteration"] == trial.iteration

    trial.answer = response["answer"].upper()
    trial.success = trial.answer == trial.text
    if trial.success:
        trial.score = C.SCORE_SUCCESS
    else:
        trial.score = C.SCORE_FAILURE

    trial.status = "COMPLETED"

    return {
        "completed": True,
        "success": trial.success,
        "score": trial.score,
    }


def update_progress(player: Player, trial: Trial, feedback: dict):
    assert trial.status == "COMPLETED"

    player.completed += 1
    player.terminated = player.completed == C.NUM_TRIALS
    if trial.success:
        player.success += 1
    else:
        player.errors += 1
    player.score += trial.score

    return {
        "completed": player.completed,
        "terminated": player.terminated,
        "success": player.success,
        "errors": player.errors,
        "score": player.score,
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
        assert not player.terminated

        trial = Trial.current(player)
        if trial is None:
            trial = Trial.next(player)
        trial.status = "LOADED"

        yield "progress", current_progress(player, trial)
        yield "trial", current_trial(player, trial)

    @staticmethod
    def live_response(player: Player, response: dict):
        assert not player.terminated

        trial = Trial.current(player)
        assert trial is not None

        feedback = evaluate_response(player, trial, response)
        yield "feedback", feedback

        if feedback["completed"]:
            trial.response_time = response["time"]
            progress = update_progress(player, trial, feedback)
            yield "progress", progress

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.terminated = True
        set_payoff(player)


class Results(Page):
    pass


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
        "player.completed",
        "player.success",
        "player.errors",
        "player.score",
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
            player.completed,
            player.success,
            player.errors,
            player.score,
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
