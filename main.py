import asyncio
import json
import random
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Darsam RPG Dungeon Engine")

app.mount("/static", StaticFiles(directory="/home/ubuntu/Github/darsam-rpg-engine/static"), name="static")
templates = Jinja2Templates(directory="/home/ubuntu/Github/darsam-rpg-engine/templates")

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

# Initial Game State
game_state = {
    "player": {
        "name": "Danas the Champion",
        "class": "Spellblade Knight",
        "hp": 100,
        "max_hp": 100,
        "mp": 50,
        "max_mp": 50,
        "gold": 25,
        "inventory": ["Pedang Pusaka Gelap", "Elixir Penyembuh (x1)", "Obor Kuno"]
    },
    "scene": {
        "title": "Gerbang Kehancuran: Makam Terlupakan",
        "location": "Bawah Tanah Kastil Oakhaven",
        "narrative": "Kabut pekat beraroma belerang menyelimuti tangga batu yang runtuh. Di hadapan Paduka, berdiri sebuah gerbang besi berkepala naga bermata safir yang bersinar redup. Suara rantai berdencing dari dalam kegelapan, diiringi hembusan angin sedingin es.",
        "choices": [
            {"id": "A", "text": "Hunus pedang dan terjang gerbang dengan paksa (Uji Kekuatan - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "B", "text": "Raba mata safir dan baca mantra kuno pembuka segel (Uji Sihir - DC 10)", "type": "roll", "dc": 10, "stat": "INT"},
            {"id": "C", "text": "Periksa lantai dan celah batu untuk mencari jebakan tersembunyi (Uji Ketelitian - DC 8)", "type": "roll", "dc": 8, "stat": "DEX"},
            {"id": "D", "text": "Teguk Elixir Penyembuh dan bersiap dalam posisi bertahan", "type": "action"}
        ],
        "log": ["Petualangan di Makam Terlupakan telah dimulai..."]
    }
}

# Procedural Scenarios Generator for Instant Dynamic Play
def process_action(choice_id: str, custom_text: str = "", roll_val: int = 0) -> Dict[str, Any]:
    current_scene = game_state["scene"]["title"]
    p = game_state["player"]
    
    if roll_val > 0:
        is_success = roll_val >= 10
        is_crit = roll_val == 20
        is_fail = roll_val == 1
        
        if is_crit:
            p["gold"] += 20
            p["mp"] = min(p["max_mp"], p["mp"] + 15)
            outcome = f"🎲 CRITICAL SUCCESS! (Roll: {roll_val}). Serangan sihir & pedang Paduka memancarkan ledakan aura dahsyat! Rantai penahan gerbang hancur berkeping-keping. Ditemukan kantung berisi 20 Koin Emas Kuno di balik reruntuhan!"
            next_scene = {
                "title": "Ruang Altar Terlarang",
                "location": "Kedalaman Makam",
                "narrative": "Sebuah altar marmer hitam berdiri di tengah kolam darah yang mengkristal. Di atas altar melayang 'Jantung Bayangan' yang berdenyut memancarkan kekuatan kosmik. Dua ksatria kerangka berzirah berkarat bangkit menghalangi jalan!",
                "choices": [
                    {"id": "A", "text": "Ayunan Pedang Badai membelah kedua kerangka sekaligus (Uji STR - DC 13)", "type": "roll", "dc": 13, "stat": "STR"},
                    {"id": "B", "text": "Lepaskan gelombang api suci untuk membakar altar (Uji INT - DC 11)", "type": "roll", "dc": 11, "stat": "INT"},
                    {"id": "C", "text": "Menghindar cepat ke balik pilar dan incar Jantung Bayangan (Uji DEX - DC 14)", "type": "roll", "dc": 14, "stat": "DEX"},
                    {"id": "D", "text": "Gunakan Obor Kuno untuk mengalihkan perhatian musuh", "type": "action"}
                ]
            }
        elif is_fail:
            dmg = 20
            p["hp"] = max(0, p["hp"] - dmg)
            outcome = f"💀 CRITICAL FAIL! (Roll: {roll_val}). Pijakan batu runtuh seketika! Tombak berkarat dari dinding menusuk bahu Paduka (-{dmg} HP). Gerbang terbuka karena mekanisme darurat, namun Paduka terluka parah!"
            next_scene = {
                "title": "Lorong Jebakan Berbisa",
                "location": "Lorong Bawah Makam",
                "narrative": "Napas Paduka terasa berat, darah menetes ke lantai obsidian. Dari dinding, patung gargoyle mulai menyemburkan gas beracun berwarna hijau lumut. Pintu keluar di ujung lorong perlahan mulai menutup!",
                "choices": [
                    {"id": "A", "text": "Berlari sekuat tenaga menembus gas beracun (Uji CON - DC 14)", "type": "roll", "dc": 14, "stat": "CON"},
                    {"id": "B", "text": "Hantam patung gargoyle untuk menyumbat semburan gas (Uji STR - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
                    {"id": "C", "text": "Luncurkan mantra perisai angin pelindung (Uji INT - DC 10)", "type": "roll", "dc": 10, "stat": "INT"},
                    {"id": "D", "text": "Minum Elixir Penyembuh untuk memulihkan luka", "type": "action"}
                ]
            }
        elif is_success:
            p["gold"] += 5
            outcome = f"⚔️ KEBERHASILAN! (Roll: {roll_val}). Tindakan Paduka berhasil secara presisi! Mekanisme gerbang terbuka perlahan tanpa memicu alarm kuno (+5 Gold)."
            next_scene = {
                "title": "Aula Pilar Kuno",
                "location": "Lantai 2 Bawah Tanah",
                "narrative": "Ruangan megah ditopang pilar-pilar batu raksasa. Di sudut ruangan tampak peti harta karun berkunci perak, dijaga oleh bayangan Spectre yang melayang tanpa suara.",
                "choices": [
                    {"id": "A", "text": "Sergap Spectre dengan tebasan pedang berbalut petir (Uji STR - DC 11)", "type": "roll", "dc": 11, "stat": "STR"},
                    {"id": "B", "text": "Buka peti harta karun dengan lockpick senyap (Uji DEX - DC 12)", "type": "roll", "dc": 12, "stat": "DEX"},
                    {"id": "C", "text": "Berdialog dalam bahasa roh kuno untuk menjinakkan Spectre (Uji CHA - DC 10)", "type": "roll", "dc": 10, "stat": "CHA"},
                    {"id": "D", "text": "Lempar koin emas ke arah lain untuk memancing musuh", "type": "action"}
                ]
            }
        else:
            dmg = 10
            p["hp"] = max(0, p["hp"] - dmg)
            outcome = f"⚠️ GAGAL! (Roll: {roll_val}). Gerbang menolak sentuhan Paduka dan melepaskan sengatan listrik kuno (-{dmg} HP). Namun segel akhirnya melemah dan pintu terbuka."
            next_scene = {
                "title": "Aula Pilar Kuno",
                "location": "Lantai 2 Bawah Tanah",
                "narrative": "Dengan luka sengatan listrik, Paduka melangkah ke aula pilar. Di kejauhan terdengar tawa hampa bayangan hantu penjaga yang bersiap menyerang.",
                "choices": [
                    {"id": "A", "text": "Serang bayangan sebelum sempat mendekat (Uji DEX - DC 12)", "type": "roll", "dc": 12, "stat": "DEX"},
                    {"id": "B", "text": "Gunakan mantra perlindungan diri (Uji INT - DC 10)", "type": "roll", "dc": 10, "stat": "INT"},
                    {"id": "C", "text": "Teguk Elixir Penyembuh untuk memulihkan HP", "type": "action"},
                    {"id": "D", "text": "Mundur perlahan dan cari jalan pintas di celah pilar", "type": "action"}
                ]
            }
    else:
        # Instant non-roll actions
        if "Elixir" in choice_id or choice_id == "D":
            heal = 35
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            outcome = f"🧪 Paduka meneguk Elixir Penyembuh! Tubuh terasa hangat, luka menutup (+{heal} HP)."
        elif custom_text:
            outcome = f"✨ Paduka bersabda: \"{custom_text}\". Takdir merespons kehendak Paduka dengan getaran energi kosmik!"
        else:
            outcome = f"🛡️ Paduka mengambil posisi bersiap dan mengamati sekitar dengan waspada."
            
        next_scene = {
            "title": game_state["scene"]["title"],
            "location": game_state["scene"]["location"],
            "narrative": game_state["scene"]["narrative"],
            "choices": game_state["scene"]["choices"]
        }

    game_state["scene"]["title"] = next_scene["title"]
    game_state["scene"]["location"] = next_scene["location"]
    game_state["scene"]["narrative"] = next_scene["narrative"]
    game_state["scene"]["choices"] = next_scene["choices"]
    game_state["scene"]["log"].append(outcome)
    if len(game_state["scene"]["log"]) > 6:
        game_state["scene"]["log"].pop(0)

    return {
        "type": "state_update",
        "outcome": outcome,
        "state": game_state
    }

@app.get("/tv", response_class=HTMLResponse)
async def tv_page(request: Request):
    return templates.TemplateResponse(request=request, name="tv.html", context={"state": game_state})

@app.get("/controller", response_class=HTMLResponse)
async def controller_page(request: Request):
    return templates.TemplateResponse(request=request, name="controller.html", context={"state": game_state})

@app.get("/api/state")
async def get_state():
    return game_state

@app.websocket("/ws/tv")
async def ws_tv(websocket: WebSocket):
    await manager.connect_tv(websocket)
    try:
        await websocket.send_json({"type": "init", "state": game_state})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_tv(websocket)

@app.websocket("/ws/controller")
async def ws_controller(websocket: WebSocket):
    await manager.connect_controller(websocket)
    try:
        await websocket.send_json({"type": "init", "state": game_state})
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            action_type = data.get("type")

            if action_type == "select_choice":
                choice = data.get("choice")
                is_roll = choice.get("type") == "roll"
                
                if is_roll:
                    # Trigger Roll Phase on TV and Controller
                    roll_result = random.randint(1, 20)
                    await manager.broadcast_all({
                        "type": "dice_rolling",
                        "choice_text": choice.get("text"),
                        "stat": choice.get("stat", "D20")
                    })
                    # Pause for suspense animation
                    await asyncio.sleep(2.5)
                    await manager.broadcast_all({
                        "type": "dice_result",
                        "value": roll_result
                    })
                    await asyncio.sleep(1.5)
                    update_data = process_action(choice.get("id"), roll_val=roll_result)
                    await manager.broadcast_all(update_data)
                else:
                    update_data = process_action(choice.get("id"))
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
                update_data = process_action("CUSTOM", custom_text=custom_text, roll_val=roll_result)
                await manager.broadcast_all(update_data)

            elif action_type == "reset_game":
                game_state["player"]["hp"] = 100
                game_state["player"]["mp"] = 50
                game_state["player"]["gold"] = 25
                game_state["scene"]["title"] = "Gerbang Kehancuran: Makam Terlupakan"
                game_state["scene"]["location"] = "Bawah Tanah Kastil Oakhaven"
                game_state["scene"]["narrative"] = "Kabut pekat beraroma belerang menyelimuti tangga batu yang runtuh. Di hadapan Paduka, berdiri sebuah gerbang besi berkepala naga bermata safir yang bersinar redup."
                game_state["scene"]["choices"] = [
                    {"id": "A", "text": "Hunus pedang dan terjang gerbang dengan paksa (Uji Kekuatan - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
                    {"id": "B", "text": "Raba mata safir dan baca mantra kuno pembuka segel (Uji Sihir - DC 10)", "type": "roll", "dc": 10, "stat": "INT"},
                    {"id": "C", "text": "Periksa lantai dan celah batu untuk mencari jebakan tersembunyi (Uji Ketelitian - DC 8)", "type": "roll", "dc": 8, "stat": "DEX"},
                    {"id": "D", "text": "Teguk Elixir Penyembuh dan bersiap dalam posisi bertahan", "type": "action"}
                ]
                game_state["scene"]["log"] = ["Game telah di-reset kembali ke awal."]
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Game telah dimulai ulang!"})

    except WebSocketDisconnect:
        await manager.disconnect_controller(websocket)
