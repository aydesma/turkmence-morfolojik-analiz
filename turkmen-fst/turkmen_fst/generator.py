# -*- coding: utf-8 -*-
"""
TurkmenFST — Sentez (Üretim) Motoru (generator.py)

Kök + morfem dizisi → Çekimli kelime üretimi.

İsim çekimi: isim_cekimle() — 6 hal, iyelik, çoğul
Fiil çekimi: fiil_cekimle() — 7 zaman × 6 şahıs × olumlu/olumsuz

Bu modül, mevcut morphology.py'deki isim_cekimle ve fiil_cekimle
fonksiyonlarının state machine güdümlü yeniden yapılandırmasıdır.
v26.0 referans sonuçlarıyla %100 uyumlu olması zorunludur.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from turkmen_fst.phonology import PhonologyRules, VowelSystem, YUVARLAKLASMA_LISTESI, SOFTENING_TABLE
from turkmen_fst.morphotactics import (
    NounMorphotactics, VerbMorphotactics, MorphCategory
)
from turkmen_fst.lexicon import Lexicon, HOMONYMS

# Tek heceli fiillerde özel k/t→g/d yumuşaması yapan fiiller
TEK_HECELI_YUMUSAMA_FIIL = {"aýt", "gaýt", "et", "git"}


# ==============================================================================
#  SONUÇ VERİ YAPILARI
# ==============================================================================

@dataclass
class GenerationResult:
    """
    Sentez sonucu.
    
    Attributes:
        word: Çekimlenmiş kelime (ör. "kitabym")
        breakdown: Şecere (ör. "kitap + ym")
        stem: Orijinal kök
        morphemes: Uygulanan morfem listesi
        is_valid: Geçerli bir çekim mi
        error: Hata mesajı (varsa)
    """
    word: str = ""
    breakdown: str = ""
    stem: str = ""
    morphemes: list = field(default_factory=list)
    is_valid: bool = True
    error: str = ""

    @property
    def success(self) -> bool:
        return self.is_valid and not self.error


@dataclass
class NounResult(GenerationResult):
    """İsim çekim sonucu — ek parça detayları."""
    parts: list = field(default_factory=list)
    meaning: Optional[str] = None  # Eş sesli kelimeler için anlam


# ==============================================================================
#  İSİM ÇEKİM MOTORU
# ==============================================================================

class NounGenerator:
    """
    Türkmen Türkçesi isim çekim motoru.
    
    State machine (NounMorphotactics) üzerinden çalışır.
    Her adımda fonoloji kurallarını (PhonologyRules) uygular.
    
    Ek sırası: KÖK + [çokluk] + [iyelik] + [hal]
    """
    
    def __init__(self, lexicon: Optional[Lexicon] = None):
        self.lexicon = lexicon

    def generate(self, stem: str, plural: bool = False,
                 possessive: Optional[str] = None, poss_type: str = "tek",
                 case: Optional[str] = None,
                 yumusama_izni: bool = True) -> GenerationResult:
        """
        İsim çekimi yapar.
        
        Args:
            stem: Kök kelime (ör. "kitap")
            plural: Çoğul eki eklensin mi
            possessive: İyelik kodu: "A1", "A2", "A3" veya None
            poss_type: İyelik tipi: "tek" (tekil) veya "cog" (çoğul)
            case: Hal kodu: "A2"-"A6" veya None
            yumusama_izni: Ünsüz yumuşaması uygulanacak mı (eş sesliler için)
            
        Returns:
            GenerationResult
        """
        # --- State machine doğrulama ---
        valid, err = NounMorphotactics.validate_noun_params(plural, possessive, case)
        if not valid:
            return GenerationResult(
                stem=stem, is_valid=False, error=err
            )

        # --- Çekim mantığı (v26 uyumlu) ---
        govde = stem.lower()
        yol = [stem]

        # Berdi Hoca kuralı: Guzy/Süri/Guýy yuvarlaklaşması
        # Sadece Çokluk ve A3 kategorilerinde kök değişir.
        yuvarlaklasma_yapildi = False
        if govde in YUVARLAKLASMA_LISTESI and (plural or possessive == "A3"):
            govde = YUVARLAKLASMA_LISTESI[govde]
            yuvarlaklasma_yapildi = True

        nit_ilk = PhonologyRules.get_vowel_quality(govde)
        kok_yuvarlak = PhonologyRules.has_rounded_vowel(govde)
        morphemes = []

        # ================================================================
        # 1) ÇOKLUK EKİ (-lar / -ler)
        # ================================================================
        if plural:
            # Yuvarlaklaşma: son harf y/i ve kök yuvarlak ise u/ü'ye
            if not yuvarlaklasma_yapildi and kok_yuvarlak and govde[-1] in "yi":
                govde = govde[:-1] + ("u" if nit_ilk == "yogyn" else "ü")

            ek = "lar" if PhonologyRules.get_vowel_quality(govde) == "yogyn" else "ler"
            govde += ek
            yol.append(ek)
            morphemes.append(("PLURAL", ek))

        # ================================================================
        # 2) İYELİK EKLERİ
        # ================================================================
        if possessive:
            nit = PhonologyRules.get_vowel_quality(govde)
            is_unlu = PhonologyRules.ends_with_vowel(govde)
            kok_yuvarlak = PhonologyRules.has_rounded_vowel(govde)

            if possessive == "A1":
                if is_unlu:
                    ek = "m" if poss_type == "tek" else ("myz" if nit == "yogyn" else "miz")
                else:
                    taban = ("um" if nit == "yogyn" else "üm") if kok_yuvarlak else ("ym" if nit == "yogyn" else "im")
                    ek = taban if poss_type == "tek" else (taban + ("yz" if nit == "yogyn" else "iz"))

            elif possessive == "A2":
                if is_unlu:
                    ek = "ň" if poss_type == "tek" else ("ňyz" if nit == "yogyn" else "ňiz")
                else:
                    taban = ("uň" if nit == "yogyn" else "üň") if kok_yuvarlak else ("yň" if nit == "yogyn" else "iň")
                    ek = taban if poss_type == "tek" else (taban + ("yz" if nit == "yogyn" else "iz"))

            elif possessive == "A3":
                # 3. tekil iyelik — yuvarlaklaşma + su/sü veya sy/si
                yuvarlaklasti = False
                if not yuvarlaklasma_yapildi and kok_yuvarlak and govde[-1] in "yi":
                    govde = govde[:-1] + ("u" if nit == "yogyn" else "ü")
                    yuvarlaklasti = True
                if is_unlu:
                    if yuvarlaklasti or yuvarlaklasma_yapildi:
                        ek = "su" if nit == "yogyn" else "sü"
                    else:
                        ek = "sy" if nit == "yogyn" else "si"
                else:
                    if yuvarlaklasma_yapildi and kok_yuvarlak:
                        ek = "u" if nit == "yogyn" else "ü"
                    else:
                        ek = "y" if nit == "yogyn" else "i"

            # Düşme ve yumuşama
            govde = PhonologyRules.apply_vowel_drop(govde, ek)
            if yumusama_izni:
                govde = PhonologyRules.apply_consonant_softening(govde)
            govde += ek
            yol.append(ek)
            morphemes.append(("POSSESSIVE", ek))

        # ================================================================
        # 3) HAL EKLERİ
        # ================================================================
        if case:
            nit = PhonologyRules.get_vowel_quality(govde)
            is_unlu = PhonologyRules.ends_with_vowel(govde)
            kok_yuvarlak = PhonologyRules.has_rounded_vowel(govde)
            yol_eki = None

            # 3. iyelikten sonra n-kaynaştırma
            n_kay = possessive == "A3"

            # Orta Hece Yuvarlaklaşma
            if n_kay and kok_yuvarlak and govde[-1] in "yi":
                govde = govde[:-1] + ("u" if nit == "yogyn" else "ü")

            if case == "A2":  # İlgi hali
                if n_kay:
                    ek = "nyň"
                elif is_unlu:
                    ek = "nyň" if nit == "yogyn" else "niň"
                else:
                    if len(stem) <= 4 and kok_yuvarlak:
                        ek = "uň" if nit == "yogyn" else "üň"
                    else:
                        ek = "yň" if nit == "yogyn" else "iň"
                    govde = PhonologyRules.apply_vowel_drop(govde, ek)
                    if yumusama_izni:
                        govde = PhonologyRules.apply_consonant_softening(govde)

            elif case == "A3":  # Yönelme hali
                if n_kay:
                    ek = "na" if nit == "yogyn" else "ne"
                elif is_unlu:
                    son = govde[-1]
                    govde = govde[:-1]
                    degisen = "a" if son in "ay" else "ä"
                    govde += degisen
                    ek = ""
                    yol_eki = degisen
                else:
                    ek = "a" if nit == "yogyn" else "e"

            elif case == "A4":  # Belirtme hali
                if n_kay:
                    ek = "ny" if nit == "yogyn" else "ni"
                elif is_unlu:
                    ek = "ny" if nit == "yogyn" else "ni"
                else:
                    ek = "y" if nit == "yogyn" else "i"
                    if yumusama_izni:
                        govde = PhonologyRules.apply_consonant_softening(govde)

            elif case == "A5":  # Bulunma hali
                ek = "nda" if n_kay else ("da" if nit == "yogyn" else "de")

            elif case == "A6":  # Çıkma hali
                ek = "ndan" if n_kay else ("dan" if nit == "yogyn" else "den")

            govde += ek
            yol.append(yol_eki if yol_eki is not None else ek)
            morphemes.append(("CASE", yol_eki if yol_eki is not None else ek))

        return GenerationResult(
            word=govde,
            breakdown=" + ".join(yol),
            stem=stem,
            morphemes=morphemes,
            is_valid=True
        )


# ==============================================================================
#  FİİL ÇEKİM MOTORU
# ==============================================================================

class VerbGenerator:
    """
    Türkmen Türkçesi fiil çekim motoru.
    
    7 zaman × 6 şahıs × 2 (olumlu/olumsuz) çekim.
    State machine (VerbMorphotactics) üzerinden çalışır.
    """

    def __init__(self, lexicon: Optional[Lexicon] = None):
        self.lexicon = lexicon

    @staticmethod
    def _person_suffix_standard(quality: str, person: str) -> str:
        """Standart şahıs eki tablosu (Ö1, Ö2, Ö3 zamanları)."""
        table = {
            "A1": "m",
            "A2": "ň",
            "A3": "",
            "B1": "k",
            "B2": "ňyz" if quality == "yogyn" else "ňiz",
            "B3": "lar" if quality == "yogyn" else "ler"
        }
        return table[person]

    @staticmethod
    def _person_suffix_extended(quality: str, person: str) -> str:
        """Genişletilmiş şahıs eki tablosu (H1, G2 zamanları)."""
        table = {
            "A1": "yn" if quality == "yogyn" else "in",
            "A2": "syň" if quality == "yogyn" else "siň",
            "A3": "",
            "B1": "ys" if quality == "yogyn" else "is",
            "B2": "syňyz" if quality == "yogyn" else "siňiz",
            "B3": "lar" if quality == "yogyn" else "ler"
        }
        return table[person]

    @staticmethod
    def _tek_heceli_dodak(govde: str) -> bool:
        """Tek heceli ve dodak (ünlü) yuvarlak fiil mi kontrol eder."""
        unluler = [c for c in govde.lower() if c in VowelSystem.ALL]
        return len(unluler) == 1 and unluler[0] in VowelSystem.DODAK

    @staticmethod
    def _fiil_yumusama(govde: str) -> str:
        """Çok heceli veya özel tek heceli fiillerde k/t→g/d yumuşaması uygular."""
        if not govde or govde[-1] not in ('k', 't'):
            return govde
        unlu_sayisi = sum(1 for c in govde if c in VowelSystem.ALL)
        if unlu_sayisi > 1 or govde in TEK_HECELI_YUMUSAMA_FIIL:
            return govde[:-1] + SOFTENING_TABLE[govde[-1]]
        return govde

    def generate(self, stem: str, tense: str, person: str,
                 negative: bool = False) -> GenerationResult:
        """
        Fiil çekimi yapar.
        
        Args:
            stem: Fiil kökü (ör. "gel", "oka")
            tense: Zaman kodu ("1"-"7")
            person: Şahıs kodu ("A1"-"B3")
            negative: Olumsuz mu
            
        Returns:
            GenerationResult
        """
        govde = stem.lower()
        quality = PhonologyRules.get_vowel_quality(govde)
        ends_vowel = PhonologyRules.ends_with_vowel(govde)
        pronoun = VerbMorphotactics.PRONOUNS.get(person, "")
        morphemes = []

        # ================================================================
        # Mälim Geljek (6) — özel format
        # ================================================================
        if tense == "6":
            tense_suffix = "jak" if quality == "yogyn" else "jek"
            if negative:
                # Olumsuz: kök + jak/jek + däl
                result = govde + tense_suffix + " däl"
                breakdown = f"{pronoun} + {stem} + {tense_suffix} + däl"
                morphemes.append(("TENSE", tense_suffix))
                morphemes.append(("NEGATION", "däl"))
            else:
                # enedilim kuralı: kök + jak/jek + dir/dyr + kişi eki
                kopula_base = "dyr" if quality == "yogyn" else "dir"
                kopula_person = self._person_suffix_extended(quality, person)
                kopula_eki = kopula_base + kopula_person
                result = govde + tense_suffix + kopula_eki
                breakdown = f"{pronoun} + {stem} + {tense_suffix} + {kopula_eki}"
                morphemes.append(("TENSE", tense_suffix))
                morphemes.append(("COPULA", kopula_eki))
            return GenerationResult(
                word=f"{pronoun} {result}",
                breakdown=breakdown,
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        # ================================================================
        # Anyk Häzirki (5) — özel yardımcı fiiller
        # ================================================================
        if tense == "5":
            table = {
                "otyr":  {"A1": "yn",  "A2": "syň",  "A3": "", "B1": "ys",  "B2": "syňyz",  "B3": "lar"},
                "dur":   {"A1": "un",  "A2": "suň",  "A3": "", "B1": "us",  "B2": "suňyz",  "B3": "lar"},
                "ýatyr": {"A1": "yn",  "A2": "syň",  "A3": "", "B1": "ys",  "B2": "syňyz",  "B3": "lar"},
                "ýör":   {"A1": "ün",  "A2": "siň",  "A3": "", "B1": "üs",  "B2": "siňiz",  "B3": "ler"}
            }
            if govde not in table:
                return GenerationResult(
                    word=f"HATA: '{stem}' fiili Anyk Häzirki zamanda çekimlenemez",
                    breakdown="",
                    stem=stem,
                    is_valid=False,
                    error=f"'{stem}' fiili Anyk Häzirki zamanda çekimlenemez"
                )
            person_suffix = table[govde][person]
            morphemes.append(("PERSON", person_suffix))
            return GenerationResult(
                word=govde + person_suffix,
                breakdown=f"{stem} + {person_suffix if person_suffix else '(0)'}",
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        # ================================================================
        # Diğer zamanlar
        # ================================================================
        neg_suffix = ("ma" if quality == "yogyn" else "me") if negative else ""
        if neg_suffix:
            morphemes.append(("NEGATION", neg_suffix))

        if tense == "1":
            # Anyk Öten: kök + [ma] + dy/di + şahıs
            # Tek heceli dodak fiillerde: -dy/-di → -du/-dü (şahıs eki varken)
            if not negative and self._tek_heceli_dodak(govde) and person != "A3":
                tense_suffix = "du" if quality == "yogyn" else "dü"
            else:
                tense_suffix = "dy" if quality == "yogyn" else "di"
            person_suffix = self._person_suffix_standard(quality, person)

        elif tense == "2":
            # Daş Öten
            if negative:
                # enedilim kuralı: kök + män/man + di/dy + kişi
                neg_suffix = ""  # genel olumsuz eki kullanılmaz
                if morphemes and morphemes[-1][0] == "NEGATION":
                    morphemes.pop()
                tense_suffix = "mändi" if quality == "ince" else "mandy"
                person_suffix = self._person_suffix_standard(quality, person)
            else:
                # Olumlu: kök + ypdy/pdy + şahıs
                if ends_vowel:
                    tense_suffix = "pdy" if quality == "yogyn" else "pdi"
                else:
                    tense_suffix = "ypdy" if quality == "yogyn" else "ipdi"
                person_suffix = self._person_suffix_standard(quality, person)

        elif tense == "3":
            # Dowamly Öten
            if negative:
                # enedilim kuralı: kök + ýan/ýän + däldi + kişi (analitik yapı)
                neg_suffix = ""  # genel olumsuz eki kullanılmaz
                if morphemes and morphemes[-1][0] == "NEGATION":
                    morphemes.pop()
                sifat_fiil = "ýan" if quality == "yogyn" else "ýän"
                # däldi her zaman ince, kişi ekleri ince
                person_suffix_str = self._person_suffix_standard("ince", person)
                result = govde + sifat_fiil + " däldi" + person_suffix_str
                morphemes.append(("PARTICIPLE", sifat_fiil))
                morphemes.append(("NEG_COPULA", "däldi"))
                if person_suffix_str:
                    morphemes.append(("PERSON", person_suffix_str))
                breakdown = f"{stem} + {sifat_fiil} + däldi + {person_suffix_str if person_suffix_str else '(0)'}"
                return GenerationResult(
                    word=result,
                    breakdown=breakdown,
                    stem=stem,
                    morphemes=morphemes,
                    is_valid=True
                )
            else:
                # Olumlu: kök + ýardy/ýärdi + şahıs
                tense_suffix = "ýardy" if quality == "yogyn" else "ýärdi"
                person_suffix = self._person_suffix_standard(quality, person)

        elif tense == "4":
            # Umumy Häzirki: kök + [ma] + ýar/ýär + şahıs
            # k/t yumuşaması (sadece olumlu formda)
            if not negative:
                govde = self._fiil_yumusama(govde)
            tense_suffix = "ýar" if quality == "yogyn" else "ýär"
            person_suffix = self._person_suffix_extended(quality, person)

        elif tense == "7":
            # Nämälim Geljek
            if negative:
                # Olumsuzluk zaman ekine dahil: -mar/-mer (1./2. şahıs), -maz/-mez (3. şahıs)
                neg_suffix = ""  # Genel olumsuz eki kullanılmaz
                if morphemes and morphemes[-1][0] == "NEGATION":
                    morphemes.pop()
                if person in ("A3", "B3"):
                    tense_suffix = "maz" if quality == "yogyn" else "mez"
                else:
                    tense_suffix = "mar" if quality == "yogyn" else "mer"
            else:
                # k/t yumuşaması
                govde = self._fiil_yumusama(govde)
                # e→ä dönüşümü
                if govde and govde[-1] == 'e':
                    govde = govde[:-1] + 'ä'
                tense_suffix = "r" if ends_vowel else ("ar" if quality == "yogyn" else "er")
            person_suffix = self._person_suffix_extended(quality, person)

        elif tense == "8":
            # Şert formasy (Şart kipi): kök + [ma/me] + sa/se + kişi
            tense_suffix = "sa" if quality == "yogyn" else "se"
            person_suffix = self._person_suffix_standard(quality, person)

        elif tense == "9":
            # Buýruk formasy (Emir kipi) — her şahıs için farklı yapı
            if negative:
                neg_suf = "ma" if quality == "yogyn" else "me"
                if morphemes and morphemes[-1][0] == "NEGATION":
                    morphemes.pop()
                morphemes.append(("NEGATION", neg_suf))
                # -ma/-me sonrası dodak uyumu iptal
                if person == "A1":
                    p_suf = "ýyn" if quality == "yogyn" else "ýin"
                elif person == "A2":
                    p_suf = ""
                elif person == "A3":
                    p_suf = "syn" if quality == "yogyn" else "sin"
                elif person == "B1":
                    p_suf = "ly" if quality == "yogyn" else "li"
                elif person == "B2":
                    p_suf = "ň"
                else:  # B3
                    p_suf = "synlar" if quality == "yogyn" else "sinler"
                result = govde + neg_suf + p_suf
                if p_suf:
                    morphemes.append(("PERSON", p_suf))
                breakdown = f"{stem} + {neg_suf} + {p_suf if p_suf else '(0)'}"
            else:
                # Olumlu emir
                neg_suffix = ""
                if morphemes and morphemes[-1][0] == "NEGATION":
                    morphemes.pop()
                if person == "A1":
                    if ends_vowel:
                        p_suf = "ýyn" if quality == "yogyn" else "ýin"
                    else:
                        p_suf = "aýyn" if quality == "yogyn" else "eýin"
                elif person == "A2":
                    p_suf = ""
                elif person == "A3":
                    if self._tek_heceli_dodak(govde):
                        p_suf = "sun" if quality == "yogyn" else "sün"
                    else:
                        p_suf = "syn" if quality == "yogyn" else "sin"
                elif person == "B1":
                    if ends_vowel:
                        p_suf = "ly" if quality == "yogyn" else "li"
                    else:
                        p_suf = "aly" if quality == "yogyn" else "eli"
                elif person == "B2":
                    if ends_vowel:
                        p_suf = "ň"
                    else:
                        if self._tek_heceli_dodak(govde):
                            p_suf = "uň" if quality == "yogyn" else "üň"
                        else:
                            p_suf = "yň" if quality == "yogyn" else "iň"
                else:  # B3
                    if self._tek_heceli_dodak(govde):
                        p_suf = "sunlar" if quality == "yogyn" else "sünler"
                    else:
                        p_suf = "synlar" if quality == "yogyn" else "sinler"
                result = govde + p_suf
                if p_suf:
                    morphemes.append(("PERSON", p_suf))
                breakdown = f"{stem} + {p_suf if p_suf else '(0)'}"
            return GenerationResult(
                word=result,
                breakdown=breakdown,
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        elif tense == "10":
            # Hökmanlyk formasy (Gereklilik): kök + maly/meli [+ däl]
            if morphemes and morphemes[-1][0] == "NEGATION":
                morphemes.pop()
            neg_suffix = ""
            tense_suf = "maly" if quality == "yogyn" else "meli"
            morphemes.append(("TENSE", tense_suf))
            if negative:
                result = govde + tense_suf + " däl"
                morphemes.append(("NEGATION", "däl"))
                breakdown = f"{stem} + {tense_suf} + däl"
            else:
                result = govde + tense_suf
                breakdown = f"{stem} + {tense_suf}"
            return GenerationResult(
                word=result,
                breakdown=breakdown,
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        elif tense == "11":
            # Nätanyş Öten (Kanıtsal / Evidential)
            if negative:
                # kök + mandyr/mändir + kişi
                neg_suffix = ""
                if morphemes and morphemes[-1][0] == "NEGATION":
                    morphemes.pop()
                tense_suffix = "mandyr" if quality == "yogyn" else "mändir"
                person_suffix = self._person_suffix_extended(quality, person)
            else:
                # kök + ypdyr/ipdir + kişi
                if ends_vowel:
                    tense_suffix = "pdyr" if quality == "yogyn" else "pdir"
                else:
                    if self._tek_heceli_dodak(govde):
                        tense_suffix = "updyr" if quality == "yogyn" else "üpdir"
                    else:
                        tense_suffix = "ypdyr" if quality == "yogyn" else "ipdir"
                person_suffix = self._person_suffix_extended(quality, person)

        elif tense == "12":
            # Arzuw-Ökünç (Optative): kök + [ma/me] + sa/se + dy/di + kişi
            sart_eki = "sa" if quality == "yogyn" else "se"
            gecmis_eki = "dy" if quality == "yogyn" else "di"
            person_suffix = self._person_suffix_standard(quality, person)
            result = govde + neg_suffix + sart_eki + gecmis_eki + person_suffix
            morphemes.append(("CONDITIONAL", sart_eki))
            morphemes.append(("TENSE", gecmis_eki))
            if person_suffix:
                morphemes.append(("PERSON", person_suffix))
            bp = [stem]
            if neg_suffix:
                bp.append(neg_suffix)
            bp.extend([sart_eki, gecmis_eki, person_suffix if person_suffix else "(0)"])
            breakdown = " + ".join(bp)
            return GenerationResult(
                word=result,
                breakdown=breakdown,
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        elif tense == "13":
            # Hal işlik (converb): kök + yp/ip/up/üp/p (neg: man/män)
            if morphemes and morphemes[-1][0] == "NEGATION":
                morphemes.pop()
            neg_suffix = ""
            if negative:
                suffix = "man" if quality == "yogyn" else "män"
            else:
                if ends_vowel:
                    suffix = "p"
                elif self._tek_heceli_dodak(govde):
                    suffix = "up" if quality == "yogyn" else "üp"
                else:
                    suffix = "yp" if quality == "yogyn" else "ip"
            morphemes.append(("CONVERB", suffix))
            return GenerationResult(
                word=govde + suffix,
                breakdown=f"{stem} + {suffix}",
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        elif tense == "14":
            # Öten ortak işlik (past participle): kök + an/en (neg: madyk/medik)
            if morphemes and morphemes[-1][0] == "NEGATION":
                morphemes.pop()
            neg_suffix = ""
            if negative:
                suffix = "madyk" if quality == "yogyn" else "medik"
            else:
                if ends_vowel:
                    suffix = "n"
                else:
                    suffix = "an" if quality == "yogyn" else "en"
            morphemes.append(("PARTICIPLE", suffix))
            return GenerationResult(
                word=govde + suffix,
                breakdown=f"{stem} + {suffix}",
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        elif tense == "15":
            # Häzirki ortak işlik (present participle): kök + ýan/ýän (neg: maýan/meýän)
            if morphemes and morphemes[-1][0] == "NEGATION":
                morphemes.pop()
            neg_suffix = ""
            if negative:
                suffix = "maýan" if quality == "yogyn" else "meýän"
            else:
                suffix = "ýan" if quality == "yogyn" else "ýän"
            morphemes.append(("PARTICIPLE", suffix))
            return GenerationResult(
                word=govde + suffix,
                breakdown=f"{stem} + {suffix}",
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        elif tense == "16":
            # Geljek ortak işlik (future participle): kök + jak/jek (neg: majak/mejek)
            if morphemes and morphemes[-1][0] == "NEGATION":
                morphemes.pop()
            neg_suffix = ""
            if negative:
                suffix = "majak" if quality == "yogyn" else "mejek"
            else:
                suffix = "jak" if quality == "yogyn" else "jek"
            morphemes.append(("PARTICIPLE", suffix))
            return GenerationResult(
                word=govde + suffix,
                breakdown=f"{stem} + {suffix}",
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        elif tense == "17":
            # Ettirgen (causative): kök + dyr/dir/dur/dür veya +t
            if morphemes and morphemes[-1][0] == "NEGATION":
                morphemes.pop()
            neg_suffix = ""
            if ends_vowel:
                suffix = "t"
            elif self._tek_heceli_dodak(govde):
                suffix = "dur" if quality == "yogyn" else "dür"
            else:
                suffix = "dyr" if quality == "yogyn" else "dir"
            morphemes.append(("CAUSATIVE", suffix))
            return GenerationResult(
                word=govde + suffix,
                breakdown=f"{stem} + {suffix}",
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        elif tense == "18":
            # Edilgen (passive): kök + yl/il/ul/ül veya +yn/in/un/ün
            if morphemes and morphemes[-1][0] == "NEGATION":
                morphemes.pop()
            neg_suffix = ""
            if ends_vowel:
                suffix = "n" if (govde and len(govde) >= 2 and govde[-2] == 'l') else "l"
            elif govde and govde[-1] == 'l':
                if self._tek_heceli_dodak(govde):
                    suffix = "un" if quality == "yogyn" else "ün"
                else:
                    suffix = "yn" if quality == "yogyn" else "in"
            else:
                if self._tek_heceli_dodak(govde):
                    suffix = "ul" if quality == "yogyn" else "ül"
                else:
                    suffix = "yl" if quality == "yogyn" else "il"
            morphemes.append(("PASSIVE", suffix))
            return GenerationResult(
                word=govde + suffix,
                breakdown=f"{stem} + {suffix}",
                stem=stem,
                morphemes=morphemes,
                is_valid=True
            )

        else:
            return GenerationResult(
                word=f"HATA: Geçersiz zaman kodu '{tense}'",
                breakdown="",
                stem=stem,
                is_valid=False,
                error=f"Geçersiz zaman kodu: {tense}"
            )

        morphemes.append(("TENSE", tense_suffix))
        if person_suffix:
            morphemes.append(("PERSON", person_suffix))

        # Sonuç birleştirme
        result = govde + neg_suffix + tense_suffix + person_suffix
        breakdown_parts = [stem]
        if neg_suffix:
            breakdown_parts.append(neg_suffix)
        breakdown_parts.append(tense_suffix)
        breakdown_parts.append(person_suffix if person_suffix else "(0)")
        breakdown = " + ".join(breakdown_parts)

        return GenerationResult(
            word=result,
            breakdown=breakdown,
            stem=stem,
            morphemes=morphemes,
            is_valid=True
        )


# ==============================================================================
#  BİRLEŞİK SENTEZ MOTORU
# ==============================================================================

class MorphologicalGenerator:
    """
    Birleşik sentez motoru — isim ve fiil çekimini tek arayüzde sunar.
    
    Kullanım:
        gen = MorphologicalGenerator(lexicon)
        result = gen.generate_noun("kitap", plural=True, possessive="A1")
        result = gen.generate_verb("gel", tense="1", person="A1")
    """
    
    def __init__(self, lexicon: Optional[Lexicon] = None):
        self.lexicon = lexicon
        self.noun_gen = NounGenerator(lexicon)
        self.verb_gen = VerbGenerator(lexicon)

    def generate_noun(self, stem: str, plural: bool = False,
                      possessive: Optional[str] = None, poss_type: str = "tek",
                      case: Optional[str] = None,
                      yumusama_izni: bool = True) -> GenerationResult:
        "İsim çekimi yapar."""
        # B1/B2 kodlarını A1/A2 + çoğul tipine dönüştür
        if possessive in ("B1", "B2"):
            poss_type = "cog"
            possessive = "A1" if possessive == "B1" else "A2"
        return self.noun_gen.generate(stem, plural, possessive, poss_type, case, yumusama_izni)

    def generate_verb(self, stem: str, tense: str, person: str,
                      negative: bool = False) -> GenerationResult:
        """Fiil çekimi yapar."""
        return self.verb_gen.generate(stem, tense, person, negative)

    def analyze_noun(self, root: str, s_code: str, i_code: str, h_code: str):
        """
        Flask uyumlu isim çekimi API'si (mevcut analyze fonksiyonuyla uyumlu).
        
        Eş sesli kelimeler için çift sonuç döndürür.
        
        Returns:
            (results_list, is_dual)
        """
        cokluk = (s_code == "S2")

        # Web dropdown kodlarını motor kodlarına dönüştür
        IYELIK_DONUSUM = {"B1": "A1", "B2": "A2", "B3": "A3"}
        iyelik = IYELIK_DONUSUM.get(i_code, i_code) if i_code else None
        i_tip = "cog" if i_code in ["B1", "B2"] else "tek"

        # Hal kodu dönüşümü
        HAL_DONUSUM = {"H2": "A2", "H3": "A3", "H4": "A4", "H5": "A5", "H6": "A6"}
        hal = HAL_DONUSUM.get(h_code) if h_code and h_code != "H1" else None

        root_lower = root.lower()

        # İyelik görüntüleme etiketleri
        IYELIK_DISPLAY_MAP = {
            "A1": "D₁b", "A2": "D₂b", "A3": "D₃b",
            "B1": "D₁k", "B2": "D₂k", "B3": "D₃k"
        }

        def _build_parts(root_word, result_word, yol, s_code, i_code, h_code, cokluk, iyelik):
            """Çekim sonucunu parts listesine dönüştürür."""
            yol_parts = yol.split(" + ")
            parts = [{"text": root_word, "type": "Kök", "code": "Kök"}]
            
            idx = 1
            if cokluk and idx < len(yol_parts):
                parts.append({"text": yol_parts[idx], "type": "Sayı", "code": s_code})
                idx += 1
            if iyelik and idx < len(yol_parts):
                iyelik_eki = yol_parts[idx]
                parts.append({"text": iyelik_eki, "type": "Degislilik", "code": i_code})
                idx += 1
            if h_code and h_code != "H1" and idx < len(yol_parts):
                hal_eki = yol_parts[idx]
                display_code = h_code.replace('H', 'A')
                parts.append({"text": hal_eki, "type": "Hal", "code": display_code})
            
            for part in parts:
                if part.get("type") == "Degislilik" and part.get("code") in IYELIK_DISPLAY_MAP:
                    part["code"] = IYELIK_DISPLAY_MAP[part["code"]]
            
            return parts

        # Eş sesli kelime kontrolü
        if root_lower in HOMONYMS:
            results = []
            for key, (anlam, yumusama) in HOMONYMS[root_lower].items():
                gen_result = self.generate_noun(root, cokluk, iyelik, i_tip, hal,
                                                yumusama_izni=yumusama)
                parts = _build_parts(root, gen_result.word, gen_result.breakdown,
                                     s_code, i_code, h_code, cokluk, iyelik)
                results.append({
                    "parts": parts,
                    "final_word": gen_result.word,
                    "anlam": anlam
                })
            return results, True

        # Normal kelime
        gen_result = self.generate_noun(root, cokluk, iyelik, i_tip, hal)
        parts = _build_parts(root, gen_result.word, gen_result.breakdown,
                             s_code, i_code, h_code, cokluk, iyelik)
        return [{"parts": parts, "final_word": gen_result.word, "anlam": None}], False

    def analyze_verb(self, root: str, tense_code: str, person_code: str,
                     negative: bool = False):
        """
        Flask uyumlu fiil çekimi API'si (mevcut analyze_verb fonksiyonuyla uyumlu).
        
        Returns:
            (parts_list, final_word)
        """
        tense = VerbMorphotactics.TENSE_CODE_MAP.get(tense_code, "1")
        quality = PhonologyRules.get_vowel_quality(root)

        gen_result = self.generate_verb(root, tense, person_code, negative)

        if not gen_result.success:
            return [{"text": gen_result.word, "type": "Hata", "code": "HATA"}], ""

        parts = []
        
        # Şahıs zamiri
        parts.append({"text": VerbMorphotactics.PRONOUNS.get(person_code, ""),
                       "type": "Şahıs", "code": person_code})
        
        # Kök
        parts.append({"text": root, "type": "Kök", "code": "Kök"})

        ends_vowel = PhonologyRules.ends_with_vowel(root)

        if tense_code in ["Ö1", "Ö2", "Ö3"]:
            if tense_code == "Ö2" and negative:
                # enedilim: kök + män/man + di/dy + kişi
                zaman_eki = "mändi" if quality == "ince" else "mandy"
                parts.append({"text": zaman_eki, "type": "Olumsuz+Zaman", "code": tense_code})
                sahis_eki = self.verb_gen._person_suffix_standard(quality, person_code)
                if sahis_eki:
                    parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

            elif tense_code == "Ö3" and negative:
                # enedilim: kök + ýan/ýän + däldi + kişi (analitik)
                sifat_fiil = "ýan" if quality == "yogyn" else "ýän"
                parts.append({"text": sifat_fiil, "type": "Sıfat-fiil", "code": "SF"})
                sahis_eki_str = self.verb_gen._person_suffix_standard("ince", person_code)
                parts.append({"text": "däldi" + sahis_eki_str, "type": "Olumsuz+Kişi", "code": tense_code})

            else:
                # Ö1 (olumlu/olumsuz), Ö2 olumlu, Ö3 olumlu
                if negative:
                    neg_ek = "ma" if quality == "yogyn" else "me"
                    parts.append({"text": neg_ek, "type": "Olumsuzluk Eki", "code": "Olumsuz"})

                if tense_code == "Ö1":
                    zaman_eki = "dy" if quality == "yogyn" else "di"
                elif tense_code == "Ö2":
                    if ends_vowel:
                        zaman_eki = "pdy" if quality == "yogyn" else "pdi"
                    else:
                        zaman_eki = "ypdy" if quality == "yogyn" else "ipdi"
                else:  # Ö3 olumlu
                    zaman_eki = "ýardy" if quality == "yogyn" else "ýärdi"
                
                parts.append({"text": zaman_eki, "type": "Zaman", "code": tense_code})
                sahis_eki = self.verb_gen._person_suffix_standard(quality, person_code)
                if sahis_eki:
                    parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        elif tense_code == "H1":
            if negative:
                zaman_eki = "maýar" if quality == "yogyn" else "meýär"
            else:
                zaman_eki = "ýar" if quality == "yogyn" else "ýär"
            parts.append({"text": zaman_eki, "type": "Zaman", "code": tense_code})

            person_table = {
                "A1": "ym" if quality == "yogyn" else "im",
                "A2": "syň" if quality == "yogyn" else "siň",
                "A3": "",
                "B1": "yk" if quality == "yogyn" else "ik",
                "B2": "syňyz" if quality == "yogyn" else "siňiz",
                "B3": "lar" if quality == "yogyn" else "ler"
            }
            sahis_eki = person_table[person_code]
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        elif tense_code == "H2":
            person_table = {
                "A1": "yn", "A2": "syň", "A3": "",
                "B1": "ys", "B2": "syňyz", "B3": "lar"
            }
            sahis_eki = person_table.get(person_code, "")
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        elif tense_code == "G1":
            zaman_eki = "jak" if quality == "yogyn" else "jek"
            parts.append({"text": zaman_eki, "type": "Zaman", "code": tense_code})
            if negative:
                parts.append({"text": "däl", "type": "Olumsuzluk", "code": "Olumsuz"})
            else:
                # enedilim: kopula + kişi eki
                kopula_base = "dyr" if quality == "yogyn" else "dir"
                kopula_person = self.verb_gen._person_suffix_extended(quality, person_code)
                kopula_eki = kopula_base + kopula_person
                parts.append({"text": kopula_eki, "type": "Kopula", "code": person_code})

        elif tense_code == "G2":
            if negative:
                zaman_eki = "maz" if quality == "yogyn" else "mez"
            else:
                zaman_eki = "r" if ends_vowel else ("ar" if quality == "yogyn" else "er")
            parts.append({"text": zaman_eki, "type": "Zaman", "code": tense_code})

            sahis_eki = self.verb_gen._person_suffix_extended(quality, person_code)
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        elif tense_code == "Ş1":
            # Şert formasy
            if negative:
                olumsuz_ek = "ma" if quality == "yogyn" else "me"
                parts.append({"text": olumsuz_ek, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
            zaman_eki = "sa" if quality == "yogyn" else "se"
            parts.append({"text": zaman_eki, "type": "Zaman", "code": tense_code})
            sahis_eki = self.verb_gen._person_suffix_standard(quality, person_code)
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        elif tense_code == "B1K":
            # Buýruk formasy
            if negative:
                olumsuz_ek = "ma" if quality == "yogyn" else "me"
                parts.append({"text": olumsuz_ek, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
                if person_code == "A1":
                    sahis_eki = "ýyn" if quality == "yogyn" else "ýin"
                elif person_code == "A2":
                    sahis_eki = ""
                elif person_code == "A3":
                    sahis_eki = "syn" if quality == "yogyn" else "sin"
                elif person_code == "B1":
                    sahis_eki = "ly" if quality == "yogyn" else "li"
                elif person_code == "B2":
                    sahis_eki = "ň"
                else:  # B3
                    sahis_eki = "synlar" if quality == "yogyn" else "sinler"
            else:
                if person_code == "A1":
                    if ends_vowel:
                        sahis_eki = "ýyn" if quality == "yogyn" else "ýin"
                    else:
                        sahis_eki = "aýyn" if quality == "yogyn" else "eýin"
                elif person_code == "A2":
                    sahis_eki = ""
                elif person_code == "A3":
                    if self.verb_gen._tek_heceli_dodak(root.lower()):
                        sahis_eki = "sun" if quality == "yogyn" else "sün"
                    else:
                        sahis_eki = "syn" if quality == "yogyn" else "sin"
                elif person_code == "B1":
                    if ends_vowel:
                        sahis_eki = "ly" if quality == "yogyn" else "li"
                    else:
                        sahis_eki = "aly" if quality == "yogyn" else "eli"
                elif person_code == "B2":
                    if ends_vowel:
                        sahis_eki = "ň"
                    else:
                        if self.verb_gen._tek_heceli_dodak(root.lower()):
                            sahis_eki = "uň" if quality == "yogyn" else "üň"
                        else:
                            sahis_eki = "yň" if quality == "yogyn" else "iň"
                else:  # B3
                    if self.verb_gen._tek_heceli_dodak(root.lower()):
                        sahis_eki = "sunlar" if quality == "yogyn" else "sünler"
                    else:
                        sahis_eki = "synlar" if quality == "yogyn" else "sinler"
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        elif tense_code == "HK":
            # Hökmanlyk formasy
            zaman_eki = "maly" if quality == "yogyn" else "meli"
            parts.append({"text": zaman_eki, "type": "Zaman", "code": tense_code})
            if negative:
                parts.append({"text": "däl", "type": "Olumsuzluk", "code": "Olumsuz"})

        elif tense_code == "NÖ":
            # Nätanyş Öten (Kanıtsal / Evidential)
            if negative:
                zaman_eki = "mandyr" if quality == "yogyn" else "mändir"
                parts.append({"text": zaman_eki, "type": "Olumsuz+Zaman", "code": tense_code})
            else:
                if ends_vowel:
                    zaman_eki = "pdyr" if quality == "yogyn" else "pdir"
                else:
                    if self.verb_gen._tek_heceli_dodak(root.lower()):
                        zaman_eki = "updyr" if quality == "yogyn" else "üpdir"
                    else:
                        zaman_eki = "ypdyr" if quality == "yogyn" else "ipdir"
                parts.append({"text": zaman_eki, "type": "Zaman", "code": tense_code})
            sahis_eki = self.verb_gen._person_suffix_extended(quality, person_code)
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        elif tense_code == "AÖ":
            # Arzuw-Ökünç (Optative)
            if negative:
                olumsuz_ek = "ma" if quality == "yogyn" else "me"
                parts.append({"text": olumsuz_ek, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
            sart_eki = "sa" if quality == "yogyn" else "se"
            gecmis_eki = "dy" if quality == "yogyn" else "di"
            parts.append({"text": sart_eki, "type": "Şart", "code": "Ş"})
            parts.append({"text": gecmis_eki, "type": "Zaman", "code": tense_code})
            sahis_eki = self.verb_gen._person_suffix_standard(quality, person_code)
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        elif tense_code in ("FH", "FÖ", "FÄ", "FG"):
            # Fiilimsi formları (şahıs eki yok)
            parts = [p for p in parts if p.get("type") != "Şahıs"]
            govde = root.lower()
            ek = gen_result.word[len(govde):]
            if ek:
                fiilimsi_tipi = {
                    "FH": "Hal işlik", "FÖ": "Öten ortak",
                    "FÄ": "Häzirki ortak", "FG": "Geljek ortak"
                }
                parts.append({"text": ek, "type": fiilimsi_tipi[tense_code], "code": tense_code})

        elif tense_code in ("ETT", "EDL"):
            # Ettirgen/Edilgen (şahıs eki yok, derivasyon)
            parts = [p for p in parts if p.get("type") != "Şahıs"]
            govde = root.lower()
            ek = gen_result.word[len(govde):]
            if ek:
                tip = "Ettirgen" if tense_code == "ETT" else "Edilgen"
                parts.append({"text": ek, "type": tip, "code": tense_code})

        return parts, gen_result.word
