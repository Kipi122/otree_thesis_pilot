from otree.api import Currency as c, currency_range, expect
from . import *
import random
import json

class PlayerBot(Bot):
    def play_round(self):
        round_number = self.player.round_number
        
        # First round setup and checks
        if round_number == 1:
            # Test mobile detection
            yield MobileCheck
            
            # Test welcome page and demographics
            yield WelcomePage, {
                'prolific_id': 'test_id_' + str(random.randint(10000, 99999)),
                'age': random.randint(18, 65),
                'gender': random.choice(['Male', 'Female', 'Other'])
            }
            
            # Test instructions
            yield Instructions
            
            # Test training sequence
            yield TrainingIntro
            yield TrainingSetUp
            yield TrainingChooserDisplay
            yield TrainingChooserChoice, {'training_choice': self.player.correct_answer}
            yield TrainingChooserFeedback
            yield TrainingModeratorCorrect
            yield TrainingModeratorIncorrect, {'training_decision': random.choice(['punish', 'warn'])}
            yield TrainingComplete
            
            # Test comprehension check
            comprehension_data = {
                'comp_fine_amount': self.player.get_fine_amount(),
                'comp_preferred_side': self.player.get_preferred_side()
            }
            yield ComprehensionCheck, comprehension_data
            
            # Test waiting pages
            yield WaitingForOtherToFinishInstructions
            yield PairingParticipants

        # Test main game sequence
        yield SetUp
        yield DotDisplay
        yield WaitForOtherParticipant
        
        # Test choice display and decision making
        if not self.player.choice_correct:
            decision_data = {'decision': random.choice(['punish', 'warn'])}
            yield ChoiceDisplay, decision_data
        else:
            yield ChoiceDisplay
            
        yield FullFeedback
        
        # Final round additional tests
        if round_number == Constants.num_rounds:
            yield Lottery
            yield Results
            
            # Verify final calculations
            expect(self.player.total_monetary_payoff, '>=', Constants.participation_fee)
            if self.player.lottery_won:
                expect(self.player.total_monetary_payoff, '>=', 
                       Constants.participation_fee + Constants.bonus_fee)

def validate_dot_generation(test_player):
    """Test dot generation logic"""
    test_player.generate_dot_counts()
    
    # Verify total number of dots
    assert test_player.dots_left + test_player.dots_right == Constants.total_dots
    
    # Verify dot counts are valid
    assert test_player.dots_left in [Constants.num_dots_big, Constants.num_dots_small]
    assert test_player.dots_right in [Constants.num_dots_big, Constants.num_dots_small]
    
    # Verify correct answer matches dot counts
    if test_player.dots_left > test_player.dots_right:
        assert test_player.correct_answer == 'left'
    else:
        assert test_player.correct_answer == 'right'

def test_bot_behavior(test_player):
    """Test bot (chooser) decision making"""
    test_player.record_participant_choice()
    
    # Verify choice is recorded
    assert test_player.participant_choice in ['left', 'right']
    
    # Verify preferred side logic
    assert test_player.preferred_side_chosen == (
        test_player.participant_choice == test_player.get_preferred_side()
    )
    
    # Verify choice correctness
    assert test_player.choice_correct == (
        test_player.participant_choice == test_player.correct_answer
    )

def test_points_calculation(test_player):
    """Test points calculation logic"""
    initial_points = test_player.total_moderator_points
    
    # Simulate correct choice
    test_player.choice_correct = True
    test_player.timeout_occurred = False
    test_player.decision = None
    
    # Calculate expected points
    expected_points = initial_points + Constants.moderator_points_per_correct
    
    # Verify points calculation
    assert test_player.round_moderator_points == Constants.moderator_points_per_correct
    assert test_player.total_moderator_points <= expected_points

def custom_export_test(players):
    """Test custom export functionality"""
    export_data = custom_export(players)
    headers = next(export_data)
    
    # Verify required columns are present
    required_columns = [
        'session_code', 'participant_code', 'round_number',
        'fine_condition', 'decision', 'choice_correct',
        'total_moderator_points', 'total_chooser_points'
    ]
    
    for column in required_columns:
        assert column in headers, f"Missing required column: {column}"
        
    # Verify data rows
    for row in export_data:
        assert len(row) == len(headers), "Data row length mismatch"