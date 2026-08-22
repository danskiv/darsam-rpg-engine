# Darsam RPG Dungeon Engine - PRD v2.0.0 (Grandmaster Ultimate Edition)

## 1. Executive Summary
**Darsam RPG Dungeon Engine** adalah platform game solo interactive Tabletop RPG (TTRPG) bergaya *Dark Fantasy* berbasis arsitektur **Dual-Screen (TV Companion Display & Standalone Mobile/Desktop Controller)**.
Game ini ditenagai oleh **Gemini 3.7 Flash Low** melalui gateway 9Router di VPS Oracle Cloud untuk menciptakan narasi tanpa batas (*Infinite Emergent Narrative*), dipadukan dengan mekanik RPG berstandar internasional (*Old School Renaissance / OSR, Diablo ARPG loot tables, and Path of Exile itemization*).

---

## 2. Core Pillars of Version 2.0.0
1. **100% Standalone Controller:** Controller di HP atau Laptop dapat mengakses seluruh fitur game (Story, Combat, Active Skills, 6-Slot Gear, 40-Slot Backpack, Shop/Barter, Dice, & Awakening) secara independen tanpa bergantung ke TV.
2. **Atmospheric TV Companion Display:** Layar TV 32" bertindak sebagai papan visual taktis (Vitals, 6 Core Stats, 40-Slot Grid Matrix, Paper Doll, D20 Chamber, Monster Card, & Rarity Aura Glow).
3. **8 Base Origins to Secret Awakening:** Pemain memulai dari 8 latar belakang warga biasa (Zero to Hero) dan berpeluang memicu pergantian kelas rahasia bertingkat kelangkaan (**Special ➔ Epic ➔ Legendary ➔ Mythic**) secara dinamis lewat event langka.
4. **Dynamic Item Level (iLvl) & Scaled Consumables:** Perlengkapan dan item konsumsi (Tier 1–5) di toko dan drop monster secara otomatis menyesuaikan dengan level pemain.
5. **6-Slot Paper Doll & Weapon Handedness:** Mendukung slot Head, Body, Feet, Accessory, Main Hand, dan Off Hand dengan mekanik 1-Hand, Off-Hand Only (Shields/Grimoires/Quivers), Versatile (Dual Wielding), dan 2-Handed (Greatsword/Bow yang mengunci slot kedua).
6. **Skill Loadout Deck (3 Active Slots):** Pengelolaan jurus melalui Grimoire (buku jurus terbuka tiap 5 level & drop tomes), di mana 3 jurus aktif dapat dieksekusi langsung saat pertarungan di tab Cerita.
7. **Living Crypt Economy:** Sistem toko pedagang acak (Scavenger, Black Market, Blood Merchant, Relic Gambler, Blacksmith) dengan tawar-menawar (*Haggling via CHA Check*) dan jasa tempa senjata (+1 s/d +5).

---

## 3. System Architecture
```
[Mobile / Laptop Browser] ◄──(WebSocket / REST)──► [FastAPI Backend] ──(9Router)──► [Gemini 3.7 Flash Low]
(Controller: Port 8090)                               (VPS NODIX1)
                                                           │
                                                   (WebSocket State)
                                                           ▼
                                                [Android TV Browser / App]
                                                    (TV: Port 8090/tv)
```

---

## 4. Versioning & Milestone Records
- **v1.0.0:** Purwarupa statis Python state machine dengan 4 job dasar dan tampilan web sederhana.
- **v1.2.0:** Integrasi Live Gemini 3.7 Flash Low, Web Audio Procedural Synthesizer, dan Dadu D20 animasi.
- **v2.0.0 (Current):** Grandmaster Edition (8 Origins, Secret Awakening RNG, 6-Slot Paper Doll, Handedness, 40-Slot Bag, iLvl Scaling, Living Shop, Tabbed Controller, & Complete Documentation).
