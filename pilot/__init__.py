from otree.api import *
import random
import math
import json

doc = """
This is a dot choice experiment where participants act as moderators, 
deciding whether to punish or warn a bot for its choices.
"""

class Constants(BaseConstants):
    name_in_url = 'my_experiment'
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
    dots_display_seconds = 5
    is_chooser_bot = True

class Subsession(BaseSubsession):
    pass

        
def creating_session(subsession: Subsession):
    import random
    if Constants.is_chooser_bot:
        # Assign fine condition to the bot
        fine_condition_assign = random.choice(['small', 'large'])
        for player in subsession.get_players():
            player.fine_condition = fine_condition_assign
            player.participant.vars['role'] = 'moderator'
            BotChooser.create(player=player)
        # Create a BotChooser instance for each group
        for group in subsession.get_groups():
            
            BotChooser.filter(group=group)[0].fine_condition = fine_condition_assign
    
    #for group in subsession.get_groups():
     #   if Constants.is_chooser_bot:
      #      player = group.get_player_by_id(1)  # Only one player per group
       #     fine_condition_assign = random.choice(['small', 'large'])
        #    #player.fine_condition = fine_condition_assign
         #   for player in group.get_players():
          #      player.fine_condition = fine_condition_assign
            # Create a BotChooser instance for each group
           # BotChooser.create(group=group)
            #BotChooser.filter(group=group)[0].fine_condition = fine_condition_assign
            #print('players', group.get_players())
            
            
        else:
            players = group.get_players()
            players[0].participant.vars['role'] = 'chooser'
            players[1].participant.vars['role'] = 'moderator'
            # Assign fine condition to the moderator
            fine_condition_assign = random.choice(['small', 'large'])
            for player in players:
                player.fine_condition = fine_condition_assign

        


class Group(BaseGroup):
    dots_left = models.IntegerField()
    dots_right = models.IntegerField()
    correct_answer = models.StringField()
    chooser_correct = models.BooleanField()
    chooser_favored = models.BooleanField()
    dot_positions = models.LongStringField()  # Store positions as JSON
    if not Constants.is_chooser_bot:
        chooser_choice = models.StringField()


    def generate_dot_counts(self):
        self.dots_left = random.choice([Constants.num_dots_small, Constants.num_dots_big])
        self.dots_right = Constants.total_dots - self.dots_left
        self.correct_answer = 'left' if self.dots_left > self.dots_right else 'right'

    def generate_dot_positions(self):
        width, height = 400, 200
        padding = 10
        min_distance = 10
        line_tolerance = 5
        max_attempts = 1000

        def is_left_of_diagonal(x, y):
            return y > 0.5 * x

        def distance_from_line(x, y):
            numerator = abs(y - 0.5 * x)
            denominator = math.sqrt(0.5 ** 2 + 1)
            return numerator / denominator

        def distance(p1, p2):
            return math.hypot(p1['x'] - p2['x'], p1['y'] - p2['y'])

        all_dots = []
        left_dots = []
        right_dots = []

        dots_left = self.dots_left
        dots_right = self.dots_right

        # Generate left-side dots
        attempts = 0
        while len(left_dots) < dots_left:
            if attempts >= max_attempts:
                raise Exception("Could not generate enough left-side dots without collisions.")
            x = random.randint(padding, width - padding)
            y = random.randint(padding, height - padding)
            attempts += 1
            if is_left_of_diagonal(x, y):
                if distance_from_line(x, y) < line_tolerance:
                    continue
                new_dot = {'x': x, 'y': y}
                collision = any(distance(new_dot, dot) < min_distance for dot in all_dots)
                if collision:
                    continue
                left_dots.append(new_dot)
                all_dots.append(new_dot)
                attempts = 0

        # Generate right-side dots
        attempts = 0
        while len(right_dots) < dots_right:
            if attempts >= max_attempts:
                raise Exception("Could not generate enough right-side dots without collisions.")
            x = random.randint(padding, width - padding)
            y = random.randint(padding, height - padding)
            attempts += 1
            if not is_left_of_diagonal(x, y):
                if distance_from_line(x, y) < line_tolerance:
                    continue
                new_dot = {'x': x, 'y': y}
                collision = any(distance(new_dot, dot) < min_distance for dot in all_dots)
                if collision:
                    continue
                right_dots.append(new_dot)
                all_dots.append(new_dot)
                attempts = 0

        # Store the positions as a JSON string
        self.dot_positions = json.dumps(all_dots)

class Player(BasePlayer):
    fine_condition = models.StringField()
    decision = models.StringField()
    if not Constants.is_chooser_bot:
        choice = models.StringField()
        favored = models.BooleanField()
        #is_bot = models.BooleanField()

    def role(self):
        if Constants.is_chooser_bot:
            return 'moderator'
        else:
            return self.participant.vars.get('role', 'moderator')

    def get_fine_amount(self):
        if self.fine_condition == 'small':
            return Constants.small_fine
        elif self.fine_condition == 'large':
            return Constants.large_fine
        else:
            return 0
       
if Constants.is_chooser_bot: 
    class BotChooser(ExtraModel):
        player = models.Link(Player)    
        group = models.Link(Group)
        choice = models.StringField()
        favored = models.BooleanField()
        choice = models.StringField()
        # You can add more fields if needed


# PAGES

class WaitForStart(WaitPage):
    wait_for_all_groups = False  # Wait for all players in the group
    body_text = "Waiting for the other participant to get ready."

    @staticmethod
    def get_timeout_seconds(player: Player):
        import random

        return random.randint(1, 5)


class SetUp(WaitPage):
    wait_for_all_groups = False

    def after_all_players_arrive(group: Group):
        group.generate_dot_counts()
        group.generate_dot_positions()
        

        if Constants.is_chooser_bot:
            bot = BotChooser.filter(group=group)[0]

            # Simulate the bot's choice
            if random.random() < Constants.mistake_probability:
             bot.choice = 'left' if group.correct_answer == 'right' else 'right'
            else:
                bot.choice = group.correct_answer
            
            bot.favored = bot.choice == Constants.preferred_side
            group.chooser_correct = bot.choice == group.correct_answer
            group.chooser_favored = bot.favored


class Introduction(Page):
    def is_displayed(player):
        if Constants.is_chooser_bot:
            return player.round_number == 1 and player.role() == 'moderator'
        return player.round_number == 1

    def vars_for_template(player):
        return {
            'role': player.role(),
            'fine_condition': player.fine_condition
        }

class DotDisplay(Page):
    timeout_seconds = Constants.dots_display_seconds

    def is_displayed(player):
        return True  # Both players see this page

    def vars_for_template(player):
        dots = json.loads(player.group.dot_positions)
        return {
            'dots': dots,
            'display_seconds': Constants.dots_display_seconds,
        }

class ChooserDecision(Page):

    def is_displayed(player):
        return player.role() == 'chooser'

    @staticmethod
    def live_method(player, data):
        if 'choice' in data:
            player.choice = data['choice']
            player.group.chooser_choice = player.choice
            player.group.chooser_correct = player.choice == player.group.correct_answer
            player.favored = player.choice == Constants.preferred_side
            player.group.chooser_favored = player.favored
            return {player.id_in_group: dict(choice_made=True)}

class WaitForChooserDecision(WaitPage):
    def is_displayed(player):
        return player.role() == 'moderator'
    
    if Constants.is_chooser_bot:
        @staticmethod
        def get_timeout_seconds(player: Player):
            return random.randint(1, 5)
    

class ModeratorFeedback(Page):

    def is_displayed(player):
        if Constants.is_chooser_bot:
            return player.role() == 'moderator'
        return player.role() == 'moderator'

    @staticmethod
    def vars_for_template(player):
        
        if Constants.is_chooser_bot:
            group = player.group
            bot = BotChooser.filter(group=group)[0]
            return {
            'chooser_choice': bot.choice,
            'chooser_correct': group.chooser_correct,
            'chooser_favored': group.chooser_favored,
            'correct_answer': group.correct_answer,
            'fine_amount': player.get_fine_amount(),
        }
        
        else: return {
            'chooser_choice': player.group.chooser_choice,
            'chooser_correct': player.group.chooser_correct,
            'chooser_favored': player.group.chooser_favored,
            'correct_answer': player.group.correct_answer,
            'fine_amount': player.get_fine_amount(),
        }

    @staticmethod
    def live_method(player, data):
        if 'decision' in data:
            player.decision = data['decision']
            return {player.id_in_group: dict(decision_made=True)}

class WaitForModeratorFeedback(WaitPage):
    def is_displayed(player):
        return player.role() == 'chooser'

class Results(Page):
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

    def vars_for_template(player):
        return {
            'decision': player.decision,
            'fine_amount': player.get_fine_amount(),
            'chooser_choice': player.group.chooser_choice,
            'correct_answer': player.group.correct_answer,
            'chooser_correct': player.group.chooser_correct,
            'dots_left': player.group.dots_left,
            'dots_right': player.group.dots_right,
            'role': player.role()
        }

page_sequence = [
    SetUp,
    Introduction,
    WaitForStart,
    DotDisplay,
    ChooserDecision,
    WaitForChooserDecision,
    ModeratorFeedback,
    WaitForModeratorFeedback,
    Results
]
