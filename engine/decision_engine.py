from typing import List, Dict, Optional, Union
from dataclasses import dataclass, field
from engine.scoring import Card, Joker, ScoringEngine
from engine.hand_evaluator import HandEvaluator
from engine.simulator import HandSimulator

@dataclass
class GameState:
    # Run stats
    ante: int = 1
    blind_type: str = "Small Blind"  # Small, Big, Boss
    money: int = 4
    
    # Player status
    jokers: List[Joker] = field(default_factory=list)
    consumables: List[str] = field(default_factory=list)
    hand: List[Card] = field(default_factory=list)
    deck: List[Card] = field(default_factory=list)
    
    # Round status
    hands_left: int = 4
    discards_left: int = 3
    required_score: int = 300
    current_score: int = 0
    
    # Shop status (if applicable)
    shop_items: List[Dict] = field(default_factory=list)

class DecisionEngine:
    def __init__(self):
        self.scoring_engine = ScoringEngine()
        self.simulator = HandSimulator(self.scoring_engine)
        self.evaluator = HandEvaluator()

    def recommend(self, state: GameState) -> Dict:
        """
        Analyzes the state and provides a recommendation.
        """
        if state.hand:
            return self._recommend_in_round(state)
        elif state.shop_items:
            return self._recommend_in_shop(state)
        else:
            return {"action": "wait", "reason": "No actionable state detected (no hand, no shop)."}

    def _recommend_in_round(self, state: GameState) -> Dict:
        # Find best hand to play
        hand_type, best_combo, result = self.simulator.find_best_hand(
            state.hand, 
            state.jokers, 
            self.evaluator.get_hand_type
        )
        
        # Heuristic: If this hand wins the round, play it.
        remaining_needed = state.required_score - state.current_score
        if result['total'] >= remaining_needed:
            return {
                "action": "play",
                "hand_type": hand_type,
                "cards": [f"{c.rank} of {c.suit}" for c in best_combo],
                "expected_score": result['total'],
                "reason": f"This hand will complete the blind ({result['total']} >= {remaining_needed})."
            }
        
        # Otherwise, suggest the best scoring hand
        return {
            "action": "play",
            "hand_type": hand_type,
            "cards": [f"{c.rank} of {c.suit}" for c in best_combo],
            "expected_score": result['total'],
            "reason": "Highest scoring hand available."
        }

    def _recommend_in_shop(self, state: GameState) -> Dict:
        # Very basic shop logic
        best_item = None
        for item in state.shop_items:
            if item['cost'] <= state.money:
                # Prioritize Jokers for now
                if item['type'] == 'Joker':
                    best_item = item
                    break
        
        if best_item:
            return {
                "action": "buy",
                "item": best_item['name'],
                "reason": f"Affordable {best_item['type']} that fits current budget."
            }
            
        return {"action": "skip", "reason": "Nothing affordable or valuable in shop."}
