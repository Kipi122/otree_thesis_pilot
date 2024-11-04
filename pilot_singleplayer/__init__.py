from otree.api import *
import random
import math



doc = """
This is a dot choice experiment where participants act as moderators, 
deciding whether to punish or warn a bot for its choices.
"""



class Constants(BaseConstants):
    debug = False
    name_in_url = 'pilot_singelplayer'
    players_per_group = None
    num_rounds = 10
    small_fine = 11
    large_fine = 99
    mistake_probability = 0.3
    preferred_side = 'right'
    preferred_side_points = 10
    num_dots_big = 17
    num_dots_small = 13
    total_dots = num_dots_big + num_dots_small
    dots_display_seconds = 5 # Display dots for 5 seconds
    participation_fee = 2.00  # Add the participation fee for repeat participants



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
        self.participant_choice = random.choice(['left', 'right'])
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
        #player.failed_comprehension = False
        return None
    
        # Add this method to reset fields when the page loads


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
        return 0
    
    
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
        }
    
    
    

class ChoiceDisplay(Page):
    
    #form_model = 'player'
    #form_fields = []
    
    @staticmethod
    def is_displayed(player):
        player.record_participant_choice()
        return True

    
    def vars_for_template(self):
        
        return {
            'participant_choice': self.participant_choice,
            'choice_correct': self.choice_correct,
            'preferred_side_chosen': self.preferred_side_chosen,
            'fine_amount': self.get_fine_amount(),
            'correct_answer': self.correct_answer,
            'dots_left': self.dots_left,
            'dots_right': self.dots_right,
        }
    
    @staticmethod
    def live_method(player, data):
        if 'decision' in data:
            player.decision = data['decision']
            return {player.id_in_group: dict(decision_made=True)}
    
    

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

page_sequence = [
    Introduction, 
    ProlificID, RepeatParticipant,
    Demographics,
    PairingParticipants,
    Instructions,
    ComprehensionCheck,
    WaitingForOtherToFinishInstructions,  
    SetUp, DotDisplay, WaitForOtherParticipant, ChoiceDisplay, 
    Results]
