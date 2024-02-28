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
        generate_trials(player, subsession.session.config)


def init_player(player: Player, config: dict):
    pass


def generate_trials(player: Player, config: dict):
    images = random.sample(IMAGES, k=C.NUM_TRIALS)

    for i, img in enumerate(images):
        generate_trial(player, i + 1, img)


def generate_trial(player: Player, iteration: int, image: Path):
    return Trial.create(
        player=player,
        iteration=iteration,
        image=image.stem,
    )


def current_trial(player: Player):
    trials = Trial.filter(player=player, iteration=player.trials_completed + 1)
    return trials[0] if trials else None


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "image_url": url_of_static("images/" + trial.image + ".png"),
    }


def evaluate_response(trial: Trial, response: dict):
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
    assert trial.status == 'COMPLETED'

    player.trials_completed += 1

    player.terminated = player.trials_completed == C.NUM_TRIALS

    player.total_score += trial.score

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
    player.payoff = max(0, player.total_score) * player.session.config["real_world_currency_per_point"]


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
        if trial.status == "LOADED":
            raise Warning("Page reloading is prohibited")
        trial.status = "LOADED"

        yield "progress", current_progress(player, trial)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_drawing(player: Player, payload: dict):
        trial = current_trial(player)
        assert trial is not None and trial.status == "LOADED"

        feedback = evaluate_response(trial, payload)
        yield "feedback", feedback

        if feedback['completed']:
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
