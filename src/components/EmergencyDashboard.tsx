import React from 'react';
import { 
  Phone, 
  Flame, 
  Activity, 
  ShieldAlert, 
  Droplet, 
  HeartPulse, 
  Zap, 
  AlertTriangle, 
  Waves, 
  Bug, 
  Wind, 
  Search,
  MessageSquareText,
  Thermometer,
  Stethoscope
} from 'lucide-react';

interface EmergencyDashboardProps {
  onSelectQuery: (query: string) => void;
  onOpenChat: () => void;
  lang: 'tr' | 'en' | 'ar' | 'es' | 'de';
}

const DASHBOARD_TEXTS = {
  tr: {
    heroTitle: 'Acil Durum & İlk Yardım Rehberi',
    heroSub: 'Hayati tehlike anında saniyeler önemlidir. Aşağıdaki hızlı kartlardan müdahale protokolünü seçin veya yapay zeka asistanına sorun.',
    speedDialTitle: 'Acil Hızlı Arama Numaraları',
    categoriesTitle: 'Acil Müdahale Kategorileri',
    askAiBtn: 'Yapay Zeka Asistanına Sor',
    searchPlaceholder: 'Acil durum veya semptom arayın (ör: Burun kanaması, Kalp krizi...)'
  },
  en: {
    heroTitle: 'Emergency & First Aid Guide',
    heroSub: 'Seconds matter in life-threatening situations. Select an action protocol below or consult our AI assistant.',
    speedDialTitle: 'Emergency Speed Dial Numbers',
    categoriesTitle: 'Emergency Response Categories',
    askAiBtn: 'Ask AI Assistant',
    searchPlaceholder: 'Search emergency or symptom (e.g. Nosebleed, Heart attack...)'
  },
  ar: {
    heroTitle: 'دليل الطوارئ والإسعافات الأولية',
    heroSub: 'الثواني حاسمة في الحالات المهددة للحياة. اختر بروتوكول التدخل أدناه أو اسأل المساعد الذكي.',
    speedDialTitle: 'أرقام الاتصال السريع بالطوارئ',
    categoriesTitle: 'فئات الاستجابة للطوارئ',
    askAiBtn: 'اسأل المساعد الذكي',
    searchPlaceholder: 'ابحث عن حالة طوارئ (مثل: نزيف الأنف، نوبة قلبية...)'
  },
  es: {
    heroTitle: 'Guía de Emergencia y Primeros Auxilios',
    heroSub: 'Los segundos cuentan en situaciones de riesgo vital. Seleccione un protocolo de acción o consulte al asistente IA.',
    speedDialTitle: 'Números de Marcado Rápido de Emergencia',
    categoriesTitle: 'Categorías de Respuesta a Emergencias',
    askAiBtn: 'Consultar al Asistente IA',
    searchPlaceholder: 'Buscar emergencia o síntoma (ej: Sangrado nasal, Ataque al corazón...)'
  },
  de: {
    heroTitle: 'Notfall- & Erste-Hilfe-Leitfaden',
    heroSub: 'Sekunden zählen in lebensbedrohlichen Situationen. Wählen Sie ein Notfallprotokoll oder fragen Sie den KI-Assistenten.',
    speedDialTitle: 'Notruf-Schnellwahlnummern',
    categoriesTitle: 'Notfall-Reaktionskategorien',
    askAiBtn: 'KI-Assistenten fragen',
    searchPlaceholder: 'Notfall oder Symptom suchen (z. B. Nasenbluten, Herzinfarkt...)'
  }
};

interface EmergencyCard {
  id: string;
  icon: any;
  title: Record<string, string>;
  desc: Record<string, string>;
  query: Record<string, string>;
  badgeColor: string;
}

const EMERGENCY_CARDS: EmergencyCard[] = [
  {
    id: 'nosebleed',
    icon: Droplet,
    title: {
      tr: 'Burun Kanaması',
      en: 'Nosebleed First Aid',
      ar: 'نزيف الأنف (الرعاف)',
      es: 'Hemorragia Nasal',
      de: 'Nasenbluten Erste Hilfe'
    },
    desc: {
      tr: 'Baş öne eğilmeli mi? Doğru baskı ve müdahale adımları.',
      en: 'Correct head positioning and pressure steps for nosebleeds.',
      ar: 'الوضعية الصحيحة للرأس وحركات الضغط لتوقف النزيف.',
      es: 'Posición correcta de la cabeza y pasos de presión.',
      de: 'Kopfhaltung und Druckpunkte bei Nasenbluten.'
    },
    query: {
      tr: 'Burnum kanıyor, ne yapmalıyım?',
      en: 'How to stop a nosebleed?',
      ar: 'كيف أوقف نزيف الأنف؟',
      es: '¿Cómo detener una hemorragia nasal?',
      de: 'Wie stoppe ich Nasenbluten?'
    },
    badgeColor: 'bg-red-500/10 text-red-500 border-red-500/30'
  },
  {
    id: 'heart_attack',
    icon: HeartPulse,
    title: {
      tr: 'Kalp Krizi Şüphesi',
      en: 'Heart Attack Protocol',
      ar: 'شبهة نوبة قلبية',
      es: 'Sospecha de Infarto',
      de: 'Verdacht auf Herzinfarkt'
    },
    desc: {
      tr: 'Göğüs ağrısı, nefes darlığı ve acil pozisyonlama.',
      en: 'Chest pain, shortness of breath, and CPR readiness.',
      ar: 'ألم الصدر وضيق التنفس والوضعية الصحيحة.',
      es: 'Dolor en el pecho y primeros auxilios inmediatos.',
      de: 'Brustschmerz, Atemnot und Notfalllagerung.'
    },
    query: {
      tr: 'Kalp krizi belirtilerinde ilk yardım nasıl yapılır?',
      en: 'First aid steps for heart attack symptoms?',
      ar: 'ما هي الإسعافات الأولية للنوبة القلبية؟',
      es: '¿Primeros auxilios ante un infarto?',
      de: 'Erste Hilfe bei Herzinfarkt?'
    },
    badgeColor: 'bg-rose-500/10 text-rose-500 border-rose-500/30'
  },
  {
    id: 'heavy_bleeding',
    icon: Activity,
    title: {
      tr: 'Ağır Yara Kanaması',
      en: 'Severe Wound Bleeding',
      ar: 'النزيف الشديد من الجروح',
      es: 'Hemorragia Severa',
      de: 'Schwere Wundblutung'
    },
    desc: {
      tr: 'Doğrudan baskı, tamponlama ve turnike kuralları.',
      en: 'Direct pressure, wound packing, and tourniquet rules.',
      ar: 'الضغط المباشر على الجرح وقواعد العاصبة.',
      es: 'Presión directa y reglas para el torniquete.',
      de: 'Direkter Druck und Regeln für Abbindungen.'
    },
    query: {
      tr: 'Ağır kanamada yaraya nasıl baskı uygulanır?',
      en: 'How to apply pressure to a severe bleeding wound?',
      ar: 'كيف اضغط على جرح شديد النزيف؟',
      es: '¿Cómo aplicar presión en hemorragias graves?',
      de: 'Wie wird eine schwere Wundblutung versorgt?'
    },
    badgeColor: 'bg-red-600/10 text-red-600 border-red-600/30'
  },
  {
    id: 'choking',
    icon: Stethoscope,
    title: {
      tr: 'Tıkanma & Heimlich',
      en: 'Choking & Heimlich',
      ar: 'الاختناق ومناورة هيمليخ',
      es: 'Atragantamiento (Heimlich)',
      de: 'Erstickungsanfall (Heimlich)'
    },
    desc: {
      tr: 'Nefes alamayan kişide sırta vurma ve bası tekniği.',
      en: 'Back blows and abdominal thrusts for airway obstruction.',
      ar: 'ضربات الظهر وضغطات البطن لإزالة انسداد التنفس.',
      es: 'Golpes en la espalda y compresiones abdominales.',
      de: 'Rückenschläge und Oberbauchkompressionen.'
    },
    query: {
      tr: 'Boğazına cisim kaçan kişiye Heimlich nasıl yapılır?',
      en: 'How to perform Heimlich maneuver on choking victim?',
      ar: 'كيف أجرى مناورة هيمليخ لشخص مختنق؟',
      es: '¿Cómo hacer la maniobra de Heimlich?',
      de: 'Wie führt man das Heimlich-Manöver aus?'
    },
    badgeColor: 'bg-amber-500/10 text-amber-500 border-amber-500/30'
  },
  {
    id: 'earthquake',
    icon: ShieldAlert,
    title: {
      tr: 'Deprem & Enkaz',
      en: 'Earthquake & Rubble',
      ar: 'الزلزال والبقاء تحت الأنقاض',
      es: 'Terremoto y Escombros',
      de: 'Erdbeben & Trümmer'
    },
    desc: {
      tr: 'Çök-kapan-tutun ve enkaz altı hayatta kalma.',
      en: 'Drop-cover-hold on and rubble survival steps.',
      ar: 'الإحتماء وتكتيكات البقاء تحت الأنقاض.',
      es: 'Agáchate, cúbrete y supervivencia en escombros.',
      de: 'Verhaltensregeln bei Beben und Rettungssignale.'
    },
    query: {
      tr: 'Deprem anında ve enkaz altında ne yapılmalı?',
      en: 'What to do during an earthquake and if trapped under rubble?',
      ar: 'ماذا أفعل أثناء الزلزال وتعت الأنقاض؟',
      es: '¿Qué hacer durante un sismo y si quedo atrapado?',
      de: 'Was tun bei Erdbeben und unter Trümmern?'
    },
    badgeColor: 'bg-orange-500/10 text-orange-500 border-orange-500/30'
  },
  {
    id: 'poisoning',
    icon: AlertTriangle,
    title: {
      tr: 'Zehirlenme Acil',
      en: 'Poisoning Emergency',
      ar: 'طوارئ التسمم',
      es: 'Emergencia por Envenenamiento',
      de: 'Notfall bei Vergiftung'
    },
    desc: {
      tr: 'Kusturmama kuralı ve UZEM (114) danışma adımları.',
      en: 'Do NOT induce vomiting rule and poison control (114).',
      ar: 'قاعدة عدم التقيؤ وإرشادات التسمم.',
      es: 'Regla de NO inducir el vómito e instrucciones.',
      de: 'Verbot von Erbrechen und Giftnotruf.'
    },
    query: {
      tr: 'Zehirlenme durumunda ne yapılmalı, kusturulmalı mı?',
      en: 'First aid for poisoning, should victim vomit?',
      ar: 'ماذا أفعل عند التسمم وهل يجب التقيؤ؟',
      es: '¿Qué hacer en caso de envenenamiento?',
      de: 'Erste Hilfe bei Vergiftungen?'
    },
    badgeColor: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30'
  },
  {
    id: 'burns',
    icon: Flame,
    title: {
      tr: 'Yanık Müdahalesi',
      en: 'Burn Injuries',
      ar: 'إسعاف الحروق',
      es: 'Tratamiento de Quemaduras',
      de: 'Verbrennungen Behandlung'
    },
    desc: {
      tr: 'Soğuk su soğutması, su toplayan kabarcıklar.',
      en: '20-min cool water cooling and protecting skin.',
      ar: 'التبريد بالماء البارد 20 دقيقة وحماية الجلد.',
      es: 'Enfriamiento con agua 20 min y cuidado de la piel.',
      de: '20 Min. fließendes Wasser und Wundschutz.'
    },
    query: {
      tr: 'Yanık üzerine ne sürülmeli, soğuk su nasıl uygulanır?',
      en: 'First aid for burns, how long to cool under water?',
      ar: 'كيف أسعف الحروق وما مدة غسلها بالماء؟',
      es: '¿Primeros auxilios para quemaduras?',
      de: 'Erste Hilfe bei Brandwunden?'
    },
    badgeColor: 'bg-orange-600/10 text-orange-600 border-orange-600/30'
  },
  {
    id: 'drowning',
    icon: Waves,
    title: {
      tr: 'Suda Boğulma',
      en: 'Drowning Recovery',
      ar: 'الغرق في الماء',
      es: 'Ahogamiento en Agua',
      de: 'Ertrinken Notfall'
    },
    desc: {
      tr: 'Sudan çıkarma, soluk borusu temizleme ve CPR.',
      en: 'Safe rescue, clearing airway, and artificial breath.',
      ar: 'الإنقاذ من الماء وتنظيف مجرى التنفس والإنعاش.',
      es: 'Rescate seguro, vía aérea y RCP inmediato.',
      de: 'Wasserrettung, Beatmung und Herzdruckmassage.'
    },
    query: {
      tr: 'Suda boğulan kişiye ilk yardım nasıl yapılır?',
      en: 'First aid steps for a drowning victim?',
      ar: 'كيف نسعف شخصاً يتعرض للغرق؟',
      es: '¿Primeros auxilios para ahogamiento?',
      de: 'Erste Hilfe bei Ertrinken?'
    },
    badgeColor: 'bg-blue-500/10 text-blue-500 border-blue-500/30'
  },
  {
    id: 'bites',
    icon: Bug,
    title: {
      tr: 'Akrep / Yılan Sokması',
      en: 'Snake & Sting Bites',
      ar: 'لدغات العقارب والأفاعي',
      es: 'Picaduras y Mordeduras',
      de: 'Schlangen- & Insektenbisse'
    },
    desc: {
      tr: 'Yarayı emmeme kuralı, soğuk uygulama ve sabitleme.',
      en: 'Do NOT suck venom, immobilize limb, apply cold.',
      ar: 'عدم مص السم، تثبيت العضو، والكمادات الباردة.',
      es: 'NO succionar veneno, inmovilizar y aplicar frío.',
      de: 'GIFT NICHT aussaugen, ruhigstellen und kühlen.'
    },
    query: {
      tr: 'Yılan veya akrep sokmasında ilk yardım nasıl olmalı?',
      en: 'First aid for snake or scorpion stings?',
      ar: 'ما الإسعاف الأولي لدغة الأفعى أو العقرب؟',
      es: '¿Primeros auxilios por picadura de serpiente?',
      de: 'Erste Hilfe bei Schlangenbissen?'
    },
    badgeColor: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30'
  },
  {
    id: 'chemical',
    icon: Wind,
    title: {
      tr: 'Kimyasal & Gaz Sızıntısı',
      en: 'Chemical Gas Spill',
      ar: 'تسرب المواد الكيميائية والغاز',
      es: 'Fuga Química de Gas',
      de: 'Chemikalien- & Gasleck'
    },
    desc: {
      tr: 'Rüzgarı arkaya alma, yüksek yerlere çıkma, maske.',
      en: 'Upwind evacuation, higher ground, protective mask.',
      ar: 'الإخلاء عكس الريح والتنفس من خلال قماش رطب.',
      es: 'Evacuación a favor del viento y mascarilla.',
      de: 'Windaufwärts evakuieren und Mundschutz.'
    },
    query: {
      tr: 'Kimyasal gaz sızıntısında ne yapılmalı?',
      en: 'What to do during a chemical gas leak?',
      ar: 'ماذا نفعل عند تسرب غاز كيميائي؟',
      es: '¿Qué hacer en fuga de gas químico?',
      de: 'Was tun bei Chemikalien- oder Gasleck?'
    },
    badgeColor: 'bg-purple-500/10 text-purple-500 border-purple-500/30'
  }
];

export const EmergencyDashboard: React.FC<EmergencyDashboardProps> = ({ onSelectQuery, onOpenChat, lang }) => {
  const [searchTerm, setSearchTerm] = React.useState('');
  const t = DASHBOARD_TEXTS[lang] || DASHBOARD_TEXTS.tr;

  const filteredCards = EMERGENCY_CARDS.filter(card => {
    const title = card.title[lang] || card.title.tr;
    const desc = card.desc[lang] || card.desc.tr;
    return title.toLowerCase().includes(searchTerm.toLowerCase()) || 
           desc.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-6 space-y-8 animate-fadeIn">
      
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-red-600 via-rose-600 to-red-700 text-white p-6 sm:p-10 shadow-2xl">
        <div className="absolute -right-10 -bottom-10 opacity-15 pointer-events-none">
          <ShieldAlert className="w-80 h-80" />
        </div>

        <div className="relative z-10 space-y-4 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/20 backdrop-blur-md text-xs font-semibold uppercase tracking-wider">
            <Activity className="w-4 h-4 text-red-200 animate-pulse" />
            7/24 Acil Müdahale Platformu
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight leading-tight">
            {t.heroTitle}
          </h1>

          <p className="text-sm sm:text-base text-red-100 font-medium leading-relaxed">
            {t.heroSub}
          </p>

          {/* Quick Search & AI Launcher */}
          <div className="pt-2 flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={t.searchPlaceholder}
                className="w-full pl-12 pr-4 py-3.5 rounded-2xl bg-white text-gray-900 placeholder-gray-400 font-medium text-sm focus:outline-none focus:ring-4 focus:ring-red-400/50 shadow-lg"
              />
            </div>

            <button
              onClick={onOpenChat}
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl bg-gray-900 hover:bg-black text-white font-bold text-sm shadow-xl hover:scale-[1.02] transition-all duration-200"
            >
              <MessageSquareText className="w-5 h-5 text-red-400" />
              {t.askAiBtn}
            </button>
          </div>
        </div>
      </div>

      {/* Speed Dial Numbers Banner */}
      <div className="space-y-3">
        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 flex items-center gap-2">
          <Phone className="w-4 h-4 text-red-500" />
          {t.speedDialTitle}
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <a
            href="tel:112"
            className="flex items-center gap-3 p-4 rounded-2xl bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 transition-all duration-200 group"
          >
            <div className="p-3 rounded-xl bg-red-600 text-white shadow-md group-hover:scale-110 transition-transform">
              <Phone className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-black text-red-600 dark:text-red-400">112</div>
              <div className="text-xs font-semibold text-gray-600 dark:text-gray-300">Acil Çağrı</div>
            </div>
          </a>

          <a
            href="tel:110"
            className="flex items-center gap-3 p-4 rounded-2xl bg-orange-500/10 border border-orange-500/30 hover:bg-orange-500/20 transition-all duration-200 group"
          >
            <div className="p-3 rounded-xl bg-orange-600 text-white shadow-md group-hover:scale-110 transition-transform">
              <Flame className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-black text-orange-600 dark:text-orange-400">110</div>
              <div className="text-xs font-semibold text-gray-600 dark:text-gray-300">İtfaiye</div>
            </div>
          </a>

          <a
            href="tel:155"
            className="flex items-center gap-3 p-4 rounded-2xl bg-blue-500/10 border border-blue-500/30 hover:bg-blue-500/20 transition-all duration-200 group"
          >
            <div className="p-3 rounded-xl bg-blue-600 text-white shadow-md group-hover:scale-110 transition-transform">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-black text-blue-600 dark:text-blue-400">155</div>
              <div className="text-xs font-semibold text-gray-600 dark:text-gray-300">Polis İmdat</div>
            </div>
          </a>

          <a
            href="tel:114"
            className="flex items-center gap-3 p-4 rounded-2xl bg-purple-500/10 border border-purple-500/30 hover:bg-purple-500/20 transition-all duration-200 group"
          >
            <div className="p-3 rounded-xl bg-purple-600 text-white shadow-md group-hover:scale-110 transition-transform">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xl font-black text-purple-600 dark:text-purple-400">114</div>
              <div className="text-xs font-semibold text-gray-600 dark:text-gray-300">UZEM Zehir</div>
            </div>
          </a>
        </div>
      </div>

      {/* Emergency Category Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-extrabold uppercase tracking-wider text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <Activity className="w-4 h-4 text-red-500" />
            {t.categoriesTitle}
          </h2>
          <span className="text-xs text-gray-400 font-medium">
            {filteredCards.length} Kart
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCards.map((card) => {
            const Icon = card.icon;
            const title = card.title[lang] || card.title.tr;
            const desc = card.desc[lang] || card.desc.tr;
            const query = card.query[lang] || card.query.tr;

            return (
              <button
                key={card.id}
                onClick={() => onSelectQuery(query)}
                className="flex flex-col justify-between text-left p-5 rounded-2xl bg-white dark:bg-[#1A1A1A] border border-gray-200/80 dark:border-gray-800 shadow-sm hover:shadow-xl hover:border-red-500/50 hover:-translate-y-1 transition-all duration-300 group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className={`p-3 rounded-xl border ${card.badgeColor} group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                      Hızlı Müdahale
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-gray-900 dark:text-white group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors">
                      {title}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 leading-relaxed line-clamp-2">
                      {desc}
                    </p>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800/80 flex items-center justify-between text-xs font-semibold text-red-600 dark:text-red-400">
                  <span>Protokolü Göster</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

    </div>
  );
};
