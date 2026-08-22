# Darsam RPG Dungeon Engine - PRD v2.1.0 (Grandmaster Ultimate Edition)

## 1. Executive Summary
**Darsam RPG Dungeon Engine** adalah platform game solo interactive Tabletop RPG (TTRPG) bergaya *Dark Fantasy* berbasis arsitektur **Dual-Screen (TV Companion Display & Standalone Mobile/Desktop Controller)**.
Game ini ditenagai oleh perpaduan **OpenRouter/Stealth/OX-Alpha (Primary Reasoning LLM)** dan **Gemini 3.7 Flash Low (Speed Fallback)** melalui gateway 9Router di VPS Oracle Cloud untuk menciptakan narasi tanpa batas (*Infinite Emergent Narrative*), dipadukan dengan mekanik RPG berstandar internasional (*Old School Renaissance / OSR, Diablo ARPG loot tables, and Path of Exile itemization*).

---

## 2. Core Pillars of Version 2.1.0
1. **100% Standalone Controller:** Controller di HP atau Laptop dapat mengakses seluruh fitur game (Story, Combat, Active Skills, 6-Slot Gear, 40-Slot Backpack, Shop/Barter, Dice, & Awakening) secara independen tanpa bergantung ke TV.
2. **Atmospheric TV Companion Display:** Layar TV 32" bertindak sebagai papan visual taktis (Vitals, 6 Core Stats, 40-Slot Grid Matrix, Paper Doll, D20 Chamber, Monster Card, & Rarity Aura Glow).
3. **8 Base Origins to Secret Awakening:** Pemain memulai dari 8 latar belakang warga biasa (Zero to Hero) dan berpeluang memicu pergantian kelas rahasia bertingkat kelangkaan (**Special ➔ Epic ➔ Legendary ➔ Mythic**) secara dinamis lewat event langka.
4. **Dynamic Item Level (iLvl) & Scaled Consumables:** Perlengkapan dan item konsumsi (Tier 1–5) di toko dan drop monster secara otomatis menyesuaikan dengan level pemain.
5. **6-Slot Paper Doll & Weapon Handedness:** Mendukung slot Head, Body, Feet, Accessory, Main Hand, dan Off Hand dengan mekanik 1-Hand, Off-Hand Only (Shields/Grimoires/Quivers), Versatile (Dual Wielding), dan 2-Handed (Greatsword/Bow yang mengunci slot kedua).
6. **Skill Loadout Deck (3 Active Slots):** Pengelolaan jurus melalui Grimoire (buku jurus terbuka tiap 5 level & drop tomes), di mana 3 jurus aktif dapat dieksekusi langsung saat pertarungan di tab Cerita.
7. **Living Crypt Economy:** Sistem toko pedagang acak (Scavenger, Black Market, Blood Merchant, Relic Gambler, Blacksmith) dengan tawar-menawar (*Haggling via CHA Check*) dan jasa tempa senjata (+1 s/d +5).
8. **Mathematical Combat Synchronization:** Status musuh terikat secara matematis murni pada `HP <= 0` (mencegah kekalahan prematur atau status hantu).
9. **Live AI Loading Indicator:** Notifikasi visual mengambang di controller saat AI sedang memproses babak cerita berikutnya.
10. **Desktop & Mobile Balanced Layout:** Antarmuka responsif penuh (*Zero Dead Space, Flex-Grow Narrative Panel, Large Font*).

---

## 3. System Architecture & Endpoints
```
[Mobile / Laptop Browser] ◄──(WebSocket / REST)──► [FastAPI Backend] ──(9Router)──► [OX-Alpha / Gemini 3.7 Flash]
(Controller: Port 8090)                               (VPS NODIX1)
                                                           │
                                                   (WebSocket State)
                                                           ▼
                                                [Android TV Browser / App]
                                                    (TV: Port 8090/tv)
```
- **TV Display:** `http://10.10.10.1:8090/tv` (WebSocket: `ws://10.10.10.1:8090/ws/tv`)
- **Controller:** `http://10.10.10.1:8090/controller` (WebSocket: `ws://10.10.10.1:8090/ws/controller`)
- **State API:** `http://10.10.10.1:8090/api/state`
- **Classes API:** `http://10.10.10.1:8090/api/classes`

---

## 4. Versioning & Milestone Records
- **v1.0.0:** Purwarupa statis Python state machine dengan 4 job dasar dan tampilan web sederhana.
- **v1.2.0:** Integrasi Live Gemini 3.7 Flash Low, Web Audio Procedural Synthesizer, dan Dadu D20 animasi.
- **v2.0.0:** Grandmaster Edition (8 Origins, Secret Awakening RNG, 6-Slot Paper Doll, Handedness, 40-Slot Bag, iLvl Scaling, Living Shop, Tabbed Controller).
- **v2.1.0 (Current):** Dual AI Engine (OX-Alpha Primary + Gemini 3.7 Fallback), AI Loading Indicator, Mathematical Combat Lock (`HP <= 0`), and Perfect Desktop/Mobile Balanced UI.
