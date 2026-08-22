# Darsam RPG Engine - Game Systems & Mathematical Mechanics (v2.1.0)

## 1. Dual AI Storyteller Architecture
- **Primary Model:** `openrouter/stealth/ox-alpha` — Model penalaran mutakhir dengan temperature 0.70 dan 2000 max tokens untuk menghasilkan narasi berbobot tinggi dan plot tak terduga.
- **Fallback Model:** `ag/gemini-3.7-flash-low` — Model kecepatan tinggi yang otomatis mengambil alih jika model utama mengalami timeout (>14s) atau error.
- **Loading State:** Banner animasi mengambang (`#m-ai-loading`) memberi tahu pemain saat AI sedang merajut takdir.

---

## 2. Attributes & Combat Formulas
Karakter memiliki 6 Core Ability Scores standar D&D:
- **STR (Strength):** `ATK = (STR // 2) + Weapon_ATK`
- **DEX (Dexterity):** `Dodge Rate % = (DEX // 3) + Boots_Dodge`, `Crit Rate % = 5% + Weapon_Crit`
- **CON (Constitution):** `Max HP = Base_HP + (Level - 1)*15 + Gear_HP`, `DEF = (CON // 3) + Armor_DEF`
- **INT (Intelligence):** Menentukan kekuatan Spell Damage & pemecahan teka-teki kuno.
- **WIS (Wisdom):** Menentukan efektivitas Healing Spells, kepekaan jebakan (*Perception DC*), dan inisiatif.
- **CHA (Charisma):** Menentukan diskon harga toko (`Discount % = (CHA - 10) * 2%`), harga jual barang bekas, dan diplomasi NPC.

---

## 3. Weapon Handedness & Dual Wielding Rules
Setiap senjata dan perisai memiliki properti `handedness`:
1. `main_hand_only`: Hanya bisa dipasang di slot Main Hand (misal: Heavy Smith Hammer).
2. `off_hand_only`: Hanya bisa dipasang di slot Off Hand (misal: Buckler Shield, Quiver, Grimoire).
3. `versatile`: Bisa dipasang di Main Hand ATAU Off Hand.
   - **Dual Wield Bonus:** Jika Main Hand & Off Hand sama-sama memegang senjata *versatile*, karakter mendapat `+15% Total Attack Damage` dan memicu peluang serangan ganda (*Double Strike*).
4. `two_handed`: Memakan 2 tangan sekaligus (misal: Zweihander Greatsword, Longbow).
   - Memasang senjata 2-tangan secara otomatis mengunci slot Off Hand (`[2-Handed Lock]`) dan melepaskan perisai yang ada ke tas 40-slot.

---

## 4. 6 Equipment Slots Architecture
1. **Head (`head`):** Topeng, Helm Baja, Mahkota Rune (`+DEF, +MP, +INT/WIS`).
2. **Body (`armor`):** Zirah Badan / Jubah (`+DEF, +HP, +CON`).
3. **Feet (`feet`):** Sepatu Bot Pengembara (`+Dodge %, +DEX`).
4. **Accessory (`accessory`):** Cincin & Jimat Pusaka (`+CHA, +Crit %, +Gold %`).
5. **Main Hand (`main_hand`):** Senjata Utama (`+ATK, +STR/DEX Modifier`).
6. **Off Hand (`off_hand`):** Perisai / Buku / Senjata Kedua (`+DEF, +Block %, +Spell Power`).

---

## 5. Experience & Level Scaling Formula (Level 1 - 20)
$$\text{Required EXP for Next Level} = 75 \times (\text{Level})^{1.6}$$
- Level 1 ➔ 2: 75 EXP
- Level 2 ➔ 3: 227 EXP
- Level 3 ➔ 4: 434 EXP
- Level 4 ➔ 5: 689 EXP *(Class Promotion & New Skill Unlock Milestone)*

---

## 6. Monster Leveling & Tiers
- **Common (Trash):** HP = `18 + (Lv * 8)`, ATK = `4 + (Lv * 2)`, Reward = `Lv * 15 EXP` + Common/Uncommon Loot.
- **Elite (Champion):** HP = `45 + (Lv * 18)`, ATK = `8 + (Lv * 3)`, Reward = `Lv * 45 EXP` + Rare/Epic Loot.
- **Boss (Overlord):** HP = `110 + (Lv * 35)`, ATK = `14 + (Lv * 4)`, Reward = `Lv * 120 EXP` + Guaranteed Epic/Legendary Loot.
- **Combat Resolution Rule:** Monster dinyatakan tumbang *hanya* jika HP numeriknya mencapai `0`. Status musuh tidak akan hilang prematur hanya karena narasi luka AI.

---

## 7. Secret Job Awakening Rarity & RNG Trigger
Pemain berpeluang menemukan Altar Terlarang, Naskah Kuno, atau mukjizat kondisi sekarat:
- **🟢 Special Class (~17.5% Chance):** *Blood-Pact Zealot, Shadowveil Ranger*.
- **🔵 Epic Class (~6% Chance):** *Rift Chronomancer, Nightblade Death-Shadow*.
- **🟣 Legendary Class (~1.5% Chance):** *Dragon-Heart Sovereign, Void Archon*.
- **🟡 Mythic Class (~0.1% Chance):** *Omniscient Sovereign of Creation*.
*(Bisa ditimpa berkali-kali seiring penemuan takdir baru; menghasilkan aura cahaya khusus di TV)*.

---

## 8. Dynamic Item Level (iLvl) & Consumables Scaling
- Toko dan Loot Drop selalu menyesuaikan dengan level pemain: $\text{iLvl} = \text{Player Level} \pm 1$.
- Tingkat Ramuan Darah: Minor Salve (20 HP) ➔ Standard Draught (60 HP) ➔ Greater Potion (140 HP) ➔ Superior Elixir (300 HP) ➔ Celestial Ambrosia (100% Full Restore).
- Obat Penangkal: Bandage (*Bleed*), Antidote (*Poison*), Holy Water (*Curse*), Torch (*Light/Blindness*).
