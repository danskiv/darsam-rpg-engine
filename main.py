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

app = FastAPI(title="Darsam RPG Dungeon Engine - Infinite AI Edition")

os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/static", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/templates", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/saves", exist_ok=True)

app.mount("/static", StaticFiles(directory="/home/ubuntu/Github/darsam-rpg-engine/static"), name="static")
templates = Jinja2Templates(directory="/home/ubuntu/Github/darsam-rpg-engine/templates")

SAVE_FILE = "/home/ubuntu/Github/darsam-rpg-engine/saves/dungeon_save.json"

# Load 9Router API Key
def get_9router_key() -> str:
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("NINE_ROUTER_API_KEY="):
                    return line.strip().split("=", 1)[1].strip("\"'")
    return ""

NINE_ROUTER_KEY = get_9router_key()

CLASSES_INFO = {
    "paladin": {
        "title": "Ksatria Suci (Holy Paladin)",
        "icon": "🛡️",
        "desc": "Ahli pedang berbaju zirah tebal dengan kemampuan mukjizat penyembuhan suci.",
        "base_hp": 130,
        "base_mp": 35,
        "str": 16,
        "dex": 10,
        "int": 10,
        "wis": 14,
        "starting_items": ["Pedang Panjang Baja", "Perisai Lambang Garuda", "Elixir Suci (x2)", "Lambang Iman Kuno"],
        "passive": "Baju zirah suci mengurangi 3 kerusakan dari serangan musuh."
    },
    "sorcerer": {
        "title": "Penyihir Bayangan (Shadow Sorcerer)",
        "icon": "🔮",
        "desc": "Penguasa mantra elemen petir dan kehampaan. Rapuh dalam benturan fisik namun mematikan dari kejauhan.",
        "base_hp": 75,
        "base_mp": 100,
        "str": 8,
        "dex": 14,
        "int": 18,
        "wis": 12,
        "starting_items": ["Tongkat Kristal Obsidian", "Gulungan Mantra Petir", "Ramuan Pemulih Mana (x3)", "Batu Api Kosmik"],
        "passive": "Mendapat bonus +3 saat melakukan Uji Sihir (INT)."
    },
    "rogue": {
        "title": "Pendekar Bayangan (Shadow Assassin)",
        "icon": "🗡️",
        "desc": "Bergerak tanpa jejak dalam kegelapan, ahli membobol kunci perangkap dan serangan mematikan dari belakang.",
        "base_hp": 90,
        "base_mp": 45,
        "str": 10,
        "dex": 18,
        "int": 12,
        "wis": 10,
        "starting_items": ["Sepasang Belati Berbisa", "Kumpulan Kunci Pembobol (Lockpick)", "Bom Asap Gelap (x2)", "Jubah Samaran"],
        "passive": "Peluang Critical Hit D20 berlaku pada angka 19 dan 20."
    },
    "berserker": {
        "title": "Pendekar Tempur (Raging Berserker)",
        "icon": "🪓",
        "desc": "Pejuang buas dengan kapak raksasa yang semakin ganas dan kuat ketika darahnya bercucuran.",
        "base_hp": 140,
        "base_mp": 20,
        "str": 18,
        "dex": 12,
        "int": 7,
        "wis": 9,
        "starting_items": ["Kapak Ganda Algojo", "Cincin Darah Liar", "Daging Kering Keras", "Obor Kayu"],
        "passive": "Jika HP di bawah 40%, semua lemparan serangan (STR) mendapat tambahan +4."
    }
}

DEFAULT_GAME_STATE = {
    "status": "character_creation",
    "floor": 1,
    "step": 0,
    "story_history": [],
    "player": {
        "name": "Danas",
        "class_id": "paladin",
        "class_name": "Ksatria Suci (Holy Paladin)",
        "class_icon": "🛡️",
        "hp": 130,
        "max_hp": 130,
        "mp": 35,
        "max_mp": 35,
        "gold": 30,
        "exp": 0,
        "level": 1,
        "stats": {"str": 16, "dex": 10, "int": 10, "wis": 14},
        "inventory": ["Pedang Panjang Baja", "Perisai Lambang Garuda", "Elixir Suci (x2)"]
    },
    "scene": {
        "chapter": "Bab 1: Pintu Masuk Makam Kuno",
        "title": "Gerbang Besi Berkepala Naga",
        "location": "Kedalaman Bawah Tanah Oakhaven",
        "narrative": "Kabut pekat beraroma belerang menyelimuti tangga batu yang runtuh. Di hadapan Paduka, berdiri sebuah gerbang besi berkepala naga bermata safir yang memancarkan hawa sedingin es. Rantai segel kuno bergetar seolah menyambut kedatangan darah baru.",
        "choices": [
            {"id": "A", "text": "Hunus senjata dan dobrak gerbang dengan tenaga penuh (Uji STR - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "B", "text": "Sentuh mata safir dan selaraskan energi gaib pembuka segel (Uji INT - DC 11)", "type": "roll", "dc": 11, "stat": "INT"},
            {"id": "C", "text": "Periksa lantai obsidian untuk melucuti kawat pemicu jebakan (Uji DEX - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Buka tas perbekalan, siapkan ramuan dan atur pernapasan", "type": "action"}
        ],
        "log": ["Petualangan agung tak terbatas bersama AI Dungeon Master dimulai..."]
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

# ASYNC LLM DUNGEON MASTER CALLER (GEMINI 3.7 FLASH LOW)
async def generate_infinite_story(player: Dict[str, Any], current_scene: Dict[str, Any], action_taken: str, roll_result: int, roll_status: str, history: List[str]) -> Dict[str, Any]:
    url = "http://127.0.0.1:20128/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NINE_ROUTER_KEY}"
    }

    system_prompt = """Kamu adalah Dungeon Master (DM) Darsam legendaris untuk game RPG Tabletop Dark Fantasy berlatar dungeon kastil kuno, kutukan, monster purba, sihir terlarang, intrik mistis, dan bahaya mematikan.
Kamu bertugas melanjutkan alur cerita yang SANGAT NYAMBUNG, KOHEKTIF, DRAMATIS, DAN PENUH KETEGANGAN berdasarkan keputusan pemain dan hasil lemparan dadu D20.

ATURAN PENTING:
1. Cerita harus logis, berbobot (high dark fantasy lore), dan konsekuensi aksi harus terasa nyata (apakah berhasil, gagal luka, atau mendapat harta/kunci rahasia).
2. Sediakan 4 pilihan tindakan baru (A, B, C, D) yang kreatif dan beragam (ada Uji STR, DEX, INT, WIS, CON, atau Aksi Taktis/Item).
3. Selalu sertakan perkiraan kerusakan (damage 0-30 jika gagal) atau hadiah (gold 10-50, exp 20-80) yang rasional.
4. Format output WAJIB HANYA JSON murni (valid JSON) tanpa awalan atau akhiran markdown triple backticks.

SCHEMA JSON OUTPUT:
{
  "chapter": "Bab X: Judul Babak",
  "location": "Nama Tempat / Ruangan",
  "title": "Nama Adegan / Pertemuan Spesifik",
  "outcome_summary": "1-2 kalimat ringkas hasil aksi langsung sang pemain (misal: Tebasan pedang Paduka membelah zirah kerangka!)",
  "narrative": "Paragraf deskripsi narasi kelanjutan situasi ruangan/tantangan baru berikutnya (3-5 kalimat atmosferik yang imersif).",
  "hp_change": 0, // negatif jika terluka, positif jika sembuh
  "mp_change": 0, // negatif jika pakai sihir, positif jika pulih
  "gold_change": 15, // bonus koin yang ditemukan
  "exp_change": 35, // pengalaman yang didapat
  "choices": [
    {"id": "A", "text": "Deskripsi tindakan A (Uji STR - DC 12)", "type": "roll", "stat": "STR", "dc": 12},
    {"id": "B", "text": "Deskripsi tindakan B (Uji INT - DC 11)", "type": "roll", "stat": "INT", "dc": 11},
    {"id": "C", "text": "Deskripsi tindakan C (Uji DEX - DC 13)", "type": "roll", "stat": "DEX", "dc": 13},
    {"id": "D", "text": "Deskripsi tindakan bertahan / gunakan item", "type": "action"}
  ]
}"""

    user_prompt = f"""PROFIL KARAKTER:
- Nama: {player['name']}
- Kelas: {player['class_name']}
- Level: {player['level']} | HP: {player['hp']}/{player['max_hp']} | MP: {player['mp']}/{player['max_mp']} | Gold: {player['gold']} G
- Item: {', '.join(player.get('inventory', []))}

SITUASI SEBELUMNYA:
- Bab/Lokasi: {current_scene.get('chapter')} - {current_scene.get('location')}
- Judul Adegan: {current_scene.get('title')}
- Narasi Lalu: {current_scene.get('narrative')}

AKSI YANG DILAKUKAN PEMAIN:
- Tindakan: "{action_taken}"
- Hasil Dadu D20: {roll_result} (Status: {roll_status})

RIWAYAT PERJALANAN TERAKHIR:
{chr(10).join(history[-3:]) if history else "- Petualangan baru dimulai."}

Tolong ciptakan kelanjutan cerita yang dramatis, saling menyambung, dan berikan 4 pilihan tindakan baru!"""

    payload = {
        "model": "ag/gemini-3.7-flash-low",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.8,
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
                # Parse SSE chunks or regular JSON
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
        
        # Clean markdown codeblocks if any
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
        # Robust Procedural Fallback
        is_success = roll_result >= 10 if roll_result > 0 else True
        dmg = random.randint(10, 20) if not is_success else 0
        gold = random.randint(10, 25) if is_success else 0
        exp = 30 if is_success else 10
        return {
            "chapter": current_scene.get("chapter", "Bab Petualangan"),
            "location": "Kedalaman Lorong Bawah Makam",
            "title": "Lorong Misteri yang Bergema",
            "outcome_summary": f"Takdir Dadu ({roll_result}): Aksi Paduka {'berhasil meretas bahaya!' if is_success else 'memicu hambatan dan luka!'}",
            "narrative": "Langkah kaki Paduka bergema di lantai batu basah. Cahaya obor menari di dinding yang dipenuhi relief pertempuran para raja kuno. Dari kejauhan, tercium aroma dupa magis dan terdengar suara tetesan air mistis.",
            "hp_change": -dmg,
            "mp_change": 0,
            "gold_change": gold,
            "exp_change": exp,
            "choices": [
                {"id": "A", "text": "Maju dengan senjata terhunus siap bertempur (Uji STR - DC 12)", "type": "roll", "stat": "STR", "dc": 12},
                {"id": "B", "text": "Raba dinding mencari sakelar pintu rahasia (Uji DEX - DC 11)", "type": "roll", "stat": "DEX", "dc": 11},
                {"id": "C", "text": "Pindai keberadaan aura sihir di sekitar (Uji INT - DC 10)", "type": "roll", "stat": "INT", "dc": 10},
                {"id": "D", "text": "Istirahat sejenak dan teguk ramuan pemulih", "type": "action"}
            ]
        }

def init_new_character(name: str, class_id: str):
    global game_state
    c = CLASSES_INFO.get(class_id, CLASSES_INFO["paladin"])
    game_state["status"] = "playing"
    game_state["floor"] = 1
    game_state["step"] = 0
    game_state["story_history"] = []
    game_state["player"] = {
        "name": name if name.strip() else "Danas the Champion",
        "class_id": class_id,
        "class_name": c["title"],
        "class_icon": c["icon"],
        "hp": c["base_hp"],
        "max_hp": c["base_hp"],
        "mp": c["base_mp"],
        "max_mp": c["base_mp"],
        "gold": 30,
        "exp": 0,
        "level": 1,
        "stats": {
            "str": c["str"],
            "dex": c["dex"],
            "int": c["int"],
            "wis": c["wis"]
        },
        "inventory": list(c["starting_items"])
    }
    game_state["scene"] = {
        "chapter": "Bab 1: Gerbang Kehancuran",
        "title": "Pintu Gerbang Besi Berkepala Naga",
        "location": "Makam Kuno Oakhaven - Lantai 1",
        "narrative": f"Sang {c['title']}, {game_state['player']['name']}, melangkah menuruni tangga batu berlumut. Di hadapan Paduka, berdiri sebuah gerbang besi berkepala naga bermata safir yang memancarkan hawa sedingin es. Rantai segel kuno bergetar seolah menyambut kedatangan darah baru.",
        "choices": [
            {"id": "A", "text": "Hunus senjata dan dobrak gerbang dengan tenaga penuh (Uji STR - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "B", "text": "Sentuh mata safir dan selaraskan energi gaib pembuka segel (Uji INT - DC 11)", "type": "roll", "dc": 11, "stat": "INT"},
            {"id": "C", "text": "Periksa lantai obsidian untuk melucuti kawat pemicu jebakan (Uji DEX - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Buka tas perbekalan, siapkan ramuan dan atur pernapasan", "type": "action"}
        ],
        "log": [f"Karakter baru '{game_state['player']['name']}' ({c['title']}) telah bangkit!"]
    }
    save_game()

async def process_live_turn(choice_id: str, choice_text: str = "", custom_text: str = "", roll_val: int = 0) -> Dict[str, Any]:
    global game_state
    p = game_state["player"]
    scene = game_state["scene"]
    game_state["step"] = game_state.get("step", 0) + 1
    
    action_description = custom_text if custom_text else choice_text
    roll_status = "Biasa / Tanpa Dadu"
    if roll_val > 0:
        if roll_val == 20 or (roll_val >= 19 and p.get("class_id") == "rogue"):
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
    if hp_diff < 0 and p.get("class_id") == "paladin":
        hp_diff = min(0, hp_diff + 3) # Paladin passive armor
    
    p["hp"] = max(0, min(p["max_hp"], p["hp"] + hp_diff))
    p["mp"] = max(0, min(p["max_mp"], p["mp"] + ai_response.get("mp_change", 0)))
    p["gold"] = max(0, p["gold"] + ai_response.get("gold_change", 0))
    p["exp"] = p["exp"] + max(0, ai_response.get("exp_change", 20))

    outcome = f"🎲 [{roll_status}] {ai_response.get('outcome_summary', '')}"
    if hp_diff < 0:
        outcome += f" (-{-hp_diff} HP)"
    elif hp_diff > 0:
        outcome += f" (+{hp_diff} HP)"
    if ai_response.get("gold_change", 0) > 0:
        outcome += f" (+{ai_response['gold_change']} Gold)"

    # Level Up Check
    if p["exp"] >= 100 * p["level"]:
        p["level"] += 1
        p["max_hp"] += 25
        p["hp"] = p["max_hp"]
        p["max_mp"] += 15
        p["mp"] = p["max_mp"]
        outcome += f" 🌟 LEVEL UP! Paduka mencapai Level {p['level']}!"

    # Append History
    game_state.setdefault("story_history", []).append(f"Aksi: {action_description} -> {ai_response.get('outcome_summary')}")
    if len(game_state["story_history"]) > 8:
        game_state["story_history"].pop(0)

    # Update Scene State
    game_state["scene"]["chapter"] = ai_response.get("chapter", scene.get("chapter"))
    game_state["scene"]["title"] = ai_response.get("title", "Ruangan Misteri")
    game_state["scene"]["location"] = ai_response.get("location", scene.get("location"))
    game_state["scene"]["narrative"] = ai_response.get("narrative", "Kabut dungeon semakin tebal...")
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
                class_id = data.get("class_id", "paladin")
                init_new_character(char_name, class_id)
                await manager.broadcast_all({
                    "type": "state_update",
                    "state": game_state,
                    "outcome": f"Karakter {game_state['player']['name']} telah siap bertualang!"
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
                    "choice_text": f"Aksi Bebas: {custom_text}",
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
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Game telah di-reset ke Ruang Penciptaan Karakter."})

    except WebSocketDisconnect:
        await manager.disconnect_controller(websocket)
