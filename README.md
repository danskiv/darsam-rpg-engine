# ⚔️ Darsam RPG Dungeon Engine

[![Version](https://img.shields.io/badge/version-2.3.0-gold.svg)](PRD.md)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An interactive, dark fantasy solo **Tabletop RPG (TTRPG) engine** powered by modern Large Language Models (**OX-Alpha & Gemini 3.7 Flash**) designed with a **Dual-Screen Architecture**: an atmospheric **16:9 TV Companion Board** and a **100% Standalone Mobile/Desktop Controller**.

---

## 🌟 Key Features

* **Dual-Screen Experience:** Play with an Android TV display (`/tv`) as your tactical battle board and ambient music station, while controlling story, combat, inventory, and skills directly from your phone/laptop browser (`/controller`).
* **Infinite Emergent Storytelling:** Narrative and room encounters generated dynamically via **OX-Alpha** (Reasoning Master) with instant fallback to **Gemini 3.7 Flash Low**, supporting a live roster of 385 AI models.
* **8 Starting Origins (Zero to Hero):** Begin as a commoner (*Hardy Peasant, Smith Apprentice, Village Scholar, Forest Trapper, Disgraced Watchman, Tomb Grave-Robber, Temple Acolyte, Alchemist Apprentice*).
* **Secret Job Awakening (RNG Dynamic Trigger):** Encounter rare subterranean events to transcend into *Special*, *Epic*, *Legendary*, or *Mythic* classes (*Dragon-Heart Sovereign, Void Archon, Omniscient Sovereign of Creation*).
* **6-Slot Paper Doll & Weapon Handedness:** Equip Head, Body Armor, Feet, Accessory, Main-Hand, and Off-Hand gear. Features Two-Handed weapons (locking off-hand) and Versatile weapons (activating Dual Wield Stance).
* **40-Slot Backpack & Auto-Sorting:** Inventory automatically categorizes equipment on top (ranked by Item Level and Rarity DESC) and stackable consumables below.
* **Procedural Web Audio Synthesizer:** Zero-bandwidth procedural music and atmospheric soundscapes synthesized directly in the TV browser using the Web Audio API.

---

## 🚀 Quick Start

### 1. Requirements
* Python 3.11+
* 9Router Gateway or OpenAI-compatible LLM endpoint

### 2. Installation
```bash
git clone https://github.com/danskiv/darsam-rpg-engine.git
cd darsam-rpg-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn websockets jinja2
```

### 3. Running the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8090
```

* **TV Display:** Open `http://<YOUR_IP>:8090/tv` on your Android TV browser or Leanback WebView.
* **Mobile / Desktop Controller:** Open `http://<YOUR_IP>:8090/controller` on your smartphone or laptop.

---

## 📖 Documentation
* [PRD.md](PRD.md) — Product Requirements Document & full specifications.
* [docs/GAME_SYSTEMS.md](docs/GAME_SYSTEMS.md) — Detailed mathematical formulas for combat, stats, EXP curves, loot drop scaling, and handedness rules.
* [CHANGELOG.md](CHANGELOG.md) — Full release history from v1.0.0 to v2.3.0.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
