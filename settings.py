from os import environ

SESSION_CONFIGS = [
    dict(
        name='pilot_multyplayer',
        display_name="pilot_multyplayer",
        num_demo_participants=2,
        app_sequence=['pilot_multyplayer'],
        use_browser_bots=False,
    ),
    dict(
        name='pilot_singleplayer',
        display_name="pilot_singleplayer",
        num_demo_participants=2,
        app_sequence=[ 'pilot_singleplayer'],
        use_browser_bots=False,
    ),
    # Add these test configurations
    dict(
        name='mobile',
        display_name='Mobile Test',
        app_sequence=['pilot_singleplayer'],
        num_demo_participants=1,
        use_browser_bots=True,
    ),
    
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""  # TODO change this to real values
)

DEBUG = 1 #HACK can change to 1 for debugging
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = []

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '9735455758331'

INSTALLED_APPS = ['otree']

EXTENSION_APPS = ['otree_extensions']
STATICFILES_DIRS = ['_static']

