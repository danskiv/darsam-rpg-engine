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

app = FastAPI(title="Darsam RPG Dungeon Engine - Grandmaster v2.0.0")

os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/static", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/templates", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/saves", exist_ok=True)
os.makedirs("/home/ubuntu/Github/darsam-rpg-engine/docs", exist_ok=True)

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

# =========================================================================
# 8 DIVERSE STARTING ORIGINS (ZERO TO HERO) WITH 6-SLOT INITIAL GEAR
# =========================================================================
CLASSES_INFO = {
    "peasant": {
        "title": "Hardy Peasant", "icon": "🌾", "tier": "common",
        "desc": "Petani tangguh berotot liat. Bertahan hidup dengan stamina alamiah, ketabahan mental, dan insting tanah liat.",
        "base_hp": 115, "base_mp": 15, "str": 14, "dex": 10, "con": 15, "int": 8, "wis": 12, "cha": 8,
        "equipped": {
            "head": {"id": "h_straw", "name": "Weathered Straw Hat", "rarity": "common", "type": "head", "slot": "head", "icon": "👒", "bonus": {"wis": 1}, "val": 2},
            "armor": {"id": "a_linen", "name": "Homespun Tunic", "rarity": "common", "type": "armor", "slot": "armor", "icon": "👕", "bonus": {"hp": 5, "def": 1}, "val": 2},
            "feet": {"id": "f_sandals", "name": "Woven Straw Sandals", "rarity": "common", "type": "feet", "slot": "feet", "icon": "👡", "bonus": {"dodge": 2}, "val": 2},
            "accessory": None,
            "main_hand": {"id": "w_hoe", "name": "Rusty Farming Hoe", "rarity": "common", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "⛏️", "bonus": {"str": 1, "atk": 4}, "val": 3},
            "off_hand": None
        },
        "starting_inventory": [
            {"id": "c_ration_1", "name": "Dry Ration Bread", "rarity": "common", "type": "consumable", "icon": "🍞", "effect": "heal_hp_25", "desc": "Restores 25 HP", "val": 2},
            {"id": "c_ration_2", "name": "Dry Ration Bread", "rarity": "common", "type": "consumable", "icon": "🍞", "effect": "heal_hp_25", "desc": "Restores 25 HP", "val": 2},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3},
            {"id": "m_rope", "name": "Hemp Rope (15m)", "rarity": "common", "type": "material", "icon": "🪢", "desc": "Utility rope for climbing", "val": 2}
        ],
        "initial_skills": [
            {"id": "sk_adrenaline", "name": "Adrenaline Surge", "cost_mp": 5, "cd": 3, "dmg_type": "heal", "est_val": "+25 HP & +2 STR", "desc": "Memulihkan 25 HP seketika & memberi bonus +2 STR selama 2 turn."}
        ],
        "level_unlocks": {
            5: {"id": "sk_reaper", "name": "Reaper's Harvest Sweep", "cost_mp": 10, "cd": 2, "dmg_type": "damage", "est_val": "35-48 Area DMG", "desc": "Ayunan sabit luas yang menebas musuh dengan kekuatan penuh (35-48 DMG)."},
            10: {"id": "sk_titan_soil", "name": "Titan of the Soil", "cost_mp": 15, "cd": 4, "dmg_type": "buff", "est_val": "+50 Max HP & Invuln", "desc": "Menyerap energi bumi: kebal damage 1 turn dan menambah +50 Max HP."}
        }
    },
    "blacksmith": {
        "title": "Smith Apprentice", "icon": "🔨", "tier": "common",
        "desc": "Magang bengkel tempa desa. Lengan kokoh terbiasa memukul baja panas, paham titik lemah struktur logam & batu.",
        "base_hp": 125, "base_mp": 10, "str": 16, "dex": 9, "con": 14, "int": 9, "wis": 10, "cha": 8,
        "equipped": {
            "head": {"id": "h_band", "name": "Sweat-Soaked Headband", "rarity": "common", "type": "head", "slot": "head", "icon": "🎽", "bonus": {"con": 1}, "val": 2},
            "armor": {"id": "a_apron", "name": "Thick Leather Apron", "rarity": "common", "type": "armor", "slot": "armor", "icon": "🦺", "bonus": {"con": 1, "def": 2}, "val": 5},
            "feet": {"id": "f_boots", "name": "Iron-Toed Work Boots", "rarity": "common", "type": "feet", "slot": "feet", "icon": "👢", "bonus": {"def": 1}, "val": 4},
            "accessory": None,
            "main_hand": {"id": "w_smith_hammer", "name": "Heavy Smith Hammer", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "handedness": "main_hand_only", "icon": "🔨", "bonus": {"str": 2, "atk": 6}, "val": 8},
            "off_hand": None
        },
        "starting_inventory": [
            {"id": "m_spikes", "name": "Iron Spikes (x5)", "rarity": "common", "type": "material", "icon": "🔩", "desc": "Wedge doors or climb walls", "val": 3},
            {"id": "m_whetstone", "name": "Smith Whetstone", "rarity": "common", "type": "consumable", "icon": "🪨", "effect": "buff_atk_2", "desc": "+2 ATK on equipped weapon", "val": 4},
            {"id": "c_ration_1", "name": "Smoked Meat Jerky", "rarity": "common", "type": "consumable", "icon": "🥩", "effect": "heal_hp_25", "desc": "Restores 25 HP", "val": 3},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3}
        ],
        "initial_skills": [
            {"id": "sk_anvil", "name": "Anvil Crush", "cost_mp": 5, "cd": 3, "dmg_type": "damage", "est_val": "22-30 Blunt DMG", "desc": "Menghantam monster dengan palu berat (22-30 DMG) dan melumpuhkan (Stun) 1 turn."}
        ],
        "level_unlocks": {
            5: {"id": "sk_furnace", "name": "Furnace Overheat Blast", "cost_mp": 12, "cd": 3, "dmg_type": "damage", "est_val": "40-55 Fire DMG", "desc": "Menyalakan amarah bara tempa, membakar musuh dengan semburan api (40-55 DMG)."},
            10: {"id": "sk_colossus_forge", "name": "Colossus Forge Hammer", "cost_mp": 20, "cd": 4, "dmg_type": "damage", "est_val": "75-95 Sunder DMG", "desc": "Hantaman raksasa yang menghancurkan zirah monster dan menghasilkan damage luar biasa."}
        }
    },
    "scholar": {
        "title": "Village Scholar", "icon": "📜", "tier": "common",
        "desc": "Asisten tabib dan pembaca naskah tua. Fisik ringkih namun cerdas mengurai ancient runes dan ramuan herbal.",
        "base_hp": 85, "base_mp": 60, "str": 7, "dex": 11, "con": 10, "int": 16, "wis": 14, "cha": 10,
        "equipped": {
            "head": {"id": "h_hood", "name": "Scholar Scholar's Cowl", "rarity": "common", "type": "head", "slot": "head", "icon": "🧙", "bonus": {"int": 1, "mp": 10}, "val": 4},
            "armor": {"id": "a_robe", "name": "Scholar Travel Robes", "rarity": "common", "type": "armor", "slot": "armor", "icon": "👘", "bonus": {"mp": 15, "def": 1}, "val": 4},
            "feet": {"id": "f_shoes", "name": "Soft Cloth Slippers", "rarity": "common", "type": "feet", "slot": "feet", "icon": "👞", "bonus": {"dodge": 2}, "val": 2},
            "accessory": None,
            "main_hand": {"id": "w_carver", "name": "Silver Lore Scalpel", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "🗡️", "bonus": {"int": 1, "atk": 3}, "val": 7},
            "off_hand": {"id": "o_diary", "name": "Ancient Herbarium Grimoire", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "📖", "bonus": {"wis": 1, "int": 1}, "val": 8}
        },
        "starting_inventory": [
            {"id": "c_salve_1", "name": "Herbal Healing Salve", "rarity": "uncommon", "type": "consumable", "icon": "🧪", "effect": "heal_hp_40", "desc": "Restores 40 HP & cures Bleeding", "val": 6},
            {"id": "c_salve_2", "name": "Herbal Healing Salve", "rarity": "uncommon", "type": "consumable", "icon": "🧪", "effect": "heal_hp_40", "desc": "Restores 40 HP & cures Bleeding", "val": 6},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3},
            {"id": "m_chalk", "name": "Alchemical Rune Chalk", "rarity": "common", "type": "material", "icon": "🖍️", "desc": "Inscribe protective glyphs", "val": 3}
        ],
        "initial_skills": [
            {"id": "sk_arcane_spark", "name": "Arcane Spark", "cost_mp": 10, "cd": 1, "dmg_type": "damage", "est_val": "25-36 Magic DMG", "desc": "Menembakkan petir sihir murni (25-36 DMG) yang menembus armor monster."}
        ],
        "level_unlocks": {
            5: {"id": "sk_chain_lightning", "name": "Thunderstorm Chain", "cost_mp": 20, "cd": 2, "dmg_type": "damage", "est_val": "45-60 Lightning DMG", "desc": "Mantra badai petir berantai yang melompat menyengat musuh bertubi-tubi."},
            10: {"id": "sk_astral_rift", "name": "Astral Void Singularity", "cost_mp": 35, "cd": 4, "dmg_type": "damage", "est_val": "85-110 Void DMG", "desc": "Membuka robekan dimensi kehampaan yang menelan monster dalam kehancuran total."}
        }
    },
    "trapper": {
        "title": "Forest Trapper", "icon": "🏹", "tier": "common",
        "desc": "Pemburu satwa lereng bukit berkabut. Langkah hening tanpa jejak, awas jebakan, dan ahli membidik di kegelapan.",
        "base_hp": 95, "base_mp": 25, "str": 10, "dex": 16, "con": 11, "int": 10, "wis": 14, "cha": 8,
        "equipped": {
            "head": {"id": "h_cap", "name": "Stalker Camo Cap", "rarity": "common", "type": "head", "slot": "head", "icon": "🧢", "bonus": {"dex": 1}, "val": 3},
            "armor": {"id": "a_camo", "name": "Camouflage Pelt Vest", "rarity": "common", "type": "armor", "slot": "armor", "icon": "🦺", "bonus": {"dex": 1, "def": 1}, "val": 5},
            "feet": {"id": "f_stalker", "name": "Silent Stalker Moccasins", "rarity": "uncommon", "type": "feet", "slot": "feet", "icon": "👟", "bonus": {"dodge": 4, "dex": 1}, "val": 6},
            "accessory": None,
            "main_hand": {"id": "w_bow", "name": "Yew Shortbow", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "handedness": "two_handed", "icon": "🏹", "bonus": {"dex": 2, "atk": 7}, "val": 10},
            "off_hand": None
        },
        "starting_inventory": [
            {"id": "c_snare", "name": "Serrated Wire Snare", "rarity": "uncommon", "type": "consumable", "icon": "🪤", "effect": "trap_bleed", "desc": "Deals 25 damage & immobilizes foe", "val": 6},
            {"id": "c_torch_1", "name": "Resin Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3},
            {"id": "c_ration_1", "name": "Dried Game Rations", "rarity": "common", "type": "consumable", "icon": "🥩", "effect": "heal_hp_25", "desc": "Restores 25 HP", "val": 2},
            {"id": "m_dagger", "name": "Flint Skinning Knife", "rarity": "common", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "🔪", "bonus": {"dex": 1, "atk": 3}, "val": 3}
        ],
        "initial_skills": [
            {"id": "sk_caltrop", "name": "Caltrop Scatter", "cost_mp": 8, "cd": 2, "dmg_type": "damage", "est_val": "18-24 Bleed DMG", "desc": "Menebar duri beracun (18-24 DMG) yang melukai dan memperlambat musuh."}
        ],
        "level_unlocks": {
            5: {"id": "sk_headshot", "name": "Precision Heartseeker Shot", "cost_mp": 15, "cd": 2, "dmg_type": "damage", "est_val": "45-60 Piercing DMG", "desc": "Tembakan panah mematikan tepat ke titik vital monster."},
            10: {"id": "sk_phantom_volley", "name": "Phantom Arrowstorm", "cost_mp": 25, "cd": 3, "dmg_type": "damage", "est_val": "80-105 Barrage DMG", "desc": "Hujan ratusan anak panah berbayang yang menyapu bersih seluruh monster."}
        }
    },
    "guard": {
        "title": "Disgraced Watchman", "icon": "🛡️", "tier": "common",
        "desc": "Mantan penjaga gerbang kota yang terbuang. Terbiasa menahan benturan tameng dan pertarungan jarak dekat.",
        "base_hp": 120, "base_mp": 15, "str": 15, "dex": 11, "con": 14, "int": 8, "wis": 10, "cha": 9,
        "equipped": {
            "head": {"id": "h_iron", "name": "Dented Iron Sallet", "rarity": "common", "type": "head", "slot": "head", "icon": "🪖", "bonus": {"def": 1}, "val": 3},
            "armor": {"id": "a_chain", "name": "Tattered Chain Shirt", "rarity": "uncommon", "type": "armor", "slot": "armor", "icon": "🥋", "bonus": {"def": 3, "hp": 10}, "val": 9},
            "feet": {"id": "f_greaves", "name": "Iron Shin Greaves", "rarity": "common", "type": "feet", "slot": "feet", "icon": "👢", "bonus": {"def": 1}, "val": 4},
            "accessory": None,
            "main_hand": {"id": "w_sword", "name": "Notched Iron Broadsword", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "handedness": "main_hand_only", "icon": "⚔️", "bonus": {"str": 2, "atk": 5}, "val": 8},
            "off_hand": {"id": "o_shield", "name": "Reinforced Oak Buckler", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "🛡️", "bonus": {"def": 3, "con": 1}, "val": 7}
        },
        "starting_inventory": [
            {"id": "c_bandage", "name": "Sterile Cloth Bandage", "rarity": "common", "type": "consumable", "icon": "🩹", "effect": "cure_bleed_heal_15", "desc": "Stops Bleeding & heals 15 HP", "val": 3},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3},
            {"id": "c_ration_1", "name": "Hardtack Biscuit", "rarity": "common", "type": "consumable", "icon": "🍘", "effect": "heal_hp_25", "desc": "Restores 25 HP", "val": 2}
        ],
        "initial_skills": [
            {"id": "sk_shield_wall", "name": "Shield Wall Bastion", "cost_mp": 6, "cd": 3, "dmg_type": "buff", "est_val": "+6 DEF & Reflect", "desc": "Meningkatkan DEF sebesar +6 dan memantulkan 50% serangan melee musuh."}
        ],
        "level_unlocks": {
            5: {"id": "sk_guard_slam", "name": "Bulwark Heavy Shield Slam", "cost_mp": 12, "cd": 2, "dmg_type": "damage", "est_val": "35-45 Stun DMG", "desc": "Benturan perisai baja berat yang meremukkan musuh dan memberi efek Stun."},
            10: {"id": "sk_unyielding_king", "name": "Unyielding Legion Sovereign", "cost_mp": 20, "cd": 4, "dmg_type": "buff", "est_val": "100% Counter & +12 DEF", "desc": "Ksatria tak terkalahkan: Menangkis seluruh serangan dan membalas dengan Critical Hit."}
        }
    },
    "grave_robber": {
        "title": "Tomb Grave-Robber", "icon": "🕯️", "tier": "common",
        "desc": "Penyusup liang kubur yang serakah. Ahli membobol gembok kuno, mencari jebakan rahasia, dan menyerang dari bayangan.",
        "base_hp": 90, "base_mp": 30, "str": 9, "dex": 16, "con": 11, "int": 13, "wis": 11, "cha": 12,
        "equipped": {
            "head": {"id": "h_mask", "name": "Silk Thief Veil", "rarity": "common", "type": "head", "slot": "head", "icon": "🎭", "bonus": {"dex": 1}, "val": 3},
            "armor": {"id": "a_cloak", "name": "Shadowed Scavenger Cloak", "rarity": "common", "type": "armor", "slot": "armor", "icon": "🧥", "bonus": {"dex": 1, "def": 1}, "val": 5},
            "feet": {"id": "f_soft", "name": "Padded Leather Boots", "rarity": "common", "type": "feet", "slot": "feet", "icon": "👢", "bonus": {"dodge": 3}, "val": 4},
            "accessory": {"id": "acc_lucky_coin", "name": "Gilded Luck Charm", "rarity": "rare", "type": "accessory", "slot": "accessory", "icon": "🪙", "bonus": {"cha": 2, "gold_drop": 15}, "val": 15},
            "main_hand": {"id": "w_stiletto", "name": "Rusty Stiletto Dagger", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "🗡️", "bonus": {"dex": 2, "atk": 4}, "val": 7},
            "off_hand": {"id": "o_lockpick", "name": "Master Thieves' Tools", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "🗝️", "bonus": {"dex": 1, "cha": 1}, "val": 8}
        },
        "starting_inventory": [
            {"id": "c_smokebomb", "name": "Sulfur Smoke Vial", "rarity": "uncommon", "type": "consumable", "icon": "💨", "effect": "escape_guarantee", "desc": "100% Escape chance from any fight", "val": 8},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3},
            {"id": "m_crowbar", "name": "Iron Prying Crowbar", "rarity": "common", "type": "material", "icon": "🦯", "desc": "Pries open sarcophagi & stuck grates", "val": 4}
        ],
        "initial_skills": [
            {"id": "sk_backstab", "name": "Shadow Ambush", "cost_mp": 10, "cd": 2, "dmg_type": "damage", "est_val": "28-42 Crit DMG", "desc": "Menyerang dari balik bayangan (28-42 DMG) dengan garansi Critical Hit."}
        ],
        "level_unlocks": {
            5: {"id": "sk_shadow_step", "name": "Shadowstep Assassinate", "cost_mp": 18, "cd": 2, "dmg_type": "damage", "est_val": "50-70 Stealth DMG", "desc": "Teleportasi sekejap ke belakang monster dan menebas lehernya secara senyap."},
            10: {"id": "sk_dance_of_death", "name": "Seven Phantoms Death Dance", "cost_mp": 30, "cd": 4, "dmg_type": "damage", "est_val": "90-120 Burst DMG", "desc": "Tarian 7 tusukan belati bayangan kilat yang merobek target seketika."}
        }
    },
    "monk": {
        "title": "Exiled Temple Acolyte", "icon": "⛪", "tier": "common",
        "desc": "Murid kuil suci yang diasingkan. Memiliki keteguhan batin, doa mukjizat perlindungan, dan kemahiran tongkat bela diri.",
        "base_hp": 105, "base_mp": 45, "str": 11, "dex": 12, "con": 13, "int": 10, "wis": 16, "cha": 12,
        "equipped": {
            "head": {"id": "h_circlet", "name": "Braided Bamboo Circlet", "rarity": "common", "type": "head", "slot": "head", "icon": "👑", "bonus": {"wis": 1}, "val": 3},
            "armor": {"id": "a_cassock", "name": "Pilgrim Cassock", "rarity": "common", "type": "armor", "slot": "armor", "icon": "🥋", "bonus": {"wis": 1, "def": 1}, "val": 4},
            "feet": {"id": "f_straw_monk", "name": "Temple Straw Sandals", "rarity": "common", "type": "feet", "slot": "feet", "icon": "👡", "bonus": {"dodge": 3}, "val": 2},
            "accessory": None,
            "main_hand": {"id": "w_staff", "name": "Polished Ash Quarterstaff", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "🦯", "bonus": {"wis": 2, "atk": 4}, "val": 7},
            "off_hand": {"id": "o_beads", "name": "Sandalwood Prayer Beads", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "📿", "bonus": {"wis": 1, "mp": 15}, "val": 8}
        },
        "starting_inventory": [
            {"id": "c_holy_water", "name": "Blessed Holy Water", "rarity": "uncommon", "type": "consumable", "icon": "🏺", "effect": "cure_curse_heal_30", "desc": "Cleanses Curse/Poison & heals 30 HP", "val": 7},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3},
            {"id": "c_ration_1", "name": "Dried Figs & Nuts", "rarity": "common", "type": "consumable", "icon": "🥜", "effect": "heal_hp_25", "desc": "Restores 25 HP & 10 MP", "val": 3}
        ],
        "initial_skills": [
            {"id": "sk_mend", "name": "Sacred Prayer of Radiance", "cost_mp": 12, "cd": 2, "dmg_type": "heal", "est_val": "+35 HP & Blind", "desc": "Memulihkan 35 HP dan membutakan musuh mayat hidup selama 1 turn."}
        ],
        "level_unlocks": {
            5: {"id": "sk_smite", "name": "Divine Wrath Palm Smite", "cost_mp": 18, "cd": 2, "dmg_type": "damage", "est_val": "45-65 Holy DMG", "desc": "Pukulan telapak tangan bertenaga surya suci yang membakar monster kegelapan."},
            10: {"id": "sk_nirvana", "name": "Celestial Avatar of Nirvana", "cost_mp": 35, "cd": 4, "dmg_type": "buff", "est_val": "Full Heal & +80 Holy Strike", "desc": "Wujud dewa matahari: Memulihkan 100% HP dan menghantam musuh dengan sinar samudra suci."}
        }
    },
    "alchemist": {
        "title": "Alchemist Apprentice", "icon": "🧪", "tier": "common",
        "desc": "Pencampur ramuan berbahaya yang diusir dari kota. Terbiasa meracik cairan asam, minyak peledak, dan eliksir ajaib.",
        "base_hp": 85, "base_mp": 50, "str": 8, "dex": 13, "con": 11, "int": 16, "wis": 12, "cha": 9,
        "equipped": {
            "head": {"id": "h_goggles", "name": "Brass Tinted Goggles", "rarity": "uncommon", "type": "head", "slot": "head", "icon": "🥽", "bonus": {"int": 1, "wis": 1}, "val": 6},
            "armor": {"id": "a_treated", "name": "Acid-Treated Leather Jerkin", "rarity": "uncommon", "type": "armor", "slot": "armor", "icon": "🦺", "bonus": {"con": 1, "def": 2}, "val": 7},
            "feet": {"id": "f_rubber", "name": "Chemical-Resistant Boots", "rarity": "common", "type": "feet", "slot": "feet", "icon": "👢", "bonus": {"def": 1}, "val": 4},
            "accessory": None,
            "main_hand": {"id": "w_pestle", "name": "Brass Mortar & Pestle Club", "rarity": "uncommon", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "🪓", "bonus": {"int": 1, "atk": 3}, "val": 6},
            "off_hand": {"id": "o_flask", "name": "Volatile Acid Catalyst Flask", "rarity": "uncommon", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "🧪", "bonus": {"int": 2}, "val": 9}
        },
        "starting_inventory": [
            {"id": "c_fire_flask", "name": "Flask of Wildfire Oil", "rarity": "uncommon", "type": "consumable", "icon": "🔥", "effect": "damage_fire_35", "desc": "Deals 35 Fire DMG to target monster", "val": 8},
            {"id": "c_antidote", "name": "Universal Antidote Draught", "rarity": "uncommon", "type": "consumable", "icon": "🧪", "effect": "cure_poison_heal_25", "desc": "Cures Poison & restores 25 HP", "val": 5},
            {"id": "c_torch_1", "name": "Pine Pitch Torch", "rarity": "common", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3}
        ],
        "initial_skills": [
            {"id": "sk_acid_throw", "name": "Corrosive Acid Bomb", "cost_mp": 10, "cd": 2, "dmg_type": "damage", "est_val": "24-32 Acid DMG", "desc": "Melelehkan zirah monster (-4 DEF) dan memberi 24-32 luka asam."}
        ],
        "level_unlocks": {
            5: {"id": "sk_magma_flask", "name": "Volcanic Hellfire Flask", "cost_mp": 18, "cd": 2, "dmg_type": "damage", "est_val": "50-65 Fire Burn", "desc": "Ledakan magma dahsyat yang membakar musuh terus-menerus."},
            10: {"id": "sk_philosopher_nova", "name": "Philosopher's Transmutation Nova", "cost_mp": 35, "cd": 4, "dmg_type": "damage", "est_val": "95-130 Pure DMG", "desc": "Transmutasi atomik murni yang merombak struktur fisik musuh menjadi debu emas."}
        }
    }
}

# =========================================================================
# SECRET AWAKENING JOBS (SPECIAL, EPIC, LEGENDARY, MYTHIC)
# =========================================================================
SECRET_CLASSES_DB = {
    "special": [
        {"id": "sec_blood_zealot", "title": "Blood-Pact Zealot", "tier": "special", "icon": "🩸", "bonus_stats": {"str": 3, "con": 2}, "desc": "Ksatria kultus darah. Mengorbankan darah sendiri demi serangan fisik berlipat ganda.", "skills": [{"id": "sk_blood_strike", "name": "Sanguine Cleave", "cost_mp": 5, "dmg_type": "damage", "est_val": "45-60 Blood DMG", "desc": "Mengorbankan 10 HP untuk menebas monster dengan 45-60 damage brutal."}]},
        {"id": "sec_shadow_ranger", "title": "Shadowveil Ranger", "tier": "special", "icon": "🏹", "bonus_stats": {"dex": 4, "wis": 2}, "desc": "Pemanah malam berkabut. Tembakan panahnya tidak terdengar dan selalu menusuk titik lemah.", "skills": [{"id": "sk_ghost_arrow", "name": "Ghostflight Shot", "cost_mp": 8, "dmg_type": "damage", "est_val": "40-52 Pierce DMG", "desc": "Anak panah hantu yang menembus perisai dan armor musuh secara mutlak."}]}
    ],
    "epic": [
        {"id": "sec_chronomancer", "title": "Rift Chronomancer", "tier": "epic", "icon": "⏳", "bonus_stats": {"int": 5, "wis": 3}, "desc": "Penyihir pemutar sangkala waktu. Mampu membatalkan kegagalan dan mempercepat perputaran mantra.", "skills": [{"id": "sk_time_dilation", "name": "Chrono-Stasis Surge", "cost_mp": 15, "dmg_type": "damage", "est_val": "60-80 Time DMG", "desc": "Menghentikan waktu selama 1 turn dan menghancurkan musuh dalam gelombang temporal."}]},
        {"id": "sec_nightblade", "title": "Nightblade Death-Shadow", "tier": "epic", "icon": "🗡️", "bonus_stats": {"dex": 6, "cha": 2}, "desc": "Pencabut nyawa legendaris dari ordo kegelapan tak bernama.", "skills": [{"id": "sk_fatal_strike", "name": "Eclipse Decapitation", "cost_mp": 18, "dmg_type": "damage", "est_val": "75-100 Fatal DMG", "desc": "Tebasan bayangan gerhana yang memberikan garansi Critical Hit dan luka pendarahan masif."}]}
    ],
    "legendary": [
        {"id": "sec_dragon_sovereign", "title": "Dragon-Heart Sovereign", "tier": "legendary", "icon": "🐉", "bonus_stats": {"str": 8, "con": 6, "cha": 4}, "desc": "Pewaris takhta naga purba. Tubuh kebal api dan setiap hantaman menggetarkan pilar dungeon.", "skills": [{"id": "sk_dragon_breath", "name": "Primeval Dragon Breath", "cost_mp": 25, "dmg_type": "damage", "est_val": "110-145 Fire DMG", "desc": "Semburan api naga primordial yang menghanguskan seluruh monster di ruangan."}]},
        {"id": "sec_void_archon", "title": "Void Archon of Eclipse", "tier": "legendary", "icon": "🌌", "bonus_stats": {"int": 8, "wis": 6, "mp": 50}, "desc": "Penguasa dimensi kehampaan tak berujung yang mampu menelan materi menjadi energi murni.", "skills": [{"id": "sk_event_horizon", "name": "Black Hole Event Horizon", "cost_mp": 30, "dmg_type": "damage", "est_val": "125-160 Void DMG", "desc": "Menciptakan singularitas lubang hitam yang meremukkan monster hingga lebur."}]}
    ],
    "mythic": [
        {"id": "sec_omniscient_keeper", "title": "Omniscient Sovereign of Creation", "tier": "mythic", "icon": "👑", "bonus_stats": {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10, "hp": 100, "mp": 100}, "desc": "Entitas Transenden yang memegang hakikat penciptaan. Seluruh realitas dan takdir tunduk di hadapannya.", "skills": [{"id": "sk_genesis_verdict", "name": "Genesis Divine Judgment", "cost_mp": 40, "dmg_type": "damage", "est_val": "200-280 True DMG", "desc": "Sabda pemusnah semesta yang menghabisi musuh apa pun dalam 1 serangan mutlak."}]}
    ]
}

# =========================================================================
# DYNAMIC ITEM LEVEL (iLvl) & PROGRESSIVE SCALED LOOT DB (TIER 1 - 5)
# =========================================================================
LOOT_DB_TIERED = {
    1: { # Player Level 1 - 4 (Rustic / Iron / Minor)
        "weapons": [
            {"name": "Honed Iron Broadsword", "type": "weapon", "slot": "main_hand", "handedness": "main_hand_only", "icon": "⚔️", "bonus": {"str": 2, "atk": 6}, "val": 6},
            {"name": "Hunting Shortbow", "type": "weapon", "slot": "main_hand", "handedness": "two_handed", "icon": "🏹", "bonus": {"dex": 2, "atk": 6}, "val": 7},
            {"name": "Smith's Heavy Mallet", "type": "weapon", "slot": "main_hand", "handedness": "main_hand_only", "icon": "🔨", "bonus": {"str": 3, "atk": 7}, "val": 8},
            {"name": "Flint Stiletto Knife", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "🗡️", "bonus": {"dex": 2, "atk": 4}, "val": 5}
        ],
        "offhands": [
            {"name": "Reinforced Oak Buckler", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "🛡️", "bonus": {"def": 2, "con": 1}, "val": 5},
            {"name": "Acolyte's Birch Cross", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "✝️", "bonus": {"wis": 2}, "val": 5}
        ],
        "armors": [
            {"name": "Studded Leather Jerkin", "type": "armor", "slot": "armor", "icon": "🦺", "bonus": {"def": 2, "hp": 15}, "val": 6},
            {"name": "Acolyte Travel Habit", "type": "armor", "slot": "armor", "icon": "🥋", "bonus": {"def": 1, "mp": 15}, "val": 5}
        ],
        "helmets": [
            {"name": "Reinforced Leather Cap", "type": "head", "slot": "head", "icon": "🧢", "bonus": {"def": 1}, "val": 4}
        ],
        "boots": [
            {"name": "Sturdy Walking Boots", "type": "feet", "slot": "feet", "icon": "👢", "bonus": {"dodge": 3}, "val": 4}
        ],
        "accessories": [
            {"name": "Copper Lucky Ring", "type": "accessory", "slot": "accessory", "icon": "💍", "bonus": {"cha": 1, "gold_drop": 5}, "val": 8}
        ],
        "consumables": [
            {"name": "Minor Healing Draught", "type": "consumable", "icon": "🧪", "effect": "heal_hp_30", "desc": "Restores 30 HP", "val": 4},
            {"name": "Minor Mana Vial", "type": "consumable", "icon": "✨", "effect": "heal_mp_20", "desc": "Restores 20 MP", "val": 4},
            {"name": "Pine Pitch Torch", "type": "consumable", "icon": "🕯️", "effect": "add_light_6", "desc": "+6 Torch Light turns", "val": 3}
        ]
    },
    2: { # Player Level 5 - 8 (Steel / Silver / Standard)
        "weapons": [
            {"name": "Tempered Steel Longsword", "type": "weapon", "slot": "main_hand", "handedness": "main_hand_only", "icon": "⚔️", "bonus": {"str": 4, "atk": 14}, "val": 20},
            {"name": "Zweihander Greatsword", "type": "weapon", "slot": "main_hand", "handedness": "two_handed", "icon": "🗡️", "bonus": {"str": 6, "atk": 22, "crit": 5}, "val": 30},
            {"name": "Silver Lore Quarterstaff", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "🦯", "bonus": {"int": 4, "wis": 2, "atk": 10}, "val": 22},
            {"name": "Shadow Ranger Warbow", "type": "weapon", "slot": "main_hand", "handedness": "two_handed", "icon": "🏹", "bonus": {"dex": 5, "atk": 18}, "val": 25}
        ],
        "offhands": [
            {"name": "Steel Kite Shield", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "🛡️", "bonus": {"def": 5, "con": 2}, "val": 18},
            {"name": "Enchanted Spellbook Grimoire", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "📖", "bonus": {"int": 3, "mp": 25}, "val": 22}
        ],
        "armors": [
            {"name": "Riveted Steel Chainmail", "type": "armor", "slot": "armor", "icon": "🥋", "bonus": {"def": 5, "hp": 35, "con": 2}, "val": 25},
            {"name": "Shadowstalker Silk Tunic", "type": "armor", "slot": "armor", "icon": "🥷", "bonus": {"def": 3, "dex": 3, "dodge": 6}, "val": 28}
        ],
        "helmets": [
            {"name": "Steel Visored Greathelm", "type": "head", "slot": "head", "icon": "🪖", "bonus": {"def": 3, "con": 1}, "val": 15}
        ],
        "boots": [
            {"name": "Elven Pathfinder Boots", "type": "feet", "slot": "feet", "icon": "👟", "bonus": {"dodge": 6, "dex": 2}, "val": 16}
        ],
        "accessories": [
            {"name": "Silver Amulet of Vitality", "type": "accessory", "slot": "accessory", "icon": "📿", "bonus": {"hp": 35, "con": 2}, "val": 24}
        ],
        "consumables": [
            {"name": "Standard Healing Draught", "type": "consumable", "icon": "🧪", "effect": "heal_hp_65", "desc": "Restores 65 HP", "val": 12},
            {"name": "Aether Mana Flask", "type": "consumable", "icon": "✨", "effect": "heal_mp_40", "desc": "Restores 40 MP", "val": 12},
            {"name": "Universal Antidote Draught", "type": "consumable", "icon": "🧪", "effect": "cure_poison_heal_30", "desc": "Cures Poison & restores 30 HP", "val": 8}
        ]
    },
    3: { # Player Level 9+ (Obsidian / Mythic / Greater)
        "weapons": [
            {"name": "Obsidian Edge War-Cleaver", "type": "weapon", "slot": "main_hand", "handedness": "main_hand_only", "icon": "🪓", "bonus": {"str": 7, "atk": 28, "crit": 8}, "val": 60},
            {"name": "Colossus Titan Greatsword", "type": "weapon", "slot": "main_hand", "handedness": "two_handed", "icon": "🗡️", "bonus": {"str": 10, "atk": 42, "sunder": 10}, "val": 85},
            {"name": "Stormcaller Quartz Scepter", "type": "weapon", "slot": "main_hand", "handedness": "versatile", "icon": "🔮", "bonus": {"int": 8, "wis": 4, "atk": 22}, "val": 70}
        ],
        "offhands": [
            {"name": "Aegis of the Sunlit Citadel", "type": "offhand", "slot": "off_hand", "handedness": "off_hand_only", "icon": "🛡️", "bonus": {"def": 9, "wis": 3, "hp": 40}, "val": 55}
        ],
        "armors": [
            {"name": "Gilded Plate of the Vanguard", "type": "armor", "slot": "armor", "icon": "🛡️", "bonus": {"def": 10, "hp": 70, "con": 4}, "val": 75}
        ],
        "helmets": [
            {"name": "Crown of the Void Seeker", "type": "head", "slot": "head", "icon": "👑", "bonus": {"def": 5, "int": 4, "mp": 40}, "val": 50}
        ],
        "boots": [
            {"name": "Greaves of the Mountain Titan", "type": "feet", "slot": "feet", "icon": "👢", "bonus": {"def": 4, "con": 3, "dodge": 4}, "val": 45}
        ],
        "accessories": [
            {"name": "Band of the Shadow Assassin", "type": "accessory", "slot": "accessory", "icon": "💍", "bonus": {"dex": 5, "crit": 12, "dodge": 8}, "val": 75}
        ],
        "consumables": [
            {"name": "Greater Vitality Potion", "type": "consumable", "icon": "🧪", "effect": "heal_hp_140", "desc": "Restores 140 HP", "val": 35},
            {"name": "Astral Essence Potion", "type": "consumable", "icon": "✨", "effect": "heal_mp_90", "desc": "Restores 90 MP", "val": 35},
            {"name": "Elixir of Full Restoration", "type": "consumable", "icon": "🌟", "effect": "full_restore", "desc": "Fully restores HP, MP & cleanses all status ailments", "val": 70}
        ]
    }
}

def get_tier_for_level(level: int) -> int:
    if level < 5: return 1
    elif level < 9: return 2
    else: return 3

def roll_dynamic_loot(player_lv: int, monster_tier: str = "common") -> Dict[str, Any]:
    tier_key = get_tier_for_level(player_lv)
    pool = LOOT_DB_TIERED[tier_key]
    
    categories = ["weapons", "offhands", "armors", "helmets", "boots", "accessories", "consumables"]
    cat = random.choice(categories)
    item_list = pool.get(cat, pool["consumables"])
    base_item = random.choice(item_list)
    
    loot_item = dict(base_item)
    loot_item["id"] = f"item_{random.randint(10000, 99999)}"
    
    roll = random.randint(1, 100)
    if monster_tier == "boss":
        loot_item["rarity"] = "legendary" if roll <= 30 else "epic"
    elif monster_tier == "elite":
        loot_item["rarity"] = "epic" if roll <= 25 else "rare"
    else:
        if roll <= 50: loot_item["rarity"] = "common"
        elif roll <= 85: loot_item["rarity"] = "uncommon"
        else: loot_item["rarity"] = "rare"
        
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

def get_required_exp_for_level(level: int) -> int:
    return int(75 * (level ** 1.6))

INITIAL_CHAPTER_CHOICES = [
    {"id": "A", "text": "Inspect the stone wall & search for weak structural points (Perception / WIS Check - DC 10)", "type": "roll", "dc": 10, "stat": "WIS"},
    {"id": "B", "text": "Use tools to clear heavy rubble and force a breach (Athletics / STR Check - DC 12)", "type": "roll", "dc": 12, "stat": "STR"},
    {"id": "C", "text": "Light a pine pitch torch and stealthily navigate the corridor (Stealth / DEX Check - DC 9)", "type": "roll", "dc": 9, "stat": "DEX"},
    {"id": "D", "text": "Take a short rest, catch breath, and inspect 40-slot backpack (Action)", "type": "action"}
]

DEFAULT_GAME_STATE = {
    "status": "character_creation",
    "floor": 1,
    "step": 1,
    "active_sound_theme": "creation",
    "torch_turns": 12,
    "rations": 3,
    "story_history": [],
    "player": {
        "name": "Danas",
        "class_id": "peasant",
        "class_name": "Hardy Peasant",
        "class_icon": "🌾",
        "class_tier": "common",
        "level": 1,
        "exp": 0,
        "exp_next": 75,
        "hp": 115,
        "max_hp": 115,
        "mp": 15,
        "max_mp": 15,
        "gold": 12,
        "stats": {"str": 14, "dex": 10, "con": 15, "int": 8, "wis": 12, "cha": 8},
        "equipped": {
            "head": None,
            "armor": None,
            "feet": None,
            "accessory": None,
            "main_hand": None,
            "off_hand": None
        },
        "inventory": [],
        "grimoire": [],
        "active_skills": [],
        "status_effects": []
    },
    "current_node": {
        "type": "entrance",
        "title": "Collapse into the Forgotten Crypt",
        "location": "Subterranean Vault - Floor 1",
        "chapter": "Chapter 1: The Dark Descent"
    },
    "monster": None,
    "pending_awakening": None,
    "scene": {
        "narrative": "Paduka hanyalah seorang warga biasa yang mencari kayu di lereng bukit. Tanah mendadak amblas runtuh! Paduka jatuh terperosok ke dalam rongga makam kuno bawah tanah. Lubang keluar di atas tertutup bebatuan tebal. Di hadapan Paduka, lorong batu berlumut gelap memancarkan hembusan angin dingin purba.",
        "choices": list(INITIAL_CHAPTER_CHOICES),
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
    m_hand = eq.get("main_hand")
    o_hand = eq.get("off_hand")
    if m_hand and o_hand and m_hand.get("handedness") == "versatile" and o_hand.get("handedness") == "versatile":
        base["dual_wield"] = True
        base["atk"] = int(base["atk"] * 1.15)
        base["crit"] += 5
    else:
        base["dual_wield"] = False

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
    game_state["pending_awakening"] = None
    
    # 40 Slots array
    inv_40 = []
    for item in c.get("starting_inventory", []):
        inv_40.append(item)
    while len(inv_40) < 40:
        inv_40.append(None)

    init_skills = list(c.get("initial_skills", []))

    game_state["player"] = {
        "name": name if name.strip() else "Danas",
        "class_id": class_id,
        "class_name": c["title"],
        "class_icon": c["icon"],
        "class_tier": "common",
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
        "inventory": inv_40,
        "grimoire": list(init_skills),
        "active_skills": list(init_skills[:3]),
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
        "choices": list(INITIAL_CHAPTER_CHOICES),
        "log": [f"Commoner '{game_state['player']['name']}' ({c['title']}) begins the underground survival journey!"]
    }
    save_game()

# =========================================================================
# GRANDMASTER AI PROMPT & STORY GENERATOR
# =========================================================================
async def generate_infinite_story(player: Dict[str, Any], current_scene: Dict[str, Any], current_node: Dict[str, Any], monster: Optional[Dict[str, Any]], action_taken: str, roll_result: int, roll_status: str, history: List[str]) -> Dict[str, Any]:
    url = "http://127.0.0.1:20128/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NINE_ROUTER_KEY}"
    }

    system_prompt = """You are Dungeon Master Darsam — an elite Grandmaster TTRPG storyteller for an authentic Dark Fantasy Solo Campaign (Zero to Hero edition).

RULES OF THE SYSTEM:
1. Narrative prose and dialogue MUST be in elegant, sensory-rich Indonesian (address player respectfully as 'Paduka').
2. ALL TECHNICAL, RPG, COMBAT, SPELL, ITEM, AND STAT TERMS MUST BE IN CLEAN STANDARD ENGLISH (e.g. 'STR Check', 'DEX Check', 'INT Check', 'WIS Check', 'CON Check', 'CHA Check', 'DC 12', 'Critical Hit', 'Critical Fail', 'Success', 'Fail', 'Short Rest', 'Poisoned', 'Bleeding', 'Dual Wielding', 'Two-Handed').
3. Show, Don't Tell: Sensory details of decay, cold limestone, and flickering shadows.
4. Fail-Forward: Failure creates complications, monster aggression, or resource loss while driving the story forward.
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
  "hp_change": 0,
  "mp_change": 0,
  "gold_change": 0,
  "monster_encounter": { // null if no monster
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
- Name: {player['name']} | Class: [{player.get('class_tier', 'common').upper()}] {player['class_name']} | Level: {player['level']} (EXP: {player['exp']}/{player['exp_next']})
- Vitals: HP {player['hp']}/{player['max_hp']} | MP {player['mp']}/{player['max_mp']} | Gold: {player['gold']} G
- Stats: STR {player['stats']['str']} | DEX {player['stats']['dex']} | CON {player['stats']['con']} | INT {player['stats']['int']} | WIS {player['stats']['wis']} | CHA {player['stats']['cha']}
- Equipped: {', '.join(equipped_names) if equipped_names else 'None'}
- Inventory: {inv_count}/40 slots used
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

Generate the next chapter of this dark fantasy survival tale!"""

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
    monster_slain = False
    
    if active_m and active_m.get("status") == "active":
        total_stats = compute_total_stats(p)
        if roll_status in ["CRITICAL SUCCESS", "SUCCESS"]:
            base_dmg = total_stats.get("atk", 4) + random.randint(6, 14)
            if roll_status == "CRITICAL SUCCESS":
                base_dmg = int(base_dmg * 2.0)
            
            active_m["hp"] = max(0, active_m["hp"] - base_dmg)
            
            narrative_lower = (ai_resp.get("outcome_summary", "") + " " + ai_resp.get("narrative", "")).lower()
            declared_dead = any(w in narrative_lower for w in ["mati", "tumbang", "tewas", "slain", "defeated", "hancur", "terbelah", "roboh", "terbunuh"])
            
            if active_m["hp"] == 0 or declared_dead:
                active_m["hp"] = 0
                active_m["status"] = "defeated"
                monster_slain = True
                exp_gained = active_m["exp_reward"]
                p["gold"] += active_m["gold_reward"]
                loot_dropped = roll_dynamic_loot(p["level"], active_m["tier"])
                
                for i in range(len(p["inventory"])):
                    if p["inventory"][i] is None:
                        p["inventory"][i] = loot_dropped
                        break
                
                game_state["monster"] = None
        else:
            m_dmg = max(2, active_m["attack"] - total_stats.get("def", 0))
            p["hp"] = max(0, p["hp"] - m_dmg)

    # Apply Vitals Changes from Story
    hp_diff = ai_resp.get("hp_change", 0)
    p["hp"] = max(0, min(p["max_hp"], p["hp"] + hp_diff))
    p["mp"] = max(0, min(p["max_mp"], p["mp"] + ai_resp.get("mp_change", 0)))
    p["gold"] = max(0, p["gold"] + ai_resp.get("gold_change", 0))

    # Spawn new monster if requested by AI
    if not game_state.get("monster") and not monster_slain and ai_resp.get("monster_encounter"):
        m_info = ai_resp["monster_encounter"]
        is_boss = m_info.get("tier") == "boss"
        is_elite = m_info.get("tier") == "elite"
        game_state["monster"] = generate_monster(p["level"], is_boss=is_boss, is_elite=is_elite)

    # Dynamic Secret Job Awakening Trigger (RNG chance on exploration)
    if not game_state.get("monster") and not game_state.get("pending_awakening"):
        rng_job = random.randint(1, 1000)
        awakening_offer = None
        if rng_job <= 1: # 0.1% Mythic
            awakening_offer = random.choice(SECRET_CLASSES_DB["mythic"])
        elif rng_job <= 15: # 1.5% Legendary
            awakening_offer = random.choice(SECRET_CLASSES_DB["legendary"])
        elif rng_job <= 75: # 6% Epic
            awakening_offer = random.choice(SECRET_CLASSES_DB["epic"])
        elif rng_job <= 250: # 17.5% Special
            awakening_offer = random.choice(SECRET_CLASSES_DB["special"])
            
        if awakening_offer and awakening_offer["title"] != p["class_name"]:
            game_state["pending_awakening"] = awakening_offer

    # Level Up Progression & Milestone Skill Unlocks Every 5 Levels
    p["exp"] += exp_gained
    leveled_up = False
    new_skill_unlocked = None
    while p["exp"] >= p["exp_next"] and p["level"] < 20:
        p["level"] += 1
        p["exp"] -= p["exp_next"]
        p["exp_next"] = get_required_exp_for_level(p["level"])
        p["max_hp"] += 15
        p["hp"] = p["max_hp"]
        p["max_mp"] += 8
        p["mp"] = p["max_mp"]
        p["stats"]["str"] += 1
        p["stats"]["con"] += 1
        leveled_up = True

        c_info = CLASSES_INFO.get(p.get("class_id"), {})
        level_unlocks = c_info.get("level_unlocks", {})
        if p["level"] in level_unlocks:
            unlocked = level_unlocks[p["level"]]
            if not any(sk["id"] == unlocked["id"] for sk in p.get("grimoire", [])):
                p.setdefault("grimoire", []).append(unlocked)
                new_skill_unlocked = unlocked
                if len(p.get("active_skills", [])) < 3:
                    p.setdefault("active_skills", []).append(unlocked)

    # Audio Theme
    game_state["active_sound_theme"] = ai_resp.get("audio_theme", "dungeon")

    # Outcome Log Construction
    outcome = f"🎲 [{roll_status}] {ai_resp.get('outcome_summary', '')}"
    if exp_gained > 0: outcome += f" (+{exp_gained} EXP, +{active_m['gold_reward']} Gold)"
    if loot_dropped: outcome += f" 💎 LOOT DROP: [{loot_dropped['rarity'].upper()}] {loot_dropped['name']}!"
    if hp_diff < 0: outcome += f" (-{-hp_diff} HP)"
    if leveled_up: outcome += f" 🌟 LEVEL UP! Paduka naik ke Level {p['level']} (Max HP/MP meningkat & HP pulih penuh)!"
    if new_skill_unlocked: outcome += f" ⚡ JURUS BARU TERBUKA (Lv.{p['level']}): {new_skill_unlocked['name']}!"

    # Update Scene State
    game_state["scene"]["chapter"] = ai_resp.get("chapter", scene.get("chapter"))
    game_state["scene"]["title"] = ai_resp.get("title", "Dungeon Chamber")
    game_state["scene"]["location"] = ai_resp.get("location", scene.get("location"))
    game_state["scene"]["narrative"] = ai_resp.get("narrative", "Suasana gua semakin pekat...")
    game_state["scene"]["choices"] = ai_resp.get("choices", scene.get("choices"))
    game_state["current_node"]["type"] = ai_resp.get("node_type", "exploration")
    game_state["scene"]["log"].append(outcome)
    if len(game_state["scene"]["log"]) > 4: game_state["scene"]["log"].pop(0)

    save_game()

    return {
        "type": "state_update",
        "outcome": outcome,
        "state": game_state
    }

# =========================================================================
# 6-SLOT EQUIPMENT & WEAPON HANDEDNESS LOGIC
# =========================================================================
def equip_item(item_index: int):
    global game_state
    p = game_state["player"]
    if item_index < 0 or item_index >= len(p["inventory"]): return
    item = p["inventory"][item_index]
    if not item or item.get("type") not in ["weapon", "offhand", "armor", "head", "feet", "accessory"]: return
    
    slot = item.get("slot")
    if not slot or slot not in p["equipped"]: return

    if slot == "main_hand" and item.get("handedness") == "two_handed":
        if p["equipped"]["off_hand"]:
            for i in range(len(p["inventory"])):
                if p["inventory"][i] is None:
                    p["inventory"][i] = p["equipped"]["off_hand"]
                    p["equipped"]["off_hand"] = None
                    break

    if slot == "off_hand" and p["equipped"].get("main_hand") and p["equipped"]["main_hand"].get("handedness") == "two_handed":
        for i in range(len(p["inventory"])):
            if p["inventory"][i] is None:
                p["inventory"][i] = p["equipped"]["main_hand"]
                p["equipped"]["main_hand"] = None
                break

    old_equipped = p["equipped"][slot]
    p["equipped"][slot] = item
    p["inventory"][item_index] = old_equipped
    save_game()

def unequip_item(slot_name: str):
    global game_state
    p = game_state["player"]
    if slot_name not in p["equipped"] or not p["equipped"][slot_name]: return
    
    for i in range(len(p["inventory"])):
        if p["inventory"][i] is None:
            p["inventory"][i] = p["equipped"][slot_name]
            p["equipped"][slot_name] = None
            save_game()
            break

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
    elif eff.startswith("add_light_"):
        amount = int(eff.split("_")[-1])
        game_state["torch_turns"] += amount
        if "blind" in p["status_effects"]: p["status_effects"].remove("blind")
    elif eff == "full_restore":
        p["hp"] = p["max_hp"]
        p["mp"] = p["max_mp"]
        p["status_effects"] = []
    
    p["inventory"][item_index] = None
    save_game()

def accept_awakening():
    global game_state
    p = game_state["player"]
    awakening = game_state.get("pending_awakening")
    if not awakening: return
    
    p["class_name"] = awakening["title"]
    p["class_icon"] = awakening["icon"]
    p["class_tier"] = awakening["tier"]
    
    if "bonus_stats" in awakening:
        for k, v in awakening["bonus_stats"].items():
            if k in p["stats"]:
                p["stats"][k] += v
            elif k == "hp":
                p["max_hp"] += v
                p["hp"] += v
            elif k == "mp":
                p["max_mp"] += v
                p["mp"] += v
                
    for sk in awakening.get("skills", []):
        if not any(s["id"] == sk["id"] for s in p.get("grimoire", [])):
            p.setdefault("grimoire", []).append(sk)
            if len(p.get("active_skills", [])) < 3:
                p.setdefault("active_skills", []).append(sk)
                
    game_state["pending_awakening"] = None
    save_game()

def decline_awakening():
    global game_state
    game_state["pending_awakening"] = None
    save_game()

def equip_active_skill(skill_id: str):
    global game_state
    p = game_state["player"]
    grimoire = p.get("grimoire", [])
    active_skills = p.setdefault("active_skills", [])
    
    skill_obj = next((s for s in grimoire if s["id"] == skill_id), None)
    if not skill_obj: return
    if any(s["id"] == skill_id for s in active_skills): return
    
    if len(active_skills) >= 3:
        active_skills.pop(0)
    
    active_skills.append(skill_obj)
    save_game()

def unequip_active_skill(skill_id: str):
    global game_state
    p = game_state["player"]
    active_skills = p.get("active_skills", [])
    p["active_skills"] = [s for s in active_skills if s["id"] != skill_id]
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

            elif action_type == "accept_awakening":
                accept_awakening()
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": f"🌟 TAKDIR DITERIMA! Paduka telah bangkit menjadi [{game_state['player']['class_tier'].upper()}] {game_state['player']['class_name']}!"})

            elif action_type == "decline_awakening":
                decline_awakening()
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Tawaran kebangkitan kelas ditolak."})

            elif action_type == "equip_skill":
                sk_id = data.get("skill_id")
                equip_active_skill(sk_id)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Jurus berhasil dipasang ke Slot Tempur!"})

            elif action_type == "unequip_skill":
                sk_id = data.get("skill_id")
                unequip_active_skill(sk_id)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Jurus dilepas dari Slot Tempur!"})

            elif action_type == "reset_game":
                game_state.clear()
                game_state.update(json.loads(json.dumps(DEFAULT_GAME_STATE)))
                game_state["status"] = "character_creation"
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                await manager.broadcast_all({"type": "state_update", "state": game_state, "outcome": "Game di-reset ke Ruang Asal-Usul Karakter."})

    except WebSocketDisconnect:
        await manager.disconnect_controller(websocket)
