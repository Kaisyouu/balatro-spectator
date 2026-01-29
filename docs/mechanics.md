# Balatro Core Mechanics

## 1. Scoring Formula
The score for a hand is calculated as:
**Score = Chips × Mult**

### 1.1 Base Values
Each hand type (High Card, Pair, etc.) has a base level with specific Chips and Mult. These increase as you level up the hand using Planet cards.

## 2. Evaluation Order (The Pipeline)
Calculation follows a strict sequence:
1.  **Base Hand**: Base Chips and Base Mult from the hand level.
2.  **Played Cards (Left to Right)**:
    -   Card Chips (Rank + Bonus)
    -   Card Mult (Enhancements like Mult Card)
    -   Editions (Foil, Holographic, Polychrome)
    -   Seals (Red Seal retriggers the card)
    -   Joker Triggers (e.g., "Played cards with Heart suit give +4 Mult")
3.  **Held in Hand (Left to Right)**:
    -   Steel cards, Gold cards.
    -   Jokers that trigger on cards held in hand (e.g., Baron, Mime).
4.  **Jokers (Left to Right)**:
    -   Additive Jokers (+Chips, +Mult)
    -   Multiplicative Jokers (xMult)
    -   *Positioning is critical for xMult.*

## 3. Blinds and Antes
-   **Small Blind**: Skips permitted. Gives 1x cash reward.
-   **Big Blind**: Gives 1.5x cash reward.
-   **Boss Blind**: Unique restrictions/abilities. Gives 2x cash reward.
-   **Ante**: A set of three blinds. Difficulty scales per Ante.

## 4. Interest
You earn $1 for every $5 held at the end of a round (capped at $5, unless Vouchers increase it).
