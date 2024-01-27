import random

from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = "local"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ["ODD", "EVEN", "MIXED"]

    NUM_TRIALS = 10  # total number of trials to generate

    PAGE_TIMEOUT = 30  # total time limit for tasks page (seconds)
    FEEDBACK_DELAY = 250  # time (ms) before next trial

    SCORE_SUCCESS = +10
    SCORE_FAILURE = -1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    trials_completed = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)

    # ;-separated answers
    answers = models.LongStringField()


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)
    # status fields
    status = models.StringField(choices=["NEW", "LOADED", "COMPLETED"], initial="NEW")
    success = models.BooleanField(initial=None)
    score = models.IntegerField(initial=0)
    # task fields
    expression = models.StringField()
    solution = models.IntegerField()
    option_1 = models.IntegerField()
    option_2 = models.IntegerField()
    option_3 = models.IntegerField()
    option_4 = models.IntegerField()

    # response fields
    answer = models.IntegerField()
    choice = models.IntegerField()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player, subsession.session.config)


def init_player(player: Player, config: dict):
    player.condition = random.choice(C.CONDITIONS)
    if "condition" in config and config["condition"] != "random":
        assert config["condition"] in C.CONDITIONS
        player.condition = config["condition"]

    for i in range(C.NUM_TRIALS):
        generate_trial(player, i + 1)


def generate_trial(player: Player, iteration: int):
    if player.condition == "MIXED":
        a = random.randint(10, 99)
        b = random.randint(10, 99)
    elif player.condition == "ODD":
        a = random.randint(5, 49) * 2 + 1
        b = random.randint(5, 49) * 2 + 1
    elif player.condition == "EVEN":
        a = random.randint(5, 49) * 2
        b = random.randint(5, 49) * 2

    expr = f"{a} + {b}"
    solution = a + b

    options = [
        solution,
        solution + 10,
        solution - 10,
        random.randint(solution - 10, solution + 10),
    ]
    random.shuffle(options)

    return Trial.create(
        player=player,
        iteration=iteration,
        expression=expr,
        solution=solution,
        option_1=options[0],
        option_2=options[1],
        option_3=options[2],
        option_4=options[3],
    )


def get_trials(player: Player):
    # NB: this relies on preserving order of creation to match iterations
    return Trial.filter(player=player)


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "expression": trial.expression,
        "options": {
            1: trial.option_1,
            2: trial.option_2,
            3: trial.option_3,
            4: trial.option_4,
        },
    }


def evaluate_responses(player: Player, answers: list):
    player.trials_completed = len(answers)

    # NB: this cuts trials list in case of less answer
    for trial, answer in zip(get_trials(player), answers):
        evaluate_response(trial, answer)


def evaluate_response(trial: Trial, answer: int):
    choices = [
        trial.option_1,
        trial.option_2,
        trial.option_3,
        trial.option_4,
    ]
    assert answer in choices

    trial.answer = answer
    trial.choice = choices.index(trial.answer) + 1
    trial.success = trial.answer == trial.solution
    trial.score = C.SCORE_SUCCESS if trial.success else C.SCORE_FAILURE
    trial.status = "COMPLETED"


def set_payoff(player: Player):
    player.total_score = sum(t.score for t in get_trials(player))
    player.payoff = max(0, player.total_score) * player.session.config["real_world_currency_per_point"]


#### PAGES ####


class Intro(Page):
    pass


class Main(Page):
    form_model = "player"
    form_fields = ["answers"]

    timeout_seconds = C.PAGE_TIMEOUT

    @staticmethod
    def js_vars(player: Player):
        return {
            "C": dict(vars(C)),
            "TRIALS": {t.iteration: output_trial(t) for t in get_trials(player)},
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        answers = list(map(int, player.answers.split(";")))
        evaluate_responses(player, answers)
        set_payoff(player)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return {
            "completed": player.trials_completed,
            "solved": len(Trial.filter(player=player, success=True)),
            "failed": len(Trial.filter(player=player, success=False)),
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
        "trial.expression",
        "trial.solution",
        "trial.options.1",
        "trial.options.2",
        "trial.options.3",
        "trial.options.4",
        "trial.choice",
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
            player.trials_completed,
            player.total_score,
        ]

        for trial in Trial.filter(player=player):
            yield player_fields + [
                trial.iteration,
                trial.status,
                trial.expression,
                trial.solution,
                trial.option_1,
                trial.option_2,
                trial.option_3,
                trial.option_4,
                trial.choice,
                trial.answer,
                trial.success,
                trial.score,
            ]
