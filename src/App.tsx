import { useState, useRef, useEffect } from 'react';
import { 
  Mic, Send, Volume2, Activity, AlertTriangle, ShieldAlert, 
  Droplet, UserRound, Wifi, Battery, Signal, Moon, Sun, 
  HeartPulse, Globe, Flame, Waves, Stethoscope, ArrowRight, HelpCircle, Home, MessageSquare, Heart, Zap, VolumeX, FileText, RotateCcw, ChevronDown, PhoneCall, CheckCircle2,
  FileUp, X, Loader2, Plus, Upload, BookOpen, Database, Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import Markdown from 'react-markdown';
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Types
type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: { source: string; content: string }[];
  isError?: boolean;
};

type Language = 'tr' | 'en';

const LANGUAGES: { code: Language; name: string; flag: string; speechCode: string }[] = [
  { code: 'tr', name: 'TR Türkçe', flag: '🇹🇷', speechCode: 'tr-TR' },
  { code: 'en', name: 'EN English', flag: '🇬🇧', speechCode: 'en-US' },
];

const TRANSLATIONS: Record<Language, {
  welcome: string;
  online: string;
  placeholder: string;
  listening: string;
  connectionError: string;
  call112: string;
  homeTab: string;
  chatTab: string;
  guidesTab: string;
  guidesTitle: string;
  guidesSubtitle: string;
  uploadCardTitle: string;
  uploadCardDesc: string;
  selectFile: string;
  maxSize: string;
  uploadBtn: string;
  uploadingBtn: string;
  indexedDocsTitle: string;
  activeStatus: string;
  listenText: string;
  loadingText: string;
  quickCategoryTitle: string;
  clearChat: string;
  sources: string;
  emergencyCategories: { title: string; desc: string; icon: any; query: string; color: string }[];
}> = {
  tr: {
    welcome: 'Merhaba! Ben **AfetRehberi** acil durum ve ilk yardım asistanıyım. 100% çevrimdışı (offline) çalışıyorum.\n\nYaşanan acil durumu aşağıya yazabilir veya hızlı konulardan birini seçebilirsiniz.',
    online: '100% Çevrimdışı',
    placeholder: 'Acil durum veya ilk yardım sorusu yazın...',
    listening: 'Dinleniyor...',
    connectionError: 'Bağlantı hatası: Sunucuya ulaşılamıyor.',
    call112: '112 ACİL ARA',
    homeTab: 'Anasayfa',
    chatTab: 'Acil Asistan',
    guidesTab: 'Kılavuzlar',
    guidesTitle: 'Afet Kılavuzları & Bilgi Tabanı',
    guidesSubtitle: 'Yerel RAG sisteminde indekslenmiş resmi protokoller ve dinamik kılavuz yükleme.',
    uploadCardTitle: 'Yeni Kılavuz / Protokol Yükle',
    uploadCardDesc: 'Sisteme yeni bir acil durum dokümanı (.txt, .md) ekleyin. Vektör tablosu sunucu durdurulmadan otomatik güncellenir.',
    selectFile: 'Doküman seçin (.txt, .md)',
    maxSize: 'Maks. 5 MB • Çevrimdışı İndeks',
    uploadBtn: 'Yükle ve İndeksle',
    uploadingBtn: 'İşleniyor...',
    indexedDocsTitle: 'İndekslenmiş Resmi Protokoller',
    activeStatus: 'Aktif',
    listenText: 'Sesli Oku',
    loadingText: 'Acil protokol hazırlanıyor...',
    quickCategoryTitle: 'Hızlı Acil Müdahale Konuları:',
    clearChat: 'Sohbeti temizle',
    sources: 'Kaynaklar',
    emergencyCategories: [
      { title: 'Burun Kanaması', desc: 'Baskı tamponu & pozisyon', icon: Droplet, query: 'Burnum kanıyor, ne yapmalıyım?', color: 'from-rose-500 to-red-600' },
      { title: 'Kalp Krizi Şüphesi', desc: 'Aspirin & semi-oturuş', icon: HeartPulse, query: 'Kalp krizi belirtilerinde ilk yardım nasıl yapılır?', color: 'from-red-600 to-rose-700' },
      { title: 'Deprem & Enkaz', desc: 'Çök-kapan-tutun & enkaz', icon: ShieldAlert, query: 'Deprem anında ve enkaz altında ne yapılmalı?', color: 'from-amber-500 to-orange-600' },
      { title: 'Enkazda Ses Duyurma', desc: 'Ritmik boru vurma & düdük', icon: VolumeX, query: 'Enkaz altındayken ses nasıl duyurulmalıdır?', color: 'from-amber-600 to-yellow-600' },
      { title: 'Zehirlenme Acil', desc: 'Çamaşır suyu & UZEM 114', icon: AlertTriangle, query: 'Zehirlenme durumunda ne yapılmalı, kusturulmalı mı?', color: 'from-purple-600 to-indigo-700' },
      { title: 'Yanık Müdahalesi', desc: 'Soğuk su & derece', icon: Flame, query: 'Yanık üzerine ne sürülmeli, soğuk su nasıl uygulanır?', color: 'from-orange-500 to-amber-600' },
      { title: 'Elektrik Çarpması', desc: 'Şalter kapatma & güvenlik', icon: Zap, query: 'Elektrik çarpmasında ilk yardım nasıl yapılır?', color: 'from-yellow-500 to-amber-600' },
      { title: 'Tıkanma (Heimlich)', desc: 'Tam boğulma müdahalesi', icon: Stethoscope, query: 'Boğazına cisim kaçan kişiye Heimlich nasıl yapılır?', color: 'from-emerald-500 to-teal-600' },
      { title: 'Ağır Kanama', desc: 'Yara baskısı & turnike', icon: Activity, query: 'Ağır kanamada yaraya nasıl baskı uygulanır?', color: 'from-rose-600 to-red-700' },
      { title: 'Suda Boğulma', desc: 'Su çekme & solunum', icon: Waves, query: 'Suda boğulan kişiye ilk yardım nasıl yapılır?', color: 'from-cyan-500 to-blue-600' },
    ]
  },
  en: {
    welcome: 'Hello! I am **DisasterGuide** emergency AI assistant. Operating 100% offline.\n\nBriefly describe the emergency below or select a quick topic.',
    online: '100% Offline',
    placeholder: 'Describe the emergency or first aid query...',
    listening: 'Listening...',
    connectionError: 'Connection error: Unable to reach server.',
    call112: 'CALL 112 EMERGENCY',
    homeTab: 'Home',
    chatTab: 'AI Assistant',
    guidesTab: 'Guides',
    guidesTitle: 'Disaster Guides & Knowledge Base',
    guidesSubtitle: 'Official protocols indexed in local RAG and runtime document ingestion.',
    uploadCardTitle: 'Upload New Guide / Protocol',
    uploadCardDesc: 'Add a new emergency document (.txt, .md). Vector store is updated instantly without restarting.',
    selectFile: 'Select document (.txt, .md)',
    maxSize: 'Max 5 MB • Offline Index',
    uploadBtn: 'Upload & Ingest',
    uploadingBtn: 'Ingesting...',
    indexedDocsTitle: 'Indexed Official Protocols',
    activeStatus: 'Active',
    listenText: 'Listen',
    loadingText: 'Preparing emergency protocol...',
    quickCategoryTitle: 'Quick Emergency Topics:',
    clearChat: 'Clear chat',
    sources: 'Sources',
    emergencyCategories: [
      { title: 'Nosebleed', desc: 'Pressure & head position', icon: Droplet, query: 'How to stop a nosebleed?', color: 'from-rose-500 to-red-600' },
      { title: 'Heart Attack', desc: 'Aspirin & semi-upright', icon: HeartPulse, query: 'First aid steps for heart attack symptoms?', color: 'from-red-600 to-rose-700' },
      { title: 'Earthquake', desc: 'Drop-cover-hold & rubble', icon: ShieldAlert, query: 'What to do during an earthquake and if trapped under rubble?', color: 'from-amber-500 to-orange-600' },
      { title: 'Signal Under Rubble', desc: 'Rhythmic pipe tapping', icon: VolumeX, query: 'How to signal for help while trapped under rubble?', color: 'from-amber-600 to-yellow-600' },
      { title: 'Poisoning', desc: 'Chemical & poison control', icon: AlertTriangle, query: 'First aid for poisoning, should victim vomit?', color: 'from-purple-600 to-indigo-700' },
      { title: 'Burns First Aid', desc: 'Cold water cooling', icon: Flame, query: 'First aid for burns, how long to cool under water?', color: 'from-orange-500 to-amber-600' },
      { title: 'Electric Shock', desc: 'Breaker shutoff & safety', icon: Zap, query: 'First aid steps for electric shock?', color: 'from-yellow-500 to-amber-600' },
      { title: 'Choking (Heimlich)', desc: 'Airway obstruction', icon: Stethoscope, query: 'How to perform Heimlich maneuver on choking victim?', color: 'from-emerald-500 to-teal-600' },
      { title: 'Severe Bleeding', desc: 'Wound pressure & tourniquet', icon: Activity, query: 'How to apply pressure to a severe bleeding wound?', color: 'from-rose-600 to-red-700' },
      { title: 'Drowning', desc: 'Rescue breaths & CPR', icon: Waves, query: 'First aid steps for a drowning victim?', color: 'from-cyan-500 to-blue-600' },
    ]
  }
};

const FRIENDLY_SOURCES: Record<string, string> = {
  'kizilay_ozel_ilkyardim.txt': 'Türk Kızılayı Özel İlk Yardım Rehberi',
  'kizilay_ilkyardim.txt': 'Türk Kızılayı Temel İlk Yardım Rehberi',
  'kizilay_kalp_cpr.txt': 'Türk Kızılayı CPR (Temel Yaşam Desteği) Rehberi',
  'kizilay_kanamalar_sok.txt': 'Türk Kızılayı Kanama ve Şok Rehberi',
  'kizilay_kemik_eklem.txt': 'Türk Kızılayı Kırık ve Çıkık Rehberi',
  'kizilay_goz_kulak_burun.txt': 'Türk Kızılayı Duyu Organları İlk Yardım Rehberi',
  'afad_deprem.txt': 'AFAD Deprem ve Enkaz Rehberi',
  'afad_yangin_sel.txt': 'AFAD Yangın ve Sel Rehberi',
  'afad_cevresel_aciller.txt': 'AFAD Çevresel Aciller Rehberi',
  'afad_kimyasal.txt': 'AFAD KBRN & Kimyasal Aciller Rehberi',
};

function formatSourceTitle(source: string): string {
  if (FRIENDLY_SOURCES[source]) return FRIENDLY_SOURCES[source];
  if (source.endsWith('.txt')) {
    return source.replace('.txt', '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }
  return source;
}

function stripSourcesFromAnswer(text: string): string {
  return text
    .replace(/\n*📎?\s*Kaynaklar?\s*[:：][\s\S]*$/i, '')
    .replace(/\n*Sources?\s*[:：][\s\S]*$/i, '')
    .replace(/\n*Fuente[s]?\s*[:：][\s\S]*$/i, '')
    .replace(/\n*Quellen?\s*[:：][\s\S]*$/i, '')
    .replace(/\n*المصادر?\s*[:：][\s\S]*$/i, '')
    .replace(/\n*Kaynak\s*[:：][\s\S]*$/i, '')
    .trim();
}
function FormattedEmergencyMessage({ content }: { content: string }) {
  if (!content) return null;

  const lines = content.split('\n');
  type Section = {
    type: 'header' | 'section-title' | 'step' | 'symptom' | 'warning' | 'alert' | 'text';
    stepNum?: string;
    title?: string;
    text: string;
  };
  const sections: Section[] = [];
  let currentBlockType: 'default' | 'warning' | 'symptom' | 'step' = 'default';

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();
    if (!trimmed) continue;

    // 1. Header / Emergency Badge (🚨 ACİL DURUM)
    if (trimmed.startsWith('🚨 ACİL DURUM') || trimmed.startsWith('🚨 EMERGENCY') || trimmed.startsWith('🚨 DİKKAT') || trimmed.startsWith('🚨 CRITICAL')) {
      sections.push({
        type: 'header',
        text: trimmed.replace(/^[🚨#\s:]+/, '').trim()
      });
      currentBlockType = 'default';
      continue;
    }

    // 2. Section Subtitles: Belirtiler (🩺)
    if (trimmed.includes('BELİRTİLER') || trimmed.includes('SYMPTOMS') || trimmed.startsWith('🩺') || trimmed.includes('🩺')) {
      sections.push({
        type: 'section-title',
        title: '🩺 ' + trimmed.replace(/^[🩺#\s:*]+/, '').replace(/[*_]/g, '').trim(),
        text: ''
      });
      currentBlockType = 'symptom';
      continue;
    }

    // 3. Section Subtitles: Adım Adım Müdahale (📋)
    if (trimmed.includes('ADIM ADIM') || trimmed.includes('MÜDAHALESİ') || trimmed.includes('STEP-BY-STEP') || trimmed.includes('PROTOKOL') || trimmed.startsWith('📋') || trimmed.includes('📋')) {
      sections.push({
        type: 'section-title',
        title: '📋 ' + trimmed.replace(/^[📋#\s:*]+/, '').replace(/[*_]/g, '').trim(),
        text: ''
      });
      currentBlockType = 'step';
      continue;
    }

    // 4. Section Subtitles: Yapılmaması Gerekenler (⚠️)
    if (trimmed.includes('YAPILMAMASI GEREKENLER') || trimmed.includes('KESİNLİKLE YAPILMAMASI') || trimmed.includes('DO NOT') || trimmed.startsWith('⚠️') || trimmed.includes('⚠️')) {
      sections.push({
        type: 'section-title',
        title: '⚠️ ' + trimmed.replace(/^[⚠️#\s:*]+/, '').replace(/[*_]/g, '').trim(),
        text: ''
      });
      currentBlockType = 'warning';
      continue;
    }

    // 5. Section Subtitles: 112 Çağrı Kriteri (🚨)
    if (trimmed.startsWith('🚨 112') || trimmed.startsWith('## 🚨 112') || trimmed.includes('112 ACİL ÇAĞRI MERKEZİ NE ZAMAN') || trimmed.includes('WHEN TO CALL 112')) {
      sections.push({
        type: 'section-title',
        title: '🚨 ' + trimmed.replace(/^[🚨#\s:*]+/, '').replace(/[*_]/g, '').trim(),
        text: ''
      });
      currentBlockType = 'default';
      continue;
    }

    // 6. Direct 112 Emergency Banner
    if (trimmed.startsWith('🚨') || trimmed.startsWith('☎️') || (trimmed.startsWith('DERHAL 112') || trimmed.startsWith('Vakit kaybetmeden 112'))) {
      sections.push({
        type: 'alert',
        text: trimmed.replace(/^[🚨☎️\s]+/, '').trim()
      });
      continue;
    }

    // 7. Numbered steps: 1) or 1. or 1 -
    const stepMatch = trimmed.match(/^(\d+)[\.\)\-]\s*(.*)$/);
    if (stepMatch) {
      sections.push({
        type: 'step',
        stepNum: stepMatch[1],
        text: stepMatch[2].trim()
      });
      continue;
    }

    // 8. Warning bullet
    if (currentBlockType === 'warning' && (trimmed.startsWith('-') || trimmed.startsWith('•') || trimmed.startsWith('*'))) {
      sections.push({
        type: 'warning',
        text: trimmed.replace(/^[-•*]\s*/, '').trim()
      });
      continue;
    }

    // 9. Symptom bullet
    if (currentBlockType === 'symptom' && (trimmed.startsWith('-') || trimmed.startsWith('•') || trimmed.startsWith('*'))) {
      sections.push({
        type: 'symptom',
        text: trimmed.replace(/^[-•*]\s*/, '').trim()
      });
      continue;
    }

    // 10. Generic bullet
    if (trimmed.startsWith('-') || trimmed.startsWith('•') || trimmed.startsWith('*')) {
      sections.push({
        type: 'step',
        stepNum: '•',
        text: trimmed.replace(/^[-•*]\s*/, '').trim()
      });
      continue;
    }

    // 11. Plain text paragraph
    sections.push({
      type: currentBlockType === 'warning' ? 'warning' : (currentBlockType === 'symptom' ? 'symptom' : 'text'),
      text: trimmed
    });
  }

  return (
    <div className="space-y-2.5">
      {sections.map((sec, idx) => {
        if (sec.type === 'header') {
          return (
            <div key={idx} className="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-400 font-bold text-xs shadow-2xs">
              <ShieldAlert className="w-4 h-4 shrink-0 text-red-600 animate-pulse" />
              <span className="tracking-wide">{sec.text}</span>
            </div>
          );
        }

        if (sec.type === 'section-title') {
          const isWarning = sec.title?.includes('⚠️') || sec.title?.includes('YAPILMAMASI');
          const is112 = sec.title?.includes('🚨') || sec.title?.includes('112');
          const isSymptom = sec.title?.includes('🩺') || sec.title?.includes('BELİRTİ');

          return (
            <div 
              key={idx} 
              className={`text-[12px] font-bold uppercase tracking-wider mt-3 mb-1 flex items-center gap-1.5 ${
                isWarning ? 'text-amber-600 dark:text-amber-400' :
                is112 ? 'text-rose-600 dark:text-rose-400' :
                isSymptom ? 'text-blue-600 dark:text-blue-400' :
                'text-gray-700 dark:text-gray-300'
              }`}
            >
              {sec.title}
            </div>
          );
        }

        if (sec.type === 'alert') {
          return (
            <div key={idx} className="flex items-start gap-2.5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-700 dark:text-rose-300 text-xs font-semibold shadow-2xs">
              <PhoneCall className="w-4 h-4 shrink-0 text-rose-600 mt-0.5 animate-bounce" />
              <div className="leading-relaxed"><Markdown>{sec.text}</Markdown></div>
            </div>
          );
        }

        if (sec.type === 'step') {
          return (
            <div key={idx} className="flex items-start gap-2.5 p-2.5 rounded-xl bg-gray-50/90 dark:bg-[#232326] border border-gray-200/70 dark:border-gray-800/80 hover:border-red-500/40 transition-colors shadow-2xs">
              <span className="w-5 h-5 rounded-full bg-red-600 text-white text-[11px] font-bold flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
                {sec.stepNum}
              </span>
              <div className="text-[12.5px] leading-relaxed text-gray-800 dark:text-gray-200 font-medium">
                <Markdown>{sec.text}</Markdown>
              </div>
            </div>
          );
        }

        if (sec.type === 'symptom') {
          return (
            <div key={idx} className="flex items-start gap-2.5 px-3 py-2 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-900 dark:text-blue-200 text-xs font-medium">
              <span className="text-blue-600 font-bold text-xs mt-0.5 shrink-0">●</span>
              <div className="leading-relaxed"><Markdown>{sec.text}</Markdown></div>
            </div>
          );
        }

        if (sec.type === 'warning') {
          return (
            <div key={idx} className="flex items-start gap-2.5 px-3 py-2 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-900 dark:text-amber-200 text-xs font-medium">
              <span className="text-red-500 font-bold text-xs mt-0.5 shrink-0">✕</span>
              <div className="leading-relaxed"><Markdown>{sec.text}</Markdown></div>
            </div>
          );
        }

        return (
          <div key={idx} className="p-2.5 rounded-xl bg-gray-50/70 dark:bg-[#202023] border border-gray-100 dark:border-gray-800/60 text-[12.5px] leading-relaxed text-gray-700 dark:text-gray-300">
            <Markdown>{sec.text}</Markdown>
          </div>
        );
      })}
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'home' | 'chat' | 'guides'>('home');
  const [selectedLang, setSelectedLang] = useState<Language>('tr');
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [timeStr, setTimeStr] = useState('');
  const [openSourcesId, setOpenSourcesId] = useState<string | null>(null);

  const currentTrans = TRANSLATIONS[selectedLang];
  const currentLangObj = LANGUAGES.find(l => l.code === selectedLang) || LANGUAGES[0];

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: TRANSLATIONS.tr.welcome
    }
  ]);

  // Clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const formatted = now.toLocaleTimeString('tr-TR', {
        timeZone: 'Europe/Istanbul',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
      setTimeStr(formatted);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleLangChange = (newLang: Language) => {
    setSelectedLang(newLang);
    setShowLangMenu(false);

    setMessages(prev => {
      if (prev.length === 1 && prev[0].id === 'welcome') {
        return [{
          id: 'welcome',
          role: 'assistant',
          content: TRANSLATIONS[newLang].welcome
        }];
      }
      return prev;
    });
  };
  
  // Speech Recognition
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = currentLangObj.speechCode;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');
        setInput(transcript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, [selectedLang]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (activeTab === 'chat') {
      scrollToBottom();
    }
  }, [messages, isLoading, activeTab]);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      setInput('');
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  const handleSpeak = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      
      const cleanText = text.replace(/[*#_~`]/g, '');
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = currentLangObj.speechCode;
      utterance.rate = 1.15;
      
      const voices = window.speechSynthesis.getVoices();
      const matchVoice = voices.find(v => v.lang.startsWith(selectedLang));
      if (matchVoice) {
        utterance.voice = matchVoice;
      }
      
      window.speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  };

  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || isUploading) return;
    setIsUploading(true);
    setUploadStatus(null);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Yükleme başarısız oldu.');
      }
      setUploadStatus({
        type: 'success',
        message: data.message || `${data.filename} başarıyla indekslendi! (${data.total_chunks} blok)`
      });
      setUploadFile(null);
    } catch (err: any) {
      setUploadStatus({
        type: 'error',
        message: err.message || 'Yükleme sırasında bir hata oluştu.'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const clearChat = () => {
    stopSpeaking();
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: currentTrans.welcome
    }]);
    setOpenSourcesId(null);
    setInput('');
  };

  const sendMessage = async (query: string, isButton: boolean = false) => {
    if (isLoading || !query.trim()) return;

    stopSpeaking();
    setActiveTab('chat');
    
    const userMsgId = Date.now().toString();
    const assistantMsgId = (Date.now() + 1).toString();

    const userMsg: Message = {
      id: userMsgId,
      role: 'user',
      content: query
    };

    const assistantMsg: Message = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      sources: []
    };
    
    setMessages(prev => [...prev, userMsg, assistantMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query, 
          lang: selectedLang, 
          is_button: isButton,
          history: messages.slice(-4).map(m => ({ role: m.role, content: m.content }))
        })
      });

      if (!response.ok || !response.body) {
        throw new Error('Streaming failed, fallback');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let accumulatedText = '';
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data:')) continue;
          const jsonStr = trimmed.replace(/^data:\s*/, '');
          if (!jsonStr) continue;

          try {
            const eventData = JSON.parse(jsonStr);
            if (eventData.type === 'meta') {
              if (eventData.detectedLang && eventData.detectedLang !== selectedLang) {
                setSelectedLang(eventData.detectedLang as Language);
              }
              setMessages(prev => prev.map(m => m.id === assistantMsgId ? { ...m, sources: eventData.sources || [] } : m));
            } else if (eventData.type === 'delta') {
              accumulatedText += eventData.delta;
              const cleanAccum = stripSourcesFromAnswer(accumulatedText);
              setMessages(prev => prev.map(m => m.id === assistantMsgId ? { ...m, content: cleanAccum } : m));
            } else if (eventData.type === 'done') {
              // Akış tamamlandı
            }
          } catch (err) {
            console.error('SSE JSON parse error:', err, jsonStr);
          }
        }
      }
    } catch (error) {
      console.warn('SSE stream error, trying fallback REST API:', error);
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            query, 
            lang: selectedLang, 
            is_button: isButton,
            history: messages.slice(-4).map(m => ({ role: m.role, content: m.content }))
          })
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        const isLangSwitched = Boolean(data.detectedLang && data.detectedLang !== selectedLang);
        if (isLangSwitched) {
          setSelectedLang(data.detectedLang as Language);
        }

        setMessages(prev => prev.map(m => m.id === assistantMsgId ? {
          ...m,
          content: stripSourcesFromAnswer(data.answer || ''),
          sources: data.sources || []
        } : m));
      } catch (fallbackError) {
        console.error('Final error sending message:', fallbackError);
        setMessages(prev => prev.map(m => m.id === assistantMsgId ? {
          ...m,
          content: currentTrans.connectionError,
          isError: true
        } : m));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn(
      "h-screen w-screen flex items-center justify-center font-sans transition-colors duration-500 relative overflow-hidden p-0 sm:p-2 select-none",
      theme === 'dark' ? 'bg-white' : 'bg-black'
    )}>
      
      {/* iPhone Mockup Frame — dark: black case, light: gray case; slightly narrower */}
      <div className={cn(
        "w-full max-w-[360px] h-full max-h-[90vh] aspect-[9/18.5] sm:rounded-[48px] shadow-2xl border-0 sm:border-[8px] flex flex-col relative overflow-hidden transition-colors duration-300",
        theme === 'dark'
          ? 'bg-[#121212] border-black'
          : 'bg-[#FAFAFA] border-gray-400'
      )}>
        
        {/* Dynamic Island / Notch */}
        <div className="hidden sm:flex absolute top-0 left-1/2 -translate-x-1/2 w-28 h-5 bg-black rounded-b-2xl z-50 items-center justify-center">
          <div className="w-2.5 h-2.5 rounded-full bg-gray-900 border border-gray-800 mr-2" />
          <div className="w-2 h-2 rounded-full bg-blue-900/60" />
        </div>

        {/* Phone Status Bar */}
        <div className="w-full px-6 pt-3 pb-1 flex items-center justify-between text-[11px] font-bold text-gray-800 dark:text-gray-200 z-40 select-none">
          <span>{timeStr || '00:30'}</span>
          <div className="flex items-center gap-1.5 opacity-80">
            <Signal className="w-3.5 h-3.5" />
            <Wifi className="w-3.5 h-3.5" />
            <Battery className="w-4 h-4" />
          </div>
        </div>

        {/* App Top Header Bar: logo left · language center · theme right */}
        <header className="px-4 py-2 bg-transparent grid grid-cols-3 items-center z-30">
          
          <div className="justify-self-start w-8 h-8 rounded-2xl bg-emerald-500 text-white flex items-center justify-center shadow-md">
            <Heart className="w-4 h-4 fill-current animate-pulse" />
          </div>

          <div className="justify-self-center relative">
            <button
              onClick={() => setShowLangMenu(!showLangMenu)}
              className="h-8 px-2.5 rounded-full bg-gray-200/80 dark:bg-gray-800 text-gray-700 dark:text-gray-300 flex items-center gap-1.5 shadow-sm hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors"
            >
              <Globe className="w-3.5 h-3.5" />
              <span className="text-[11px] font-semibold tracking-wide">{currentLangObj.code.toUpperCase()}</span>
              <ChevronDown className={cn("w-3 h-3 opacity-60 transition-transform", showLangMenu && "rotate-180")} />
            </button>

            <AnimatePresence>
              {showLangMenu && (
                <motion.div
                  initial={{ opacity: 0, y: 5, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 5, scale: 0.95 }}
                  className="absolute left-1/2 -translate-x-1/2 mt-2 w-44 rounded-2xl bg-white dark:bg-[#1A1A1A] border border-gray-200/80 dark:border-gray-800 shadow-2xl p-2 z-50"
                >
                  {LANGUAGES.map((l) => (
                    <button
                      key={l.code}
                      onClick={() => handleLangChange(l.code)}
                      className={cn(
                        "w-full flex items-center gap-2 px-2.5 py-1.5 rounded-xl text-xs transition-colors text-left",
                        selectedLang === l.code
                          ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold"
                          : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 font-medium"
                      )}
                    >
                      <span>{l.flag}</span>
                      <span>{l.name}</span>
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            className="justify-self-end w-8 h-8 rounded-full bg-gray-200/80 dark:bg-gray-800 text-gray-700 dark:text-gray-300 flex items-center justify-center shadow-sm hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5 text-amber-400" />}
          </button>

        </header>

        {/* TAB 1: ANASAYFA (HOME VIEW) */}
        {activeTab === 'home' && (
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4 scrollbar-none">
            
            {/* Title & Status */}
            <div className="text-center pt-1">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center justify-center gap-1.5 tracking-tight">
                AfetRehberi <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20">AI</span>
              </h2>
              <p className="text-[11px] font-medium text-emerald-600 dark:text-emerald-400 flex items-center justify-center gap-1.5 mt-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                {currentTrans.online}
              </p>
            </div>

            {/* Emergency Category Cards Grid */}
            <div className="space-y-2 pb-2">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
                {currentTrans.quickCategoryTitle}
              </p>

              <div className="grid grid-cols-2 gap-2.5">
                {currentTrans.emergencyCategories.map((cat, idx) => {
                  const Icon = cat.icon;
                  return (
                    <button
                      key={idx}
                      disabled={isLoading}
                      onClick={() => sendMessage(cat.query, true)}
                      className={cn(
                        "flex flex-col items-center justify-center text-center p-4 rounded-2xl bg-white dark:bg-[#1E1E1E] border border-gray-200/90 dark:border-gray-800 shadow-sm hover:shadow-md hover:border-red-500/50 transition-all group",
                        isLoading && "opacity-50 pointer-events-none cursor-not-allowed"
                      )}
                    >
                      <div className={cn("w-9 h-9 rounded-xl text-white flex items-center justify-center mb-2 shadow-md bg-gradient-to-tr", cat.color)}>
                        <Icon className="w-4.5 h-4.5" />
                      </div>
                      <span className="text-xs font-semibold text-gray-800 dark:text-gray-100 group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors leading-tight">{cat.title}</span>
                    </button>
                  );
                })}
              </div>
            </div>

          </div>
        )}

        {/* TAB 2: ACİL ASİSTAN (CHAT VIEW) */}
        {activeTab === 'chat' && (
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 scrollbar-none">
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  "flex gap-2.5",
                  m.role === 'user' ? "justify-end" : "justify-start"
                )}
              >
                {m.role === 'assistant' && (
                  <div className="w-6 h-6 rounded-lg bg-red-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                    <Activity className="w-3.5 h-3.5" />
                  </div>
                )}

                {/* Message Bubble */}
                <div
                  className={cn(
                    "max-w-[88%] rounded-2xl px-3.5 py-2.5 text-[13px] shadow-sm leading-relaxed transition-colors",
                    m.role === 'user'
                      ? "bg-slate-800 dark:bg-red-600/90 text-white rounded-br-sm font-medium"
                      : m.isError
                      ? "bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-400 rounded-bl-sm"
                      : "bg-white/90 dark:bg-[#1C1C1E] text-gray-800 dark:text-gray-100 border border-gray-200/70 dark:border-gray-800/80 rounded-bl-sm backdrop-blur-sm"
                  )}
                >
                  {m.role === 'user' ? (
                    <p className="whitespace-pre-wrap font-medium">{m.content}</p>
                  ) : m.content ? (
                    <FormattedEmergencyMessage content={m.content} />
                  ) : (
                    /* Loading State Inside Assistant Bubble while text streams */
                    <div className="flex items-center gap-2 py-1 text-xs text-gray-500 dark:text-gray-400 font-medium">
                      <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
                      <span>{currentTrans.loadingText}</span>
                    </div>
                  )}

                  {/* Actions: source + read aloud (ONLY render if content is present and not empty) */}
                  {m.role === 'assistant' && !m.isError && m.content && (
                    <div className="mt-2 pt-1.5 border-t border-gray-100 dark:border-gray-800/60 space-y-1.5">
                      <div className="flex items-center justify-end gap-2">
                        {m.sources && m.sources.length > 0 && (
                          <button
                            onClick={() => setOpenSourcesId(openSourcesId === m.id ? null : m.id)}
                            className={cn(
                              "flex items-center gap-1 text-[11px] font-medium transition-colors px-1.5 py-0.5 rounded-md",
                              openSourcesId === m.id
                                ? "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10"
                                : "text-gray-400 hover:text-emerald-600"
                            )}
                          >
                            <FileText className="w-3.5 h-3.5" />
                            <span>{currentTrans.sources}</span>
                          </button>
                        )}
                        <button
                          onClick={() => handleSpeak(m.content)}
                          className="flex items-center gap-1 text-[11px] font-medium text-gray-400 hover:text-red-500 transition-colors"
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                          <span>{currentTrans.listenText}</span>
                        </button>
                      </div>

                      <AnimatePresence>
                        {openSourcesId === m.id && m.sources && m.sources.length > 0 && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="overflow-hidden"
                          >
                            <ul className="space-y-1.5 rounded-xl bg-gray-50 dark:bg-black/30 border border-gray-100 dark:border-gray-800/80 p-2">
                              {m.sources.map((s, i) => (
                                <li key={`${s.source}-${i}`} className="text-[11px] leading-snug">
                                  <p className="font-semibold text-emerald-700 dark:text-emerald-400 truncate">{formatSourceTitle(s.source)}</p>
                                  {s.content && (
                                    <p className="text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-3">{s.content}</p>
                                  )}
                                </li>
                              ))}
                            </ul>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  )}
                </div>

                {m.role === 'user' && (
                  <div className="w-6 h-6 rounded-lg bg-slate-800 dark:bg-gray-700 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                    <UserRound className="w-3.5 h-3.5" />
                  </div>
                )}
              </motion.div>
            ))}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* HORIZONTAL IN-CHAT QUICK CATEGORY CHIPS */}
        {activeTab === 'chat' && (
          <div className="px-3 py-1.5 bg-transparent overflow-x-auto scrollbar-none flex items-center gap-1.5 z-30">
            {currentTrans.emergencyCategories.slice(0, 6).map((cat, idx) => {
              const Icon = cat.icon;
              return (
                <motion.button
                  key={idx}
                  whileHover={isLoading ? {} : { scale: 1.03 }}
                  whileTap={isLoading ? {} : { scale: 0.96 }}
                  disabled={isLoading}
                  onClick={() => sendMessage(cat.query, true)}
                  className={cn(
                    "flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-white/90 dark:bg-[#1C1C1E] border border-gray-200/70 dark:border-gray-800/80 shadow-xs hover:border-red-500/50 text-gray-700 dark:text-gray-200 text-[11px] font-medium shrink-0 transition-all",
                    isLoading && "opacity-50 pointer-events-none cursor-not-allowed"
                  )}
                >
                  <Icon className="w-3 h-3 text-red-500" />
                  <span>{cat.title}</span>
                </motion.button>
              );
            })}
          </div>
        )}

        {/* FLOATING PILL CHAT INPUT BAR — only on chat tab */}
        {activeTab === 'chat' && (
          <div className="px-3 py-2 bg-transparent border-t border-gray-200/40 dark:border-gray-800 space-y-1.5">
            <div className="flex justify-end px-0.5">
              <button
                type="button"
                onClick={clearChat}
                disabled={isLoading || messages.length <= 1}
                className="flex items-center gap-1 text-[11px] font-medium text-gray-400 hover:text-red-500 disabled:opacity-30 transition-colors"
              >
                <RotateCcw className="w-3 h-3" />
                <span>{currentTrans.clearChat}</span>
              </button>
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage(input, false);
              }}
              className="flex items-center gap-2 px-2 py-1.5 rounded-full bg-white dark:bg-[#1E1E1E] border border-gray-200/90 dark:border-gray-800 shadow-md"
            >
              <button
                type="button"
                disabled={isLoading}
                onClick={toggleListening}
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 shrink-0",
                  isLoading && "opacity-40 pointer-events-none cursor-not-allowed",
                  isListening
                    ? "bg-red-600 text-white animate-bounce"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
                )}
              >
                <Mic className="w-4 h-4" />
              </button>

              <input
                type="text"
                disabled={isLoading}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={isListening ? currentTrans.listening : currentTrans.placeholder}
                className="flex-1 bg-transparent px-1 text-xs sm:text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none disabled:opacity-60"
              />

              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-300 disabled:opacity-30 flex items-center justify-center transition-all duration-200 shrink-0 active:scale-95 hover:bg-red-600 hover:text-white"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        )}

        {/* TAB 3: KILAVUZLAR & DOKÜMAN YÖNETİMİ (GUIDES VIEW) */}
        {activeTab === 'guides' && (
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4 scrollbar-none">
            
            {/* Header Title */}
            <div className="text-center pt-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20 text-[10px] font-semibold mb-1.5">
                <BookOpen className="w-3 h-3" />
                <span>{selectedLang === 'tr' ? '100% Yerel RAG Bilgi Havuzu' : '100% Local RAG Knowledge Base'}</span>
              </div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white tracking-tight">
                {currentTrans.guidesTitle}
              </h2>
              <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5 leading-snug">
                {currentTrans.guidesSubtitle}
              </p>
            </div>

            {/* Document Upload Card */}
            <div className="p-3.5 rounded-2xl bg-white dark:bg-[#1E1E1E] border border-gray-200/90 dark:border-gray-800 shadow-sm space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center">
                  <FileUp className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-gray-900 dark:text-white">{currentTrans.uploadCardTitle}</h3>
                  <p className="text-[10px] text-gray-400">{currentTrans.maxSize}</p>
                </div>
              </div>

              <p className="text-[11px] text-gray-600 dark:text-gray-400 leading-tight">
                {currentTrans.uploadCardDesc}
              </p>

              <form onSubmit={handleUpload} className="space-y-2.5">
                <label className="border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-blue-500 rounded-2xl p-3 flex flex-col items-center justify-center gap-1 cursor-pointer transition-colors text-center bg-gray-50/50 dark:bg-gray-900/50">
                  <Upload className="w-5 h-5 text-blue-500" />
                  <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300 truncate max-w-[220px]">
                    {uploadFile ? uploadFile.name : currentTrans.selectFile}
                  </span>
                  <input
                    type="file"
                    accept=".txt,.md"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setUploadFile(e.target.files[0]);
                        setUploadStatus(null);
                      }
                    }}
                  />
                </label>

                {uploadStatus && (
                  <motion.div
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={cn(
                      "p-2.5 rounded-xl text-[11px] leading-tight flex items-start gap-2",
                      uploadStatus.type === 'success'
                        ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                        : "bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20"
                    )}
                  >
                    {uploadStatus.type === 'success' ? (
                      <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                    )}
                    <span>{uploadStatus.message}</span>
                  </motion.div>
                )}

                <button
                  type="submit"
                  disabled={!uploadFile || isUploading}
                  className={cn(
                    "w-full py-2 rounded-xl text-xs font-semibold text-white flex items-center justify-center gap-1.5 transition-all shadow-md",
                    !uploadFile || isUploading
                      ? "bg-gray-400 cursor-not-allowed opacity-60"
                      : "bg-blue-600 hover:bg-blue-700 active:scale-95"
                  )}
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>{currentTrans.uploadingBtn}</span>
                    </>
                  ) : (
                    <>
                      <FileUp className="w-3.5 h-3.5" />
                      <span>{currentTrans.uploadBtn}</span>
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Indexed Guides List */}
            <div className="space-y-2 pb-2">
              <div className="flex items-center justify-between">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
                  {currentTrans.indexedDocsTitle}
                </p>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  10+ Doküman
                </span>
              </div>

              <div className="space-y-1.5">
                {[
                  { name: 'Türk Kızılayı Temel İlk Yardım Rehberi', tag: 'Kızılay', category: 'İlk Yardım' },
                  { name: 'AFAD Deprem ve Enkaz Rehberi', tag: 'AFAD', category: 'Deprem' },
                  { name: 'AFAD Yangın ve Sel Rehberi', tag: 'AFAD', category: 'Afet' },
                  { name: 'Türk Kızılayı CPR (Temel Yaşam Desteği)', tag: 'Kızılay', category: 'CPR' },
                  { name: 'Türk Kızılayı Kanama ve Şok Rehberi', tag: 'Kızılay', category: 'İlk Yardım' },
                  { name: 'AFAD KBRN & Kimyasal Aciller Rehberi', tag: 'AFAD', category: 'Kimyasal' },
                  { name: 'Türk Kızılayı Kırık ve Çıkık Rehberi', tag: 'Kızılay', category: 'İlk Yardım' },
                  { name: 'AFAD Çevresel Aciller Rehberi', tag: 'AFAD', category: 'Çevre' },
                ].map((doc, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-xl bg-white dark:bg-[#1E1E1E] border border-gray-200/80 dark:border-gray-800/80 shadow-xs flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <div className="w-6 h-6 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
                        <FileText className="w-3.5 h-3.5" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-gray-800 dark:text-gray-200 truncate">{doc.name}</p>
                        <p className="text-[10px] text-gray-400">{doc.category}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      <span className="text-[9px] px-1.5 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 font-medium">
                        {doc.tag}
                      </span>
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* BOTTOM NAVIGATION TAB BAR (3 TABS) */}
        <div className="px-4 py-2 bg-white/95 dark:bg-[#151515] border-t border-gray-200/40 dark:border-gray-800 flex items-center justify-around z-40 backdrop-blur-md">
          
          <button
            onClick={() => setActiveTab('home')}
            className={cn(
              "flex flex-col items-center gap-0.5 text-[11px] font-medium transition-colors",
              activeTab === 'home'
                ? "text-emerald-600 dark:text-emerald-400 font-semibold"
                : "text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            )}
          >
            <Home className="w-4 h-4" />
            <span>{currentTrans.homeTab}</span>
          </button>

          <button
            onClick={() => setActiveTab('chat')}
            className={cn(
              "flex flex-col items-center gap-0.5 text-[11px] font-medium transition-colors relative",
              activeTab === 'chat'
                ? "text-red-600 dark:text-red-400 font-semibold"
                : "text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            )}
          >
            <MessageSquare className="w-4 h-4" />
            <span>{currentTrans.chatTab}</span>
            {messages.length > 1 && (
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 absolute -top-0.5 right-2" />
            )}
          </button>

          <button
            onClick={() => setActiveTab('guides')}
            className={cn(
              "flex flex-col items-center gap-0.5 text-[11px] font-medium transition-colors",
              activeTab === 'guides'
                ? "text-blue-600 dark:text-blue-400 font-semibold"
                : "text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            )}
          >
            <BookOpen className="w-4 h-4" />
            <span>{currentTrans.guidesTab}</span>
          </button>

        </div>

      </div>

    </div>
  );
}
