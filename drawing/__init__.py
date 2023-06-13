import random

from otree.api import *
from otree.common2 import url_of_static

from utils.live_utils import live_page, live_method

# correspond to assets subdir
IMAGES = [
    "1F609.png",
    "1F60F.png",
    "1F615.png",
    "1F61F.png",
    "1F641.png",
    "1F642.png",
    "2639.png",
    "263A.png",
]

# built-in url_for_static doesnt work
def url_of_image(image):
    return url_of_static("images/" + image)


class C(BaseConstants):
    NAME_IN_URL = "drawing"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = len(IMAGES)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    trials_completed = models.IntegerField(initial=0)

    @property
    def current_iter(self):
        "current iteration is 1 forward of completed" ""
        return self.trials_completed + 1


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)

    # task fields
    image = models.StringField()

    # response fields
    response_time = models.IntegerField()
    drawing = models.LongStringField()

    # status fields
    completed = models.BooleanField()


def generate_trial(player: Player, iteration: int, image):
    """generate single trial of the task"""

    return Trial.create(
        player=player,
        iteration=iteration,
        image=image,
    )


def generate_trials(player):
    """generate all trials for a player"""
    images = random.sample(IMAGES, k=C.NUM_TRIALS)
    return [generate_trial(player, idx + 1, img) for idx, img in enumerate(images)]


def evaluate_trial(trial: Trial, response_data: dict):
    trial.completed = True

#### INIT ####


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        trials = generate_trials(player)
        if len(trials) != C.NUM_TRIALS:
            raise RuntimeError("Failed to generate trials", player)


#### FORMAT ####


def format_progress(player: Player):
    return {"total": C.NUM_TRIALS, "completed": player.trials_completed}


def format_trial(trial: Trial):
    return {"image": url_of_image(trial.image)}


def format_trials(trials):
    return {t.iteration: format_trial(t) for t in trials}


#### PAGES ####


class Intro(Page):
    pass


@live_page
class Tasks(Page):
    @staticmethod
    def js_vars(player: Player):
        return {
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
        trial.drawing = data['drawing']

        player.trials_completed += 1

        yield "progress", format_progress(player)


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
        #
        "iteration",
        "image",
        "response_time",
        "drawing",
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            player.trials_completed,
        ]
        for trial in Trial.filter(player=player):
            yield player_fields + [
                trial.iteration,
                trial.image,
                trial.response_time,
                trial.drawing,
            ]
