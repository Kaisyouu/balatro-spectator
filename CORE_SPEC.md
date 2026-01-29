# Balatro Spectator - Core Specification

## Goal
An AI-assisted decision engine to provide optimal play and purchase suggestions for Balatro.

## Repository Structure
- `docs/`: Game mechanics, card data, and strategy notes.
- `engine/`: Core logic (Scoring, Simulation, AI).
- `data/`: JSON data for Jokers, Hands, and Blinds.
- `tests/`: Unit tests for scoring accuracy.

## Data Schema for Jokers
```json
{
  "id": "j_joker_name",
  "name": "Joker Name",
  "rarity": "Common|Uncommon|Rare|Legendary",
  "effect": {
    "type": "add_mult|x_mult|add_chips|retrigger|utility",
    "value": 0.0,
    "condition": "string_heuristic"
  }
}
```

## AI Instructions
When working on this codebase, always refer to `docs/mechanics.md` for scoring order and `docs/strategy.md` for decision priorities.
