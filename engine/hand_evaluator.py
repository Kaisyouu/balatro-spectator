from typing import List, Dict, Tuple
from collections import Counter
from engine.scoring import Card

class HandEvaluator:
    @staticmethod
    def get_hand_type(cards: List[Card]) -> str:
        if not cards:
            return "High Card"
            
        # Get ranks and suits
        ranks = []
        for c in cards:
            r = c.rank
            # Convert to numeric for sorting/math
            if r == 'A': val = 14
            elif r == 'K': val = 13
            elif r == 'Q': val = 12
            elif r == 'J': val = 11
            else: val = int(r)
            ranks.append(val)
        
        ranks.sort()
        suits = [c.suit for c in cards]
        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)
        
        # Check Flush
        is_flush = len(set(suits)) == 1 and len(cards) >= 5
        
        # Check Straight
        is_straight = False
        if len(cards) >= 5:
            # Normal straight
            if len(set(ranks)) == 5 and (max(ranks) - min(ranks) == 4):
                is_straight = True
            # Ace-low straight (A, 2, 3, 4, 5)
            elif set(ranks) == {14, 2, 3, 4, 5}:
                is_straight = True

        # Determine Hand Type
        if is_straight and is_flush: return "Straight Flush"
        if 4 in counts: return "Four of a Kind"
        if 3 in counts and 2 in counts: return "Full House"
        if is_flush: return "Flush"
        if is_straight: return "Straight"
        if 3 in counts: return "Three of a Kind"
        if counts.count(2) >= 2: return "Two Pair"
        if 2 in counts: return "Pair"
        
        return "High Card"

    @staticmethod
    def get_all_hands() -> List[str]:
        return [
            "Straight Flush", "Four of a Kind", "Full House", 
            "Flush", "Straight", "Three of a Kind", 
            "Two Pair", "Pair", "High Card"
        ]
