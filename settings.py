from os import environ

SESSION_CONFIGS = [
    dict(
        name="trials_simple",
        display_name="Simple trials",
        app_sequence=["simple"],
        condition="random",
    ),
    dict(
        name="trials_csv",
        display_name="Simple trials pregenerated from csv file",
        app_sequence=["simple_csv"],
        condition="random",
        tasks="tasks.csv",
    ),
    dict(
        name="trials_time",
        display_name="Simple trials with timers",
        app_sequence=["simple_time"],
        condition="random",
    ),
    dict(
        name="choices",
        display_name="Choices with buttons",
        app_sequence=["choices"],
        condition="random",
    ),
    dict(
        name="choices_radio",
        display_name="Choices with radio buttons",
        app_sequence=["choices_radio"],
        condition="random",
    ),
    dict(
        name="choices_layout",
        display_name="Choices with labels and random layout",
        app_sequence=["choices_layout"],
        condition="random",
    ),
    dict(
        name="gonogo",
        display_name="Go/Nogo trials with time-scheduled phases",
        app_sequence=["gonogo"],
        condition="random",
    ),
    dict(
        name="captcha",
        display_name="Transcribing text from generated images",
        app_sequence=["captcha"],
        condition="random",
    ),
    dict(
        name="drawing",
        display_name="Free hand drawing",
        app_sequence=["drawing"],
        condition="random",
    ),
    # dict(
    #     name="multistep",
    #     display_name="Multiple sequential inputs in trials",
    #     app_sequence=['multistep'],
    #     condition="random",
    # ),
    # dict(
    #     name="multistage",
    #     display_name="Multiple nonregular stages of trials",
    #     app_sequence=['multistage'],
    #     condition="random",
    # ),
    # dict(
    #     name="voting",
    #     display_name="Group voting and chatting",
    #     app_sequence=["voting"],
    #     num_demo_participants=3,
    # ),
    # dict(
    #     name="sliders",
    #     display_name="Sliders task",
    #     app_sequence=["sliders"],
    # ),
    # dict(
    #     name="ultimatum",
    #     display_name="Utimatum game",
    #     app_sequence=['ultimatum_screener', 'ultimatum_game'],
    #     num_demo_participants=2,
    # ),
    # dict(
    #     name="forms",
    #     app_sequence=["forms"],
    # )
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
