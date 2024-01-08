from pathlib import Path
import random

from otree.api import *
from otree.common2 import url_of_static

from utils.live import live_page


APPDIR = Path(__file__).parent
IMAGES = list((APPDIR / "static" / "images").glob("*.png"))


class C(BaseConstants):
    NAME_IN_URL = "drawing"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = len(IMAGES)

    PAGE_TIMEOUT = 300
    FEEDBACK_DELAY = 2000  # time (ms) to show feedback before next trial

    CANVAS_SIZE = (256, 256)
    FEATHER = 4
    COLOR = "#00000"

    SCORE_DRAW = +1
    SCORE_SKIP = 0


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
    score = models.IntegerField(initial=0)
    # task fields
    image = models.StringField()
    # response fields
    response_time = models.IntegerField()
    drawing = models.LongStringField()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player, subsession.session.config)


def init_player(player: Player, config: dict):
    images = random.sample(IMAGES, k=C.NUM_TRIALS)

    for i, img in enumerate(images):
        generate_trial(player, i + 1, img)


def set_payoff(player: Player):
    """calculate final payoff"""
    player.payoff = (
        player.total_score * player.session.config["real_world_currency_per_point"]
    )


def generate_trial(player: Player, iteration: int, image: Path):
    """generate single trial of the task"""
    return Trial.create(
        player=player,
        iteration=iteration,
        image=image.stem,
    )


def evaluate_response(trial: Trial, response: dict):
    """evaluate response and update trial status and score, return feedback"""
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


def update_progress(player: Player, feedback: dict):
    """update players progress using last feedback"""
    player.total_score += feedback["score"]
    player.total_score = max(0, player.total_score)

    if feedback["completed"]:
        player.trials_completed += 1
        player.terminated = player.trials_completed == C.NUM_TRIALS


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
        "image_url": url_of_static("images/" + trial.image + ".png"),
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
        if trial.status == 'LOADED':
            raise RuntimeError("Page reloading is prohibited")
        trial.status = 'LOADED'

        yield "progress", output_progress(player, trial)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_drawing(player: Player, payload: dict):
        """handle response from player"""
        trial = current_trial(player)
        assert trial is not None and trial.status == 'LOADED'

        trial.response_time = payload["time"]
        feedback = evaluate_response(trial, payload)
        update_progress(player, feedback)

        yield "progress", output_progress(player, trial)
        yield "feedback", feedback

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
        "trial.image",
        "trial.response_time",
        "trial.score",
        "trial.drawing",
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
                trial.image,
                trial.response_time,
                trial.score,
                trial.drawing,
            ]
