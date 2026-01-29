import json
import os
from engine.decision_engine import DecisionEngine, GameState
from engine.scoring import Card, Joker

def parse_card(card_str: str) -> Card:
    # Format: "Rank of Suit" or "Rank of Suit [Enhancement]"
    parts = card_str.split(' of ')
    rank = parts[0]
    suit_parts = parts[1].split(' ')
    suit = suit_parts[0]
    enhancement = None
    if len(suit_parts) > 1:
        enhancement = suit_parts[1].strip('[]')
    return Card(rank=rank, suit=suit, enhancement=enhancement)

def main():
    print("=== Balatro Spectator CLI ===")
    print("Feed me the game state, and I'll tell you what to do.")
    
    engine = DecisionEngine()
    
    while True:
        print("\nOptions: [1] Load State from JSON [2] Manual Input (Quick) [q] Quit")
        choice = input("> ").lower()
        
        if choice == 'q':
            break
            
        state = None
        if choice == '1':
            path = input("Enter path to state.json: ")
            if os.path.exists(path):
                with open(path, 'r') as f:
                    raw_data = json.load(f)
                    # Convert raw data to GameState (simplified conversion)
                    state = GameState(
                        ante=raw_data.get('ante', 1),
                        money=raw_data.get('money', 0),
                        required_score=raw_data.get('required_score', 300),
                        current_score=raw_data.get('current_score', 0)
                    )
                    state.hand = [parse_card(c) for c in raw_data.get('hand', [])]
                    state.jokers = [Joker(j['id'], j['name'], j['type'], j['value'], i) 
                                   for i, j in enumerate(raw_data.get('jokers', []))]
            else:
                print("File not found.")
                continue
        
        elif choice == '2':
            # Fast manual input for a round
            print("Enter hand (e.g. 'A of Hearts, K of Hearts'):")
            cards_input = input("> ")
            hand = [parse_card(c.strip()) for c in cards_input.split(',')]
            
            state = GameState(hand=hand)
            # Add some default jokers if needed or ask
            state.required_score = int(input("Required Score (default 300): ") or 300)

        if state:
            recommendation = engine.recommend(state)
            print("\n--- RECOMMENDATION ---")
            print(f"ACTION: {recommendation['action'].upper()}")
            if 'hand_type' in recommendation:
                print(f"HAND: {recommendation['hand_type']}")
                print(f"CARDS: {', '.join(recommendation['cards'])}")
            print(f"REASON: {recommendation['reason']}")
            print("-----------------------")

if __name__ == "__main__":
    main()
