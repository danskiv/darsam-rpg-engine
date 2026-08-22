# Darsam RPG Engine - Game Systems & Mathematical Mechanics (v2.3.3)

## 1. Chapter Progression & Dungeon Floors
Sebelumnya, pergantian bab (*Chapter*) bergantung murni pada respons model AI yang kerap mempertahankan teks `"Chapter 1: The Descent"` meskipun pemain telah melangkah belasan kali.
Di v2.3.3, sistem bab diatur secara terstruktur dan deterministik berdasarkan jumlah langkah (*Milestone Steps*):

| Bab & Lantai | Rentang Langkah (*Steps*) | Nama Bab & Tema Lingkungan | Musuh & Ancaman Utama |
|---|---|---|---|
| **Chapter 1 (Floor 1)** | Langkah `1 – 5` | **The Descent:** Reruntuhan Rongga Makam Runtuh & Lorong Lumut | Hewan buas & serangga gua biasa |
| **Chapter 2 (Floor 1)** | Langkah `6 – 12` | **The Sarcophagus Halls:** Aula Makam Kuno & Altar Terkutuk | Prajurit kerangka & penyihir sesat |
| **Chapter 3 (Floor 2)** | Langkah `13 – 20`| **The Abyssal Waterway:** Kanal Bawah Tanah & Jembatan Rapuh | Lendir asam, monster air & racun |
| **Chapter 4 (Floor 2)** | Langkah `21 – 30`| **The Forgotten Necropolis:** Kota Mati Purba & Toko Terlarang | Pembunuh bayangan & ksatria terkutuk |
| **Chapter 5 (Floor 3)** | Langkah `31+` | **The Archon's Sanctum:** Istana Dewa Kehampaan | Pertarungan Puncak Boss: Lich Lord Malakor |

---

## 2. Mobile Responsive Layout Architecture
- **Baris 1:** Profil Karakter di Kiri + Dropdown Model AI di Kanan (tidak lagi bertubrukan).
- **Baris 2:** Grid 3 Kolom Simetris Berdimensi Seragam (`❤️ HP`, `✨ MP`, `🪙 Gold`).
- **Baris 3:** Bilah Kemajuan EXP (`⭐ EXPERIENCE`).
- **Baris 4:** Tab Navigasi Seimbang 50:50 (`📖 STORY & ACTIONS` vs `🎒 STATS & BACKPACK`).
- **Bantalan Bawah Aman (`pb-32`):** Memastikan pilihan aksi di bagian paling bawah tidak pernah terpotong di tepi layar ponsel.
