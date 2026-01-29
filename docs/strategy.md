# Strategy Engine Blueprint

## 1. Expected Value (EV) Calculation
For any given hand and set of discards, the engine should calculate the average expected score, accounting for:
- Probabilities of "1 in X" triggers (Lucky, Glass, Bloodstone).
- Probabilities of drawing specific cards if discarding.

## 2. Shop Logic
- **Interest vs. Power**: Is buying this Joker worth losing $1/round of interest?
- **Scaling**: Priority given to Jokers that scale over time (e.g., Constellation, Green Joker, Ride the Bus).
- **Synergy Check**: Does this Joker multiply my existing build or just add flat value?

## 3. Boss Blind Preparation
- The engine must flag upcoming Bosses that counter the current build (e.g., "The Flint" halving base chips/mult).
