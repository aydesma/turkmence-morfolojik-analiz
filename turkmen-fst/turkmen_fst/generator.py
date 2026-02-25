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
            # B3 çoğul eki (olumlu formda)
            plural_suffix = ""
            if person == "B3" and not negative:
                plural_suffix = "lar" if quality == "yogyn" else "ler"
            result = govde + tense_suffix + plural_suffix + (" däl" if negative else "")
            breakdown = f"{pronoun} + {stem} + {tense_suffix}" + (f" + {plural_suffix}" if plural_suffix else "") + (" + däl" if negative else "")
            morphemes.append(("TENSE", tense_suffix))
            if plural_suffix:
                morphemes.append(("PLURAL", plural_suffix))
            if negative:
                morphemes.append(("NEGATION", "däl"))
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
            # Daş Öten: kök + [ma] + ypdy/pdy + şahıs
            if ends_vowel:
                tense_suffix = "pdy" if quality == "yogyn" else "pdi"
            else:
                tense_suffix = "ypdy" if quality == "yogyn" else "ipdi"
            person_suffix = self._person_suffix_standard(quality, person)

        elif tense == "3":
            # Dowamly Öten: kök + [ma] + ýardy/ýärdi + şahıs
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
            else:
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

        elif tense_code == "G2":
            if negative:
                zaman_eki = "maz" if quality == "yogyn" else "mez"
            else:
                zaman_eki = "r" if ends_vowel else ("ar" if quality == "yogyn" else "er")
            parts.append({"text": zaman_eki, "type": "Zaman", "code": tense_code})

            sahis_eki = self.verb_gen._person_suffix_extended(quality, person_code)
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": person_code})

        return parts, gen_result.word
