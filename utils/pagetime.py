""" Utils to track time spent on a page

USAGE:

from somewhere import pagetime

@pagetime.track
class SomePage(Page):
    @statitmethod
    def before_next_page(player, timeout_happened):
        player.time_somepage = pagetime.last(player.participant)  # time of the current page
        player.time_total = pagetime.total(player.participant)    # time from the beginning of session
"""
from time import time

def track(cls):
    """Adds tracking functionality to a page
    All tracking goes to participant.vars
    """
    orig_get = cls.get
    orig_post = cls.post

    def _tracking_get(page):
        now = int(time())
        page.participant.vars['_tracking_get_timestamp'] = now
        if '_tracking_first_timestamp' not in page.participant.vars:
            page.participant.vars['_tracking_first_timestamp'] = now
        if '_tracking_post_timestamp' in page.participant.vars:
            del page.participant.vars['_tracking_post_timestamp']
        return orig_get(page)

    def _tracking_post(page):
        page.participant.vars['_tracking_post_timestamp'] = int(time())
        return orig_post(page)

    cls.get = _tracking_get
    cls.post = _tracking_post

    return cls


def last(participant):
    """Returns time on the last page"""
    return participant.vars['_tracking_post_timestamp'] - participant.vars['_tracking_get_timestamp']


def total(participant):
    """Returns total time on all pages"""
    return participant.vars['_tracking_post_timestamp'] - participant.vars['_tracking_first_timestamp']