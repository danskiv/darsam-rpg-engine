# Darsam RPG Dungeon Engine - PRD v2.2.0 (Grandmaster Ultimate Edition)

## 1. Executive Summary
**Darsam RPG Dungeon Engine** adalah platform game solo interactive Tabletop RPG (TTRPG) bergaya *Dark Fantasy* berbasis arsitektur **Dual-Screen (TV Companion Display & Standalone Mobile/Desktop Controller)**.
Game ini ditenagai oleh **OX-Alpha (Primary Reasoning Engine)** dan **Gemini 3.7 Flash Low (Speed Fallback)** dengan katalog 385 model AI dinamis yang dapat dipilih kapan saja oleh pemain.

---

## 2. Core Pillars of Version 2.2.0
1. **Balanced RPG Dice & Stat Modifier Engine:** Mengimplementasikan formula standar TTRPG `(Score - 10) // 2` sebagai penambah angka lemparan dadu D20 vs DC (Difficulty Class 8–12), menyeimbangkan peluang *Success* agar pemain tidak sering *Fail* tanpa alasan logis.
2. **Proper Multi-Source EXP Progression:** Pemain mendapatkan EXP tidak hanya dari membunuh monster, tetapi juga dari keberhasilan *Skill Check* (+15 EXP) dan *Critical Success D20* (+25 EXP).
3. **Consumable Stacking System:** Item konsumsi (Rations, Potions, Torches, Bandages) kini otomatis menumpuk (*stacked*) dalam 1 slot tas (`qty: N`), menghemat ruang 40-slot backpack secara efisien.
4. **Dynamic Item Level (iLvl) & Real Rarity Scaling:** Setiap perlengkapan memiliki tingkatan Level (`item_level: N`) dan pengganda stat kelangkaan yang nyata (*Common 1.0x, Uncommon 1.3x, Rare 1.8x, Epic 2.5x, Legendary 3.6x*). Item *Rare* dipastikan memiliki atribut yang jauh lebih kuat dibanding *Common*.
5. **6-Slot Paper Doll & Weapon Handedness:** Mendukung slot Head, Body, Feet, Accessory, Main Hand, dan Off Hand dengan mekanik 1-Hand, Off-Hand Only (Shields/Grimoires), Versatile (Dual Wielding +15% ATK), dan Two-Handed Lock.
6. **100% Standalone Controller & Live AI Indicator:** Layar controller mandiri dengan pemilih 385 model AI, bilah status EXP, dan indikator proses AI real-time.

---

## 3. Versioning Records
- **v1.0.0:** Purwarupa statis Python state machine.
- **v1.2.0:** Integrasi Live Gemini 3.7 Flash Low & Web Audio Synthesizer.
- **v2.0.0:** Grandmaster Edition (8 Origins, 6-Slot Gear, Handedness, 40-Slot Bag).
- **v2.1.0:** Dual AI Engine (OX-Alpha + Gemini), AI Loading Indicator, & Desktop Balance UI.
- **v2.2.0 (Current):** Proper EXP & Stat Modifiers, Consumable Item Stacking, Real Rarity Stat Multipliers, and Equipment Item Levels.
