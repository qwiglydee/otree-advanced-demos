""" Simple demo app

Trials are numeric expressions like "NN + NN".
An answer is given in text input.
Score is calculated as number of correct answers.

Iteration loop runs on server, it communicates progress, trials, responses, feedback.
Correct answers are not revieled onto page in any way.
Responses are saved into database per-trial and can be exported using 'custom export'.
"""
import random

from otree.api import *
from utils.live_utils import live_page, live_method


class C(BaseConstants):
    NAME_IN_URL = 'trials_live'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NUM_TRIALS = 5
    
    TRIAL_DELAY = 500 # delay in ms at the end of trial 


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    current_iter = models.IntegerField(initial=0)

    total_score = models.IntegerField()


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
    def generate(cls, player: Player, iteration: int):
        """create single trial with random numbers"""
        number_a = random.randint(11, 99)
        number_b = random.randint(11, 99)
        result = number_a + number_b

        return Trial.create(
            player=player,
            iteration=iteration,
            question=f"{number_a} + {number_b}",
            solution=result,
        )

    def validate(self):
        "checks if response is correct"""
        self.success = (self.solution == self.response)  # boolean
        self.score = int(self.success)  # int

    @classmethod
    def select(cls, player: Player, **kwargs):
        "select all trials for the player"
        return cls.filter(player=player, **kwargs)

    @classmethod
    def select1(cls, player: Player, **kwargs):
        "select one trial for the player"
        [trial] = cls.filter(player=player, **kwargs)
        return trial


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        generate_trials(player)
        player.total_score = 0


def generate_trials(player: Player):
    """pregenerate all trials for the player"""
    return [Trial.generate(player, i+1) for i in range(C.NUM_TRIALS)]


def format_trial(trial):
    """convert the trial into data for a page"""
    # only return question
    return dict(
        question=trial.question,
    )

# PAGES

class Intro(Page):
    pass


@live_page
class Main(Page):

    @staticmethod
    def js_vars(player: Player):
        ## restore current state
        if player.current_iter > 0:
            trial = Trial.select1(player, iteration=player.current_iter)
            current = dict(
                total_score=player.total_score,
                iteration=player.current_iter, 
                trial=format_trial(trial)
            )
        else:
            current = None

        return dict(
            num_trials=C.NUM_TRIALS,
            trial_delay=C.TRIAL_DELAY,
            current=current
        )

    @live_method('iterate')
    def handle_iteration(player: Player, data: dict):
        """move to next iteration and return progress and trial"""
        if player.current_iter > 0:
            current_trial = Trial.select1(player, iteration=player.current_iter)
            if current_trial.success is None:
                raise RuntimeError("Client skips iteration")

        if player.current_iter == C.NUM_TRIALS:
            yield "progress", dict(iteration=player.current_iter, completed=True)
            return

        player.current_iter += 1
        trial = Trial.select1(player, iteration=player.current_iter)

        yield "progress", dict(iteration=player.current_iter)
        yield "trial", format_trial(trial)


    @live_method('response')
    def handle_response(player: Player, data: dict):
        """process player's response and return feedback """

        trial = Trial.select1(player, iteration=data['iter'])

        if trial.score is not None:
            raise RuntimeError("Client responds to an already responded iteration")

        trial.response = data['response']
        trial.response_time = data['response_time']
        trial.validate()
        player.total_score += trial.score

        yield "feedback", dict(success=trial.success, score=trial.score, total_score=player.total_score)


class Results(Page):
    pass


page_sequence = [Intro, Main, Results]


def custom_export(players):
    yield [
        "participant.code",
        "session.code",
        "iteration",
        "question",
        "solution",
        "response",
        "response_time",
        "success",
        "score"
    ]

    for player in players:
        player_fields = [
            player.participant.code,
            player.session.code,
        ]

        for trial in Trial.select(player):
            yield player_fields + [
                trial.iteration,
                trial.question,
                trial.solution,
                trial.response,
                trial.response_time,
                trial.success,
                trial.score,
            ]