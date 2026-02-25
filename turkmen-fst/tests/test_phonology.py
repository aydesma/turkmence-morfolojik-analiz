# -*- coding: utf-8 -*-
"""
TurkmenFST — Fonoloji Birim Testleri

Test kapsamı:
  - Ünlü niteligi (kalın/ince)
  - Yuvarlak ünlü kontrolü
  - Ünsüz yumuşaması (p→b, t→d, ç→j, k→g)
  - Ünsüz sertleşmesi (ters yön)
  - Ünlü düşmesi (burun→burn, asyl→asl)
  - Yuvarlaklaşma uyumu
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from turkmen_fst.phonology import PhonologyRules, VowelSystem, VOWEL_DROP_CANDIDATES, VOWEL_DROP_EXCEPTIONS


class TestVowelSystem:
    """Ünlü sistemi testleri."""

    def test_yogyn_vowels(self):
        assert "a" in VowelSystem.YOGYN
        assert "o" in VowelSystem.YOGYN
        assert "u" in VowelSystem.YOGYN
        assert "y" in VowelSystem.YOGYN
        assert "e" not in VowelSystem.YOGYN

    def test_ince_vowels(self):
        assert "e" in VowelSystem.INCE
        assert "ä" in VowelSystem.INCE
        assert "ö" in VowelSystem.INCE
        assert "i" in VowelSystem.INCE
        assert "ü" in VowelSystem.INCE
        assert "a" not in VowelSystem.INCE

    def test_rounded_vowels(self):
        assert "o" in VowelSystem.DODAK
        assert "ö" in VowelSystem.DODAK
        assert "u" in VowelSystem.DODAK
        assert "ü" in VowelSystem.DODAK
        assert "a" not in VowelSystem.DODAK

    def test_all_vowels_union(self):
        assert VowelSystem.ALL == VowelSystem.YOGYN | VowelSystem.INCE


class TestVowelQuality:
    """Ünlü niteliği testi — kalın/ince ayrımı."""

    def test_yogyn_words(self):
        assert PhonologyRules.get_vowel_quality("kitap") == "yogyn"
        assert PhonologyRules.get_vowel_quality("okuw") == "yogyn"
        assert PhonologyRules.get_vowel_quality("yol") == "yogyn"
        assert PhonologyRules.get_vowel_quality("gurt") == "yogyn"

    def test_ince_words(self):
        assert PhonologyRules.get_vowel_quality("gelin") == "ince"
        assert PhonologyRules.get_vowel_quality("deňiz") == "ince"
        assert PhonologyRules.get_vowel_quality("mekdep") == "ince"
        assert PhonologyRules.get_vowel_quality("köwüş") == "ince"

    def test_no_vowel_default(self):
        """Ünlüsüz kelime → varsayılan yogyn."""
        assert PhonologyRules.get_vowel_quality("brn") == "yogyn"

    def test_empty_string(self):
        assert PhonologyRules.get_vowel_quality("") == "yogyn"


class TestRoundedVowel:
    """Yuvarlak ünlü kontrolü."""

    def test_rounded(self):
        assert PhonologyRules.has_rounded_vowel("ogul") is True
        assert PhonologyRules.has_rounded_vowel("kömür") is True
        assert PhonologyRules.has_rounded_vowel("boýun") is True

    def test_not_rounded(self):
        assert PhonologyRules.has_rounded_vowel("kitap") is False
        assert PhonologyRules.has_rounded_vowel("gelin") is False
        assert PhonologyRules.has_rounded_vowel("bagyr") is False


class TestConsonantSoftening:
    """Ünsüz yumuşaması testi — p→b, ç→j, t→d, k→g."""

    def test_p_to_b(self):
        assert PhonologyRules.apply_consonant_softening("kitap") == "kitab"

    def test_t_to_d(self):
        assert PhonologyRules.apply_consonant_softening("at") == "ad"

    def test_c_to_j(self):
        assert PhonologyRules.apply_consonant_softening("agaç") == "agaj"

    def test_k_to_g(self):
        assert PhonologyRules.apply_consonant_softening("ýürek") == "ýüreg"

    def test_no_softening(self):
        """Yumuşama gerektirmeyen son harf."""
        assert PhonologyRules.apply_consonant_softening("gelin") == "gelin"
        assert PhonologyRules.apply_consonant_softening("okuw") == "okuw"

    def test_empty(self):
        assert PhonologyRules.apply_consonant_softening("") == ""


class TestReverseSoftening:
    """Ters yön: b→p, d→t, j→ç, g→k."""

    def test_b_to_p(self):
        assert PhonologyRules.reverse_consonant_softening("kitab") == "kitap"

    def test_d_to_t(self):
        assert PhonologyRules.reverse_consonant_softening("ad") == "at"

    def test_j_to_c(self):
        assert PhonologyRules.reverse_consonant_softening("agaj") == "agaç"

    def test_g_to_k(self):
        assert PhonologyRules.reverse_consonant_softening("ýüreg") == "ýürek"


class TestVowelDrop:
    """Ünlü düşmesi testi — burun→burn, asyl→asl."""

    def test_general_candidates(self):
        """Genel aday listesinden düşme."""
        assert PhonologyRules.apply_vowel_drop("burun", "um") == "burn"
        assert PhonologyRules.apply_vowel_drop("agyz", "y") == "agz"
        assert PhonologyRules.apply_vowel_drop("ogul", "y") == "ogl"
        assert PhonologyRules.apply_vowel_drop("garyn", "y") == "garn"

    def test_exception_drops(self):
        """İstisna tablosundan düşme."""
        assert PhonologyRules.apply_vowel_drop("asyl", "y") == "asl"
        assert PhonologyRules.apply_vowel_drop("nesil", "i") == "nesl"
        assert PhonologyRules.apply_vowel_drop("ylym", "y") == "ylm"

    def test_no_drop_consonant_suffix(self):
        """Ek ünlüyle başlamıyorsa düşme olmaz."""
        assert PhonologyRules.apply_vowel_drop("burun", "lar") == "burun"
        assert PhonologyRules.apply_vowel_drop("asyl", "da") == "asyl"

    def test_non_candidate(self):
        """Düşme adayı olmayan kelime."""
        assert PhonologyRules.apply_vowel_drop("kitap", "y") == "kitap"


class TestReverseVowelDrop:
    """Ünlü düşmesini geri alma testi."""

    def test_reverse_general(self):
        assert PhonologyRules.reverse_vowel_drop("burn") == "burun"
        assert PhonologyRules.reverse_vowel_drop("agz") == "agyz"

    def test_reverse_exception(self):
        assert PhonologyRules.reverse_vowel_drop("asl") == "asyl"
        assert PhonologyRules.reverse_vowel_drop("nesl") == "nesil"

    def test_no_match(self):
        assert PhonologyRules.reverse_vowel_drop("kitap") is None


class TestRoundingHarmony:
    """Yuvarlaklaşma uyumu testi."""

    def test_y_to_u(self):
        """Kalın yuvarlak kökler: y→u."""
        assert PhonologyRules.apply_rounding_harmony("goýy", "yogyn") == "goýu"

    def test_i_to_u_umlaut(self):
        """İnce yuvarlak kökler: i→ü."""
        assert PhonologyRules.apply_rounding_harmony("köwüşi", "ince") == "köwüşü"

    def test_no_change_flat(self):
        """Düz (yuvarlak olmayan) köklerde değişiklik yok."""
        assert PhonologyRules.apply_rounding_harmony("gelini", "ince") == "gelini"

    def test_empty(self):
        assert PhonologyRules.apply_rounding_harmony("", "yogyn") == ""


class TestEndsWithVowel:
    """Son harf ünlü mü testi."""

    def test_vowel_ending(self):
        assert PhonologyRules.ends_with_vowel("ata") is True
        assert PhonologyRules.ends_with_vowel("ene") is True

    def test_consonant_ending(self):
        assert PhonologyRules.ends_with_vowel("kitap") is False
        assert PhonologyRules.ends_with_vowel("gelin") is False

    def test_empty(self):
        assert PhonologyRules.ends_with_vowel("") is False


class TestPreSuffixPipeline:
    """Bileşik ses kuralı pipeline testi."""

    def test_drop_and_soften(self):
        """burun + ym → burn (düşme) → burn (yumuşama yok) → burnym."""
        result = PhonologyRules.apply_pre_suffix_rules("burun", "ym")
        assert result == "burn"

    def test_soften_only(self):
        """kitap + ym → kitab (yumuşama)."""
        result = PhonologyRules.apply_pre_suffix_rules("kitap", "ym",
                                                        apply_drop=True,
                                                        apply_softening=True)
        assert result == "kitab"
