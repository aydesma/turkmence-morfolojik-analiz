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
        # case + daky pairs: normal cases OR daky (aitlik eki replaces case)
        case_daky_opts = [
            (None, False), ("A2", False), ("A3", False),
            ("A4", False), ("A5", False), ("A6", False),
            (None, True),  # daky: lokatif+kI → göreceli sıfat
        ]

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

                            for case, daky_flag in case_daky_opts:
                                # Yalın hal + ek yok = sadece kök
                                if not plural and poss is None and case is None and not daky_flag:
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
                                        yumusama_izni=yumusama_izni,
                                        daky=daky_flag
                                    )
                                except Exception:
                                    continue

                                if not gen.is_valid or not _rounding_equivalent(gen.word.lower(), w):
                                    continue

                                # İyelik display kodu
                                actual_poss_code = poss
                                if poss and poss_type == "cog":
                                    actual_poss_code = {"A1": "B1", "A2": "B2"}.get(poss, poss)

                                sig = f"{stem}|{plural}|{actual_poss_code}|{case}|{daky_flag}|{anlam}"
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

                                if case and not daky_flag and mi < len(gen.morphemes):
                                    _, suf = gen.morphemes[mi]
                                    disp = CASE_DISPLAY.get(case, case)
                                    suffixes.append({"suffix": suf, "type": "Düşüm", "code": disp})
                                    mi += 1

                                if daky_flag and mi < len(gen.morphemes):
                                    _, suf = gen.morphemes[mi]
                                    suffixes.append({"suffix": suf, "type": "Aitlik", "code": "+kI"})

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
                            elif cat == "CONVERB":
                                suffixes.append({"suffix": suf, "type": "Zarf-fiil", "code": tense_disp})
                            elif cat == "PARTICIPLE":
                                suffixes.append({"suffix": suf, "type": "Sıfat-fiil", "code": tense_disp})
                            elif cat == "CONDITIONAL":
                                suffixes.append({"suffix": suf, "type": "Şert", "code": tense_disp})
                            elif cat in ("NEGATION+CONDITIONAL",):
                                suffixes.append({"suffix": suf, "type": "Olumsuz+Şert", "code": tense_disp})
                            elif cat == "NEG_COPULA":
                                suffixes.append({"suffix": suf, "type": "Olumsuz", "code": "däl"})
                            elif cat == "CAUSATIVE":
                                suffixes.append({"suffix": suf, "type": "Ettirgen", "code": "Caus"})
                            elif cat == "PASSIVE":
                                suffixes.append({"suffix": suf, "type": "Edilgen", "code": "Pass"})
                            elif cat == "RECIPROCAL":
                                suffixes.append({"suffix": suf, "type": "İşteşlik", "code": "Rec"})
                            elif cat == "REFLEXIVE":
                                suffixes.append({"suffix": suf, "type": "Dönüşlü", "code": "Ref"})

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
    #  MASTAR (İNFİNİTİVE) TAHLİLİ
    #  -mAk/-mek + opsiyonel hal eki → fiilimsi isim
    #  Tabaklar §141: etmek, bermek, etmäge, edilmegi...
    # ------------------------------------------------------------------

    # Mastar ek kalıpları: (suffix, is_front, case_label, display)
    _INFINITIVE_PATTERNS = [
        # Yönelme (dative) — en yaygın, k→g + A/Ä
        ("maga", False, "A3", "-mAk+A3"),
        ("mäge", True, "A3", "-mAk+A3"),
        # Belirtme (accusative) — k→g + y/i
        ("magy", False, "A4", "-mAk+A4"),
        ("megi", True, "A4", "-mAk+A4"),
        # İlgi (genitive) — k→g + yň/iň
        ("magyň", False, "A2", "-mAk+A2"),
        ("megiň", True, "A2", "-mAk+A2"),
        # Bulunma (locative) — mAk+dA
        ("makda", False, "A5", "-mAk+A5"),
        ("mekde", True, "A5", "-mAk+A5"),
        # Çıkma (ablative) — mAk+dAn
        ("makdan", False, "A6", "-mAk+A6"),
        ("mekden", True, "A6", "-mAk+A6"),
        # Yalın (bare infinitive) — en son dene (daha kısa, daha çok false positive)
        ("mak", False, None, "-mAk"),
        ("mek", True, None, "-mAk"),
    ]

    def parse_infinitive(self, word: str) -> list[AnalysisResult]:
        """
        Kelimeyi mastar (infinitive) olarak çözümler.
        
        -mAk/-mek mastar ekleri + opsiyonel hal çekimi:
        bermek, goramak, etmäge, edilmegi, berkitmäge...
        """
        w = word.lower().strip()
        if len(w) < 4:  # en kısa: et+mek = 5 harf
            return []

        results = []
        seen = set()

        for suffix, is_front, case_label, display in self._INFINITIVE_PATTERNS:
            if not w.endswith(suffix):
                continue

            stem_part = w[:-len(suffix)]
            if len(stem_part) < 2:
                continue

            # Ünlü uyumu kontrolü: kalın kök + mak, ince kök + mek
            from turkmen_fst.phonology import PhonologyRules
            stem_quality = PhonologyRules.get_vowel_quality(stem_part)
            if is_front and stem_quality == "yogyn":
                continue
            if not is_front and stem_quality == "ince":
                continue

            # Sözlükte fiil olarak var mı?
            if self.lexicon:
                entries = self.lexicon.lookup(stem_part)
                verb_entries = [e for e in entries if e.pos == "v"]
                if not verb_entries:
                    continue
            else:
                continue

            sig = f"inf|{stem_part}|{suffix}"
            if sig in seen:
                continue
            seen.add(sig)

            # Ek bilgisi oluştur
            suffixes = [{"suffix": suffix, "type": "Mastar", "code": display}]
            if case_label:
                case_names = {"A2": "İlgi", "A3": "Yönelme", "A4": "Belirtme",
                              "A5": "Bulunma", "A6": "Çıkma"}
                parts_str = f"{stem_part.capitalize()} (Kök) + {suffix} ({display})"
            else:
                parts_str = f"{stem_part.capitalize()} (Kök) + {suffix} (Mastar)"

            results.append(AnalysisResult(
                success=True,
                original=word,
                stem=stem_part.capitalize(),
                suffixes=suffixes,
                breakdown=parts_str,
                word_type="verb"
            ))

        return results

    # ------------------------------------------------------------------
    #  TÜRETİLMİŞ FİİL ÇÖZÜMLEMESİ  (Ettirgen / Edilgen + Dış Çekim)
    # ------------------------------------------------------------------
    # Dış çekim kalıpları: (ek, etiket, kod, is_front)
    #   is_front=True  → ince (front) ünlü uyumu
    #   is_front=False → kalın (back) ünlü uyumu
    #   is_front=None  → her ikisi de olabilir
    _DERIVED_OUTER = [
        # ── Mastar + hal (uzundan kısaya) ──
        ("magyň",  "Mastar+İlgi",     "-mAk+A2", False),
        ("megiň",  "Mastar+İlgi",     "-mAk+A2", True),
        ("magy",   "Mastar+Belirtme", "-mAk+A4", False),
        ("megi",   "Mastar+Belirtme", "-mAk+A4", True),
        ("maga",   "Mastar+Yönelme",  "-mAk+A3", False),
        ("mäge",   "Mastar+Yönelme",  "-mAk+A3", True),
        ("makda",  "Mastar+Bulunma",  "-mAk+A5", False),
        ("mekde",  "Mastar+Bulunma",  "-mAk+A5", True),
        ("makdan", "Mastar+Çıkma",    "-mAk+A6", False),
        ("mekden", "Mastar+Çıkma",    "-mAk+A6", True),
        ("mak",    "Mastar",          "-mAk",    False),
        ("mek",    "Mastar",          "-mAk",    True),
        # ── Zarf-fiil (converb) -Ip ──
        ("yp", "Zarf-fiil", "-Ip", False),
        ("ip", "Zarf-fiil", "-Ip", True),
        ("up", "Zarf-fiil", "-Ip", False),
        ("üp", "Zarf-fiil", "-Ip", True),
        ("p",  "Zarf-fiil", "-Ip", None),
        # ── Geçmiş ortaç -An ──
        ("an", "Ortaç", "-An", False),
        ("en", "Ortaç", "-An", True),
        # ── Şimdiki ortaç -ýAn ──
        ("ýan", "Ortaç-ş", "-ýAn", False),
        ("ýän", "Ortaç-ş", "-ýAn", True),
        # ── Gelecek ortaç -jAk ──
        ("jak", "Ortaç-g", "-jAk", False),
        ("jek", "Ortaç-g", "-jAk", True),
        # ── Sonlu çekim (finite) — sık karşılaşılan 3.şahıs ──
        # Geçmiş -dI  (3.şahıs)
        ("dylar", "Geçmiş-3ç",  "Z1+3ç", False),
        ("diler", "Geçmiş-3ç",  "Z1+3ç", True),
        ("dy",    "Geçmiş",      "Z1",    False),
        ("di",    "Geçmiş",      "Z1",    True),
        # Şimdiki -ýAr (3.şahıs)
        ("ýarlar", "Şimdiki-3ç", "Z3+3ç", False),
        ("ýärler", "Şimdiki-3ç", "Z3+3ç", True),
        ("ýar",    "Şimdiki",    "Z3",    False),
        ("ýär",    "Şimdiki",    "Z3",    True),
    ]

    # Çatı ekleri (voice): (ek, etiket, kod, is_front)
    _VOICE = [
        # Ettirgen (causative) — uzundan kısaya
        ("dyr", "Ettirgen", "ETT", False),
        ("dir", "Ettirgen", "ETT", True),
        ("dur", "Ettirgen", "ETT", False),
        ("dür", "Ettirgen", "ETT", True),
        ("t",   "Ettirgen", "ETT", None),
        # Edilgen (passive) — uzundan kısaya
        ("yl", "Edilgen", "EDL", False),
        ("il", "Edilgen", "EDL", True),
        ("ul", "Edilgen", "EDL", False),
        ("ül", "Edilgen", "EDL", True),
        ("yn", "Edilgen", "EDL", False),
        ("in", "Edilgen", "EDL", True),
        ("un", "Edilgen", "EDL", False),
        ("ün", "Edilgen", "EDL", True),
        ("l",  "Edilgen", "EDL", None),
        ("n",  "Edilgen", "EDL", None),
        # İşteş (reciprocal)
        ("yş", "İşteş", "İŞT", False),
        ("iş", "İşteş", "İŞT", True),
        ("uş", "İşteş", "İŞT", False),
        ("üş", "İşteş", "İŞT", True),
        ("ş",  "İşteş", "İŞT", None),
    ]

    # Bildiriş kopulası (copula) — opsiyonel son katman
    _COPULA = ["dyr", "dir", "dur", "dür"]

    # ---- yardımcılar ----
    def _reverse_soften(self, base: str) -> list[str]:
        """Ters yumuşama adayları: d→t, g→k"""
        candidates = [base]
        if base.endswith("d"):
            candidates.append(base[:-1] + "t")
        elif base.endswith("g"):
            candidates.append(base[:-1] + "k")
        return candidates

    def _is_verb(self, stem: str) -> bool:
        """Sözlükte fiil kökü mü?"""
        if not self.lexicon:
            return False
        return any(e.pos == "v" for e in self.lexicon.lookup(stem))

    def parse_derived_verb(self, word: str) -> list[AnalysisResult]:
        """
        Türetilmiş fiil çözümlemesi.      kök_fiil + çatı_eki + dış_çekim

        Tek çatı örnekleri:
          ösdürmek   → ös + dür(ETT) + mek(Mastar)
          edilen     → et + il(EDL) + en(Ortaç)
          alnyp      → al + n(EDL) + yp(Zarf-fiil)

        Çift çatı örnekleri:
          göñükdirilen → göñük + dir(ETT) + il(EDL) + en(Ortaç)
        """
        w = word.lower().strip()
        if len(w) < 5:
            return []

        results: list[AnalysisResult] = []
        seen: set[str] = set()

        # Kopula katmanı: orijinal + opsiyonel -dIr sıyırma
        bases_to_try: list[tuple[str, str | None]] = [(w, None)]
        for cop in self._COPULA:
            if w.endswith(cop) and len(w) > len(cop) + 5:
                bases_to_try.append((w[:-len(cop)], cop))
                break  # tek kopula yeterli

        for base_w, copula in bases_to_try:

            # ═══ 1) Tek çatı:  base + voice + outer ═══
            for o_suf, o_lbl, o_code, o_fr in self._DERIVED_OUTER:
                if not base_w.endswith(o_suf):
                    continue
                derived = base_w[:-len(o_suf)]
                if len(derived) < 3:
                    continue

                for v_suf, v_lbl, v_code, v_fr in self._VOICE:
                    if not derived.endswith(v_suf):
                        continue
                    raw = derived[:-len(v_suf)]
                    if len(raw) < 2:
                        continue

                    for base in self._reverse_soften(raw):
                        if not self._is_verb(base):
                            continue
                        sig = f"dv|{base}|{v_suf}|{o_suf}|{copula}"
                        if sig in seen:
                            continue
                        seen.add(sig)

                        suf_list = [
                            {"suffix": v_suf, "type": v_lbl, "code": v_code},
                            {"suffix": o_suf, "type": o_lbl, "code": o_code},
                        ]
                        parts = f"{base.capitalize()} (Kök) + {v_suf} ({v_lbl}) + {o_suf} ({o_lbl})"
                        if copula:
                            suf_list.append({"suffix": copula, "type": "Bildiriş", "code": "-dIr"})
                            parts += f" + {copula} (Bildiriş)"

                        results.append(AnalysisResult(
                            success=True, original=word,
                            stem=base.capitalize(),
                            suffixes=suf_list,
                            breakdown=parts,
                            word_type="verb"
                        ))

            # ═══ 2) Çift çatı:  base + voice₁ + voice₂ + outer ═══
            for o_suf, o_lbl, o_code, o_fr in self._DERIVED_OUTER:
                if not base_w.endswith(o_suf):
                    continue
                rest1 = base_w[:-len(o_suf)]
                if len(rest1) < 5:
                    continue

                for v2s, v2l, v2c, _ in self._VOICE:
                    if not rest1.endswith(v2s):
                        continue
                    rest2 = rest1[:-len(v2s)]
                    if len(rest2) < 4:
                        continue

                    for v1s, v1l, v1c, _ in self._VOICE:
                        # Aynı çatı tipi: Edilgen+Edilgen izin ver (n+il gibi),
                        # diğerlerinde (ETT+ETT, İŞT+İŞT) atla
                        if v1l == v2l and v1l != "Edilgen":
                            continue
                        if not rest2.endswith(v1s):
                            continue
                        raw = rest2[:-len(v1s)]
                        if len(raw) < 2:
                            continue

                        for base in self._reverse_soften(raw):
                            if not self._is_verb(base):
                                continue
                            sig = f"dv2|{base}|{v1s}|{v2s}|{o_suf}|{copula}"
                            if sig in seen:
                                continue
                            seen.add(sig)

                            suf_list = [
                                {"suffix": v1s, "type": v1l, "code": v1c},
                                {"suffix": v2s, "type": v2l, "code": v2c},
                                {"suffix": o_suf, "type": o_lbl, "code": o_code},
                            ]
                            parts = (
                                f"{base.capitalize()} (Kök)"
                                f" + {v1s} ({v1l})"
                                f" + {v2s} ({v2l})"
                                f" + {o_suf} ({o_lbl})"
                            )
                            if copula:
                                suf_list.append({"suffix": copula, "type": "Bildiriş", "code": "-dIr"})
                                parts += f" + {copula} (Bildiriş)"

                            results.append(AnalysisResult(
                                success=True, original=word,
                                stem=base.capitalize(),
                                suffixes=suf_list,
                                breakdown=parts,
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

        # ── Sıra sayı tanıma: "2024-nji", "25-njy" ──
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

        # ── Yazılı sıra sayı tanıma: "ýedinji", "birinji", "ilkinji" vb. ──
        _CARDINAL_ORDINAL_MAP = {
            "bir": "birinji", "iki": "ikinji", "üç": "üçünji",
            "dört": "dördünji", "bäş": "bäşinji", "alty": "altynjy",
            "ýedi": "ýedinji", "sekiz": "sekizinji", "dokuz": "dokuzynjy",
            "on": "onunjy", "ýigrimi": "ýigriminji", "otuz": "otuzynjy",
            "kyrk": "kyrkynjy", "elli": "ellinji", "altmyş": "altmyşynjy",
            "ýetmiş": "ýetmişinji", "segsen": "segseninji", "togsan": "togsanynjy",
            "ýüz": "ýüzünji", "müň": "müňünji", "ilki": "ilkinji",
        }
        _ORDINAL_TO_CARDINAL = {v: k for k, v in _CARDINAL_ORDINAL_MAP.items()}
        if w_lower in _ORDINAL_TO_CARDINAL:
            cardinal = _ORDINAL_TO_CARDINAL[w_lower]
            suffix = w_lower[len(cardinal):]  # nji, njy, ünji etc.
            return MultiAnalysisResult(original=word, results=[AnalysisResult(
                success=True, original=word,
                stem=cardinal, suffixes=[{"suffix": "+OncI", "type": "Sıra sayı (yapım eki)", "code": "SıS"}],
                breakdown=f"{cardinal} + {suffix} (Sıra sayı sıfatı)",
                word_type="adjective"
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

        # Mastar (infinitive) olarak çözümle
        all_results.extend(self.parse_infinitive(word))

        # Türetilmiş fiil (ettirgen/edilgen + dış çekim)
        all_results.extend(self.parse_derived_verb(word))

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
