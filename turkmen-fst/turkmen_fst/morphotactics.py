# -*- coding: utf-8 -*-
"""
TurkmenFST — Morfotaktik Model (morphotactics.py)

FST-inspired state machine: Ek sırası kurallarını formal bir model olarak tanımlar.

İsim çekim sırası:  KÖK → [ÇOĞUL] → [İYELİK] → [HAL]
Fiil çekim sırası:  KÖK → [OLUMSUZ] → ZAMAN → [ŞAHIS]

"The system is based on a rule-driven morphotactic model
inspired by finite-state morphology (Beesley & Karttunen, 2003)."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable


# ==============================================================================
#  DURUM (STATE) TANIMLARI
# ==============================================================================

class StateType(Enum):
    """State machine durum türleri."""
    NOUN_STEM   = auto()
    PLURAL      = auto()
    POSSESSIVE  = auto()
    CASE        = auto()
    VERB_STEM   = auto()
    NEGATION    = auto()
    TENSE       = auto()
    PERSON      = auto()


@dataclass
class State:
    """
    FST durumu.
    
    Attributes:
        name: Durum adı (ör. "STEM", "PLURAL")
        state_type: Durum türü enum'ı
        is_final: Bu durumda durulabilir mi? (geçerli çıkış noktası)
    """
    name: str
    state_type: StateType
    is_final: bool = True

    def __repr__(self) -> str:
        return f"State({self.name}, final={self.is_final})"


# ==============================================================================
#  GEÇİŞ (TRANSITION) TANIMLARI
# ==============================================================================

@dataclass
class Transition:
    """
    Durum geçişi.
    
    Attributes:
        source: Kaynak durum adı
        target: Hedef durum adı  
        category: Morfolojik kategori (ör. "PLURAL", "POSS_1SG", "CASE_DAT")
        description: Açıklama
    """
    source: str
    target: str
    category: str
    description: str = ""

    def __repr__(self) -> str:
        return f"Transition({self.source}→{self.target}, {self.category})"


# ==============================================================================
#  MORFOLOJİK KATEGORİLER
# ==============================================================================

class MorphCategory(Enum):
    """Morfolojik kategori sabitleri."""
    # İsim kategorileri
    PLURAL       = "PLURAL"        # Çoğul: -lar/-ler
    POSS_1SG     = "POSS_1SG"      # 1. tekil iyelik: -ym/-im/-um/-üm/-m
    POSS_2SG     = "POSS_2SG"      # 2. tekil iyelik: -yň/-iň/-uň/-üň/-ň
    POSS_3SG     = "POSS_3SG"      # 3. tekil iyelik: -y/-i/-sy/-si
    POSS_1PL     = "POSS_1PL"      # 1. çoğul iyelik: -ymyz/-imiz/-umyz/-ümiz
    POSS_2PL     = "POSS_2PL"      # 2. çoğul iyelik: -yňyz/-iňiz/-uňyz/-üňiz
    CASE_GEN     = "CASE_GEN"      # İlgi hali: -yň/-iň/-nyň/-niň
    CASE_DAT     = "CASE_DAT"      # Yönelme hali: -a/-e/-na/-ne
    CASE_ACC     = "CASE_ACC"      # Belirtme hali: -y/-i/-ny/-ni
    CASE_LOC     = "CASE_LOC"      # Bulunma hali: -da/-de/-nda/-nde
    CASE_ABL     = "CASE_ABL"      # Çıkma hali: -dan/-den/-ndan/-nden
    
    # Fiil kategorileri
    NEGATION     = "NEGATION"      # Olumsuzluk: -ma/-me
    TENSE_PAST1  = "TENSE_PAST1"   # Anyk Öten (1): -dy/-di
    TENSE_PAST2  = "TENSE_PAST2"   # Daş Öten (2): -ypdy/-ipdi
    TENSE_PAST3  = "TENSE_PAST3"   # Dowamly Öten (3): -ýardy/-ýärdi
    TENSE_PRES1  = "TENSE_PRES1"   # Umumy Häzirki (4): -ýar/-ýär
    TENSE_PRES2  = "TENSE_PRES2"   # Anyk Häzirki (5): özel
    TENSE_FUT1   = "TENSE_FUT1"    # Mälim Geljek (6): -jak/-jek
    TENSE_FUT2   = "TENSE_FUT2"    # Nämälim Geljek (7): -ar/-er/-r
    PERSON_1SG   = "PERSON_1SG"    # 1. tekil şahıs
    PERSON_2SG   = "PERSON_2SG"    # 2. tekil şahıs
    PERSON_3SG   = "PERSON_3SG"    # 3. tekil şahıs
    PERSON_1PL   = "PERSON_1PL"    # 1. çoğul şahıs
    PERSON_2PL   = "PERSON_2PL"    # 2. çoğul şahıs
    PERSON_3PL   = "PERSON_3PL"    # 3. çoğul şahıs


# ==============================================================================
#  İSİM MORFOTAKTİK MODELİ
# ==============================================================================

class NounMorphotactics:
    """
    İsim çekim state machine.
    
    Geçerli sıra: STEM → [PLURAL] → [POSSESSIVE] → [CASE]
    
    Durumlar:
        STEM       — Kök (final: ✅ yalın hal)
        PLURAL     — Çoğul ekinden sonra (final: ✅)
        POSSESSIVE — İyelik ekinden sonra (final: ✅)
        CASE       — Hal ekinden sonra (final: ✅)
    
    Geçersiz diziler (reject):
        CASE → PLURAL ❌
        CASE → POSSESSIVE ❌
        POSSESSIVE → PLURAL ❌
    """

    STATES = {
        "STEM":       State("STEM",       StateType.NOUN_STEM,  is_final=True),
        "PLURAL":     State("PLURAL",     StateType.PLURAL,     is_final=True),
        "POSSESSIVE": State("POSSESSIVE", StateType.POSSESSIVE, is_final=True),
        "CASE":       State("CASE",       StateType.CASE,       is_final=True),
    }

    TRANSITIONS = [
        # STEM → ...
        Transition("STEM", "PLURAL",     MorphCategory.PLURAL.value,   "Kök → Çoğul"),
        Transition("STEM", "POSSESSIVE", MorphCategory.POSS_1SG.value, "Kök → 1.tekil iyelik"),
        Transition("STEM", "POSSESSIVE", MorphCategory.POSS_2SG.value, "Kök → 2.tekil iyelik"),
        Transition("STEM", "POSSESSIVE", MorphCategory.POSS_3SG.value, "Kök → 3.tekil iyelik"),
        Transition("STEM", "POSSESSIVE", MorphCategory.POSS_1PL.value, "Kök → 1.çoğul iyelik"),
        Transition("STEM", "POSSESSIVE", MorphCategory.POSS_2PL.value, "Kök → 2.çoğul iyelik"),
        Transition("STEM", "CASE",       MorphCategory.CASE_GEN.value, "Kök → İlgi hali"),
        Transition("STEM", "CASE",       MorphCategory.CASE_DAT.value, "Kök → Yönelme hali"),
        Transition("STEM", "CASE",       MorphCategory.CASE_ACC.value, "Kök → Belirtme hali"),
        Transition("STEM", "CASE",       MorphCategory.CASE_LOC.value, "Kök → Bulunma hali"),
        Transition("STEM", "CASE",       MorphCategory.CASE_ABL.value, "Kök → Çıkma hali"),

        # PLURAL → ...
        Transition("PLURAL", "POSSESSIVE", MorphCategory.POSS_1SG.value, "Çoğul → 1.tekil iyelik"),
        Transition("PLURAL", "POSSESSIVE", MorphCategory.POSS_2SG.value, "Çoğul → 2.tekil iyelik"),
        Transition("PLURAL", "POSSESSIVE", MorphCategory.POSS_3SG.value, "Çoğul → 3.tekil iyelik"),
        Transition("PLURAL", "POSSESSIVE", MorphCategory.POSS_1PL.value, "Çoğul → 1.çoğul iyelik"),
        Transition("PLURAL", "POSSESSIVE", MorphCategory.POSS_2PL.value, "Çoğul → 2.çoğul iyelik"),
        Transition("PLURAL", "CASE",       MorphCategory.CASE_GEN.value, "Çoğul → İlgi hali"),
        Transition("PLURAL", "CASE",       MorphCategory.CASE_DAT.value, "Çoğul → Yönelme hali"),
        Transition("PLURAL", "CASE",       MorphCategory.CASE_ACC.value, "Çoğul → Belirtme hali"),
        Transition("PLURAL", "CASE",       MorphCategory.CASE_LOC.value, "Çoğul → Bulunma hali"),
        Transition("PLURAL", "CASE",       MorphCategory.CASE_ABL.value, "Çoğul → Çıkma hali"),

        # POSSESSIVE → ...
        Transition("POSSESSIVE", "CASE", MorphCategory.CASE_GEN.value, "İyelik → İlgi hali"),
        Transition("POSSESSIVE", "CASE", MorphCategory.CASE_DAT.value, "İyelik → Yönelme hali"),
        Transition("POSSESSIVE", "CASE", MorphCategory.CASE_ACC.value, "İyelik → Belirtme hali"),
        Transition("POSSESSIVE", "CASE", MorphCategory.CASE_LOC.value, "İyelik → Bulunma hali"),
        Transition("POSSESSIVE", "CASE", MorphCategory.CASE_ABL.value, "İyelik → Çıkma hali"),
    ]

    @classmethod
    def get_transitions_from(cls, state_name: str) -> list[Transition]:
        """Belirli bir durumdan çıkan tüm geçişleri döndürür."""
        return [t for t in cls.TRANSITIONS if t.source == state_name]

    @classmethod
    def get_transition(cls, source: str, category: str) -> Optional[Transition]:
        """Belirli bir kaynak ve kategori için geçişi döndürür."""
        for t in cls.TRANSITIONS:
            if t.source == source and t.category == category:
                return t
        return None

    @classmethod
    def is_valid_sequence(cls, categories: list[str]) -> bool:
        """
        Verilen morfolojik kategori dizisinin geçerli olup olmadığını kontrol eder.
        
        Args:
            categories: ["PLURAL", "POSS_1SG", "CASE_GEN"] gibi bir dizi
        
        Returns:
            True ise geçerli bir geçiş dizisi
        """
        current = "STEM"
        for cat in categories:
            transition = cls.get_transition(current, cat)
            if transition is None:
                return False
            current = transition.target
        
        # Son durumun final olup olmadığını kontrol et
        state = cls.STATES.get(current)
        return state is not None and state.is_final

    @classmethod
    def validate_noun_params(cls, plural: bool, possessive: Optional[str],
                              case: Optional[str]) -> tuple[bool, str]:
        """
        İsim çekim parametrelerinin geçerliliğini doğrular.
        
        Returns:
            (is_valid, error_message)
        """
        categories = []
        
        if plural:
            categories.append(MorphCategory.PLURAL.value)
        
        if possessive:
            poss_map = {
                "A1": MorphCategory.POSS_1SG.value,
                "A2": MorphCategory.POSS_2SG.value,
                "A3": MorphCategory.POSS_3SG.value,
                "B1": MorphCategory.POSS_1PL.value,  # → A1 çoğul
                "B2": MorphCategory.POSS_2PL.value,  # → A2 çoğul
            }
            cat = poss_map.get(possessive)
            if cat is None:
                return False, f"Geçersiz iyelik kodu: {possessive}"
            categories.append(cat)
        
        if case:
            case_map = {
                "A2": MorphCategory.CASE_GEN.value,
                "A3": MorphCategory.CASE_DAT.value,
                "A4": MorphCategory.CASE_ACC.value,
                "A5": MorphCategory.CASE_LOC.value,
                "A6": MorphCategory.CASE_ABL.value,
            }
            cat = case_map.get(case)
            if cat is None:
                return False, f"Geçersiz hal kodu: {case}"
            categories.append(cat)
        
        if not cls.is_valid_sequence(categories):
            return False, f"Geçersiz ek sırası: {categories}"
        
        return True, ""


# ==============================================================================
#  FİİL MORFOTAKTİK MODELİ
# ==============================================================================

class VerbMorphotactics:
    """
    Fiil çekim state machine.
    
    Geçerli sıra: V_STEM → [NEGATION] → TENSE → [PERSON]
    
    Durumlar:
        V_STEM   — Fiil kökü (final: ❌)
        NEGATION — Olumsuzluk ekinden sonra (final: ❌)
        TENSE    — Zaman ekinden sonra (final: ✅, 3.tekil)
        PERSON   — Şahıs ekinden sonra (final: ✅)
    """

    STATES = {
        "V_STEM":   State("V_STEM",   StateType.VERB_STEM, is_final=False),
        "NEGATION": State("NEGATION", StateType.NEGATION,  is_final=False),
        "TENSE":    State("TENSE",    StateType.TENSE,     is_final=True),   # 3. tekil şahıs final
        "PERSON":   State("PERSON",   StateType.PERSON,    is_final=True),
    }

    TRANSITIONS = [
        # V_STEM → ...
        Transition("V_STEM", "NEGATION", MorphCategory.NEGATION.value,    "Kök → Olumsuz"),
        Transition("V_STEM", "TENSE",    MorphCategory.TENSE_PAST1.value, "Kök → Anyk Öten"),
        Transition("V_STEM", "TENSE",    MorphCategory.TENSE_PAST2.value, "Kök → Daş Öten"),
        Transition("V_STEM", "TENSE",    MorphCategory.TENSE_PAST3.value, "Kök → Dowamly Öten"),
        Transition("V_STEM", "TENSE",    MorphCategory.TENSE_PRES1.value, "Kök → Umumy Häzirki"),
        Transition("V_STEM", "TENSE",    MorphCategory.TENSE_PRES2.value, "Kök → Anyk Häzirki"),
        Transition("V_STEM", "TENSE",    MorphCategory.TENSE_FUT1.value,  "Kök → Mälim Geljek"),
        Transition("V_STEM", "TENSE",    MorphCategory.TENSE_FUT2.value,  "Kök → Nämälim Geljek"),

        # NEGATION → TENSE
        Transition("NEGATION", "TENSE", MorphCategory.TENSE_PAST1.value, "Olumsuz → Anyk Öten"),
        Transition("NEGATION", "TENSE", MorphCategory.TENSE_PAST2.value, "Olumsuz → Daş Öten"),
        Transition("NEGATION", "TENSE", MorphCategory.TENSE_PAST3.value, "Olumsuz → Dowamly Öten"),
        Transition("NEGATION", "TENSE", MorphCategory.TENSE_PRES1.value, "Olumsuz → Umumy Häzirki"),
        Transition("NEGATION", "TENSE", MorphCategory.TENSE_PRES2.value, "Olumsuz → Anyk Häzirki"),
        Transition("NEGATION", "TENSE", MorphCategory.TENSE_FUT1.value,  "Olumsuz → Mälim Geljek"),
        Transition("NEGATION", "TENSE", MorphCategory.TENSE_FUT2.value,  "Olumsuz → Nämälim Geljek"),

        # TENSE → PERSON
        Transition("TENSE", "PERSON", MorphCategory.PERSON_1SG.value, "Zaman → 1.tekil"),
        Transition("TENSE", "PERSON", MorphCategory.PERSON_2SG.value, "Zaman → 2.tekil"),
        Transition("TENSE", "PERSON", MorphCategory.PERSON_3SG.value, "Zaman → 3.tekil"),
        Transition("TENSE", "PERSON", MorphCategory.PERSON_1PL.value, "Zaman → 1.çoğul"),
        Transition("TENSE", "PERSON", MorphCategory.PERSON_2PL.value, "Zaman → 2.çoğul"),
        Transition("TENSE", "PERSON", MorphCategory.PERSON_3PL.value, "Zaman → 3.çoğul"),
    ]

    # Şahıs zamirleri
    PRONOUNS = {
        "A1": "Men",  "A2": "Sen",  "A3": "Ol",
        "B1": "Biz",  "B2": "Siz",  "B3": "Olar"
    }

    # Zaman kodu dönüşümü (web dropdown → motor)
    TENSE_CODE_MAP = {
        "Ö1": "1", "Ö2": "2", "Ö3": "3",
        "H1": "4", "H2": "5",
        "G1": "6", "G2": "7",
        "Ş1": "8", "B1K": "9", "HK": "10",
        "NÖ": "11", "AÖ": "12",
        "FH": "13", "FÖ": "14", "FÄ": "15", "FG": "16",
        "ETT": "17", "EDL": "18"
    }

    # Zaman görüntüleme isimleri
    TENSE_DISPLAY = {
        "1": "Anyk Öten",       # Geçmiş zaman (kesin)
        "2": "Daş Öten",        # Geçmiş zaman (dolaylı)
        "3": "Dowamly Öten",    # Geçmiş zaman (sürekli)
        "4": "Umumy Häzirki",   # Geniş zaman
        "5": "Anyk Häzirki",    # Şimdiki zaman (kesin)
        "6": "Mälim Geljek",    # Gelecek zaman (kesin)
        "7": "Nämälim Geljek",  # Gelecek zaman (belirsiz)
        "8": "Şert formasy",     # Şart kipi
        "9": "Buýruk formasy",   # Emir kipi
        "10": "Hökmanlyk formasy", # Gereklilik kipi
        "11": "Nätanyş Öten",   # Kanıtsal / Evidential
        "12": "Arzuw-Ökünç",     # Optative / dileksi
        "13": "Hal işlik",        # Converb (-yp/-ip/-up/-üp/-p)
        "14": "Öten ortak işlik", # Past participle (-an/-en)
        "15": "Häzirki ortak",    # Present participle (-ýan/-ýän)
        "16": "Geljek ortak",     # Future participle (-jak/-jek)
        "17": "Ettirgen",         # Causative (voice derivation)
        "18": "Edilgen",          # Passive (voice derivation)
    }

    @classmethod
    def get_transitions_from(cls, state_name: str) -> list[Transition]:
        """Belirli bir durumdan çıkan tüm geçişleri döndürür."""
        return [t for t in cls.TRANSITIONS if t.source == state_name]

    @classmethod
    def get_transition(cls, source: str, category: str) -> Optional[Transition]:
        """Belirli bir kaynak ve kategori için geçişi döndürür."""
        for t in cls.TRANSITIONS:
            if t.source == source and t.category == category:
                return t
        return None

    @classmethod
    def is_valid_sequence(cls, categories: list[str]) -> bool:
        """Verilen kategori dizisinin geçerli olup olmadığını kontrol eder."""
        current = "V_STEM"
        for cat in categories:
            transition = cls.get_transition(current, cat)
            if transition is None:
                return False
            current = transition.target
        
        state = cls.STATES.get(current)
        return state is not None and state.is_final

    @classmethod    
    def validate_verb_params(cls, tense: str, person: str,
                              negative: bool = False) -> tuple[bool, str]:
        """
        Fiil çekim parametrelerinin geçerliliğini doğrular.
        
        Returns:
            (is_valid, error_message)
        """
        categories = []
        
        if negative:
            categories.append(MorphCategory.NEGATION.value)
        
        tense_map = {
            "1": MorphCategory.TENSE_PAST1.value,
            "2": MorphCategory.TENSE_PAST2.value,
            "3": MorphCategory.TENSE_PAST3.value,
            "4": MorphCategory.TENSE_PRES1.value,
            "5": MorphCategory.TENSE_PRES2.value,
            "6": MorphCategory.TENSE_FUT1.value,
            "7": MorphCategory.TENSE_FUT2.value,
        }
        
        tense_cat = tense_map.get(tense)
        if tense_cat is None:
            return False, f"Geçersiz zaman kodu: {tense}"
        categories.append(tense_cat)
        
        person_map = {
            "A1": MorphCategory.PERSON_1SG.value,
            "A2": MorphCategory.PERSON_2SG.value,
            "A3": MorphCategory.PERSON_3SG.value,
            "B1": MorphCategory.PERSON_1PL.value,
            "B2": MorphCategory.PERSON_2PL.value,
            "B3": MorphCategory.PERSON_3PL.value,
        }
        
        person_cat = person_map.get(person)
        if person_cat is None:
            return False, f"Geçersiz şahıs kodu: {person}"
        
        # A3 (3.tekil) boş ek alır ama yine de geçerli bir geçiş
        categories.append(person_cat)
        
        return cls.is_valid_sequence(categories), ""
