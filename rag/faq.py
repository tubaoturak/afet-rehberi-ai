"""Hayati acil durumlar için hızlı refleks ve doğrulanmış protokol cevapları (Instant FAQ)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from rag.hybrid import normalize_turkish


@dataclass(frozen=True)
class FastFaqItem:
    patterns: list[str]
    answer: str
    source: str
    answer_en: Optional[str] = None


FAST_FAQ_DATABASE: list[FastFaqItem] = [
    # 1. DEPREM
    FastFaqItem(
        patterns=[
            r"\bcok kapan tutun\b",
            r"\bdeprem\w*",
            r"\bearthquake\b",
            r"\bsismo\b",
            r"\berdbeben\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Deprem Anı Protokolü (Bina İçi)\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Panik yapmayın, koşmayın ve pencerelerden uzak durun.\n"
            "2) Sağlam bir eşyanın (çamaşır makinesi, ağır koltuk yanı) yanında ÇÖK-KAPAN-TUTUN pozisyonu alın.\n"
            "3) Baş ve boynunuzu ellerinizle veya bir yastıkla koruyun.\n"
            "4) Sarsıntı tamamen bitene kadar pozisyonunuzu koruyun.\n\n"
            "⚠️ YAPILMAMASI GEREKENLER:\n"
            "- Asla merdivenlere koşmayın, asansöre binmeyin veya balkona çıkmayın.\n\n"
            "🚨 Sarsıntı bittikten sonra gaz/elektrik vanalarını kapatıp acil durum çantasıyla toplanma alanına geçin."
        ),
        source="afad_deprem.txt",
        answer_en=(
            "🚨 EMERGENCY: Earthquake Indoor Safety Protocol\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Do not panic, do not run, stay away from windows.\n"
            "2) Take DROP - COVER - HOLD ON position next to a sturdy object (heavy sofa, washing machine).\n"
            "3) Protect your head and neck with your arms or a cushion.\n"
            "4) Maintain position until shaking completely stops.\n\n"
            "⚠️ DO NOT:\n"
            "- Never run to stairs, elevators, or balconies during shaking.\n\n"
            "🚨 After shaking stops, shut off gas/electricity and evacuate to the designated assembly area."
        ),
    ),
    # 2. ENKAZ
    FastFaqItem(
        patterns=[
            r"\benkaz\w*",
            r"\bgocuk\w*",
            r"\brubble\b",
            r"\bescombros\b",
            r"\btrummer\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Enkaz Altında Hayatta Kalma Protokolü\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Enerjinizi ve oksijeninizi tasarruflu kullanın; ağzınızı/burnunuzu bir bezle örterek tozu filtreleyin.\n"
            "2) Dışarıdan arama-kurtarma veya iş makinesi sesi duyduğunuzda yakındaki boru veya duvara ritmik vurun (3 kısa, 3 uzun darbe).\n"
            "3) Cebinizde düdük varsa kısa aralıklarla çalın.\n"
            "4) Yalnızca kurtarma ekipleri 'Sesimi duyan var mı?' dediğinde var gücünüzle bağırın.\n\n"
            "⚠️ YAPILMAMASI GEREKENLER:\n"
            "- Sürekli bağırmayın (toz çeker, oksijeni hızla tüketir).\n"
            "- Çakmak veya kibrit yakmayın (gaz kaçağı riski)."
        ),
        source="afad_deprem.txt",
        answer_en=(
            "🚨 EMERGENCY: Trapped Under Rubble Survival Protocol\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Conserve energy and oxygen; cover nose and mouth with cloth to filter dust.\n"
            "2) When you hear rescue sounds, rhythmically tap on nearby pipes or walls (3 short, 3 long taps).\n"
            "3) If you have a whistle, blow in short intervals.\n"
            "4) Shout only when you hear rescuers asking 'Is anyone there?'.\n\n"
            "⚠️ DO NOT:\n"
            "- Do not shout continuously (inhales dust, depletes oxygen quickly).\n"
            "- Do not light matches or lighters (gas leak danger)."
        ),
    ),
    # 3. KLOR GAZI / ÇAMAŞIR SUYU + TUZ RUHU
    FastFaqItem(
        patterns=[
            r"\b(camasir suyu|tuz ruhu|klor gaz)\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Klor Gazı ve Kimyasal Zehirlenme Protokolü\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Gazın bulunduğu kapalı alanda KESİNLİKLE BEKLEMEYİN.\n"
            "- Zehirlenen kişiyi kusturmaya çalışmayın veya süt/yoğurt içirmeyin.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Derhal kapı ve pencereleri açarak gazlı ortamı terk edin ve AÇIK TEMİZ HAVAYA çıkın.\n"
            "2) Ağız ve burnunuzu ıslak bir bez/havlu ile kapatıp derin temiz hava soluyun.\n"
            "3) Göze veya cilde temas varsa en az 15-20 dakika bol suyla yıkayın.\n"
            "4) Derhal 112 Acil Çağrı Merkezi'ni ve 114 UZEM'i (Ulusal Zehir Danışma) arayın."
        ),
        source="afad_kimyasal.txt",
    ),
    # 4. KALP KRİZİ BELİRTİLERİ
    FastFaqItem(
        patterns=[
            r"\bkalp\s+kriz\w*\s+belirti\w*",
            r"\bkalp\s+krizi\s+(nasil|belirt|anlasil)\w*",
            r"\bheart\s+attack\s+symptom\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Kalp Krizi Belirtileri\n\n"
            "🩺 EN YAYGIN KALP KRİZİ BELİRTİLERİ:\n"
            "- Göğüs ortasında 15-20 dakikadan uzun süren ezici, sıkıştırıcı, baskılayıcı ve şiddetli ağrı.\n"
            "- Ağrının sol kola, sol omuza, boyna, çeneye, sırta veya mideye doğru yayılması.\n"
            "- Şiddetli nefes darlığı, soğuk terleme, mide bulantısı, baş dönmesi ve ölüm korkusu (huzursuzluk).\n\n"
            "⚠️ DİKKAT:\n"
            "- Kadınlarda, yaşlılarda ve şeker hastalarında göğüs ağrısı yerine ani nefes darlığı, aşırı halsizlik ve hazımsızlık benzeri mide ağrısı görülebilir.\n\n"
            "🚨 Bu belirtilerden herhangi biri başladığı anda vakit kaybetmeden DERHAL 112 Acil Çağrı Merkezini arayın!"
        ),
        source="kizilay_kalp_cpr.txt",
        answer_en=(
            "🚨 EMERGENCY: Heart Attack Symptoms\n\n"
            "🩺 COMMON HEART ATTACK SYMPTOMS:\n"
            "- Crushing, squeezing, intense chest pressure lasting more than 15-20 minutes.\n"
            "- Pain radiating to the left arm, shoulder, neck, jaw, back, or stomach.\n"
            "- Shortness of breath, cold sweat, nausea, dizziness, and intense anxiety/fear.\n\n"
            "🚨 CALL 112 / 911 IMMEDIATELY at the first sign of these symptoms."
        ),
    ),
    # 5. KALP KRİZİ ANINDA İLK YARDIM (NE YAPILMALI)
    FastFaqItem(
        patterns=[
            r"\bkalp\s+kriz\w*\s+(aninda|geciren|geciriyor|ne yap|nasil yardim|ilk yardim|mudahale)\w*",
            r"\b(kriz|kalp)\s+aninda\s+ne\s+yap\w*",
            r"\bkalp\s+krizi\s+aspirin\b",
            r"\bheart\s+attack\s+(what to do|first aid)\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Kalp Krizi İlk Yardım Protokolü\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Vakit kaybetmeden derhal 112 Acil Çağrı Merkezini arayın veya birine aratın.\n"
            "2) Hastayı hemen rahatlatın; sırtı desteklenmiş YARI OTURUR (Semi-Fowler) pozisyona getirin.\n"
            "3) Solunumu rahatlatmak için kravat, gömlek yakası, kemer gibi dar giysileri gevşetin.\n"
            "4) Hastayı sakinleştirin ve hareket etmesini KESİNLİKLE engelleyin (yürütmeyin, koşturmayın).\n"
            "5) Bilinen aspirin alerjisi veya aktif mide kanaması yoksa 1 adet 300 mg ASPİRİN ÇİĞNETİN (hızlı emilim için çiğnetilmeli).\n"
            "6) Hastanın bilincini ve solunumunu sürekli takip edin; bilinç ve nefes durursa derhal sert zemine alıp CPR (kalp masajı) başlatın.\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Hastayı ASLA ayakta tutmayın, yürütmeyin veya merdiven çıkartmayın (kalbin oksijen tüketimini artırır).\n"
            "- Hastayı sırtüstü düz yatırmayın (akciğer baskısını artırır).\n"
            "- Aspirini suyla yutturmayın; çiğnetin.\n"
            "- Bilinci kapalı veya bulanık kişiye su veya ilaç vermeyin."
        ),
        source="kizilay_kalp_cpr.txt",
        answer_en=(
            "🚨 EMERGENCY: Heart Attack First Aid Protocol\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Call 112 / 911 Emergency immediately.\n"
            "2) Place the victim in a SEMI-UPRIGHT (Semi-Fowler) seated position with back supported.\n"
            "3) Loosen all tight clothing (collar, tie, belt) to ease breathing.\n"
            "4) Keep the patient calm and absolutely still (no walking).\n"
            "5) Unless allergic or experiencing active bleeding, have them CHEW a 300 mg aspirin.\n"
            "6) Monitor breathing and consciousness continuously. If breathing stops, begin CPR immediately.\n\n"
            "⚠️ DO NOT:\n"
            "- Never let the patient walk or climb stairs.\n"
            "- Never lay the patient flat on their back.\n"
            "- Never give food, water, or swallowed pills to an unconscious person."
        ),
    ),
    # 6. BEBEKLERDE KALP MASAJI (CPR)
    FastFaqItem(
        patterns=[
            r"\bbebek\w*\s+(kalp masaj|cpr|kac parmak|nasil yap)\w*",
            r"\b(kalp masaj|cpr)\w*\s+bebek\w*",
            r"\b(kac parmak|iki parmak)\w*\s+bebek\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Bebeklerde (0-1 Yaş) Kalp Masajı (CPR) Protokolü\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Bebeğin ayak tabanına hafifçe vurarak bilinç ve tepkisini kontrol edin.\n"
            "2) 10 saniye solunumu kontrol edin; nefes yoksa derhal 112'yi aratın.\n"
            "3) İki meme ucunu birleştiren hayali çizginin hemen altına İKİ PARMAK (işaret ve orta parmak) yerleştirin.\n"
            "4) Göğüs kalınlığının 1/3'ü kadar (yaklaşık 4 cm) derinlikte, dakikada 100-120 hızında 30 GÖĞÜS BASISI uygulayın.\n"
            "5) Ağzınızla bebeğin HEM AĞZINI HEM BURNUNU kapatacak şekilde 2 hafif kurtarıcı nefes verin.\n"
            "6) 30 Bası : 2 Solunum döngüsünü yardım gelene kadar sürdürün.\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Bebeğe el ayasıyla veya iki elle bası yapmayın (kaburga ve organ hasarı oluşturur).\n"
            "- Bebeğin başını aşırı geriye bükmeyin."
        ),
        source="kizilay_kalp_cpr.txt",
    ),
    # 5. YETİŞKİN KALP MASAJI (CPR)
    FastFaqItem(
        patterns=[
            r"\bkalp\s+masaj\w*",
            r"\bcpr\b",
            r"\bkalbi\s+dur\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Kalp Masajı (CPR) Protokolü\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Derhal 112'yi arayın veya birine aratın; çevrede OED (otomatik defibrilatör) varsa getirtin.\n"
            "2) Hastayı sert ve düz bir zemine sırtüstü yatırın.\n"
            "3) Göğüs kemiğinin ortasına ellerinizi üst üste kenetleyip dik kollarla 5-6 cm çökecek şekilde bası yapın.\n"
            "4) Dakikada 100-120 ritimle 30 KALP MASAJI uygulayın.\n"
            "5) Baş geri-çene yukarı pozisyonu vererek 2 SUNİ SOLUNUM uygulayın (eğitiminiz yoksa sadece aralıksız kalp masajına devam edin).\n"
            "6) 30:2 döngüsünü 112 ekipleri gelene veya hasta tepki verene kadar kesintisiz sürdürün."
        ),
        source="kizilay_kalp_cpr.txt",
    ),
    # 6. HEIMLICH & BOĞULMA
    FastFaqItem(
        patterns=[
            r"\bheimlich\b",
            r"\b(bogaz|bogul|yemek)\w*\s+(kacti|tikan|ilk yardim|ne yap|nasil)\w*",
            r"\btam tikanma\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Tam Soluk Yolu Tıkanması (Heimlich Manevrası)\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Kişi nefes alamıyor, konuşamıyor ve ellerini boynuna götürüyorsa tam tıkanmadır.\n"
            "2) Önce iki kürek kemiği arasına el ayasıyla 5 kez süpürür tarzda kuvvetlice vurun.\n"
            "3) Cisim çıkmazsa arkasına geçip sarılın; bir elinizi yumruk yapıp göbek deliği ile göğüs kemiği arasına koyun.\n"
            "4) Diğer elinizle yumruğunuzu kavrayıp İÇE VE YUKARI doğru 5 kez kuvvetle bastırın (Heimlich Manevrası).\n"
            "5) Cisim çıkana veya kişi bilincini kaybedene kadar 5 sırt vuruşu - 5 Heimlich döngüsünü tekrarlayın.\n"
            "6) Bilinç kapanırsa derhal 112'yi arayıp CPR (kalp masajı) başlatın."
        ),
        source="kizilay_ilkyardim.txt",
        answer_en=(
            "🚨 EMERGENCY: Complete Airway Choking (Heimlich Maneuver)\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) If victim cannot breathe, speak, or cough and clutches neck, airway is completely blocked.\n"
            "2) Stand to the side and give 5 FIRM BACK BLOWS between shoulder blades with the heel of your hand.\n"
            "3) If unblocked, stand behind, place a fist just above navel, grasp with other hand, and give 5 QUICK UPWARD & INWARD ABDOMINAL THRUSTS (Heimlich).\n"
            "4) Repeat 5 back blows : 5 abdominal thrusts until object is expelled.\n"
            "5) If victim becomes unconscious, gently lower to ground, call 112, and begin CPR."
        ),
    ),
    # 7. İNME / FELÇ (FAST TESTİ)
    FastFaqItem(
        patterns=[
            r"\binme\b",
            r"\bfelc\b",
            r"\bfast\s+test\w*",
            r"\byuz\w*\s+kay\w*",
            r"\byuzu\s+kaydi\b",
            r"\bkolu\s+dustu\b",
        ],
        answer=(
            "🚨 ACİL DURUM: İnme ve Felç (FAST Testi) Protokolü\n\n"
            "📋 FAST BELİRTİLERİ VE YAPILACAKLAR:\n"
            "1) **F (Face - Yüz):** Kişiden gülümsemesini isteyin; yüzün bir tarafında sarkma veya ağızda kayma var mı kontrol edin.\n"
            "2) **A (Arms - Kollar):** Her iki kolunu havaya kaldırmasını isteyin; bir kol aşağı düşüyor veya güçsüzlük var mı bakın.\n"
            "3) **S (Speech - Konuşma):** Basit bir cümle söylemesini isteyin; konuşmada pelteklik veya anlamsız kelimeler var mı dinleyin.\n"
            "4) **T (Time - Zaman):** Bu belirtilerden biri bile varsa ZAMAN HAYATİDİR; belirtilerin başladığı saati not edin.\n"
            "5) Derhal 112'yi arayın; hastayı hareket ettirmeden başı hafif yüksekte rahat bir pozisyonda tutun.\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Hastaya ASLA aspirin, tansiyon ilacı, su veya yiyecek vermeyin (kanamalı inmede ölümcül olabilir)."
        ),
        source="kizilay_ozel_ilkyardim.txt",
    ),
    # 8. YANIK SU TOPLAMASI (BÜLLER)
    FastFaqItem(
        patterns=[
            r"\b(su topla|patlat|kabarcik|baloncuk)\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Yanık Su Toplaması (Büller) Protokolü\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Yanık sonrası su toplayan kabarcıkları (bülleri) KESİNLİKLE PATLATMAYIN! (Bu kabarcıklar deriyi mikroplara ve enfeksiyona karşı koruyan doğal steril bariyerdir).\n"
            "- Üzerine yoğurt, diş macunu, salça, zeytinyağı veya merhem sürmeyin.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Yanık bölgesini en az 15-20 dakika tazyiksiz serin/soğuk çeşme suyu altında tutarak soğutun.\n"
            "2) Yanan yerdeki takı ve sıkı giysileri şişme olmadan hemen çıkarın.\n"
            "3) Bölgeyi temiz, nemli veya yapışmayan steril bir bezle gevşekçe örtün.\n"
            "4) Geniş veya derin yanıklarda derhal 112'yi arayın."
        ),
        source="kizilay_ozel_ilkyardim.txt",
    ),
    # 9. BAYILAN / BİLİNCİ KAPALI KİŞİYE SU VERİLİR Mİ?
    FastFaqItem(
        patterns=[
            r"\b(bayil|bilinc\w* kapal\w*)\s+(kisi\w*|biri\w*)?\s*(su|icecek|yemek|hap)\b",
            r"\b(su|icecek)\s+(iciril|veril)\w*",
            r"\bbayil\w*\s+su\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Bayılan / Bilinci Kapalı Kişiye Müdahale\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Bilinci kapalı veya yarı baygın kişiye KESİNLİKLE SU, İÇECEK VEYA YİYECEK VERMEYİN! (Yutma refleksi kaybolduğu için sıvı akciğerlere ve nefes borusuna kaçarak boğulmaya ve ölüme yol açar).\n"
            "- Kişiyi sarsmayın, tokat atmayın veya kolonya/alkol koklatmayın.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Hastayı sırtüstü yatırın ve bacaklarını 30 cm yukarı kaldırın (Şok Pozisyonu).\n"
            "2) Sıkı giysilerini (yaka, kravat, kemer) gevşetin.\n"
            "3) Solunumunu kontrol edin; solunum düzenliyse yan yatış (Koma/İyileşme) pozisyonu verin.\n"
            "4) Solunum durursa derhal 112'yi arayıp CPR (kalp masajı) başlatın."
        ),
        source="kizilay_ilkyardim.txt",
    ),
    # 10. GÖZE BATAN / SAPLANAN CİSİM
    FastFaqItem(
        patterns=[
            r"\b(goze|gozume)\s+(bat|saplan|demir|capak|cam|metal|civ)\w*",
            r"\b(bat|saplan|capak|demir)\w*\s+(goze|gozume)\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Göze Saplanmış Yabancı Cisim Protokolü\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Göze batan veya saplanan cismi (demir, çapak, cam, metal vb.) KESİNLİKLE ÇIKARMAYIN veya oynatmayın!\n"
            "- Göz küresine kesinlikle baskı yapmayın veya ovalamayın.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Cismin etrafına ve gözün üzerine koruyucu bir kağıt bardak, plastik kapak veya koni şeklinde gazlı bez yerleştirerek sabitleyin.\n"
            "2) Gözler senkronize hareket ettiği için sağlam olan DİĞER GÖZÜ DE kapatın (böylece yaralı gözün oynaması engellenir).\n"
            "3) Kazazedeyi sakinleştirin, başını sabit tutun ve derhal 112 Acil Çağrı Merkezini arayın."
        ),
        source="kizilay_goz_kulak_burun.txt",
    ),
    # 11. YILAN / AKREP ISIRIĞI VE KESME / EMME
    FastFaqItem(
        patterns=[
            r"\b(yilan|akrep)\s+(sok|isir)\w*",
            r"\b(yilan|akrep)\w*\s+(emil|kesil|bicak)\w*",
            r"\b(isirik|sokma)\w*\s+(emil|kesil)\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Yılan ve Akrep Sokması İlk Yardımı\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Isırılan bölgeyi bıçakla KESMEYİN, jilet atmayın.\n"
            "- Yarayı ağızla KESİNLİKLE EMİP TÜKÜRMEYİN (zehir ağız içi mukozasından hızla kana karışır).\n"
            "- Kan dolaşımını tamamen durduracak sıkı turnike yapmayın.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Isırılan bölgeyi su ve sabunla nazikçe yıkayın.\n"
            "2) Zehrin yayılmasını yavaşlatmak için uzvu KALP SEVİYESİNİN ALTINDA ve hareketsiz tutun.\n"
            "3) Bölgedeki takıları (yüzük, saat) şişme olmadan çıkarın.\n"
            "4) Beze sarılı soğuk kompres uygulayın ve derhal 112'yi arayın."
        ),
        source="kizilay_ozel_ilkyardim.txt",
    ),
    # 12. ÇIKIK VE KIRIK YERİNE OTURTULUR MU?
    FastFaqItem(
        patterns=[
            r"\b(cikik|omuz|parmak|kirik|kemik)\b.*\b(yerine|oturt|duzelt|cekil|iceri it)\w*",
            r"\bcikik\s+(yerine|nasil)\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Kırık ve Çıkık Müdahale Protokolü\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Kırık veya çıkan kemik/eklemi ASLA YERİNE OTURTMAYA VEYA DÜZELTMEYE ÇALIŞMAYIN! (Damar, sinir kopmalarına ve kalıcı felce yol açar).\n"
            "- Açık kırıkta dışarı çıkan kemik uçlarını KESİNLİKLE içeri itmeyin.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Yaralı uzvu bulunduğu mevcut pozisyonda atel/sert destek ile sabitleyin.\n"
            "2) Ağrı ve şişliği azaltmak için beze sarılı buz/soğuk kompres uygulayın.\n"
            "3) Parmaklarda renk, his ve nabız kontrolü yapın.\n"
            "4) Derhal 112 Acil Çağrı Merkezini arayın."
        ),
        source="kizilay_kemik_eklem.txt",
    ),
    # 13. BURUN KANAMASI
    FastFaqItem(
        patterns=[
            r"\b(burun|burnu|burnum)\w*\s+kan\w*",
            r"\bkan\w*.*(burun|burnu|burnum)\w*",
            r"\bburnum\s+kani\w*",
            r"\bnosebleed\b",
            r"\bhemorragia\s+nasal\b",
            r"\bnasenbluten\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Burun Kanaması İlk Yardımı\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Sakinleşin ve dik bir pozisyonda oturun.\n"
            "2) Başınızı HAFİFÇE ÖNE eğin (asla geriye atmayın).\n"
            "3) Burun kanatlarını baş ve işaret parmağınızla sıkıca 5-10 dakika boyunca kesintisiz sıkın.\n"
            "4) Alına ve enseye soğuk kompres (buz) uygulayabilirsiniz.\n\n"
            "⚠️ YAPILMAMASI GEREKENLER:\n"
            "- Baş geriye atılmaz (kan yutulabilir veya soluk borusuna kaçabilir).\n"
            "- Burun içine pamuk veya peçete tıkamayın.\n\n"
            "🚨 15-20 dakikadan uzun süren veya durdurulamayan şiddetli kanamalarda 112 Acil Çağrı Merkezi'ni arayın."
        ),
        source="kizilay_ozel_ilkyardim.txt",
        answer_en=(
            "🚨 EMERGENCY: Nosebleed First Aid Protocol\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Stay calm and sit upright.\n"
            "2) Lean head SLIGHTLY FORWARD (never tilt backwards).\n"
            "3) Firmly pinch soft parts of the nose with thumb and forefinger for 5-10 minutes continuously.\n"
            "4) Apply cold compress or ice pack to forehead and neck.\n\n"
            "⚠️ DO NOT:\n"
            "- Do not tilt head backward (blood may be swallowed or block airway).\n"
            "- Do not pack cotton or tissues into nasal cavities.\n\n"
            "🚨 If bleeding lasts longer than 15-20 minutes, call 112 / Emergency immediately."
        ),
    ),
    # 14. YANIK GENEL (DİŞ MACUNU / YOĞURT)
    FastFaqItem(
        patterns=[
            r"\byan[ıi]k\w*",
            r"\bhaslan\w*",
            r"\bburns?\b",
            r"\bquemaduras?\b",
            r"\bbrandwunden?\b",
            r"\bverbrennung\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Yanık İlk Yardımı\n\n"
            "⚠️ YAPILMAMASI GEREKENLER:\n"
            "- Yanık üzerine ASLA diş macunu, yoğurt, salça, un, zeytinyağı veya merhem sürmeyin (enfeksiyon riskini artırır ve dokuyu bozar).\n"
            "- Oluşan su kabarcıklarını (bülleri) patlatmayın.\n"
            "- Yapışan kıyafetleri zorla çekip çıkarmayın.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Yanık bölgesini derhal en az 15-20 dakika tazyiksiz serin/soğuk çeşme suyu altında tutun.\n"
            "2) Yanan yerdeki yüzük, bilezik, saat gibi takıları şişme olmadan hemen çıkarın.\n"
            "3) Temiz, nemli ve steril bir bezle üzerini gevşekçe örtün.\n\n"
            "🚨 Geniş veya derin yanıklarda vakit kaybetmeden 112'yi arayın."
        ),
        source="kizilay_ozel_ilkyardim.txt",
        answer_en=(
            "🚨 EMERGENCY: Burn First Aid Protocol\n\n"
            "⚠️ DO NOT:\n"
            "- NEVER apply toothpaste, yogurt, butter, tomato paste, flour, oil, or ointments on burns.\n"
            "- Do not pop burn blisters.\n"
            "- Do not force-pull stuck clothing off burned skin.\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Cool burn under gentle cool tap water for 15-20 minutes immediately.\n"
            "2) Remove rings, watches, and tight items before swelling occurs.\n"
            "3) Cover loosely with clean, sterile, moist cloth.\n\n"
            "🚨 For large, deep, or chemical/electrical burns, call 112 immediately."
        ),
    ),
    # 15. TAVA / YAĞ YANGINI
    FastFaqItem(
        patterns=[
            r"\b(tava|yag)\s+yangin\w*",
            r"\byanan\s+tava\w*",
            r"\byaga\s+su\s+dokul\w*",
            r"\btavaya\s+su\s+dokul\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Mutfak ve Tava (Yağ) Yangını Protokolü\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Yanan kızgın yağa KESİNLİKLE SU DÖKMEYİN! (Su döküldüğünde patlayarak devasa bir alev topu oluşturur ve yangını tüm eve yayar).\n"
            "- Tavayı elinize alıp lavaboya veya balkona taşımaya çalışmayın.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Derhal ısı kaynağını kesin (ocağı veya fırını kapatın).\n"
            "2) Tavanın üzerine metal bir kapak, tepsi veya yangın battaniyesi kapatarak alevlerin oksijenini kesin.\n"
            "3) Tava tamamen soğuyana kadar kapağı açmayın.\n\n"
            "🚨 Alevler mutfak dolaplarına veya davlumbaza sıçrarsa vakit kaybetmeden 112 Acil Çağrı Merkezi'ni arayın."
        ),
        source="afad_yangin_sel.txt",
    ),
    # 16. KANAMA 2. BEZ KURALI VE AĞIR KANAMA BASKISI
    FastFaqItem(
        patterns=[
            r"\bkanama\b.*\b(bez|islandi|ikinci|kaldirm)\w*",
            r"\b(bez\w*|kumas\w*)\s+(islandi|doldu|ikinci)\w*",
            r"\bagir\s+kanama\w*",
            r"\byaraya\s+(nasil\s+)?baski\w*",
            r"\bsevere\s+bleeding\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Ağır Kanama ve Baskı Protokolü\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Kanayan yerin üzerine temiz bir bez/gazlı bez yerleştirip avuç içinizle KESİNTİSİZ BASKI uygulayın.\n"
            "2) İlk bez kanla ıslanırsa bezi KESİNLİKLE KALDIRMAYIN; üzerine doğrudan İKİNCİ bir temiz bez ekleyip baskıyı artırın.\n"
            "3) Kırık şüphesi yoksa kanayan uzvu KALP SEVİYESİNİN YUKARISINA kaldırın.\n"
            "4) Uzuv kopması veya durdurulamayan fışkırır kanamalarda uzvun üst kısmına TURNİKE uygulayın ve uygulama saatini not edin.\n"
            "5) Kazazedeyi sırtüstü yatırıp bacaklarını 30 cm kaldırın (Şok pozisyonu) ve derhal 112'yi arayın."
        ),
        source="kizilay_kanamalar_sok.txt",
        answer_en=(
            "🚨 EMERGENCY: Severe Bleeding and Wound Pressure Protocol\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Apply CONTINUOUS DIRECT PRESSURE over wound with clean sterile gauze or cloth.\n"
            "2) If the first cloth is soaked with blood, DO NOT REMOVE IT; place a SECOND clean cloth directly on top and press firmer.\n"
            "3) If no fracture suspected, elevate bleeding limb ABOVE HEART LEVEL.\n"
            "4) For severe amputation or uncontrollable spurting bleeding, apply a TOURNIQUET and record exact time.\n"
            "5) Lay victim flat, raise legs 30 cm (Shock position), and call 112 / 911 immediately."
        ),
    ),
    # 17. KALP KRİZİ ŞÜPHESİ
    FastFaqItem(
        patterns=[
            r"\bkalp\s+krizi\w*",
            r"\bheart\s+attack\b",
            r"\bgogus\s+agrisi\w*",
            r"\bgoguste\s+baski\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Kalp Krizi Şüphesi Protokolü\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Derhal 112 Acil Çağrı Merkezi'ni arayın veya yakınınızdaki birine aratın.\n"
            "2) Hastayı hemen YARI OTURUR (Semi-Fowler) pozisyona getirin (sırtı destekleyin, dizleri hafif bükün).\n"
            "3) Sıkı giysilerini (kravat, yaka, kemer) derhal gevşetin ve ortamı havalandırın.\n"
            "4) Hastanın bilinci açıksa ve aspirin alerjisi/mide kanaması yoksa 1 adet 300 mg ASPİRİN ÇİĞNETİN.\n"
            "5) Bilinci kapanır ve solunumu durursa derhal KALP MASAJINA (CPR) başlayın.\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Hastayı yürütmeyin, koşturmayın veya merdiven çıkartmayın.\n"
            "- Hastayı sırtüstü düz yatırmayın (kalbin yükü artar ve nefes darlığı şiddetlenir)."
        ),
        source="kizilay_ozel_ilkyardim.txt",
        answer_en=(
            "🚨 EMERGENCY: Suspected Heart Attack Protocol\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Call 112 / 911 Emergency Services immediately.\n"
            "2) Place patient in a SEMI-UPRIGHT (Semi-Fowler) seated position with back supported and knees bent.\n"
            "3) Loosen tight clothing (collar, tie, belt) and ensure open fresh air.\n"
            "4) If conscious and not allergic, give 1 chewable ASPIRIN (300 mg).\n"
            "5) If victim loses consciousness and breathing stops, begin CPR immediately.\n\n"
            "⚠️ DO NOT:\n"
            "- Do not let patient walk or exert energy.\n"
            "- Do not lay patient flat on back."
        ),
    ),
    # 18. ELEKTRİK ÇARPMASI
    FastFaqItem(
        patterns=[
            r"\belektrik\s+carp\w*",
            r"\belectric\s+shock\b",
            r"\bcerayan\s+carp\w*",
        ],
        answer=(
            "🚨 ACİL DURUM: Elektrik Çarpması İlk Yardımı\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Elektrik akımı kesilmeden kazazedeye KESİNLİKLE ÇIPLAK ELLE DOKUNMAYIN (akım size de geçer ve hayati risk oluşturur).\n"
            "- Metal veya ıslak nesnelerle kazazedeye yaklaşmayın.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Derhal ana sigortayı/şalteri kapatarak veya fişi çekerek elektrik akımını kesin.\n"
            "2) Şaltere ulaşılamıyorsa KURU VE YALITKAN bir cisimle (tahta süpürge sapı, kuru plastik, kuru paspas) kazazedenin kabloyla temasını kesin.\n"
            "3) Kazazedenin bilinç ve solunumunu 10 saniye kontrol edin; solunum yoksa derhal 112'yi arayıp CPR (kalp masajı) başlatın.\n"
            "4) Elektrik yanıklarının üzerini temiz, kuru ve steril bir bezle örtün."
        ),
        source="afad_cevresel_aciller.txt",
        answer_en=(
            "🚨 EMERGENCY: Electric Shock First Aid\n\n"
            "⚠️ DO NOT:\n"
            "- NEVER touch victim with bare hands before electrical current is shut off.\n"
            "- Do not approach with metal or wet objects.\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Turn off main electrical breaker or unplug power source immediately.\n"
            "2) If breaker is unreachable, use a DRY, NON-CONDUCTIVE object (wooden broom handle, dry plastic) to separate victim from wire.\n"
            "3) Check consciousness and breathing; if absent, call 112 and begin CPR.\n"
            "4) Cover burn wounds with clean dry sterile dressing."
        ),
    ),
    # 19. SUDA BOĞULMA
    FastFaqItem(
        patterns=[
            r"\bsuda\s+bogul\w*",
            r"\bbogulan\s+(kisi|biri|adam|cocuk)\w*",
            r"\bdrowning\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Suda Boğulma İlk Yardımı\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Kazazedeyi sudan çıkarırken kendi can güvenliğinizi tehlikeye atmayın (can simidi, ip, kürek uzatın).\n"
            "2) Kazazedeyi karaya çıkardıktan sonra sırtüstü yatırın, ağız içindeki yabancı cisim ve yosunları temizleyin.\n"
            "3) Solunumu 10 saniye dinleyin; solunum yoksa derhal 112'yi aratın.\n"
            "4) Suda boğulmalarda önce 5 KURTARICI SUNİ SOLUNUM verin, ardından 30 KALP MASAJI : 2 SOLUNUM döngüsünü kesintisiz uygulayın.\n"
            "5) Kazazedenin ıslak kıyafetlerini çıkarıp kuru bir battaniyeye sararak vücut ısısını koruyun (Hipotermiyi önleyin).\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Karnına basarak veya baş aşağı sallayarak akciğerlerdeki suyu çıkarmaya çalışmayın (mide içeriği akciğere kaçarak boğulmaya yol açar)."
        ),
        source="afad_cevresel_aciller.txt",
        answer_en=(
            "🚨 EMERGENCY: Drowning Victim First Aid\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Ensure rescuer safety; throw lifebuoy, rope or paddle.\n"
            "2) Lay victim flat on firm ground and clear visible mouth debris.\n"
            "3) Check breathing for 10 seconds; if absent, call 112 immediately.\n"
            "4) Give 5 INITIAL RESCUE BREATHS, then perform continuous 30 CHEST COMPRESSIONS : 2 BREATHS cycle.\n"
            "5) Remove wet clothing and wrap in dry blanket to prevent hypothermia.\n\n"
            "⚠️ DO NOT:\n"
            "- Do not squeeze abdomen to expel water."
        ),
    ),
    # 20. SEL VE SU BASKINI
    FastFaqItem(
        patterns=[
            r"\bsel\s+uyari\w*",
            r"\bsel\s+aninda\w*",
            r"\bsu\s+baskini\w*",
            r"\bselde\s+ne\s+yap\w*",
            r"\bflood\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Sel ve Su Baskını Güvenlik Protokolü\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Sel veya taşkın uyarısı alındığında derhal bodrum ve zemin katları boşaltıp binanın üst katlarına veya en yüksek güvenli tepelere çıkın.\n"
            "2) Su basma riskine karşı ana elektrik şalterini, doğalgaz ve su vanalarını derhal kapatın.\n"
            "3) Sel sularının içine kesinlikle girmeyin; sadece 15 cm derinliğindeki hızlı akan su bir insanı devirip sürükleyebilir.\n"
            "4) Sel sularının bastığı yollarda ve köprülerde kesinlikle araç sürmeyin; aracınız suda stop ederse hemen terk edip araç tavanına veya yüksek noktaya çıkın.\n"
            "5) Suya temas eden elektrik direkleri ve kopmuş kablolardan en az 10-15 metre uzakta durun.\n\n"
            "🚨 Mahsur kalındığında veya yaralanma durumunda derhal 112 Acil Çağrı Merkezi'ni arayın."
        ),
        source="afad_yangin_sel.txt",
        answer_en=(
            "🚨 EMERGENCY: Flood and Flash Flood Safety Protocol\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Evacuate basements and ground floors immediately to higher floors or higher ground.\n"
            "2) Shut off main electricity breaker, gas, and water valves.\n"
            "3) Never walk into flood waters (15 cm of moving water can knock down an adult).\n"
            "4) Never drive through flooded roads or bridges; if car stalls, climb onto car roof.\n"
            "5) Stay at least 15 meters away from downed power lines and flooded poles.\n\n"
            "🚨 If trapped or injured, call 112 / Emergency Services immediately."
        ),
    ),
    # 21. YANGIN SIRASINDA TAHLİYE
    FastFaqItem(
        patterns=[
            r"\byangin\s+sirasinda\w*",
            r"\byangin\s+aninda\w*",
            r"\byangin\s+ciktiginda\w*",
            r"\bevimde\s+yangin\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Bina İçi Yangın ve Duman Tahliye Protokolü\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Yangını fark ettiğiniz anda derhal 112 Acil Çağrı Merkezini arayın ve çevrenizdekileri bağırarak uyarın.\n"
            "2) Duman tavana yükseldiği için derhal yere çömelin veya emekleyerek en temiz hava tabakasına yakın hareket edin.\n"
            "3) Ağız ve burnunuzu ıslak bir bez, havlu veya giysinizle kapatıp nefes alın.\n"
            "4) Kapıları açmadan önce elinizin tersiyle kapı kolunu kontrol edin; sıcaksa kapıyı kesinlikle açmayın.\n"
            "5) Yangın tahliye merdivenlerini kullanarak binayı sakince terk edin.\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Asla asansörleri kullanmayın (baca etkisiyle duman dolar veya elektrik kesintisinde mahsur kalırsınız).\n"
            "- Kıyafetiniz alev alırsa asla koşmayın; derhal DUR - YAT - YUVARLAN kuralını uygulayın."
        ),
        source="afad_yangin_sel.txt",
        answer_en=(
            "🚨 EMERGENCY: Indoor Fire and Smoke Evacuation Protocol\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) Call 112 / Emergency immediately and shout to alert others.\n"
            "2) Stay low and crawl under smoke near floor level.\n"
            "3) Cover mouth and nose with a damp cloth or clothing.\n"
            "4) Feel door handles with back of hand before opening; if hot, keep door closed.\n"
            "5) Evacuate calmly using fire escape stairs.\n\n"
            "⚠️ DO NOT:\n"
            "- Never use elevators.\n"
            "- If clothes catch fire, STOP - DROP - ROLL."
        ),
    ),
    # 22. ZEHİRLENME ACİL (GENEL)
    FastFaqItem(
        patterns=[
            r"\bzehirlen\w*\s+kustur\w*",
            r"\bzehirlenme\s+durumunda\w*",
            r"\bpoisoning\b",
        ],
        answer=(
            "🚨 ACİL DURUM: Zehirlenme İlk Yardımı\n\n"
            "⚠️ KESİNLİKLE YAPILMAMASI GEREKENLER:\n"
            "- Zehirlenen kişiyi KESİNLİKLE KUSTURMAYIN (özellikle kimyasal, asit, deterjan, çamaşır suyu zehirlenmelerinde kusmuk yemek borusunu ikinci kez yakarak deler).\n"
            "- Zehirlenen kişiye yoğurt, süt veya sıvı içirmeyin.\n\n"
            "📋 ADIM ADIM YAPILACAKLAR:\n"
            "1) Gaz zehirlenmesinde kazazedeyi derhal açık temiz havaya çıkarın.\n"
            "2) Cilde veya göze temas varsa en az 15-20 dakika bol suyla yıkayın.\n"
            "3) Derhal 114 UZEM'i (Ulusal Zehir Danışma Merkezi) ve 112 Acil Çağrı Merkezi'ni arayın.\n"
            "4) Zehirlenmeye yol açan maddenin ambalajını veya etiketini sağlık ekiplerine göstermek üzere saklayın."
        ),
        source="afad_kimyasal.txt",
        answer_en=(
            "🚨 EMERGENCY: Poisoning First Aid Protocol\n\n"
            "⚠️ DO NOT:\n"
            "- DO NOT INDUCE VOMITING (especially for corrosive chemicals, detergents, bleach, acids; vomiting burns esophagus twice).\n"
            "- Do not give milk, yogurt, or drinks without poison center guidance.\n\n"
            "📋 STEP-BY-STEP ACTIONS:\n"
            "1) For inhaled toxic gases, move victim to FRESH OPEN AIR immediately.\n"
            "2) For skin/eye contact, flush with running water for 15-20 minutes.\n"
            "3) Call Poison Control and 112 / 911 immediately.\n"
            "4) Save product bottle or packaging for doctors."
        ),
    ),
]


def match_fast_faq(query: str, lang: str = "tr") -> Optional[tuple[str, str]]:
    """
    Sorguyu acil durum kritik refleks veritabanıyla eşleştirir.
    
    Returns:
        (cevap, kaynak_adi) veya None
    """
    norm = normalize_turkish(query)
    for item in FAST_FAQ_DATABASE:
        for pat in item.patterns:
            if re.search(pat, norm):
                if lang == "en" and item.answer_en:
                    return item.answer_en, item.source
                return item.answer, item.source
    return None
