# Darsam RPG Engine - Changelog

## [2.2.0] - 2026-08-22
### Added
- **Natural Character Naming in In-Game Narrative:** Prompt system updated to strictly address the protagonist by their custom character name (e.g. `Danas`, `Danas mengayunkan cangkul...`) eliminating royal honorifics inside game lore.
- **D20 Stat Modifier & Difficulty Balance Engine:** Implemented official TTRPG formula `(Attribute - 10) // 2` added to raw D20 rolls vs balanced DC (8–12), fixing high unfair failure rates.
- **Multi-Source Proper EXP Progression:** EXP awarded from Monster Kills, Skill Check Successes (+15 EXP), and D20 Critical Successes (+25 EXP).
- **Consumable Item Stacking System:** Consumables of the same type automatically stack into 1 inventory slot with a `qty` counter (e.g. `x3`, `x5`).
- **Dynamic Equipment Item Level (iLvl) & Real Rarity Scaling:** Equipment now features explicit item levels (`Lv.N`) and non-linear stat multipliers per rarity (*Common 1.0x, Uncommon 1.3x, Rare 1.8x, Epic 2.5x, Legendary 3.6x*), ensuring higher rarity items have distinctly superior attributes.
- **Dynamic 9Router/Hermes Model Catalog (385 Models):** Exposed full live model roster to controller dropdowns with priority ordering.
- **Real-Time EXP Progress Bar in Controller:** Added visual EXP progress gauge in controller header and Tab 2 status details.

## [2.1.0] - 2026-08-22
### Added
- Dual AI Engine Integration (OX-Alpha Primary + Gemini 3.7 Fallback).
- Real-time AI processing pulse banner overlay.
- Desktop & Mobile balanced layout with enlarged text.
- Mathematical combat lock on monster HP <= 0.

## [2.0.0] - 2026-08-22
### Added
- 6-Slot Paper Doll Equipment & Weapon Handedness (1-Hand, Off-Hand Only, Versatile Dual Wield, Two-Handed Lock).
- 40-Slot Backpack Expansion.
- Secret Job Awakening Engine (Special, Epic, Legendary, Mythic).
