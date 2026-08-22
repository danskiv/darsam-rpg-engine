# Darsam RPG Dungeon Engine - PRD v2.3.0 (Grandmaster Ultimate Edition)

## 1. Executive Summary
**Darsam RPG Dungeon Engine** adalah platform game solo interaktif berbasis *Tabletop RPG (TTRPG)* bertema *Dark Fantasy* dengan arsitektur **Dual-Screen (TV Companion Display & Standalone Mobile/Desktop Controller)**.
Game ini ditenagai oleh kecerdasan buatan (*AI Dungeon Master*) yang memadukan model penalaran **OX-Alpha (Primary Reasoning Engine)** dan **Gemini 3.7 Flash Low (High-Speed Fallback)** melalui gateway 9Router, serta mendukung katalog dinamis 385 model AI.

Game ini menggabungkan filosofi narasi mendalam ala *Old School Renaissance (OSR)* dengan mekanik adiktif *Action RPG (Diablo, Path of Exile)*: sistem inventaris ber-grid, loot table berjenjang kelangkaan (*Rarity Multipliers*), pergantian kelas rahasia (*Secret Job Awakening*), serta pertarungan taktis D20 berbasis atribut karakter.

---

## 2. Fitur Utama & Pilar Sistem (Core Pillars v2.3.0)

### 📱 A. 100% Standalone Controller
* **Kemandirian Penuh:** Controller di HP atau Laptop dapat mengakses seluruh fitur game (Narasi Cerita, Pertarungan Monster, Jurus Aktif, 6-Slot Paper Doll, 40-Slot Tas, Belanja/Barter, Dadu D20, & Pemilihan Model AI) secara mandiri tanpa bergantung pada layar TV.
* **Tata Letak Seimbang (Desktop & Mobile):** 
  - Desktop view 50:50 simetris dengan panel cerita *full vertical stretch* (`flex-grow: 1`), teks berukuran besar dan tajam (`text-base`), serta bebas dari ruang kosong yang terpotong.
  - Mobile view mengalir vertikal secara alami (*native smooth scrolling*) dengan bantalan bawah yang lega.
* **Pilihan Aksi Bersih (Opsi A):** Kalimat narasi aksi murni dipisahkan dari lencana teknis status (`[💪 STR • Target: 11]`, `[🎯 DEX • Target: 10]`, `[⚡ ACTION]`).

### 📺 B. Atmospheric TV Companion Display (Layar 32" Optimized)
* **Zero Dead Space:** Menampilkan papan visual taktis beresolusi 16:9 yang mengisi layar penuh (*edge-to-edge*).
* **Komponen Display TV:**
  - Vitals Karakter (Bar HP & MP tebal).
  - 6 Atribut D&D (STR, DEX, CON, INT, WIS, CHA) yang terkalkulasi otomatis dengan bonus perlengkapan.
  - 6 Slot Perlengkapan Visual (Head, Armor, Feet, Main Hand, Off Hand, Accessory).
  - Matriks Tas 40-Slot (Grid 8x5) dengan border berkilau sesuai warna kelangkaan item.
  - D20 Live Rolling Chamber dengan animasi kocokan dadu interaktif.
  - Kartu Status Monster Target & Catatan Kronik Cerita (*Live Chronicle Log*).
  - Efek Cahaya Aura Dinamis sesuai kasta kelas (*Common, Special, Epic, Legendary, Mythic*).

### 🎭 C. 8 Latar Belakang Awal (Zero to Hero)
Pemain memulai sebagai warga desa biasa tanpa kesaktian berlebihan:
1. 🌾 **Hardy Peasant:** Petani berotot liat (`HP 115, STR 14, CON 15`) • Skill: *Adrenaline Surge*.
2. 🔨 **Smith Apprentice:** Magang pandai besi (`HP 125, STR 16, CON 14`) • Skill: *Anvil Crush*.
3. 📜 **Village Scholar:** Asisten tabib desa (`HP 85, MP 60, INT 16`) • Skill: *Arcane Spark*.
4. 🏹 **Forest Trapper:** Pemburu berkabut (`HP 95, DEX 16, WIS 14`) • Skill: *Caltrop Scatter*.
5. 🛡️ **Disgraced Watchman:** Penjaga gerbang kota (`HP 120, STR 15, CON 14`) • Skill: *Shield Wall*.
6. 🕯️ **Tomb Grave-Robber:** Penyusup makam kuno (`HP 90, DEX 16, CHA 12`) • Skill: *Shadow Ambush*.
7. ⛪ **Temple Acolyte:** Murid kuil suci (`HP 105, MP 45, WIS 16`) • Skill: *Prayer of Radiance*.
8. 🧪 **Alchemist Apprentice:** Peracik ramuan liar (`HP 85, MP 50, INT 16`) • Skill: *Corrosive Acid Bomb*.

### 🌌 D. Dynamic Secret Job Awakening (RNG Rare Trigger)
Eksplorasi bawah tanah dapat memicu peristiwa langka untuk berganti ke kelas yang lebih tinggi:
* 🟢 **Special Class (~17.5% Peluang):** *Blood-Pact Zealot, Shadowveil Ranger*.
* 🔵 **Epic Class (~6% Peluang):** *Rift Chronomancer, Nightblade Death-Shadow*.
* 🟣 **Legendary Class (~1.5% Peluang):** *Dragon-Heart Sovereign, Void Archon*.
* 🟡 **Mythic Class (~0.1% Peluang):** *Omniscient Sovereign of Creation*.
*(Pemain dapat menerima atau menolak takdir baru; kelas dapat ditimpa berkali-kali seiring ditemukannya rahasia yang lebih dalam)*.

### 🛡️ E. 6-Slot Paper Doll & Weapon Handedness
* **6 Slot Perlengkapan:** `Head (🪖)`, `Body Armor (🥋)`, `Feet (👢)`, `Accessory (💍)`, `Main Hand (⚔️)`, `Off Hand (🛡️)`.
* **Aturan Penanganan Senjata:**
  - **Two-Handed Weapons (Greatsword/Warbow):** Otomatis mengunci slot Off-Hand (`[2-Handed Lock]`) dan melepaskan perisai ke tas.
  - **Dual Wielding (Versatile Weapon di kedua tangan):** Mengaktifkan status **Dual Wield (+15% Attack Damage & +5% Crit)**.
* **Agregasi Status Total:** Memasang perlengkapan berbonus HP, MP, STR, DEX, dll. langsung memperbesar kapasitas bar status di Controller dan TV secara *real-time*.

### 🎒 F. Tas 40-Slot & Auto-Sorting Cerdas
* **Kapasitas 40 Slot:** Menyediakan ruang luas untuk menampung berbagai jarahan makam.
* **Hierarki Pengurutan Otomatis:**
  1. Perlengkapan tempur diurutkan paling atas berdasarkan **Item Level Tertinggi (`Lv.5` ➔ `Lv.1`)**, lalu **Kelangkaan Tertinggi (*Legendary ➔ Common*)**.
  2. Barang konsumsi (*Consumables*) dan bahan (*Materials*) disusun rapi di bawah perlengkapan.
* **Stacking Barang Konsumsi:** Item konsumsi yang sama otomatis ditumpuk dalam 1 slot tas (`qty: N`).

### 📈 G. Dynamic Item Level (iLvl) & Real Rarity Multiplier
* Item di toko dan drop monster menyesuaikan dengan level pemain: $\text{iLvl} = \text{Player Level} \pm 1$.
* Skala pengali atribut nyata:
  - ⚪ **Common:** 1.0x Base Stat (0 Atribut Sekunder).
  - 🟢 **Uncommon:** 1.3x Base Stat (+1 Atribut Sekunder).
  - 🔵 **Rare:** 1.8x Base Stat (+2 Atribut Sekunder).
  - 🟣 **Epic:** 2.5x Base Stat (+3 Atribut Sekunder).
  - 🟡 **Legendary:** 3.6x Base Stat (+4 Atribut Sekunder).

### 🎲 H. D20 Check & Multi-Source EXP Progression
* **Formula Dadu TTRPG:** $\text{Total Roll} = \text{D20} + \frac{\text{Attribute Score} - 10}{2}$ vs $\text{DC 8–12}$.
* **Sumber EXP Beragam:** EXP didapat dari mengalahkan monster, keberhasilan *Skill Check* (+15 EXP), dan *Critical Success* (+25 EXP).
* **Kenaikan Level:** Setiap naik level memulihkan HP/MP 100% penuh, menambah +15 Max HP, +8 Max MP, +1 STR, +1 CON, serta membuka jurus baru setiap kelipatan Level 5 dan 10.

### 🧠 I. Dual AI Engine & Pemilih 385 Model
* **Model Utama:** `openrouter/stealth/ox-alpha` untuk penalaran sastra *dark fantasy* yang mendalam.
* **Model Cadangan:** `ag/gemini-3.7-flash-low` untuk kecepatan respon instan.
* **Katalog Lengkap:** Dropdown di controller memungkinkan pergantian instan ke salah satu dari 385 model AI yang tersedia di gateway 9Router.
* **Indikator Live AI:** Banner mengambang memberi tahu pemain bahwa Dungeon Master sedang merajut babak cerita berikutnya.
* **Penyebutan Karakter:** AI selalu menyebut protagonis langsung dengan Nama Karakter (tanpa gelar kerajaan di dalam narasi game).

---

## 3. Arsitektur Teknis & Endpoint

```
[Mobile / Laptop Controller] ◄──(WebSocket / REST)──► [FastAPI Backend Engine] ──(9Router Gateway)──► [AI LLMs]
(Port 8090: /controller)                               (VPS Oracle Linux)
                                                              │
                                                      (WebSocket State)
                                                              ▼
                                                   [Android TV Display App]
                                                       (Port 8090: /tv)
```

### Daftar Endpoint:
* `GET /tv` — Antarmuka panggung TV 16:9.
* `GET /controller` — Antarmuka pengendali mandiri di ponsel/laptop.
* `GET /api/state` — REST endpoint status permainan saat ini.
* `GET /api/classes` — REST endpoint data 8 Origin awal.
* `GET /api/models` — REST endpoint daftar 385 model AI yang aktif.
* `WS /ws/tv` — WebSocket sinkronisasi layar TV.
* `WS /ws/controller` — WebSocket interaksi dua arah kontroler.

---

## 4. Riwayat Versi & Milestone

| Versi | Tanggal | Sorotan Pembaruan |
|---|---|---|
| **v1.0.0** | 2026-08-21 | Purwarupa awal web dual-screen dengan FastAPI, WebSockets, dan 4 job dasar. |
| **v1.2.0** | 2026-08-22 | Integrasi Gemini 3.7 Flash Low AI Dungeon Master & Web Audio Synthesizer. |
| **v2.0.0** | 2026-08-22 | Grandmaster Edition: 8 Origins, 6-Slot Paper Doll, Handedness, 40-Slot Bag, & Awakening. |
| **v2.1.0** | 2026-08-22 | Dual AI Engine (OX-Alpha), AI Loading Banner, & Keseimbangan Desktop UI. |
| **v2.2.0** | 2026-08-22 | Penyeimbangan D20 Modifier, Multi-Source EXP, Consumable Stacking, & Rarity Multipliers. |
| **v2.3.0** | 2026-08-22 | Intelligent Inventory Sorting (Lv & Rarity DESC), Dynamic Gear HP/MP Aggregation, & Public Repo Release. |
