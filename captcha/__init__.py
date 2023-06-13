import random
import string
from pathlib import Path

from otree.api import *

from utils.live_utils import live_page, live_method
from utils import image_utils


APPDIR = Path(__file__).parent  # directory of the app


class C(BaseConstants):
    NAME_IN_URL = "captcha"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    SYMBOLS = string.ascii_uppercase
    LENGTH = 3
    TEXT_SIZE = 64
    TEXT_BGCOLOR = "#FFFFFF"
    TEXT_COLOR = "#000000"
    TEXT_FONT = image_utils.font(APPDIR / "assets" / "FreeSerifBold.otf", TEXT_SIZE)  # preload the file

    TASKS_TIMEOUT = 30  # seconds
    TRIAL_DELAY = 500  # milliseconds

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
    text = models.StringField()
    image = models.LongStringField()

    # response fields
    response = models.StringField()
    response_time = models.IntegerField()

    # status fields
    completed = models.BooleanField()
    success = models.BooleanField()
    score = models.IntegerField(initial=0)


def generate_trial(player: Player, iteration: int):
    """generate single trial of the task"""
    text = "".join(random.sample(C.SYMBOLS, k=C.LENGTH))

    image = image_utils.text(
        text, C.TEXT_FONT, size=C.TEXT_SIZE, padding=C.TEXT_SIZE // 2, color=C.TEXT_COLOR, bgcolor=C.TEXT_BGCOLOR
    )
    image = image_utils.distort(image)
    data = image_utils.encode(image)

    return Trial.create(
        player=player,
        iteration=iteration,
        text=text,
        image=data,
    )


def evaluate_trial(trial: Trial, response_data: dict):
    """evaluate trial success and score from response"""
    trial.response = response_data["response"]

    trial.success = trial.response.upper() == trial.text
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
        "score": player.total_score,
    }


def format_trial(trial: Trial):
    return {"image": trial.image}


def format_feedback(trial: Trial):
    return {"success": trial.success, "score": trial.score}


#### PAGES ####


class Intro(Page):
    pass


@live_page
class Tasks(Page):
    timeout_seconds = C.TASKS_TIMEOUT

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
        "text",
        "image",
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
                trial.text,
                trial.image,
                trial.response_time,
                trial.response,
                trial.success,
                trial.score,
            ]
