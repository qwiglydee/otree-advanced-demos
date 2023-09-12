from os import environ

SESSION_CONFIGS = [
    dict(
        name="trials_live",
        display_name="Simple Trials (live)",
        app_sequence=["trials_live"],
    ),
    dict(
        name="trials_inf",
        display_name="Simple Trials (infinite)",
        app_sequence=["trials_inf"],
    ),
    dict(
        name="captcha",
        display_name="Captcha (generated images)",
        app_sequence=["captcha"]
    ),
    dict(
        name="drawing",
        display_name="Drawing (free hand draw input)",
        app_sequence=["drawing"]
    ),
    dict(
        name="sliders",
        display_name="Sliders task",
        app_sequence=["sliders"]
    ),
    # dict(
    #     name="voting",
    #     app_sequence=["voting"],
    #     num_demo_participants=3,
    # )
    dict(
        name="dumb",
        display_name="just a dumb app for testing",
        app_sequence=["dumb"],
        num_demo_participants=2,
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
