# Darsam RPG Engine - Changelog

## [2.4.0] - 2026-08-22
### Added
- **Encounter Ecosystem Engine:** Fully integrated weighted encounter system with interactive Merchant Shops, Treasure Chests & Mimic detection, Branching Crossroads, and Campfire Rest Sites.
- **Living Crypt Merchant & Barter Encampment UI:** Embedded shop in controller with dual Buy/Sell tabs, live stock scaled to player level ($iLvl = \text{Player Level} \pm 1$), and Charisma-based Haggling (`CHA Check vs DC 11`).
- **Selective Item Selling & Equipped Gear Protection:** Players can select specific backpack items to sell for gold; actively equipped gear is protected and hidden from the sell list until explicitly unequipped.
- **One-Click "Sell All Junk" Engine:** Instant liquidation of all common white/gray gear and materials in the 40-slot backpack for fast gold acquisition.
- **Structured Story Item Rewards & Chest Auto-Loot:** AI JSON schema extended with `item_awarded` contract and automatic chest looting directly into player inventory upon successful story skill checks.
- **Expanded Cross-Class Awakening Tree (Common to Mythic):** Added diverse multi-tier secret classes (Common: Scavenger, Sellsword, Apothecary; Special: Pyromancer, Juggernaut; Epic: Storm-Weaver, Plague-Lord; Legendary: Solar Archangel, Ashen Dread-Emperor; Mythic: Primordial Ouroboros) allowing full cross-discipline transitions.
- **Infinite Dynamic Chapter & Floor Scaling Engine:** Implemented continuous milestone scaling ($\text{Chapter} = \lfloor(\text{Steps}-1)/8\rfloor + 1$ across 5 increasing floor depths) resolving late-game chapter stagnation.
- **Vitals Calculation Fix:** Enforced effective maximum HP and MP on all healing items, short rests, level-up restoration, and story events so gear bonuses are fully utilized.
- **Mobile Responsive Layout & Viewport Fixes:** Clean 4-row mobile header with symmetric 3-column vitals grid, EXP progress bar, 50:50 tab switcher, and safe bottom padding (`pb-32`).
- **Clean Standard English RPG Terms:** Standardized all technical terms in controller and TV interfaces (Skills, Backpack, Loadout, Equipped Slots, Ratios).

## [2.3.3] - 2026-08-22
### Added
- Deterministic Milestone-Based Chapter & Floor Progression (Chapter 1–5 across Floors 1–3).
- Mobile Responsive Header & Vitals Overhaul.
- Extended Bottom Safe Padding (`pb-32`).

## [2.3.2] - 2026-08-22
### Added
- Standardized all RPG technical terms to clean English.

## [2.3.1] - 2026-08-22
### Fixed
- Fixed undefined variable in controller Effective Max HP/MP calculation.

## [2.3.0] - 2026-08-22
### Added
- Intelligent Inventory Sorting (gear by Lv & rarity DESC, consumables below).
- Dynamic effective max HP/MP gear bonuses.
- Real rarity multipliers (Common 1.0x to Legendary 3.6x).
