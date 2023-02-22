import random
from otree.api import *

from utils.live_utils import live_page, live_method


class C(BaseConstants):
    NAME_IN_URL = 'trials_stream'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    MAX_FAILURES = 3  # number of failures to stop trials
    TRIAL_DELAY = 1000  # ms
    PAGE_TIMEOUT = 60  # sec


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    total_trials = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)
    total_fails = models.IntegerField(initial=0)


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)
    question = models.StringField()
    solution = models.IntegerField()

    response = models.IntegerField()
    response_time = models.IntegerField()
    success = models.BooleanField()
    score = models.IntegerField()

    @classmethod
    def select(cls, player: Player, **kwargs):
        "select all trials for the player, matching kwargs"
        return cls.filter(player=player, **kwargs)

    @classmethod
    def select1(cls, player: Player, **kwargs):
        "select single trial for the player, matching kwargs"
        trials = cls.filter(player=player, **kwargs)
        if len(trials) == 0:
            return None
        return trials[0]

    @property
    def completed(self):
        "the property is true when the trial is already answered/completed"
        return self.response is not None

    def validate(self):
        "check if given response is correct and update fields"
        self.success = (self.solution == self.response)
        self.score = int(self.success)  # 1pt for success


def generate_trial(player: Player, i):
    """create single trial with random numbers"""
    number_a = random.randint(11, 99)
    number_b = random.randint(11, 99)
    result = number_a + number_b

    return Trial.create(
        player=player,
        iteration=i,
        question=f"{number_a} + {number_b}",
        solution=result,
    )


def generate_trials(player: Player):
    """pregenerate all trials for the player"""
    return [generate_trial(player, i+1) for i in range(C.NUM_TRIALS)]


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        pass


def calc_results(player: Player):
    """calculate player payoff"""
    player.payoff = cu(player.total_score)


#### data for js_vars and live messages

def format_trial(trial: Trial):
    """convert the trial into data for a page"""
    # only return question
    return {'question': str(trial.question)}


def format_feedback(trial):
    return {
        'success': trial.success,
        'score': trial.score
    }

def format_progress(player, **kwargs):
    data = {
        'completed': player.total_trials,
        'failed': player.total_fails,
        'score': player.total_score
    }
    data.update(kwargs)
    return data


#### PAGES


class Intro(Page):
    pass


@live_page
class Main(Page):
    """A live page to iterate trials
    It communicates progress, trial, response and feedback

    Scheme of work:
    - player.total_trials indicate number of trials completed so far, initially 0
    - js_vars provide currently completed trials and gained score

    - client requests 'iteration'
    - server generates new trials and sends them via `trial` message
    - server also sends an update of iteration via `progress` message
    - if server decides to stop the iteration, the progress message includes flag `completed`

    - client sends `response` messages, including curent iteration
    - server checks if state of iteration matches on server and client
    - server validates and saves response and increments total_trials
    - server sends `feedback` so that client can complete trial and continue iteration loop
    - server also sends 'progress' message with update of completed trials and total score

    - if the page reloads, the process starts from current saved state
    """
    timeout_seconds = C.PAGE_TIMEOUT

    @staticmethod
    def js_vars(player: Player):
        # restoring any stalled unanswered trial
        trial = Trial.select1(player, iteration=player.total_trials+1)
        if trial is not None and trial.completed:
            trial = None

        return {
            'trial_delay': C.TRIAL_DELAY,
            'current': {
                'completed': player.total_trials,
                'failed': player.total_fails,
                'score': player.total_score,
                'current': trial.iteration if trial else player.total_trials,
                'trial': format_trial(trial) if trial else None
            }
        }

    @live_method('iterate')
    def on_iteration(player: Player, data):
        next_iteration = player.total_trials+1
        trial = Trial.select1(player, iteration=next_iteration)
        if trial is not None:
            raise RuntimeError("Iterating over existing trial")

        if player.total_fails == C.MAX_FAILURES:
            yield "progress", format_progress(player, gameover=True)
            return

        trial = generate_trial(player, next_iteration)

        yield "progress", format_progress(player, current=trial.iteration)
        yield "trial", format_trial(trial)

    @live_method('response')
    def handle_response(player: Player, data: dict):
        curr_iteration = player.total_trials + 1

        if data['iteration'] != curr_iteration:
            raise RuntimeError("Iteration mismatch")

        trial = Trial.select1(player, iteration=data['iteration'])

        if trial is None:
            raise RuntimeError("Missing trial")

        if trial.response is not None:
            raise RuntimeError("Trial already responded")

        trial.response = data["response"]
        trial.response_time = data["response_time"]
        trial.validate()

        yield "feedback", format_feedback(trial)

        player.total_score += trial.score
        player.total_trials += 1
        if trial.success is False:
            player.total_fails += 1

        yield "progress", format_progress(player)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        calc_results(player)


class Results(Page):
    pass


page_sequence = [Intro, Main, Results]


def custom_export(players):
    yield [
        "session",
        "participent.code",
        "participent.label",
        #
        "iteration",
        "question",
        "solution",
        "response",
        "time",
        "success",
        "score"
    ]

    for player in players:
        player_fields = [
            player.session.code,
            player.participant.code,
            player.participant.label,
        ]
        for trial in Trial.select(player):
            yield player_fields + [
                trial.iteration,
                trial.question,
                trial.solution,
                trial.response,
                trial.response_time,
                trial.success,
                trial.score
            ]
