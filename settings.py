from os import environ

SESSION_CONFIGS = [
    dict(
        name="trials_live",
        display_name="Simple Trials",
        app_sequence=["trials_live"],
    ),
    dict(
        name="trials_inf",
        display_name="Simple Trials (infinite series)",
        app_sequence=["trials_inf"],
    ),
    dict(
        name="captcha",
        display_name="Captcha: generated images",
        app_sequence=["captcha"]
    ),
    dict(
        name="drawing",
        display_name="Drawing: free hand draw input",
        app_sequence=["drawing"]
    ),
    dict(
        name="multistep",
        display_name="Multiple inputs in trials",
        app_sequence=["multistep"],
    ),
    dict(
        name="conditional",
        display_name="Conditional trial workflow",
        app_sequence=["conditional"],
    ),
    dict(
        name="sliders",
        display_name="Sliders task",
        app_sequence=["sliders"],
    ),
    dict(
        name="voting",
        display_name="Real-time voting and chatting",
        app_sequence=["voting"],
        num_demo_participants=3,
    ),
    dict(
        name="phases",
        display_name="Phases: time schedued trial phases",
        app_sequence=["phases"],
    ),
    dict(
        name="dumb",
        display_name="just a dumb app for testing",
        app_sequence=["dumb"],
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
