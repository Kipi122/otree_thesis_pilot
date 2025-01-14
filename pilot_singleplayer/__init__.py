from otree.api import *
import random
import math



doc = """
This is a dot choice experiment where participants act as moderators, 
deciding whether to punish or warn a bot for its choices.
"""

#TODO add pictures to instructions
#TODO add new comprehension questions
#TODO add new failed comprehension page
#TODO put everything in the center of the screen
#TODO change "participant" to "chooser" throughout the game

class Constants(BaseConstants):
    debug = True
    name_in_url = 'pilot_singelplayer' #FIXME change to correct name before deployment!!!!!!!
    players_per_group = None
    num_rounds = 40
    small_fine = 11
    large_fine = 99
    tempting_rounds = 2/3 * num_rounds # 2/3 of the rounds are tempting #TODO implement tempting rounds
    #mistake_probability = 0.3 # [x]   adjust to two probabilities - probability to be correct if prefered side (.93), probability if not prefered side (.6) from theodorsecue et al. study 1
    correct_probability_preferred = 0.93 #[ ] Implement the correct probabilities in code 
    correct_probability_not_preferred = 0.6
    preferred_side = 'right' # TODO add alternation - randomise for each round for SP. theodorsecue et al. study 1 was alternating between left and right
    preferred_side_points = 10
    num_dots_big = 17
    num_dots_small = 13
    total_dots = num_dots_big + num_dots_small
    fixation_display_seconds = 0.2  # Display fixation cross for 500ms
    dots_display_seconds = 0.2 # Display dots for X seconds 
    participation_fee = 2.00  # Add the participation fee for repeat participants
    bonus_fee_per_point = 0.1 #TODO set to correct value

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
            print(f"player condition: {player.fine_condition}")
    else:
        # Get condition from participant.vars for subsequent rounds
        for player in subsession.get_players():
            player.fine_condition = player.participant.vars['fine_condition']

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    #Prolific ID
    prolific_id = models.StringField(label="Please enter your Prolific ID")
    is_repeat_participant = models.BooleanField(initial=False)
    passed_comprehension = models.BooleanField(initial=False)
    failed_comprehension = models.BooleanField(initial=False)

    
    # Demographics
    age = models.IntegerField(label="What is your age?", min=18, max=100)
    gender = models.StringField(
        choices=[['Male', 'Male'], ['Female', 'Female'], ['Other', 'Other']],
        label="What is your gender?",
        widget=widgets.RadioSelect
    )
    education = models.StringField(
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

    # Comprehension Questions
    comp_fine_amount = models.IntegerField(
        label="How many points are deducted when you issue a penalty?",
    )
    
    comp_preferred_side = models.StringField(
        label="Which side gives the participant bonus points?",
        choices=[['left', 'Left side'], ['right', 'Right side']],
    )
    
    comp_bonus_points = models.IntegerField(
        label="How many bonus points does the participant get for choosing their preferred side?",
    )

    comp_moderator_role = models.StringField(
        label="What is your role in this experiment?",
        choices=[
            ['counter', 'Count dots and choose which side has more'],
            ['moderator', 'Monitor other participants and decide on warnings/penalties'],
            ['participant', 'Choose which side has more dots to earn points'],
        ]
    )

    comp_warning = models.StringField(
        label="What happens when you issue a warning?",
        choices=[
            ['points_lost', 'The participant loses points'],
            ['no_effect', 'No points are deducted'],
            ['bonus_lost', 'The participant loses their bonus points'],
        ]
    )

    # Game fields
    fine_condition = models.StringField()
    participant_choice  = models.StringField()
    choice_correct  = models.BooleanField()
    preferred_side_chosen  = models.BooleanField()
    correct_answer = models.StringField()
    dots_left = models.IntegerField()
    dots_right = models.IntegerField()
    decision = models.StringField()

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
    label="How many points could you have deducted from the reward of the Chooser in each round?",
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

    
    def validate_prolific_id(self):
        # Get the set of used Prolific IDs from session vars
        used_prolific_ids = self.session.vars.get('used_prolific_ids', set())
        
        # Check if this Prolific ID has been used
        if self.prolific_id in used_prolific_ids:
            self.is_repeat_participant = True
            return False
        else:
            # Add the new Prolific ID to the set
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
        print("Generating dot counts")
        self.dots_left = random.choice([Constants.num_dots_small, Constants.num_dots_big])
        self.dots_right = Constants.total_dots - self.dots_left
        self.correct_answer = 'left' if self.dots_left > self.dots_right else 'right'
        
    def record_participant_choice(self):
        self.participant_choice = random.choice(['left', 'right']) #TODO change to participant choice based on preffered/not side
        self.choice_correct = self.participant_choice == self.correct_answer
        self.preferred_side_chosen = self.participant_choice == Constants.preferred_side

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


    

    
    


# PAGES

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['comp_fine_amount', 'comp_preferred_side', 'comp_bonus_points', 
                   'comp_moderator_role', 'comp_warning']
    
    def is_displayed(player):
        # Show if it's round 1 and they haven't passed comprehension yet
        return (player.round_number == 1 and 
                not player.passed_comprehension and not Constants.debug)

    def error_message(player, values):
        errors = []
        if values['comp_fine_amount'] != player.get_fine_amount():
            errors.append(f'Incorrect penalty amount. Correct answer is {player.get_fine_amount()}.')
        if values['comp_preferred_side'] != Constants.preferred_side:
            errors.append('Incorrect preferred side.')
        if values['comp_bonus_points'] != Constants.preferred_side_points:
            errors.append('Incorrect bonus points amount. Correck answer is 10')
        if values['comp_moderator_role'] != 'moderator':
            errors.append('Incorrect role understanding.')
        if values['comp_warning'] != 'no_effect':
            errors.append('Incorrect understanding of warnings.')
        
        if errors:
            player.failed_comprehension = True
            return errors
        
        # If no errors, mark as passed
        player.passed_comprehension = True
        player.failed_comprehension = False
        return None
    
    def before_next_page(player, timeout_happened):
       # # Only allow proceeding if comprehension check was passed
        if not player.passed_comprehension:
            player.participant._is_bot = False  # Prevent auto-proceeding
            return       
    
    #def before_next_page(player, timeout_happened):
        #p = self.player
        #if player.failed_comprehension:
            #player._is_frozen = False
            #self._is_frozen = False
            #self._index_in_pages -= 2
            #print("self._index_in_pages: ", self._index_in_pages)
            #self._index_in_pages -= 2
            #print("self._index_in_pages: ", self._index_in_pages)

            #player.participant._index_in_pages -= 2


class ComprehensionFailed(Page):
    def is_displayed(player):
        return (player.round_number == 1 and 
                player.failed_comprehension and not Constants.debug)

    def vars_for_template(player):
        return {
            'fine_amount': player.get_fine_amount(),
            'preferred_side': Constants.preferred_side,
            'bonus_points': Constants.preferred_side_points,
        }
    
    def before_next_page(player, timeout_happened):
        # Reset failed flag but keep passed as False
        player.failed_comprehension = False
        player.passed_comprehension = False
        player.participant._index_in_pages -= 2

    def app_after_this_page(player, upcoming_apps):
        # This will force oTree to restart from the beginning of page_sequence
        # but since the other pages have their own is_displayed conditions,
        # it will effectively only show ComprehensionCheck
        return upcoming_apps[0]

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
            'preferred_side': Constants.preferred_side,
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
        return self.round_number == 1
    
    @staticmethod
    def get_timeout_seconds(player: Player):
        import random

        return random.randint(3, 10)
    
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
    
    @staticmethod
    def is_displayed(player):
        player.record_participant_choice()
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
        if 'decision' in data:
            player.decision = data['decision']
            return {player.id_in_group: dict(decision_made=True)}
        

class FullFeedback(Page):
    timeout_seconds = 5 #adjust this to modify the time the feedback is displayed
    def is_displayed(player):
        if player.field_maybe_none('decision') != None: # If decision has been made
            return True 
        else: 
            return False
    
    def vars_for_template(self):
        return {
            'decision': self.decision,
            'alternative': 'warn' if self.decision == 'punish' else 'punish',
            'fine_amount': self.get_fine_amount(),
            'participant_choice': self.participant_choice,
            'correct_answer': self.correct_answer,
            'choice_correct': self.choice_correct,
            'payoff_punish': 10 - self.get_fine_amount() if self.preferred_side_chosen else -self.get_fine_amount(),
            'payoff_warn': 10 if self.preferred_side_chosen else 0,
            'round_number': self.subsession.round_number,
        }

    
    

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
            'preferred_side': Constants.preferred_side,
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
        preferred_side_chosen = player.training_choice == Constants.preferred_side
        return {
            'choice': player.training_choice,
            'correct_answer': player.correct_answer,
            'choice_correct': choice_correct,
            'preferred_side_chosen': preferred_side_chosen,
            'preferred_side': Constants.preferred_side,
            'points': 10 if preferred_side_chosen else 0,
        }

class TrainingModeratorCorrect(Page):
    def is_displayed(player):
        return player.round_number == 1 and not Constants.debug

    def vars_for_template(player):
        return {
            'preferred_side': Constants.preferred_side,
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
            'preferred_side': Constants.preferred_side,
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
        preferred_side_chosen = player.training_choice == Constants.preferred_side
        
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
            'preferred_side_chosen': preferred_side_chosen,
            'decision': player.training_decision,
            'final_points': final_points,
            'alternative_points': alternative_points,
            'fine_amount': player.get_fine_amount(),
            # Calculate payoffs for the alternative choice
            'payoff_punish': (10 if player.training_choice != Constants.preferred_side else 0) - player.get_fine_amount(),
            'payoff_warn': 10 if player.training_choice != Constants.preferred_side else 0
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
    Introduction, 
    ProlificID, RepeatParticipant,
    Demographics,
    PairingParticipants,
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
    
    WaitingForOtherToFinishInstructions, 
    # Main game pages 
    SetUp, DotDisplay, WaitForOtherParticipant, ChoiceDisplay, FullFeedback,
    AttentionCheck,
    Results]
