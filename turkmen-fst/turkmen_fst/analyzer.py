# -*- coding: utf-8 -*-
"""
TurkmenFST — Tahlil (Analiz / Derňew) Motoru (analyzer.py)

Çekimli kelime → Kök + morfem çözümlemesi.

Strateji: Generator-doğrulamalı ters çözümleme (reverse generation).
Her olası kök adayı + ek kombinasyonunu generator ile üretip
giriş kelimesiyle eşleştirerek %100 doğru sonuç verir.

İsim analizi: parse_noun()  — hal, iyelik, çoğul ekleri ayırma
Fiil analizi: parse_verb()  — zaman, şahıs, olumsuzluk ekleri ayırma
Otomatik:     parse()       — birden fazla sonuç döndürebilen ana giriş noktası
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from turkmen_fst.phonology import (
    PhonologyRules, VowelSystem, SOFTENING_TABLE,
    VOWEL_DROP_CANDIDATES, VOWEL_DROP_EXCEPTIONS,
    YUVARLAKLASMA_LISTESI
)
from turkmen_fst.lexicon import Lexicon, HOMONYMS


# ==============================================================================
#  ANALİZ SONUÇ YAPISI
# ==============================================================================

@dataclass
class AnalysisResult:
    """
    Tek bir morfolojik çözümleme sonucu.
    
    Attributes:
        success: Analiz başarılı mı
        original: Orijinal kelime
        stem: Bulunan kök
        suffixes: Ek listesi (her biri dict: suffix, type, code)
        breakdown: Analiz string'i (ör. "Kitap (Kök) + lar (S2) + ym (D₁b)")
        word_type: "noun" / "verb" / "unknown"
        meaning: Eş sesli kelimeler için anlam açıklaması
    """
    success: bool = False
    original: str = ""
    stem: str = ""
    suffixes: list = field(default_factory=list)
    breakdown: str = ""
    word_type: str = "unknown"
    meaning: str = ""


@dataclass
class MultiAnalysisResult:
    """
    Çoklu sonuç döndüren analiz yapısı.
    
    Attributes:
        original: Orijinal kelime
        results: AnalysisResult listesi
        count: Sonuç sayısı
    """
    original: str = ""
    results: list = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.results)

    @property
    def success(self) -> bool:
        return self.count > 0


# ==============================================================================
#  DISPLAY KODLARI
# ==============================================================================

POSSESSIVE_DISPLAY = {
    "A1": "D₁b", "A2": "D₂b", "A3": "D₃b",
    "B1": "D₁k", "B2": "D₂k",
}

CASE_DISPLAY = {
    "A2": "A₂", "A3": "A₃", "A4": "A₄", "A5": "A₅", "A6": "A₆",
}

TENSE_DISPLAY = {
    "1": "Ö1", "2": "Ö2", "3": "Ö3",
    "4": "H1", "5": "H2",
    "6": "G1", "7": "G2",
    # Goşma zamanlar
    "22": "HK_GN", "23": "HK_HD", "24": "HK_ÖR", "25": "HK_GL",
    "26": "HK_NY", "27": "HK_ŞR", "28": "HK_HK",
    "29": "RW_GN", "30": "RW_HD", "31": "RW_ÖR", "32": "RW_HK",
    "33": "ŞR_GL", "34": "ŞR_NY", "35": "ŞR_ŞR",
}


# ==============================================================================
#  MORFOLOJİK ANALİZÖR
# ==============================================================================

# ==============================================================================
#  Yuvarlaklaşma toleranslı karşılaştırma
# ==============================================================================

# Yuvarlaklaşma çiftleri: u↔y ve ü↔i
_ROUNDING_PAIRS = frozenset({('u', 'y'), ('y', 'u'), ('ü', 'i'), ('i', 'ü')})

def _rounding_equivalent(gen_word: str, input_word: str) -> bool:
    """
    İki kelimenin yuvarlaklaşma farkları hariç eşit olup olmadığını kontrol eder.
    
    Türkmen'de bazı çekimlerda y↔u ve i↔ü dönüşümü olur.
    Kullanıcı 'okuwçylar' yazabilir ama generator 'okuwçular' üretir.
    Bu fonksiyon her iki formu da kabul eder.
    
    Örnekler:
        okuwçular ↔ okuwçylar  → True
        gözlerüňiz ↔ gözleriňiz → True
        kitap ↔ kitab           → False (farklı uzunluk)
        kitap ↔ kitap           → True
    """
    if gen_word == input_word:
        return True
    if len(gen_word) != len(input_word):
        return False
    for g, i in zip(gen_word, input_word):
        if g != i and (g, i) not in _ROUNDING_PAIRS:
            return False
    return True


class MorphologicalAnalyzer:
    """
    Generator-doğrulamalı morfolojik çözümleyici.
    
    Strateji:
    1. Olası kök adaylarını üret (ek soyma + ses değişimi geri alma + sözlük kontrolü)
    2. Her aday için tüm (çoğul, iyelik, hal) kombinasyonlarını generator ile üret
    3. Üretilen kelime girişle eşleşirse → geçerli çözümleme
    4. Birden fazla eşleşme varsa hepsini döndür
    
    Kullanım:
        analyzer = MorphologicalAnalyzer(lexicon)
        multi = analyzer.parse("kitabym")
        for r in multi.results:
            print(r.breakdown)
    """

    def __init__(self, lexicon: Optional[Lexicon] = None):
        self.lexicon = lexicon
        self._noun_gen = None
        self._verb_gen = None

    @property
    def noun_gen(self):
        if self._noun_gen is None:
            from turkmen_fst.generator import NounGenerator
            self._noun_gen = NounGenerator(self.lexicon)
        return self._noun_gen

    @property
    def verb_gen(self):
        if self._verb_gen is None:
            from turkmen_fst.generator import VerbGenerator
            self._verb_gen = VerbGenerator(self.lexicon)
        return self._verb_gen

    # ------------------------------------------------------------------
    #  KÖK ADAY OLUŞTURUCU
    # ------------------------------------------------------------------

    def _generate_stem_candidates(self, word: str) -> list[str]:
        """
        Verilen kelimeden olası kök adaylarını üretir.
        
        Ek soyma, ünsüz yumuşaması / ünlü düşmesi / yuvarlaklaşma
        geri alma işlemleriyle tüm olası kökleri listeler,
        sonra sözlüke kontrol ederek filtreler.
        """
        candidates = set()
        w = word.lower()

        # Kelime doğrudan kök olabilir
        candidates.add(w)

        # Son 1-12 karakteri soyarak olası kökler
        for end_len in range(1, min(13, len(w))):
            remaining = w[:-end_len]
            if len(remaining) < 1:
                continue
            candidates.add(remaining)

            # Ünsüz yumuşamasını geri al (b→p, d→t, j→ç, g→k)
            hard = PhonologyRules.reverse_consonant_softening(remaining)
            if hard != remaining:
                candidates.add(hard)

            # Ünlü düşmesini geri al (burn→burun, asl→asyl)
            restored = PhonologyRules.reverse_vowel_drop(remaining)
            if restored:
                candidates.add(restored)
            restored_hard = PhonologyRules.reverse_vowel_drop(hard)
            if restored_hard:
                candidates.add(restored_hard)

            # Yuvarlaklaşmayı geri al (guzu→guzy, sürü→süri)
            for orig, rounded in YUVARLAKLASMA_LISTESI.items():
                if remaining.startswith(rounded):
                    candidates.add(orig + remaining[len(rounded):])

            # Genel yuvarlaklaşma geri al: son harf u→y veya ü→i
            if remaining and remaining[-1] == 'u':
                candidates.add(remaining[:-1] + 'y')
            elif remaining and remaining[-1] == 'ü':
                candidates.add(remaining[:-1] + 'i')

        # Sözlükte olanları filtrele
        if self.lexicon:
            verified = [c for c in candidates if self.lexicon.exists(c)]
            return sorted(verified, key=len, reverse=True)

        return sorted(candidates, key=len, reverse=True)

    # ------------------------------------------------------------------
    #  İSİM TAHLİLİ
    # ------------------------------------------------------------------

    def parse_noun(self, word: str) -> list[AnalysisResult]:
        """
        İsim kelimesini generator ile doğrulayarak çözümler.

        Her kök adayı × her (çoğul, iyelik, hal) kombinasyonu denenir.
        Üretim sonucu girişle eşleşirse geçerli çözümleme olarak eklenir.
        """
        w = word.lower().strip()
        if not w:
            return []

        results = []
        seen = set()

        candidates = self._generate_stem_candidates(w)

        plural_opts = [False, True]
        poss_opts = [None, "A1", "A2", "A3"]
        poss_type_opts = ["tek", "cog"]
        case_opts = [None, "A2", "A3", "A4", "A5", "A6"]

        for stem in candidates:
            # Eş sesli kelime kontrolü
            homonym_data = HOMONYMS.get(stem)
            yumusama_variants = []

            if homonym_data:
                for key, (anlam, yumusama) in homonym_data.items():
                    yumusama_variants.append((yumusama, anlam))
            else:
                # Sözlükteki softening bayrağına bak
                entries = self.lexicon.lookup(stem)
                noun_entries = [e for e in entries if e.pos in ("n", "np", "n?")]
                if noun_entries:
                    yumusama = noun_entries[0].allows_softening
                    yumusama_variants.append((yumusama, ""))
                else:
                    # İsim olarak bulunamadıysa yumuşamasız dene
                    yumusama_variants.append((False, ""))

            for yumusama_izni, anlam in yumusama_variants:
                for plural in plural_opts:
                    for poss in poss_opts:
                        for poss_type in poss_type_opts:
                            # İyelik yoksa sadece tek dene (gereksiz çoğullama engelle)
                            if poss is None and poss_type == "cog":
                                continue

                            for case in case_opts:
                                # Yalın hal + ek yok = sadece kök
                                if not plural and poss is None and case is None:
                                    if stem == w:
                                        key = f"{stem}|bare|{anlam}"
                                        if key not in seen:
                                            seen.add(key)
                                            results.append(AnalysisResult(
                                                success=True,
                                                original=word,
                                                stem=stem.capitalize(),
                                                suffixes=[],
                                                breakdown=f"{stem.capitalize()} (Kök)",
                                                word_type="noun",
                                                meaning=anlam
                                            ))
                                    continue

                                try:
                                    gen = self.noun_gen.generate(
                                        stem, plural, poss, poss_type, case,
                                        yumusama_izni=yumusama_izni
                                    )
                                except Exception:
                                    continue

                                if not gen.is_valid or not _rounding_equivalent(gen.word.lower(), w):
                                    continue

                                # İyelik display kodu
                                actual_poss_code = poss
                                if poss and poss_type == "cog":
                                    actual_poss_code = {"A1": "B1", "A2": "B2"}.get(poss, poss)

                                sig = f"{stem}|{plural}|{actual_poss_code}|{case}|{anlam}"
                                if sig in seen:
                                    continue
                                seen.add(sig)

                                # Ek listesi oluştur
                                suffixes = []
                                mi = 0  # morpheme index

                                if plural and mi < len(gen.morphemes):
                                    _, suf = gen.morphemes[mi]
                                    suffixes.append({"suffix": suf, "type": "San", "code": "S2"})
                                    mi += 1

                                if poss and mi < len(gen.morphemes):
                                    _, suf = gen.morphemes[mi]
                                    disp = POSSESSIVE_DISPLAY.get(actual_poss_code, actual_poss_code)
                                    suffixes.append({"suffix": suf, "type": "Degişlilik", "code": disp})
                                    mi += 1

                                if case and mi < len(gen.morphemes):
                                    _, suf = gen.morphemes[mi]
                                    disp = CASE_DISPLAY.get(case, case)
                                    suffixes.append({"suffix": suf, "type": "Düşüm", "code": disp})

                                parts = [f"{stem.capitalize()} (Kök)"]
                                for s in suffixes:
                                    parts.append(f"{s['suffix']} ({s['code']})")

                                results.append(AnalysisResult(
                                    success=True,
                                    original=word,
                                    stem=stem.capitalize(),
                                    suffixes=suffixes,
                                    breakdown=" + ".join(parts),
                                    word_type="noun",
                                    meaning=anlam
                                ))

        # Sıralama: tam kök eşleşmesi önce, hayalet ekler en sona
        w_lower = word.lower().strip()
        def _noun_sort_key(r):
            stem_lower = r.stem.lower()
            is_bare = len(r.suffixes) == 0 and stem_lower == w_lower
            is_ghost = len(r.suffixes) > 0 and stem_lower == w_lower
            return (
                0 if is_bare else (2 if is_ghost else 1),
                -len(r.stem),        # uzun kök önce
                len(r.suffixes),     # az ekli önce
            )
        results.sort(key=_noun_sort_key)
        return results

    # ------------------------------------------------------------------
    #  FİİL TAHLİLİ
    # ------------------------------------------------------------------

    # Zamir → şahıs eşleştirme
    _ZAMIRLER = {
        "men": "A1", "sen": "A2", "ol": "A3",
        "biz": "B1", "siz": "B2", "olar": "B3"
    }

    def parse_verb(self, word: str) -> list[AnalysisResult]:
        """
        Fiil kelimesini generator ile doğrulayarak çözümler.
        Her kök adayı × her (zaman, şahıs, olumsuzluk) kombinasyonu denenir.

        Çok kelimeli girişi de destekler: "Men geljek", "Biz geldik däl" vb.
        Zamir + fiil formu → tek çözümleme olarak döner.
        """
        w = word.lower().strip()
        if not w:
            return []

        # ── Çok kelimeli giriş: Zamir + Fiil (+ däl) ──
        w_parts = w.split()
        is_multi_word = len(w_parts) > 1
        verb_token = w  # tek kelimede aynen kullan

        if is_multi_word:
            first = w_parts[0]
            # Zamir ile başlıyorsa, fiil kısmını çıkar
            if first in self._ZAMIRLER:
                verb_token = w_parts[1]  # "geljek" kısmı
            else:
                verb_token = w_parts[0]  # zamir yoksa ilk kelime

        results = []
        seen = set()

        candidates = self._generate_stem_candidates(verb_token)

        # 1-7: temel zamanlar, 8-18: şert/buýruk/ortaç/ulaç/ettirgen vb.
        # 22-35: goşma zamanlar (hekaýa/rowaýat/şert)
        tense_opts = [str(i) for i in range(1, 19)] + [str(i) for i in range(22, 36)]
        person_opts = ["A1", "A2", "A3", "B1", "B2", "B3"]

        for stem in candidates:
            for tense in tense_opts:
                for person in person_opts:
                    for neg in [False, True]:
                        try:
                            gen = self.verb_gen.generate(stem, tense, person, neg)
                        except Exception:
                            continue

                        if not gen.is_valid:
                            continue

                        # Fiil çekimi "Zamir kelime" veya "kelime" olabilir
                        gen_word = gen.word.lower()
                        gen_parts = gen_word.split()
                        gen_word_only = gen_parts[-1] if len(gen_parts) >= 2 else gen_word

                        # Eşleşme kontrolü: tam form veya sadece fiil kısmı
                        matched = False
                        if is_multi_word:
                            # Çok kelimeli giriş: tam üretim ("men geljek" vs "men geljek")
                            if _rounding_equivalent(gen_word, w):
                                matched = True
                            # Veya däl içeren olumsuz: "men geljek däl" vs gen+däl
                            elif len(w_parts) >= 3 and w_parts[-1] in ("däl", "däldir"):
                                w_without_dal = " ".join(w_parts[:-1])
                                if _rounding_equivalent(gen_word, w_without_dal):
                                    matched = True
                        else:
                            # Tek kelime: zamirsiz kısım
                            if _rounding_equivalent(gen_word_only, w):
                                matched = True

                        if not matched:
                            continue

                        tense_disp = TENSE_DISPLAY.get(tense, tense)
                        sig = f"{stem}|{tense}|{person}|{neg}"
                        if sig in seen:
                            continue
                        seen.add(sig)

                        # Aynı breakdown'u tekrar ekleme (ör. G1'de A1-B2 aynı kelime)
                        breakdown_key = f"{stem}|{tense}|{neg}|{gen_word_only}"
                        if breakdown_key in seen:
                            continue
                        seen.add(breakdown_key)

                        suffixes = []
                        for cat, suf in gen.morphemes:
                            if cat == "NEGATION":
                                suffixes.append({"suffix": suf, "type": "Olumsuzluk", "code": "Olumsuz"})
                            elif cat == "TENSE":
                                suffixes.append({"suffix": suf, "type": "Zaman", "code": tense_disp})
                            elif cat in ("PERSON", "PERSON1", "PERSON2"):
                                suffixes.append({"suffix": suf, "type": "Şahıs", "code": person})
                            elif cat == "HEKAYA":
                                suffixes.append({"suffix": suf, "type": "Hekaýa", "code": "HK"})
                            elif cat == "ROWAYAT":
                                suffixes.append({"suffix": suf, "type": "Rowaýat", "code": "RW"})
                            elif cat == "CONDITIONAL_BOL":
                                suffixes.append({"suffix": suf, "type": "Şert (bol-)", "code": "ŞR"})
                            elif cat == "NEGATION+TENSE":
                                suffixes.append({"suffix": suf, "type": "Olumsuz+Zaman", "code": tense_disp})

                        parts = [f"{stem.capitalize()} (Kök)"]
                        for s in suffixes:
                            parts.append(f"{s['suffix']} ({s['code']})")

                        results.append(AnalysisResult(
                            success=True,
                            original=word,
                            stem=stem.capitalize(),
                            suffixes=suffixes,
                            breakdown=" + ".join(parts),
                            word_type="verb"
                        ))

        return results

    # ------------------------------------------------------------------
    #  ANA GİRİŞ NOKTASI
    # ------------------------------------------------------------------

    def parse(self, word: str) -> MultiAnalysisResult:
        """
        Verilen kelimeyi hem isim hem fiil olarak analiz eder.
        Birden fazla geçerli çözümleme varsa hepsini döndürür.

        Args:
            word: Çekimli kelime (ör. "kitabym", "geldim", "guzulary")

        Returns:
            MultiAnalysisResult — tüm geçerli çözümlemeler
        """
        word = word.strip()
        if not word:
            return MultiAnalysisResult(original=word)

        w_lower = word.lower()

        # ── Sıra sayı tanıma: "2024-nji", "25-njy", "ýedinji" ──
        import re as _re
        _ordinal_m = _re.match(r'^(\d+)-(nji|njy)$', w_lower)
        if _ordinal_m:
            num = _ordinal_m.group(1)
            suf = _ordinal_m.group(2)
            return MultiAnalysisResult(original=word, results=[AnalysisResult(
                success=True, original=word,
                stem=num, suffixes=[{"suffix": suf, "type": "Sıra", "code": "SıS"}],
                breakdown=f"{num} + {suf} (Sıra sayı)",
                word_type="noun"
            )])

        # ── Tireli bağlaç/zarf tanıma ──
        _TIRELI_BAGLACLAR = {
            "hem-de": ("hem-de", "bağlaç", "ayrıca, ve"),
            "has-da": ("has-da", "bağlaç", "daha da"),
            "beýläk-de": ("beýläk-de", "bağlaç", "bundan böyle"),
            "hususan-da": ("hususan-da", "zarf", "özellikle"),
            "ýene-de": ("ýene-de", "bağlaç", "yine de"),
            "başga-da": ("başga-da", "bağlaç", "başka da"),
            "şeýle-de": ("şeýle-de", "bağlaç", "ayrıca, öyle de"),
        }
        if w_lower in _TIRELI_BAGLACLAR:
            stem, wtype, meaning = _TIRELI_BAGLACLAR[w_lower]
            return MultiAnalysisResult(original=word, results=[AnalysisResult(
                success=True, original=word,
                stem=stem.capitalize(), suffixes=[],
                breakdown=f"{stem.capitalize()} ({wtype})",
                word_type="noun", meaning=meaning
            )])

        all_results = []

        # İsim olarak çözümle
        all_results.extend(self.parse_noun(word))

        # Fiil olarak çözümle
        all_results.extend(self.parse_verb(word))

        # İsim–fiil arası çapraz tekilleştirme (ot/at gibi eş sesliler)
        seen_breakdowns = set()
        unique_results = []
        for r in all_results:
            if r.breakdown not in seen_breakdowns:
                seen_breakdowns.add(r.breakdown)
                unique_results.append(r)
        all_results = unique_results

        # ── Sonuç sıralama: en doğal çözümleme önce ──
        w_lower = word.lower().strip()

        def _sort_key(r):
            stem_lower = r.stem.lower()
            # 1) Tamamen eşleşen kök (bare root) en yüksek
            is_bare_root = len(r.suffixes) == 0 and stem_lower == w_lower
            # 2) Ek içeren fiil çözümlemeleri (değerli analiz)
            is_verb_with_suffix = r.word_type == "verb" and len(r.suffixes) > 0
            # 3) Hayalet ek: ek var ama kök == giriş kelimesi (form değişmemiş)
            is_ghost = len(r.suffixes) > 0 and stem_lower == w_lower
            return (
                0 if is_bare_root else (1 if is_verb_with_suffix else (3 if is_ghost else 2)),
                -len(r.stem),       # uzun kök önce
                -len(r.suffixes),   # çok ekli sonra
            )

        all_results.sort(key=_sort_key)

        # Hiç sonuç yoksa bilinmeyen kök olarak döndür
        if not all_results:
            all_results.append(AnalysisResult(
                success=True,
                original=word,
                stem=word.capitalize(),
                suffixes=[],
                breakdown=f"{word.capitalize()} (Kök)",
                word_type="unknown"
            ))

        return MultiAnalysisResult(original=word, results=all_results)
