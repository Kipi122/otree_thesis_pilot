from otree.api import Currency as c, currency_range, expect, Submission
from . import *
import random
import json

class PlayerBot(Bot):
    
    # Single test case focusing on dropout scenario
    cases = ['dropout_test']

    def play_round(self):
        round_number = self.player.round_number
        
        # First round setup
        if round_number == 1:
            # Store this player's initial role for tracking
            self.participant.vars['initial_role'] = self.player.role
            self.participant.vars['timeout_rounds'] = []
            
            # Mark one specific Chooser as the dropout candidate
            if self.player.role == Constants.CHOOSER_ROLE and not self.session.vars.get('dropout_marked'):
                self.participant.vars['should_dropout'] = True
                self.session.vars['dropout_marked'] = True
                print(f"🎯 P{self.participant.id_in_session} marked as dropout candidate (Role: {self.player.role})")
            else:
                self.participant.vars['should_dropout'] = False
            
            yield WelcomePage, {
                'prolific_id': f'test_{self.participant.id_in_session}',
                'age': 25,
                'gender': 'Male'
            }
            
            yield Instructions
            yield TrainingIntro
            yield Submission(TrainingSetUp, {}, check_html=False)
            yield Submission(TrainingChooserDisplay, {}, check_html=False)
            
            # For training choice, use a simple approach
            training_choice = 'left' if random.random() < 0.5 else 'right'
            yield Submission(TrainingChooserChoice, {'training_choice': training_choice}, check_html=False)
            
            yield TrainingChooserFeedback
            yield TrainingModeratorCorrect
            yield TrainingModeratorIncorrect, {'training_decision': 'warn'}
            yield TrainingComplete
            
            yield ComprehensionCheck, {
                'comp_fine_amount': Constants.small_fine,  # Use the constant directly
                'comp_preferred_side': 'right'  # Use the default from session config
            }
            
            yield Submission(Role_Assignment, {}, check_html=False)

        # Transition page
        if round_number == Constants.transition_round:
            yield Submission(TransitionPage, {}, check_html=False)

        # Main game sequence
        yield Submission(SetUp, {}, check_html=False)
        yield Submission(DotDisplay, {}, check_html=False)
        
        # Handle role-specific pages
        if self.player.role == Constants.CHOOSER_ROLE:
            # Check if this player should timeout
            should_dropout = self.participant.vars.get('should_dropout', False)
            is_dropout_round = round_number in [10, 11, 12, 13]
            
            if should_dropout and is_dropout_round:
                print(f"🔴 R{round_number}: P{self.participant.id_in_session} (Chooser) TIMEOUT")
                self.participant.vars['timeout_rounds'].append(round_number)
                # For timeout, submit empty or don't set chooser_choice
                # This will trigger the timeout handling in before_next_page
                yield Submission(ChooserChoice, {}, timeout_happened=True, check_html=False)
            else:
                # Normal choice
                choice = self.make_choice()
                print(f"✅ R{round_number}: P{self.participant.id_in_session} (Chooser) chose {choice}")
                yield Submission(ChooserChoice, {'chooser_choice': choice}, check_html=False)
                
        else:  # Moderator role
            # Wait page happens automatically between Chooser and Moderator
            # After wait page, check if we need to make a decision
            
            # First, we need to check if the choice was correct
            # This info should be available after WaitForChooserChoice
            if not self.player.choice_correct:
                # Incorrect choice - moderator needs to decide
                decision = 'warn' if round_number % 2 == 0 else 'punish'
                print(f"✅ R{round_number}: P{self.participant.id_in_session} (Moderator) decided {decision}")
                yield Submission(ModeratorChoiceDisplay, {'decision': decision}, check_html=False)
            else:
                # Correct choice - just proceed
                print(f"✅ R{round_number}: P{self.participant.id_in_session} (Moderator) - choice was correct, proceeding")
                yield Submission(ModeratorChoiceDisplay, {}, check_html=False)
            
        yield Submission(FullFeedback, {}, check_html=False)
        
        # Final round
        if round_number == Constants.num_rounds:
            if self.player.role == Constants.MODERATOR_ROLE:
                yield End_Questionnaire_Moderator, {
                    'effectiveness_rating': 3,
                    'fairness_rating_1': 3,
                    'fairness_rating_2': 3,
                    'additional_comments': 'Test'
                }
            else:
                yield End_Questionnaire_Chooser, {
                    'effectiveness_rating': 3,
                    'fairness_rating_1': 3,
                    'fairness_rating_2': 3,
                    'additional_comments': 'Test'
                }
            
            yield Submission(Lottery, {}, check_html=False)
            yield Results
            
            # Final validation
            self.final_validation()

    def make_choice(self):
        """Make a choice based on the dots"""
        # Check if we have dot data
        if hasattr(self.player, 'correct_answer') and self.player.correct_answer:
            # Use the probabilistic logic from Constants
            if self.player.correct_answer == self.player.get_preferred_side():
                # 93% chance to be correct when preferred side is correct
                if random.random() < Constants.correct_probability_preferred:
                    return self.player.correct_answer
                else:
                    return 'left' if self.player.correct_answer == 'right' else 'right'
            else:
                # 60% chance to be correct when non-preferred side is correct
                if random.random() < Constants.correct_probability_not_preferred:
                    return self.player.correct_answer
                else:
                    return 'left' if self.player.correct_answer == 'right' else 'right'
        else:
            # Fallback to random choice
            return random.choice(['left', 'right'])

    def final_validation(self):
        """Validate the experiment results"""
        print("\n" + "="*70)
        print("DROPOUT SCENARIO VALIDATION REPORT")
        print("="*70)
        
        participant_id = self.participant.id_in_session
        was_dropout_candidate = self.participant.vars.get('should_dropout', False)
        timeout_rounds = self.participant.vars.get('timeout_rounds', [])
        
        print(f"\n📋 Participant P{participant_id} Summary:")
        print(f"  Role: {self.player.role} (id_in_group={self.player.id_in_group})")
        print(f"  Dropout candidate: {was_dropout_candidate}")
        print(f"  Timeout rounds recorded: {timeout_rounds}")
        
        # Check actual timeout flags in player data
        actual_timeout_rounds = []
        for r in range(1, Constants.num_rounds + 1):
            player_in_round = self.player.in_round(r)
            if player_in_round.timeout_occurred:
                actual_timeout_rounds.append(r)
        print(f"  Actual timeout flags: {actual_timeout_rounds}")
        
        if was_dropout_candidate:
            # Check dropout detection
            dropout_list = self.session.vars.get('dropout_list', [])
            is_dropout = participant_id in dropout_list
            
            print(f"\n🔍 Dropout Detection Analysis:")
            print(f"  Expected timeouts: [10, 11, 12, 13]")
            print(f"  Session dropout list: {dropout_list}")
            print(f"  Is in dropout list: {'✅ YES' if is_dropout else '❌ NO'}")
            
            # Check consecutive timeouts
            consecutive_count = 0
            for r in range(10, 14):
                if r in actual_timeout_rounds:
                    consecutive_count += 1
            print(f"  Consecutive timeouts (R10-13): {consecutive_count}/4")
            
            # Check if marked as dropout in player model
            print(f"  Player.is_dropout: {self.player.is_dropout}")
            print(f"  Participant.is_dropout: {self.player.participant.is_dropout}")
            
            if is_dropout:
                # Check permanent pairing
                dropout_pairs = self.session.vars.get('dropout_pairs', {})
                print(f"\n🔗 Permanent Pairing Analysis:")
                print(f"  All dropout pairs: {dropout_pairs}")
                
                if participant_id in dropout_pairs:
                    partner_id = dropout_pairs[participant_id]
                    print(f"  Assigned permanent partner: P{partner_id}")
                    
                    # Check pairing stability from round 14 onwards
                    stable_rounds = []
                    unstable_rounds = []
                    first_pair_round = None
                    
                    for r in range(14, min(Constants.num_rounds + 1, 25)):  # Check first 10 rounds after pairing
                        player_in_round = self.player.in_round(r)
                        actual_partner = player_in_round.paired_player_id
                        
                        if actual_partner == partner_id:
                            stable_rounds.append(r)
                            if first_pair_round is None:
                                first_pair_round = r
                        else:
                            unstable_rounds.append((r, actual_partner))
                    
                    print(f"  First paired in round: {first_pair_round}")
                    print(f"  Stable pairing rounds: {len(stable_rounds)} rounds")
                    
                    if unstable_rounds:
                        print(f"  ❌ Pairing changes detected:")
                        for r, partner in unstable_rounds[:5]:  # Show first 5 changes
                            print(f"      Round {r}: paired with P{partner} instead of P{partner_id}")
                    else:
                        print(f"  ✅ Pairing remained stable after establishment")
                else:
                    print(f"  ❌ No permanent partner assigned despite being in dropout list")
            else:
                print(f"\n⚠️ WARNING: Dropout candidate was not detected as dropout!")
                print(f"  This suggests the dropout detection logic may not be working correctly")
        
        # Check dot generation consistency
        print(f"\n🎲 Dot Generation Check (Final Round):")
        if hasattr(self.player, 'dots_left'):
            print(f"  Dots left: {self.player.dots_left}")
            print(f"  Dots right: {self.player.dots_right}")
            print(f"  Total: {self.player.dots_left + self.player.dots_right} (expected: {Constants.total_dots})")
            print(f"  Correct answer: {self.player.correct_answer}")
            print(f"  Is tempting round: {self.player.is_tempting_round}")
            print(f"  Preferred side: {self.player.get_preferred_side()}")
            
            # Verify dot distribution matches correct answer
            if self.player.dots_left > self.player.dots_right:
                expected_correct = 'left'
            else:
                expected_correct = 'right'
                
            if expected_correct == self.player.correct_answer:
                print(f"  ✅ Correct answer matches dot distribution")
            else:
                print(f"  ❌ ERROR: Correct answer doesn't match dot distribution!")
            
            # Verify tempting round logic
            preferred_side = self.player.get_preferred_side()
            if self.player.is_tempting_round:
                if self.player.correct_answer != preferred_side:
                    print(f"  ✅ Tempting logic correct (correct≠preferred)")
                else:
                    print(f"  ❌ Tempting logic error (correct should ≠ preferred)")
            else:
                if self.player.correct_answer == preferred_side:
                    print(f"  ✅ Non-tempting logic correct (correct=preferred)")
                else:
                    print(f"  ❌ Non-tempting logic error (correct should = preferred)")
        
        # Check role consistency
        print(f"\n👥 Role Consistency Check:")
        initial_role = self.participant.vars.get('initial_role')
        role_changes = []
        id_changes = []
        
        for r in range(1, min(Constants.num_rounds + 1, 20)):  # Check first 20 rounds
            round_player = self.player.in_round(r)
            if round_player.role != initial_role:
                role_changes.append(r)
            if round_player.id_in_group != self.player.in_round(1).id_in_group:
                id_changes.append(r)
        
        if role_changes:
            print(f"  ❌ Role changed in rounds: {role_changes[:10]}")  # Show first 10
        else:
            print(f"  ✅ Role remained consistent: {initial_role}")
            
        if id_changes:
            print(f"  ❌ ID in group changed in rounds: {id_changes[:10]}")
        else:
            print(f"  ✅ ID in group remained consistent: {self.player.id_in_group}")
        
        # Check fine condition transition
        print(f"\n💰 Fine Condition Transition Check:")
        if Constants.transition_round <= Constants.num_rounds:
            round_before = min(Constants.transition_round - 1, Constants.num_rounds)
            round_after = min(Constants.transition_round + 1, Constants.num_rounds)
            
            fine_before = self.player.in_round(round_before).fine_condition
            fine_after = self.player.in_round(round_after).fine_condition
            
            print(f"  Round {round_before} (before): {fine_before} fine")
            print(f"  Round {round_after} (after): {fine_after} fine")
            
            if fine_before != fine_after:
                print(f"  ✅ Fine condition changed at transition")
            else:
                print(f"  ❌ Fine condition did not change at transition")
        
        # Summary
        print(f"\n📊 Summary:")
        dropout_success = was_dropout_candidate and (participant_id in dropout_list)
        pairing_success = dropout_success and (participant_id in dropout_pairs)
        
        if was_dropout_candidate:
            if dropout_success and pairing_success:
                print("  ✅ Dropout detection and permanent pairing working correctly")
            elif dropout_success and not pairing_success:
                print("  ⚠️ Dropout detected but permanent pairing not established")
            else:
                print("  ❌ Dropout detection failed - check timeout handling")
        else:
            print("  ℹ️ This participant was not the dropout candidate")
        
        print("\n" + "="*70)
        print("END OF VALIDATION REPORT")
        print("="*70 + "\n")