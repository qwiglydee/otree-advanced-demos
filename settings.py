from os import environ

SESSION_CONFIGS = [
    # dict(
    #     name="trials",
    #     app_sequence=["trials"],
    # ),
    # dict(
    #     name="sliders",
    #     app_sequence=["sliders"]
    # ),
    # dict(
    #     name="captcha",
    #     app_sequence=["captcha"]
    # ),
    # dict(
    #     name="drawing",
    #     app_sequence=["drawing"]
    # ),
    # dict(
    #     name="voting",
    #     app_sequence=["voting"],
    #     num_demo_participants=3,
    # )
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
