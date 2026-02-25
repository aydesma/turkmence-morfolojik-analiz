# -*- coding: utf-8 -*-
"""
TurkmenFST — Sözlük Modülü (lexicon.py)

Sözlük verilerini yükler, kelime arar, morfolojik özellikleri yönetir.

Sözlük formatı (turkmence_sozluk.txt):
    kelime<TAB>%<pos%>

Morfolojik özellikler (ünlü düşmesi, yumuşama izni) doğrudan
sözlük girişine entegre edilmiştir — bu modern ve modüler yaklaşımı sağlar.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional
from turkmen_fst.phonology import (
    VOWEL_DROP_CANDIDATES, VOWEL_DROP_EXCEPTIONS,
    SOFTENING_TABLE, PhonologyRules
)


# ==============================================================================
#  SÖZLÜK GİRİŞİ
# ==============================================================================

@dataclass
class LexiconEntry:
    """
    Bir sözlük girişi.
    
    Attributes:
        word: Kelime kökü (ör. "kitap")
        pos: Kelime türü (ör. "n", "v", "adj")
        features: Morfolojik özellikler sözlüğü
    """
    word: str
    pos: str  # "n", "v", "adj", "adv", "conj", "det", "interj", "num", "phr", "postp", "prep", "pro", "np", "suf", "unk", "n?" (muhtemel isim)
    features: dict = field(default_factory=dict)

    @property
    def allows_softening(self) -> bool:
        """Bu kelime ünsüz yumuşamasına izin veriyor mu?"""
        return self.features.get("softening", self._default_softening())

    @property
    def allows_vowel_drop(self) -> bool:
        """Bu kelime ünlü düşmesine aday mı?"""
        return self.features.get("vowel_drop", self._default_vowel_drop())

    @property
    def is_exception_drop(self) -> bool:
        """Bu kelime istisna ünlü düşmesi mi?"""
        return self.features.get("exception_drop", self.word.lower() in VOWEL_DROP_EXCEPTIONS)

    def _default_softening(self) -> bool:
        """Kelimenin son harfine göre varsayılan yumuşama davranışı."""
        if not self.word:
            return False
        return self.word[-1].lower() in SOFTENING_TABLE

    def _default_vowel_drop(self) -> bool:
        """Kelime genel düşme adayları listesinde mi?"""
        return self.word.lower() in VOWEL_DROP_CANDIDATES


# ==============================================================================
#  EŞ SESLİ KELİMELER
# ==============================================================================

# Her eş sesli kelime: {anahtar: (anlam_etiketi, yumuşama_izni)}
HOMONYMS = {
    "at":   {"1": ("A:T (Ad, isim)", True),       "2": ("AT (At, beygir)", False)},
    "but":  {"1": ("BU:T (Vücut bölümü)", True),  "2": ("BUT (Temel taşı)", False)},
    "gurt": {"1": ("GU:RT (Kurt, hayvan)", True),  "2": ("GURT (Kurutulmuş süzme)", False)},
    "saç":  {"1": ("SA:Ç (Sac metal)", True),      "2": ("SAÇ (Saç kılı)", False)},
    "yok":  {"1": ("YO:K (Yok, var olmayan)", True),"2": ("YOK (Kalıntı, iz)", False)},
    "ot":   {"1": ("O:T (Ateş)", False),            "2": ("OT (Bitki)", False)}
}


# ==============================================================================
#  POS ETİKET DÖNÜŞÜM TABLOSU
# ==============================================================================

# Sözlük dosyasındaki format → internal kısa kod
POS_TAG_MAP = {
    "%<n%>":      "n",
    "%<v%>":      "v",
    "%<adj%>":    "adj",
    "%<adv%>":    "adv",
    "%<conj%>":   "conj",
    "%<det%>":    "det",
    "%<interj%>": "interj",
    "%<num%>":    "num",
    "%<phr%>":    "phr",
    "%<postp%>":  "postp",
    "%<prep%>":   "prep",
    "%<pro%>":    "pro",
    "%<np%>":     "np",
    "%<suf%>":    "suf",
    "%<unk%>":    "unk",
    "%<n?%>":     "n?",   # POS belirsiz — muhtemelen isim (tum.txt kaynağı)
}

# POS görüntüleme etiketleri (Türkmence/Türkçe)
POS_DISPLAY = {
    "n":      "At (İsim)",
    "v":      "İşlik (Fiil)",
    "adj":    "Sypat (Sıfat)",
    "adv":    "Hal (Zarf)",
    "conj":   "Baglanyşyk (Bağlaç)",
    "det":    "Belgilik (Belirteç)",
    "interj": "Ündew (Ünlem)",
    "num":    "San (Sayı)",
    "phr":    "Söz düzümi (Deyim)",
    "postp":  "Sözsoňy (Son edat)",
    "prep":   "Sözöňi (Ön edat)",
    "pro":    "Çalyşma (Zamir)",
    "np":     "Özel at (Özel isim)",
    "suf":    "Goşulma (Ek)",
    "unk":    "Näbelli (Bilinmiyor)",
    "n?":     "At? (Muhtemel isim)",
}


# ==============================================================================
#  ANA SÖZLÜK SINIFI
# ==============================================================================

class Lexicon:
    """
    Ana sözlük sınıfı.
    
    Sözlük dosyasını yükler, kelime arar, morfolojik özellikleri yönetir.
    
    Kullanım:
        lexicon = Lexicon()
        lexicon.load("data/turkmence_sozluk.txt")
        entries = lexicon.lookup("kitap")
    """

    def __init__(self):
        self._entries: dict[str, list[LexiconEntry]] = {}  # kelime → [LexiconEntry, ...]
        self._loaded = False
        self._word_count = 0

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def word_count(self) -> int:
        return self._word_count

    def load(self, path: str) -> int:
        """
        Sözlük dosyasını yükler.
        
        Args:
            path: turkmence_sozluk.txt dosya yolu
        
        Returns:
            Yüklenen kelime sayısı
        """
        self._entries.clear()
        count = 0

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Boş satır, yorum satırı veya etiket tanımı satırını atla
                if not line or line.startswith("#") or line.startswith("="):
                    continue
                # Etiket tanım satırlarını atla (ör. %<adj%>      ! Adjective)
                if line.startswith("%<") and "!" in line:
                    continue

                parts = line.split("\t")
                if len(parts) < 2:
                    continue

                word = parts[0].strip()
                pos_raw = parts[1].strip()

                # POS etiketi dönüşümü
                pos = POS_TAG_MAP.get(pos_raw, "unk")

                # Morfolojik özellikleri sözlük dosyasından oku (3. sütun)
                if len(parts) >= 3:
                    features = self._parse_features(parts[2].strip(), word, pos)
                else:
                    # Eski format — otomatik hesapla (geriye uyumluluk)
                    features = self._compute_features(word, pos)

                entry = LexiconEntry(word=word, pos=pos, features=features)

                key = word.lower()
                if key not in self._entries:
                    self._entries[key] = []
                self._entries[key].append(entry)
                count += 1

        self._word_count = count
        self._loaded = True
        return count

    def _compute_features(self, word: str, pos: str) -> dict:
        """
        Kelime için morfolojik özellikleri otomatik hesaplar (eski format uyumluluk).
        
        Mevcut global listelerden (DUSME_ADAYLARI, DUSME_ISTISNALARI, YUMUSAMA_TABLOSU)
        bilgi çekerek her girişe entegre eder.
        """
        w = word.lower()
        features = {}

        # Ünlü düşmesi
        if w in VOWEL_DROP_EXCEPTIONS:
            features["vowel_drop"] = True
            features["exception_drop"] = True
            features["dropped_form"] = VOWEL_DROP_EXCEPTIONS[w]
        elif w in VOWEL_DROP_CANDIDATES:
            features["vowel_drop"] = True
            features["exception_drop"] = False

        # Ünsüz yumuşaması (isimler için)
        if pos in ("n", "np", "n?") and w and w[-1] in SOFTENING_TABLE:
            features["softening"] = True

        return features

    def _parse_features(self, feature_str: str, word: str, pos: str) -> dict:
        """
        Sözlük dosyasındaki 3. sütundaki özellik stringini parse eder.
        
        Format örnekleri:
            vowel_drop
            exception_drop:asl
            softening
            homonym:1=A:T_(Ad,_isim)|yes;2=AT_(At,_beygir)|no
            vowel_drop;softening
        """
        features = {}
        if not feature_str:
            return features

        for token in feature_str.split(";"):
            token = token.strip()
            if not token:
                continue
            
            if token == "vowel_drop":
                features["vowel_drop"] = True
                features["exception_drop"] = False
            elif token.startswith("exception_drop:"):
                dropped_form = token.split(":", 1)[1]
                features["vowel_drop"] = True
                features["exception_drop"] = True
                features["dropped_form"] = dropped_form
            elif token == "softening":
                features["softening"] = True
            elif token.startswith("homonym:"):
                features["homonym"] = True
                # Homonym detayları token'ın geri kalanında
                homonym_data = token.split(":", 1)[1]
                features["homonym_data"] = homonym_data
        
        return features

    def lookup(self, word: str) -> list[LexiconEntry]:
        """
        Kelime ara. Bulunamazsa boş liste döndürür.
        
        Args:
            word: Aranacak kelime
        Returns:
            Eşleşen sözlük girişleri
        """
        return self._entries.get(word.lower(), [])

    def exists(self, word: str) -> bool:
        """Kelime sözlükte var mı?"""
        return word.lower() in self._entries

    def get_homonyms(self, word: str) -> Optional[dict]:
        """
        Eş sesli kelime bilgilerini döndürür.
        
        Returns:
            Eş sesli sözlüğü veya None
        """
        return HOMONYMS.get(word.lower())

    def is_homonym(self, word: str) -> bool:
        """Kelime eş sesli mi?"""
        return word.lower() in HOMONYMS

    def get_pos(self, word: str) -> Optional[str]:
        """
        Kelimenin POS etiketini döndürür.
        Birden fazla giriş varsa ilkini döndürür.
        """
        entries = self.lookup(word)
        return entries[0].pos if entries else None

    def get_nouns(self) -> list[LexiconEntry]:
        """Tüm isimleri döndürür (n ve n? dahil)."""
        result = []
        for entries in self._entries.values():
            for entry in entries:
                if entry.pos in ("n", "n?"):
                    result.append(entry)
        return result

    def get_verbs(self) -> list[LexiconEntry]:
        """Tüm fiilleri döndürür."""
        result = []
        for entries in self._entries.values():
            for entry in entries:
                if entry.pos == "v":
                    result.append(entry)
        return result

    def get_by_pos(self, pos: str) -> list[LexiconEntry]:
        """Belirli bir POS etiketine sahip tüm kelimeleri döndürür."""
        result = []
        for entries in self._entries.values():
            for entry in entries:
                if entry.pos == pos:
                    result.append(entry)
        return result

    def all_words(self) -> list[str]:
        """Tüm kelimelerin listesini döndürür."""
        return list(self._entries.keys())

    def __len__(self) -> int:
        return self._word_count

    def __contains__(self, word: str) -> bool:
        return self.exists(word)

    def __repr__(self) -> str:
        return f"Lexicon(words={self._word_count}, loaded={self._loaded})"
