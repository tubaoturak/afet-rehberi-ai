"""Tam senaryo matrisi terminal testi."""

import json
import time
import urllib.request

TESTS = [
    # Kategori 1: Fast FAQ Refleksleri (0ms)
    ("1.1 Fast FAQ: Burun Kanaması", "burnum kanıyor"),
    ("1.2 Fast FAQ: Deprem Çök Kapan", "çök kapan tutun nasıl yapılır"),
    ("1.3 Fast FAQ: Tava Yangını", "yanan tavaya su dökülür mü"),
    ("1.4 Fast FAQ: Kalp Masajı", "kalp masajı nasıl yapılır"),
    ("1.5 Fast FAQ: Heimlich Boğulma", "boğazına yemek kaçtı nefes alamıyor"),

    # Kategori 2: Spesifik Protokoller
    ("2.1 Spesifik: Kanama 2. Bez", "Kanama durmuyor, ilk koyduğum bez tamamen ıslandı ne yapmalıyım?"),
    ("2.2 Spesifik: Göze Batan Cisim", "Göze demir çapak battı, nasıl çıkarırım?"),
    ("2.3 Spesifik: Çamaşır Suyu + Tuz Ruhu", "Çamaşır suyu ile tuz ruhunu karıştırdım nefes alamıyorum ne yapmalıyım?"),
    ("2.4 Spesifik: Bebek Kalp Masajı", "Bebeklerde kalp masajı kaç parmakla ve nereye yapılır?"),
    ("2.5 Spesifik: İnme FAST Testi", "İnme geçirdiğini nasıl anlarım (FAST testi)?"),

    # Kategori 3: Yanlış İnanışlar & Tuzak Sorular
    ("3.1 Tuzak: Yanık Su Toplaması", "Yanık su topladı, patlatmalı mıyım?"),
    ("3.2 Tuzak: Yılan Sokması Kesme/Emme", "Yılan soktuğunda yarayı bıçakla kesip emmeli miyim?"),
    ("3.3 Tuzak: Bayılan Kişiye Su", "Bayılan veya bilinci kapalı kişiye su içirilir mi?"),
    ("3.4 Tuzak: Çıkık Yerine Oturtma", "Çıkık olan omuzu kendim yerine oturtmaya çalışayım mı?"),

    # Kategori 4: Kapsam Dışı
    ("4.1 Kapsam Dışı: Yemek Tarifi", "Bana çikolatalı sufle tarifi verir misin?"),
    ("4.2 Kapsam Dışı: Genel Kültür", "İstanbul'un fethi hangi tarihte gerçekleşti?"),

    # Kategori 5: Çok Dilli
    ("5.1 Çok Dilli: İngilizce Yanık", "How to treat a burn?"),
    ("5.2 Çok Dilli: Almanca Burun", "Was tun bei Nasenbluten?"),
]

def main():
    print("=" * 80)
    print("🚑 AFET REHBERİ — OTOMATİK SENARYO MATRİSİ TESTİ")
    print("=" * 80)

    for i, (name, q) in enumerate(TESTS, start=1):
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/chat",
            data=json.dumps({"query": q}).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dur = data.get("elapsedSeconds", round(time.time() - t0, 3))
                is_faq = data.get("isFastFaq", False)
                out_scope = data.get("outOfScope", False)
                lang = data.get("detectedLang", "tr")
                ans = data.get("answer", "").strip()
                sources = [s.get("source") for s in data.get("sources", []) if s.get("source")]

                print("-" * 80)
                print(f"[{i}/{len(TESTS)}] {name}")
                print(f"📌 Soru: {q}")
                print(f"⏱️ Süre: {dur} sn | ⚡ FastFAQ: {is_faq} | 🛡️ Kapsam Dışı: {out_scope} | 🌐 Dil: {lang}")
                print(f"📚 Kaynak: {', '.join(sources) if sources else 'Yok (Kapsam Dışı)'}")
                print("📝 Yanıt:")
                print(ans)
                print()
        except Exception as e:
            print(f"❌ [{i}/{len(TESTS)}] {name} HATA: {e}")

if __name__ == "__main__":
    main()
