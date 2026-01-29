from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class Card:
    rank: str  # '2'-'10', 'J', 'Q', 'K', 'A'
    suit: str  # 'Hearts', 'Diamonds', 'Clubs', 'Spades'
    enhancement: Optional[str] = None  # 'Bonus', 'Mult', 'Wild', 'Glass', 'Steel', 'Stone', 'Lucky'
    edition: Optional[str] = None      # 'Foil', 'Holographic', 'Polychrome', 'Negative'
    seal: Optional[str] = None         # 'Red', 'Blue', 'Gold', 'Purple'
    
    def get_base_chips(self) -> int:
        if self.enhancement == 'Stone':
            return 50
        rank_map = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        return rank_map.get(self.rank, 0)

@dataclass
class Joker:
    id: str
    name: str
    effect_type: str  # 'add_mult', 'x_mult', 'add_chips', 'retrigger'
    value: float
    position: int

@dataclass
class HandLevel:
    chips: int
    mult: int

class ScoringEngine:
    def __init__(self):
        # Base stats for Level 1 hands (simplified)
        self.hand_base_stats = {
            'High Card': HandLevel(5, 1),
            'Pair': HandLevel(10, 2),
            'Two Pair': HandLevel(20, 2),
            'Three of a Kind': HandLevel(30, 3),
            'Straight': HandLevel(30, 4),
            'Flush': HandLevel(35, 4),
            'Full House': HandLevel(40, 4),
            'Four of a Kind': HandLevel(60, 7),
            'Straight Flush': HandLevel(100, 8),
            'Five of a Kind': HandLevel(120, 12),
        }

    def calculate_score(
        self, 
        hand_type: str, 
        played_cards: List[Card], 
        held_cards: List[Card], 
        jokers: List[Joker]
    ) -> Dict[str, float]:
        """
        Calculates the score following Balatro's exact pipeline.
        """
        base = self.hand_base_stats.get(hand_type, HandLevel(0, 0))
        chips = float(base.chips)
        mult = float(base.mult)

        # 1. Played Cards
        for card in played_cards:
            # Add base chips
            chips += card.get_base_chips()
            
            # Enhancements
            if card.enhancement == 'Bonus':
                chips += 30
            elif card.enhancement == 'Mult':
                mult += 4
            elif card.enhancement == 'Glass':
                mult *= 2
            
            # Editions
            if card.edition == 'Foil':
                chips += 50
            elif card.edition == 'Holographic':
                mult += 10
            elif card.edition == 'Polychrome':
                mult *= 1.5

        # 2. Held in Hand
        for card in held_cards:
            if card.enhancement == 'Steel':
                mult *= 1.5

        # 3. Jokers (Left to Right sequence)
        sorted_jokers = sorted(jokers, key=lambda x: x.position)
        
        for joker in sorted_jokers:
            if joker.effect_type == 'add_chips':
                chips += joker.value
            elif joker.effect_type == 'add_mult':
                mult += joker.value
            elif joker.effect_type == 'x_mult':
                mult *= joker.value

        # Final floor and calculation
        chips = max(0.0, chips)
        mult = max(1.0, mult)
        
        return {
            "chips": round(chips),
            "mult": round(mult),
            "total": round(chips) * round(mult)
        }

if __name__ == "__main__":
    # Test case: Flush with a basic Joker and one Steel card in hand
    engine = ScoringEngine()
    played = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('Q', 'Hearts', edition='Foil'),
        Card('J', 'Hearts'),
        Card('10', 'Hearts')
    ]
    held = [Card('2', 'Spades', enhancement='Steel')]
    jokers = [
        Joker('j_joker', 'Joker', 'add_mult', 4, 0),
        Joker('j_poly', 'Polychrome Joker', 'x_mult', 1.5, 1)
    ]
    
    result = engine.calculate_score('Flush', played, held, jokers)
    print(f"Test Result: {result['chips']} Chips x {result['mult']} Mult = {result['total']}")
