from otree.api import *
import random
import math
import json
import time




doc = """
This is a dot choice experiment where participants act as moderators, 
deciding whether to punish or warn a bot for its choices.
"""
#FIXME implement timestamps savings as participants vars
#FIXME for the multiplayer, we want he "temping rounds" order to be the same for all players in the group? 
#FIXME for the multiplayer, we want "tempting rounds" to be created in the Group and not the player

#TODO add pictures to instructions
#TODO put everything in the center of the screen
#TODO change "participant" to "chooser" throughout the game
#FIXME change the payoff throughout the game to be points based on docomentation
#TODO check detect mobile snippet to block mobile browsers after deployment #FIXME ITS NOT WORKING BUT LOOKS GOOD SO DOESNT MATTER

class Constants(BaseConstants):
    estimated_minutes = 37  # Estimated time to complete the experiment
    is_multiplayer = True  # Set to True for multiplayer, False for singleplayer
    is_zoom = True  # Set to True for zoom, False non-zoom
    debug = False  # Set to False for production
    is_within_session = True  # Set to True for within-session experiments, False for between-session
    name_in_url = 'Dot_Experiment' #FIXME change to correct name before deployment!!!!!!!
    MODERATOR_ROLE = 'Moderator'
    CHOOSER_ROLE = 'Chooser'  
    players_per_group = 2
    num_rounds = 60  # Total number of rounds in the experiment
    transition_round = 31 # Add a new constant for the transition point
    rounds_per_condition = 30  # Each condition lasts 40 rounds
    small_fine = 11
    large_fine = 99
    tempting_rounds_probability = 2/3  # Probability of a round being tempting
    tempting_rounds = int(tempting_rounds_probability * num_rounds) # 2/3 of the rounds are tempting
    correct_probability_preferred = 0.93   
    correct_probability_not_preferred = 0.6
    expectation_average_points = ((tempting_rounds*correct_probability_not_preferred + (num_rounds-tempting_rounds)*correct_probability_preferred)*10)-50 #minus 50 for the lottery probability
    #preferred_side = 'right' # [x] add alternation - randomise for each round for SP. theodorsecue et al. study 1 was alternating between left and right
    preferred_side_points = 10
    moderator_points_per_correct = 10
    num_dots_big = 17
    num_dots_small = 13
    total_dots = num_dots_big + num_dots_small
    fixation_display_seconds = 1.2  # Display fixation cross for 500ms
    dots_display_seconds = 0.6 # Display dots for X seconds 
    participation_fee = 6.50  #TODO implement using session vars
    bonus_fee = 3.50 # Add the bonus fee if the participant wins the lottery
    #bonus_fee_per_point = 0.1 #We have a lottery 
    TransitionPage_timeout_seconds = 45  # Time for transition page to auto proceed
    feedback_timeout_correct = 8 # Time to display feedback before proceeding
    feedback_timeout_incorrect = 8 # Time to display feedback before proceeding
    decision_timeout_seconds = 15  # Time to wait for decision before proceeding and getting a fine 
    timeout_penalty = 10 # Points deducted for not making a decision in time 
    waiting_compensation_fee = 1  # £1 per 10 minutes 
    min_waiting_for_compensation = 600   # X minutes in seconds x*60
    waiting_compensation_minutes_for_reference = 10  # 10 minutes for reference
    
    # Multiplayer-specific constants
    #initial_fine_condition = 'small'   # Initial fine condition for the first 30 rounds
    #initial_preferred_side = 'right'  # Initial preferred side for the whole experiment 



class Subsession(BaseSubsession):
   pass

def creating_session(subsession: Subsession):
    subsession.group_randomly(fixed_id_in_group=True)

    for group in subsession.get_groups():
        #random if bigger than tempting_round_probability
        group.is_tempting_round_group = random.random() < Constants.tempting_rounds_probability

        #if group.is_tempting_round_group, set is_tempting_round for each player in group
        for player in group.get_players():
            player.is_tempting_round = group.is_tempting_round_group


    #check distribution of tempting rounds, check mean number of is_tempting_round for each player

        

    for player in subsession.get_players():
        #set paired_player_id 
        #print(f"{player.participant.id_in_session} is paired with {player.get_others_in_group()[0].participant.id_in_session}")
        player.paired_player_id  = player.get_others_in_group()[0].participant.id_in_session

    if subsession.round_number == 1:
        # Initialize the used_prolific_ids in session vars if it doesn't exist
        if not subsession.session.vars.get('used_prolific_ids'):
            subsession.session.vars['used_prolific_ids'] = set()

        # Define the initial conditions array (half start with small, half with large)
        #num_players = len(subsession.get_players())
        #conditions = ['small'] * (num_players // 2) + ['large'] * (num_players - num_players // 2)
        #random.shuffle(conditions)
        
        # Store the conditions in session vars
        #subsession.session.vars['initial_fine_conditions'] = conditions
        #subsession.session.vars['condition_index'] = 0
        
        # For each player, set up their conditions
        for player in subsession.get_players():
            # Assign initial condition
            #condition_index = subsession.session.vars['condition_index']
            #initial_condition = conditions[condition_index % len(conditions)]
            
            # Store the initial and second conditions in participant vars
            #player.participant.vars['initial_fine_condition'] = initial_condition
            #player.participant.vars['second_fine_condition'] = 'large' if initial_condition == 'small' else 'small'
            
           
            # Generate tempting rounds separately for each condition
            # First condition (rounds 1-X)
            #tempting_list_first = sorted(random.sample(range(1, Constants.rounds_per_condition + 1), 
            #                                          int(Constants.tempting_rounds / 2)))
            # Second condition (rounds X-END)
            #tempting_list_second = sorted(random.sample(range(Constants.transition_round, 
            #                                                Constants.num_rounds + 1), 
            #                                          int(Constants.tempting_rounds / 2)))
            
            # Combine both lists
            #combined_tempting_list = tempting_list_first + tempting_list_second
            #player.player_tempting_rounds = json.dumps(combined_tempting_list)
            
            # Set the current condition for round 1
            player.fine_condition = 'small' if subsession.session.config['STARTING_FINE_CONDITION'] == 'small' else 'large'  # Use the initial condition for round 1
            player.participant.vars['initial_fine_condition'] = 'small' if subsession.session.config['STARTING_FINE_CONDITION'] == 'small' else 'large'

            #set condition for second half of the game 
            player.participant.vars['second_fine_condition'] = 'large' if player.participant.vars['initial_fine_condition'] == 'small' else 'small'
            
            # Set preferred side
            player.participant.vars['preferred_side'] = 'right' if subsession.session.config['PREFERRED_SIDE'] == 'right' else 'left'  # Use the initial preferred side for round 1
            player.preferred_side = player.participant.vars['preferred_side']

            # Initialize participant fields
            participant = player.participant
            participant.prolific_id = None  # Initialize Prolific ID
            participant.timeout_num = 0  # Initialize timeout count
            participant.comperhension_attempts = 0
            participant.passed_comprehension = False
            participant.failed_comprehension = False
            participant.is_dropout = False  # Initialize dropout status
            
            participant.total_points = 0  # Initialize total points #TODO IMPLEMENT total_points
            participant.total_chooser_points = 0 #FIXME REMOVE?
            participant.total_moderator_points = 0 #FIXME REMOVE?
            participant.total_waiting_time = 0
            participant.waiting_compensation = 0
            participant.got_waiting_compensation = False
            participant.lottery_won = False
            participant.finished = False
            
            
            # Increment the condition index
            #subsession.session.vars['condition_index'] += 1
            
            # Set role in experiment
            player.role_in_experiment = player.role  
    else:
        # For rounds >1
        for player in subsession.get_players():
            # Copy tempting rounds list from round 1
            #player.player_tempting_rounds = player.in_round(1).player_tempting_rounds
            
            # Set condition based on round number
            if player.round_number < Constants.transition_round:
                # First 40 rounds - use initial condition
                player.fine_condition = player.participant.vars['initial_fine_condition']
            else:
                # Rounds 41-80 - use second condition
                player.fine_condition = player.participant.vars['second_fine_condition']
            
            # Copy preferred side and role
            player.preferred_side = player.participant.vars['preferred_side']
            player.role_in_experiment = player.role  # For singleplayer mode
            
            # Copy points and waiting time from previous round
            if player.round_number > 1:
                current_round = player.round_number
                player.total_points = player.in_round(current_round - 1).total_points
                player.total_chooser_points = player.in_round(current_round - 1).total_chooser_points
                player.total_moderator_points = player.in_round(current_round - 1).total_moderator_points
                player.total_waiting_time = player.in_round(current_round - 1).total_waiting_time
                #player.is_dropout = player.in_round(current_round - 1).is_dropout

    # generate dot counts for each player in the group
    for group in subsession.get_groups():
        for player in group.get_players():
            player.generate_pair_dot_counts()
    
    #set dot positions for each player in the group
    for group in subsession.get_groups():
        for player in group.get_players():
            player.get_pair_dot_positions()




class Group(BaseGroup):
    is_tempting_round_group= models.BooleanField(initial=False)  # Track if the group is in a tempting check round

    chooser_choice_group = models.StringField()  # Store the choice made by the chooser in the group
    moderator_decision_group = models.StringField(blank=True)  # Store the decision made by the moderator in the group

    chooser_rt_group = models.FloatField(initial=0)  # Reaction time of the chooser in the group
    moderator_rt_group = models.FloatField(initial=0)  # Reaction time of the moderator in the group

    choice_correct_group = models.BooleanField()  # Was the chooser's choice correct? 
    preferred_side_chosen_group = models.BooleanField()  # Was the preferred side chosen by the chooser?

    
    #pass

class Player(BasePlayer):
    #multiplayer-specific fields
    is_dropout = models.BooleanField(initial=False)  # Track if the player is a dropout
    subsequent_timeouts = models.IntegerField(initial=0)  # Count of subsequent timeouts
    paired_player_id  = models.IntegerField()
    chooser_choice_time = models.FloatField(initial=0)  # Reaction time of the chooser


    total_points = models.IntegerField(initial=0)  # Track total points for the player

    def generate_pair_dot_positions(self):
        """
        Generate dot positions for this specific pair using original player dot counts.
        Only called by the first player in group to avoid duplication.
        """

        #print(f"Generating dot positions for player {self.participant.id_in_session} in group {self.group.id_in_subsession}")
        import math
        import random

        width, height = 400, 200
        padding = 10  # Keep dots away from edges
        min_distance = 10  # Minimum distance between dots
        line_tolerance = 5  # Minimum distance from the line y = 0.5x
        max_attempts = 1000  # Max attempts to find a valid position for a dot

        # Adjusted function to account for SVG coordinate system
        def is_left_of_diagonal(x, y):
            # In SVG, y increases downward, so we need to adjust the comparison
            return y > 0.5 * x  # Points below the line are on the left side

        def distance_from_line(x, y):
            # Distance from point (x, y) to line y = 0.5x
            numerator = abs(y - 0.5 * x)
            denominator = math.sqrt(0.5 ** 2 + 1)
            return numerator / denominator

        def distance(p1, p2):
            return math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])

        all_dots = []
        left_dots = []
        right_dots = []

        # Use original player dot counts
        target_left_dots = self.dots_left
        target_right_dots = self.dots_right

        # Generate left-side dots
        attempts = 0
        while len(left_dots) < target_left_dots:
            if attempts >= max_attempts:
                raise Exception(f"Could not generate enough left-side dots without collisions. Target: {target_left_dots}, Generated: {len(left_dots)}")
            x = random.randint(padding, width - padding)
            y = random.randint(padding, height - padding)
            attempts += 1
            if is_left_of_diagonal(x, y):
                # Check if the point is too close to the dividing line
                if distance_from_line(x, y) < line_tolerance:
                    continue  # Reject point
                # Check for collisions with existing dots
                new_dot = {'x': x, 'y': y}
                collision = any(distance(new_dot, dot) < min_distance for dot in all_dots)
                if collision:
                    continue  # Reject point due to collision
                left_dots.append(new_dot)
                all_dots.append(new_dot)
                attempts = 0  # Reset attempts after successful placement

        # Generate right-side dots
        attempts = 0
        while len(right_dots) < target_right_dots:
            if attempts >= max_attempts:
                raise Exception(f"Could not generate enough right-side dots without collisions. Target: {target_right_dots}, Generated: {len(right_dots)}")
            x = random.randint(padding, width - padding)
            y = random.randint(padding, height - padding)
            attempts += 1
            if not is_left_of_diagonal(x, y):
                # Check if the point is too close to the dividing line
                if distance_from_line(x, y) < line_tolerance:
                    continue  # Reject point
                # Check for collisions with existing dots
                new_dot = {'x': x, 'y': y}
                collision = any(distance(new_dot, dot) < min_distance for dot in all_dots)
                if collision:
                    continue  # Reject point due to collision
                right_dots.append(new_dot)
                all_dots.append(new_dot)
                attempts = 0  # Reset attempts after successful placement

        # Store the generated positions as JSON string for both players in the pair
        dot_positions = left_dots + right_dots
        dot_positions_json = json.dumps(dot_positions)
        
        # Store in both players of the pair
        self.dot_positions = dot_positions_json
        
        # Copy to the other player in the group (assuming 2-player groups)
        paired_participant = self.get_others_in_group()[0]
        paired_participant.dot_positions = dot_positions_json
        
        return dot_positions


    def get_pair_dot_positions(self):
        """
        Helper function to retrieve the dot positions for this pair.
        Can be called by either player in the pair.
        """

        #print(f"Getting dot positions for player {self.participant.id_in_session} in group {self.group.id_in_subsession}")
        import json
        
        dot_positions = self.field_maybe_none('dot_positions')
        if dot_positions:
            #print(f"Using existing dot positions for player {self.participant.id_in_session}")
            return json.loads(self.dot_positions)
        else:
            # Fallback: generate if not already generated
            if self.id_in_group == 1:
                #print(f"Generating new dot positions for player {self.participant.id_in_session} in group {self.group.id_in_subsession}")
                return self.generate_pair_dot_positions()
            else:
                #print(f"Waiting for player 1 to generate dot positions for player {self.participant.id_in_session} in group {self.group.id_in_subsession}")
                # Wait for the first player to generate
                first_player = self.group.get_player_by_id(1)
                first_player_positions = first_player.field_maybe_none('dot_positions')
                if first_player_positions:
                    #print(f"Using generated dot positions from player {first_player.participant.id_in_session}")
                    self.dot_positions = first_player.dot_positions
                    return json.loads(self.dot_positions)
                else:
                    raise Exception("Dot positions not yet generated for this pair")


# Additional Player model field needed:
# Add this to your Player class:
    dot_positions = models.LongStringField(blank=True)  # Store JSON of dot positions

# Modified generate_pair_dot_counts function to integrate with dot position generation:
    def generate_pair_dot_counts(self):
        """Generate unique dots for this specific pair"""
        if self.id_in_group == 1:
            # Only first player generates dots to avoid duplication
            is_tempting = self.is_tempting_round
            preferred = self.get_preferred_side()
            
            if is_tempting:
                # Force incorrect preferred side choice
                if preferred == 'left':
                    self.dots_right = Constants.num_dots_big
                    self.dots_left = Constants.total_dots - self.dots_right
                    self.correct_answer = 'right'
                else:
                    self.dots_left = Constants.num_dots_big
                    self.dots_right = Constants.total_dots - self.dots_left
                    self.correct_answer = 'left'
            else:
                # Force correct preferred side choice
                if preferred == 'left':
                    self.dots_left = Constants.num_dots_big
                    self.dots_right = Constants.total_dots - self.dots_left
                    self.correct_answer = 'left'
                else:
                    self.dots_right = Constants.num_dots_big
                    self.dots_left = Constants.total_dots - self.dots_right
                    self.correct_answer = 'right'
            
            # Copy to paired participant
            paired_participant = self.get_others_in_group()[0]
            paired_participant.dots_left = self.dots_left
            paired_participant.dots_right = self.dots_right
            paired_participant.correct_answer = self.correct_answer
            
            # Generate the actual dot positions after setting counts
            

    temp_timeout = models.FloatField(initial=0)

    got_waiting_compensation = models.BooleanField(initial=False)  # Track if the participant received waiting compensation
    waiting_compensation = models.FloatField(initial=0)  # Track the amount of waiting compensation received

    finished = models.BooleanField(initial=False)

    #tempting rounds - for singleplayer
    #player_tempting_rounds = models.LongStringField(blank=True)

    is_tempting_round = models.BooleanField()
    
    timeout_occurred_chooser = models.BooleanField(initial=False)  # Track if timeout happened
    timeout_occurred_moderator = models.BooleanField(initial=False)  # Track if timeout happened
    timeout_occurred = models.BooleanField(initial=False)  # Track if timeout happened for the player
    # Mobile detection
    is_mobile = models.BooleanField(initial=False)
    #Prolific ID
    prolific_id = models.StringField(label="Please enter your Prolific ID")
    is_repeat_participant = models.BooleanField(initial=False)

    # Demographics
    age = models.IntegerField(label="What is your age?", min=18, max=100)
    gender = models.StringField(
        choices=[['Male', 'Male'], ['Female', 'Female'], ['Other', 'Other']],
        label="What is your gender?",
        widget=widgets.RadioSelect
    )

    # Comprehension check fields
    comp_fine_amount = models.IntegerField(
        label="How many points are deducted when the Moderator issues a penalty?",
    )
    
    comp_preferred_side = models.StringField(
        label="Which side gives the Chooser more points?",
        choices=[['left', 'Left side'], ['right', 'Right side']],
    )
    
    comprehension_attempts = models.IntegerField(initial=0)
    passed_comprehension = models.BooleanField(initial=False)
    failed_comprehension = models.BooleanField(initial=False)


    # Constant Game fields
    fine_condition = models.StringField()
    preferred_side = models.StringField()
    role_in_experiment = models.StringField()  # 'chooser' or 'moderator'

    # Round fields
    #chooser
    chooser_choice  = models.StringField() #the choice of the chooser
    choice_correct  = models.BooleanField() #is the choice correct
    preferred_side_chosen  = models.BooleanField() #was the preferred side chosen
    correct_answer = models.StringField() #the correct answer for the round
    dots_left = models.IntegerField() #number of dots on the left side
    dots_right = models.IntegerField() #number of dots on the right side
    #moderator
    decision = models.StringField(blank=True) #the decision of the moderator. can be 'punish' or 'warn' or empty if chooser was correct
    def get_decision(self):
        """Safely get the decision value"""
        return self.field_maybe_none('decision') or ''

    #training fields
    training_choice = models.StringField(
        choices=[['left', 'Left side'], ['right', 'Right side']],
        label="Which side has more dots?"
    )
    
    training_decision = models.StringField(
        choices=[['punish', 'Punish'], ['warn', 'Warn']],
        label="Choose your action"
    )

    chooser_choice = models.StringField(
        choices=[['left', 'Left side'], ['right', 'Right side']],
        label="Which side has more dots?"
    )
    '''
    #attention check fields
    attention_check_fine = models.IntegerField(
    label="How many points could the Moderator have deducted from the reward of the Chooser in each round?",
    choices=[
        [5, "5 points"],
        [11, "11 points"],
        [20, "20 points"], 
        [50, "50 points"],
        [99, "99 points"],
        [150, "150 points"]
    ],
    widget=widgets.RadioSelect
    )
    attention_check_passed = models.BooleanField(initial=False) # store whether the participant passed the attention check
    attention_check_answer = models.IntegerField() # store the answer made by the participant for the attention check
    correct_fine_amount = models.IntegerField() # store the correct fine amount for the attention check
    '''
    #save points for each round
    round_chooser_points = models.IntegerField() #FIXME saving not working
    round_chooser_alternative_points = models.IntegerField()
    round_moderator_points = models.IntegerField() #FIXME saving not working

    #save the total points for the whole game
    total_chooser_points = models.IntegerField(initial=0)  # Add initial=0
    total_moderator_points = models.IntegerField(initial=0)  # Add initial=0
    
    #Bonus Lottery
    lottery_won = models.BooleanField(initial=False)  # Track if the participant won the lottery
    #total money earned
    total_monetary_payoff = models.FloatField(initial=0)  # Track the total monetary payoff

    # Response time measurements
    moderator_decision_time = models.FloatField()  # Time taken to make moderator decision
    chooser_decision_time = models.FloatField()  # Time taken for chooser (bot) decision
    
    # Phase timing measurements
    instruction_start_time = models.FloatField()  # When instructions began
    instruction_end_time = models.FloatField()    # When instructions ended
    training_start_time = models.FloatField()     # When training began
    training_end_time = models.FloatField()       # When training ended
    comprehension_start_time = models.FloatField() # When comprehension check began
    comprehension_end_time = models.FloatField()   # When comprehension check ended
    experiment_start_time = models.FloatField()    # When main experiment began
    experiment_end_time = models.FloatField()      # When experiment ended
    experiment_date = models.StringField()         # Date of the experiment
    
    # Cumulative waiting time
    total_waiting_time = models.FloatField(initial=0)  # Total time spent waiting

    #End_Questionnaire Questions
    # Add these fields to the Player class in __init__.py
    effectiveness_rating = models.IntegerField(
        label="How much do you think your decisions as a Moderator have effected the Chooser's choices?",
        choices=[0, 1, 2, 3, 4, 5],
        widget=widgets.RadioSelectHorizontal
    )

    fairness_rating_1 = models.IntegerField(
        label="How fair do you think the 'Punish' penalty was in the first part?",
        choices=[0, 1, 2, 3, 4, 5],
        widget=widgets.RadioSelectHorizontal
    )

    fairness_rating_2 = models.IntegerField(
        label="How fair do you think the 'Punish' penalty was in the second part?",
        choices=[0, 1, 2, 3, 4, 5],
        widget=widgets.RadioSelectHorizontal
    )

    additional_comments = models.LongStringField(
        label="Do you have any additional comments about the experiment?", 
        blank=True  # This makes the field optional
    )

    # Calculate derived timing metrics
    def get_instruction_time(self):
        return self.instruction_end_time - self.instruction_start_time
        
    def get_training_time(self):
        return self.training_end_time - self.training_start_time
        
    def get_comprehension_time(self):
        return self.comprehension_end_time - self.comprehension_start_time
        
    def get_total_experiment_time(self):
        return self.experiment_end_time - self.experiment_start_time

    
    def get_preferred_side(self):
        return self.participant.vars.get('preferred_side', 'right')  # Default to right if not set
    
    def validate_prolific_id(self):
        #print("Validating Prolific ID")
        # Get the set of used Prolific IDs from session vars
        used_prolific_ids = self.session.vars.get('used_prolific_ids', set())
        
        # Check if this Prolific ID has been used
        if self.prolific_id in used_prolific_ids:
            #print("Prolific ID already used")
            self.is_repeat_participant = True
            self.participant.vars['is_repeat_participant'] = True
            return False
        else:
            # Add the new Prolific ID to the set
            #print("Prolific ID is valid")
            used_prolific_ids.add(self.prolific_id)
            self.session.vars['used_prolific_ids'] = used_prolific_ids
            self.participant.prolific_id = self.prolific_id  # Store in participant vars for persistence
            return True

    def generate_dot_positions(self):
        import math

        width, height = 400, 200
        padding = 10  # Keep dots away from edges
        min_distance = 10  # Minimum distance between dots
        line_tolerance = 5  # Minimum distance from the line y = 0.5x
        max_attempts = 1000  # Max attempts to find a valid position for a dot

        # Adjusted function to account for SVG coordinate system
        def is_left_of_diagonal(x, y):
            # In SVG, y increases downward, so we need to adjust the comparison
            return y > 0.5 * x  # Points below the line are on the left side

        def distance_from_line(x, y):
            # Distance from point (x, y) to line y = 0.5x
            numerator = abs(y - 0.5 * x)
            denominator = math.sqrt(0.5 ** 2 + 1)
            return numerator / denominator

        def distance(p1, p2):
            return math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])

        all_dots = []
        left_dots = []
        right_dots = []

        # Generate left-side dots
        attempts = 0
        while len(left_dots) < self.dots_left:
            if attempts >= max_attempts:
                raise Exception("Could not generate enough left-side dots without collisions.")
            x = random.randint(padding, width - padding)
            y = random.randint(padding, height - padding)
            attempts += 1
            if is_left_of_diagonal(x, y):
                # Check if the point is too close to the dividing line
                if distance_from_line(x, y) < line_tolerance:
                    continue  # Reject point
                # Check for collisions with existing dots
                new_dot = {'x': x, 'y': y}
                collision = any(distance(new_dot, dot) < min_distance for dot in all_dots)
                if collision:
                    continue  # Reject point due to collision
                left_dots.append(new_dot)
                all_dots.append(new_dot)
                attempts = 0  # Reset attempts after successful placement

        # Generate right-side dots
        attempts = 0
        while len(right_dots) < self.dots_right:
            if attempts >= max_attempts:
                raise Exception("Could not generate enough right-side dots without collisions.")
            x = random.randint(padding, width - padding)
            y = random.randint(padding, height - padding)
            attempts += 1
            if not is_left_of_diagonal(x, y):
                # Check if the point is too close to the dividing line
                if distance_from_line(x, y) < line_tolerance:
                    continue  # Reject point
                # Check for collisions with existing dots
                new_dot = {'x': x, 'y': y}
                collision = any(distance(new_dot, dot) < min_distance for dot in all_dots)
                if collision:
                    continue  # Reject point due to collision
                right_dots.append(new_dot)
                all_dots.append(new_dot)
                attempts = 0  # Reset attempts after successful placement

        return left_dots + right_dots

    def generate_dot_counts(self):
        """
        Generates dot counts for each side of the display, ensuring the proper ratio
        of tempting vs non-tempting rounds.
        """
        #print("Generating dot counts")

        #changes for tempting_rounds
        #current_round = self.subsession.round_number
        # Parse the JSON string to get the list of tempting rounds.

        #tempting rounds - for multiplayer
        #tempting_list = json.loads(self.group.tempting_rounds_mygroup)
        #tempting rounds - for singleplayer
        #tempting_list = json.loads(self.player_tempting_rounds)

        is_tempting = self.is_tempting_round  # Use the group variable for multiplayer
        preferred = self.get_preferred_side()
        

        if is_tempting:
            self.is_tempting_round = True
            # In tempting rounds, force the correct answer to be opposite the preferred side.
            if preferred == 'left':
                self.dots_right = Constants.num_dots_big
                self.dots_left = Constants.total_dots - self.dots_right
                self.correct_answer = 'right'
            else:  # preferred == 'right'
                self.dots_left = Constants.num_dots_big
                self.dots_right = Constants.total_dots - self.dots_left
                self.correct_answer = 'left'
        else:
            self.is_tempting_round = False
            # In non-tempting rounds, force the correct answer to match the preferred side.
            if preferred == 'left':
                self.dots_left = Constants.num_dots_big
                self.dots_right = Constants.total_dots - self.dots_left
                self.correct_answer = 'left'
            else:  # preferred == 'right'
                self.dots_right = Constants.num_dots_big
                self.dots_left = Constants.total_dots - self.dots_right
                self.correct_answer = 'right'

        #print(f"Player_id: {self.id_in_group}  Round {current_round}: Tempting={is_tempting}, Preferred={preferred}, Dots Left={self.dots_left}, Dots Right={self.dots_right}, Correct Answer={self.correct_answer}")
        
    def record_participant_choice(self):
        # Instead of random choice, implement bot behavior based on Teodorescu's parameters
        if self.correct_answer == self.get_preferred_side():
            # 93% chance to be correct when preferred side is correct
            self.chooser_choice = self.correct_answer if random.random() < Constants.correct_probability_preferred else ('left' if self.correct_answer == 'right' else 'right')
        else:
            # 60% chance to be correct when non-preferred side is correct
            self.chooser_choice = self.correct_answer if random.random() < Constants.correct_probability_not_preferred else ('left' if self.correct_answer == 'right' else 'right')
        
        self.choice_correct = self.chooser_choice == self.correct_answer
        self.preferred_side_chosen = self.chooser_choice == self.get_preferred_side()

    def get_fine_amount(self):
        if not self.fine_condition:  # If fine_condition is None or empty
            # Get from participant.vars if available, otherwise default to 'small'
            self.fine_condition = self.participant.vars.get('fine_condition', 'small')
        
        if self.fine_condition == 'small':
            return Constants.small_fine
        elif self.fine_condition == 'large':
            return Constants.large_fine
        else:
            return Constants.small_fine  # Default to small fine if something goes wrong

class ComprehensionResponse(ExtraModel):
    """Model to store incorrect comprehension check responses"""
    player = models.Link(Player)
    field_name = models.StringField()
    response = models.StringField()
    timestamp = models.StringField()
    attempt_number = models.IntegerField()
    

    
    
def vars_for_admin_report(subsession):

    return {
        'num_participants': len(subsession.get_players()),
        'mean_tempting_rounds_per_player': sum(player.is_tempting_round for player in subsession.get_players()) / len(subsession.get_players()) if subsession.get_players() else 0,
        'num_timeouts': sum(player.timeout_occurred for player in subsession.get_players()),
        'num_dropout_players': sum(player.participant.is_dropout for player in subsession.get_players()),
            }

# PAGES



class MobileCheck(Page):
    form_model = 'player'
    form_fields = ['is_mobile']
    def is_displayed(player):
        return player.round_number == 1
    
    def get_timeout_seconds(player: Player):
        return 0  
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        # Store mobile status in participant vars for persistence across rounds
        player.participant.vars['is_mobile'] = player.is_mobile
        

class MobileBlock(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('is_mobile', False)

class WelcomePage(Page):
    form_model = 'player'
    form_fields = ['prolific_id', 'age', 'gender']
    
    def is_displayed(player):
        if player.round_number == 1:
            player.experiment_start_time = time.time()
            player.experiment_date = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime())
        return (player.round_number == 1 and 
                not player.is_repeat_participant and 
                not player.participant.vars.get('is_mobile', False) and 
                not Constants.debug)
    
    def vars_for_template(player):

        min_waiting_comp_minutes = int(Constants.min_waiting_for_compensation / 60)
        return {
            'participation_fee': Constants.participation_fee,
            'bonus_fee': Constants.bonus_fee,
            'waiting_compensation_minutes': min_waiting_comp_minutes,
            'waiting_compensation_fee': Constants.waiting_compensation_fee,
            'estimated_minutes': Constants.estimated_minutes,
            'is_zoom': Constants.is_zoom,
        }
    
    def before_next_page(player, timeout_happened):
        if not player.validate_prolific_id():
            #print("Repeat participant detected1")
            player.is_repeat_participant = True
            player.participant.vars['is_repeat_participant'] = True
        player.participant.vars['age'] = player.age
        player.participant.vars['gender'] = player.gender

    def app_after_this_page(player, upcoming_apps):
        if player.is_repeat_participant:
            #print("Repeat participant detected")
            return 'repeat_participant'

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['comp_fine_amount', 'comp_preferred_side']
    
    def is_displayed(player):
        if player.round_number == 1:
            player.comprehension_start_time = time.time()
        return (player.round_number == 1 and 
                not player.passed_comprehension and 
                not player.failed_comprehension and  # Only show on first attempt
                not Constants.debug)

    @staticmethod
    def error_message(player: Player, values):
        from datetime import datetime
        
        # Increment attempt counter
        current_attempts = player.field_maybe_none('comprehension_attempts') or 0
        player.comprehension_attempts = current_attempts + 1
        
        # Define correct answers
        solutions = {
            'comp_fine_amount': player.get_fine_amount(),
            'comp_preferred_side': player.get_preferred_side()
        }
        
        # Check for errors and store wrong answers
        has_errors = False
        for name, solution in solutions.items():
            if values[name] != solution:
                has_errors = True
                # Store the wrong answer
                ComprehensionResponse.create(
                    player=player,
                    field_name=name,
                    response=str(values[name]),
                    timestamp=datetime.now().isoformat(),
                    attempt_number=current_attempts
                )

        if has_errors:
            player.failed_comprehension = True
            return None  # Don't show error message, just redirect to ComprehensionFailed
        
        # If no errors, mark as passed
        player.passed_comprehension = True
        return None

    def before_next_page(player, timeout_happened):
        # This ensures we redirect to ComprehensionFailed if there were errors
        if player.failed_comprehension:
            return 'comprehension_failed'
        
'''
def custom_export(players):
    """Custom export for comprehension check data"""
    # Headers
    yield [
        'participant_code',
        'participant_id_in_session',
        'round_number',
        'field_name',
        'response',
        'correct_answer',
        'attempt_number',
        'timestamp',
        'condition'  # small/large fine condition
    ]
    
    # Get all responses
    responses = ComprehensionResponse.filter()
    
    for resp in responses:
        player = resp.player
        participant = player.participant
        
        # Get correct answer for this field
        if resp.field_name == 'comp_fine_amount':
            correct_answer = str(player.get_fine_amount())
        else:  # comp_preferred_side
            correct_answer = player.get_preferred_side()
        
        yield [
            participant.code,
            participant.id_in_session,
            player.round_number,
            resp.field_name,
            resp.response,
            correct_answer,
            resp.attempt_number,
            resp.timestamp,
            player.fine_condition
        ]   

'''

# Add this to your __init__.py file

def custom_export(players):
    """
    Custom export combining both comprehension check data and timing metrics.
    Creates two separate sections in the export file.
    """
    # Section 1: Comprehension Check Data
    yield ['SECTION: COMPREHENSION CHECK DATA']
    yield [
        'participant_code',
        'participant_id_in_session',
        'round_number',
        'field_name',
        'response',
        'correct_answer',
        'attempt_number',
        'timestamp',
        'condition'
    ]
    
    # Get all comprehension responses
    responses = ComprehensionResponse.filter()
    
    for resp in responses:
        player = resp.player
        participant = player.participant
        
        # Get correct answer for this field
        if resp.field_name == 'comp_fine_amount':
            correct_answer = str(player.get_fine_amount())
        else:  # comp_preferred_side
            correct_answer = player.get_preferred_side()
        
        yield [
            participant.code,
            participant.id_in_session,
            player.round_number,
            resp.field_name,
            resp.response,
            correct_answer,
            resp.attempt_number,
            resp.timestamp,
            player.fine_condition
        ]
    
    # Empty row to separate sections
    yield []
    yield ['SECTION: EXPERIMENT DATA']
    
    # Section 2: Timing and Game Data
    # Header row for experiment data
    yield [
        # Participant identifiers
        'session_code',
        'participant_code',
        'participant_label',
        'round_number',
        
        # Condition and role information
        'fine_condition',       # 'small' or 'large'
        'condition_phase',      # 'first' or 'second'
        'fine_amount',          # actual value: 11 or 99
        'role_in_experiment',
        
        # Response times
        'moderator_decision_time',
        'chooser_decision_time',
        
        # Phase timing measurements
        'instruction_time',
        'training_time',
        'comprehension_time',
        'total_experiment_time',
        'total_waiting_time',
        
        # Game-specific data
        'chooser_choice',
        'choice_correct',
        'preferred_side_chosen',
        'decision',
        'round_chooser_points',
        'round_moderator_points',
        'total_chooser_points',
        'total_moderator_points',
        
        # Trial information
        'is_tempting_round',
        'dots_left',
        'dots_right',
        'correct_answer',
        'timeout_occurred_moderator',
        
        # Additional metrics
        'comprehension_attempts',
        'passed_comprehension',
    ]

    # Data rows for experiment data
    for p in players:
        participant = p.participant
        session = p.session
        
        # Calculate derived timing metrics
        instruction_time = (p.field_maybe_none('instruction_end_time') or 0) - (p.field_maybe_none('instruction_start_time') or 0)
        training_time = (p.field_maybe_none('training_end_time') or 0) - (p.field_maybe_none('training_start_time') or 0)
        comprehension_time = (p.field_maybe_none('comprehension_end_time') or 0) - (p.field_maybe_none('comprehension_start_time') or 0)
        total_experiment_time = (p.field_maybe_none('experiment_end_time') or 0) - (p.field_maybe_none('experiment_start_time') or 0)
        
        # Determine condition phase and fine amount
        condition_phase = 'first' if p.round_number <= Constants.rounds_per_condition else 'second'
        fine_amount = Constants.small_fine if p.fine_condition == 'small' else Constants.large_fine
        
        yield [
            # Participant identifiers
            session.code,
            participant.code,
            participant.label,
            p.round_number,
            
            # Condition and role information
            p.field_maybe_none('fine_condition'),
            condition_phase,
            fine_amount,
            p.field_maybe_none('role_in_experiment'),
            
            # Response times
            p.field_maybe_none('moderator_decision_time'),
            p.field_maybe_none('chooser_decision_time'),
            
            # Phase timing measurements
            instruction_time,
            training_time,
            comprehension_time,
            total_experiment_time,
            p.field_maybe_none('total_waiting_time'),
            
            # Game-specific data
            p.field_maybe_none('chooser_choice'),
            p.field_maybe_none('choice_correct'),
            p.field_maybe_none('preferred_side_chosen'),
            p.field_maybe_none('decision'),
            p.field_maybe_none('round_chooser_points'),
            p.field_maybe_none('round_moderator_points'),
            p.field_maybe_none('total_chooser_points'),
            p.field_maybe_none('total_moderator_points'),
            
            # Trial information
            p.field_maybe_none('is_tempting_round'),
            p.field_maybe_none('dots_left'),
            p.field_maybe_none('dots_right'),
            p.field_maybe_none('correct_answer'),
            p.field_maybe_none('timeout_occurred_moderator'),
            
            # Additional metrics
            p.field_maybe_none('comprehension_attempts'),
            p.field_maybe_none('passed_comprehension'),
        ]
        
class ComprehensionFailed(Page):
    form_model = 'player'
    form_fields = ['comp_fine_amount', 'comp_preferred_side']
    
    def is_displayed(player):
        return (player.round_number == 1 and 
                player.failed_comprehension and 
                not Constants.debug)

    def vars_for_template(player):
        return {
            'fine_amount': player.get_fine_amount(),
            'preferred_side': player.get_preferred_side(),
            'bonus_points': Constants.preferred_side_points,
            'display_seconds': Constants.dots_display_seconds,
            'attempts': player.comprehension_attempts
        }
    
    @staticmethod
    def error_message(player: Player, values):
        from datetime import datetime
        
        # Increment attempt counter
        player.comprehension_attempts += 1
        current_attempt = player.comprehension_attempts
        
        # Define correct answers
        solutions = {
            'comp_fine_amount': player.get_fine_amount(),
            'comp_preferred_side': player.get_preferred_side()
        }
        
        # Check for errors
        errors = {}
        for name, solution in solutions.items():
            if values[name] != solution:
                ComprehensionResponse.create(
                    player=player,
                    field_name=name,
                    response=str(values[name]),
                    timestamp=datetime.now().isoformat(),
                    attempt_number=current_attempt
                )
                errors[name] = 'Incorrect answer. Please review the instructions above carefully.'
        
        if errors:
            player.failed_comprehension = True
            return errors
        
        # If no errors, mark as passed
        player.passed_comprehension = True
        player.failed_comprehension = False
        return None

    def app_after_this_page(player, upcoming_apps):
        if player.passed_comprehension:
            return None  # Continue with the experiment
        return None  # Stay on this page if answers are wrong

class ProlificID(Page):
    form_model = 'player'
    form_fields = ['prolific_id']
    
    def is_displayed(player):  # Changed from self to player
        return player.round_number == 1 and not player.is_repeat_participant and not Constants.debug

    def before_next_page(player, timeout_happened):  # Changed from self to player
        if not player.validate_prolific_id():
            player.is_repeat_participant = True

    def app_after_this_page(player, upcoming_apps):  # Changed from self to player
        if player.is_repeat_participant:
            return 'repeat_participant'
        
class RepeatParticipant(Page):
    def is_displayed(player):  # Changed from self to player
        return player.is_repeat_participant and not Constants.debug

    def vars_for_template(player):  # Changed from self to player
        return {
            'participation_fee': Constants.participation_fee
        }

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education']
    
    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug
    
class Instructions(Page):
    def is_displayed(player):
        if player.round_number == 1:
            player.instruction_start_time = time.time() #BUG THE SAME AS INSTRUCTION END!!!
        return player.round_number == 1 and not Constants.debug

    def vars_for_template(player):
        return {
            'fine_amount': player.get_fine_amount(),  # Get player's specific fine amount
            'preferred_side': player.get_preferred_side(),
            'preferred_side_points': Constants.preferred_side_points,
            'display_seconds': Constants.dots_display_seconds,
            'num_rounds': Constants.num_rounds,
            'participation_fee': Constants.participation_fee,
            'bonus_fee': Constants.bonus_fee,
            'decision_timeout_seconds': Constants.decision_timeout_seconds,
            'moderator_points_per_correct': Constants.moderator_points_per_correct,
            'timeout_penalty': Constants.timeout_penalty,
            'is_within': Constants.is_within_session,
           
        }
    
    def before_next_page(player, timeout_happened):
        player.instruction_end_time = time.time()




#setup page to generate dots for each player
class SetUp(Page):
    def get_timeout_seconds(player: Player):
        return Constants.fixation_display_seconds
    
    
    def before_next_page(self, timeout_happened):
        for player in self.group.get_players(): #FIXME remove "for" for singleplayer
            if Constants.is_multiplayer:
                #player.generate_pair_dot_counts()
                pass
            else:
                player.generate_dot_counts()

#class SetUp(WaitPage):
#    wait_for_all_groups = False  # Proceed immediately without waiting
#
#    def after_all_players_arrive(self):
#        for player in self.group.get_players():
#            player.generate_dot_counts()



class WaitForModeratorDecision(WaitPage):
    """waiting page - Moderator wait for Chooser's choice"""
    
    body_text = "Waiting for Moderator's review"
    template_name = 'pilot_multiplayer/WaitForModeratorDecision.html'

    def is_displayed(self):
        self.participant.vars['wait_start_time'] = time.time()
        return self.role == Constants.CHOOSER_ROLE
    
    
    def vars_for_template(self):

        return {
            'round_number': self.subsession.round_number,
        }
    

    def after_all_players_arrive(group: Group):
        for player in group.get_players():
            waiting_time = time.time() - player.participant.vars.get('wait_start_time', time.time())
            player.participant.total_waiting_time += waiting_time
            player.total_waiting_time = player.participant.total_waiting_time

            if player.role == Constants.CHOOSER_ROLE:
                if not player.choice_correct:
                    player.moderator_decision_time = player.group.chooser_rt_group
                    player.decision = player.group.moderator_decision_group
    
            print(f"Waiting time: {waiting_time} for participant {player.participant.id_in_session}")
            print(f"participant Total waiting time: {player.participant.total_waiting_time}")
    
class WaitForChooserChoice(WaitPage):
    """waiting page - Moderator wait for Chooser's choice"""
    body_text = "Waiting for Chooser's choice"
    template_name = 'pilot_multiplayer/WaitForChooserChoice.html'


    def is_displayed(self):
        self.participant.vars['wait_start_time'] = time.time()
        return self.role == Constants.MODERATOR_ROLE
    
    
    def vars_for_template(self):

        return {
            'round_number': self.subsession.round_number,
        }
    

    def after_all_players_arrive(group: Group):
        for player in group.get_players():
            waiting_time = time.time() - player.participant.vars.get('wait_start_time', time.time())
            player.participant.total_waiting_time += waiting_time
            player.total_waiting_time = player.participant.total_waiting_time

            if player.role == Constants.MODERATOR_ROLE:
                player.chooser_choice_time = player.group.chooser_rt_group
                player.chooser_choice = player.group.chooser_choice_group
    
            print(f"Waiting time: {waiting_time} for participant {player.participant.id_in_session}")
            print(f"participant Total waiting time: {player.participant.total_waiting_time}")


class PairingParticipants(WaitPage):
    wait_for_all_groups = True
    #title_text = "Please wait"
    body_text = ""
    template_name = 'pilot_multiplayer/PairingParticipants.html'

    
    def is_displayed(self):
        self.participant.vars['wait_start_time'] = time.time()
        #other_role = 'Moderator' if self.role == Constants.CHOOSER_ROLE else 'Chooser'
        #body_text = f"Pairing you with a {other_role}. The Game will start automatically after pairing has completed."
        return True
    
    
    def after_all_players_arrive(subsession):

        
        for group in subsession.get_groups():
            for player in group.get_players():
                
                #player.my_page_timeout_seconds = 5
                waiting_time = time.time() - player.participant.vars.get('wait_start_time', time.time())

                player.participant.total_waiting_time += waiting_time
                player.total_waiting_time += player.participant.total_waiting_time
            
                print(f"Waiting time1: {waiting_time} for participant {player.participant.id_in_session}")
                print(f"participant Total waiting time22: {player.participant.total_waiting_time}")        
    

class WaitingForOtherToFinishInstructions(WaitPage):
    """Simulated waiting page for pairing participants"""
    wait_for_all_groups = True
    title_text = "Waiting for other participants to finish instructions"
    body_text = "Please wait while other participants finish the instructions"
    #group_by_arrival_time = True

    def is_displayed(self):
        if self.round_number == 1:
            self.comprehension_end_time = time.time()
            self.participant.vars['wait_start_time'] = time.time()
        return self.round_number == 1
    
    @staticmethod
    
    
    #def vars_for_template(player):
    #    player.participant.vars['wait_start_time'] = time.time()
    #    return {}
    
    def after_all_players_arrive(subsession):
        
        for group in subsession.get_groups():
            for player in group.get_players():
                waiting_time = time.time() - player.participant.vars.get('wait_start_time', time.time())

                player.participant.total_waiting_time += waiting_time
                player.total_waiting_time = player.participant.total_waiting_time
            
                print(f"Waiting time1: {waiting_time} for participant {player.participant.id_in_session}")
                print(f"participant Total waiting time22: {player.participant.total_waiting_time}")
        
    
    
            


class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1
    
    #def before_next_page(player, timeout_happened):
    #    player.generate_dot_counts()
    
    
class DotDisplay(Page):
    timeout_seconds = Constants.dots_display_seconds  # Display dots for 5 seconds
    
    def vars_for_template(self):
        return {
            #'dots': self.generate_dot_positions(), SP
            'dots': self.get_pair_dot_positions(),  # Use the method to get dot positions in multiplayer
            'display_seconds': Constants.dots_display_seconds,
            'round_number': self.subsession.round_number,
            'is_zoom': Constants.is_zoom,
        }
    
    
    
class ModeratorChoiceDisplay(Page):
    form_model = 'player'
    form_fields = []
    timer_text = 'Time remaining to make a decision:'


    def get_timeout_seconds(player):
        print(f"player dropout status: {player.participant.is_dropout}" )
        if player.participant.is_dropout:
            print("Player is dropout, random timeout")
            return random.randint(3, 7)  # Random timeout for dropout players
        else:
            return Constants.decision_timeout_seconds

    @staticmethod
    def is_displayed(player):
        # Only record the choice if it hasn't been recorded yet
        if player.field_maybe_none('chooser_choice') is None:
            player.record_participant_choice()
            
           # print("Choice recorded:")
            #rint(f"Decision: {player.field_maybe_none('decision')}")
            #print(f"Fine amount: {player.get_fine_amount()}")
            #print(f"Participant choice: {player.chooser_choice}")
            #print(f"Correct answer: {player.correct_answer}")
            #print(f"Choice correct: {player.choice_correct}")
            #print(f"Preferred side chosen: {player.preferred_side_chosen}")

        else:
            player.chooser_choice = player.group.chooser_choice_group
            player.choice_correct = player.group.choice_correct_group
            player.preferred_side_chosen = player.group.preferred_side_chosen_group

        return player.role == Constants.MODERATOR_ROLE
    
    def vars_for_template(self):
        return {
            'round_number': self.subsession.round_number,
            'chooser_choice': self.chooser_choice,
            'choice_correct': self.choice_correct,
            'preferred_side_chosen': self.preferred_side_chosen,
            'fine_amount': self.get_fine_amount(),
            'correct_answer': self.correct_answer,
            'dots_left': self.dots_left,
            'dots_right': self.dots_right,
            'payoff_punish': 10 - self.get_fine_amount() if self.preferred_side_chosen else -self.get_fine_amount(),
            'payoff_warn': 10 if self.preferred_side_chosen else 0,
        }

    @staticmethod
    def live_method(player, data):
        try:
            if 'decision' in data:
                player.decision = data['decision']
                player.moderator_decision_time = data.get('decision_time', 0)

                player.group.moderator_rt_group = player.moderator_decision_time
                player.group.moderator_decision_group = player.decision

                return {player.id_in_group: dict(decision_made=True)}
        except Exception as e:
            print(f"Error in live_method: {e}")
            return {player.id_in_group: dict(error=True)}
        
    def before_next_page(player, timeout_happened):
        #print("Before next page")
        if timeout_happened:
            print("Timeout occurred")
            # Make random choice and apply penalty
            #if not choice_correct - generate random choice
            if not player.choice_correct:
                player.decision = random.choice(['punish', 'warn'])
                player.group.moderator_decision_group = player.decision

            player.timeout_occurred_moderator = True
            player.timeout_occurred = True  # Set timeout flag for the player
            player.participant.timeout_num += 1
            if player.round_number > 1:
                player.subsequent_timeouts = player.in_round(player.round_number - 1).subsequent_timeouts + 1
            else:
                player.subsequent_timeouts = 1

            if player.round_number >= 4:
                a = player.in_round(player.round_number - 1).timeout_occurred
                b = player.in_round(player.round_number - 2).timeout_occurred
                c = player.in_round(player.round_number - 3).timeout_occurred
                if player.timeout_occurred and a and b and c:
                    print("4 consecutive timeouts occurred - Moderator")
                    #change player to dropout
                    player.is_dropout = True
                    player.participant.is_dropout = True
                    
            
            # Apply timeout penalty
            #player.total_moderator_points = player.participant.total_moderator_points
            #print(f"total_moderator_points: {player.field_maybe_none('total_moderator_points')}")
            #print(f"player.participant.total_moderator_points: {player.participant.total_moderator_points}")
            #current_total = player.field_maybe_none('total_moderator_points') or 0 # maybe this?
            #print(f"current_total: {current_total}")
            #player.total_moderator_points = current_total - Constants.timeout_penalty
            #player.participant.total_moderator_points = player.total_moderator_points
            #print(f"total_moderator_points after penalty: {player.total_moderator_points}")
            
            
        
        

class FullFeedback(Page):
   
    def get_timeout_seconds(player):
        if player.choice_correct:
            return Constants.feedback_timeout_correct
        else:
            return Constants.feedback_timeout_incorrect

    def is_displayed(player):
        return True #display feedback for all rounds, not just the wrong ones
    
    def vars_for_template(self):
        # Calculate round payoff based on the scenario
        round_payoff = 0
        alternative_payoff = 0
        #print("fullfeedback")
        #print(f"Decision: {self.field_maybe_none('decision')}")
        #print(f"Fine amount: {self.get_fine_amount()}")
        #print(f"Participant choice: {self.chooser_choice}")
        #print(f"Correct answer: {self.correct_answer}") #BUG why have both??? 
        #print(f"Choice correct: {self.choice_correct}") #BUG why have both???
        #print(f"Preferred side chosen: {self.preferred_side_chosen}")

        if self.timeout_occurred:
            # If timeout occurred, apply penalty
            round_payoff = -Constants.timeout_penalty
            alternative_payoff = 0
        else:
            if self.choice_correct:
                # For correct choices, payoff only depends on preferred side
                round_payoff = 10 if self.preferred_side_chosen else 0
                alternative_payoff = 0 if self.preferred_side_chosen else 10
            else:
                # For incorrect choices, check the moderator's decision
                decision = self.field_maybe_none('decision')
                if decision == 'punish':
                    round_payoff = 10 - self.get_fine_amount() if self.preferred_side_chosen else -self.get_fine_amount()
                    alternative_payoff = 10 if self.preferred_side_chosen else 0  # if warned instead
                elif decision == 'warn':
                    round_payoff = 10 if self.preferred_side_chosen else 0
                    alternative_payoff = 10 - self.get_fine_amount() if self.preferred_side_chosen else -self.get_fine_amount()  # if punished instead
                else:
                    # Handle unexpected cases
                    round_payoff = 0
                    alternative_payoff = 0

        self.round_chooser_alternative_points = alternative_payoff

        return {
            'timeout_occurred': self.timeout_occurred,
            'timeout_seconds': Constants.decision_timeout_seconds,
            'timeout_penalty': Constants.timeout_penalty,
            'decision': self.field_maybe_none('decision'),
            'alternative': 'warn' if self.field_maybe_none('decision') == 'punish' else 'punish',
            'fine_amount': self.get_fine_amount(),
            'chooser_choice': self.chooser_choice,
            'correct_answer': self.correct_answer,
            'choice_correct': self.choice_correct,  # This boolean controls which feedback is shown
            'preferred_side_chosen': self.preferred_side_chosen,
            'payoff_punish': 10 - self.get_fine_amount() if self.preferred_side_chosen else -self.get_fine_amount(),
            'payoff_warn': 10 if self.preferred_side_chosen else 0,
            'round_number': self.subsession.round_number,
            'round_payoff': round_payoff,
            'alternative_payoff': alternative_payoff,
            'moderator_points_if_correct': Constants.moderator_points_per_correct,  # Add moderator points
            'preferred_side_points': Constants.preferred_side_points,  # Add preferred side points
        }
    

    def before_next_page(player, timeout_happened):
        # Calculate chooser's points for this round
        chooser_round_payoff = 0
        
        if player.choice_correct:
            # For correct choices, only consider preferred side bonus
            chooser_round_payoff = 10 if player.preferred_side_chosen else 0
        else:
            # For incorrect choices, consider the moderator's decision
            decision = player.field_maybe_none('decision')
            if decision == 'punish':
                chooser_round_payoff = (10 - player.get_fine_amount() if player.preferred_side_chosen 
                                      else -player.get_fine_amount())
            else:  # warning or no decision
                chooser_round_payoff = 10 if player.preferred_side_chosen else 0
        
        # Save points for this round
        player.round_chooser_points = chooser_round_payoff
        if not player.timeout_occurred_moderator:
            player.round_moderator_points = 10 if player.choice_correct and not player.timeout_occurred_moderator else 0 #TODO check
        else:
            player.round_moderator_points = 0 - Constants.timeout_penalty
        
        # Get current totals (using 0 if None)
        #current_chooser_total = player.field_maybe_none('total_chooser_points') or 0
        #current_moderator_total = player.field_maybe_none('total_moderator_points') or 0
        #current_chooser_total = player.participant.vars['total_chooser_points'] or 0

        # Update totals
        if player.role == Constants.CHOOSER_ROLE:
            current_moderator_total = player.get_others_in_group()[0].participant.total_moderator_points or 0
            current_chooser_total = player.participant.vars['total_chooser_points'] or 0
        else:
            current_moderator_total = player.participant.vars['total_moderator_points'] or 0
            current_chooser_total = player.get_others_in_group()[0].participant.total_chooser_points or 0

        player.participant.total_chooser_points = current_chooser_total + player.round_chooser_points
        player.participant.total_moderator_points = current_moderator_total + player.round_moderator_points
        player.total_chooser_points = player.participant.total_chooser_points
        player.total_moderator_points = player.participant.total_moderator_points

        if player.role == Constants.CHOOSER_ROLE:

            player.participant.total_points += player.round_chooser_points
            player.total_points = player.participant.total_points

        elif player.role == Constants.MODERATOR_ROLE:
            player.participant.total_points += player.round_moderator_points
            player.total_points = player.participant.total_points

    
class Lottery(Page):
    timeout_seconds = 0  # do not show this page
    def is_displayed(player):
        return player.round_number == Constants.num_rounds
    
    
    def before_next_page(player, timeout_happened):
        #check if participant won the lottery #TODO need to be in a page before - now if refreshing doing lottery again
        winning_prob = (player.participant.total_points-Constants.expectation_average_points)/100
        random_number = random.random()
        player.lottery_won = random_number < winning_prob
        player.total_monetary_payoff = Constants.participation_fee + (Constants.bonus_fee if player.lottery_won else 0)
        print(f"winnig prob: {winning_prob}")
        print(f"random number: {random_number}")
        print(f"lottery won: {player.lottery_won}")
        print(f"total points: {player.participant.total_points}")

        #check if player is aligible for compensation for waiting time
        if player.participant.total_waiting_time > Constants.min_waiting_for_compensation:
            player.got_waiting_compensation = True
            #calculate bonus
            seconds_reference = Constants.waiting_compensation_minutes_for_reference * 60
            time_ratio = player.participant.total_waiting_time / seconds_reference
            waiting_compensation = Constants.waiting_compensation_fee * time_ratio
            player.waiting_compensation = waiting_compensation
            player.total_monetary_payoff += waiting_compensation
        
        print(f"total monetary payoff: {player.total_monetary_payoff}")
        print(f"player.payoff: {player.payoff}")
        print(f"player.total_monetary_payoff - Constants.participation_fee: {player.total_monetary_payoff - Constants.participation_fee}")
        player.payoff = player.total_monetary_payoff - Constants.participation_fee
        print(f"updated player.payoff: {player.payoff}")
        #player.participant.payoff = player.total_monetary_payoff



class Results(Page):
    def is_displayed(player):
        if player.round_number == Constants.num_rounds:
            player.experiment_end_time = time.time()
            player.finished = True
            player.participant.finished = True

            #player.participant.finished = True
        return player.round_number == Constants.num_rounds 
    
    def vars_for_template(player):
        total_waiting_time_minutes = int(player.participant.total_waiting_time // 60)
        waiting_remaining_seconds = int(player.participant.total_waiting_time % 60)
        waiting_time_string = f"{total_waiting_time_minutes}:{waiting_remaining_seconds:02d}"

        return {
            'experiment_role': player.role_in_experiment,
            'total_chooser_points': player.total_chooser_points,
            'total_moderator_points': player.total_moderator_points,
            'participation_fee': Constants.participation_fee,
            'lottery_won': player.lottery_won,
            'bonus_fee': Constants.bonus_fee,
            'total_fee': player.total_monetary_payoff,
            'completion_code': player.session.config['completionCode'],
            'waiting_time': waiting_time_string,
            'got_waiting_compensation': player.got_waiting_compensation,
            'waiting_compensation': player.waiting_compensation,
            'waiting_compensation_minutes': int(Constants.min_waiting_for_compensation // 60),
            'is_zoom': Constants.is_zoom,
        }
    

    #training pages
class TrainingIntro(Page):
    def is_displayed(player):
        if player.round_number == 1:
            player.training_start_time = time.time()
        return player.round_number == 1 and not Constants.debug
    
    def vars_for_template(player):
        return {
            'fine_amount': player.get_fine_amount(),
            'preferred_side': player.get_preferred_side(),
            'preferred_side_points': Constants.preferred_side_points,
        }
    
class TrainingSetUp(Page): #HACK Maybe this Fixation cross is better?????
    def get_timeout_seconds(player):
        return Constants.fixation_display_seconds
    
    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug
    
    def before_next_page(player, timeout_happened):
        # Generate dots for the training display
        player.generate_dot_counts()


class TrainingChooserDisplay(Page): 
    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug
    
    timeout_seconds = Constants.dots_display_seconds
    
    def vars_for_template(player):
        # Generate dots for training
        player.generate_dot_counts()  # Reuse existing method
        return {
            'dots': player.generate_dot_positions(),  # Reuse existing method
            'display_seconds': Constants.dots_display_seconds,
        }

class TrainingChooserChoice(Page):
    form_model = 'player'
    form_fields = ['training_choice']
    
    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug

    def vars_for_template(player):
        #define text on the buttons. if right is preffered, right button text = 'Right (10)' and left button text = 'Left (0)'
        if player.get_preferred_side() == 'right':
            right_text = f'Right Side ({Constants.preferred_side_points})'
            left_text = 'Left Side (0)'
        else:
            right_text = 'Right Side (0)'
            left_text = f'Left Side ({Constants.preferred_side_points})'

        return {
            'correct_answer': player.correct_answer,
            'dots_left': player.dots_left,
            'dots_right': player.dots_right,
            'right_text': right_text,
            'left_text': left_text
        }
    
    @staticmethod
    def live_method(player, data):
        if 'choice' in data:
            player.training_choice = data['choice']
            return {player.id_in_group: dict(choice_recorded=True)}
        return {player.id_in_group: dict(error=True)}

class TrainingChooserFeedback(Page):
    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug

    def vars_for_template(player):
        choice_correct = player.training_choice == player.correct_answer
        preferred_side_chosen = player.training_choice == player.get_preferred_side()
        return {
            'choice': player.training_choice,
            'correct_answer': player.correct_answer,
            'choice_correct': choice_correct,
            'preferred_side_chosen': preferred_side_chosen,
            'preferred_side': player.get_preferred_side(),
            'points': 10 if preferred_side_chosen else 0,
        }

class TrainingModeratorCorrect(Page):
    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug

    def vars_for_template(player):
        return {
            'preferred_side': player.get_preferred_side(),
            'preferred_side_points': Constants.preferred_side_points,
            'training_choice': player.training_choice,
            'chooser_got': Constants.preferred_side_points if player.training_choice == player.get_preferred_side() else 0,
        }

class TrainingModeratorIncorrect(Page):
    form_model = 'player'
    form_fields = ['training_decision']
    
    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug

    def vars_for_template(player):
        return {
            'fine_amount': player.get_fine_amount(),
            'preferred_side': player.get_preferred_side(),
            'preferred_side_points': Constants.preferred_side_points,
            'payoff_punish': Constants.preferred_side_points - player.get_fine_amount() if player.training_choice == player.get_preferred_side() else -player.get_fine_amount(),  
            'payoff_warn': Constants.preferred_side_points if player.training_choice == player.get_preferred_side() else 0,  # Points for preferred side without punishment
            'training_choice': player.training_choice,
            'chooser_got': Constants.preferred_side_points if player.training_choice == player.get_preferred_side() else 0,
        }

class TrainingComplete(Page):

    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug
    

    def vars_for_template(player):
        # Chooser role feedback
        choice_correct = player.training_choice == player.correct_answer
        preferred_side_chosen = player.training_choice == player.get_preferred_side()
        preferred_side = player.get_preferred_side()
        
        # Calculate points based on choices
        base_points = 10 if preferred_side_chosen else 0
        
        # If choice was incorrect and player decided to punish
        if not choice_correct and player.training_decision == 'punish':
            final_points = base_points - player.get_fine_amount()
            alternative_points = base_points  # if warned instead
        else:
            final_points = base_points
            alternative_points = base_points - player.get_fine_amount()  # if punished instead
        
        return {
            'choice': player.training_choice,
            'correct_answer': player.correct_answer,
            'choice_correct': choice_correct,
            'preferred_side': preferred_side,
            'preferred_side_chosen': preferred_side_chosen,
            'decision': player.training_decision,
            'final_points': final_points,
            'alternative_points': alternative_points,
            'fine_amount': player.get_fine_amount(),
            # Calculate payoffs for the alternative choice
            'payoff_punish': (10 if player.training_choice != player.get_preferred_side() else 0) - player.get_fine_amount(),
            'payoff_warn': 10 if player.training_choice != player.get_preferred_side() else 0
        }

    def before_next_page(player, timeout_happened):
        player.participant.vars['passed_training'] = True
        player.training_end_time = time.time()


class End_Questionnaire_Moderator(Page):
    """Page for collecting participant feedback before showing results"""
    
    form_model = 'player'
    form_fields = ['effectiveness_rating', 'fairness_rating_1', 'fairness_rating_2', 'additional_comments']
    
    def is_displayed(player):
        # Display only in the final round
        return player.round_number == Constants.num_rounds and player.role == Constants.MODERATOR_ROLE
    
    def before_next_page(player, timeout_happened):
        # Store the answers in participant vars for easy access in later analysis
        player.participant.vars['effectiveness_rating'] = player.effectiveness_rating
        player.participant.vars['fairness_rating_1'] = player.fairness_rating_1
        player.participant.vars['fairness_rating_2'] = player.fairness_rating_2

        player.participant.vars['additional_comments'] = player.additional_comments


class End_Questionnaire_Chooser(Page): #TODO CHANGE ACCORDINGLY
    """Page for collecting participant feedback before showing results"""
    
    form_model = 'player'
    form_fields = ['effectiveness_rating', 'fairness_rating_1', 'fairness_rating_2', 'additional_comments']
    
    def is_displayed(player):
        # Display only in the final round
        return player.round_number == Constants.num_rounds and player.role == Constants.CHOOSER_ROLE
    
    def before_next_page(player, timeout_happened):
        # Store the answers in participant vars for easy access in later analysis
        player.participant.vars['effectiveness_rating'] = player.effectiveness_rating
        player.participant.vars['fairness_rating_1'] = player.fairness_rating_1
        player.participant.vars['fairness_rating_2'] = player.fairness_rating_2

        player.participant.vars['additional_comments'] = player.additional_comments

'''
class AttentionCheck(Page):
    form_model = 'player'
    form_fields = ['attention_check_fine']
    
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

    def vars_for_template(player):
        if player.fine_condition == 'small':
            choices = [
                [5, "5 points"],
                [11, "11 points"],
                [20, "20 points"],
                [50, "50 points"], 
                [99, "99 points"],
                [150, "150 points"]
            ]
        else:  # large fine condition
            choices = [
                [11, "11 points"],
                [50, "50 points"],
                [75, "75 points"],
                [99, "99 points"],
                [120, "120 points"],
                [150, "150 points"]
            ]
        return {
            'choices': choices
        }

    def before_next_page(player, timeout_happened):
        # Store the correct fine amount based on condition
        player.correct_fine_amount = Constants.small_fine if player.fine_condition == 'small' else Constants.large_fine
        
        # Check if answer matches their condition and store results
        player.attention_check_passed = (player.attention_check_fine == player.correct_fine_amount)
        
        # Calculate and store the deviation (can be positive or negative)
        player.attention_check_answer = player.attention_check_fine
'''


class TransitionPage(Page):
    """Page shown after the first part rounds to inform about the condition change"""
    timeout_seconds = Constants.TransitionPage_timeout_seconds  # Display for X seconds
    timer_text = 'Proceeding to part 2 in:'

    
    def is_displayed(player):
        return player.round_number == Constants.transition_round and Constants.is_within_session

   
    
    
    def vars_for_template(player):
        old_fine = Constants.small_fine if player.participant.vars['initial_fine_condition'] == 'small' else Constants.large_fine
        new_fine = Constants.large_fine if player.participant.vars['initial_fine_condition'] == 'small' else Constants.small_fine
        
        return {
            'old_fine': old_fine,
            'new_fine': new_fine,
            'increasing': new_fine > old_fine,
            'proceeding_seconds': Constants.TransitionPage_timeout_seconds,
        }


class Role_Assignment(Page):
    """Page to display the participant's assigned role"""
    
    timeout_seconds = 30  # Auto-proceed after 20 seconds
    timer_text = 'Time remaining to review your role:'
    
    def is_displayed(player):
        return player.round_number == 1 #and not Constants.debug 
    
    def vars_for_template(player):
        # Get the role display name for better presentation
        role_display = "Moderator" if player.role == Constants.MODERATOR_ROLE else "Chooser"
        
        return {
            'role_display': role_display,
            'role': player.role,
            'is_moderator': player.role == Constants.MODERATOR_ROLE,
            'is_chooser': player.role == Constants.CHOOSER_ROLE,
        }
    
    def before_next_page(player, timeout_happened):
        # Store role assignment confirmation in participant vars
        player.participant.vars['role_confirmed'] = True
        player.participant.vars['role_assignment_time'] = time.time()
        
        # Track if participant waited for timeout vs clicked continue
        player.participant.vars['role_assignment_timeout'] = timeout_happened


class ChooserChoice(Page):
    form_model = 'player'
    form_fields = ['chooser_choice']
    timer_text = 'Time remaining to make a choice:'
    
    def is_displayed(player):
        return player.role == Constants.CHOOSER_ROLE

    def get_timeout_seconds(player):
        print(f"player dropout status: {player.participant.is_dropout}" )
        if player.participant.is_dropout:
            print("Player is dropout, random timeout")
            return random.randint(3, 7)  # Random timeout for dropout players
        else:
            return Constants.decision_timeout_seconds

    def vars_for_template(player):
        #define text on the buttons. if right is preffered, right button text = 'Right (10)' and left button text = 'Left (0)'
        if player.get_preferred_side() == 'right':
            right_text = f'Right Side ({Constants.preferred_side_points})'
            left_text = 'Left Side (0)'
        else:
            right_text = 'Right Side (0)'
            left_text = f'Left Side ({Constants.preferred_side_points})'

        return {
            'round_number': player.round_number,
            'correct_answer': player.correct_answer,
            'dots_left': player.dots_left,
            'dots_right': player.dots_right,
            'right_text': right_text,
            'left_text': left_text
        }

    @staticmethod
    def live_method(player, data):
        print(f"choice: {data.get('choice')}, data: {data}")
        if 'choice' in data:
            
            player.chooser_choice_time = data.get('choice_time', 0)
            player.chooser_choice = data['choice']
            player.group.chooser_choice_group = data['choice']
            player.group.chooser_rt_group = player.chooser_choice_time

            player.choice_correct = (player.chooser_choice == player.correct_answer)
            player.preferred_side_chosen = (player.chooser_choice == player.get_preferred_side())
            player.group.choice_correct_group = player.choice_correct
            player.group.preferred_side_chosen_group = player.preferred_side_chosen

            return {player.id_in_group: dict(choice_recorded=True)}

            
        return {player.id_in_group: dict(error=True)}

    def before_next_page(player, timeout_happened):
        print("Before next page")

        if timeout_happened:
            print("Timeout occurred")
            # Make random choice and apply penalty
            #if not choice_correct - generate random choice
            player.chooser_choice = random.choice(['right', 'left'])
            player.group.chooser_choice_group = player.chooser_choice

            player.choice_correct = (player.chooser_choice == player.correct_answer)
            player.preferred_side_chosen = (player.chooser_choice == player.get_preferred_side())
            player.group.choice_correct_group = player.choice_correct
            player.group.preferred_side_chosen_group = player.preferred_side_chosen
            player.timeout_occurred_chooser = True
            player.timeout_occurred = True
            player.participant.timeout_num += 1
            
            if player.round_number > 1:
                player.subsequent_timeouts = player.in_round(player.round_number - 1).subsequent_timeouts + 1
            else:
                player.subsequent_timeouts = 1


            #check if 2 consecutive timeouts happened
            if player.round_number >= 4:
                a = player.in_round(player.round_number - 1).timeout_occurred
                b = player.in_round(player.round_number - 2).timeout_occurred
                c = player.in_round(player.round_number - 3).timeout_occurred
                if player.timeout_occurred and a and b and c:
                    print("4 consecutive timeouts occurred - Chooser")
                    #change player to dropout
                    player.is_dropout = True
                    player.participant.is_dropout = True





page_sequence = [
    MobileCheck,
    MobileBlock,
    WelcomePage,
    RepeatParticipant,
    Instructions,
    # Training pages
    TrainingIntro,
    TrainingSetUp,         
    TrainingChooserDisplay,
    TrainingChooserChoice,
    TrainingChooserFeedback,
    TrainingModeratorCorrect,
    TrainingModeratorIncorrect,
    TrainingComplete,
    # 
    ComprehensionCheck,
    ComprehensionFailed,
    
    WaitingForOtherToFinishInstructions,
    Role_Assignment,


    # Main game pages
    TransitionPage,  
    PairingParticipants, 
    SetUp, DotDisplay, ChooserChoice, WaitForChooserChoice, ModeratorChoiceDisplay, WaitForModeratorDecision, FullFeedback,
    #AttentionCheck, #we decided to remove the attention check
    End_Questionnaire_Moderator, End_Questionnaire_Chooser,
    Lottery,
    Results]
