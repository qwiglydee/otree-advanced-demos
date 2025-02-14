from os import environ

SESSION_CONFIGS = [
    dict(
        name="trials",
        display_name="Simple trials (pregenerated)",
        app_sequence=["simple"],
        condition="random",
    ),
    dict(
        name="trials_ondemand",
        display_name="Simple trials (generating on demand)",
        app_sequence=["simple_ondemand"],
        condition="random",
    ),
    dict(
        name="trials_choices",
        display_name="Choice trials with buttons",
        app_sequence=["choices"],
        condition="random",
    ),
    dict(
        name="trials_radio",
        display_name="Choice trials with radio and submit",
        app_sequence=["choices_radio"],
        condition="random",
    ),
    dict(
        name="forms",
        app_sequence=["forms"],
    ),
    dict(
        name="ultimatum",
        display_name="Ultimatum game (2 players)",
        app_sequence=["ultimatum_screener", "ultimatum_game"],
        num_demo_participants=2,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    participation_fee=1.00,
    real_world_currency_per_point=0.01,
    num_demo_participants=1,
)

LANGUAGE_CODE = "en"

REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = False

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")


# PARTICIPANT_FIELDS = ['dropout']

SECRET_KEY = "12345"

DEBUG = environ.get("DEBUG", False)
