import asyncio
import json
import os
import random
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Darsam RPG Dungeon Engine - Advanced Edition")

os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/static", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/templates", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/saves", exist_ok=True)

app.mount("/static", StaticFiles(directory="/home/ubuntu/Github/darsam-rpg-engine/static"), name="static")
templates = Jinja2Templates(directory="/home/ubuntu/Github/darsam-rpg-engine/templates")

SAVE_FILE = "/home/ubuntu/Github/darsam-rpg-engine/saves/dungeon_save.json"

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
    "status": "character_creation", # "character_creation" | "playing" | "game_over"
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
        "chapter": "Bab 1: Reruntuhan yang Menjerit",
        "title": "Pintu Gerbang Besi Berkepala Naga",
        "location": "Makam Kuno Oakhaven - Lantai 1",
        "narrative": "Kabut pekat beraroma belerang dan lumut basah menyelimuti tangga batu yang runtuh. Di hadapan Paduka, berdiri sebuah gerbang besi berkepala naga bermata safir yang memancarkan aura dingin mencekam. Dari dalam kegelapan lorong di balik pintu, terdengar suara geraman rendah dan bunyi logam bergesekan.",
        "choices": [
            {"id": "A", "text": "Hunus senjata dan dobrak gerbang dengan tenaga penuh (Uji STR - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "B", "text": "Sentuh mata safir dan selaraskan energi gaib pembuka segel (Uji INT - DC 11)", "type": "roll", "dc": 11, "stat": "INT"},
            {"id": "C", "text": "Periksa lantai obsidian untuk melucuti kawat pemicu jebakan (Uji DEX - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Buka tas perbekalan, siapkan ramuan dan atur pernapasan", "type": "action"}
        ],
        "log": ["Ksatria telah memasuki Makam Kuno Oakhaven. Petualangan dimulai..."]
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

def init_new_character(name: str, class_id: str):
    global game_state
    c = CLASSES_INFO.get(class_id, CLASSES_INFO["paladin"])
    game_state["status"] = "playing"
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
        "chapter": "Bab 1: Reruntuhan yang Menjerit",
        "title": "Pintu Gerbang Besi Berkepala Naga",
        "location": "Makam Kuno Oakhaven - Lantai 1",
        "narrative": f"Sang {c['title']}, {game_state['player']['name']}, melangkah menuruni tangga batu berlumut. Di hadapan Paduka, berdiri sebuah gerbang besi berkepala naga bermata safir yang memancarkan hawa sedingin es. Rantai segel kuno bergetar seolah menyambut kedatangan darah baru.",
        "choices": [
            {"id": "A", "text": "Hunus senjata dan dobrak gerbang dengan tenaga penuh (Uji STR - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "B", "text": "Sentuh mata safir dan selaraskan energi gaib pembuka segel (Uji INT - DC 11)", "type": "roll", "dc": 11, "stat": "INT"},
            {"id": "C", "text": "Periksa lantai obsidian untuk melucuti kawat pemicu jebakan (Uji DEX - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Buka tas perbekalan, siapkan ramuan dan atur pernapasan", "type": "action"}
        ],
        "log": [f"Karakter baru '{game_state['player']['name']}' ({c['title']}) telah dibangkitkan."]
    }
    save_game()

def advance_dungeon_scene(choice_id: str, custom_text: str = "", roll_val: int = 0) -> Dict[str, Any]:
    global game_state
    p = game_state["player"]
    scene = game_state["scene"]
    
    if roll_val > 0:
        is_crit = roll_val == 20 or (roll_val >= 19 and p.get("class_id") == "rogue")
        is_fail = roll_val == 1
        is_success = roll_val >= 10

        if is_crit:
            p["gold"] += 25
            p["exp"] += 50
            outcome = f"🔥 CRITICAL SUCCESS! (Dadu: {roll_val}). Serangan spektakuler Paduka memancarkan ledakan aura dahsyat! Rantai penahan hancur berkeping-keping dan ditemukan peti kuno berisi 25 Keping Emas (+50 EXP)."
            next_scene = {
                "chapter": "Bab 2: Ruang Altar Hitam",
                "title": "Ruang Altar Jantung Bayangan",
                "location": "Kedalaman Makam - Lantai 2",
                "narrative": "Sebuah altar marmer obsidian berdiri di tengah danau darah yang membeku. Di atas altar melayang 'Jantung Bayangan' yang berdenyut memancarkan kekuatan kosmik. Dua ksatria kerangka berzirah hitam bangkit dengan pedang menyala!",
                "choices": [
                    {"id": "A", "text": "Terjang dan tebas kedua kerangka dengan tebasan badai melingkar (Uji STR - DC 13)", "type": "roll", "dc": 13, "stat": "STR"},
                    {"id": "B", "text": "Lepaskan gelombang api suci untuk membakar altar dan mengusir roh (Uji INT - DC 12)", "type": "roll", "dc": 12, "stat": "INT"},
                    {"id": "C", "text": "Melompat lincah ke pilar atas dan bidik Jantung Bayangan (Uji DEX - DC 14)", "type": "roll", "dc": 14, "stat": "DEX"},
                    {"id": "D", "text": "Teguk ramuan pemulihan dan pasang kuda-kuda bertahan", "type": "action"}
                ]
            }
        elif is_fail:
            dmg = 25
            p["hp"] = max(0, p["hp"] - dmg)
            outcome = f"💀 CRITICAL FAIL! (Dadu: {roll_val}). Pijakan batu runtuh seketika! Jebakan tombak beracun menembus bahu Paduka (-{dmg} HP). Gerbang terbuka karena sistem darurat, namun Paduka terluka cukup parah!"
            next_scene = {
                "chapter": "Bab 1: Lorong Malapetaka",
                "title": "Lorong Semburan Gas Beracun",
                "location": "Lorong Bawah Makam",
                "narrative": "Darah menetes ke lantai obsidian yang dingin. Dari celah dinding batu, deretan patung gargoyle mulai menyemburkan gas beracun berwarna hijau lumut. Pintu keluar di ujung lorong perlahan mulai menutup!",
                "choices": [
                    {"id": "A", "text": "Berlari sekuat tenaga menembus kabut gas beracun (Uji STR/DEX - DC 13)", "type": "roll", "dc": 13, "stat": "DEX"},
                    {"id": "B", "text": "Gunakan perisai/senjata untuk menghancurkan kepala patung penyembur (Uji STR - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
                    {"id": "C", "text": "Luncurkan mantra perisai angin pelindung (Uji INT - DC 10)", "type": "roll", "dc": 10, "stat": "INT"},
                    {"id": "D", "text": "Gunakan ramuan penyembuh untuk menetralkan rasa sakit", "type": "action"}
                ]
            }
        elif is_success:
            p["gold"] += 10
            p["exp"] += 25
            outcome = f"⚔️ KEBERHASILAN! (Dadu: {roll_val}). Tindakan Paduka sukses tanpa cela! Mekanisme gerbang terbuka perlahan tanpa memicu jebakan alarm (+10 Gold, +25 EXP)."
            next_scene = {
                "chapter": "Bab 2: Aula Pilar Kuno",
                "title": "Aula Pilar Kuno & Penjaga Hantu",
                "location": "Kedalaman Makam - Lantai 2",
                "narrative": "Sebuah aula megah ditopang pilar-pilar batu raksasa terbentang luas. Di sudut ruangan tampak peti harta karun berkunci perak, dijaga oleh sesosok bayangan Spectre berpunggung sayap yang melayang tanpa suara.",
                "choices": [
                    {"id": "A", "text": "Sergap Spectre dengan serangan kejutan kilat (Uji STR - DC 11)", "type": "roll", "dc": 11, "stat": "STR"},
                    {"id": "B", "text": "Buka peti harta karun dengan lockpick senyap tanpa menarik perhatian (Uji DEX - DC 12)", "type": "roll", "dc": 12, "stat": "DEX"},
                    {"id": "C", "text": "Berdialog dalam bahasa roh kuno untuk menjinakkan Spectre (Uji INT/WIS - DC 10)", "type": "roll", "dc": 10, "stat": "INT"},
                    {"id": "D", "text": "Lempar koin emas ke arah sudut pilar untuk mengalihkan pandangannya", "type": "action"}
                ]
            }
        else:
            dmg = 12
            p["hp"] = max(0, p["hp"] - dmg)
            outcome = f"⚠️ GAGAL! (Dadu: {roll_val}). Sentuhan Paduka ditolak oleh rune pelindung, melepaskan sengatan listrik kuno (-{dmg} HP). Namun hentakan energi tersebut meremukkan engsel pintu."
            next_scene = {
                "chapter": "Bab 2: Aula Pilar Kuno",
                "title": "Aula Pilar Kuno (Kondisi Waspada)",
                "location": "Kedalaman Makam - Lantai 2",
                "narrative": "Dengan tubuh masih terasa perih akibat sengatan listrik, Paduka melangkah masuk ke aula pilar. Di kejauhan, hantu Spectre telah mendeteksi suara dentuman dan kini bersiap menyerang!",
                "choices": [
                    {"id": "A", "text": "Pasang posisi bertahan dan tangkis tebasan sabit hantu (Uji STR - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
                    {"id": "B", "text": "Mundur cepat dan lemparkan mantra pengusir roh (Uji INT - DC 11)", "type": "roll", "dc": 11, "stat": "INT"},
                    {"id": "C", "text": "Gunakan item penyembuh atau elixir dari tas", "type": "action"},
                    {"id": "D", "text": "Berlari mencari jalan tembus rahasia di balik pilar", "type": "action"}
                ]
            }
    else:
        # Non-roll / Rest / Item
        if "ramuan" in choice_id.lower() or "elixir" in choice_id.lower() or choice_id == "D":
            heal = 40
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            outcome = f"🧪 Paduka meneguk Elixir Penyembuh! Tubuh terasa hangat berdenyut, luka menutup (+{heal} HP)."
        elif custom_text:
            outcome = f"✨ Paduka bersabda: \"{custom_text}\". Takdir merespons kehendak sang ksatria dengan guncangan mistis!"
        else:
            outcome = f"🛡️ Paduka mengambil posisi bersiap dan memindai suasana dengan tatapan tajam."
            
        next_scene = {
            "chapter": scene.get("chapter", "Bab 1"),
            "title": scene.get("title", "Gerbang Makam"),
            "location": scene.get("location", "Makam Kuno"),
            "narrative": scene.get("narrative", "..."),
            "choices": scene.get("choices", [])
        }

    # Level Up Check
    if p["exp"] >= 100 * p["level"]:
        p["level"] += 1
        p["max_hp"] += 20
        p["hp"] = p["max_hp"]
        p["max_mp"] += 15
        p["mp"] = p["max_mp"]
        outcome += f" 🌟 LEVEL UP! Paduka mencapai Level {p['level']}! Max HP & MP meningkat tajam!"

    game_state["scene"]["chapter"] = next_scene["chapter"]
    game_state["scene"]["title"] = next_scene["title"]
    game_state["scene"]["location"] = next_scene["location"]
    game_state["scene"]["narrative"] = next_scene["narrative"]
    game_state["scene"]["choices"] = next_scene["choices"]
    game_state["scene"]["log"].append(outcome)
    if len(game_state["scene"]["log"]) > 6:
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
                choice = data.get("choice")
                is_roll = choice.get("type") == "roll"
                
                if is_roll:
                    roll_result = random.randint(1, 20)
                    await manager.broadcast_all({
                        "type": "dice_rolling",
                        "choice_text": choice.get("text"),
                        "stat": choice.get("stat", "D20")
                    })
                    await asyncio.sleep(2.5)
                    await manager.broadcast_all({
                        "type": "dice_result",
                        "value": roll_result
                    })
                    await asyncio.sleep(1.5)
                    update_data = advance_dungeon_scene(choice.get("id"), roll_val=roll_result)
                    await manager.broadcast_all(update_data)
                else:
                    update_data = advance_dungeon_scene(choice.get("id"))
                    await manager.broadcast_all(update_data)

            elif action_type == "custom_action":
                custom_text = data.get("text", "")
                roll_result = random.randint(1, 20)
                await manager.broadcast_all({
                    "type": "dice_rolling",
                    "choice_text": f"Aksi Khusus: {custom_text}",
                    "stat": "D20"
                })
                await asyncio.sleep(2.5)
                await manager.broadcast_all({
                    "type": "dice_result",
                    "value": roll_result
                })
                await asyncio.sleep(1.5)
                update_data = advance_dungeon_scene("CUSTOM", custom_text=custom_text, roll_val=roll_result)
                await manager.broadcast_all(update_data)

            elif action_type == "reset_game":
                game_state.clear()
                game_state.update(json.loads(json.dumps(DEFAULT_GAME_STATE)))
                game_state["status"] = "character_creation"
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Game telah dimulai ulang ke Pemilihan Karakter."})

    except WebSocketDisconnect:
        await manager.disconnect_controller(websocket)
