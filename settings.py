from os import environ

SESSION_CONFIGS = [
    dict(
        name="trials_simple",
        display_name="Simple trials",
        app_sequence=["simple"],
        condition="random",
    ),
    dict(
        name="trials_simple2",
        display_name="Simple trials with multiple fields and submit button",
        app_sequence=["simple2"],
        condition="random",
    ),
    dict(
        name="trials_choices_buttons",
        display_name="Choices with buttons",
        app_sequence=["choices"],
        condition="random",
    ),
    dict(
        name="trials_choices_radio",
        display_name="Choices with radio",
        app_sequence=["choices2"],
        condition="random",
    ),
    dict(
        name="trials_infinite",
        display_name="Infinite series",
        app_sequence=["infinite"],
        condition="random",
    ),
    dict(
        name="trials_infinite_timers",
        display_name="Infinite series with timers",
        app_sequence=["timers"],
        condition="random",
    ),
    dict(
        name="trials_phases",
        display_name="Scheduled phases",
        app_sequence=["phases"],
        condition="random",
    ),
    dict(
        name="sliders",
        display_name="Sliders task",
        app_sequence=["sliders"],
    ),
    # dict(
    #     name="voting",
    #     display_name="Real-time voting and chatting",
    #     app_sequence=["voting"],
    #     num_demo_participants=3,
    # ),
    # dict(
    #     name="drawing",
    #     display_name="Drawing: freehand drawing input",
    #     app_sequence=["drawing"]
    # ),
    # dict(
    #     name="dumb",
    #     app_sequence=["dumb"],
    # ),
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
