# PRD: Darsam RPG Engine (Dark Fantasy D&D Edition)

## 1. Overview
Sebuah game Interactive RPG Dungeon Master berbasis Web & WebSocket yang dirancang khusus untuk dimainkan secara multi-screen:
- **Display Screen (TV):** `http://10.10.10.1:8090/tv` (Layar 16:9, Dark Fantasy aesthetic, Story Narrative, Stats, Live D20 Roll Animation, Visual Scene Card, Sound Atmosphere).
- **Controller Screen (HP):** `http://10.10.10.1:8090/controller` (Mobile Touchscreen, Choice Cards A/B/C/D, Free Text Action, Roll D20 Button).

## 2. Technical Stack
- **Backend:** FastAPI (Python 3.12/asyncio) + WebSocket Room Hub.
- **Frontend TV:** HTML5 + Tailwind CSS + Vanilla JS (Web Audio API sound synthesizers, D20 3D/CSS Dice Roller, Typewriter effect).
- **Frontend HP:** HTML5 + Tailwind CSS + Mobile Haptic Feedback (Vibration API) + WebSocket Controller.
- **Port:** `8090` (Private WireGuard only: `10.10.10.1`).
- **AI Narrative Engine:** Integrated Procedural + LLM Game Master for dynamic dungeon generation.

## 3. Game Mechanics
- **Player Stats:**
  - HP (Health Points): 100
  - MP (Mana Points): 50
  - Gold: 20
  - Level: 1 | Class: Knight / Sorcerer / Rogue
- **Action Loop:**
  1. Game Master (Darsam) menjabarkan skenario & suasana ruangan.
  2. TV merender teks, visual mood, dan pilihan aksi.
  3. HP menerima kartu pilihan aksi (A, B, C, D) atau kolom Custom Action.
  4. Pemain memilih aksi di HP.
  5. Jika aksi butuh tantangan, TV & HP memicu animasi lemparan Dadu D20 (Critical Fail 1, Normal 2-19, Critical Success 20).
  6. AI Game Master memproses hasil lemparan dan melanjutkan jalan cerita.
