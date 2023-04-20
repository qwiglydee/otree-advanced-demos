from os import environ

SESSION_CONFIGS = [
    dict(
        name="trials_form",
        app_sequence=['trials_form'],
    ),
    dict(
        name="trials_live",
        app_sequence=['trials_live'],
    ),
    dict(
        name="trials_stream",
        app_sequence=['trials_stream'],
    ),
    dict(
        name="trials_buttons",
        app_sequence=['trials_buttons'],
    ),
    dict(
        name="trials_choices",
        app_sequence=['trials_choices'],
    ),
    dict(
        name="dumb",
        app_sequence=['dumb'],
    )
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
    num_demo_participants=1,
)

LANGUAGE_CODE = "en"

REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = False

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_TITLE = "Demo apps"
DEMO_PAGE_INTRO_HTML = """
Demo apps
"""

SECRET_KEY = "12345"
