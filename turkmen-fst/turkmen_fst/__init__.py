# -*- coding: utf-8 -*-
"""
TurkmenFST — Türkmen Türkçesi Morfolojik Analiz Sistemi

Zemberek NLP benzeri, modüler bir morfolojik analiz ve sentez motoru.

Modüller:
    - phonology: Ses kuralları (ünlü uyumu, ünsüz yumuşaması, ünlü düşmesi)
    - lexicon: Sözlük modülü (kelime kökü + POS etiketleri + morfolojik özellikler)
    - morphotactics: Ek sırası kuralları (FST-inspired state machine)
    - generator: Sentez (üretim) motoru
    - analyzer: Tahlil (analiz) motoru
"""

__version__ = "1.0.0"
__author__ = "TurkmenFST Project"

from turkmen_fst.phonology import PhonologyRules, VowelSystem
from turkmen_fst.lexicon import Lexicon, LexiconEntry
from turkmen_fst.morphotactics import NounMorphotactics, VerbMorphotactics
from turkmen_fst.generator import MorphologicalGenerator, GenerationResult
from turkmen_fst.analyzer import MorphologicalAnalyzer, AnalysisResult
