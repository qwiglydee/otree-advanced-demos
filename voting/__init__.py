from otree.api import *

from utils.live_utils import live_page


class C(BaseConstants):
    NAME_IN_URL = "voting"
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    CHOICES = ["Foo", "Bar", "Baz"]
    VOTE_TEIMEOUT = 6000  # seconds for voting


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    decision = models.StringField(chocie=C.CHOICES, initial="")
    consensus = models.BooleanField(initial=False)
    # majority = models.BooleanField(initial=False)

    def get_votes(self):
        return { p.id_in_group: p.vote for p in self.get_players() if p.field_maybe_none('vote') is not None }


class Player(BasePlayer):
    vote = models.StringField(chocie=C.CHOICES)

    @property
    def name(self):
        return f"Player{self.id_in_group}"


def evaluate_votes(group):
    votes = group.get_votes()
    voted = list(votes.keys())
    voteset = set(votes.values())

    if len(voted) == C.PLAYERS_PER_GROUP and len(voteset) == 1:
        group.consensus = True
        group.decision = voteset.pop()

# PAGES


class Intro(Page):
    pass


class Wait(WaitPage):
    pass


@live_page
class Main(Page):
    timeout_seconds = C.VOTE_TEIMEOUT

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'options': enumerate(C.CHOICES)
        }

    @staticmethod
    def live_chat(player: Player, data: dict):
        # broadcast the message to all the group
        yield "all", "chat", {"player": player.name, "text": data["text"]}

    @staticmethod
    def live_vote(player: Player, data: dict):
        group = player.group

        # save the vote
        player.vote = data['vote']

        evaluate_votes(group)

        yield "all", "votes", group.get_votes()
        yield "all", "chat", { "player": player.name, "vote": player.vote }

        if group.consensus:
            yield "all", "terminate"


class Results(Page):
    pass


page_sequence = [
    Intro,
    Wait,
    Main,
    Results,
]
