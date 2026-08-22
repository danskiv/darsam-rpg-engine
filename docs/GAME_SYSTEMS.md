# Darsam RPG Engine - Game Systems & Mathematical Mechanics (v2.3.0)

## 1. Inventory Auto-Sorting Hierarchy
Daftar tas (40-Slot Backpack) kini diurutkan secara otomatis dan dinamis di controller:
1. **Grup Perlengkapan (Equipments) Tampil Paling Atas:**
   - **Tingkat 1 (Item Level DESC):** Item ber-level tinggi (`Lv.5`, `Lv.4`, `Lv.3`) berada paling atas.
   - **Tingkat 2 (Rarity Tier DESC):** Jika level sama, diurutkan berdasarkan kelangkaan (*Legendary (5) ➔ Epic (4) ➔ Rare (3) ➔ Uncommon (2) ➔ Common (1)*).
   - **Tingkat 3 (Slot Category):** Weapon ➔ Offhand ➔ Armor ➔ Head ➔ Feet ➔ Accessory.
2. **Grup Bahan & Konsumsi (Consumables & Materials) di Bawah:**
   - Disusun rapi di bawah perlengkapan tempur dengan indikator tumpukan (`xN`).

---

## 2. Dynamic Equipment HP/MP & Attribute Aggregation
- **Effective Max HP/MP:**
  $$\text{Effective Max HP} = \text{Base Max HP} + \sum \text{Bonus HP Gear}$$
  $$\text{Effective Max MP} = \text{Base Max MP} + \sum \text{Bonus MP Gear}$$
- Setiap kali pemain memasang item dengan bonus HP/MP (misal: *Padded Leather Cuirass +15 HP* atau *Acolyte Prayer Beads +42 MP*):
  - Bar status HP/MP di Controller dan TV langsung melonjak naik secara *real-time*.

---

## 3. Dynamic Rarity Multiplier & Non-Linear Scaling
Perlengkapan dijamin memiliki atribut yang berjenjang sesuai kelangkaannya:
- ⚪ **Common (1.0x Base Stat):** 0 Atribut Sekunder Tambahan.
- 🟢 **Uncommon (1.3x Base Stat):** +1 Atribut Sekunder Tambahan.
- 🔵 **Rare (1.8x Base Stat):** +2 Atribut Sekunder Tambahan (*Dipastikan jauh lebih kuat dari Common/Uncommon*).
- 🟣 **Epic (2.5x Base Stat):** +3 Atribut Sekunder Tambahan.
- 🟡 **Legendary (3.6x Base Stat):** +4 Atribut Sekunder Tambahan.

$$\text{Equipment ATK} = (\text{Base ATK} + (\text{iLvl} \times 2)) \times \text{Rarity Multiplier}$$
$$\text{Equipment DEF} = (\text{Base DEF} + (\text{iLvl} \times 1.2)) \times \text{Rarity Multiplier}$$
$$\text{Equipment HP} = (\text{Base HP} + (\text{iLvl} \times 8)) \times \text{Rarity Multiplier}$$
$$\text{Equipment MP} = (\text{Base MP} + (\text{iLvl} \times 6)) \times \text{Rarity Multiplier}$$
