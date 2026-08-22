# Darsam RPG Engine - Changelog

## [2.4.0-dev] - 2026-08-22 (Branch: feat/encounter-ecosystem)
### Added
- **Dynamic Living Crypt Merchant & Barter Encampment UI:** Full interactive merchant shop embedded in controller when entering `merchant` node type, featuring real-time stock scaled to player level ($iLvl = \text{Player Level} \pm 1$).
- **Haggling via Charisma Check (`CHA Check vs DC 11`):** Roll D20 to attempt haggling prices with merchants (20% discount on Success, 40% discount on Natural 20, 15% surcharge on Fail).
- **One-Click "Sell All Junk" Engine:** Instant liquidation of all common white/gray gear & materials in 40-slot backpack directly to merchant for immediate gold.
- **Dynamic Encounter Types in Storyteller Prompt:** Expanded AI prompt to natively support and generate `combat`, `merchant`, `crossroads`, `chest`, `campfire`, `shrine`, and `exploration` nodes.
- **Established Feature Branch:** Development cleanly organized and tracked on `feat/encounter-ecosystem`.

## [2.3.3] - 2026-08-22
### Added
- Deterministic Milestone-Based Chapter & Floor Progression (Chapter 1–5 across Floors 1–3).
- Mobile Responsive Header & Vitals Overhaul.
- Extended Bottom Safe Padding (`pb-32`).
