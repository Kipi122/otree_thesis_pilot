from otree.api import *
from . import *
import random
import time


def call_live_method(method, **kwargs):
    """Simulate live method calls for pages that use JavaScript interaction"""
    
    page_class = kwargs.get('page_class')
    round_number = kwargs.get('round_number')
    
    # Handle TrainingChooserChoice page
    if page_class == TrainingChooserChoice:
        # Simulate player making a choice
        choice = random.choice(['left', 'right'])
        choice_time = random.uniform(0.5, 3.0)  # Simulate reaction time
        method(1, {'choice': choice, 'choice_time': choice_time})
        
    # Handle ChooserChoice page (main experiment)
    elif page_class == ChooserChoice:
        # Find the chooser player (should be player with CHOOSER_ROLE)
        # In multiplayer, we need to simulate the chooser's choice
        for player_id in [1, 2]:
            try:
                # Try to call method for each player to find the chooser
                # The chooser will accept the call, moderator will ignore it
                choice = random.choice(['left', 'right'])
                choice_time = random.uniform(0.5, 3.0)
                result = method(player_id, {
                    'choice': choice,
                    'choice_time': choice_time
                })
                if result and player_id in result:
                    # Successfully recorded choice for this player
                    break
            except:
                continue
    
    # Handle ModeratorChoiceDisplay page
    elif page_class == ModeratorChoiceDisplay:
        # Find the moderator player and simulate their decision
        for player_id in [1, 2]:
            try:
                # Moderator only makes a decision if choice was incorrect
                # Simulate decision with some strategy
                decision = 'punish' if random.random() < 0.5 else 'warn'
                decision_time = random.uniform(1.0, 4.0)
                result = method(player_id, {
                    'decision': decision,
                    'decision_time': decision_time
                })
                if result and player_id in result:
                    # Successfully recorded decision for this player
                    break
            except:
                continue


class PlayerBot(Bot):
    cases = ['aggressive', 'lenient', 'mixed']  # Different moderator strategies
    
    def play_round(self):
        # Only run certain pages on round 1
        if self.round_number == 1:
            # Mobile Check - commented out as per your setup
            # yield MobileCheck, dict(is_mobile=False)
            
            # Welcome Page (if not debug mode)
            if not Constants.debug:
                yield WelcomePage, dict(
                    prolific_id=f"TEST_ID_{self.participant.id_in_session}_{random.randint(1000,9999)}",
                    age=random.randint(18, 65),
                    gender=random.choice(['Male', 'Female', 'Other'])
                )
            
            # Instructions
            if not Constants.debug:
                yield Instructions
            
            # Training sequence
            if not Constants.debug:
                yield TrainingIntro
                
                # TrainingSetUp - timeout page with fixation cross
                yield Submission(TrainingSetUp, timeout_happened=True, check_html=False)
                
                # TrainingChooserDisplay - timeout page showing dots
                yield Submission(TrainingChooserDisplay, timeout_happened=True, check_html=False)
                
                # TrainingChooserChoice - will use call_live_method
                yield Submission(TrainingChooserChoice, {'training_choice': random.choice(['left', 'right'])}, check_html=False)

                yield TrainingChooserFeedback
                yield TrainingModeratorCorrect
                
                # Training decision for moderator
                training_decision = 'punish' if self.case == 'aggressive' else 'warn'
                yield TrainingModeratorIncorrect, dict(training_decision=training_decision)
                
                yield TrainingComplete
            
            # Comprehension Check
            if not Constants.debug:
                # Get the correct answers
                correct_fine = self.player.get_fine_amount()
                correct_preferred = self.player.get_preferred_side()
                
                # Test error handling occasionally
                if random.random() < 0.5:  # 20% chance to make a mistake
                    wrong_fine = 99 if correct_fine == 11 else 11
                    yield Submission(
                        ComprehensionCheck, 
                        dict(
                            comp_fine_amount=wrong_fine,
                            comp_preferred_side=correct_preferred
                        ),
                        #error_fields=['comp_fine_amount']
                    )
                    # Now submit correct answers on ComprehensionFailed page
                    yield ComprehensionFailed, dict(
                        comp_fine_amount=correct_fine,
                        comp_preferred_side=correct_preferred
                    )
                else:
                    # Submit correct answers immediately
                    yield ComprehensionCheck, dict(
                        comp_fine_amount=correct_fine,
                        comp_preferred_side=correct_preferred
                    )
            
            # WaitingForOtherToFinishInstructions - WaitPage, handled automatically
            
            # Role_Assignment - timeout page
            yield Submission(Role_Assignment, timeout_happened=True)
            
            # Verify role assignment
            expect(self.player.role in [Constants.MODERATOR_ROLE, Constants.CHOOSER_ROLE], True)
            expect(self.player.role_in_experiment, self.player.role)
        
        # Transition page (only at round 41 for within-session)
        if self.round_number == Constants.transition_round and Constants.is_within_session:
            yield Submission(TransitionPage, timeout_happened=True)
            
            # Verify fine condition changed
            old_fine = Constants.small_fine if self.participant.vars['initial_fine_condition'] == 'small' else Constants.large_fine
            new_fine = Constants.large_fine if self.participant.vars['initial_fine_condition'] == 'small' else Constants.small_fine
            current_fine = self.player.get_fine_amount()
            expect(current_fine, new_fine)
        
        # PairingParticipants - WaitPage, handled automatically
        
        # Main game pages (all rounds)
        # SetUp page - timeout page (fixation cross)
        yield Submission(SetUp, timeout_happened=True, check_html=False)
        
        # DotDisplay - timeout page (shows dots)
        yield Submission(DotDisplay, timeout_happened=True, check_html=False)
        
        # Role-specific pages
        if self.player.role == Constants.CHOOSER_ROLE:
            # ChooserChoice - will use call_live_method to make actual choice
            yield ChooserChoice, {"chooser_choice": random.choice(['left', 'right'])}

            # Verify choice was recorded
            expect(self.player.chooser_choice in ['left', 'right'], True)
            
            # Verify choice characteristics
            expect(self.player.choice_correct in [True, False], True)
            expect(self.player.preferred_side_chosen in [True, False], True)
            
        elif self.player.role == Constants.MODERATOR_ROLE:
            # WaitForChooserChoice - WaitPage, handled automatically
            
            # ModeratorChoiceDisplay - will use call_live_method
            yield ModeratorChoiceDisplay
            
            # Check if a decision was made (only for incorrect choices)
            if not self.player.choice_correct:
                # Verify decision was recorded based on test case
                if self.case == 'aggressive':
                    # Aggressive moderator punishes more often
                    expect(self.player.decision in ['punish', 'warn'], True)
                elif self.case == 'lenient':
                    # Lenient moderator warns more often
                    expect(self.player.decision in ['punish', 'warn'], True)
                else:  # mixed
                    expect(self.player.decision in ['punish', 'warn'], True)
        
        # WaitForModeratorDecision - WaitPage for Chooser, handled automatically
        
        # FullFeedback - timeout page showing feedback
        yield Submission(FullFeedback, timeout_happened=True, check_html=False)
        
        # Verify points calculation after feedback
        if self.player.role == Constants.CHOOSER_ROLE:
            # Check chooser points logic
            if self.player.choice_correct:
                expected_points = 10 if self.player.preferred_side_chosen else 0
                expect(self.player.round_chooser_points, expected_points)
            else:
                if self.player.decision == 'punish':
                    expected_points = (10 - self.player.get_fine_amount() if self.player.preferred_side_chosen 
                                     else -self.player.get_fine_amount())
                else:  # warn
                    expected_points = 10 if self.player.preferred_side_chosen else 0
                expect(self.player.round_chooser_points, expected_points)
        
        elif self.player.role == Constants.MODERATOR_ROLE:
            # Check moderator points
            if not self.player.timeout_occurred_moderator:
                expected_points = 10 if self.player.choice_correct else 0
            else:
                expected_points = -Constants.timeout_penalty
            expect(self.player.round_moderator_points, expected_points)
        
        # Verify cumulative points are updating
        #if self.round_number > 1:
        #    expect(self.player.total_points >= 0, True)
        #    expect(self.player.total_chooser_points >= 0, True)
        #    expect(self.player.total_moderator_points >= 0, True)
        
        # Final round pages
        if self.round_number == Constants.num_rounds:
            # End questionnaire based on role
            questionnaire_data = dict(
                effectiveness_rating=random.randint(2, 4),  # Middle ratings
                fairness_rating_1=3 if self.case == 'lenient' else 2,
                fairness_rating_2=2 if self.case == 'aggressive' else 3,
                additional_comments=f"Bot test case: {self.case}"
            )
            
            if self.player.role == Constants.MODERATOR_ROLE:
                yield End_Questionnaire_Moderator, questionnaire_data
            else:
                yield End_Questionnaire_Chooser, questionnaire_data
            
            # Lottery page - instant timeout
            yield Submission(Lottery, timeout_happened=True, check_html=False)

            # Results page
            yield Submission(Results, check_html=False)

            # Final verifications
            expect(self.player.finished, True)
            expect(self.participant.finished, True)
            
            # Verify total points match role
            if self.player.role == Constants.CHOOSER_ROLE:
                expect(self.player.total_points, self.player.total_chooser_points)
            else:
                expect(self.player.total_points, self.player.total_moderator_points)
            
            # Verify lottery was run
            expect(self.player.lottery_won in [True, False], True)
            
            # Check monetary payoff calculation
            if self.player.lottery_won:
                min_payoff = Constants.participation_fee + Constants.bonus_fee
            else:
                min_payoff = Constants.participation_fee
            
            # Add waiting compensation if applicable
            if self.player.got_waiting_compensation:
                min_payoff += self.player.waiting_compensation
            
            expect(self.player.total_monetary_payoff >= min_payoff, True)