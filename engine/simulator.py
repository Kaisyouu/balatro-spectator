import itertools
from typing import List, Tuple
from engine.scoring import ScoringEngine, Card, Joker

class HandSimulator:
    def __init__(self, engine: ScoringEngine):
        self.engine = engine

    def find_best_hand(
        self, 
        hand: List[Card], 
        jokers: List[Joker], 
        hand_type_finder_callback
    ) -> Tuple[str, List[Card], dict]:
        """
        Finds the 5-card combination that results in the highest score.
        Note: This is computationally expensive if done naively for all 5-card combos 
        of a large hand, but Balatro hands are small (max ~12).
        """
        best_score = -1
        best_combo = []
        best_hand_type = ""
        best_result = {}

        # Balatro allows playing 1 to 5 cards.
        for r in range(1, 6):
            for combo in itertools.combinations(hand, r):
                combo_list = list(combo)
                # Identify the hand type (e.g., Flush, Straight, etc.)
                hand_type = hand_type_finder_callback(combo_list)
                
                # Cards not in the combo are "held in hand"
                held_cards = [c for c in hand if c not in combo_list]
                
                result = self.engine.calculate_score(hand_type, combo_list, held_cards, jokers)
                
                if result['total'] > best_score:
                    best_score = result['total']
                    best_combo = combo_list
                    best_hand_type = hand_type
                    best_result = result
        
        return best_hand_type, best_combo, best_result

# Example Hand Type Finder (Mock)
def mock_hand_finder(cards: List[Card]) -> str:
    # This would normally have logic to detect Flush, Straight, etc.
    if len(cards) == 5:
        return "Flush"
    return "High Card"
