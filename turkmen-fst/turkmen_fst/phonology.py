# -*- coding: utf-8 -*-
"""
TurkmenFST — Fonoloji Modülü (phonology.py)

Türkmen Türkçesinin ses kurallarını tek yerde toplar:
  - Ünlü sistemi (kalın/ince, yuvarlak/düz)
  - Ünlü uyumu
  - Ünsüz yumuşaması (p→b, ç→j, t→d, k→g)
  - Ünlü düşmesi (burun→burn, asyl→asl)
  - Yuvarlaklaşma uyumu

Mevcut morphology.py'den ayıklanmış ve modülerleştirilmiş versiyon.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ==============================================================================
#  ÜNLÜ SİSTEMİ
# ==============================================================================

class VowelSystem:
    """
    Türkmen Türkçesi ünlü sistemi.
    
    Kalın (yogyn): a, o, u, y
    İnce:          e, ä, ö, i, ü  
    Yuvarlak:      o, ö, u, ü
    """
    YOGYN  = frozenset("aouy")       # Kalın ünlüler (back vowels)
    INCE   = frozenset("eäöiü")      # İnce ünlüler (front vowels)
    DODAK  = frozenset("oöuü")       # Yuvarlak ünlüler (rounded vowels)
    ALL    = YOGYN | INCE            # Tüm ünlüler


# ==============================================================================
#  ÜNSÜZ YUMUŞAMA TABLOSU
# ==============================================================================

# Sert ünsüz → yumuşak ünsüz dönüşümü
SOFTENING_TABLE = {'p': 'b', 'ç': 'j', 't': 'd', 'k': 'g'}

# Yumuşak → sert (ters yön, analiz için)
HARDENING_TABLE = {v: k for k, v in SOFTENING_TABLE.items()}


# ==============================================================================
#  ÜNLÜ DÜŞME VERİLERİ
# ==============================================================================

# İstisna ünlü düşmeleri (özel kelimeler — düzensiz değişim)
VOWEL_DROP_EXCEPTIONS = {
    "asyl": "asl", "pasyl": "pasl", "nesil": "nesl",
    "ylym": "ylm", "mähir": "mähr"
}

# Genel ünlü düşme adayları (son hecedeki ünlü düşer)
VOWEL_DROP_CANDIDATES = frozenset({
    "burun", "alyn", "agyz", "gobek", "ogul", "erin",
    "bagyr", "sabyr", "kömür", "sygyr", "deňiz",
    "goýun", "boýun", "howuz", "tomus", "tizir",
    "köwüş", "orun", "garyn", "gelin"
})

# Özel yuvarlaklaşma listesi (y/i → u/ü dönüşümü)
# Bu kelimeler hal ekleri (A5, A6) öncesinde de yuvarlaklaşır.
# Jenerik kural sadece çokluk ve 3. iyelik öncesinde uygulanır;
# bu liste A5/A6 yalın hal için ek kural sağlar.
YUVARLAKLASMA_LISTESI = {
    "guzy": "guzu",
    "süri": "sürü",
    "guýy": "guýu"
}


# ==============================================================================
#  FONOLOJİ KURALLARI
# ==============================================================================

class PhonologyRules:
    """
    Fonotaktik kurallar — pipeline olarak çalışır.
    
    Her metot saf (pure) fonksiyon gibi davranır: girdi alır, çıktı döndürür.
    State tutmaz — modüler ve test edilebilir.
    """

    # -- Ünlü nitelikleri ------------------------------------------------

    @staticmethod
    def get_vowel_quality(word: str) -> str:
        """
        Kelimenin son ünlüsüne göre kalınlık niteliğini döndürür.
        
        Returns:
            "yogyn" (kalın/back) veya "ince" (ince/front)
        """
        for ch in reversed(word.lower()):
            if ch in VowelSystem.YOGYN:
                return "yogyn"
            if ch in VowelSystem.INCE:
                return "ince"
        return "yogyn"  # Varsayılan: kalın

    @staticmethod
    def has_rounded_vowel(word: str) -> bool:
        """Kelimede yuvarlak (dudak) ünlü var mı?"""
        return any(ch in VowelSystem.DODAK for ch in word.lower())

    @staticmethod
    def ends_with_vowel(word: str) -> bool:
        """Son harf ünlü mü?"""
        if not word:
            return False
        return word[-1].lower() in VowelSystem.ALL

    @staticmethod
    def last_vowel(word: str) -> Optional[str]:
        """Kelimenin son ünlüsünü döndürür. Yoksa None."""
        for ch in reversed(word.lower()):
            if ch in VowelSystem.ALL:
                return ch
        return None

    # -- Ünsüz yumuşaması ------------------------------------------------

    @staticmethod
    def apply_consonant_softening(stem: str) -> str:
        """
        Ünsüz yumuşaması uygular (kökün son harfine).
        
        Kurallar: p→b, ç→j, t→d, k→g
        Örnek:  kitap → kitab, agaç → agaj
        """
        if stem and stem[-1] in SOFTENING_TABLE:
            return stem[:-1] + SOFTENING_TABLE[stem[-1]]
        return stem

    @staticmethod
    def reverse_consonant_softening(stem: str) -> str:
        """
        Ünsüz yumuşamasını geri alır (analiz için).
        
        Kurallar: b→p, j→ç, d→t, g→k
        """
        if stem and stem[-1] in HARDENING_TABLE:
            return stem[:-1] + HARDENING_TABLE[stem[-1]]
        return stem

    # -- Ünlü düşmesi ----------------------------------------------------

    @staticmethod
    def apply_vowel_drop(stem: str, suffix: str) -> str:
        """
        Ünlü düşmesi uygular: ek ünlüyle başlıyorsa, kökün son hecesindeki
        ünlü düşebilir.
        
        Örnekler:
            burun + um → burn + um
            asyl  + y  → asl + y
        """
        stem_lower = stem.lower()
        suffix_lower = suffix.lower()

        # Ek ünlüyle başlamıyorsa düşme olmaz
        if not suffix_lower or suffix_lower[0] not in VowelSystem.ALL:
            return stem_lower

        # İstisna kelimeleri kontrol et
        if stem_lower in VOWEL_DROP_EXCEPTIONS:
            return VOWEL_DROP_EXCEPTIONS[stem_lower]

        # Genel düşme adayları: sondan 2. harfi (ünlü) düşür
        if stem_lower in VOWEL_DROP_CANDIDATES:
            return stem_lower[:-2] + stem_lower[-1]

        return stem_lower

    @staticmethod
    def reverse_vowel_drop(stem: str) -> Optional[str]:
        """
        Ünlü düşmesini geri alır (analiz için).
        burn → burun, asl → asyl
        
        Returns:
            Orijinal kök veya None (eşleşme yoksa)
        """
        # İstisna tablosunu ters çevir
        reverse_exceptions = {v: k for k, v in VOWEL_DROP_EXCEPTIONS.items()}
        stem_lower = stem.lower()
        if stem_lower in reverse_exceptions:
            return reverse_exceptions[stem_lower]
        
        # Genel düşme adayları tablosunu ters çevir
        for candidate in VOWEL_DROP_CANDIDATES:
            dropped = candidate[:-2] + candidate[-1]
            if dropped == stem_lower:
                return candidate
        
        return None

    # -- Yuvarlaklaşma uyumu ----------------------------------------------

    @staticmethod
    def apply_rounding_harmony(stem: str, quality: str) -> str:
        """
        Yuvarlaklaşma uyumu: son harf y/i ise ve kök yuvarlak ise,
        y→u (kalın) veya i→ü (ince) dönüşümü.
        
        Çoğul eki ve 3. tekil iyelik ekinden önce uygulanır.
        
        Args:
            stem: Gövde
            quality: "yogyn" veya "ince"
        Returns:
            Dönüştürülmüş gövde
        """
        if not stem:
            return stem
        if PhonologyRules.has_rounded_vowel(stem) and stem[-1] in "yi":
            return stem[:-1] + ("u" if quality == "yogyn" else "ü")
        return stem

    # -- Bileşik ses kuralı pipeline'ı ------------------------------------

    @staticmethod
    def apply_pre_suffix_rules(stem: str, suffix: str, 
                                apply_drop: bool = True,
                                apply_softening: bool = True) -> str:
        """
        Ek eklemeden önce uygulanan ses kuralları pipeline'ı.
        
        Sıra:
            1. Ünlü düşmesi (ek ünlüyle başlıyorsa)
            2. Ünsüz yumuşaması
        
        Args:
            stem: Kök/gövde
            suffix: Eklenecek ek
            apply_drop: Ünlü düşmesi uygulansın mı
            apply_softening: Ünsüz yumuşaması uygulansın mı
        """
        result = stem.lower()
        if apply_drop:
            result = PhonologyRules.apply_vowel_drop(result, suffix)
        if apply_softening:
            result = PhonologyRules.apply_consonant_softening(result)
        return result
