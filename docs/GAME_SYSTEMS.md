# Darsam RPG Engine - Game Systems & Mathematical Mechanics (v2.2.0)

## 1. D20 Roll & Stat Modifier Balancing
Sebelumnya, sistem mengecek angka mentah D20 terhadap DC tanpa menyertakan bonus atribut karakter, menyebabkan tingkat kegagalan (*Fail Rate*) terlalu sering.
Di v2.2.0, sistem menggunakan standar resmi TTRPG:
$$\text{Stat Modifier} = \frac{\text{Attribute Score} - 10}{2}$$
$$\text{Total Roll} = \text{Raw D20} + \text{Stat Modifier}$$

- **Contoh:** Peasant dengan STR 16 (Modifier +3) melempar D20 dapat angka `8` vs DC `11` ➔ Total = `8 + 3 = 11` ➔ **SUCCESS!**
- **Difficulty Class (DC):** Diseimbangkan antara 8 (Mudah) hingga 12 (Menantang) untuk lantai 1–3.

---

## 2. Multi-Source Proper EXP Progression
Sistem perolehan EXP diperluas agar progresi terasa memuaskan dan alami:
1. **Monster Kill EXP:**
   - Common Minion: `Level * 25 EXP`
   - Elite Champion: `Level * 60 EXP`
   - Dungeon Boss: `Level * 150 EXP`
2. **Skill Check Success EXP:** `+15 EXP` setiap kali berhasil melewati rintangan / pintu / jebakan.
3. **Critical Success D20 Bonus:** `+25 EXP` ekstra.

---

## 3. Consumable Item Stacking System
- Item berjenis `consumable` (Rations, Potions, Torches, Bandages) yang memiliki nama dan efek sama akan otomatis ditumpuk dalam **1 slot tas**.
- Properti `qty: N` ditampilkan dengan badge `xN` di inventaris.
- Menggunakan item konsumsi akan mengurangi `qty` sebesar 1; slot tas baru dikosongkan jika `qty == 0`.

---

## 4. Equipment Item Level & Real Rarity Scaling
Setiap perlengkapan memiliki **Item Level (`item_level`)** dan pengali kelangkaan (**Rarity Multiplier**):
- ⚪ **Common (1.0x Base Stat):** 0 Atribut Sekunder.
- 🟢 **Uncommon (1.3x Base Stat):** +1 Atribut Sekunder Tambahan.
- 🔵 **Rare (1.8x Base Stat):** +2 Atribut Sekunder Tambahan (*Dipastikan jauh lebih kuat dari Common/Uncommon*).
- 🟣 **Epic (2.5x Base Stat):** +3 Atribut Sekunder Tambahan.
- 🟡 **Legendary (3.6x Base Stat):** +4 Atribut Sekunder Tambahan.

$$\text{Equipment ATK} = (\text{Base ATK} + (\text{iLvl} \times 2)) \times \text{Rarity Multiplier}$$
$$\text{Equipment DEF} = (\text{Base DEF} + (\text{iLvl} \times 1.2)) \times \text{Rarity Multiplier}$$
$$\text{Equipment HP} = (\text{Base HP} + (\text{iLvl} \times 8)) \times \text{Rarity Multiplier}$$

---

## 5. Dual Wielding & Weapon Handedness
- **Versatile:** Dapat dipasang di Main Hand dan Off Hand sekaligus ➔ Mengaktifkan **Dual Wield Stance (+15% ATK & +5% Crit)**.
- **Two-Handed:** Mengunci slot Off Hand (`[2-Handed Lock]`) dan memiliki daya rusak 1.5x lebih besar.
