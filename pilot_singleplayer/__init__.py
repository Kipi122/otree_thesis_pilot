from otree.api import *
import random
import math



doc = """
This is a dot choice experiment where participants act as moderators, 
deciding whether to punish or warn a bot for its choices.
"""

#FIXME for the multiplayer, we want he "temping rounds" order to be the same for all players in the group? 

#TODO add pictures to instructions
#[x] add new comprehension questions
#[x] add new failed comprehension page
#TODO put everything in the center of the screen
#TODO change "participant" to "chooser" throughout the game
#FIXME change the payoff throughout the game to be points based on docomentation
#TODO check detect mobile snippet to block mobile browsers after deployment
#TODO IMPORTANT!!! ASK ORI - MAYBE PUT THE POINTS AMOUNT ON THE CHOOSER'S BOTTONS!!!!

class Constants(BaseConstants):
    debug = True  # Set to False for production
    name_in_url = 'pilot_singleplayer' #FIXME change to correct name before deployment!!!!!!!
    players_per_group = None
    num_rounds = 10
    small_fine = 11
    large_fine = 99
    tempting_rounds = 2/3 * num_rounds # 2/3 of the rounds are tempting #TODO implement tempting rounds
    #mistake_probability = 0.3 # [x]   adjust to two probabilities - probability to be correct if prefered side (.93), probability if not prefered side (.6) from theodorsecue et al. study 1
    correct_probability_preferred = 0.93 #[x] Implement the correct probabilities in code 
    correct_probability_not_preferred = 0.6
    #preferred_side = 'right' # [x] add alternation - randomise for each round for SP. theodorsecue et al. study 1 was alternating between left and right
    preferred_side_points = 10
    moderator_points_per_correct = 10
    num_dots_big = 17
    num_dots_small = 13
    total_dots = num_dots_big + num_dots_small
    fixation_display_seconds = 0.2  # Display fixation cross for 500ms
    dots_display_seconds = 0.2 # Display dots for X seconds 
    participation_fee = 2.00  # Add the participation fee for repeat participants
    bonus_fee_per_point = 0.1 #TODO set to correct value
#################TODO implement the following constants
    feedback_timeout = 5 # Time to display feedback before proceeding
    decision_timeout_seconds = 15  # Time to wait for decision before proceeding and getting a fine #TODO IMPLEMENT
    timeout_penalty = 10 # Points deducted for not making a decision in time #TODO IMPLEMENT
    base_payment = 2.00  # £2 base payment #TODO set to correct value
    bonus_amount = 1.00  # £1  #TODO set to correct value and #[ ] implement probability based on points to get bonus    
    waiting_compensation_rate = 0.10  # £1 per 10 minutes #TODO set to correct value
    min_waiting_for_compensation = 180  # 3 minutes in seconds #TODO set to correct value



class Subsession(BaseSubsession):
   pass

def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        # Initialize the used_prolific_ids in session vars if it doesn't exist
        if not subsession.session.vars.get('used_prolific_ids'):
            subsession.session.vars['used_prolific_ids'] = set()

        for player in subsession.get_players():
            # Store the condition in participant.vars
            player.participant.vars['fine_condition'] = random.choice(['small', 'large'])
            player.fine_condition = player.participant.vars['fine_condition']

            player.participant.vars['preferred_side'] = random.choice(['left', 'right'])
            player.preferred_side = player.participant.vars['preferred_side']

            print(f"player condition: {player.fine_condition}")
            print(f"player preferred side: {player.preferred_side}")
    else:
        # Get condition from participant.vars for subsequent rounds
        for player in subsession.get_players():
            player.fine_condition = player.participant.vars['fine_condition']
            player.preferred_side = player.participant.vars['preferred_side']

    for p in subsession.get_players():
            p.total_chooser_points = 0
            p.total_moderator_points = 0

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    
    timeout_occurred = models.BooleanField(initial=False)  # Track if timeout happened
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
    education = models.StringField( #FIXME REMOVE THIS FIELD
        choices=[
            ['High school', 'High school'],
            ['Bachelor’s degree', 'Bachelor’s degree'],
            ['Master’s degree', 'Master’s degree'],
            ['Doctoral degree', 'Doctoral degree'],
            ['Other', 'Other']
        ],
        label="What is your highest level of education?",
        widget=widgets.RadioSelect
    )

    # Comprehension check fields
    comp_fine_amount = models.IntegerField(
        label="How many points are deducted when the Moderator issue a penalty?",
    )
    
    comp_preferred_side = models.StringField(
        label="Which side gives the Chooser bonus points?",
        choices=[['left', 'Left side'], ['right', 'Right side']],
    )
    
    comprehension_attempts = models.IntegerField(initial=0)
    passed_comprehension = models.BooleanField(initial=False)
    failed_comprehension = models.BooleanField(initial=False)


    # Game fields
    fine_condition = models.StringField()
    participant_choice  = models.StringField()
    choice_correct  = models.BooleanField()
    preferred_side = models.StringField()
    preferred_side_chosen  = models.BooleanField()
    correct_answer = models.StringField()
    dots_left = models.IntegerField()
    dots_right = models.IntegerField()

    decision = models.StringField(blank=True)
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

    #save points for each round
    round_chooser_points = models.IntegerField() #FIXME saving not working
    round_chooser_alternative_points = models.IntegerField()
    round_moderator_points = models.IntegerField() #FIXME saving not working

    #save the total points for the whole game
    total_chooser_points = models.IntegerField(initial=0)  # Add initial=0
    total_moderator_points = models.IntegerField(initial=0)  # Add initial=0
    
    def get_preferred_side(self):
        return self.participant.vars.get('preferred_side', 'right')  # Default to right if not set
    
    def validate_prolific_id(self):
        print("Validating Prolific ID")
        # Get the set of used Prolific IDs from session vars
        used_prolific_ids = self.session.vars.get('used_prolific_ids', set())
        
        # Check if this Prolific ID has been used
        if self.prolific_id in used_prolific_ids:
            print("Prolific ID already used")
            self.is_repeat_participant = True
            return False
        else:
            # Add the new Prolific ID to the set
            print("Prolific ID is valid")
            used_prolific_ids.add(self.prolific_id)
            self.session.vars['used_prolific_ids'] = used_prolific_ids
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
        print("Generating dot counts")
        self.dots_left = random.choice([Constants.num_dots_small, Constants.num_dots_big])
        self.dots_right = Constants.total_dots - self.dots_left
        self.correct_answer = 'left' if self.dots_left > self.dots_right else 'right'
        
    def record_participant_choice(self):
        # Instead of random choice, implement bot behavior based on Teodorescu's parameters
        if self.correct_answer == self.get_preferred_side():
            # 93% chance to be correct when preferred side is correct
            self.participant_choice = self.correct_answer if random.random() < Constants.correct_probability_preferred else ('left' if self.correct_answer == 'right' else 'right')
        else:
            # 60% chance to be correct when non-preferred side is correct
            self.participant_choice = self.correct_answer if random.random() < Constants.correct_probability_not_preferred else ('left' if self.correct_answer == 'right' else 'right')
        
        self.choice_correct = self.participant_choice == self.correct_answer
        self.preferred_side_chosen = self.participant_choice == self.get_preferred_side()

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
    

    
    


# PAGES

class MobileCheck(Page):
    form_model = 'player'
    form_fields = ['is_mobile']

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
        return (player.round_number == 1 and 
                not player.is_repeat_participant and 
                not player.participant.vars.get('is_mobile', False) and 
                not Constants.debug)
    
    def before_next_page(player, timeout_happened):
        if not player.validate_prolific_id():
            print("Repeat participant detected1")
            player.is_repeat_participant = True

    def app_after_this_page(player, upcoming_apps):
        if player.is_repeat_participant:
            print("Repeat participant detected")
            return 'repeat_participant'

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['comp_fine_amount', 'comp_preferred_side']
    
    def is_displayed(player):
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
        return player.round_number == 1 and not Constants.debug

    def vars_for_template(player):
        return {
            'fine_amount': player.get_fine_amount(),  # Get player's specific fine amount
            'preferred_side': player.get_preferred_side(),
            'preferred_side_points': Constants.preferred_side_points,
            'display_seconds': Constants.dots_display_seconds,
            'num_rounds': Constants.num_rounds,
           
        }



#setup page to generate dots for each player
class SetUp(Page):
    def get_timeout_seconds(player: Player):
        return Constants.fixation_display_seconds
    
    
    def before_next_page(self, timeout_happened):
        for player in self.group.get_players():
            player.generate_dot_counts()

#class SetUp(WaitPage):
#    wait_for_all_groups = False  # Proceed immediately without waiting
#
#    def after_all_players_arrive(self):
#        for player in self.group.get_players():
#            player.generate_dot_counts()

class WaitForOtherParticipant(Page):
    """Simulated waiting page to make the experience more realistic"""
    @staticmethod
    def get_timeout_seconds(player: Player):
        import random

        return random.randint(1, 5)
    
    def vars_for_template(self):
        return {
            'round_number': self.subsession.round_number,
        }
    
class PairingParticipants(Page):
    """Simulated waiting page for pairing participants"""
    def is_displayed(self):
        return True
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import random

        return random.randint(3, 7)
    
class WaitingForOtherToFinishInstructions(Page):
    """Simulated waiting page for pairing participants"""
    def is_displayed(self):
        return self.round_number == 1
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import random

        return random.randint(3, 10)


class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1
    
    #def before_next_page(player, timeout_happened):
    #    player.generate_dot_counts()
    
    
class DotDisplay(Page):
    timeout_seconds = Constants.dots_display_seconds  # Display dots for 5 seconds
    
    def vars_for_template(self):
        return {
            'dots': self.generate_dot_positions(),
            'display_seconds': Constants.dots_display_seconds,
            'round_number': self.subsession.round_number,
        }
    
    
    
class ChoiceDisplay(Page):
    form_model = 'player'
    form_fields = []
    timer_text = 'Time remaining to make a decision:'


    def get_timeout_seconds(player):
        return Constants.decision_timeout_seconds
    
    @staticmethod
    def is_displayed(player):
        # Only record the choice if it hasn't been recorded yet
        if player.field_maybe_none('participant_choice') is None:
            player.record_participant_choice()
            
            print("Choice recorded:")
            print(f"Decision: {player.field_maybe_none('decision')}")
            print(f"Fine amount: {player.get_fine_amount()}")
            print(f"Participant choice: {player.participant_choice}")
            print(f"Correct answer: {player.correct_answer}")
            print(f"Choice correct: {player.choice_correct}")
            print(f"Preferred side chosen: {player.preferred_side_chosen}")

        return True
    
    def vars_for_template(self):
        return {
            'round_number': self.subsession.round_number,
            'participant_choice': self.participant_choice,
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
                print(f"Decision recorded: {player.decision}")  # Add logging
                return {player.id_in_group: dict(decision_made=True)}
        except Exception as e:
            print(f"Error in live_method: {e}")  # Add error logging
            return {player.id_in_group: dict(error=True)}
        
    def before_next_page(player, timeout_happened):
        print("Before next page")
        if timeout_happened:
            print("Timeout occurred")
            # Make random choice and apply penalty
            #if not choice_correct - generate random choice
            if not player.choice_correct:
                player.decision = random.choice(['punish', 'warn'])
            player.timeout_occurred = True
            
            # Apply timeout penalty
            current_total = player.field_maybe_none('total_moderator_points') or 0
            player.total_moderator_points = current_total - Constants.timeout_penalty
            
            
        
        

class FullFeedback(Page):
    timeout_seconds = Constants.feedback_timeout #adjust this to modify the time the feedback is displayed 
    def is_displayed(player):
        return True #display feedback for all rounds, not just the wrong ones
    
    def vars_for_template(self):
        # Calculate round payoff based on the scenario
        round_payoff = 0
        alternative_payoff = 0
        print("fullfeedback")
        print(f"Decision: {self.field_maybe_none('decision')}")
        print(f"Fine amount: {self.get_fine_amount()}")
        print(f"Participant choice: {self.participant_choice}")
        print(f"Correct answer: {self.correct_answer}") #BUG why have both??? 
        print(f"Choice correct: {self.choice_correct}") #BUG why have both???
        print(f"Preferred side chosen: {self.preferred_side_chosen}")


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
            'participant_choice': self.participant_choice,
            'correct_answer': self.correct_answer,
            'choice_correct': self.choice_correct,  # This boolean controls which feedback is shown
            'preferred_side_chosen': self.preferred_side_chosen,
            'payoff_punish': 10 - self.get_fine_amount() if self.preferred_side_chosen else -self.get_fine_amount(),
            'payoff_warn': 10 if self.preferred_side_chosen else 0,
            'round_number': self.subsession.round_number,
            'round_payoff': round_payoff,
            'alternative_payoff': alternative_payoff,
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
        player.round_moderator_points = 10 if player.choice_correct else 0
        
        # Get current totals (using 0 if None)
        current_chooser_total = player.field_maybe_none('total_chooser_points') or 0
        current_moderator_total = player.field_maybe_none('total_moderator_points') or 0
        
        # Update totals
        player.total_chooser_points = current_chooser_total + player.round_chooser_points
        player.total_moderator_points = current_moderator_total + player.round_moderator_points

    
    

class Results(Page):
    def is_displayed(player):
        return (player.round_number == Constants.num_rounds and 
                player.participant.vars.get('passed_training', False))
    
    def vars_for_template(self):
        return {
            'decision': self.decision,
            'fine_amount': self.get_fine_amount(),
            'participant_choice': self.participant_choice,
            'correct_answer': self.correct_answer,
            'choice_correct': self.choice_correct,
            'dots_left': self.dots_left,
            'dots_right': self.dots_right,
        }
    

    #training pages
class TrainingIntro(Page):
    def is_displayed(player):
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


class TrainingChooserDisplay(Page): #FIXME change to buttons to be like theodorsecue et al. study. 
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
        return {
            'correct_answer': player.correct_answer,
            'dots_left': player.dots_left,
            'dots_right': player.dots_right,
        }

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
            'payoff_punish': 10 - player.get_fine_amount(),  # Assuming preferred side was chosen
            'payoff_warn': 10,  # Points for preferred side without punishment
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
    

page_sequence = [
    MobileCheck,
    MobileBlock,
    WelcomePage,
    RepeatParticipant,
    #Introduction, 
    #ProlificID, RepeatParticipant,
    #Demographics,
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
    # Main game pages
    PairingParticipants,

    SetUp, DotDisplay, WaitForOtherParticipant, ChoiceDisplay, FullFeedback,
    AttentionCheck,
    Results]
