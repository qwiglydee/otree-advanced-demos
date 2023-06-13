from otree.api import *

from utils.live_utils import live_page, live_method


class C(BaseConstants):
    NAME_IN_URL = "voting"
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    CHOICES = ["A", "B", "C"]
    VOTE_TEIMEOUT = 60  # seconds for voting


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    decision = models.StringField(chocie=C.CHOICES, initial="")
    consensus = models.BooleanField(initial=False)
    # majority = models.BooleanField(initial=False)

    def get_votes(self):
        return { p.id: p.vote for p in self.get_players() }


def evaluate_votes(group):
    votes = [p.vote for p in group.get_players() if p.vote != ""]
    if len(votes) != C.PLAYERS_PER_GROUP:
        return

    votes = set(votes)
    if len(votes) == 1:
        group.consensus = True
        group.decision = votes.pop()


class Player(BasePlayer):
    vote = models.StringField(chocie=C.CHOICES, initial="")

    @property
    def name(self):
        return f"Player{self.id_in_group}"


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
            'options': enumerate(C.CHOICES)  # need them to have index
        }

    @live_method("message")
    def handle_message(player: Player, data: dict):
        # broadcast the message to all the group
        yield player.group, "message", {"player": player.name, "text": data["text"]}

    @live_method("vote")
    def handle_vote(player: Player, data: dict):
        group = player.group

        # save the vote
        player.vote = data['vote']

        evaluate_votes(group)

        # broadcast new votes to the group
        yield group, "votes", group.get_votes()

        # also send a massage to the chat
        yield group, "message", { "player": player.name, "text": f"* votes: {player.vote}" }

        if group.consensus:
            yield group, "complete"


class Results(Page):
    pass


page_sequence = [
    Intro,
    Wait,
    Main,
    Results,
]
