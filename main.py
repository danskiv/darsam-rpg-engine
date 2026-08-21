import asyncio
import json
import os
import random
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Darsam RPG Dungeon Engine - Grandmaster Edition")

os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/static", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/templates", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/saves", exist_ok=True)

app.mount("/static", StaticFiles(directory="/home/ubuntu/Github/darsam-rpg-engine/static"), name="static")
templates = Jinja2Templates(directory="/home/ubuntu/Github/darsam-rpg-engine/templates")

SAVE_FILE = "/home/ubuntu/Github/darsam-rpg-engine/saves/dungeon_save.json"

def get_9router_key() -> str:
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("NINE_ROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1].strip("\"'")
    return ""

NINE_ROUTER_KEY = get_9router_key()

# 4 Starting Origins (Ordinary Commoner to Legendary Hero)
CLASSES_INFO = {
    "peasant": {
        "title": "Hardy Peasant",
        "icon": "🌾",
        "desc": "Petani tangguh berotot liat. Bertahan hidup dengan stamina alamiah, ketabahan mental, dan insting tanah liat.",
        "base_hp": 110,
        "base_mp": 15,
        "str": 14,
        "dex": 10,
        "con": 14,
        "int": 8,
        "wis": 12,
        "starting_items": ["Rusty Hoe", "Harvest Sickle", "Dry Ration Bread", "Hemp Rope (15m)"],
        "passive": "Hardy Survivalist: Memulihkan +10 HP ekstra saat mengambil action Rest/Camp."
    },
    "blacksmith": {
        "title": "Smith Apprentice",
        "icon": "🔨",
        "desc": "Magang bengkel tempa desa. Lengan kokoh terbiasa memukul baja panas, paham titik lemah struktur logam & batu.",
        "base_hp": 120,
        "base_mp": 10,
        "str": 16,
        "dex": 9,
        "con": 13,
        "int": 9,
        "wis": 10,
        "starting_items": ["Heavy Smith Hammer", "Leather Apron", "Iron Spikes (x5)", "Grindstone"],
        "passive": "Heavy Impact: Attack menggunakan blunt weapons mendapat bonus +2 STR Modifier."
    },
    "scholar": {
        "title": "Village Scholar",
        "icon": "📜",
        "desc": "Asisten tabib dan pembaca naskah tua. Fisik ringkih namun cerdas mengurai ancient runes dan ramuan herbal.",
        "base_hp": 80,
        "base_mp": 55,
        "str": 7,
        "dex": 11,
        "con": 9,
        "int": 16,
        "wis": 14,
        "starting_items": ["Carving Knife", "Ancient Lore Diary", "Healing Herbal Salve (x2)", "Flint & Tinder"],
        "passive": "Arcane Insight: Mendapat bonus +3 INT Check saat membaca runes, glyphs, atau spell traps."
    },
    "trapper": {
        "title": "Forest Trapper",
        "icon": "🏹",
        "desc": "Pemburu satwa lereng bukit berkabut. Langkah hening tanpa jejak, awas jebakan, dan ahli membidik di kegelapan.",
        "base_hp": 90,
        "base_mp": 20,
        "str": 10,
        "dex": 16,
        "con": 11,
        "int": 10,
        "wis": 13,
        "starting_items": ["Crude Shortbow & 10 Arrows", "Skinning Dagger", "Wire Snare Trap", "Pine Resin Torch"],
        "passive": "Silent Stalker: Selalu mendapat Advantage (+2 DEX Check) saat Stealth atau Escape."
    }
}

DEFAULT_GAME_STATE = {
    "status": "character_creation",
    "floor": 1,
    "step": 0,
    "active_sound_theme": "creation", # creation | dungeon | danger | mystery | suspense
    "story_history": [],
    "player": {
        "name": "Danas",
        "class_id": "peasant",
        "class_name": "Hardy Peasant",
        "class_icon": "🌾",
        "hp": 110,
        "max_hp": 110,
        "mp": 15,
        "max_mp": 15,
        "gold": 5,
        "exp": 0,
        "level": 1,
        "stats": {"str": 14, "dex": 10, "con": 14, "int": 8, "wis": 12},
        "inventory": ["Rusty Hoe", "Harvest Sickle", "Dry Ration Bread", "Hemp Rope (15m)"]
    },
    "scene": {
        "chapter": "Chapter 1: The Descent",
        "title": "Collapse into the Forgotten Crypt",
        "location": "Underground Ruins - Floor 1",
        "narrative": "Paduka hanyalah seorang warga biasa yang mencari kayu bakar di lereng bukit berkabut. Tanpa peringatan, tanah di bawah kaki amblas runtuh seketika! Paduka terperosok ke dalam rongga makam kuno bawah tanah yang gelap, lembap, dan berbau belerang. Runtuhan batu besar telah menutup rapat jalan kembali ke atas. Di hadapan Paduka terbentang lorong batu purba yang memancarkan hawa dingin menusuk tulang.",
        "choices": [
            {"id": "A", "text": "Inspect the stone wall & search for weak structural points (Perception / WIS Check - DC 10)", "type": "roll", "dc": 10, "stat": "WIS"},
            {"id": "B", "text": "Use farming/smithing tools to clear heavy debris (Athletics / STR Check - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "C", "text": "Light a pine torch and stealthily navigate the corridor (Stealth / DEX Check - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Take a short rest, catch breath, and inspect inventory (Action)", "type": "action"}
        ],
        "log": ["A commoner's survival journey in the dark subterranean ruins begins..."]
    }
}

game_state = json.loads(json.dumps(DEFAULT_GAME_STATE))

def load_save():
    global game_state
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                saved = json.load(f)
                game_state.update(saved)
                print("Game state loaded from save file.")
        except Exception as e:
            print("Failed to load save:", e)

def save_game():
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(game_state, f, indent=2)
    except Exception as e:
        print("Failed to save game:", e)

load_save()

class ConnectionManager:
    def __init__(self):
        self.tv_sockets: List[WebSocket] = []
        self.controller_sockets: List[WebSocket] = []

    async def connect_tv(self, websocket: WebSocket):
        await websocket.accept()
        self.tv_sockets.append(websocket)

    async def disconnect_tv(self, websocket: WebSocket):
        if websocket in self.tv_sockets:
            self.tv_sockets.remove(websocket)

    async def connect_controller(self, websocket: WebSocket):
        await websocket.accept()
        self.controller_sockets.append(websocket)

    async def disconnect_controller(self, websocket: WebSocket):
        if websocket in self.controller_sockets:
            self.controller_sockets.remove(websocket)

    async def broadcast_to_tv(self, data: Dict[str, Any]):
        for socket in list(self.tv_sockets):
            try:
                await socket.send_json(data)
            except Exception:
                await self.disconnect_tv(socket)

    async def broadcast_to_controllers(self, data: Dict[str, Any]):
        for socket in list(self.controller_sockets):
            try:
                await socket.send_json(data)
            except Exception:
                await self.disconnect_controller(socket)

    async def broadcast_all(self, data: Dict[str, Any]):
        await self.broadcast_to_tv(data)
        await self.broadcast_to_controllers(data)

manager = ConnectionManager()

# GRANDMASTER AI DUNGEON MASTER PROMPT (GEMINI 3.7 FLASH LOW)
async def generate_infinite_story(player: Dict[str, Any], current_scene: Dict[str, Any], action_taken: str, roll_result: int, roll_status: str, history: List[str]) -> Dict[str, Any]:
    url = "http://127.0.0.1:20128/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NINE_ROUTER_KEY}"
    }

    system_prompt = """You are Dungeon Master Darsam — an elite, atmospheric, and responsive Grandmaster TTRPG storyteller running a dark fantasy solo campaign (Zero to Hero edition).

PHILOSOPHY & TONE:
- Tone: Gritty, visceral, atmospheric Dark Fantasy (inspired by Dark Souls, Ravenloft, and classic D&D).
- Core Premise: The protagonist is an ordinary commoner fighting for survival with rustic tools, makeshift grit, and wit, gradually unearthing ancient lore, artifacts, and combat prowess.
- Narrative Language: Indonesian with royal respect and immersive sensory descriptions (address player as 'Paduka').
- TECHNICAL & GAMEPLAY TERMS: MUST BE IN CLEAN STANDARD ENGLISH (e.g. 'STR Check', 'DEX Check', 'INT Check', 'WIS Check', 'CON Check', 'DC 12', 'Critical Hit', 'Critical Fail', 'Success', 'Fail', 'Sneak Attack', 'Perception Check', 'Arcana Check', 'Healing Salve', 'Short Rest').

STORYTELLING PRINCIPLES:
1. Show, Don't Tell: Describe sensory details (the smell of ozone, cold moisture dripping on stone, the metallic scrape of bone against iron).
2. Fail-Forward Mechanics: Failure NEVER stalls the story. A failed check creates complications, damage, loss of torches, or draws enemy attention while still moving the scene forward.
3. Meaningful Agency: Provide 4 distinct tactical choices (A, B, C, D) with varied mechanics (Physical, Stealth, Mental/Arcane, Item/Rest).
4. Audio Theme Control: Select the most fitting mood for the scene: 'dungeon' (exploration), 'danger' (combat/trap), 'mystery' (shrine/merchant/relic).
5. OUTPUT CONTRACT: Output ONLY valid, pure JSON without any markdown formatting or code blocks.

JSON SCHEMA:
{
  "chapter": "Chapter X: Title",
  "location": "Specific Underground Room / Chamber Name",
  "title": "Scene / Encounter Title",
  "outcome_summary": "1-2 concise Indonesian sentences explaining the immediate impact of the player's action (using English technical terms).",
  "narrative": "3-5 rich, immersive, atmospheric Indonesian sentences describing the evolving crisis and environment.",
  "audio_theme": "dungeon" | "danger" | "mystery",
  "hp_change": 0, // negative for damage (-5 to -25), positive for heal
  "mp_change": 0,
  "gold_change": 5, // coins found or looted
  "exp_change": 25,
  "choices": [
    {"id": "A", "text": "Action description (STR / Athletics Check - DC 12)", "type": "roll", "stat": "STR", "dc": 12},
    {"id": "B", "text": "Action description (DEX / Stealth Check - DC 11)", "type": "roll", "stat": "DEX", "dc": 11},
    {"id": "C", "text": "Action description (INT / Arcana Check - DC 10)", "type": "roll", "stat": "INT", "dc": 10},
    {"id": "D", "text": "Tactical action / Use item / Take Short Rest (Action)", "type": "action"}
  ]
}"""

    user_prompt = f"""PROTAGONIST PROFILE:
- Name: {player['name']}
- Origin / Class: {player['class_name']}
- Stats: STR {player['stats']['str']} | DEX {player['stats']['dex']} | CON {player['stats']['con']} | INT {player['stats']['int']} | WIS {player['stats']['wis']}
- Current Vitals: Level {player['level']} | HP: {player['hp']}/{player['max_hp']} | MP: {player['mp']}/{player['max_mp']} | Gold: {player['gold']} G
- Equipment: {', '.join(player.get('inventory', []))}

CURRENT SITUATION:
- Chapter & Location: {current_scene.get('chapter')} - {current_scene.get('location')}
- Encounter Title: {current_scene.get('title')}
- Previous Narrative: {current_scene.get('narrative')}

PLAYER ACTION TAKEN:
- Action: "{action_taken}"
- D20 Dice Roll: {roll_result} (Result: {roll_status})

CHRONICLE LOG:
{chr(10).join(history[-3:]) if history else "- Collapsed through the ground into the ancient ruins."}

Narrate the next chapter of this dark fantasy survival tale!"""

    payload = {
        "model": "ag/gemini-3.7-flash-low",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.78,
        "max_tokens": 1200
    }

    try:
        def _call_api():
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                raw = resp.read().decode("utf-8")
                full_content = ""
                for line in raw.split("\n"):
                    line = line.strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0].get("delta", {}).get("content", "")
                            full_content += delta
                        except Exception:
                            pass
                if not full_content:
                    try:
                        obj = json.loads(raw)
                        full_content = obj["choices"][0]["message"]["content"]
                    except Exception:
                        pass
                return full_content

        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, _call_api)
        
        clean_json = content.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()
        
        data = json.loads(clean_json)
        return data

    except Exception as e:
        print("LLM Generation Fallback triggered:", e)
        is_success = roll_result >= 10 if roll_result > 0 else True
        dmg = random.randint(8, 16) if not is_success else 0
        gold = random.randint(5, 12) if is_success else 0
        exp = 25 if is_success else 10
        return {
            "chapter": current_scene.get("chapter", "Chapter 1: The Dark Vault"),
            "location": "Subterranean Ruins - Floor 1",
            "title": "Echoing Stone Chambers",
            "outcome_summary": f"D20 Roll ({roll_result}): {'Aksi Paduka berhasil meretas rintangan!' if is_success else 'Paduka tergores bebatuan tajam dan menerima damage!'}",
            "narrative": "Tetesan air dingin menggema di lorong batu obsidian. Bau lumut purba menyelimuti udara. Di hadapan Paduka, sebuah pintu batu berukir lambang kerajaan kuno memancarkan pendar cahaya keemasan redup.",
            "audio_theme": "dungeon",
            "hp_change": -dmg,
            "mp_change": 0,
            "gold_change": gold,
            "exp_change": exp,
            "choices": [
                {"id": "A", "text": "Force open the reinforced stone gate (STR Check - DC 11)", "type": "roll", "stat": "STR", "dc": 11},
                {"id": "B", "text": "Examine the glowing lock mechanism (INT / Arcana Check - DC 10)", "type": "roll", "stat": "INT", "dc": 10},
                {"id": "C", "text": "Search for a concealed bypass passage (Perception / WIS Check - DC 9)", "type": "roll", "stat": "WIS", "dc": 9},
                {"id": "D", "text": "Consume dry rations & rest to restore Health (Action)", "type": "action"}
            ]
        }

def init_new_character(name: str, class_id: str):
    global game_state
    c = CLASSES_INFO.get(class_id, CLASSES_INFO["peasant"])
    game_state["status"] = "playing"
    game_state["floor"] = 1
    game_state["step"] = 0
    game_state["active_sound_theme"] = "dungeon"
    game_state["story_history"] = []
    game_state["player"] = {
        "name": name if name.strip() else "Danas",
        "class_id": class_id,
        "class_name": c["title"],
        "class_icon": c["icon"],
        "hp": c["base_hp"],
        "max_hp": c["base_hp"],
        "mp": c["base_mp"],
        "max_mp": c["base_mp"],
        "gold": 5,
        "exp": 0,
        "level": 1,
        "stats": {
            "str": c["str"],
            "dex": c["dex"],
            "con": c.get("con", 10),
            "int": c["int"],
            "wis": c["wis"]
        },
        "inventory": list(c["starting_items"])
    }
    game_state["scene"] = {
        "chapter": "Chapter 1: The Descent",
        "title": "Collapse into the Forgotten Crypt",
        "location": "Underground Ruins - Floor 1",
        "narrative": f"Sang {c['title']}, {game_state['player']['name']}, hanyalah warga biasa yang hidup sederhana di desa. Namun takdir berkata lain: saat sedang mencari kayu di bukit, tanah amblas runtuh seketika! Paduka terperosok ke dalam rongga makam kuno bawah tanah. Lubang keluar di atas tertutup reruntuhan tebal. Satu-satunya jalan bertahan hidup adalah menembus lorong batu berlumut yang dingin dan gelap di depan mata.",
        "choices": [
            {"id": "A", "text": "Examine the ancient wall runes to find an exit path (WIS / Perception Check - DC 10)", "type": "roll", "dc": 10, "stat": "WIS"},
            {"id": "B", "text": "Use farming/smithing tools to clear heavy debris (STR / Athletics Check - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "C", "text": "Light a torch and stealthily navigate the corridor (DEX / Stealth Check - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Take a short rest, catch breath, and inspect inventory (Action)", "type": "action"}
        ],
        "log": [f"Commoner '{game_state['player']['name']}' ({c['title']}) begins the underground survival journey!"]
    }
    save_game()

async def process_live_turn(choice_id: str, choice_text: str = "", custom_text: str = "", roll_val: int = 0) -> Dict[str, Any]:
    global game_state
    p = game_state["player"]
    scene = game_state["scene"]
    game_state["step"] = game_state.get("step", 0) + 1
    
    action_description = custom_text if custom_text else choice_text
    roll_status = "Direct Action"
    if roll_val > 0:
        if roll_val >= 20:
            roll_status = "CRITICAL SUCCESS"
        elif roll_val == 1:
            roll_status = "CRITICAL FAIL"
        elif roll_val >= 10:
            roll_status = "SUCCESS"
        else:
            roll_status = "FAIL"

    # Call Gemini 3.7 Flash Low AI Story Engine
    ai_response = await generate_infinite_story(
        player=p,
        current_scene=scene,
        action_taken=action_description,
        roll_result=roll_val,
        roll_status=roll_status,
        history=game_state.get("story_history", [])
    )

    # Apply Stats Changes
    hp_diff = ai_response.get("hp_change", 0)
    p["hp"] = max(0, min(p["max_hp"], p["hp"] + hp_diff))
    p["mp"] = max(0, min(p["max_mp"], p["mp"] + ai_response.get("mp_change", 0)))
    p["gold"] = max(0, p["gold"] + ai_response.get("gold_change", 0))
    p["exp"] = p["exp"] + max(0, ai_response.get("exp_change", 20))
    game_state["active_sound_theme"] = ai_response.get("audio_theme", "dungeon")

    outcome = f"🎲 [{roll_status}] {ai_response.get('outcome_summary', '')}"
    if hp_diff < 0:
        outcome += f" (-{-hp_diff} HP)"
    elif hp_diff > 0:
        outcome += f" (+{hp_diff} HP)"
    if ai_response.get("gold_change", 0) > 0:
        outcome += f" (+{ai_response['gold_change']} Gold)"

    # Level Up Check (Zero to Hero Progression)
    if p["exp"] >= 80 * p["level"]:
        p["level"] += 1
        p["max_hp"] += 20
        p["hp"] = p["max_hp"]
        p["max_mp"] += 10
        p["mp"] = p["max_mp"]
        outcome += f" 🌟 LEVEL UP! Paduka naik ke Level {p['level']}! Stats & Survival Prowess meningkat!"

    # Append History
    game_state.setdefault("story_history", []).append(f"Aksi: {action_description} -> {ai_response.get('outcome_summary')}")
    if len(game_state["story_history"]) > 8:
        game_state["story_history"].pop(0)

    # Update Scene State
    game_state["scene"]["chapter"] = ai_response.get("chapter", scene.get("chapter"))
    game_state["scene"]["title"] = ai_response.get("title", "Dungeon Chamber")
    game_state["scene"]["location"] = ai_response.get("location", scene.get("location"))
    game_state["scene"]["narrative"] = ai_response.get("narrative", "Suasana gua semakin mencekam...")
    game_state["scene"]["choices"] = ai_response.get("choices", scene.get("choices"))
    game_state["scene"]["log"].append(outcome)
    if len(game_state["scene"]["log"]) > 5:
        game_state["scene"]["log"].pop(0)

    save_game()

    return {
        "type": "state_update",
        "outcome": outcome,
        "state": game_state
    }

@app.get("/tv", response_class=HTMLResponse)
async def tv_page(request: Request):
    return templates.TemplateResponse(request=request, name="tv.html", context={"state": game_state, "classes": CLASSES_INFO})

@app.get("/controller", response_class=HTMLResponse)
async def controller_page(request: Request):
    return templates.TemplateResponse(request=request, name="controller.html", context={"state": game_state, "classes": CLASSES_INFO})

@app.get("/api/state")
async def get_state():
    return game_state

@app.get("/api/classes")
async def get_classes():
    return CLASSES_INFO

@app.websocket("/ws/tv")
async def ws_tv(websocket: WebSocket):
    await manager.connect_tv(websocket)
    try:
        await websocket.send_json({"type": "init", "state": game_state, "classes": CLASSES_INFO})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_tv(websocket)

@app.websocket("/ws/controller")
async def ws_controller(websocket: WebSocket):
    await manager.connect_controller(websocket)
    try:
        await websocket.send_json({"type": "init", "state": game_state, "classes": CLASSES_INFO})
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            action_type = data.get("type")

            if action_type == "create_character":
                char_name = data.get("name", "Danas")
                class_id = data.get("class_id", "peasant")
                init_new_character(char_name, class_id)
                await manager.broadcast_all({
                    "type": "state_update",
                    "state": game_state,
                    "outcome": f"Karakter {game_state['player']['name']} telah siap memulai petualangan!"
                })

            elif action_type == "select_choice":
                choice = data.get("choice", {})
                is_roll = choice.get("type") == "roll"
                choice_text = choice.get("text", "")
                
                if is_roll:
                    roll_result = random.randint(1, 20)
                    await manager.broadcast_all({
                        "type": "dice_rolling",
                        "choice_text": choice_text,
                        "stat": choice.get("stat", "D20")
                    })
                    await asyncio.sleep(2.5)
                    await manager.broadcast_all({
                        "type": "dice_result",
                        "value": roll_result
                    })
                    await asyncio.sleep(1.0)
                    update_data = await process_live_turn(choice.get("id"), choice_text=choice_text, roll_val=roll_result)
                    await manager.broadcast_all(update_data)
                else:
                    update_data = await process_live_turn(choice.get("id"), choice_text=choice_text)
                    await manager.broadcast_all(update_data)

            elif action_type == "custom_action":
                custom_text = data.get("text", "")
                roll_result = random.randint(1, 20)
                await manager.broadcast_all({
                    "type": "dice_rolling",
                    "choice_text": f"Custom Action: {custom_text}",
                    "stat": "D20"
                })
                await asyncio.sleep(2.5)
                await manager.broadcast_all({
                    "type": "dice_result",
                    "value": roll_result
                })
                await asyncio.sleep(1.0)
                update_data = await process_live_turn("CUSTOM", custom_text=custom_text, roll_val=roll_result)
                await manager.broadcast_all(update_data)

            elif action_type == "reset_game":
                game_state.clear()
                game_state.update(json.loads(json.dumps(DEFAULT_GAME_STATE)))
                game_state["status"] = "character_creation"
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Game di-reset ke Ruang Asal-Usul Karakter."})

    except WebSocketDisconnect:
        await manager.disconnect_controller(websocket)
