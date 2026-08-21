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

app = FastAPI(title="Darsam RPG Dungeon Engine - Grandmaster Ultimate Edition")

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

# ==========================================
# 8 DIVERSE STARTING ORIGINS (ZERO TO HERO)
# ==========================================
CLASSES_INFO = {
    "peasant": {
        "title": "Hardy Peasant",
        "icon": "🌾",
        "desc": "Petani tangguh berotot liat. Bertahan hidup dengan stamina alamiah, ketabahan mental, dan insting tanah liat.",
        "base_hp": 115, "base_mp": 15, "str": 14, "dex": 10, "con": 15, "int": 8, "wis": 12, "cha": 8,
        "equipped": {
            "main_hand": {"id": "w_hoe", "name": "Rusty Farming Hoe", "rarity": "common", "type": "weapon", "slot": "main_hand", "icon": "⛏️", "bonus": {"str": 1, "atk": 4}, "val": 3},
            "off_hand": None,
            "armor": {"id": "a_linen", "name": "Homespun Tunic", "rarity": "common", "type": "armor", "slot": "armor", "icon": "👕", "bonus": {"hp": 5, "def": 1}, "val": 2},
            "accessory": None
        },
        "starting_inventory": [
            {"id": "c_ration_1", "name": "Dry Ration Bread", "rarity": "common", "type": "consumable", "icon": "🍞", "effect": "heal_hp_20", "desc": "Restores 20 HP", "val": 2},
            {"id": "c_ration_2", "name": "Dry Ration Bread", "rarity": "common", "type": "consumable", "icon": "🍞", "effect": "heal_hp_20", "desc": "Restores 20 HP", "val": 2},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3},
            {"id": "m_rope", "name": "Hemp Rope (15m)", "rarity": "common", "type": "material", "icon": "🪢", "desc": "Utility rope for climbing", "val": 2}
        ],
        "skills": [{"id": "sk_adrenaline", "name": "Adrenaline Surge", "cost_mp": 5, "cd": 3, "desc": "Instantly restores 25 HP & gain +2 STR for 2 turns."}]
    },
    "blacksmith": {
        "title": "Smith Apprentice",
        "icon": "🔨",
        "desc": "Magang bengkel tempa desa. Lengan kokoh terbiasa memukul baja panas, paham titik lemah struktur logam & batu.",
        "base_hp": 125, "base_mp": 10, "str": 16, "dex": 9, "con": 14, "int": 9, "wis": 10, "cha": 8,
        "equipped": {
            "main_hand": {"id": "w_smith_hammer", "name": "Heavy Smith Hammer", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "icon": "🔨", "bonus": {"str": 2, "atk": 6}, "val": 8},
            "off_hand": None,
            "armor": {"id": "a_apron", "name": "Thick Leather Apron", "rarity": "common", "type": "armor", "slot": "armor", "icon": "🦺", "bonus": {"con": 1, "def": 2}, "val": 5},
            "accessory": None
        },
        "starting_inventory": [
            {"id": "m_spikes", "name": "Iron Spikes (x5)", "rarity": "common", "type": "material", "icon": "🔩", "desc": "Wedge doors or climb walls", "val": 3},
            {"id": "m_whetstone", "name": "Smith Whetstone", "rarity": "common", "type": "consumable", "icon": "🪨", "effect": "buff_atk_2", "desc": "+2 ATK on equipped weapon", "val": 4},
            {"id": "c_ration_1", "name": "Smoked Meat Jerky", "rarity": "common", "type": "consumable", "icon": "🥩", "effect": "heal_hp_25", "desc": "Restores 25 HP", "val": 3},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3}
        ],
        "skills": [{"id": "sk_anvil", "name": "Anvil Crush", "cost_mp": 5, "cd": 3, "desc": "Deals massive STR-based blunt damage and stuns the monster for 1 turn."}]
    },
    "scholar": {
        "title": "Village Scholar",
        "icon": "📜",
        "desc": "Asisten tabib dan pembaca naskah tua. Fisik ringkih namun cerdas mengurai ancient runes dan ramuan herbal.",
        "base_hp": 85, "base_mp": 60, "str": 7, "dex": 11, "con": 10, "int": 16, "wis": 14, "cha": 10,
        "equipped": {
            "main_hand": {"id": "w_carver", "name": "Silver Lore Scalpel", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "icon": "🗡️", "bonus": {"int": 1, "atk": 3}, "val": 7},
            "off_hand": {"id": "o_diary", "name": "Ancient Herbarium Grimoire", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "icon": "📖", "bonus": {"wis": 1, "int": 1}, "val": 8},
            "armor": {"id": "a_robe", "name": "Scholar Travel Robes", "rarity": "common", "type": "armor", "slot": "armor", "icon": "👘", "bonus": {"mp": 10, "def": 1}, "val": 4},
            "accessory": None
        },
        "starting_inventory": [
            {"id": "c_salve_1", "name": "Herbal Healing Salve", "rarity": "uncommon", "type": "consumable", "icon": "🧪", "effect": "heal_hp_35", "desc": "Restores 35 HP & cures Bleeding", "val": 6},
            {"id": "c_salve_2", "name": "Herbal Healing Salve", "rarity": "uncommon", "type": "consumable", "icon": "🧪", "effect": "heal_hp_35", "desc": "Restores 35 HP & cures Bleeding", "val": 6},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3},
            {"id": "m_chalk", "name": "Alchemical Rune Chalk", "rarity": "common", "type": "material", "icon": "🖍️", "desc": "Inscribe protective glyphs", "val": 3}
        ],
        "skills": [{"id": "sk_arcane_spark", "name": "Arcane Spark", "cost_mp": 10, "cd": 1, "desc": "Blasts the target with pure INT magic damage (Bypasses armor)."}]
    },
    "trapper": {
        "title": "Forest Trapper",
        "icon": "🏹",
        "desc": "Pemburu satwa lereng bukit berkabut. Langkah hening tanpa jejak, awas jebakan, dan ahli membidik di kegelapan.",
        "base_hp": 95, "base_mp": 25, "str": 10, "dex": 16, "con": 11, "int": 10, "wis": 14, "cha": 8,
        "equipped": {
            "main_hand": {"id": "w_bow", "name": "Yew Shortbow", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "icon": "🏹", "bonus": {"dex": 2, "atk": 5}, "val": 8},
            "off_hand": {"id": "w_quiver", "name": "Fletched Arrow Quiver (15)", "rarity": "common", "type": "offhand", "slot": "off_hand", "icon": "🎯", "bonus": {"dex": 1}, "val": 4},
            "armor": {"id": "a_camo", "name": "Camouflage Pelt Vest", "rarity": "common", "type": "armor", "slot": "armor", "icon": "🦺", "bonus": {"dex": 1, "def": 1}, "val": 5},
            "accessory": None
        },
        "starting_inventory": [
            {"id": "c_snare", "name": "Serrated Wire Snare", "rarity": "uncommon", "type": "consumable", "icon": "🪤", "effect": "trap_bleed", "desc": "Deals 20 damage & immobilizes foe", "val": 6},
            {"id": "c_torch_1", "name": "Resin Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3},
            {"id": "c_ration_1", "name": "Dried Game Rations", "rarity": "common", "type": "consumable", "icon": "🥩", "effect": "heal_hp_20", "desc": "Restores 20 HP", "val": 2},
            {"id": "m_dagger", "name": "Flint Skinning Knife", "rarity": "common", "type": "weapon", "icon": "🔪", "bonus": {"dex": 1, "atk": 3}, "val": 3}
        ],
        "skills": [{"id": "sk_caltrop", "name": "Caltrop Scatter", "cost_mp": 8, "cd": 2, "desc": "Scatters razor spikes, inflicting Bleed and giving Advantage on next turn."}]
    },
    "guard": {
        "title": "Disgraced Watchman",
        "icon": "🛡️",
        "desc": "Mantan penjaga gerbang kota yang terbuang. Terbiasa menahan benturan tameng dan pertarungan jarak dekat.",
        "base_hp": 120, "base_mp": 15, "str": 15, "dex": 11, "con": 14, "int": 8, "wis": 10, "cha": 9,
        "equipped": {
            "main_hand": {"id": "w_sword", "name": "Notched Iron Broadsword", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "icon": "⚔️", "bonus": {"str": 2, "atk": 5}, "val": 8},
            "off_hand": {"id": "o_shield", "name": "Reinforced Oak Buckler", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "icon": "🛡️", "bonus": {"def": 3, "con": 1}, "val": 7},
            "armor": {"id": "a_chain", "name": "Tattered Chain Shirt", "rarity": "uncommon", "type": "armor", "slot": "armor", "icon": "🥋", "bonus": {"def": 3, "hp": 10}, "val": 9},
            "accessory": None
        },
        "starting_inventory": [
            {"id": "c_bandage", "name": "Sterile Cloth Bandage", "rarity": "common", "type": "consumable", "icon": "🩹", "effect": "cure_bleed_heal_15", "desc": "Stops Bleeding & heals 15 HP", "val": 3},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3},
            {"id": "c_ration_1", "name": "Hardtack Biscuit", "rarity": "common", "type": "consumable", "icon": "🍘", "effect": "heal_hp_20", "desc": "Restores 20 HP", "val": 2}
        ],
        "skills": [{"id": "sk_shield_wall", "name": "Shield Wall Bastion", "cost_mp": 6, "cd": 3, "desc": "Increases DEF by +6 and reflects 50% of melee damage for 2 turns."}]
    },
    "grave_robber": {
        "title": "Tomb Grave-Robber",
        "icon": "🕯️",
        "desc": "Penyusup liang kubur yang serakah. Ahli membobol gembok kuno, mencari jebakan rahasia, dan menyerang dari bayangan.",
        "base_hp": 90, "base_mp": 30, "str": 9, "dex": 16, "con": 11, "int": 13, "wis": 11, "cha": 12,
        "equipped": {
            "main_hand": {"id": "w_stiletto", "name": "Rusty Stiletto Dagger", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "icon": "🗡️", "bonus": {"dex": 2, "atk": 4}, "val": 7},
            "off_hand": {"id": "o_lockpick", "name": "Master Thieves' Tools", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "icon": "🗝️", "bonus": {"dex": 1, "cha": 1}, "val": 8},
            "armor": {"id": "a_cloak", "name": "Shadowed Scavenger Cloak", "rarity": "common", "type": "armor", "slot": "armor", "icon": "🧥", "bonus": {"dex": 1, "def": 1}, "val": 5},
            "accessory": {"id": "acc_lucky_coin", "name": "Gilded Luck Charm", "rarity": "rare", "type": "accessory", "slot": "accessory", "icon": "🪙", "bonus": {"cha": 2, "gold_drop": 15}, "val": 15}
        },
        "starting_inventory": [
            {"id": "c_smokebomb", "name": "Sulfur Smoke Vial", "rarity": "uncommon", "type": "consumable", "icon": "💨", "effect": "escape_guarantee", "desc": "100% Escape chance from any fight", "val": 8},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3},
            {"id": "m_crowbar", "name": "Iron Prying Crowbar", "rarity": "common", "type": "material", "icon": "🦯", "desc": "Pries open sarcophagi & stuck grates", "val": 4}
        ],
        "skills": [{"id": "sk_backstab", "name": "Shadow Ambush", "cost_mp": 10, "cd": 2, "desc": "Strikes from behind for 2.5x DEX damage with a guaranteed Critical Hit."}]
    },
    "monk": {
        "title": "Exiled Temple Acolyte",
        "icon": "⛪",
        "desc": "Murid kuil suci yang diasingkan. Memiliki keteguhan batin, doa mukjizat perlindungan, dan kemahiran tongkat bela diri.",
        "base_hp": 105, "base_mp": 45, "str": 11, "dex": 12, "con": 13, "int": 10, "wis": 16, "cha": 12,
        "equipped": {
            "main_hand": {"id": "w_staff", "name": "Polished Ash Quarterstaff", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "icon": "🦯", "bonus": {"wis": 2, "atk": 4}, "val": 7},
            "off_hand": {"id": "o_beads", "name": "Sandalwood Prayer Beads", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "icon": "📿", "bonus": {"wis": 1, "mp": 15}, "val": 8},
            "armor": {"id": "a_cassock", "name": "Pilgrim Cassock", "rarity": "common", "type": "armor", "slot": "armor", "icon": "🥋", "bonus": {"wis": 1, "def": 1}, "val": 4},
            "accessory": None
        },
        "starting_inventory": [
            {"id": "c_holy_water", "name": "Blessed Holy Water", "rarity": "uncommon", "type": "consumable", "icon": "🏺", "effect": "cure_curse_heal_25", "desc": "Cleanses Curse/Poison & heals 25 HP", "val": 7},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3},
            {"id": "c_ration_1", "name": "Dried Figs & Nuts", "rarity": "common", "type": "consumable", "icon": "🥜", "effect": "heal_hp_20", "desc": "Restores 20 HP & 10 MP", "val": 3}
        ],
        "skills": [{"id": "sk_mend", "name": "Sacred Prayer of Radiance", "cost_mp": 12, "cd": 2, "desc": "Restores 35 HP to self and blinds all undead monsters for 1 turn."}]
    },
    "alchemist": {
        "title": "Alchemist Apprentice",
        "icon": "🧪",
        "desc": "Pencampur ramuan berbahaya yang diusir dari kota. Terbiasa meracik cairan asam, minyak peledak, dan eliksir ajaib.",
        "base_hp": 85, "base_mp": 50, "str": 8, "dex": 13, "con": 11, "int": 16, "wis": 12, "cha": 9,
        "equipped": {
            "main_hand": {"id": "w_pestle", "name": "Brass Mortar & Pestle Club", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "icon": "🪓", "bonus": {"int": 1, "atk": 3}, "val": 6},
            "off_hand": {"id": "o_flask", "name": "Volatile Acid Catalyst Flask", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "icon": "🧪", "bonus": {"int": 2}, "val": 9},
            "armor": {"id": "a_treated", "name": "Acid-Treated Leather Jerkin", "rarity": "uncommon", "type": "armor", "slot": "armor", "icon": "🦺", "bonus": {"con": 1, "def": 2}, "val": 7},
            "accessory": None
        },
        "starting_inventory": [
            {"id": "c_fire_flask", "name": "Flask of Wildfire Oil", "rarity": "uncommon", "type": "consumable", "icon": "🔥", "effect": "damage_fire_30", "desc": "Deals 30 Fire DMG to target monster", "val": 8},
            {"id": "c_antidote", "name": "Universal Antidote Draught", "rarity": "uncommon", "type": "consumable", "icon": "🧪", "effect": "cure_poison_heal_20", "desc": "Cures Poison & restores 20 HP", "val": 5},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3}
        ],
        "skills": [{"id": "sk_acid_throw", "name": "Corrosive Acid Bomb", "cost_mp": 10, "cd": 2, "desc": "Melts monster armor (-4 DEF) and deals continuous poison burn damage."}]
    }
}

# ==========================================
# LOOT TABLES & GENERATORS (RARITY SCALING)
# ==========================================
LOOT_DB = {
    "common": [
        {"name": "Chipped Iron Broadsword", "type": "weapon", "slot": "main_hand", "icon": "⚔️", "bonus": {"str": 1, "atk": 4}, "val": 4},
        {"name": "Crude Oak Staff", "type": "weapon", "slot": "main_hand", "icon": "🦯", "bonus": {"int": 1, "atk": 3}, "val": 3},
        {"name": "Reinforced Hide Vest", "type": "armor", "slot": "armor", "icon": "🦺", "bonus": {"def": 2, "hp": 10}, "val": 5},
        {"name": "Wooden Round Shield", "type": "offhand", "slot": "off_hand", "icon": "🛡️", "bonus": {"def": 2}, "val": 4},
        {"name": "Copper Signet Ring", "type": "accessory", "slot": "accessory", "icon": "💍", "bonus": {"cha": 1}, "val": 6},
        {"name": "Dry Ration Pack", "type": "consumable", "icon": "🍞", "effect": "heal_hp_20", "desc": "Restores 20 HP", "val": 2},
        {"name": "Pine Pitch Torch", "type": "consumable", "icon": "🕯️", "effect": "add_light_5", "desc": "+5 Torch Light turns", "val": 3},
        {"name": "Sterile Linen Bandage", "type": "consumable", "icon": "🩹", "effect": "cure_bleed_heal_15", "desc": "Stops Bleeding & heals 15 HP", "val": 3}
    ],
    "uncommon": [
        {"name": "Honed Steel Longsword", "type": "weapon", "slot": "main_hand", "icon": "⚔️", "bonus": {"str": 2, "atk": 7}, "val": 12},
        {"name": "Hunter's Composite Bow", "type": "weapon", "slot": "main_hand", "icon": "🏹", "bonus": {"dex": 3, "atk": 6}, "val": 14},
        {"name": "Iron-Studded Leather Cuirass", "type": "armor", "slot": "armor", "icon": "🥋", "bonus": {"def": 4, "hp": 20, "con": 1}, "val": 16},
        {"name": "Engraved Bronze Kite Shield", "type": "offhand", "slot": "off_hand", "icon": "🛡️", "bonus": {"def": 4, "con": 1}, "val": 14},
        {"name": "Silver Amulet of Vitality", "type": "accessory", "slot": "accessory", "icon": "📿", "bonus": {"hp": 25, "con": 2}, "val": 18},
        {"name": "Greater Healing Draught", "type": "consumable", "icon": "🧪", "effect": "heal_hp_45", "desc": "Restores 45 HP", "val": 10},
        {"name": "Aether Mana Flask", "type": "consumable", "icon": "✨", "effect": "heal_mp_30", "desc": "Restores 30 MP", "val": 10}
    ],
    "rare": [
        {"name": "Obsidian Edge War-Cleaver", "type": "weapon", "slot": "main_hand", "icon": "🪓", "bonus": {"str": 4, "atk": 12, "crit": 5}, "val": 35},
        {"name": "Stormcaller Quartz Scepter", "type": "weapon", "slot": "main_hand", "icon": "🔮", "bonus": {"int": 4, "wis": 2, "atk": 9}, "val": 38},
        {"name": "Gilded Plate of the Vanguard", "type": "armor", "slot": "armor", "icon": "🛡️", "bonus": {"def": 7, "hp": 45, "str": 2}, "val": 45},
        {"name": "Aegis of the Sunlit Citadel", "type": "offhand", "slot": "off_hand", "icon": "🛡️", "bonus": {"def": 6, "wis": 2, "hp": 20}, "val": 40},
        {"name": "Band of the Shadow Assassin", "type": "accessory", "slot": "accessory", "icon": "💍", "bonus": {"dex": 3, "crit": 10, "dodge": 5}, "val": 50},
        {"name": "Elixir of Restoration", "type": "consumable", "icon": "🌟", "effect": "full_restore", "desc": "Fully restores HP, MP & cleanses all status ailments", "val": 25}
    ],
    "epic": [
        {"name": "Malakor's Cursed Dreadblade", "type": "weapon", "slot": "main_hand", "icon": "🗡️", "bonus": {"str": 6, "dex": 3, "atk": 18, "lifesteal": 10}, "val": 95},
        {"name": "Archmage's Chrono-Weave Robes", "type": "armor", "slot": "armor", "icon": "👘", "bonus": {"def": 8, "int": 6, "mp": 50, "spell_power": 15}, "val": 110},
        {"name": "Ring of the Dragon Sovereign", "type": "accessory", "slot": "accessory", "icon": "👑", "bonus": {"str": 3, "con": 3, "hp": 60, "fire_res": 25}, "val": 130}
    ],
    "legendary": [
        {"name": "Garuda's Solar Relic Spear", "type": "weapon", "slot": "main_hand", "icon": "🔱", "bonus": {"str": 8, "dex": 5, "atk": 25, "crit": 15, "sun_burst": 20}, "val": 250},
        {"name": "Immortal Aegis of Primeval Earth", "type": "armor", "slot": "armor", "icon": "🛡️", "bonus": {"def": 14, "con": 8, "hp": 120, "dmg_reduction": 8}, "val": 300}
    ]
}

def roll_loot(monster_tier: str = "common", monster_lv: int = 1) -> Dict[str, Any]:
    roll = random.randint(1, 100)
    rarity = "common"
    if monster_tier == "boss":
        if roll <= 40: rarity = "epic"
        else: rarity = "legendary"
    elif monster_tier == "elite":
        if roll <= 45: rarity = "uncommon"
        elif roll <= 85: rarity = "rare"
        else: rarity = "epic"
    else: # common
        if roll <= 60: rarity = "common"
        elif roll <= 92: rarity = "uncommon"
        else: rarity = "rare"
    
    item_pool = LOOT_DB[rarity]
    base_item = random.choice(item_pool)
    loot_item = dict(base_item)
    loot_item["id"] = f"item_{random.randint(10000, 99999)}"
    loot_item["rarity"] = rarity
    return loot_item

def generate_monster(player_lv: int, is_boss: bool = False, is_elite: bool = False) -> Dict[str, Any]:
    if is_boss:
        tier = "boss"
        m_lv = player_lv + random.randint(1, 2)
        m_names = [
            ("Lich Lord Malakor", "💀", "Ancient Undead Sorcerer"),
            ("Abyssal Chimera Behemoth", "🦁", "Three-Headed Abyssal Beast"),
            ("Cursed Obsidian Golem", "🗿", "Colossal Enchanted Automaton")
        ]
        chosen = random.choice(m_names)
        hp = 110 + (m_lv * 35)
        atk = 14 + (m_lv * 4)
        exp_reward = m_lv * 120
        gold_reward = random.randint(50, 110)
    elif is_elite:
        tier = "elite"
        m_lv = max(1, player_lv + random.randint(0, 1))
        m_names = [
            ("Crypt Warden Champion", "🛡️", "Armored Skeleton Knight"),
            ("Venomous Broodmother", "🕷️", "Giant Cavern Arachnid"),
            ("Shadowblade Stalker", "🗡️", "Ghostly Assassin")
        ]
        chosen = random.choice(m_names)
        hp = 45 + (m_lv * 18)
        atk = 8 + (m_lv * 3)
        exp_reward = m_lv * 45
        gold_reward = random.randint(15, 35)
    else:
        tier = "common"
        m_lv = max(1, player_lv - random.randint(0, 1))
        m_names = [
            ("Ravenous Cave Rat", "🐀", "Frenzied Rodent"),
            ("Restless Skeleton Grunt", "💀", "Decayed Bone Warrior"),
            ("Tomb Scavenger Goblin", "👺", "Sneaky Trap-Lover"),
            ("Corrosive Slime Mass", "🦠", "Acidic Jelly Organism")
        ]
        chosen = random.choice(m_names)
        hp = 18 + (m_lv * 8)
        atk = 4 + (m_lv * 2)
        exp_reward = m_lv * 15
        gold_reward = random.randint(3, 10)

    return {
        "name": f"{chosen[0]} (Lv.{m_lv})",
        "title": chosen[0],
        "icon": chosen[1],
        "desc": chosen[2],
        "level": m_lv,
        "tier": tier,
        "hp": hp,
        "max_hp": hp,
        "attack": atk,
        "exp_reward": exp_reward,
        "gold_reward": gold_reward,
        "status": "active"
    }

# ==========================================
# EXP PROGRESSION & LEVEL FORMULA (1 - 20)
# ==========================================
def get_required_exp_for_level(level: int) -> int:
    return int(75 * (level ** 1.6))

DEFAULT_GAME_STATE = {
    "status": "character_creation",
    "floor": 1,
    "step": 1,
    "active_sound_theme": "creation",
    "torch_turns": 10,
    "rations": 3,
    "story_history": [],
    "player": {
        "name": "Danas",
        "class_id": "peasant",
        "class_name": "Hardy Peasant",
        "class_icon": "🌾",
        "level": 1,
        "exp": 0,
        "exp_next": 75,
        "hp": 115,
        "max_hp": 115,
        "mp": 15,
        "max_mp": 15,
        "gold": 10,
        "stats": {"str": 14, "dex": 10, "con": 15, "int": 8, "wis": 12, "cha": 8},
        "equipped": {
            "main_hand": None,
            "off_hand": None,
            "armor": None,
            "accessory": None
        },
        "inventory": [], # 25 slot max array
        "skills": [],
        "status_effects": [] # "bleeding", "poisoned", "blind", "cursed"
    },
    "current_node": {
        "type": "entrance", # entrance | exploration | combat | merchant | puzzle | campfire | boss
        "title": "Collapse into the Forgotten Crypt",
        "location": "Subterranean Vault - Floor 1",
        "chapter": "Chapter 1: The Dark Descent"
    },
    "monster": None,
    "merchant_stock": [],
    "scene": {
        "narrative": "Paduka hanyalah seorang warga biasa yang mencari kayu di lereng bukit. Tanah mendadak amblas runtuh! Paduka jatuh terperosok ke dalam rongga makam kuno bawah tanah. Lubang keluar di atas tertutup bebatuan tebal. Di hadapan Paduka, lorong batu berlumut gelap memancarkan hembusan angin dingin purba.",
        "choices": [
            {"id": "A", "text": "Inspect the stone wall & search for weak structural points (Perception / WIS Check - DC 10)", "type": "roll", "dc": 10, "stat": "WIS"},
            {"id": "B", "text": "Use farming tools to clear heavy rubble and force a breach (Athletics / STR Check - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "C", "text": "Light a torch and stealthily navigate the corridor (Stealth / DEX Check - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Take a short rest, catch breath, and inspect inventory (Action)", "type": "action"}
        ],
        "log": ["A commoner's dark fantasy survival journey begins in the underground crypt..."]
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

def compute_total_stats(player: Dict[str, Any]) -> Dict[str, int]:
    base = dict(player["stats"])
    base["atk"] = base["str"] // 2
    base["def"] = base["con"] // 3
    base["crit"] = 5
    base["dodge"] = base["dex"] // 3
    
    eq = player.get("equipped", {})
    for slot, item in eq.items():
        if item and "bonus" in item:
            for k, v in item["bonus"].items():
                base[k] = base.get(k, 0) + v
    return base

def init_new_character(name: str, class_id: str):
    global game_state
    c = CLASSES_INFO.get(class_id, CLASSES_INFO["peasant"])
    game_state["status"] = "playing"
    game_state["floor"] = 1
    game_state["step"] = 1
    game_state["torch_turns"] = 12
    game_state["rations"] = 3
    game_state["active_sound_theme"] = "dungeon"
    game_state["story_history"] = []
    game_state["monster"] = None
    game_state["merchant_stock"] = []
    
    inv_25 = []
    for item in c.get("starting_inventory", []):
        inv_25.append(item)
    while len(inv_25) < 25:
        inv_25.append(None)

    game_state["player"] = {
        "name": name if name.strip() else "Danas",
        "class_id": class_id,
        "class_name": c["title"],
        "class_icon": c["icon"],
        "level": 1,
        "exp": 0,
        "exp_next": get_required_exp_for_level(1),
        "hp": c["base_hp"],
        "max_hp": c["base_hp"],
        "mp": c["base_mp"],
        "max_mp": c["base_mp"],
        "gold": 12,
        "stats": {
            "str": c["str"],
            "dex": c["dex"],
            "con": c["con"],
            "int": c["int"],
            "wis": c["wis"],
            "cha": c["cha"]
        },
        "equipped": json.loads(json.dumps(c.get("equipped", {}))),
        "inventory": inv_25,
        "skills": list(c.get("skills", [])),
        "status_effects": []
    }
    game_state["current_node"] = {
        "type": "exploration",
        "title": "Collapse into the Forgotten Crypt",
        "location": "Subterranean Vault - Floor 1",
        "chapter": "Chapter 1: The Descent"
    }
    game_state["scene"] = {
        "chapter": "Chapter 1: The Descent",
        "title": "Collapse into the Forgotten Crypt",
        "location": "Subterranean Vault - Floor 1",
        "narrative": f"Sang {c['title']}, {game_state['player']['name']}, hanyalah warga biasa yang hidup sederhana di desa. Namun takdir berkata lain: saat sedang mencari kayu di lereng bukit berkabut, tanah di bawah kaki amblas runtuh seketika! Paduka terperosok jatuh ke dalam rongga makam kuno bawah tanah. Lubang keluar di atas tertutup reruntuhan batu besar. Satu-satunya jalan bertahan hidup adalah menembus lorong batu berlumut yang dingin dan gelap di depan mata.",
        "choices": [
            {"id": "A", "text": "Examine the ancient wall runes to decipher structural exits (INT / Arcana Check - DC 10)", "type": "roll", "dc": 10, "stat": "INT"},
            {"id": "B", "text": "Use farming/smithing tools to clear heavy debris (STR / Athletics Check - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
            {"id": "C", "text": "Light a pine pitch torch and stealthily navigate the corridor (DEX / Stealth Check - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
            {"id": "D", "text": "Take a short rest, catch breath, and inspect equipment bag (Action)", "type": "action"}
        ],
        "log": [f"Commoner '{game_state['player']['name']}' ({c['title']}) begins the underground survival journey!"]
    }
    save_game()

# ==========================================
# GRANDMASTER AI PROMPT & STORY GENERATOR
# ==========================================
async def generate_infinite_story(player: Dict[str, Any], current_scene: Dict[str, Any], current_node: Dict[str, Any], monster: Optional[Dict[str, Any]], action_taken: str, roll_result: int, roll_status: str, history: List[str]) -> Dict[str, Any]:
    url = "http://127.0.0.1:20128/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NINE_ROUTER_KEY}"
    }

    system_prompt = """You are Dungeon Master Darsam — an elite, atmospheric Grandmaster TTRPG storyteller for an authentic Dark Fantasy Solo Campaign (Zero to Hero edition).

RULES OF THE SYSTEM:
1. Narrative prose and dialogue MUST be in elegant, sensory-rich Indonesian (address player respectfully as 'Paduka').
2. ALL TECHNICAL, RPG, COMBAT, SPELL, ITEM, AND STAT TERMS MUST BE IN CLEAN STANDARD ENGLISH (e.g. 'STR Check', 'DEX Check', 'INT Check', 'WIS Check', 'CON Check', 'CHA Check', 'DC 12', 'Critical Hit', 'Critical Fail', 'Success', 'Fail', 'Short Rest', 'Poisoned', 'Bleeding', 'Shield Wall', 'Adrenaline Surge').
3. Show, Don't Tell: Rich sensory details (smell of damp sulfur, cold condensation, the scrape of rusted steel).
4. Meaningful Failure (Fail-Forward): Failure never halts the game; it inflicts damage, burns torch turns, alerts foes, or damages equipment.
5. Provide 4 distinct tactical choices (A, B, C, D) with varied mechanics (Physical, Stealth, Mental/Arcane, Item/Rest).
6. Audio Theme Selector: Choose 'dungeon', 'danger', 'mystery', or 'suspense'.
7. Output MUST BE PURE VALID JSON only.

JSON SCHEMA:
{
  "chapter": "Chapter X: Title",
  "location": "Room / Chamber Name",
  "title": "Scene Encounter Title",
  "node_type": "exploration" | "combat" | "merchant" | "puzzle" | "campfire" | "boss",
  "outcome_summary": "1-2 concise Indonesian sentences explaining the immediate impact of the player's action (using English technical terms).",
  "narrative": "3-5 rich, immersive Indonesian sentences describing the new situation.",
  "audio_theme": "dungeon" | "danger" | "mystery",
  "hp_change": 0, // negative for damage (-5 to -25), positive for heal
  "mp_change": 0,
  "gold_change": 0,
  "monster_encounter": { // null if no monster in this scene
    "name": "Monster Name",
    "tier": "common" | "elite" | "boss",
    "level": 1
  },
  "choices": [
    {"id": "A", "text": "Action description (STR Check - DC 12)", "type": "roll", "stat": "STR", "dc": 12},
    {"id": "B", "text": "Action description (DEX Check - DC 11)", "type": "roll", "stat": "DEX", "dc": 11},
    {"id": "C", "text": "Action description (INT Check - DC 10)", "type": "roll", "stat": "INT", "dc": 10},
    {"id": "D", "text": "Tactical action / Use item / Rest (Action)", "type": "action"}
  ]
}"""

    equipped_names = [f"{k}: {v['name']}" for k, v in player.get('equipped', {}).items() if v]
    inv_count = len([x for x in player.get('inventory', []) if x])
    
    user_prompt = f"""CHARACTER PROFILE:
- Name: {player['name']} | Origin: {player['class_name']} | Level: {player['level']} (EXP: {player['exp']}/{player['exp_next']})
- Vitals: HP {player['hp']}/{player['max_hp']} | MP {player['mp']}/{player['max_mp']} | Gold: {player['gold']} G
- Stats: STR {player['stats']['str']} | DEX {player['stats']['dex']} | CON {player['stats']['con']} | INT {player['stats']['int']} | WIS {player['stats']['wis']} | CHA {player['stats']['cha']}
- Equipped: {', '.join(equipped_names) if equipped_names else 'None'}
- Inventory: {inv_count}/25 slots used
- Status Ailments: {', '.join(player.get('status_effects', [])) if player.get('status_effects') else 'Healthy'}

CURRENT CONTEXT:
- Chapter & Location: {current_scene.get('chapter')} - {current_scene.get('location')} (Node Type: {current_node.get('type')})
- Encounter: {current_scene.get('title')}
- Narrative: {current_scene.get('narrative')}
- Active Monster: {monster['name'] if monster else 'None'}

ACTION TAKEN BY PLAYER:
- Choice/Action: "{action_taken}"
- D20 Dice Roll: {roll_result} (Status: {roll_status})

CHRONICLE LOG:
{chr(10).join(history[-3:]) if history else "- Just collapsed into the subterranean crypt."}

Generate the next immersive chapter of this dark fantasy dungeon crawl!"""

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
        if clean_json.startswith("```json"): clean_json = clean_json[7:]
        if clean_json.startswith("```"): clean_json = clean_json[3:]
        if clean_json.endswith("```"): clean_json = clean_json[:-3]
        clean_json = clean_json.strip()
        return json.loads(clean_json)

    except Exception as e:
        print("LLM Fallback triggered:", e)
        is_success = roll_result >= 10 if roll_result > 0 else True
        dmg = random.randint(8, 16) if not is_success else 0
        return {
            "chapter": current_scene.get("chapter", "Chapter 1: The Dark Corridor"),
            "location": "Subterranean Vault - Floor 1",
            "title": "Echoing Stone Chambers",
            "node_type": "exploration",
            "outcome_summary": f"D20 Roll ({roll_result}): {'Aksi Paduka berhasil mengatasi rintangan!' if is_success else 'Paduka tergores pecahan batu tajam dan menerima damage!'}",
            "narrative": "Tetesan air dingin menggema di lorong batu obsidian. Bau lumut purba menyelimuti udara. Di hadapan Paduka, sebuah pintu batu berukir lambang kerajaan kuno memancarkan pendar cahaya keemasan redup.",
            "audio_theme": "dungeon",
            "hp_change": -dmg,
            "mp_change": 0,
            "gold_change": 0,
            "choices": [
                {"id": "A", "text": "Force open the reinforced stone gate (STR Check - DC 11)", "type": "roll", "stat": "STR", "dc": 11},
                {"id": "B", "text": "Examine the glowing lock mechanism (INT / Arcana Check - DC 10)", "type": "roll", "stat": "INT", "dc": 10},
                {"id": "C", "text": "Search for a concealed bypass passage (Perception / WIS Check - DC 9)", "type": "roll", "stat": "WIS", "dc": 9},
                {"id": "D", "text": "Consume dry rations & rest to restore Health (Action)", "type": "action"}
            ]
        }

async def process_live_turn(choice_id: str, choice_text: str = "", custom_text: str = "", roll_val: int = 0) -> Dict[str, Any]:
    global game_state
    p = game_state["player"]
    scene = game_state["scene"]
    node = game_state["current_node"]
    active_m = game_state.get("monster")
    
    game_state["step"] = game_state.get("step", 0) + 1
    
    # Torch degradation
    if game_state["torch_turns"] > 0:
        game_state["torch_turns"] -= 1
        if game_state["torch_turns"] == 0:
            if "blind" not in p["status_effects"]:
                p["status_effects"].append("blind")
    
    action_description = custom_text if custom_text else choice_text
    roll_status = "Direct Action"
    if roll_val > 0:
        if roll_val >= 20: roll_status = "CRITICAL SUCCESS"
        elif roll_val == 1: roll_status = "CRITICAL FAIL"
        elif roll_val >= 10: roll_status = "SUCCESS"
        else: roll_status = "FAIL"

    # AI Turn Generation
    ai_resp = await generate_infinite_story(
        player=p,
        current_scene=scene,
        current_node=node,
        monster=active_m,
        action_taken=action_description,
        roll_result=roll_val,
        roll_status=roll_status,
        history=game_state.get("story_history", [])
    )

    # Combat Resolution if Monster is active
    loot_dropped = None
    exp_gained = 0
    if active_m and active_m.get("status") == "active":
        if roll_status in ["CRITICAL SUCCESS", "SUCCESS"]:
            # Player hits monster
            total_stats = compute_total_stats(p)
            base_dmg = total_stats.get("atk", 4) + random.randint(4, 10)
            if roll_status == "CRITICAL SUCCESS": base_dmg = int(base_dmg * 2.0)
            
            active_m["hp"] = max(0, active_m["hp"] - base_dmg)
            if active_m["hp"] == 0:
                active_m["status"] = "defeated"
                exp_gained = active_m["exp_reward"]
                p["gold"] += active_m["gold_reward"]
                loot_dropped = roll_loot(active_m["tier"], active_m["level"])
                # Add loot to inventory
                added_to_inv = False
                for i in range(len(p["inventory"])):
                    if p["inventory"][i] is None:
                        p["inventory"][i] = loot_dropped
                        added_to_inv = True
                        break
                game_state["monster"] = None
        else:
            # Monster attacks player
            m_dmg = max(1, active_m["attack"] - compute_total_stats(p).get("def", 0))
            p["hp"] = max(0, p["hp"] - m_dmg)

    # Apply Vitals Changes from Story
    hp_diff = ai_resp.get("hp_change", 0)
    p["hp"] = max(0, min(p["max_hp"], p["hp"] + hp_diff))
    p["mp"] = max(0, min(p["max_mp"], p["mp"] + ai_resp.get("mp_change", 0)))
    p["gold"] = max(0, p["gold"] + ai_resp.get("gold_change", 0))

    # Spawn new monster if requested by AI and not in combat
    if not game_state.get("monster") and ai_resp.get("monster_encounter"):
        m_info = ai_resp["monster_encounter"]
        is_boss = m_info.get("tier") == "boss"
        is_elite = m_info.get("tier") == "elite"
        game_state["monster"] = generate_monster(p["level"], is_boss=is_boss, is_elite=is_elite)

    # Level Up Progression
    p["exp"] += exp_gained
    leveled_up = False
    while p["exp"] >= p["exp_next"] and p["level"] < 20:
        p["level"] += 1
        p["exp"] -= p["exp_next"]
        p["exp_next"] = get_required_exp_for_level(p["level"])
        p["max_hp"] += 15
        p["hp"] = p["max_hp"]
        p["max_mp"] += 8
        p["mp"] = p["max_mp"]
        # Stat increase
        p["stats"]["str"] += 1
        p["stats"]["con"] += 1
        leveled_up = True

    # Audio Theme
    game_state["active_sound_theme"] = ai_resp.get("audio_theme", "dungeon")

    # Outcome Log Construction
    outcome = f"🎲 [{roll_status}] {ai_resp.get('outcome_summary', '')}"
    if exp_gained > 0: outcome += f" (+{exp_gained} EXP, +{active_m['gold_reward']} Gold)"
    if loot_dropped: outcome += f" 💎 LOOT DROP: [{loot_dropped['rarity'].upper()}] {loot_dropped['name']}!"
    if hp_diff < 0: outcome += f" (-{-hp_diff} HP)"
    if leveled_up: outcome += f" 🌟 LEVEL UP! Paduka naik ke Level {p['level']} (Max HP/MP meningkat & HP pulih penuh)!"

    # Update Scene State
    game_state["scene"]["chapter"] = ai_resp.get("chapter", scene.get("chapter"))
    game_state["scene"]["title"] = ai_resp.get("title", "Dungeon Chamber")
    game_state["scene"]["location"] = ai_resp.get("location", scene.get("location"))
    game_state["scene"]["narrative"] = ai_resp.get("narrative", "Suasana gua semakin pekat...")
    game_state["scene"]["choices"] = ai_resp.get("choices", scene.get("choices"))
    game_state["current_node"]["type"] = ai_resp.get("node_type", "exploration")
    game_state["scene"]["log"].append(outcome)
    if len(game_state["scene"]["log"]) > 4: game_state["scene"]["log"].pop(0)

    # Save to storage
    save_game()

    return {
        "type": "state_update",
        "outcome": outcome,
        "state": game_state
    }

# ==========================================
# INVENTORY & EQUIPMENT ACTIONS
# ==========================================
def equip_item(item_index: int):
    global game_state
    p = game_state["player"]
    if item_index < 0 or item_index >= len(p["inventory"]): return
    item = p["inventory"][item_index]
    if not item or item.get("type") not in ["weapon", "offhand", "armor", "accessory"]: return
    
    slot = item.get("slot")
    if not slot or slot not in p["equipped"]: return

    old_equipped = p["equipped"][slot]
    p["equipped"][slot] = item
    p["inventory"][item_index] = old_equipped
    save_game()

def unequip_item(slot_name: str):
    global game_state
    p = game_state["player"]
    if slot_name not in p["equipped"] or not p["equipped"][slot_name]: return
    
    # Find free inventory slot
    free_idx = -1
    for i in range(len(p["inventory"])):
        if p["inventory"][i] is None:
            free_idx = i
            break
    if free_idx == -1: return # Inventory full!

    p["inventory"][free_idx] = p["equipped"][slot_name]
    p["equipped"][slot_name] = None
    save_game()

def use_consumable(item_index: int):
    global game_state
    p = game_state["player"]
    if item_index < 0 or item_index >= len(p["inventory"]): return
    item = p["inventory"][item_index]
    if not item or item.get("type") != "consumable": return

    eff = item.get("effect", "")
    if eff.startswith("heal_hp_"):
        amount = int(eff.split("_")[-1])
        p["hp"] = min(p["max_hp"], p["hp"] + amount)
    elif eff.startswith("heal_mp_"):
        amount = int(eff.split("_")[-1])
        p["mp"] = min(p["max_mp"], p["mp"] + amount)
    elif eff == "add_light_5":
        game_state["torch_turns"] += 6
        if "blind" in p["status_effects"]: p["status_effects"].remove("blind")
    elif eff == "full_restore":
        p["hp"] = p["max_hp"]
        p["mp"] = p["max_mp"]
        p["status_effects"] = []
    
    # Remove consumed item
    p["inventory"][item_index] = None
    save_game()

# ==========================================
# FASTAPI ROUTES & WEBSOCKETS
# ==========================================
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

            elif action_type == "equip_item":
                item_idx = data.get("index")
                equip_item(item_idx)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Perlengkapan berhasil dipasang!"})

            elif action_type == "unequip_item":
                slot_name = data.get("slot")
                unequip_item(slot_name)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Perlengkapan dilepas ke tas!"})

            elif action_type == "use_item":
                item_idx = data.get("index")
                use_consumable(item_idx)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Item konsumsi berhasil digunakan!"})

            elif action_type == "reset_game":
                game_state.clear()
                game_state.update(json.loads(json.dumps(DEFAULT_GAME_STATE)))
                game_state["status"] = "character_creation"
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Game di-reset ke Ruang Asal-Usul Karakter."})

    except WebSocketDisconnect:
        await manager.disconnect_controller(websocket)
