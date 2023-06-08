from os import environ

SESSION_CONFIGS = [
    dict(
        name="trials_local",
        app_sequence=["trials_local"],
    ),
    dict(
        name="trials_live",
        app_sequence=["trials_live"],
    ),
    dict(
        name="trials_infinite",
        app_sequence=["trials_infinite"],
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    participation_fee=1.00,
    real_world_currency_per_point=0.1,
    doc="",
    num_demo_participants=1,
)

LANGUAGE_CODE = "en"

REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = False

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")


# PARTICIPANT_FIELDS = ['dropout']

SECRET_KEY = "12345"
