import random

from otree.api import *

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "slider"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_SLIDERS = 13
    SLIDER_RANGE = 10  # from -N to +N, target is always 0
    MAX_OFFSET = 100  # pixels
    PAGE_TIMEOUT = 600  # seconds

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
    moves = models.IntegerField(initial=0)
    solved = models.BooleanField(initial=False)


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player, subsession.session.config)


def init_player(player: Player, config: dict):
    for i in range(C.NUM_SLIDERS):
        generate_slider(player)


def generate_slider(player: Player):
    offset = random.randint(0, C.MAX_OFFSET)
    value = random.randint(1, C.SLIDER_RANGE) * random.choice([-1, +1])

    return Slider.create(
        player=player,
        offset=offset,
        initial=value,
        value=value,
    )


def get_slider(player: Player, slider_id: int):
    [slider] = Slider.filter(player=player, id=slider_id)
    return slider


def output_slider(slider: Slider):
    return {
        "id": slider.id,
        "value": slider.value,
        "offset": slider.offset,
        "solved": slider.solved,
    }


def evaluate_move(slider: Slider, response: dict):
    slider.moves += 1
    slider.value = response['value']
    slider.solved = slider.value == 0

    score = C.SCORE_CORRECT_MOVE if slider.solved else C.SCORE_INCORRECT_MOVE

    return {
        "id": slider.id,
        "value": slider.value,
        "solved": slider.solved,
        "score": score,
    }


def update_progress(player: Player, feedback: dict):
    player.total_score += feedback["score"]
    player.sliders_solved = len(Slider.filter(player=player, solved=True))
    player.terminated = player.sliders_solved == C.NUM_SLIDERS



def current_progress(player: Player):
    return {
        "total": C.NUM_SLIDERS,
        "solved": player.sliders_solved,
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
class Sliders(Page):
    timeout_seconds = C.PAGE_TIMEOUT

    @staticmethod
    def is_displayed(player: Player):
        return not player.terminated

    @staticmethod
    def js_vars(player: Player):
        return {"C": dict(vars(C))}

    @staticmethod
    def vars_for_template(player: Player):
        # sequence of ids for initial rendering only
        return {"sliders": [s.id for s in Slider.filter(player=player)]}

    @staticmethod
    def live_reset(player: Player, _):
        yield "progress", current_progress(player)
        yield "sliders", {s.id: output_slider(s) for s in Slider.filter(player=player)}

    @staticmethod
    def live_slider(player: Player, payload: dict):
        slider = get_slider(player, payload["id"])

        feedback = evaluate_move(slider, payload)
        update_progress(player, feedback)

        yield "progress", current_progress(player)
        yield "feedback", feedback

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
        #
        "player.sliders_solved",
        "player.total_score",
        #
        "slider.id",
        "slider.initial",
        "slider.moves",
        "slider.value",
        "slider.solved",
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            #
            player.sliders_solved,
            player.total_score,
        ]
        for slider in Slider.filter(player=player):
            yield player_fields + [
                slider.id,
                slider.initial,
                slider.moves,
                slider.value,
                slider.solved,
            ]
