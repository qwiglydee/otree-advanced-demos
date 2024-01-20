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
    decision = models.StringField(choices=C.CHOICES)
    consensus = models.BooleanField(initial=False)


class Player(BasePlayer):
    vote = models.StringField(choices=C.CHOICES)


def get_votes(group: Group):
    """all non-null votes as dict { player: vote }"""
    return {
        p.id_in_group: p.vote
        for p in group.get_players()
        if p.field_maybe_none('vote') is not None
    }


def output_votes(group: Group):
    return {
        "votes": [{"player": f"Player {p}", "vote": v} for p, v in get_votes(group).items()],
        "consensus": group.consensus,
    }


def evaluate_vote(player: Player, vote: str):
    assert vote in C.CHOICES

    player.vote = vote
    group = player.group

    voting = get_votes(group)
    voted_players = list(voting.keys())
    uniq_choices = set(voting.values())

    if len(voted_players) == C.PLAYERS_PER_GROUP and len(uniq_choices) == 1:
        group.consensus = True
        group.decision = uniq_choices.pop()


# PAGES


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
    def live_vote(player: Player, payload: str):
        evaluate_vote(player, payload)

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
