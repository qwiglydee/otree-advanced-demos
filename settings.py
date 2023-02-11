from os import environ

SESSION_CONFIGS = [
    dict(
        name="trials_basic",
        display_name="local trials with text input",
        app_sequence=['trials_basic']
    ),
    dict(
        name="trials_choices",
        display_name="local trials with answer choices",
        app_sequence=['trials_choices']
    ),
    dict(
        name="trials_halflive",
        display_name="half-live trials with server-side validation and feedback",
        app_sequence=['trials_halflive']
    ),
    dict(
        name="trials_live",
        display_name="live trials, full communication with server",
        app_sequence=['trials_live']
    ),
    dict(
        name="trials_infinite",
        display_name="live trials infinite sequence",
        app_sequence=['trials_infinite']
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00, 
    doc="",
    num_demo_participants=1
)

LANGUAGE_CODE = "en"

REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_TITLE = "Demo apps"
DEMO_PAGE_INTRO_HTML = """
Demo apps
"""

SECRET_KEY = "12345"
