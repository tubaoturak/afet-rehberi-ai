"""Sorgu önişleme, normalizasyon ve afet / ilk yardım eş anlamlı & çok dilli genişletme."""

from __future__ import annotations

import re
from rag.hybrid import normalize_turkish

# Afet & İlk Yardım Kök / Eş Anlamlı & Çok Dilli Eşleşmeleri
SYNONYM_RULES: list[tuple[str, list[str]]] = [
    # Suda Boğulma / Drowning / Ertrinken (Öncelikli kural - Heimlich ile karışmaz)
    (r"\b(suda|deniz|havuz|drown|drowning|ertrink)\w*", ["suda boğulma", "suni solunum", "su çıkarma", "suda ilk yardım"]),
    # Boğulma / Cisim Kaçması / Choking / Heimlich / Ersticken
    (r"\b(bogaz|tikan|choking|choke|ersticken|heimlich|soluk\s+boru)\w*", ["heimlich manevrası", "soluk yolu tıkanıklığı", "tam tıkanma", "sırt vuruşu"]),
    # Deprem Bina İçi / Evde / Kapalı Alan
    (r"\b(deprem|sarsinti|zelzele|sallanti)\b.*\b(bina\s+ic|bina\s+ici|bina\s+icinde|evde|odada|iceride|dairede|mutfakta|banyoda)\b|\b(bina\s+ic|bina\s+ici|bina\s+icinde|evde|odada|iceride|dairede|mutfakta|banyoda)\b.*\b(deprem|sarsinti|zelzele|sallanti)\b", ["bina içi", "çök kapan tutun", "sağlam eşya yanı"]),
    # Deprem Açık Alan / Sokak / Park
    (r"\b(deprem|sarsinti|zelzele|sallanti)\b.*\b(acik\s+alan|sokakta|parkta|meydanda|disarida)\b|\b(acik\s+alan|sokakta|parkta|meydanda|disarida)\b.*\b(deprem|sarsinti|zelzele|sallanti)\b|\b(acik\s+alanda\s+deprem|sokakta\s+deprem)\b", ["açık alanda", "binalardan uzaklaşın", "direklerden uzak"]),
    # Deprem Genel / Earthquake / Erdbeben
    (r"\b(zelzele|sarsinti|sallanti|earthquake|erdbeben|quake)\w*", ["deprem", "çök", "kapan", "tutun"]),
    # Enkaz / Debris / Trümmer
    (r"\b(enkaz|gocuk|rubble|debris|truemmer|trapped)\w*", ["enkaz", "sesimi", "duyan", "ritmik", "düdük"]),
    # Kalp Krizi / Heart Attack / Herzinfarkt
    (r"\b(kalp\s+kriz|kriz|heart\s+attack|herzinfarkt)\w*", ["kalp krizi", "göğüs ağrısı", "yarı oturur", "aspirin"]),
    # Kalp Masajı / CPR / Cardiac Arrest / Kalbi Durdu
    (r"\b(cpr|kalp\s+masaj|masaj|cardiac\s+arrest|suni\s+solunum|kalbi?\s+dur)\w*", ["cpr", "kalp masajı", "suni solunum", "30", "2"]),
    # Kopan Uzuv / Parmak Kopması / Amputasyon
    (r"\b(kopan|kopma|kopmas[ıi]|koptu|amputasyon|parmak\s+kop)\w*", ["kopan uzuv", "kopan parmak", "turnike", "buzlu poşet", "suya koymayın"]),
    # Arı / Böcek / Akrep / Yılan Sokması
    (r"\b(arı|ari|b[oö]cek|akrep|y[ıi]lan|soktu|isirdi|sokmas[ıi]|isirmas[ıi])\w*", ["yılan akrep arı böcek sokması", "soğuk kompres", "emmeyin", "iğneyi çıkarın"]),
    # Kanama / Bleeding / Blutung
    (r"\b(kanama|kan|fiskir|damar|bleeding|bleed|blutung|tourniquet)\w*", ["turnike", "baskı", "tampon", "kanama"]),
    # Yanık / Burn / Verbrennung
    (r"\b(yanik|haslan|ates|burn|burns|scald|verbrennung|verbrannt)\w*", ["yanık", "soğuk su", "15-20 dakika", "diş macunu sürmeyin"]),
    # Kırık / Çıkık / Fracture / Knochenbruch
    (r"\b(kirik|cikik|burkul|incin|fracture|broken|dislocation|knochenbruch)\w*", ["atel", "sabitleme", "hareketsiz", "kemik"]),
    # Zehirlenme / Poison / Vergiftung
    (r"\b(zehir|ilac|deterjan|poison|toxic|vergiftung)\w*", ["zehirlenme", "kusturmayın", "114", "uzem"]),
    # Elektrik / Electric Shock / Stromschlag
    (r"\b(elektrik|carpma|akim|electric|shock|stromschlag)\w*", ["elektrik çarpması", "şalter", "kuru tahta"]),
    # Burun Kanaması / Nosebleed / Nasenbluten
    (r"\b(burun|burnu|nosebleed|nasenbluten)\w*", ["burun kanaması", "baş öne", "kanatları sık"]),
    # Hipotermi / Donma / Hypothermia / Erfrierung
    (r"\b(donma|soguk|hipotermi|hypothermia|frostbite|erfrierung)\w*", ["hipotermi", "yavaş ısıtma", "ovalamayın"]),
    # Bayılma / Şok / Faint / Ohnmacht (sok değil, yalnızca şok/bayılma)
    (r"\b(bayil|koma|şok|faint|unconscious|ohnmacht|bewusstlos)\w*", ["şok pozisyonu", "koma pozisyonu", "ayakları 30 cm kaldır"]),
]


def expand_query(query: str) -> str:
    """
    Kullanıcı sorgusundaki halk ağzı / eş anlamlı ve yabancı dil terimlerini Türkçe afet terimleriyle genişletir.
    """
    normalized = normalize_turkish(query)
    additions: list[str] = []

    for pattern, syns in SYNONYM_RULES:
        if re.search(pattern, normalized, re.IGNORECASE):
            for s in syns:
                norm_s = normalize_turkish(s)
                if norm_s not in normalized and s not in additions:
                    additions.append(s)

    if additions:
        return f"{query} {' '.join(additions)}"
    return query
