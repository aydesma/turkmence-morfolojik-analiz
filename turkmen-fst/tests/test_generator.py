# -*- coding: utf-8 -*-
"""
TurkmenFST — v26 Referans Doğrulama Testi

Bu test, mevcut morphology.py (v26.0) tarafından üretilen 4788 isim çekim
sonucunu yeni TurkmenFST motoruyla karşılaştırır.

Her test vakası:
  kelime   — kök kelime (ör. "kitap")
  cokluk   — çoğul eki var mı (bool)
  iyelik   — iyelik kodu (None, "A1", "A2", "A3")
  i_tip    — iyelik tipi ("tek" veya "cog")
  hal      — hal kodu (None, "A2"-"A6")
  sonuc    — beklenen çıktı (BÜYÜK HARF)
  secere   — beklenen şecere (kök + ek + ek)

Başarı kriteri: %100 eşleşme (0 hata toleransı).
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from turkmen_fst.generator import NounGenerator
from turkmen_fst.lexicon import Lexicon


# ==============================================================================
#  Veri yükleme
# ==============================================================================

REFERENCE_PATH = os.path.join(os.path.dirname(__file__), "v26_reference.json")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

@pytest.fixture(scope="module")
def reference_data():
    """v26 referans verilerini yükle."""
    with open(REFERENCE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def generator():
    """Sözlük yüklü NounGenerator oluştur."""
    lexicon = Lexicon()
    dict_path = os.path.join(DATA_DIR, "turkmence_sozluk.txt")
    if os.path.exists(dict_path):
        lexicon.load(dict_path)
    return NounGenerator(lexicon)


# ==============================================================================
#  Toplu doğrulama (tek büyük test — hata raporu detaylı)
# ==============================================================================

class TestV26ReferenceValidation:
    """v26 referans sonuçlarıyla %100 uyumluluk testi."""

    def test_all_noun_inflections(self, generator, reference_data):
        """
        Tüm 4788 isim çekimini doğrula.
        
        Başarısız olanları detaylı raporla.
        """
        failures = []
        total = len(reference_data)

        for i, case in enumerate(reference_data):
            kelime = case["kelime"]
            cokluk = case["cokluk"]
            iyelik = case.get("iyelik")
            i_tip = case.get("i_tip", "tek")
            hal = case.get("hal")
            expected_word = case["sonuc"]
            expected_breakdown = case["secere"]

            result = generator.generate(
                stem=kelime,
                plural=cokluk,
                possessive=iyelik,
                poss_type=i_tip,
                case=hal
            )

            actual_word = result.word.upper()
            actual_breakdown = result.breakdown

            if actual_word != expected_word:
                failures.append({
                    "index": i,
                    "kelime": kelime,
                    "params": f"cokluk={cokluk}, iyelik={iyelik}, i_tip={i_tip}, hal={hal}",
                    "expected": expected_word,
                    "got": actual_word,
                    "expected_breakdown": expected_breakdown,
                    "got_breakdown": actual_breakdown,
                })

        # Sonuç raporu
        pass_count = total - len(failures)
        pass_rate = (pass_count / total) * 100 if total > 0 else 0

        if failures:
            # İlk 50 hatayı göster
            report_lines = [
                f"\n{'='*72}",
                f"  v26 REFERANS DOĞRULAMA RAPORU",
                f"  Toplam: {total} | Başarılı: {pass_count} | Başarısız: {len(failures)}",
                f"  Başarı oranı: {pass_rate:.1f}%",
                f"{'='*72}",
            ]
            for f in failures[:50]:
                report_lines.append(
                    f"  [{f['index']:4d}] {f['kelime']:12s} | "
                    f"{f['params']:50s} | "
                    f"Beklenen: {f['expected']:20s} | "
                    f"Üretilen: {f['got']:20s}"
                )
            if len(failures) > 50:
                report_lines.append(f"  ... ve {len(failures) - 50} hata daha")

            pytest.fail("\n".join(report_lines))

    def test_pass_rate_above_threshold(self, generator, reference_data):
        """Minimum %95 başarı oranı (geliştirme sürecinde geçici hedef)."""
        total = len(reference_data)
        pass_count = 0

        for case in reference_data:
            result = generator.generate(
                stem=case["kelime"],
                plural=case["cokluk"],
                possessive=case.get("iyelik"),
                poss_type=case.get("i_tip", "tek"),
                case=case.get("hal"),
            )
            if result.word.upper() == case["sonuc"]:
                pass_count += 1

        pass_rate = (pass_count / total) * 100 if total > 0 else 0
        assert pass_rate >= 95.0, f"Başarı oranı {pass_rate:.1f}% — minimum %95 gerekli"


# ==============================================================================
#  Kelime bazlı detaylı testler (kritik kelimeler)
# ==============================================================================

class TestCriticalWords:
    """En çok hata çıkabilecek morfolojik olayları test eder."""

    def test_kitap_softening(self, generator):
        """kitap → kitab+ym (p→b yumuşama)."""
        r = generator.generate("kitap", possessive="A1")
        assert r.word == "kitabym", f"Expected 'kitabym', got '{r.word}'"

    def test_kitap_genitive(self, generator):
        """kitap → kitabyň (ilgi hali)."""
        r = generator.generate("kitap", case="A2")
        assert r.word == "kitabyň", f"Expected 'kitabyň', got '{r.word}'"

    def test_burun_vowel_drop(self, generator):
        """burun → burny (ünlü düşmesi + 3. iyelik)."""
        r = generator.generate("burun", possessive="A3")
        assert r.word == "burny", f"Expected 'burny', got '{r.word}'"

    def test_agyz_vowel_drop(self, generator):
        """agyz → agzy (ünlü düşmesi)."""
        r = generator.generate("agyz", possessive="A3")
        assert r.word == "agzy", f"Expected 'agzy', got '{r.word}'"

    def test_gol_rounding(self, generator):
        """göl → göl+ler (ince sesli uyumu)."""
        r = generator.generate("göl", plural=True)
        assert r.word == "göller", f"Expected 'göller', got '{r.word}'"

    def test_alma_dative(self, generator):
        """alma → alma (ünlüyle biten + yönelme)."""
        r = generator.generate("alma", case="A3")
        # alma → almä veya alma → alma (ünlü değişimi)
        assert r.word.upper() in ["ALMA", "ALMÄ", "ALMA"], f"Unexpected: '{r.word}'"

    def test_at_plural_possessive_case(self, generator):
        """at → atlarynyň (çoğul + 3. iyelik + ilgi hali)."""
        r = generator.generate("at", plural=True, possessive="A3", case="A2")
        assert r.word.upper() == "ATLARYNYŇ", f"Expected 'ATLARYNYŇ', got '{r.word.upper()}'"

    def test_adam_basic(self, generator):
        """adam → adam (yalın)."""
        r = generator.generate("adam")
        assert r.word == "adam"

    def test_adam_plural(self, generator):
        """adam → adamlar (çoğul)."""
        r = generator.generate("adam", plural=True)
        assert r.word == "adamlar"


# ==============================================================================
#  Şecere (breakdown) testleri
# ==============================================================================

class TestBreakdown:
    """Şecere (kök + ek) formatı doğrulama."""

    def test_basic_stem(self, generator):
        r = generator.generate("kitap")
        assert r.breakdown == "kitap", f"Expected 'kitap', got '{r.breakdown}'"

    def test_plural_breakdown(self, generator):
        r = generator.generate("kitap", plural=True)
        assert "lar" in r.breakdown

    def test_possessive_breakdown(self, generator):
        r = generator.generate("kitap", possessive="A1")
        assert "ym" in r.breakdown or "im" in r.breakdown

    def test_case_breakdown(self, generator):
        r = generator.generate("kitap", case="A2")
        assert "yň" in r.breakdown or "iň" in r.breakdown
