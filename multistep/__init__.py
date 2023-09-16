import random

from otree.api import *

from utils.live_utils import live_page


class C(BaseConstants):
    NAME_IN_URL = "multistep"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = 10  # total number of trials to generate
    MAX_FAILURES = 5  # num of failures (not counting retries) to abort the game
    TASKS_TIMEOUT = 600  # total time limit for tasks (s)
    FEEDBACK_DELAY = 3000  # pause (ms) after feedback
    RETRY_DELAY = 1000  # pause (ms) after failed retry
    SCORE_SUCCESS = +1
    SCORE_FAILURE = -1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    trials_completed = models.IntegerField(initial=0)
    trials_solved = models.IntegerField(initial=0)
    trials_failed = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)

    terminated = models.BooleanField(initial=False)

    @property
    def current_iter(self):
        "current iteration is always 1 forward of completed"
        return self.trials_completed + 1


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)

    # task fields
    expression = models.StringField()
    solution = models.IntegerField()
    choice_1 = models.IntegerField()
    choice_2 = models.IntegerField()
    choice_3 = models.IntegerField()
    choice_4 = models.IntegerField()

    # response fields
    choice = models.IntegerField()     # position
    response = models.IntegerField()   # value
    confidence = models.IntegerField(min=1, max=5)
    response_time = models.IntegerField()

    # status fields
    completed = models.BooleanField()
    success = models.BooleanField()
    score = models.IntegerField(initial=0)

    @property
    def partial(self):
        "indicate that the trial is partially answered"
        return not self.completed and (self.response is not None or self.confidence is not None)


def generate_trial(player: Player, iteration: int):
    """generate single trial of the task"""
    a = random.randint(11, 99)
    b = random.randint(11, 99)
    expr = f"{a} + {b}"
    solution = a + b

    choices = [
        solution,
        solution + 10,
        solution - 10,
        random.randint(solution - 10, solution + 10),
    ]
    random.shuffle(choices)

    return Trial.create(
        player=player,
        iteration=iteration,
        expression=expr,
        solution=solution,
        choice_1=choices[0],
        choice_2=choices[1],
        choice_3=choices[2],
        choice_4=choices[3],
    )


def generate_trials(player: Player):
    return [generate_trial(player, i) for i in range(1, 1 + C.NUM_TRIALS)]


def current_trial(player: Player):
    """retrieve current trial"""
    trials = Trial.filter(player=player, iteration=player.current_iter)
    assert len(trials) == 1
    return trials[0]


def evaluate_trial(trial: Trial):
    """evaluate trial status and score
    using already answered trial
    """
    assert trial.response is not None

    trial.success = trial.response == trial.solution
    if trial.success:
        trial.score = C.SCORE_SUCCESS
    else:
        trial.score = C.SCORE_FAILURE

    trial.completed = trial.response is not None and trial.confidence is not None


def update_progress(player: Player, trial: Trial):
    """update players progress
    using last responded trial
    """
    assert trial.completed

    player.total_score += trial.score
    player.total_score = max(0, player.total_score)

    player.trials_completed += 1
    if trial.success:
        player.trials_solved += 1
    else:
        player.trials_failed += 1

    player.terminated = player.trials_completed == C.NUM_TRIALS or player.trials_failed == C.MAX_FAILURES


#### INIT ####


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player)


def init_player(player: Player):
    generate_trials(player)


def set_payoff(player: Player):
    """calculate final payoff"""
    player.payoff = player.total_score * player.session.config["real_world_currency_per_point"]


#### FORMAT ####


def output_progress(player: Player):
    return {
        "completed": player.trials_completed,
        "score": player.total_score,
    }


def output_trial(trial: Trial):
    return {
        "iteration": trial.iteration,
        "expression": trial.expression,
        "choices": {
            1: trial.choice_1,
            2: trial.choice_2,
            3: trial.choice_3,
            4: trial.choice_4,
        },
        # possible partial inputs
        "choice": trial.choice,
        "response": trial.response,
        "confidence": trial.confidence,
    }


def output_feedback(trial: Trial):
    if trial.completed:
        return {
            "solution": trial.solution,
            "success": trial.success,
            "score": trial.score,
            "completed": trial.completed,
        }
    else:
        return {
            "completed": False,
        }


#### PAGES ####


class Intro(Page):
    pass


@live_page
class Tasks(Page):
    """Live page with series of trials"""

    timeout_seconds = C.TASKS_TIMEOUT

    @staticmethod
    def js_vars(player: Player):
        return {
            "feedback_delay": C.FEEDBACK_DELAY,
            "retry_delay": C.RETRY_DELAY,
        }


    @staticmethod
    def live_start(player: Player, data):
        "send inital (restored) state"

        yield "progress", output_progress(player)

        if player.terminated:
            yield "terminate"
            return

        trial = current_trial(player)
        yield "trial", output_trial(trial)


    @staticmethod
    def live_next(player: Player, data):
        "send next (or current) trial"
        yield "progress", output_progress(player)

        if player.terminated:
            yield "terminate"
            return

        trial = current_trial(player)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_response(player: Player, data: dict):
        "handle response from player"
        assert not player.terminated
        assert data["iteration"] == player.current_iter

        trial = current_trial(player)

        if "response" in data:
            assert trial.response is None
            trial.choice = data["choice"]
            trial.response = data["response"]
            trial.response_time = data["time"]
        if "confidence" in data:
            assert trial.confidence is None
            trial.confidence = data["confidence"]

        evaluate_trial(trial)
        yield "feedback", output_feedback(trial)

        if trial.completed:
            update_progress(player, trial)
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
    Tasks,
    Results,
]


def custom_export(players: list[Player]):
    yield [
        "session.code",
        "participant.code",
        #
        "player.trials_completed",
        "player.trials_solved",
        "player.trials_failed",
        "player.total_score",
        #
        "trial.iteration",
        "trial.expression",
        "trial.solution",
        "trial.response_time",
        "trial.response",
        "trial.success",
        "trial.score",
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            #
            player.trials_completed,
            player.trials_solved,
            player.trials_failed,
            player.total_score,
        ]
        for trial in Trial.filter(player=player):
            yield player_fields + [
                trial.iteration,
                trial.expression,
                trial.solution,
                trial.response_time,
                trial.response,
                trial.success,
                trial.score,
            ]
