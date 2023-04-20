from otree.models import Participant

def last_page_time(participant: Participant):
    """Returns time spent on last page, in seconds
    Should be called in before_next_page
    """
    return participant._last_request_timestamp - participant._last_page_timestamp


def tracktime(cls):
    """Adds tracking functionality to a page
    Passes time_spent arg to before_next_page
    """
    orig_before_next = getattr(cls, 'before_next_page')
    if orig_before_next:
        def tracking_before_next(player, timeout_happened):
            time_spent = last_page_time(player.participant)
            orig_before_next(player, timeout_happened, time_spent)
        cls.before_next_page = staticmethod(tracking_before_next)

    return cls
