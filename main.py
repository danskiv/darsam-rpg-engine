import asyncio
import json
import os
import random
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Darsam RPG Dungeon Engine - Master Edition")

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

DUNGEON_BIOMES = [
    {
        "chapter": "Bab 1: Gerbang Kehancuran",
        "location": "Makam Kuno Oakhaven - Lantai 1",
        "title": "Pintu Gerbang Besi Berkepala Naga",
        "narrative": "Kabut pekat beraroma belerang menyelimuti tangga batu yang runtuh. Di hadapan Paduka, berdiri sebuah gerbang besi berkepala naga bermata safir yang memancarkan hawa sedingin es. Rantai segel kuno bergetar seolah menyambut kedatangan darah baru.",
        "choices": [
            {"id": "A", "text": "Hunus senjata dan dobrak gerbang dengan tenaga penuh (Uji STR - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "B", "text": "Sentuh mata safir dan selaraskan energi gaib pembuka segel (Uji INT - DC 11)", "type": "roll", "dc": 11, "stat": "INT"},
            {"id": "C", "text": "Periksa lantai obsidian untuk melucuti kawat pemicu jebakan (Uji DEX - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Buka tas perbekalan, siapkan ramuan dan atur pernapasan", "type": "action"}
        ]
    },
    {
        "chapter": "Bab 2: Aula Tulang & Altar Obsidian",
        "location": "Kubah Kematian - Lantai 2",
        "title": "Altar Jantung Kegelapan",
        "narrative": "Lantai marmer hitam retak ditaburi ribuan tengkorak ksatria masa lalu. Di atas altar melayang kristal berdenyut berwarna merah darah. Dua Prajurit Kerangka Raksasa berpedang api bangkit dari tumpukan tulang!",
        "choices": [
            {"id": "A", "text": "Ayunkan serangan putar dahsyat menghantam kedua kerangka (Uji STR - DC 13)", "type": "roll", "dc": 13, "stat": "STR"},
            {"id": "B", "text": "Keluarkan mantra badai halilintar untuk menghancurkan kristal altar (Uji INT - DC 12)", "type": "roll", "dc": 12, "stat": "INT"},
            {"id": "C", "text": "Menyelinap di balik bayangan pilar dan tusuk titik lemah inti tengkorak (Uji DEX - DC 14)", "type": "roll", "dc": 14, "stat": "DEX"},
            {"id": "D", "text": "Lemparkan koin perak kuno untuk mengacaukan pandangan sihir musuh", "type": "action"}
        ]
    },
    {
        "chapter": "Bab 3: Labirin Air Terjun Beracun",
        "location": "Gua Jamur Bercahaya - Lantai 3",
        "title": "Jembatan Batu Gantung yang Rapuh",
        "narrative": "Suara gemuruh air terjun asam kehijauan menggema di gua raksasa. Jembatan tali berlumut bergoyang tertiup angin bawah tanah. Di seberang, seekor Chimera Bersayap Kelelawar sedang tertidur menjaga peti harta karun berlapis emas.",
        "choices": [
            {"id": "A", "text": "Melangkah perlahan menyeberangi jembatan tanpa mengeluarkan suara (Uji DEX - DC 12)", "type": "roll", "dc": 12, "stat": "DEX"},
            {"id": "B", "text": "Lontarkan panah/mantra jarak jauh tepat ke leher Chimera (Uji DEX/INT - DC 14)", "type": "roll", "dc": 14, "stat": "DEX"},
            {"id": "C", "text": "Pelajari aliran angin dan temukan jalur tebing alternatif (Uji WIS - DC 10)", "type": "roll", "dc": 10, "stat": "WIS"},
            {"id": "D", "text": "Teguk ramuan stamina dan siapkan posisi tempur", "type": "action"}
        ]
    },
    {
        "chapter": "Bab 4: Singgasana Raja Terkutuk",
        "location": "Kuil Kehampaan - Lantai Terdalam",
        "title": "Kemunculan Sang Lich Lord Malakor",
        "narrative": "Singgasana dari besi tempa neraka menjulang tinggi. Sesosok Lich purba berjubah ungu gelap melayang turun dengan tongkat bermata intan hitam. Matanya menyala biru menusuk jiwa. 'Siapa yang berani mengotori kesunyian makamku?!' gelegarnya!",
        "choices": [
            {"id": "A", "text": "Terjang langsung dengan segenap tekad dan tebaskan senjata pusaka (Uji STR - DC 15)", "type": "roll", "dc": 15, "stat": "STR"},
            {"id": "B", "text": "Rapal mantra pembalik kutukan suci untuk melumpuhkan pelindung Lich (Uji INT/WIS - DC 14)", "type": "roll", "dc": 14, "stat": "INT"},
            {"id": "C", "text": "Gulingkan tubuh ke samping dan lemparkan belati/bom ke jimat pengikat roh (Uji DEX - DC 13)", "type": "roll", "dc": 13, "stat": "DEX"},
            {"id": "D", "text": "Gunakan Elixir Tertinggi untuk memulihkan seluruh tenaga dan pertahanan", "type": "action"}
        ]
    }
]

RANDOM_EVENTS = [
    {
        "title": "Pedagang Misterius dari Kegelapan",
        "desc": "Sesosok makhluk kerdil bertudung kain perak muncul dari balik pilar retak. Matanya berbinar melihat kantung koin Paduka. 'Peralatan langka untuk ksatria sejati, Tuan...' bisiknya.",
        "type": "merchant",
        "choices": [
            {"id": "A", "text": "Beli 'Elixir Darah Naga' (+60 HP Maksimal) seharga 25 Gold", "type": "action", "cost": 25, "effect": "buy_elixir"},
            {"id": "B", "text": "Beli 'Gulungan Mantra Kosmik' (+40 MP Maksimal) seharga 25 Gold", "type": "action", "cost": 25, "effect": "buy_mana"},
            {"id": "C", "text": "Tolak tawaran secara sopan dan lanjutkan perjalanan", "type": "action", "effect": "pass"},
            {"id": "D", "text": "Ancam pedagang untuk mendapatkan diskon (Uji STR/CHA - DC 13)", "type": "roll", "dc": 13, "stat": "STR"}
        ]
    },
    {
        "title": "Mata Air Suci Kuno",
        "desc": "Di sudut reruntuhan memancar mata air bercahaya biru keemasan. Gemericik airnya memancarkan aroma bunga teratai mistis yang menenangkan jiwa.",
        "type": "shrine",
        "choices": [
            {"id": "A", "text": "Basuh luka dan minum air suci (Pulihkan 50 HP & 30 MP)", "type": "action", "effect": "heal_full"},
            {"id": "B", "text": "Celupkan senjata ke dalam mata air untuk memberkati daya serang (Uji WIS - DC 11)", "type": "roll", "dc": 11, "stat": "WIS"},
            {"id": "C", "text": "Isi botol kosong dengan air suci sebagai cadangan perbekalan", "type": "action", "effect": "get_potion"},
            {"id": "D", "text": "Heningkan cipta berdoa kepada para leluhur kerajaan", "type": "action", "effect": "blessing"}
        ]
    },
    {
        "title": "Peti Harta Terjebak Mimic",
        "desc": "Sebuah peti kayu berukir emas tergeletak tanpa penjagaan. Namun lidah kayu di kuncinya tampak bergerak sedikit seperti bernapas...",
        "type": "mimic",
        "choices": [
            {"id": "A", "text": "Buka peti dengan cepat dan tebas lidahnya sebelum bergerak (Uji STR - DC 13)", "type": "roll", "dc": 13, "stat": "STR"},
            {"id": "B", "text": "Bakar peti dari kejauhan dengan semburan api mantra (Uji INT - DC 11)", "type": "roll", "dc": 11, "stat": "INT"},
            {"id": "C", "text": "Lempar potongan daging kering untuk menguji apakah itu monster Mimic", "type": "action", "effect": "feed_mimic"},
            {"id": "D", "text": "Abaikan peti mencurigakan ini dan ambil rute memutar", "type": "action", "effect": "pass"}
        ]
    }
]

DEFAULT_GAME_STATE = {
    "status": "character_creation",
    "floor": 1,
    "step": 0,
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
        "chapter": DUNGEON_BIOMES[0]["chapter"],
        "title": DUNGEON_BIOMES[0]["title"],
        "location": DUNGEON_BIOMES[0]["location"],
        "narrative": DUNGEON_BIOMES[0]["narrative"],
        "choices": DUNGEON_BIOMES[0]["choices"],
        "log": ["Petualangan agung di Makam Kuno Oakhaven dimulai..."]
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
    game_state["floor"] = 1
    game_state["step"] = 0
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
    first_biome = DUNGEON_BIOMES[0]
    game_state["scene"] = {
        "chapter": first_biome["chapter"],
        "title": first_biome["title"],
        "location": first_biome["location"],
        "narrative": f"Sang {c['title']}, {game_state['player']['name']}, melangkah menuruni tangga batu berlumut. Di hadapan Paduka, berdiri sebuah gerbang besi berkepala naga bermata safir yang memancarkan hawa sedingin es. Rantai segel kuno bergetar seolah menyambut kedatangan darah baru.",
        "choices": list(first_biome["choices"]),
        "log": [f"Karakter baru '{game_state['player']['name']}' ({c['title']}) telah bangkit!"]
    }
    save_game()

def advance_dungeon_scene(choice_id: str, custom_text: str = "", roll_val: int = 0) -> Dict[str, Any]:
    global game_state
    p = game_state["player"]
    scene = game_state["scene"]
    game_state["step"] = game_state.get("step", 0) + 1
    
    # Check trigger for Random Encounter Event (Every 3-4 steps)
    trigger_random_event = (game_state["step"] % 3 == 0) and random.random() < 0.75

    if roll_val > 0:
        is_crit = roll_val >= 20 or (roll_val >= 19 and p.get("class_id") == "rogue")
        is_fail = roll_val == 1
        is_success = roll_val >= 10

        if is_crit:
            gold_gain = random.randint(25, 45)
            exp_gain = random.randint(50, 75)
            p["gold"] += gold_gain
            p["exp"] += exp_gain
            outcome = f"🔥 CRITICAL SUCCESS! (Dadu: {roll_val}). Serangan spektakuler Paduka memancarkan ledakan aura dahsyat! Rantai penahan hancur berkeping-keping dan ditemukan peti pusaka berisi {gold_gain} Keping Emas (+{exp_gain} EXP)!"
        elif is_fail:
            dmg = random.randint(18, 28)
            if p.get("class_id") == "paladin":
                dmg = max(5, dmg - 3)
            p["hp"] = max(0, p["hp"] - dmg)
            outcome = f"💀 CRITICAL FAIL! (Dadu: {roll_val}). Pijakan batu runtuh seketika! Jebakan tombak menusuk bahu Paduka (-{dmg} HP). Paduka terluka namun berhasil merayap maju!"
        elif is_success:
            gold_gain = random.randint(10, 20)
            exp_gain = random.randint(25, 40)
            p["gold"] += gold_gain
            p["exp"] += exp_gain
            outcome = f"⚔️ KEBERHASILAN! (Dadu: {roll_val}). Tindakan Paduka sukses tanpa cela! Jalan pintas terbuka (+{gold_gain} Gold, +{exp_gain} EXP)."
        else:
            dmg = random.randint(8, 15)
            if p.get("class_id") == "paladin":
                dmg = max(3, dmg - 3)
            p["hp"] = max(0, p["hp"] - dmg)
            outcome = f"⚠️ GAGAL! (Dadu: {roll_val}). Serangan ditangkis atau jebakan menyengat Paduka (-{dmg} HP). Namun hentakan energi membuka celah ruangan berikutnya."
    else:
        # Action handler
        if choice_id == "buy_elixir" and p["gold"] >= 25:
            p["gold"] -= 25
            p["max_hp"] += 40
            p["hp"] = p["max_hp"]
            outcome = f"🍷 Paduka membeli dan meminum Elixir Darah Naga! Kekuatan fisik melonjak dahsyat (+40 Max HP)!"
        elif choice_id == "buy_mana" and p["gold"] >= 25:
            p["gold"] -= 25
            p["max_mp"] += 30
            p["mp"] = p["max_mp"]
            outcome = f"📜 Paduka mempelajari Gulungan Mantra Kosmik! Kapasitas energi sihir membesar (+30 Max MP)!"
        elif choice_id == "heal_full":
            p["hp"] = p["max_hp"]
            p["mp"] = p["max_mp"]
            outcome = f"🌊 Paduka membasuh diri di Mata Air Suci! Seluruh luka menutup dan stamina pulih sempurna (HP & MP Penuh)!"
        elif "ramuan" in choice_id.lower() or "elixir" in choice_id.lower() or choice_id == "D":
            heal = 45
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            outcome = f"🧪 Paduka meneguk Elixir Penyembuh! Tubuh terasa hangat, luka menutup (+{heal} HP)."
        elif custom_text:
            outcome = f"✨ Paduka bersabda: \"{custom_text}\". Takdir merespons kehendak sang ksatria dengan aura magis!"
        else:
            outcome = f"🛡️ Paduka mengambil posisi bersiap dan memindai suasana dengan tatapan tajam."

    # Next Scene Selection (Random Event vs Progressive Biome)
    if trigger_random_event:
        event = random.choice(RANDOM_EVENTS)
        next_scene = {
            "chapter": f"Peristiwa Acak: Pertemuan Takdir",
            "title": event["title"],
            "location": "Ruang Rahasia Tersembunyi",
            "narrative": event["desc"],
            "choices": list(event["choices"])
        }
    else:
        current_floor_idx = (game_state.get("floor", 1) - 1) % len(DUNGEON_BIOMES)
        game_state["floor"] = (current_floor_idx + 1) + 1
        biome = DUNGEON_BIOMES[(current_floor_idx + 1) % len(DUNGEON_BIOMES)]
        next_scene = {
            "chapter": biome["chapter"],
            "title": biome["title"],
            "location": biome["location"],
            "narrative": biome["narrative"],
            "choices": list(biome["choices"])
        }

    # Level Up Check
    if p["exp"] >= 100 * p["level"]:
        p["level"] += 1
        p["max_hp"] += 25
        p["hp"] = p["max_hp"]
        p["max_mp"] += 15
        p["mp"] = p["max_mp"]
        outcome += f" 🌟 LEVEL UP! Paduka naik ke Level {p['level']}! HP & MP pulih dan bertambah maksimal!"

    # Check Game Over
    if p["hp"] <= 0:
        outcome = f"💀 PADUKA TELAH GUGUR DALAM PERTEMPURAN! Jiwa sang ksatria terserap oleh Makam Kuno..."
        next_scene = {
            "chapter": "Akhir Petualangan",
            "title": "Makam Abadi",
            "location": "Kehampaan",
            "narrative": "Tubuh Paduka jatuh berlutut ke tanah dingin. Kegelapan menyelimuti pandangan, namun legenda keberanian Paduka akan terus bergema di lorong-lorong batu ini...",
            "choices": [
                {"id": "A", "text": "Bangkit kembali dari abu makam (Mulai Ulang)", "type": "action"}
            ]
        }

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
