# Darsam RPG Dungeon Engine - PRD v2.4.0 (Encounter & Exploration Expansion)

## 1. Executive Summary
**Darsam RPG Dungeon Engine** bertransformasi menjadi game petualangan *Living Crypt Roguelike* dengan peluncuran **Encounter Ecosystem Engine (v2.4.0)**.
Pemain tidak lagi hanya berjalan lurus bertarung tanpa henti, melainkan menghadapi dinamika penjelajahan realistis: **Toko & Pedagang Pasar Gelap**, **Peti Harta Karun & Ancaman Mimic**, **Persimpangan Jalan Bercabang (Crossroads Dilemma)**, **Ruang Api Unggun (Campfire Rest Site)**, serta **Altar Takdir Purba (Shrines of Fate)**.

---

## 2. Weighted Encounter Generator Engine (v2.4.0)

Setiap langkah penjelajahan diundi secara dinamis menggunakan algoritma pembobotan probabilistik (*Weighted RNG*):

| Tipe Pertemuan (*Node Type*) | Peluang Muncul | Karakteristik & Fitur Unik |
|---|---|---|
| 🗡️ **Combat Encounter** | **35%** | Pertarungan taktis melawan Minion, Elite Monster, atau Dungeon Boss. |
| 🔀 **Branching Crossroads** | **20%** | Memilih 2–3 rute eksplorasi (Jalur Aman vs Toko/Peti vs Sarang Monster Berbahaya). |
| 🎁 **Treasure Chest & Puzzles** | **15%** | Peti Kayu, Peti Besi Terkunci (Butuh Lockpick/STR Check), Peti Emas, atau Ancaman Monster Mimic! |
| 🦹‍♂️ **Merchant & NPC Encampment** | **12%** | Toko pedagang kelana (Beli/Jual rongsokan), Pasar Gelap, dan Makelar Jiwa (Blood Barter). |
| 🏕️ **Campfire Rest Site** | **10%** | Memulihkan HP/MP, meracik makanan, dan mengatur ulang Skill Loadout sebelum babak berikutnya. |
| 🔮 **Shrine of Fate & Awakening** | **8%** | Altar mistis untuk mengorbankan emas/darah demi lonjakan stat permanen atau memicu Secret Awakening. |

---

## 3. Detail Mekanik Sistem Baru

### A. 🦹‍♂️ Living Crypt Merchant & Barter System
* **Stok Terbatas (4–6 Barang per Pertemuan):** Toko menjual perlengkapan yang berskala dengan level pemain ($iLvl = \text{Player Level} \pm 1$), ramuan berjenjang (Tier 1–5), obor, dan Skill Tome langka.
* **Fitur Tawar-Menawar (Haggling via CHA Check):**
  - *Sukses:* Diskon 20% untuk semua barang di toko.
  - *Critical Success (Dadu 20):* Diskon 40% + Hadiah Gratis 1 Ramuan!
  - *Gagal:* Pedagang tersinggung, harga naik 15%.
* **One-Click "Sell All Junk":** Menjual seluruh item rongsokan common putih/abu-abu dari 40-slot tas dalam 1 detik.

### B. 🎁 Treasure Chests & Mimic Traps
* **Peti Kayu Biasa:** Berisi ransum, obor, dan emas.
* **Peti Besi Terkunci:** Memerlukan *Lockpick (DEX Check DC 11)* atau *Crowbar (STR Check DC 13)* untuk membuka jarahan *Rare & Epic*.
* **Monster Mimic (Peluang 15%):** Peti bertaring lapar yang menyerang pemain ceroboh. Pemain jeli dapat menggunakan *Perception (WIS Check)* untuk mendeteksi mimic sebelum membuka.

### C. 🔀 Branching Routes & Strategic Navigation
* Lorong terbelah menjadi pilihan jalur dengan visibilitas atmosferik yang jelas:
  - *Jalur Lumut Sejuk:* Menuju mata air penyembuh / ruang aman.
  - *Pintu Besi Berkarat:* Menuju ruang toko atau peti besi kuno.
  - *Lorong Berlumur Darah:* Menuju sarang monster Elite dengan imbalan EXP & pusaka *Legendary*.

### D. 🏕️ Campfire Rest Sites
* Memberikan 3 opsi taktis:
  - *Rest & Recover:* Memulihkan 40% Max HP & 50% Max MP.
  - *Sharpen & Meditate:* Menghapus status kutukan/racun dan menata 3 slot jurus tempur.
  - *Cook Rations:* Memasak ransum untuk mendapatkan *Buff +2 ATK* pada pertempuran berikutnya.

---

## 4. Endpoint & Kontrak Payload

### WebSocket Actions Baru:
* `{"type": "buy_item", "merchant_item_id": "...", "cost": 15}` — Membeli barang dari toko.
* `{"type": "sell_item", "index": 4}` — Menjual barang tertentu dari 40 slot tas.
* `{"type": "sell_all_junk"}` — Menjual seluruh item common dari tas.
* `{"type": "rest_campfire", "rest_type": "sleep" | "meditate" | "cook"}` — Istirahat di api unggun.
* `{"type": "interact_altar", "altar_action": "pray" | "sacrifice_gold" | "sacrifice_hp"}` — Berinteraksi dengan altar dewa.
