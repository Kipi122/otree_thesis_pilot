from os import environ

SESSION_CONFIGS = [
    dict(
        name='pilot_multiplayer',
        display_name="pilot_multiplayer",
        num_demo_participants=4,
        app_sequence=['pilot_multiplayer'],
        use_browser_bots=False,
        completionCode='CF9ZHXKD', #FIXME add the link to the completion form
        STARTING_FINE_CONDITION ='small',  # Set the starting condition for the multiplayer experiment
        PREFERRED_SIDE='right',  # Set the preferred side for the multiplayer experiment

    ),
    dict(
        name='pilot_singleplayer',
        display_name="pilot_singleplayer",
        num_demo_participants=2,
        app_sequence=[ 'pilot_singleplayer'],
        use_browser_bots=False,
        completionCode='CF9ZHXKD', #FIXME add the link to the completion form
    ),
    # Add these test configurations
    #dict(
    #    name='mobile',
    #    display_name='Mobile Test',
    #    app_sequence=['pilot_singleplayer'],
    #    num_demo_participants=1,
    #    use_browser_bots=True,
    #),
    
]

PARTICIPANT_FIELDS = [
    #demographic variables
    'is_repeat_participant',
    'is_dropout',
    'timeout_num',

    'age',
    'gender',
    'fine_condition',
    'preferred_side',
    'prolific_id',
    
    #comprehension variables
    'comprehension_attempts',
    'passed_comprehension',
    'failed_comprehension',

     #role assignment
    'role_confirmed',
    'role_assignment_time',
    
    #payoff variables
    'total_points',
    'total_chooser_points',
    'total_moderator_points',
    'waiting_compensation',
    'got_waiting_compensation',
    'lottery_won',
    'total_monetary_payoff',
    'finished',
    
    #timestamps
    'instruction_start_time',
    'instruction_end_time',
    'training_start_time',
    'training_end_time',
    'comprehension_start_time',
    'comprehension_end_time',
    'experiment_start_time',
    'experiment_end_time',
    'experiment_date',
    'total_waiting_time',
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=6.50, doc=""  # TODO change this to real values
)
OTREE_PRODUCTION = environ.get('OTREE_PRODUCTION')
DEBUG = 0
OTREE_AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL') #can be DEMO or STUDY
OTREE_ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
#DEBUG = 1 #HACK can change to 1 for debugging
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = False  # Set to False to use real currency instead of points

ROOMS = [
         dict(
        name='dot_1',
        display_name='dot-experiment1',
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
    dict(
        name='dot_2',
        display_name='dot-experiment2',
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
    dict(
        name='dot_3',
        display_name='dot-experiment3',
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),
    dict(
        name='dot_4',
        display_name='dot-experiment4',
        # participant_label_file='_rooms/your_study.txt',
        # use_secure_urls=True,
    ),

]

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '9735455758331'

INSTALLED_APPS = ['otree']

EXTENSION_APPS = ['otree_extensions']
STATICFILES_DIRS = ['_static']

