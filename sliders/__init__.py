import random

from otree.api import *

from utils.live_utils import live_page, live_method


class C(BaseConstants):
    NAME_IN_URL = "slider"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_SLIDERS = 32
    SLIDER_RANGE = 10  # from -N to +N, target is always 0
    MAX_OFFSET = 100   # pixels
    TASK_TIMEOUT = 60000  # seconds

    SCORE_CORRECT_MOVE = +1
    SCORE_INCORRECT_MOVE = -1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    sliders_solved = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)
    terminated = models.BooleanField(initial=False)


class Slider(ExtraModel):
    player = models.Link(Player)
    name = models.StringField()  # should be id-like string to fit better into input names
    offset = models.IntegerField()
    initial = models.IntegerField()

    value = models.IntegerField()
    solved = models.BooleanField(initial=False)


def evaluate_move(slider: Slider, move: dict):
    "update state of slider and player and return score for the move"
    was_solved = slider.solved

    slider.value = move["value"]
    slider.solved = slider.value == 0

    if was_solved != slider.solved:  # status changed
        if slider.solved:
            slider.player.sliders_solved += 1
        else:
            slider.player.sliders_solved -= 1

    if slider.solved:
        return C.SCORE_CORRECT_MOVE
    else:
        return C.SCORE_INCORRECT_MOVE


def generate_slider(player: Player, idx: int):
    offset = random.randint(0, C.MAX_OFFSET)
    value = random.randint(1, C.SLIDER_RANGE) * random.choice([-1, +1])

    return Slider.create(
        player=player,
        name=f"s{idx}",
        offset=offset,
        initial=value,
        value=value,
    )


def generate_sliders(player):
    return [generate_slider(player, i + 1) for i in range(C.NUM_SLIDERS)]


def calculate_payoff(player):
    """calculate final payoff"""
    player.payoff = player.total_score * player.session.config["real_world_currency_per_point"]


#### INIT ####


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        generate_sliders(player)


#### FORMAT ####


def format_progress(player: Player):
    return {
        "total": C.NUM_SLIDERS,
        "solved": player.sliders_solved,
        "score": player.total_score,
        "terminated": player.terminated,
    }


def format_slider(slider: Slider):
    return {
        "name": slider.name,
        "value": slider.value,
        "margins": {
            'l': slider.offset,
            'r': C.MAX_OFFSET - slider.offset
        },
    }


def format_feedback(slider: Slider):
    return {"name": slider.name, "solved": slider.solved}


#### PAGES ####


class Intro(Page):
    pass


@live_page
class Sliders(Page):
    timeout_seconds = C.TASK_TIMEOUT

    @staticmethod
    def vars_for_template(player: Player):
        sliders = Slider.filter(player=player)
        return {"sliders": [format_slider(s) for s in sliders]}

    @staticmethod
    def js_vars(player: Player):
        return {"progress": format_progress(player)}

    @live_method("move")
    def handle_move(player: Player, data: dict):
        [slider] = Slider.filter(player=player, name=data["name"])

        score = evaluate_move(slider, data)

        yield "feedback", format_feedback(slider)

        player.total_score = max(0, player.total_score + score)

        yield "progress", format_progress(player)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        calculate_payoff(player)


class Results(Page):
    pass


page_sequence = [
    Intro,
    Sliders,
    Results,
]


def custom_export(players: list[Player]):
    yield [
        "session",
        "participant",
        "sliders_solved",
        "total_score",
        #
        "slider",
        "initial",
        "value",
        "solved",
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            player.sliders_solved,
            player.total_score,
        ]
        for slider in Slider.filter(player=player):
            yield player_fields + [
                slider.name,
                slider.initial,
                slider.value,
                slider.solved,
            ]
