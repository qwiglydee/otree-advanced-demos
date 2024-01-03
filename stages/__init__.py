import random

from otree.api import *

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "stages"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CONDITIONS = ['ODD', 'EVEN', 'MIXED']

    NUM_TRIALS = 10  # total number of trials to generate
    MAX_FAILURES = 5  # num of failures to abort the game

    PAGE_TIMEOUT = 600  # total time limit for tasks page (seconds)
    FEEDBACK_DELAY = 2000  # time (ms) to show feedback before next trial

    DECISIONS = ['ANSWER', 'REDUCE', 'SKIP']

    SCORE_SUCCESS = +10
    SCORE_FAILURE = -10
    SCORE_REDUCE = -5
    SCORE_SKIP = -5


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
    option_1 = models.IntegerField()
    option_2 = models.IntegerField()
    option_3 = models.IntegerField()
    option_4 = models.IntegerField()
    options = models.StringField()

    # response fields
    decision_time = models.IntegerField()
    decision = models.StringField()
    answer_time = models.IntegerField()
    choice = models.IntegerField()
    answer = models.IntegerField()



def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        init_player(player, subsession.session.config)


def init_player(player: Player, config: dict):
    player.condition = random.choice(C.CONDITIONS)
    if 'condition' in config and config['condition'] != 'random':
        assert config['condition'] in C.CONDITIONS
        player.condition = config['condition']

    for i in range(C.NUM_TRIALS):
        generate_trial(player, i+1)


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
        options="1234"
    )

def reduce_trial(trial: Trial):
    """remove half of the options, keep correct one """
    options = [1, 2, 3, 4]
    correct = [trial.option_1, trial.option_2, trial.option_3, trial.option_4].index(trial.solution) + 1
    options.pop(correct-1)
    another = random.choice(options)
    options = [correct, another]
    trial.options = "".join(map(str, options))


def evaluate_decision(trial: Trial, response: dict):
    """evaluate first response"""
    assert response["iteration"] == trial.iteration
    assert response["decision"] in C.DECISIONS

    trial.decision = response["decision"]
    if trial.decision == 'SKIP':
        trial.status = 'COMPLETED'
        trial.score = C.SCORE_SKIP
        return {
            "success": trial.success,
            "score": trial.score,
        }
    elif trial.decision == 'REDUCE':
        reduce_trial(trial)


def evaluate_response(trial: Trial, response: dict):
    """evaluate second response and update trial status and score, return feedback"""
    assert response["iteration"] == trial.iteration
    assert isinstance(response["answer"], int)

    trial.answer = response["answer"]
    trial.choice = [trial.option_1, trial.option_2, trial.option_3, trial.option_4].index(trial.answer) + 1

    trial.success = trial.answer == trial.solution

    if trial.success:
        trial.score = C.SCORE_SUCCESS
    else:
        trial.score = C.SCORE_FAILURE

    if trial.decision == 'REDUCE':
        trial.score += C.SCORE_REDUCE

    trial.status = 'COMPLETED'

    return {
        "success": trial.success,
        "score": trial.score,
    }


def update_progress(player: Player, feedback: dict):
    """update players progress using last feedback"""
    player.trials_played += 1
    player.total_score += feedback['score']
    player.total_score = max(0, player.total_score)

    trials_failed = len(Trial.filter(player=player, success=False))
    player.terminated = player.trials_played == C.NUM_TRIALS or trials_failed >= C.MAX_FAILURES


def current_trial(player: Player):
    """retrieve current trial"""
    trials = Trial.filter(player=player, iteration=player.trials_played + 1)
    return trials[0] if trials else None



#### FORMAT ####


def output_progress(player: Player):
    return {
        "total": C.NUM_TRIALS,
        "played": player.trials_played,
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
        }
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
    def live_iter(player: Player, data):
        """retrieve current progress and trial"""
        trial = current_trial(player)
        assert trial is not None

        # detect reloading incomplete tasks
        if trial.status == 'LOADED':
            raise RuntimeError("Page reloading is prohibited")
        trial.status = 'LOADED'

        yield "progress", output_progress(player)
        yield "trial", output_trial(trial)

    @staticmethod
    def live_decision(player: Player, data: dict):
        """handle response from player"""
        trial = current_trial(player)
        assert trial is not None

        trial.decision_time = data["time"]

        feedback = evaluate_decision(trial, data)

        if feedback is not None:
            update_progress(player, feedback)
            yield "progress", output_progress(player)
            yield "feedback", feedback
        else:
            yield "options", { 'options': trial.options }


    @staticmethod
    def live_answer(player: Player, data: dict):
        """handle response from player"""
        trial = current_trial(player)
        assert trial is not None

        trial.answer_time = data["time"]

        feedback = evaluate_response(trial, data)
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
        "trial.options.1",
        "trial.options.2",
        "trial.options.3",
        "trial.options.4",
        "trial.available",
        "trial.decision_time",
        "trial.answer_time",
        "trial.decision",
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
            player.trials_played,
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
                trial.options,
                trial.decision_time,
                trial.answer_time,
                trial.decision,
                trial.choice,
                trial.answer,
                trial.success,
                trial.score,
            ]
