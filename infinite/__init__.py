import random

from otree.api import *

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "infinite"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ['ODD', 'EVEN', 'MIXED']

    MAX_FAILURES = 5  # num of failures to abort the game

    PAGE_TIMEOUT = 300  # total time limit for tasks page (seconds)
    FEEDBACK_DELAY = 2000  # time (ms) to show feedback before next trial

    SCORE_SUCCESS = +10
    SCORE_FAILURE = -1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    condition = models.StringField()
    trials_played = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)
    terminated = models.BooleanField(initial=False)


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)
    # status fields
    status = models.StringField(choices=['NEW', 'LOADED', 'COMPLETED'], initial='NEW')
    success = models.BooleanField(initial=None)
    score = models.IntegerField(initial=0)
    # task fields
    expression = models.StringField()
    solution = models.IntegerField()
    # response fields
    response_time = models.IntegerField()
    answer = models.IntegerField()


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player, subsession.session.config)


def init_player(player: Player, config: dict):
    player.condition = random.choice(C.CONDITIONS)
    if 'condition' in config and config['condition'] != 'random':
        assert config['condition'] in C.CONDITIONS
        player.condition = config['condition']


def set_payoff(player: Player):
    """calculate final payoff"""
    player.payoff = player.total_score * player.session.config["real_world_currency_per_point"]


def generate_trial(player: Player, iteration: int):
    """generate single trial of the task"""

    if player.condition == 'MIXED':
        a = random.randint(10, 99)
        b = random.randint(10, 99)
    elif player.condition == 'ODD':
        a = random.randint(5, 49) * 2 + 1
        b = random.randint(5, 49) * 2 + 1
    elif player.condition == 'EVEN':
        a = random.randint(5, 49) * 2
        b = random.randint(5, 49) * 2

    expr = f"{a} + {b}"
    solution = a + b

    return Trial.create(
        player=player,
        iteration=iteration,
        expression=expr,
        solution=solution,
    )


def evaluate_response(trial: Trial, response: dict):
    """evaluate response and update trial status and score, return feedback"""
    assert response["iteration"] == trial.iteration
    assert isinstance(response["answer"], int)

    answer = response["answer"]

    trial.answer = answer
    trial.success = trial.answer == trial.solution

    if trial.success:
        trial.score = C.SCORE_SUCCESS
    else:
        trial.score = C.SCORE_FAILURE

    trial.status = 'COMPLETED'

    return {
        "solution": trial.solution,
        "success": trial.success,
        "score": trial.score,
    }


def update_progress(player: Player, feedback: dict):
    """update players progress using last feedback"""
    player.trials_played += 1
    player.total_score += feedback['score']
    player.total_score = max(0, player.total_score)

    trials_failed = len(Trial.filter(player=player, success=False))
    player.terminated = trials_failed >= C.MAX_FAILURES


def current_trial(player: Player):
    """retrieve current trial"""
    trials = Trial.filter(player=player, iteration=player.trials_played + 1)
    return trials[0] if trials else None


def next_trial(player: Player):
    """generate next trial"""
    return generate_trial(player, player.trials_played + 1)


#### FORMAT ####


def output_progress(player: Player):
    return {
        "played": player.trials_played,
        "score": player.total_score,
        "terminated": player.terminated,
    }


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "expression": trial.expression,
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
        return { 'C': dict(vars(C)) }

    @staticmethod
    def live_iter(player: Player, _):
        """retrieve current progress and trial"""
        # detect reloading of incomplete tasks
        trial = current_trial(player)
        if trial is not None and trial.status == 'LOADED':
            raise RuntimeError("Page reloading is prohibited")

        trial = next_trial(player)
        trial.status = 'LOADED'

        yield "progress", output_progress(player)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_response(player: Player, payload: dict):
        """handle response from player"""
        trial = current_trial(player)
        assert trial is not None

        trial.response_time = payload["time"]
        feedback = evaluate_response(trial, payload)
        update_progress(player, feedback)

        yield "progress", output_progress(player)
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
            'played': player.trials_played,
            'solved': len(Trial.filter(player=player, success=True)),
            'failed': len(Trial.filter(player=player, success=False)),
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
        "player.trials_played",
        "player.total_score",
        #
        "trial.iteration",
        "trial.status",
        "trial.expression",
        "trial.solution",
        "trial.response_time",
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
            player.trials_played,
            player.total_score,
        ]
        for trial in Trial.filter(player=player):
            yield player_fields + [
                trial.iteration,
                trial.status,
                trial.expression,
                trial.solution,
                trial.response_time,
                trial.answer,
                trial.success,
                trial.score,
            ]
