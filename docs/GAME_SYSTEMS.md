# Darsam RPG Engine - Game Systems & Mathematical Mechanics (v2.4.2)

## 1. Dynamic Infinite Chapter & Floor Milestone Scaling
Sebelumnya, tabel bab terkunci di batas maksimal Chapter 5 (langkah 45+), sehingga ketika pemain mencapai langkah ke-100+, status bab tetap terkunci di Chapter 5 selamanya.
Di v2.4.2, sistem bab diubah menjadi **Formula Progresi Tak Terbatas (*Infinite Milestone Scaling*)**:

$$\text{Chapter Number} = \left\lfloor \frac{\text{Steps} - 1}{8} \right\rfloor + 1$$
$$\text{Floor Depth} = \min\left(5, \max\left(1, \left\lfloor \frac{\text{Chapter Number} - 1}{3} \right\rfloor + 1\right)\right)$$

Setiap **8 Langkah Penjelajahan**, bab akan otomatis berganti ke babak baru dengan tema lantai yang semakin dalam dan berbahaya:
1. **Floor 1 (Lantai 1 - Makam Atas):** *The Descent*, *The Sarcophagus Halls*, *The Bone Crypts*, *The Weeping Catacombs*.
2. **Floor 2 (Lantai 2 - Kanal Bawah Tanah):** *The Abyssal Waterway*, *The Submerged Ruins*, *The Sunken Cistern*, *The Venomous Depths*.
3. **Floor 3 (Lantai 3 - Kubah Kegelapan):** *The Forgotten Necropolis*, *The Obsidian Mausoleum*, *The Archon's Sanctum*, *The Blood-Forged Citadel*.
4. **Floor 4 (Lantai 4 - Labirin Kehampaan):** *The Void Chasm*, *The Astral Rift*, *The Hall of Shifting Realities*, *The Singularity Gate*.
5. **Floor 5 (Lantai 5 - Kuil Penciptaan Purba):** *The Primordial Sanctum*, *The Crown of Eternity*, *The Genesis Vault*, *The Transcendent Apex*.
