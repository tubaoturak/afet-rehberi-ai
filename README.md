# 🚨 AfetRehberi AI — Çevrimdışı Acil Durum & İlk Yardım RAG Asistanı

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Offline First](https://img.shields.io/badge/Offline-100%25_Air--Gapped-green)](#)
[![Tests](https://img.shields.io/badge/Tests-20%2F20_Passed-brightgreen)](#)

> **AFAD ve Türk Kızılayı** resmi protokollerine dayalı, tamamen çevrimdışı (offline) çalışan, hibrit vektör aramalı (Okapi BM25 + Vektör Cosine), anlık refleksli ve çok dilli acil durum karar destek sistemi.

---

## 📱 Genel Bakış ve Mimari

Afet ve acil durumlarda internet bağlantısının kesilebileceği veya baz istasyonlarının çökebileceği senaryolar düşünülerek geliştirilmiştir. Dil modelleri, gömme (embedding) algoritmaları ve SQLite vektör veritabanı tamamen yerel sistemde çalışır; **hiçbir dış bulut API'sine bağımlılığı yoktur.**

```
┌────────────────────────────────────────────────────────┐
│               React + Vite Mobil Arayüz                │
│    (3 Sekmeli Mobil UI, Sesli STT/TTS, Canlı Yükleme)  │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP POST /api/chat/stream (SSE)
┌───────────────────────────▼────────────────────────────┐
│              FastAPI + Hibrit RAG Motoru               │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ⚡ Fast FAQ Refleks Motoru (0.0 ms Anında Yanıt)  │  │
│  │    (Deprem, Yanık, CPR, Heimlich, Turnike vb.)   │  │
│  └────────────────────────┬─────────────────────────┘  │
│                           │ (Gerekirse Hibrit RAG)     │
│  ┌────────────────────────▼─────────────────────────┐  │
│  │ 🔍 Hibrit Sıralama Füzyonu (BM25 + Cosine Top-K)  │  │
│  │    SQLite Vektör DB (424 Kurumsal Bilgi Bloğu)   │  │
│  └────────────────────────┬─────────────────────────┘  │
│                           │                            │
│  ┌────────────────────────▼─────────────────────────┐  │
│  │ 🧠 Microsoft Foundry Local (Phi-3.5-mini-instruct)│  │
│  │    Kompakt & Filtreli Türkçe İlk Yardım Promptu  │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## ✨ Temel Özellikler

1. **⚡ Fast FAQ (0 ms Kritik Refleks):**
   - Hayati tehlike arz eden durumlarda (Burun Kanaması, Çök-Kapan-Tutun, Boğulma/Heimlich, Tava Yangını, Bebek/Yetişkin Kalp Masajı, İnme/FAST, Yılan Sokması, Çıkık vb.) beklemeden **0.001 saniyede** doğrulanmış adımları sunar.
2. **🔍 Hibrit Arama (Okapi BM25 + Qwen3 0.6B Vektör):**
   - Vektör anlamsal araması ile BM25 anahtar kelime eşleştirmesini birleştirir. Eş anlamlı kelimeleri (ör. *zelzele -> deprem*) otomatik genişletir.
3. **🛡️ Güçlendirilmiş Kapsam Dışı & Halüsinasyon Kalkanı:**
   - Günlük hava durumu, sohbet, tarih, yemek tarifleri gibi afet veya ilk yardım dışı sorularda uydurma yapmaz, sıfır kaynak atfı ile nazikçe kapsam dışı olduğunu bildirir.
4. **📡 Gerçek Zamanlı SSE Token Akışı (Streaming):**
   - `/api/chat/stream` uç noktası üzerinden Server-Sent Events (SSE) ile daktilo efektli anlık yanıt akışı sağlar.
5. **📑 Dinamik Kılavuz Yükleme (Runtime Ingest):**
   - Arayüzdeki **Kılavuzlar (Guides)** sekmesinden yeni `.txt` ve `.md` afet protokolleri sunucu durdurulmadan (Zero-Downtime) anında yüklenir, vektörleştirilir ve `./data` klasöründe kalıcı hale getirilir.
6. **📱 3 Sekmeli Mobil Navigasyon & Çok Dillilik (TR / EN):**
   - **Anasayfa (Home)**: Hızlı acil durum kartları ve 112 Acil Arama.
   - **Acil Asistan (AI Assistant)**: Sesli ve yazılı interaktif RAG sohbeti, daktilo akışı ve kaynak görüntüleyici.
   - **Kılavuzlar (Guides)**: Aktif resmi protokol listesi ve canlı doküman yükleyici.
   - Tek tıkla Türkçe ve İngilizce dilleri arasında tam senkronize geçiş.
7. **🎙️ Sesli Etkileşim (STT & TTS):**
   - Web Speech Recognition ile sesli soru sorma ve Web Speech Synthesis ile sesli ilk yardım dinleme desteği.

---

## 🚀 Hızlı Başlangıç (Docker ile Tek Komut)

Projeyi herhangi bir bilgisayarda ayağa kaldırmak için tek komut yeterlidir:

```bash
docker compose up --build
```

* 🌐 **Mobil Web Arayüzü:** [http://localhost:8000](http://localhost:8000)
* 📖 **API Dokümantasyonu (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
* 🩺 **Sistem Sağlık Durumu:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

*(Not: İlk çalıştırmada model ağırlıkları otomatik indirilir ve `foundry_models` Docker volume'ünde saklanır. Sonraki açılışlar tamamen offline gerçekleşir.)*

---

## 📡 API Uç Noktaları (REST & SSE)

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Sistem ve model sağlık durumu kontrolü |
| `POST` | `/api/chat` | Standart REST JSON tabanlı acil durum RAG sorgusu |
| `POST` | `/api/chat/stream` | Gerçek zamanlı SSE token daktilo akışı |
| `POST` | `/api/upload` | Sıfır kesintili (Zero-Downtime) yeni afet dokümanı yükleme ve indeksleme |

---

## 💻 Yerel Geliştirme (Docker Olmadan)

### Gereksinimler:
- Python 3.10+
- Node.js 18+

### Adımlar:
```bash
# 1. Sanal ortam oluşturun ve bağımlılıkları kurun
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
npm install

# 2. Ön yüzü derleyin (veya geliştirme sunucusunu çalıştırın: npm run dev)
npm run build

# 3. Bilgi tabanını indeksleyin
python main.py ingest

# 4. Sunucuyu başlatın
python main.py serve --host 0.0.0.0 --port 8000
```

---

## 🧪 Testleri Çalıştırma

Projede bulunan 20 birim testini ve senaryo matrisini çalıştırmak için:

```bash
# Docker içinde birim testleri çalıştırma (20/20 PASSED)
docker exec afet_rehberi pytest -v

# Yerel ortamda çalıştırma
pytest -v
```

---

## 📂 Proje Dizin Yapısı

```
afet_project_final/
├── data/                      # 10 adet zenginleştirilmiş AFAD & Kızılay metin dosyaları
│   ├── afad_deprem.txt
│   ├── afad_yangin_sel.txt
│   ├── afad_cevresel_aciller.txt
│   ├── afad_kimyasal.txt
│   ├── kizilay_ilkyardim.txt
│   ├── kizilay_goz_kulak_burun.txt
│   ├── kizilay_kalp_cpr.txt
│   ├── kizilay_kanamalar_sok.txt
│   ├── kizilay_kemik_eklem.txt
│   └── kizilay_ozel_ilkyardim.txt
├── docker/                    # Konteyner başlangıç betiği (entrypoint.sh)
├── rag/                       # RAG çekirdeği ve algoritmalar
│   ├── api.py                 # FastAPI backend uç noktaları & SSE streaming
│   ├── config.py              # Sistem yapılandırma parametreleri
│   ├── db.py                  # SQLite vektör veritabanı & önbellek
│   ├── faq.py                 # 0 ms acil durum refleks motoru
│   ├── foundry_runtime.py     # Microsoft Foundry Local entegrasyonu
│   ├── hybrid.py              # Okapi BM25 & Rank Fusion algoritması
│   ├── ingest.py              # Başlık duyarlı chunking & embedding motoru
│   ├── pipeline.py            # Uçtan uca RAG boru hattı & Kapsam dışı kalkanı
│   ├── prompts.py             # Küçük model optimizasyonlu sistem kuralları
│   ├── query.py               # Eş anlamlı & çok dilli sorgu genişletici
│   └── retrieval.py           # Kosinüs ve hibrit filtreleme
├── src/                       # React + Vite mobil telefon arayüzü
├── tests/                     # Kapsamlı otomatik test senaryoları (Pytest)
├── .env.example               # Güvenli ortam değişkenleri şablonu
├── .gitignore                 # GitHub ignore filtreleri
├── Dockerfile                 # Çok aşamalı (multi-stage) üretim Dockerfile'ı
├── docker-compose.yml         # Tek komutla orkestrasyon
├── main.py                    # CLI giriş noktası (ingest, serve, chat, ask)
├── package.json               # Ön yüz bağımlılıkları
└── requirements.txt           # Python bağımlılıkları
```

---

## 📑 Bilgi Tabanı Kapsamı

Bilgi tabanında toplam **424 yüksek yoğunluklu bilgi bloğu** bulunmaktadır:
1. **AFAD Deprem ve Enkaz:** Çök-kapan-tutun, enkaz altı ritmik vuruş, tahliye, toplanma alanları.
2. **AFAD Yangın ve Sel:** Tava yağ yangını, duman tahliyesi, yangın tüpü PASS, sel tahliyesi.
3. **AFAD Çevresel Aciller:** Yıldırım çarpması, çığ, heyelan, fırtına, sıcak çarpması.
4. **AFAD Kimyasal & KBRN:** Klor gazı, asit/baz teması, gaz sızıntısı, sığınak koruması.
5. **Kızılay Temel İlk Yardım:** Bilinç ve solunum kontrolü, Heimlich, şok ve koma pozisyonu.
6. **Kızılay Duyu Organları:** Göze batan cisimler, kulak/burun yabancı cisim ilk yardımı.
7. **Kızılay CPR & Kalp:** Yetişkin/çocuk/bebek kalp masajı, OED defibrilatör kullanımı, kalp krizi.
8. **Kızılay Kanama ve Şok:** Doğrudan baskı, 2. bez kuralı, turnike (saat yazımı), iç kanama.
9. **Kızılay Kırık ve Çıkık:** Atel bağlama, çıkık yerine oturtmama kuralı, omurga tespiti.
10. **Kızılay Özel Durumlar:** Burun kanaması, FAST inme testi, zehirlenme (114 UZEM), yılan/akrep sokması, yanıklar.

