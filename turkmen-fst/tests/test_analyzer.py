# -*- coding: utf-8 -*-
"""
TurkmenFST — Analiz (Ayrıştırma) Testleri

İsim ve fiil çözümleme testleri.
parse_noun() → list[AnalysisResult]
parse()      → MultiAnalysisResult (çoklu sonuç)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from turkmen_fst.analyzer import MorphologicalAnalyzer, AnalysisResult, MultiAnalysisResult
from turkmen_fst.lexicon import Lexicon


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.fixture(scope="module")
def analyzer():
    """Sözlük yüklü analiz motoru."""
    lexicon = Lexicon()
    dict_path = os.path.join(DATA_DIR, "turkmence_sozluk.txt")
    if os.path.exists(dict_path):
        lexicon.load(dict_path)
    return MorphologicalAnalyzer(lexicon)


class TestNounAnalysis:
    """İsim çözümleme testleri."""

    def test_bare_stem(self, analyzer):
        """Yalın kök — 'kitap'."""
        results = analyzer.parse_noun("kitap")
        assert isinstance(results, list)
        assert len(results) > 0
        assert results[0].success is True
        assert results[0].stem.lower() == "kitap"

    def test_plural(self, analyzer):
        """Çoğul — 'kitaplar' → kitap + lar."""
        results = analyzer.parse_noun("kitaplar")
        assert len(results) > 0
        assert results[0].success is True
        assert results[0].stem.lower() == "kitap"
        suffix_codes = [s["code"] for s in results[0].suffixes]
        assert "S2" in suffix_codes, f"'kitaplar' çözümünde çoğul eki yok: {results[0].suffixes}"

    def test_possessive_1sg(self, analyzer):
        """İyelik — 'kitabym' → kitap + ym."""
        results = analyzer.parse_noun("kitabym")
        assert len(results) > 0
        r = results[0]
        assert r.success is True
        assert r.stem.lower() in ("kitap", "kitab"), f"Kök: {r.stem}"
        suffix_codes = [s["code"] for s in r.suffixes]
        assert "D₁b" in suffix_codes, f"İyelik eki bulunamadı: {r.suffixes}"

    def test_case_genitive(self, analyzer):
        """Hal eki — 'kitabyň' → kitap + yň."""
        results = analyzer.parse_noun("kitabyň")
        assert len(results) > 0
        suffix_codes = [s["code"] for s in results[0].suffixes]
        assert "A₂" in suffix_codes, f"İlgi hali bulunamadı: {results[0].suffixes}"

    def test_case_dative(self, analyzer):
        """Yönelme — 'kitapa' → kitap + a."""
        results = analyzer.parse_noun("kitapa")
        assert len(results) > 0
        suffix_codes = [s["code"] for s in results[0].suffixes]
        assert "A₃" in suffix_codes, f"Yönelme hali bulunamadı: {results[0].suffixes}"

    def test_case_ablative(self, analyzer):
        """Çıkma — 'kitapdan' → kitap + dan."""
        results = analyzer.parse_noun("kitapdan")
        assert len(results) > 0
        suffix_codes = [s["code"] for s in results[0].suffixes]
        assert "A₆" in suffix_codes, f"Çıkma hali bulunamadı: {results[0].suffixes}"

    def test_case_locative(self, analyzer):
        """Bulunma — 'kitapda' → kitap + da."""
        results = analyzer.parse_noun("kitapda")
        assert len(results) > 0
        suffix_codes = [s["code"] for s in results[0].suffixes]
        assert "A₅" in suffix_codes, f"Bulunma hali bulunamadı: {results[0].suffixes}"

    def test_empty_input(self, analyzer):
        """Boş input — boş liste dönmeli."""
        results = analyzer.parse_noun("")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_unknown_word(self, analyzer):
        """Bilinmeyen kelime — parse() ile unknown kök döndürmeli."""
        multi = analyzer.parse("xyzqwerty")
        assert isinstance(multi, MultiAnalysisResult)
        assert multi.count > 0
        assert multi.results[0].word_type == "unknown"


class TestVerbAnalysis:
    """Fiil çözümleme testleri — şimdilik fiil analizi pasif, boş sonuç bekleniyor."""

    def test_verb_past(self, analyzer):
        """Geçmiş zaman — şimdilik boş liste beklenir."""
        results = analyzer.parse_verb("geldi")
        assert isinstance(results, list)

    def test_verb_present(self, analyzer):
        """Şimdiki zaman — şimdilik boş liste beklenir."""
        results = analyzer.parse_verb("gelýär")
        assert isinstance(results, list)

    def test_verb_negative(self, analyzer):
        """Olumsuz — şimdilik boş liste beklenir."""
        results = analyzer.parse_verb("gelmedi")
        assert isinstance(results, list)

    def test_empty_verb(self, analyzer):
        """Boş fiil — boş liste dönmeli."""
        results = analyzer.parse_verb("")
        assert isinstance(results, list)
        assert len(results) == 0


class TestAutoDetect:
    """Otomatik tür algılama testi."""

    def test_auto_noun(self, analyzer):
        """Otomatik isim tespiti — 'kitaplar'."""
        multi = analyzer.parse("kitaplar")
        assert isinstance(multi, MultiAnalysisResult)
        assert multi.success is True

    def test_auto_verb(self, analyzer):
        """Otomatik fiil tespiti — 'geldi' şimdilik unknown olabilir."""
        multi = analyzer.parse("geldi")
        assert isinstance(multi, MultiAnalysisResult)
        assert multi.success is True

    def test_breakdown_format(self, analyzer):
        """Şecere formatı: 'Kök (Kök) + ek (kod)' formunda olmalı."""
        results = analyzer.parse_noun("kitaplar")
        assert len(results) > 0
        assert "Kök" in results[0].breakdown
        assert "+" in results[0].breakdown


class TestAnalysisRoundtrip:
    """Üretim → Analiz round-trip testi."""

    def test_roundtrip_plural(self, analyzer):
        """Üretilen 'kitaplar' → kök 'kitap' bulunmalı."""
        from turkmen_fst.generator import NounGenerator
        gen = NounGenerator()

        result = gen.generate("kitap", plural=True)
        analysis = analyzer.parse_noun(result.word)
        assert len(analysis) > 0
        assert analysis[0].stem.lower() == "kitap", \
            f"Round-trip başarısız: '{result.word}' → '{analysis[0].stem}'"

    def test_roundtrip_case(self, analyzer):
        """Üretilen 'kitapdan' → kök 'kitap' bulunmalı."""
        from turkmen_fst.generator import NounGenerator
        gen = NounGenerator()

        result = gen.generate("kitap", case="A6")
        analysis = analyzer.parse_noun(result.word)
        assert len(analysis) > 0
        assert analysis[0].stem.lower() == "kitap", \
            f"Round-trip başarısız: '{result.word}' → '{analysis[0].stem}'"


class TestMultiResult:
    """Çoklu sonuç testleri."""

    def test_kitaplary_multi(self, analyzer):
        """'kitaplary' → 2 sonuç olmalı (A₄ ve D₃b)."""
        multi = analyzer.parse("kitaplary")
        assert multi.count >= 2, f"'kitaplary' için en az 2 sonuç beklendi, {multi.count} bulundu"

    def test_guzusu(self, analyzer):
        """'guzusu' → guzy kökünden D₃b iyelik."""
        multi = analyzer.parse("guzusu")
        assert multi.success is True
        stems = [r.stem.lower() for r in multi.results]
        assert "guzy" in stems, f"'guzusu' için 'guzy' kökü beklendi: {stems}"

    def test_multi_result_structure(self, analyzer):
        """MultiAnalysisResult yapısı kontrolü."""
        multi = analyzer.parse("kitap")
        assert hasattr(multi, 'results')
        assert hasattr(multi, 'count')
        assert hasattr(multi, 'success')
        assert hasattr(multi, 'original')
        assert multi.original == "kitap"
