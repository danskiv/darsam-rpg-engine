# Darsam RPG Engine - Changelog

## [2.1.0] - 2026-08-22
### Added
- **Dual AI Engine Integration:** Configured `openrouter/stealth/ox-alpha` as Primary Storyteller with `ag/gemini-3.7-flash-low` as High-Speed Fallback.
- **AI Processing Loading Indicator:** Real-time floating pulse banner (`#m-ai-loading`) displayed in controller during D20 rolls and AI narrative generation.
- **Desktop & Mobile Balanced UI:** Upgraded story pane to full vertical stretch (`flex-grow: 1`), enlarged narrative text (`text-base`), increased choices hitboxes, and eliminated whitespace.
- **Dual Fail-Safe Hydration:** Combined DOMContentLoaded & WebSocket `onopen` REST sync to guarantee choices render instantaneously on any browser.
- **Mathematical Combat Sync:** Monster defeat status is now strictly tied to numerical `HP <= 0`, preventing premature disappearance.

### Fixed
- Fixed choices button container rendering bug on initial character creation.
- Fixed controller body viewport clipping on small laptop displays by enabling smooth native vertical scrolling (`overflow-y: auto`, `pb-24`).
- Fixed prompt JSON schema enforcement to eliminate truncation.

## [2.0.0] - 2026-08-22
### Added
- **6-Slot Equipment System:** Added Head, Body, Feet, Accessory, Main Hand, and Off Hand equipment slots.
- **Weapon Handedness Engine:** Implemented 1-Hand, Off-Hand Only (Shields/Grimoires), Versatile (Dual Wielding with +15% ATK & Double Strike bonus), and Two-Handed Weapons (Greatsword/Longbow auto-locking Off-Hand).
- **40-Slot Backpack Expansion:** Upgraded inventory matrix from 25 to 40 slots with full filtering & sorting support.
- **Secret Job Awakening Engine:** Dynamic RNG trigger for rare classes across 4 tiers (Special, Epic, Legendary, Mythic) that can overwrite and stack as player explores deeper.
- **Dynamic Item Level (iLvl) & Scaled Consumables:** Monsters and shops scale gear and potions from Tier 1 to Tier 5 based on player level.
- **Skill Loadout Deck (3 Active Slots):** Players can manage skills in their Grimoire (unlocked every 5 levels) and equip up to 3 active combat skills directly accessible in battle.
- **Living Crypt Shop & Barter:** Implemented 5 specialized merchant encounters with Charisma-based Haggling and Sell All Junk features.
- **Comprehensive Project Documentation:** Created `PRD.md`, `docs/GAME_SYSTEMS.md`, and `CHANGELOG.md`.

## [1.2.0] - 2026-08-22
### Added
- Live Gemini 3.7 Flash Low AI Dungeon Master storytelling integration via 9Router.
- Web Audio procedural sound synthesizer (4 situational ambient themes & SFX).
- Animated D20 dice rolling chamber.

## [1.0.0] - 2026-08-21
### Initial Release
- Initial prototype of web-based dual screen RPG engine with FastAPI and WebSocket.
