# -*- coding: utf-8 -*-
"""
TurkmenFST — Morfotaktik State Machine Testleri

Test kapsamı:
  - Geçerli geçiş dizileri (STEM→PLURAL→POSSESSIVE→CASE ✅)
  - Geçersiz geçişler (CASE→PLURAL ❌)
  - Tüm state'lerin final durumu kontrolü
  - İsim ve fiil parametreleri doğrulama
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from turkmen_fst.morphotactics import (
    NounMorphotactics, VerbMorphotactics,
    MorphCategory, State, StateType
)


class TestNounStates:
    """İsim state'leri kontrol."""

    def test_all_states_defined(self):
        assert "STEM" in NounMorphotactics.STATES
        assert "PLURAL" in NounMorphotactics.STATES
        assert "POSSESSIVE" in NounMorphotactics.STATES
        assert "CASE" in NounMorphotactics.STATES

    def test_all_states_final(self):
        """İsim state machine'deki tüm durumlar final (yalın, çoğul, iyelikli hepsi geçerli çıkış)."""
        for name, state in NounMorphotactics.STATES.items():
            assert state.is_final is True, f"{name} durumu final olmalı"


class TestNounTransitions:
    """İsim geçiş dizileri testi."""

    def test_stem_only(self):
        """Yalın hal — sadece kök."""
        assert NounMorphotactics.is_valid_sequence([]) is True

    def test_stem_plural(self):
        """Kök + çoğul."""
        assert NounMorphotactics.is_valid_sequence([MorphCategory.PLURAL.value]) is True

    def test_stem_possessive(self):
        """Kök + iyelik."""
        assert NounMorphotactics.is_valid_sequence([MorphCategory.POSS_1SG.value]) is True

    def test_stem_case(self):
        """Kök + hal."""
        assert NounMorphotactics.is_valid_sequence([MorphCategory.CASE_DAT.value]) is True

    def test_stem_plural_possessive(self):
        """Kök + çoğul + iyelik."""
        seq = [MorphCategory.PLURAL.value, MorphCategory.POSS_1SG.value]
        assert NounMorphotactics.is_valid_sequence(seq) is True

    def test_stem_plural_case(self):
        """Kök + çoğul + hal."""
        seq = [MorphCategory.PLURAL.value, MorphCategory.CASE_ABL.value]
        assert NounMorphotactics.is_valid_sequence(seq) is True

    def test_stem_possessive_case(self):
        """Kök + iyelik + hal."""
        seq = [MorphCategory.POSS_3SG.value, MorphCategory.CASE_GEN.value]
        assert NounMorphotactics.is_valid_sequence(seq) is True

    def test_full_chain(self):
        """Kök + çoğul + iyelik + hal (tam zincir)."""
        seq = [MorphCategory.PLURAL.value, MorphCategory.POSS_2PL.value, MorphCategory.CASE_LOC.value]
        assert NounMorphotactics.is_valid_sequence(seq) is True

    def test_invalid_case_then_plural(self):
        """CASE → PLURAL ❌ geçersiz."""
        seq = [MorphCategory.CASE_DAT.value, MorphCategory.PLURAL.value]
        assert NounMorphotactics.is_valid_sequence(seq) is False

    def test_invalid_possessive_then_plural(self):
        """POSSESSIVE → PLURAL ❌ geçersiz."""
        seq = [MorphCategory.POSS_1SG.value, MorphCategory.PLURAL.value]
        assert NounMorphotactics.is_valid_sequence(seq) is False

    def test_invalid_case_then_possessive(self):
        """CASE → POSSESSIVE ❌ geçersiz."""
        seq = [MorphCategory.CASE_GEN.value, MorphCategory.POSS_3SG.value]
        assert NounMorphotactics.is_valid_sequence(seq) is False

    def test_invalid_double_plural(self):
        """PLURAL → PLURAL ❌ geçersiz."""
        seq = [MorphCategory.PLURAL.value, MorphCategory.PLURAL.value]
        assert NounMorphotactics.is_valid_sequence(seq) is False


class TestNounParamValidation:
    """İsim parametreleri doğrulama testi."""

    def test_valid_basic(self):
        valid, msg = NounMorphotactics.validate_noun_params(False, None, None)
        assert valid is True

    def test_valid_full(self):
        valid, msg = NounMorphotactics.validate_noun_params(True, "A1", "A6")
        assert valid is True

    def test_invalid_possessive(self):
        valid, msg = NounMorphotactics.validate_noun_params(False, "X9", None)
        assert valid is False
        assert "Geçersiz iyelik" in msg

    def test_invalid_case(self):
        valid, msg = NounMorphotactics.validate_noun_params(False, None, "A9")
        assert valid is False
        assert "Geçersiz hal" in msg


class TestVerbStates:
    """Fiil state'leri kontrol."""

    def test_all_states_defined(self):
        assert "V_STEM" in VerbMorphotactics.STATES
        assert "NEGATION" in VerbMorphotactics.STATES
        assert "TENSE" in VerbMorphotactics.STATES
        assert "PERSON" in VerbMorphotactics.STATES

    def test_stem_not_final(self):
        """Fiil kökü tek başına geçerli bir çıkış değil."""
        assert VerbMorphotactics.STATES["V_STEM"].is_final is False

    def test_negation_not_final(self):
        """Olumsuzluk eki tek başına geçerli değil."""
        assert VerbMorphotactics.STATES["NEGATION"].is_final is False

    def test_tense_final(self):
        """Zaman eki final (3. tekil şahıs)."""
        assert VerbMorphotactics.STATES["TENSE"].is_final is True

    def test_person_final(self):
        assert VerbMorphotactics.STATES["PERSON"].is_final is True


class TestVerbTransitions:
    """Fiil geçiş dizileri testi."""

    def test_stem_tense_person(self):
        """Kök → Zaman → Şahıs."""
        seq = [MorphCategory.TENSE_PAST1.value, MorphCategory.PERSON_1SG.value]
        assert VerbMorphotactics.is_valid_sequence(seq) is True

    def test_stem_neg_tense_person(self):
        """Kök → Olumsuz → Zaman → Şahıs."""
        seq = [MorphCategory.NEGATION.value, MorphCategory.TENSE_PRES1.value, MorphCategory.PERSON_2SG.value]
        assert VerbMorphotactics.is_valid_sequence(seq) is True

    def test_stem_tense_only(self):
        """Kök → Zaman (3. tekil — boş ek)."""
        seq = [MorphCategory.TENSE_FUT1.value]
        assert VerbMorphotactics.is_valid_sequence(seq) is True

    def test_invalid_person_without_tense(self):
        """Kök → Şahıs (zaman olmadan) ❌."""
        seq = [MorphCategory.PERSON_1SG.value]
        assert VerbMorphotactics.is_valid_sequence(seq) is False

    def test_invalid_tense_then_tense(self):
        """Zaman → Zaman ❌."""
        seq = [MorphCategory.TENSE_PAST1.value, MorphCategory.TENSE_FUT1.value]
        assert VerbMorphotactics.is_valid_sequence(seq) is False

    def test_invalid_neg_only(self):
        """Sadece olumsuzluk (final değil) ❌."""
        seq = [MorphCategory.NEGATION.value]
        assert VerbMorphotactics.is_valid_sequence(seq) is False


class TestVerbParamValidation:
    """Fiil parametreleri doğrulama testi."""

    def test_valid_basic(self):
        valid, msg = VerbMorphotactics.validate_verb_params("1", "A1", False)
        assert valid is True

    def test_valid_negative(self):
        valid, msg = VerbMorphotactics.validate_verb_params("4", "B3", True)
        assert valid is True

    def test_invalid_tense(self):
        valid, msg = VerbMorphotactics.validate_verb_params("9", "A1", False)
        assert valid is False

    def test_invalid_person(self):
        valid, msg = VerbMorphotactics.validate_verb_params("1", "X9", False)
        assert valid is False
