from otree.api import Bot, SubmissionMustFail
from . import *
import random

class PlayerBot(Bot):
    def play_round(self):
        player = self.player
        role = player.role()
        group = player.group
        


        

        if role == 'chooser':
            if player.round_number == 1:
                yield Introduction
            # Both players see the DotDisplay page
            #yield DotDisplay
            yield Submission(DotDisplay, check_html=False)
            # Chooser makes a choice
            # Simulate making a choice based on mistake probability
            if random.random() < Constants.mistake_probability:
                # Make an incorrect choice
                choice = 'left' if group.correct_answer == 'right' else 'right'
            else:
                # Make the correct choice
                choice = group.correct_answer
            #yield Submission(ChooserDecision, {'choice': choice}, check_html=False)
            yield ChooserDecision, {'_live_method': 'live_method', 'choice': choice}
        

            # Wait for the moderator's feedback
            yield WaitForModeratorFeedback


        elif role == 'moderator':
            # Human participant (should not be controlled by the bot)
            pass
        """
            # Wait for the chooser to make a decision
            yield WaitForChooserDecision

            # Moderator decides to punish or warn
            # For example, punish if the chooser favored their preferred side incorrectly
            if not group.chooser_correct and group.chooser_favored:
                decision = 'punish'
            else:
                decision = 'warn'
            yield ModeratorFeedback, {'decision': decision}
            """
