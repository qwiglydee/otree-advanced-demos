from otree.api import *

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "voting"
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1

    CHOICES = ["Foo", "Bar", "Baz"]
    PAGE_TIMEOUT = 600


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    decision = models.StringField(chocie=C.CHOICES, initial="")
    consensus = models.BooleanField(initial=False)


def get_votes(group: Group):
    """return non-null votes as dictionary"""
    return {
        p.id_in_group: p.vote
        for p in group.get_players()
        if p.field_maybe_none("vote") is not None
    }


class Player(BasePlayer):
    vote = models.StringField(chocie=C.CHOICES)


def evaluate_votes(player, vote):
    player.vote = vote
    group = player.group

    voting = get_votes(group)
    voted = list(voting.keys())
    votes = set(voting.values())

    if len(voted) == C.PLAYERS_PER_GROUP and len(votes) == 1:
        group.consensus = True
        group.decision = votes.pop()


# PAGES


def output_votes(group: Group):
    return {
        "votes": [{"player": f"Player {p}", "choice": c} for p, c in get_votes(group).items()],
        "consensus": group.consensus,
    }


class Intro(Page):
    pass


class Wait(WaitPage):
    pass


@live_page
class Main(Page):
    timeout_seconds = C.PAGE_TIMEOUT

    @staticmethod
    def vars_for_template(player: Player):
        return {"options": enumerate(C.CHOICES)}

    @staticmethod
    def live_load(player: Player, _):
        """send votes to a reloaded page"""
        yield "votes", output_votes(player.group)

    @staticmethod
    def live_vote(player: Player, payload: str):
        evaluate_votes(player, payload)

        yield player.group, "votes", output_votes(player.group)
        yield player.group, "chat", {"player": player.id_in_group, "vote": player.vote}

    @staticmethod
    def live_chat(player: Player, payload: str):
        yield player.group, "chat", {"player": player.id_in_group, "text": payload}


class Results(Page):
    pass


page_sequence = [
    Intro,
    Wait,
    Main,
    Results,
]
