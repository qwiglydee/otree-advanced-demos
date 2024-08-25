import random

from otree.api import *

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "slider"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ["A", "B"]
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
    condition = models.StringField()

    solved = models.IntegerField(initial=0)
    terminated = models.BooleanField(initial=False)
    score = models.IntegerField(initial=0)

    def setup(player):
        conf = player.session.config

        if conf.get("condition", "random") != "random":
            assert conf["condition"] in C.CONDITIONS
            player.condition = conf["condition"]
        else:
            player.condition = random.choice(C.CONDITIONS)


class Slider(ExtraModel):
    # id = built-in field
    player = models.Link(Player)
    offset = models.IntegerField()
    initial = models.IntegerField()
    target = models.IntegerField()
    value = models.IntegerField()
    moves = models.IntegerField(initial=0)
    solved = models.BooleanField(initial=False)

    @staticmethod
    def generate(player: Player):
        offset = random.randint(0, C.MAX_OFFSET)
        target = random.randint(-C.SLIDER_RANGE + 1, C.SLIDER_RANGE - 1)
        initial = random.randint(-C.SLIDER_RANGE + 1, C.SLIDER_RANGE - 1)
        if initial == target:
            initial += random.choice([-1, +1])

        return Slider.create(
            player=player,
            offset=offset,
            initial=initial,
            target=target,
            value=initial,
        )

    @staticmethod
    def pregenerate(player: Player, count: int):
        for i in range(count):
            Slider.generate(player)

    @staticmethod
    def get(player: Player, slider_id: int):
        return Slider.objects_get(player=player, id=slider_id)


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        player.setup()
        Slider.pregenerate(player, C.NUM_SLIDERS)


def set_payoff(player: Player):
    player.payoff = max(0, player.score) * player.session.config["real_world_currency_per_point"]


####


def current_progress(player: Player):
    return {
        "total": C.NUM_SLIDERS,
        "solved": player.solved,
        "terminated": player.terminated,
        "score": player.score,
    }


def evaluate_move(slider: Slider, response: dict):
    assert "value" in response
    assert isinstance(response["value"], int)

    slider.moves += 1
    slider.value = response["value"]
    slider.solved = slider.value == slider.target

    if slider.solved:
        score = C.SCORE_CORRECT_MOVE
    else:
        score = C.SCORE_INCORRECT_MOVE

    return {
        "id": slider.id,
        "solved": slider.solved,
        "score": score,
    }


def update_progress(player: Player, slider: Slider, feedback: dict):
    player.score += feedback["score"]
    player.solved = len(Slider.filter(player=player, solved=True))
    player.terminated = player.solved == C.NUM_SLIDERS

    return {
        "solved": player.solved,
        "score": player.score,
        "terminated": player.terminated,
    }


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
    def vars_for_template(player: Player):
        # only sequence of ids for initial rendering only
        return {"sliders": [s.id for s in Slider.filter(player=player)]}

    @staticmethod
    def js_vars(player: Player):
        return {
            "C": dict(vars(C)),
            "sliders": {
                s.id: {"target": s.target, "value": s.value, "offset": s.offset, "solved": s.solved}
                for s in Slider.filter(player=player)
            },
            "progress": current_progress(player),
        }

    # @staticmethod
    # def live_reset(player: Player, _):
    #     yield "progress", current_progress(player)
    #     yield "sliders", {s.id: output_slider(s) for s in Slider.filter(player=player)}

    @staticmethod
    def live_slider(player: Player, response: dict):
        slider = Slider.get(player, response["id"])

        feedback = evaluate_move(slider, response)
        yield "feedback", feedback

        progress = update_progress(player, slider, feedback)
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
        "slider.target",
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
            player.solved,
            player.score,
        ]
        for slider in Slider.filter(player=player):
            yield player_fields + [
                slider.id,
                slider.target,
                slider.initial,
                slider.moves,
                slider.value,
                slider.solved,
            ]
