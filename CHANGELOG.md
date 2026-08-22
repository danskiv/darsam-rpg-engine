# Darsam RPG Engine - Changelog

## [2.3.0] - 2026-08-22
### Added
- **Intelligent Inventory Sorting Hierarchy:** Backpack automatically sorts all 40 slots with Equipment on top (ranked by Item Level DESC, then Rarity DESC), followed by Consumables and Materials below.
- **Dynamic Effective Max HP & Max MP Calculation:** Equipment with HP and MP bonus stats now immediately expands and updates total Max HP/MP on both Controller and TV display.
- **Strict Rarity Scaling Multiplier:** Completely overhauled loot generator to guarantee that Rare/Epic/Legendary equipment consistently rolls significantly higher stats than Common items of the same level.

## [2.2.0] - 2026-08-22
### Added
- **Option A Visual Choice Badges:** Clean narrative text with iconic color-coded stat target badges (`[💪 STR • Target: 11]`).
- **Natural Character Naming:** In-game story strictly addresses the player by their character name.
- **Consumable Item Stacking:** Identical consumables automatically stack into 1 inventory slot (`qty: N`).
- **D20 Stat Modifiers:** Standard TTRPG formula `(Score - 10) // 2` applied to rolls.
- **Multi-Source EXP:** EXP awarded for Monster Kills, Skill Check Successes (+15 EXP), and Critical Hits (+25 EXP).

## [2.1.0] - 2026-08-22
### Added
- Dual AI Engine (OX-Alpha Primary + Gemini 3.7 Fallback).
- Real-time AI processing pulse banner overlay.
- Desktop & Mobile balanced layout with enlarged text.
- Mathematical combat lock on monster HP <= 0.
