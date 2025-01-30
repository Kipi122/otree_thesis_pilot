from otree.api import Bot, Submission
from . import *

class PlayerBot(Bot):
    def play_round(self):
        # Only run mobile detection and blocking in round 1
        if self.round_number == 1:
            # First page is MobileCheck
            yield Submission(MobileCheck, dict(is_mobile=1), check_html=False)
            
            # Verify mobile flag is set
            assert self.player.is_mobile == True, f"Expected is_mobile to be True, got {self.player.is_mobile}"
            assert self.player.participant.vars['is_mobile'] == True, "Expected participant vars is_mobile to be True"
            
            # Submit MobileBlock page
            yield Submission(MobileBlock, check_html=False)