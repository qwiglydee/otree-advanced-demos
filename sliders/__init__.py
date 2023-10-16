import random

from otree.api import *

from utils.live_utils import live_page


class C(BaseConstants):
    NAME_IN_URL = "slider"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_SLIDERS = 7
    SLIDER_RANGE = 10  # from -N to +N, target is always 0
    MAX_OFFSET = 100   # pixels
    TASK_TIMEOUT = 600  # seconds

    SCORE_CORRECT_MOVE = +5
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

    offset = models.IntegerField()
    initial = models.IntegerField()

    value = models.IntegerField()
    solved = models.BooleanField(initial=False)


def generate_slider(player: Player, idx: int):
    offset = random.randint(0, C.MAX_OFFSET)
    value = random.randint(1, C.SLIDER_RANGE) * random.choice([-1, +1])

    return Slider.create(
        player=player,
        offset=offset,
        initial=value,
        value=value,
    )


def generate_sliders(player):
    return [generate_slider(player, i) for i in range(1, 1+C.NUM_SLIDERS)]


def evaluate_move(slider: Slider, value: int):
    """evaluate a move of a slider and update, return feedback including score for a move"""
    slider.value = value
    slider.solved = (slider.value == 0)

    score = C.SCORE_CORRECT_MOVE if slider.solved else C.SCORE_INCORRECT_MOVE

    return {
        "slider": slider.id,
        "solved": slider.solved,
        "score": score
    }


def update_progress(player: Player, score: int):
    """update players progress"""
    player.total_score += score
    player.sliders_solved = len(Slider.filter(player=player, solved=True))
    player.terminated = player.sliders_solved == C.NUM_SLIDERS


#### INIT ####

def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player)


def init_player(player: Player):
    generate_sliders(player)


def set_payoff(player):
    player.payoff = player.total_score * player.session.config["real_world_currency_per_point"]


#### OUTPUTS ####


def output_progress(player: Player):
    return {
        "total": C.NUM_SLIDERS,
        "solved": player.sliders_solved,
        "score": player.total_score,
        "terminated": player.terminated,
    }


def output_slider(slider: Slider):
    return {
        "id": slider.id,
        "value": slider.value,
        "offset": {
            'L': slider.offset,
            'R': C.MAX_OFFSET - slider.offset
        },
        "solved": slider.solved,
    }


def output_sliders(player: Player):
    return [output_slider(s) for s in Slider.filter(player=player)]


#### PAGES ####


class Intro(Page):
    pass


@live_page
class Sliders(Page):
    timeout_seconds = C.TASK_TIMEOUT

    @staticmethod
    def vars_for_template(player: Player):
        # sliders for initial rendering, value/status ignored
        return {
            'sliders': output_sliders(player)
        }

    @staticmethod
    def live_start(player: Player, data):
        yield "progress", output_progress(player)

        if not player.terminated:
            yield "sliders", { 'sliders': output_sliders(player) }

    @staticmethod
    def live_slider(player: Player, data: dict):
        assert not player.terminated

        [slider] = Slider.filter(player=player, id=data["id"])

        feedback = evaluate_move(slider, data['value'])
        yield "feedback", feedback

        update_progress(player, feedback['score'])
        yield "progress", output_progress(player)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.terminated = True
        set_payoff(player)


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
                slider.id,
                slider.initial,
                slider.value,
                slider.solved,
            ]
