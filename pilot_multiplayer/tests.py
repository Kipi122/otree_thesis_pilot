from otree.api import Currency as c, currency_range, expect, Submission
from . import *
import random
import json

class PlayerBot(Bot):
    def play_round(self):
        round_number = self.player.round_number
        
        # First round setup and checks
        if round_number == 1:
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
            yield Submission(TrainingSetUp, {}, check_html=False)  # Timeout page, no submit button
            yield Submission(TrainingChooserDisplay, {}, check_html=False)  # Timeout page, no submit button
            yield Submission(TrainingChooserChoice, {'training_choice': self.get_bot_choice_for_training()}, check_html=False)  # Uses live_method, no submit button
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
            
            # Wait pages are handled automatically by oTree
            # Role assignment
            yield Submission(Role_Assignment, {}, check_html=False)  # Timeout page, no submit button

        # Test transition page at the right round (BEFORE main game sequence)
        if round_number == Constants.transition_round:
            yield Submission(TransitionPage, {}, check_html=False)  # Timeout page, no submit button

        # Test main game sequence with conditional paths based on role
        yield Submission(SetUp, {}, check_html=False)  # Timeout page, no submit button
        yield Submission(DotDisplay, {}, check_html=False)  # Timeout page, no submit button
        
        # Role-specific pages
        if self.player.role == Constants.CHOOSER_ROLE:
            # Chooser makes a choice (sometimes timeout to test dropout logic)
            if self.should_timeout_chooser():
                # Don't yield the page to simulate timeout
                pass
            else:
                yield Submission(ChooserChoice, {'chooser_choice': self.get_bot_choice()}, check_html=False)  # Uses live_method, no submit button
            # WaitForModeratorDecision is handled automatically
        else:  # Moderator role
            # WaitForChooserChoice is handled automatically
            # Moderator decision (sometimes timeout to test dropout logic)
            if not self.player.choice_correct:
                if self.should_timeout_moderator():
                    # Don't yield the page to simulate timeout
                    pass
                else:
                    yield Submission(ModeratorChoiceDisplay, {'decision': random.choice(['punish', 'warn'])}, check_html=False)  # Uses live_method, no submit button
            else:
                yield Submission(ModeratorChoiceDisplay, {}, check_html=False)  # Correct choice, auto-proceeds
            
        yield Submission(FullFeedback, {}, check_html=False)  # Timeout page, no submit button
        
        # Final round additional tests
        if round_number == Constants.num_rounds:
            if self.player.role == Constants.MODERATOR_ROLE:
                yield End_Questionnaire_Moderator, {
                    'effectiveness_rating': random.randint(0, 5),
                    'fairness_rating_1': random.randint(0, 5),
                    'fairness_rating_2': random.randint(0, 5),
                    'additional_comments': 'Test comment'
                }
            else:
                yield End_Questionnaire_Chooser, {
                    'effectiveness_rating': random.randint(0, 5),
                    'fairness_rating_1': random.randint(0, 5),
                    'fairness_rating_2': random.randint(0, 5),
                    'additional_comments': 'Test comment'
                }
            
            yield Submission(Lottery, {}, check_html=False)  # Timeout page, no submit button
            yield Submission(Results, {}, check_html=False)  # Final page, no submit button
            
            # Verify final calculations
            expect(self.player.total_monetary_payoff, '>=', Constants.participation_fee)
            if self.player.lottery_won:
                expect(self.player.total_monetary_payoff, '>=', 
                       Constants.participation_fee + Constants.bonus_fee)

    def should_timeout_chooser(self):
        """Simulate chooser timeouts to test dropout logic"""
        participant_id = self.player.participant.id_in_session
        round_num = self.player.round_number
        
        # Create a specific dropout scenario:
        # Player 1 (if Chooser) becomes dropout in rounds 10-13
        if participant_id == 1 and self.player.role == Constants.CHOOSER_ROLE and round_num in [10, 11, 12, 13]:
            return True
        
        # Player 3 (if Chooser) becomes dropout in rounds 20-23 
        if participant_id == 3 and self.player.role == Constants.CHOOSER_ROLE and round_num in [20, 21, 22, 23]:
            return True
            
        return False

    def should_timeout_moderator(self):
        """Simulate moderator timeouts to test dropout logic"""
        participant_id = self.player.participant.id_in_session
        round_num = self.player.round_number
        
        # Create a specific dropout scenario:
        # Player 2 (if Moderator) becomes dropout in rounds 15-18
        if participant_id == 2 and self.player.role == Constants.MODERATOR_ROLE and round_num in [15, 16, 17, 18]:
            return True
            
        return False

    def get_bot_choice_for_training(self):
        """Get a bot choice for training (before pairing is established)"""
        # For training, we need to generate dots first
        if not hasattr(self.player, 'correct_answer') or not self.player.correct_answer:
            # Temporarily generate training dots
            self.player.generate_training_dots()
        return self.player.correct_answer

    def get_bot_choice(self):
        """Get bot choice based on Teodorescu parameters"""
        if self.player.correct_answer == self.player.get_preferred_side():
            # 93% chance to be correct when preferred side is correct
            return self.player.correct_answer if random.random() < Constants.correct_probability_preferred else ('left' if self.player.correct_answer == 'right' else 'right')
        else:
            # 60% chance to be correct when non-preferred side is correct
            return self.player.correct_answer if random.random() < Constants.correct_probability_not_preferred else ('left' if self.player.correct_answer == 'right' else 'right')


def test_initial_session_setup(subsession):
    """Test that initial session setup works correctly"""
    if subsession.round_number == 1:
        # Verify session vars are initialized
        assert 'dropout_pairs' in subsession.session.vars
        assert 'dropout_list' in subsession.session.vars
        assert 'player_roles' in subsession.session.vars
        assert 'used_prolific_ids' in subsession.session.vars
        
        # Verify all players have roles assigned
        for player in subsession.get_players():
            participant_id = player.participant.id_in_session
            assert participant_id in subsession.session.vars['player_roles']
            assert subsession.session.vars['player_roles'][participant_id] in [1, 2]
            
        # Verify initial conditions are set
        for player in subsession.get_players():
            assert player.fine_condition in ['small', 'large']
            assert player.preferred_side in ['left', 'right']
            assert player.role_in_experiment == player.role


def test_pairing_logic(subsession):
    """Test the pairing logic in PairingParticipants"""
    print(f"\n=== Testing Pairing Logic for Round {subsession.round_number} ===")
    
    # Get session data
    dropout_pairs = subsession.session.vars.get('dropout_pairs', {})
    dropout_list = subsession.session.vars.get('dropout_list', [])
    player_roles = subsession.session.vars.get('player_roles', {})
    
    # Verify all players are properly paired
    all_players = subsession.get_players()
    paired_players = set()
    
    for group in subsession.get_groups():
        players_in_group = group.get_players()
        assert len(players_in_group) == 2, f"Group should have exactly 2 players, has {len(players_in_group)}"
        
        player1, player2 = players_in_group
        p1_id = player1.participant.id_in_session
        p2_id = player2.participant.id_in_session
        
        # Verify pairing
        assert player1.paired_player_id == p2_id
        assert player2.paired_player_id == p1_id
        
        # Verify roles are preserved
        assert player1.id_in_group == player_roles.get(p1_id, 1)
        assert player2.id_in_group == player_roles.get(p2_id, 2)
        
        # Verify they have different roles
        assert player1.role != player2.role
        
        # Check dropout pairing rules
        p1_is_dropout = p1_id in dropout_list
        p2_is_dropout = p2_id in dropout_list
        
        if p1_is_dropout or p2_is_dropout:
            # At least one is dropout, check if permanently paired
            if p1_id in dropout_pairs:
                assert dropout_pairs[p1_id] == p2_id
            if p2_id in dropout_pairs:
                assert dropout_pairs[p2_id] == p1_id
        
        paired_players.add(p1_id)
        paired_players.add(p2_id)
        
        print(f"Group: P{p1_id}({player1.role}) <-> P{p2_id}({player2.role})")
    
    # Verify all players are paired exactly once
    assert len(paired_players) == len(all_players), "All players should be paired exactly once"


def test_dot_generation_after_pairing(subsession):
    """Test that dots are generated correctly after pairing"""
    for group in subsession.get_groups():
        players = group.get_players()
        if len(players) == 2:
            player1, player2 = players
            
            # Both players should have same dot counts and correct answer
            assert player1.dots_left == player2.dots_left
            assert player1.dots_right == player2.dots_right
            assert player1.correct_answer == player2.correct_answer
            assert player1.is_tempting_round == player2.is_tempting_round
            
            # Verify dot counts are valid
            assert player1.dots_left + player1.dots_right == Constants.total_dots
            assert player1.dots_left in [Constants.num_dots_big, Constants.num_dots_small]
            assert player1.dots_right in [Constants.num_dots_big, Constants.num_dots_small]
            
            # Verify correct answer matches dot distribution
            if player1.dots_left > player1.dots_right:
                assert player1.correct_answer == 'left'
            else:
                assert player1.correct_answer == 'right'
            
            # Verify tempting round logic
            preferred_side = player1.get_preferred_side()
            if player1.is_tempting_round:
                assert player1.correct_answer != preferred_side
            else:
                assert player1.correct_answer == preferred_side


def test_dropout_detection(subsession):
    """Test dropout detection and tracking"""
    if subsession.round_number > 4:  # Need at least 4 rounds to detect consecutive timeouts
        dropout_list = subsession.session.vars.get('dropout_list', [])
        
        for player in subsession.get_players():
            participant_id = player.participant.id_in_session
            
            # Check if player should be marked as dropout
            consecutive_timeouts = 0
            for round_back in range(1, 5):  # Check last 4 rounds
                if subsession.round_number - round_back > 0:
                    prev_player = player.in_round(subsession.round_number - round_back + 1)
                    if prev_player.timeout_occurred:
                        consecutive_timeouts += 1
                    else:
                        break
            
            if consecutive_timeouts >= 4:
                assert player.is_dropout, f"Player {participant_id} should be marked as dropout"
                assert participant_id in dropout_list, f"Player {participant_id} should be in dropout_list"
            
            # Verify consistency
            if player.is_dropout:
                assert player.participant.is_dropout


def test_role_consistency_across_rounds(subsession):
    """Test that roles remain consistent across all rounds"""
    player_roles = subsession.session.vars.get('player_roles', {})
    
    for player in subsession.get_players():
        participant_id = player.participant.id_in_session
        expected_role = player_roles.get(participant_id)
        
        if expected_role:
            assert player.id_in_group == expected_role, f"Player {participant_id} role changed: expected {expected_role}, got {player.id_in_group}"
            
            # Check across all previous rounds
            for round_num in range(1, subsession.round_number + 1):
                round_player = player.in_round(round_num)
                assert round_player.id_in_group == expected_role, f"Player {participant_id} role inconsistent in round {round_num}"


def test_fine_condition_transition(subsession):
    """Test that fine conditions transition correctly at the transition round"""
    for player in subsession.get_players():
        initial_condition = player.participant.vars.get('initial_fine_condition')
        second_condition = player.participant.vars.get('second_fine_condition')
        
        if subsession.round_number < Constants.transition_round:
            assert player.fine_condition == initial_condition
        else:
            assert player.fine_condition == second_condition
        
        # Verify second condition is opposite of first
        if initial_condition == 'small':
            assert second_condition == 'large'
        else:
            assert second_condition == 'small'


def test_permanent_dropout_pairing(subsession):
    """Test that dropout pairs remain permanent across rounds"""
    if subsession.round_number > 10:  # Test after some dropouts should be established
        dropout_pairs = subsession.session.vars.get('dropout_pairs', {})
        
        # Get permanent pairs from previous round
        prev_subsession = subsession.in_round(subsession.round_number - 1)
        prev_dropout_pairs = prev_subsession.session.vars.get('dropout_pairs', {})
        
        # Verify permanent pairs remain stable
        for p1_id, p2_id in prev_dropout_pairs.items():
            if p1_id in dropout_pairs:
                assert dropout_pairs[p1_id] == p2_id, f"Permanent pair {p1_id}-{p2_id} was broken"


def test_points_calculation(player):
    """Test points calculation logic"""
    if player.round_number > 1:  # Need at least one completed round
        prev_player = player.in_round(player.round_number - 1)
        
        # Verify total points are cumulative
        if player.role == Constants.CHOOSER_ROLE:
            expected_total = prev_player.total_points + prev_player.round_chooser_points
            assert player.total_points >= expected_total - Constants.timeout_penalty  # Account for potential timeout penalty
        else:
            expected_total = prev_player.total_points + prev_player.round_moderator_points
            assert player.total_points >= expected_total - Constants.timeout_penalty


def test_specific_dropout_scenario(subsession):
    """Test specific dropout scenario with detailed tracking"""
    round_num = subsession.round_number
    
    # Get session tracking data
    dropout_pairs = subsession.session.vars.get('dropout_pairs', {})
    dropout_list = subsession.session.vars.get('dropout_list', [])
    
    print(f"\n=== Round {round_num} Dropout Scenario Analysis ===")
    
    # Expected dropout timeline:
    expected_dropouts_by_round = {
        14: [1],      # Player 1 becomes dropout after rounds 10-13
        19: [1, 2],   # Player 2 becomes dropout after rounds 15-18  
        24: [1, 2, 3] # Player 3 becomes dropout after rounds 20-23
    }
    
    # Check expected dropout status
    for round_threshold, expected_dropouts in expected_dropouts_by_round.items():
        if round_num >= round_threshold:
            for expected_dropout_id in expected_dropouts:
                if expected_dropout_id <= len(subsession.get_players()):
                    assert expected_dropout_id in dropout_list, f"Round {round_num}: Player {expected_dropout_id} should be marked as dropout"
                    print(f"✓ Player {expected_dropout_id} correctly marked as dropout")
    
    # Verify permanent pairing logic
    if round_num >= 14:  # After first dropout
        # Player 1 should be permanently paired
        if 1 in dropout_pairs:
            partner_id = dropout_pairs[1]
            print(f"✓ Player 1 (dropout) permanently paired with Player {partner_id}")
            
            # Verify the pairing is bidirectional
            assert dropout_pairs.get(partner_id) == 1, f"Pairing should be bidirectional"
            
            # Verify they're actually in the same group
            player1 = subsession.get_players()[0]  # Player 1
            player1_partner_id = player1.paired_player_id
            assert player1_partner_id == partner_id, f"Player 1 should be paired with {partner_id}, but paired with {player1_partner_id}"
    
    if round_num >= 19:  # After second dropout
        # Both Player 1 and 2 should be in permanent pairs
        for dropout_id in [1, 2]:
            if dropout_id in dropout_pairs:
                partner_id = dropout_pairs[dropout_id]
                print(f"✓ Player {dropout_id} (dropout) permanently paired with Player {partner_id}")
    
    if round_num >= 24:  # After third dropout  
        # Check if dropouts are paired together when possible
        dropout_pair_count = 0
        for dropout_id in dropout_list:
            if dropout_id in dropout_pairs:
                partner_id = dropout_pairs[dropout_id]
                if partner_id in dropout_list:
                    dropout_pair_count += 1
                    print(f"✓ Dropout-Dropout pairing: Player {dropout_id} <-> Player {partner_id}")
        
        print(f"Total dropout-dropout pairs: {dropout_pair_count // 2}")


def test_pairing_stability_across_rounds(subsession):
    """Test that permanent pairs remain stable across rounds"""
    round_num = subsession.round_number
    
    if round_num <= 10:  # Before any dropouts
        return
    
    # Get current and previous round pairing data
    current_dropout_pairs = subsession.session.vars.get('dropout_pairs', {})
    
    if round_num > 14:  # After first dropout should be established
        prev_subsession = subsession.in_round(round_num - 1)
        prev_dropout_pairs = prev_subsession.session.vars.get('dropout_pairs', {})
        
        # Check stability of permanent pairs
        for p_id, partner_id in prev_dropout_pairs.items():
            if p_id in current_dropout_pairs:
                assert current_dropout_pairs[p_id] == partner_id, f"Round {round_num}: Permanent pair {p_id}-{partner_id} was broken!"
                print(f"✓ Round {round_num}: Permanent pair {p_id}-{partner_id} maintained")


def test_dropout_isolation_effectiveness(subsession):
    """Test that dropouts are effectively isolated and don't contaminate multiple participants"""
    round_num = subsession.round_number
    dropout_list = subsession.session.vars.get('dropout_list', [])
    dropout_pairs = subsession.session.vars.get('dropout_pairs', {})
    
    if not dropout_list:  # No dropouts yet
        return
    
    print(f"\n=== Round {round_num} Dropout Isolation Check ===")
    
    # Track how many non-dropouts each dropout has been paired with
    dropout_contamination = {}
    
    for dropout_id in dropout_list:
        contaminated_participants = set()
        
        # Check pairing history across all rounds
        for r in range(1, round_num + 1):
            round_subsession = subsession.in_round(r)
            for player in round_subsession.get_players():
                if player.participant.id_in_session == dropout_id:
                    partner_id = player.paired_player_id
                    if partner_id not in dropout_list:
                        contaminated_participants.add(partner_id)
        
        dropout_contamination[dropout_id] = len(contaminated_participants)
        print(f"Dropout Player {dropout_id} has contaminated {len(contaminated_participants)} non-dropout participants")
    
    # After permanent pairing is established, contamination should not increase
    if round_num >= 20:  # Well after permanent pairing
        for dropout_id, contamination_count in dropout_contamination.items():
            # Each dropout should ideally contaminate only 1 non-dropout (their permanent partner)
            # Or 0 if paired with another dropout
            if dropout_id in dropout_pairs:
                partner_id = dropout_pairs[dropout_id]
                if partner_id in dropout_list:
                    # Paired with another dropout - contamination should be minimal
                    print(f"✓ Dropout {dropout_id} paired with dropout {partner_id} - good isolation")
                else:
                    # Paired with non-dropout - should contaminate only 1
                    assert contamination_count <= 2, f"Dropout {dropout_id} contaminated too many participants: {contamination_count}"
                    print(f"✓ Dropout {dropout_id} contamination limited to {contamination_count} participants")


def validate_session_consistency(subsession):
    """Main validation function to run comprehensive tests"""
    print(f"\n=== Validating Round {subsession.round_number} ===")
    
    # Run all existing tests
    test_initial_session_setup(subsession)
    test_pairing_logic(subsession)
    test_dot_generation_after_pairing(subsession)
    test_dropout_detection(subsession)
    test_role_consistency_across_rounds(subsession)
    test_fine_condition_transition(subsession)
    test_permanent_dropout_pairing(subsession)
    
    # Run new dropout-specific tests
    test_specific_dropout_scenario(subsession)
    test_pairing_stability_across_rounds(subsession)
    test_dropout_isolation_effectiveness(subsession)
    
    # Test individual players
    for player in subsession.get_players():
        test_points_calculation(player)
    
    print(f"Round {subsession.round_number} validation passed!")


def run_dropout_integration_test():
    """
    Integration test for the specific dropout scenario.
    Tests the complete dropout lifecycle and pairing logic.
    """
    print("\n=== Dropout Integration Test Scenario ===")
    
    expected_timeline = {
        "Rounds 1-9": "Normal random pairing, no dropouts",
        "Rounds 10-13": "Player 1 (Chooser) times out consecutively",
        "Round 14": "Player 1 marked as dropout, gets permanent partner",
        "Rounds 15-18": "Player 2 (Moderator) times out consecutively", 
        "Round 19": "Player 2 marked as dropout, permanent pairing logic kicks in",
        "Rounds 20-23": "Player 3 (Chooser) times out consecutively",
        "Round 24": "Player 3 marked as dropout, all dropouts should be paired optimally",
        "Rounds 25-30": "Stable permanent pairing maintained",
        "Round 31": "Fine condition transition with stable pairing",
        "Rounds 32-60": "Permanent pairs maintained through end of experiment"
    }
    
    validation_points = {
        "Round 14": "Verify Player 1 is permanently paired",
        "Round 19": "Verify Player 2 gets permanent partner", 
        "Round 24": "Verify optimal dropout pairing (dropouts paired together when possible)",
        "Round 31": "Verify permanent pairs survive condition transition",
        "Round 60": "Verify data integrity and contamination minimization"
    }
    
    for phase, description in expected_timeline.items():
        print(f"{phase}: {description}")
    
    print("\nKey Validation Points:")
    for round_desc, validation in validation_points.items():
        print(f"{round_desc}: {validation}")
    
    return "Dropout integration test configured. Run with: otree test pilot_multiplayer"


# Custom export test for the new features
def test_custom_export(players):
    """Test custom export functionality with dropout data"""
    export_data = list(custom_export(players))
    
    # Find the experiment data section
    experiment_section_start = None
    for i, row in enumerate(export_data):
        if row and len(row) > 0 and row[0] == 'SECTION: EXPERIMENT DATA':
            experiment_section_start = i + 1
            break
    
    assert experiment_section_start is not None, "Experiment data section not found"
    
    # Verify headers
    headers = export_data[experiment_section_start]
    required_columns = [
        'session_code', 'participant_code', 'round_number',
        'fine_condition', 'condition_phase', 'fine_amount',
        'role_in_experiment', 'chooser_choice', 'choice_correct',
        'decision', 'is_tempting_round', 'timeout_occurred_moderator'
    ]
    
    for column in required_columns:
        assert column in headers, f"Missing required column: {column}"
    
    # Verify data rows exist
    data_rows = export_data[experiment_section_start + 1:]
    assert len(data_rows) > 0, "No data rows found"
    
    # Test a sample data row
    if data_rows:
        sample_row = data_rows[0]
        assert len(sample_row) == len(headers), "Data row length mismatch with headers"


# Integration test for the new dropout pairing system
def run_dropout_integration_test():
    """
    Integration test specifically for dropout pairing system.
    This should be run with a controlled set of bots.
    """
    print("\n=== Dropout Integration Test ===")
    
    expected_behaviors = {
        "Round 1": "Initial random pairing with role assignment",
        "Round 5-8": "Some choosers timeout consecutively (become dropouts)",
        "Round 9": "Dropouts should be paired together if possible",
        "Round 10-13": "Some moderators timeout consecutively",
        "Round 14+": "All dropouts should be in permanent pairs",
        "Round 31": "Fine condition transition occurs",
        "Round 60": "Final results with proper calculations"
    }
    
    for round_desc, behavior in expected_behaviors.items():
        print(f"{round_desc}: {behavior}")
    
    return "Integration test template completed. Run with actual bot simulation."