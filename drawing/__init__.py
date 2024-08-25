from pathlib import Path
import random

from otree.api import *
from otree.common2 import url_of_static

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "drawing"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ["A", "B"]

    NUM_TRIALS = 10  # total number of trials to generate

    PAGE_TIMEOUT = 600  # total time limit for tasks page (seconds)
    FEEDBACK_DELAY = 2  # time to show feedback before next trial

    CANVAS_SIZE = (256, 256)
    FEATHER = 4
    COLOR = "#00000"

    SCORE_ENDOWMENT = 0
    SCORE_DRAW = +1
    SCORE_SKIP = 0


APPDIR = Path(__file__).parent
IMAGES = list((APPDIR / "static" / "images").glob("*.png"))


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
    image = models.StringField()
    drawing = models.LongStringField()
    #
    response_time = models.IntegerField()
    score = models.IntegerField(initial=0)

    @staticmethod
    def generate(player: Player, iteration: int, image: Path):
        """generate single trial for the player and iteration"""
        return Trial.create(
            player=player,
            iteration=iteration,
            image=image.stem,
        )

    @staticmethod
    def pregenerate(player: Player, count: int):
        images = random.sample(IMAGES, k=count)

        for i, img in enumerate(images):
            Trial.generate(player, i + 1, img)

    @staticmethod
    def next(player: Player):
        "generates new trial for the player"
        assert player.completed < C.NUM_TRIALS
        return Trial.objects_filter(player=player, status="NEW").order_by("id").first()

    @staticmethod
    def current(player: Player):
        "retrieves a trial currently loaded for a player, None if not loaded"
        return Trial.objects_filter(player=player, status="LOADED").order_by("id").first()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        player.setup()
        Trial.pregenerate(player, C.NUM_TRIALS)


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
        "score": player.score,
    }


def current_trial(player: Player, trial: Trial):
    return {
        "iteration": trial.iteration,
        "image_url": url_of_static("images/" + trial.image + ".png"),
    }


def evaluate_response(player: Player, trial: Trial, response: dict):
    assert response["iteration"] == trial.iteration

    if "drawing" in response:
        trial.drawing = response["drawing"]
        trial.score = C.SCORE_DRAW
    else:
        trial.score = C.SCORE_SKIP

    trial.status = "COMPLETED"

    return {
        "completed": True,
        "score": trial.score,
    }


def update_progress(player: Player, trial: Trial, feedback: dict):
    assert trial.status == "COMPLETED"

    player.completed += 1
    player.terminated = player.completed == C.NUM_TRIALS
    player.score += trial.score

    return {
        "completed": player.completed,
        "terminated": player.terminated,
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
    def live_drawing(player: Player, response: dict):
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
        "player.score",
        #
        "trial.iteration",
        "trial.status",
        "trial.image",
        "trial.response_time",
        "trial.drawing",
        "trial.score",
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            #
            player.condition,
            player.completed,
            player.score,
        ]
        for trial in Trial.filter(player=player):
            yield player_fields + [
                trial.iteration,
                trial.status,
                trial.image,
                trial.response_time,
                trial.drawing,
                trial.score,
            ]
