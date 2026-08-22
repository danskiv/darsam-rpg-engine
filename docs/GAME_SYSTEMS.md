# Darsam RPG Engine - Game Systems & Mathematical Mechanics (v2.4.0)

## 1. Weighted Encounter Generation Engine
Setiap kali pemain menyelesaikan sebuah babak/ruangan, sistem backend secara probabilistik menentukan jenis pertemuan berikutnya (*Next Room Encounter*):
- 🗡️ **Combat Encounter (35%):** Pertarungan melawan Minion, Elite Monster, atau Dungeon Boss.
- 🔀 **Branching Crossroads (20%):** Pilihan rute strategis (Jalur Aman, Jalur Toko/Peti, atau Sarang Monster Berbahaya).
- 🎁 **Treasure Chest & Puzzles (15%):** Peti Kayu, Peti Terkunci (Lockpick/STR Check), atau Monster Mimic.
- 🦹‍♂️ **Merchant & NPC Encampment (12%):** Toko bawah tanah dengan fitur tawar-menawar (Haggling via CHA Check) dan Jual Sampah 1-Klik (*Sell All Junk*).
- 🏕️ **Campfire Rest Site (10%):** Istirahat untuk memulihkan HP/MP, meracik makanan (*Buff ATK*), dan menata jurus.
- 🔮 **Shrine of Fate (8%):** Altar dewa untuk pengorbanan emas/darah atau memicu *Secret Job Awakening*.

---

## 2. Living Crypt Merchant Economy
1. **Dynamic Stock:** Toko membawa 4–6 barang acak dengan level item menyesuaikan level pemain ($iLvl = \text{Player Level} \pm 1$).
2. **Haggling Mechanics (CHA Check vs DC 11):**
   - **Success (D20 + CHA Mod >= 11):** Diskon 20% untuk semua barang di toko.
   - **Critical Success (Natural 20):** Diskon 40% + 1 Ramuan Gratis.
   - **Fail (Total < 11):** Harga barang naik 15%.
   - **Critical Fail (Natural 1):** Toko ditutup paksa seketika.
3. **One-Click Sell All Junk:** Menjual seluruh item berkasta `common` putih/abu-abu dari tas secara instan.

---

## 3. Treasure Chest & Mimic Trap Ratios
- 📦 **Wooden Chest (50%):** Ransum, Obor, 10–25 Gold.
- 🔒 **Locked Iron Chest (35%):** Butuh Lockpick/STR Check ➔ Perlengkapan *Rare/Epic*.
- 👹 **Chest Mimic (15%):** Peti penyamar bertaring yang memicu pertarungan dadakan jika gagal dideteksi via *Perception / WIS Check*.
