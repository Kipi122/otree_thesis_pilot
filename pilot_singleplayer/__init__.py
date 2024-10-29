from otree.api import *
import random
import math



doc = """
This is a dot choice experiment where participants act as moderators, 
deciding whether to punish or warn a bot for its choices.
"""



class Constants(BaseConstants):
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

class Subsession(BaseSubsession):
   pass

def creating_session(subsession: Subsession):
        for player in subsession.get_players():
            player.fine_condition = random.choice(['small', 'large'])
            print(f"player condition: {player.fine_condition}")

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    fine_condition = models.StringField()
    # Remove the decision field
    #decision = models.StringField(choices=['punish', 'warn'])
    bot_choice = models.StringField()
    bot_correct = models.BooleanField()
    bot_favored = models.BooleanField()
    correct_answer = models.StringField()
    dots_left = models.IntegerField()
    dots_right = models.IntegerField()
    # Add a new field to store the decision
    decision = models.StringField()
    
    
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
        
    def bot_makes_choice(self):
        self.bot_choice = random.choice(['left', 'right'])
        #self.bot_correct = random.random() > Constants.mistake_probability # 0.7 chance of being correct
        self.bot_correct = self.bot_choice == self.correct_answer # 0.5 chance of being correct
        self.bot_favored = self.bot_choice == Constants.preferred_side

    def get_fine_amount(self):
        if self.fine_condition == 'small':
            return Constants.small_fine
        elif self.fine_condition == 'large':
            return Constants.large_fine
        else:
            return 0  # Default value if fine_condition is not set


    

    
    


# PAGES

#swtup page to generate dots for each player
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

class WaitForBot(Page):
    """
    This is just for show, to make it feel more realistic.
    Also, note it's a Page, not a WaitPage.
    Removing this page won't affect functionality.
    """

    @staticmethod
    def get_timeout_seconds(player: Player):
        import random

        return random.randint(1, 5)


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
        player.bot_makes_choice()
        return True

    #def before_next_page(self, timeout_happened):
    #    print("Im here")
    #    self.generate_dot_counts()
    
    def vars_for_template(self):
        
        return {
            'bot_choice': self.bot_choice,
            'bot_correct': self.bot_correct,
            'bot_favored': self.bot_favored,
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
    
    """
    @staticmethod
    def get_form_fields(self):
        if not self.bot_correct:
            return ['decision']
        else:
            return []
    """
    

class Results(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds
    
    def vars_for_template(self):
        return {
            'decision': self.decision,
            'fine_amount': self.get_fine_amount(),
            'bot_choice': self.bot_choice,
            'correct_answer': self.correct_answer,
            'bot_correct': self.bot_correct,
            'dots_left': self.dots_left,
            'dots_right': self.dots_right,
        }

page_sequence = [SetUp, Introduction, DotDisplay, WaitForBot, ChoiceDisplay, Results]
