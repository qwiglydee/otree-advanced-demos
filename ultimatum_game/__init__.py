from otree.api import *

from utils.live import live_page


class C(BaseConstants):
    NAME_IN_URL = "ultimatum_game"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    SCREENER_APP = "ultimatum_screener"
    SCREENER_FIELDS = ["gender", "age"]

    ENDOWMENT = 100
    GAME_TIMEOUT = 60

    PROPOSER_ROLE = "Proposer"
    RECEIVER_ROLE = "Receiver"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    stage = models.StringField(initial="NEW", choices=["STARTING", "PROPOSING", "DECIDING", "COMPLETED"])
    dropped = models.BooleanField(initial=False)
    completed = models.BooleanField(initial=False)

    endowment = models.IntegerField()
    proposal = models.IntegerField()
    decision = models.StringField(choices=["ACCEPT", "REJECT"])

    @property
    def proposer(self):
        return self.get_player_by_role(C.PROPOSER_ROLE)

    @property
    def receiver(self):
        return self.get_player_by_role(C.RECEIVER_ROLE)

    def init(group, config):
        group.endowment = C.ENDOWMENT


def get_bonus(group: Group):
    decision = group.field_maybe_none("decision")

    if decision == "ACCEPT":
        return {
            C.PROPOSER_ROLE: group.endowment - group.proposal,
            C.RECEIVER_ROLE: group.proposal,
        }
    elif decision == "REJECT":
        return {C.PROPOSER_ROLE: 0, C.RECEIVER_ROLE: 0}
    else:
        return None


class Player(BasePlayer):
    gender = models.StringField()
    age = models.IntegerField()

    checkin = models.BooleanField(initial=False)
    response_time = models.IntegerField()

    def get_adjacent_player(player, app_name):
        [screener_player] = [p for p in player.participant.get_players() if p.get_folder_name() == app_name]
        return screener_player

    def init(player, config):
        screener_player = player.get_adjacent_player(C.SCREENER_APP)
        for fld in C.SCREENER_FIELDS:
            setattr(player, fld, getattr(screener_player, fld))


def creating_session(subsession: BaseSubsession):
    # init is postponed until Gather page
    pass


def set_payoffs(group: Group):
    assert not group.dropped
    assert group.stage == "COMPLETED"

    rate = group.session.config["real_world_currency_per_point"]
    bonus = get_bonus(group)

    if bonus:
        group.proposer.payoff = bonus[C.PROPOSER_ROLE] * rate
        group.receiver.payoff = bonus[C.RECEIVER_ROLE] * rate


# I/O


def output_game(group: Group):
    return {
        "stage": group.stage,
        "endowment": group.endowment,
        "proposal": group.field_maybe_none("proposal"),
        "decision": group.field_maybe_none("decision"),
        "bonus": get_bonus(group),
    }


# PAGES


class Gather(WaitPage):
    group_by_arrival_time = True

    @staticmethod
    def after_all_players_arrive(group: Group):
        group.init(group.session.config)
        for player in group.get_players():
            player.init(group.session.config)


class Intro(Page):
    @staticmethod
    def vars_for_template(player: Player):
        [partner] = player.get_others_in_group()
        return {"partner": partner}


@live_page
class Main(Page):
    timeout_seconds = C.GAME_TIMEOUT

    @staticmethod
    def is_displayed(player: Player):
        return not player.group.dropped and not player.group.completed

    @staticmethod
    def js_vars(player: Player):
        return {"C": dict(vars(C)), "role": player.role}

    @staticmethod
    def live_start(player: Player, payload: None):
        group = player.group
        player.checkin = True

        checked = sum(p.checkin for p in group.get_players())
        if checked < C.PLAYERS_PER_GROUP:
            group.stage = "STARTING"
        else:
            group.stage = "PROPOSING"
        yield group, "game", output_game(group)

    @staticmethod
    def live_proposal(player: Player, payload: dict):
        group = player.group
        assert group.stage == "PROPOSING"

        assert isinstance(payload["proposal"], int)
        assert 0 <= payload["proposal"] <= C.ENDOWMENT
        assert isinstance(payload["time"], int)

        player.response_time = payload["time"]
        group.proposal = payload["proposal"]
        group.stage = "DECIDING"

        yield group, "game", output_game(group)

    @staticmethod
    def live_decision(player: Player, payload: dict):
        group = player.group
        assert group.stage == "DECIDING"

        assert isinstance(payload["decision"], str)
        assert payload["decision"] in ("ACCEPT", "REJECT")
        assert isinstance(payload["time"], int)

        player.response_time = payload["time"]
        group.decision = payload["decision"]
        group.stage = "COMPLETED"
        group.completed = True

        yield group, "game", output_game(group)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group

        group.dropped = timeout_happened or group.stage != "COMPLETED"

        if not group.dropped:
            set_payoffs(group)


class Failure(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.group.dropped


class Results(Page):
    pass


page_sequence = [
    Gather,
    Intro,
    Main,
    Failure,
    Results,
]
