import random

from otree.api import *

from utils.live_utils import live_page


class C(BaseConstants):
    NAME_IN_URL = "multistage"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NUM_TRIALS = 10  # total number of trials to generate
    MAX_FAILURES = 3  # num of failures to abort the game
    TASKS_TIMEOUT = 600  # total time limit for tasks (seconds)
    TRIAL_DELAY = 2000  # pause (ms) after trial
    RETRY_DELAY = 1000  # pause (ms) before retry
    SCORE_SUCCESS = +10
    SCORE_FAILURE = -10
    SCORE_SKIP = 0
    SCORE_REDUCE = -5

    STRATEGIES = ['choose', 'reduce', 'skip']


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


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)

    # task fields
    expression = models.StringField()
    solution = models.IntegerField()
    option_1 = models.IntegerField()
    option_2 = models.IntegerField()
    option_3 = models.IntegerField()
    option_4 = models.IntegerField()
    choices = models.StringField()

    # response fields
    strategy = models.IntegerField(choices=C.STRATEGIES)
    choice = models.IntegerField()     # position
    response = models.IntegerField()   # value
    response_time = models.IntegerField()

    # status fields
    completed = models.BooleanField()
    success = models.BooleanField()
    score = models.IntegerField(initial=0)

    def option(self, num):
        "get an option by number"
        options = (self.option_1, self.option_2, self.option_3, self.option_4)
        return options[num-1]

    def correct_choice(self):
        options = (self.option_1, self.option_2, self.option_3, self.option_4)
        return options.index(self.solution) + 1


def generate_trial(player: Player, iteration: int):
    """generate single trial of the task"""
    a = random.randint(11, 99)
    b = random.randint(11, 99)
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
        choices="1234",
    )

def reduce_trial(trial: Trial):
    answer = trial.correct_choice()
    reduced = random.sample([1, 2, 3, 4], k=2)
    if answer not in reduced:
        reduced[0] = answer

    trial.choices = "".join([str(r) for r in reduced])


def generate_trials(player: Player):
    return [generate_trial(player, i) for i in range(1, 1 + C.NUM_TRIALS)]


def current_trial(player: Player):
    """retrieve current trial"""
    assert player.trials_completed < C.NUM_TRIALS
    [trial] = Trial.filter(player=player, iteration=player.trials_completed + 1)
    return trial


def evaluate_trial(trial: Trial):
    """evaluate trial status and score
    using already answered trial
    """
    assert trial.response is not None

    trial.completed = True
    trial.success = trial.response == trial.solution

    # NB: success is None when skipped
    if trial.success is True:
        trial.score = C.SCORE_SUCCESS
    if trial.success is False:
        trial.score = C.SCORE_FAILURE

    if trial.strategy == 'reduce':
        trial.score += C.SCORE_REDUCE

    trial.completed = True


def evaluate_strategy(trial: Trial):
    assert trial.strategy is not None

    if trial.strategy == 'choose':
        return

    if trial.strategy == 'skip':
        trial.score = C.SCORE_SKIP
        trial.completed = True

    if trial.strategy == 'reduce':
        reduce_trial(trial)


def update_progress(player: Player, trial: Trial):
    """update players progress
    using last responded trial
    """
    assert trial.completed

    player.total_score += trial.score
    player.total_score = max(0, player.total_score)

    player.trials_completed += 1
    # NB: success is None when skipped
    if trial.success is True:
        player.trials_solved += 1
    if trial.success is False:
        player.trials_failed += 1

    player.terminated = player.trials_completed == C.NUM_TRIALS or player.trials_failed >= C.MAX_FAILURES


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
        "total": C.NUM_TRIALS,
        "completed": player.trials_completed,
        "score": player.total_score,
        "terminated": player.terminated,
    }


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
        "choices": tuple(trial.choices),
        # possible partial inputs
        "strategy": trial.strategy,
        "choice": trial.choice,
        "response": trial.response,
    }


def output_feedback(trial: Trial):
    if trial.completed:
        return {
            "solution": trial.solution,
            "success": trial.success,
            "score": trial.score,
            "completed": True,
        }
    else:
        return {
            'choices': tuple(trial.choices),
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
        return { 'C': dict(vars(C)) }

    @staticmethod
    def live_iter(player: Player, data):
        """retrieve current progress and trial"""

        yield "progress", output_progress(player)
        if not player.terminated:
            trial = current_trial(player)
            yield "trial", output_trial(trial)

    @staticmethod
    def live_strategy(player: Player, data: dict):
        assert not player.terminated

        trial = current_trial(player)

        assert data["iteration"] == trial.iteration
        assert trial.strategy is None
        trial.strategy = data["strategy"]

        evaluate_strategy(trial)

        yield "feedback", output_feedback(trial)

        if trial.completed:
            update_progress(player, trial)
            yield "progress", output_progress(player)

    @staticmethod
    def live_response(player: Player, data: dict):
        """handle response from player"""

        assert not player.terminated

        trial = current_trial(player)

        assert data["iteration"] == trial.iteration
        assert trial.response is None and trial.strategy is not None
        trial.response_time = data["time"]
        trial.choice = data["choice"]
        trial.response = trial.option(trial.choice)

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
        "trial.options.1",
        "trial.options.2",
        "trial.options.3",
        "trial.options.4",
        "trial.choices",
        "trial.response_time",
        "trial.strategy",
        "trial.choice",
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
                trial.option_1,
                trial.option_2,
                trial.option_3,
                trial.option_4,
                trial.choices,
                trial.response_time,
                trial.strategy,
                trial.choice,
                trial.response,
                trial.success,
                trial.score,
            ]
