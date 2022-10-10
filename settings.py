from os import environ

SESSION_CONFIGS = [
   dict(
       name="demo_chat",
       display_name="multi-player chat",
       num_demo_participants=3,
       app_sequence=['chat']
   ),
#    dict(
#        name="sliders",
#        display_name="classic sliders task",
#        num_demo_participants=1,
#        app_sequence=['sliders']
#    ),
#    dict(
#        name="demo_task",
#        display_name="demo task app: solving math",
#        num_demo_participants=1,
#        app_sequence=['demo_task']
#    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
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
