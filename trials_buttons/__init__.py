import random
from otree.api import *

from utils.live_utils import live_page, live_method


class C(BaseConstants):
    NAME_IN_URL = 'trials_buttons'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NUM_TRIALS = 5
    TRIAL_DELAY = 1000  # ms
    PAGE_TIMEOUT = 300  # sec

    CHOICES = ['A', 'B', 'C']


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    total_trials = models.IntegerField(initial=0)
    total_score = models.IntegerField(initial=0)
    layout = models.StringField()  # description of buttons layout like "ABC", "CBA"


class Trial(ExtraModel):
    player = models.Link(Player)
    iteration = models.IntegerField(min=1)
    question = models.StringField()
    solution = models.IntegerField()

    layout = models.StringField()
    choice_a = models.IntegerField()
    choice_b = models.IntegerField()
    choice_c = models.IntegerField()

    choice = models.StringField()
    position = models.StringField()
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

    @property
    def choices(self):
        "represents choices as dictionary for convenience"
        return {
            'A': self.choice_a,
            'B': self.choice_b,
            'C': self.choice_c,
        }

    def validate(self):
        "check if given response is correct and update fields"
        self.response = self.choices[self.choice]
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
        layout=player.layout,
        choice_a=result-10,
        choice_b=result,
        choice_c=result+10
    )


def generate_trials(player: Player):
    """pregenerate all trials for the player"""
    return [generate_trial(player, i+1) for i in range(C.NUM_TRIALS)]


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        player.layout = "".join(random.sample(C.CHOICES, k=3))
        generate_trials(player)


def calc_results(player: Player):
    """calculate player payoff"""
    player.payoff = cu(player.total_score)


# data for js_vars and live messages

def format_trial(trial: Trial):
    """convert the trial into data for a page"""
    # only return question
    return {
        'question': str(trial.question),
        'choices': trial.choices
    }


def format_trials(trials: list[Trial]):
    """dictionary of formatted trials indexed by iter number"""
    return {t.iteration: format_trial(t) for t in trials}


def format_feedback(trial):
    return {
        'success': trial.success,
        'score': trial.score
    }


def format_progress(player, **kwargs):
    data = {
        'completed': player.total_trials,
        'score': player.total_score
    }
    data.update(kwargs)
    return data

# PAGES


class Intro(Page):
    pass


@live_page
class Main(Page):
    """A live page to iterate trials
    It communicates response, feedback and progress
    Scheme of work is the same as trials_live.
    """

    timeout_seconds = C.PAGE_TIMEOUT

    @staticmethod
    def js_vars(player: Player):
        return {
            'trials': format_trials(Trial.select(player)),
            'num_trials': C.NUM_TRIALS,
            'trial_delay': C.TRIAL_DELAY,
            'layout': player.layout,
            'current': {
                'completed': player.total_trials,
                'score': player.total_score,
            }
        }

    @live_method('response')
    def handle_response(player: Player, data: dict):
        if data['iteration'] != player.total_trials + 1:
            raise RuntimeError("Iteration mismatch")

        trial = Trial.select1(player, iteration=data['iteration'])

        if trial is None:
            raise RuntimeError("Missing trial")

        if trial.completed:
            raise RuntimeError("Trial already responded")

        trial.choice = data["response"]["choice"]
        trial.position = data["response"]["position"]
        trial.response = data["response"]["value"]
        trial.response_time = data["response_time"]
        trial.validate()

        yield "feedback", format_feedback(trial)

        player.total_score += trial.score
        player.total_trials += 1

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
        "layout",
        "A",
        "B",
        "C",
        "choice",
        "position",
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
                trial.layout,
                trial.choice_a,
                trial.choice_b,
                trial.choice_c,
                trial.choice,
                trial.position,
                trial.response,
                trial.response_time,
                trial.success,
                trial.score
            ]
