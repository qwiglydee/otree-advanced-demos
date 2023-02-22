import random
from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'trials_form'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NUM_TRIALS = 5
    TRIAL_DELAY = 1000
    PAGE_TIMEOUT = 30


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    total_trials = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)
    total_time = models.FloatField(initial=0)
    #
    answers = models.StringField()  # semicolon-joined answers
    expected = models.StringField()  # semicolon-joined correct answers


def decode_answers(joined):
    "decoding semicolon-joined answers"
    return list(map(int, joined.split(";")[:-1]))


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)
    question = models.StringField()
    solution = models.IntegerField()

    @classmethod
    def select(cls, player: Player, **kwargs):
        "select all trials for the player"
        return cls.filter(player=player, **kwargs)


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
        trials = generate_trials(player)
        player.expected = "".join(f"{t.solution};" for t in trials)


def calc_results(player):
    """calculate player score and payoff"""
    given = decode_answers(player.answers)
    correct = decode_answers(player.expected)
    matched = sum(a == b for a, b in zip(given, correct))  # compare pairwize and summarize 'true' values
    player.total_trials = len(given)
    player.total_score = matched
    player.payoff = player.total_score


def format_trial(trial):
    """convert the trial into data for a page"""
    # only return question
    return dict(question=trial.question)

def format_trials(trials):
    """dictionary of formatted trials indexed by iter number"""
    return  {t.iteration: format_trial(t) for t in trials }


# PAGES


class Intro(Page):
    pass


class Main(Page):
    """A form page to iterate trials

    Scheme of work:
    - trials should be pregenerated in advance (and numbered from 1)
    - trials data is provided to the client side via js_vars
    - on-page scripts iterate over the trials and save responses to hidden fields
    """

    form_model = "player"
    form_fields = ["answers", "total_time"]
    timeout_seconds = C.PAGE_TIMEOUT

    @staticmethod
    def js_vars(player: Player):
        trials = Trial.select(player)
        return {
            'trials': format_trials(trials),
            'num_trials': C.NUM_TRIALS,
            'trial_delay': C.TRIAL_DELAY
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.total_time = C.PAGE_TIMEOUT
        calc_results(player)


class Results(Page):
    pass


page_sequence = [Intro, Main, Results]
