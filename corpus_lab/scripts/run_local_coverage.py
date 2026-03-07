#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Local Corpus Coverage Test — yerel metbugat_corpus.txt üzerinden çalışır.

Büyük corpus'u rastgele örnekleyerek (veya ilk N kelime) hızlı coverage ölçer.
Kategorize edilmiş hata raporu üretir.
"""

import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime

# Proje kökünü sys.path'e ekle
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
_FST_DIR = os.path.join(_PROJECT_ROOT, "turkmen-fst")
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _FST_DIR not in sys.path:
    sys.path.insert(0, _FST_DIR)

from turkmen_fst.analyzer import MorphologicalAnalyzer
from turkmen_fst.lexicon import Lexicon

# ==============================================================================
#  Tokenization — geliştirilmiş (v2)
# ==============================================================================

# Ana kelime regex'i: Türkmence harflerden oluşan kelimeler + tireli bileşikler
TURKMEN_WORD_RE = re.compile(
    r"\b([a-zA-ZçÇäÄöÖüÜşŞňŇžŽýÝ][a-zA-ZçÇäÄöÖüÜşŞňŇžŽýÝ'-]*[a-zA-ZçÇäÄöÖüÜşŞňŇžŽýÝ]|[a-zA-ZçÇäÄöÖüÜşŞňŇžŽýÝ])\b"
)
SKIP_RE = re.compile(r"^(\d+|[IVXLCDM]+|[A-Z]{1,3}\.?)$")

# Sıra sayı kalıbı: 1-nji, 2024-nji, 25-njy vb.
ORDINAL_RE = re.compile(r"\b(\d+)-(nji|njy)\b")

# Sözlükte kayıtlı 2-harfli kelimeler (beyaz liste).
# Bu listedeki kelimeler 2 harf olsa da geçerli token olarak kabul edilir.
# Sözlük yüklendikten sonra dinamik olarak da doldurulabilir.
_TWO_LETTER_WHITELIST: set[str] = set()

# Bilinen tireli bağlaçlar/zarflar — tek token olarak kabul edilir
TIRELI_SABIT_LISTE = {
    "hem-de", "has-da", "beýläk-de", "hususan-da",
    "ýene-de", "başga-da", "şeýle-de", "hatda",
}


def _build_two_letter_whitelist(lexicon: Lexicon | None = None):
    """Sözlükten 2 harfli geçerli kelimeleri beyaz listeye ekle."""
    global _TWO_LETTER_WHITELIST
    if lexicon is None:
        return
    for entries in lexicon._entries.values():
        for e in entries:
            if len(e.word) == 2:
                _TWO_LETTER_WHITELIST.add(e.word.lower())


def tokenize(text: str) -> list[str]:
    tokens = []

    # 1. Sıra sayılarını ön-işle: "2024-nji" → "2024nji" (tire kaldır)
    #    Böylece ana regex tarafından yakalanmaz, ayrı ele alınır.
    ordinals_found: list[str] = []
    def _replace_ordinal(m):
        ordinals_found.append(m.group(0).lower())
        return " "  # boşlukla değiştir (ana regex'ten gizle)
    text = ORDINAL_RE.sub(_replace_ordinal, text)

    for match in TURKMEN_WORD_RE.finditer(text):
        word = match.group(1)
        if SKIP_RE.match(word):
            continue
        word = word.strip("-'")
        w_lower = word.lower()

        # Tireli sabit liste kontrolü
        if w_lower in TIRELI_SABIT_LISTE:
            tokens.append(w_lower)
            continue

        # Kısaltma+ek kalıbı: BMG-niň, ÝUNESKO-nyň, ABŞ-da vb.
        # Sol taraf TAMAMEN büyük harf (2+ karakter), sağ taraf küçük harf eki
        if "-" in w_lower:
            _dash = word.index("-")
            _left = word[:_dash]
            _right = word[_dash+1:]
            if (len(_left) >= 2 and _left == _left.upper()
                    and _right and _right == _right.lower()):
                tokens.append(w_lower)       # tek token olarak tut
                continue

        # Tireli bileşik: parçalara ayır ve her birini ayrı token olarak ekle
        if "-" in w_lower:
            parts = [p.strip() for p in w_lower.split("-") if p.strip()]
            for part in parts:
                if len(part) >= 3 or part in _TWO_LETTER_WHITELIST:
                    tokens.append(part)
            continue

        # Minimum uzunluk filtresi: 3+ harf VEYA beyaz listede
        if len(w_lower) >= 3 or w_lower in _TWO_LETTER_WHITELIST:
            tokens.append(w_lower)

    # Sıra sayılarını ayrı token olarak ekle
    tokens.extend(ordinals_found)
    return tokens


# ==============================================================================
#  Hata kategorileme
# ==============================================================================

def categorize_unrecognized(word: str) -> str:
    """Tanınmayan kelimeyi olası hata kategorisine ata."""
    w = word.lower()

    # 1. Sıra sayı: "2024-nji", "nji", "ýedinji" vb. (tireli kontrolünden ÖNCE)
    if re.match(r"^\d+-?nji$", w) or re.match(r"^\d+-?njy$", w):
        return "sira_sayi"
    if w.endswith("njy") or w.endswith("nji") or w == "nji" or w == "njy":
        return "sira_sayi"

    # 2. Tireli birleşik yapılar: hem-de, has-da, beýläk-de
    if "-" in w:
        return "tireli_bilesik"

    # 3. Özel isimler (büyük harfle başlayan — tokenize lowercase yapıyor,
    #    ama bazı kalıplar tanınabilir)
    if any(w.startswith(p) for p in ["berdimuhamedow", "türkmenistan"]):
        return "ozel_isim"

    # 4. Ettirgen/Edilgen fiil gövdeleri: -dyr/-dir, -yl/-il, -yr/-ir
    ettirgen_pats = ["dürme", "dürip", "düril", "dirmek", "dirme", "dirip",
                     "dyrmak", "dyryş", "diriş", "diril", "dürýä", "dirýä",
                     "dylan", "dilen", "dyryp", "dirip", "düren", "diren",
                     "dyrmaga", "dirmäge", "dyrmaly", "dirmeli",
                     "landyr", "leşdir", "laşdyr", "leşdir",
                     "ösdür", "ösdürm"]
    for pat in ettirgen_pats:
        if pat in w:
            return "ettirgen_edilgen"

    # 5. Fiilimsi formları: -mak/-mek, -yp/-ip (zarf-fiil), -an/-en, -ýan/-ýen
    fiilimsi_endings = ["mak", "mek", "maga", "mäge", "makda", "mekde",
                        "maklyg", "meklig", "magy", "megi",
                        "magyn", "megin",
                        "yp", "ip", "up", "üp",
                        "ýan", "ýen", "ýär", "ýäk"]
    for ending in fiilimsi_endings:
        if w.endswith(ending) and len(w) > len(ending) + 1:
            return "fiilimsi_zarf"

    # 6. -lyk/-lik, -çy/-çi, -ly/-li yapım ekleri
    yapim_endings = ["lyk", "lik", "luk", "lük",
                     "çy", "çi", "çylyk", "çilik",
                     "ly", "li", "lu", "lü",
                     "syz", "siz", "suz", "süz",
                     "daş", "deş"]
    for ending in yapim_endings:
        if w.endswith(ending) and len(w) > len(ending) + 2:
            return "yapim_ekli"

    # 7. Yabancı kelimeler (Rusça, İngilizce vb.)
    foreign_markers = ["ph", "th", "tion", "sion", "ing", "ment",
                       "golf", "cup", "club", "team", "match"]
    for m in foreign_markers:
        if m in w:
            return "yabanci"

    # 8. Kısaltma / Akronim
    if w.endswith("-nyň") or w.endswith("-niň") or w.endswith("-yň") or w.endswith("-da"):
        return "kisaltma_ekli"

    # 9. Çokluk+hal bileşik ekleri (sözlükte kök yok)
    if any(w.endswith(e) for e in ["lary", "leri", "laryn", "leriň",
                                    "laryň", "leriň", "laryny", "lerini",
                                    "larynda", "lerinde", "laryndan", "lerinden"]):
        return "cok_ekli_isim"

    # 10. Diğer fiil çekimleri
    fiil_endings = ["dym", "dim", "dyk", "dik", "dy", "di",
                    "ýaryn", "ýärin", "jek", "jak",
                    "ypdyr", "ipdir", "ypmyş", "ipmiş",
                    "sa", "se", "syn", "sin",
                    "aýyn", "eýin", "aly", "eli",
                    "ar", "er", "ýar", "ýär"]
    for ending in fiil_endings:
        if w.endswith(ending) and len(w) > len(ending) + 1:
            return "fiil_cekimi"

    return "diger"


# ==============================================================================
#  Ana analiz
# ==============================================================================

def run_coverage(corpus_path: str, sample_size: int = 0):
    """
    Corpus dosyasından coverage testi yap.
    sample_size=0 → tüm corpus
    """
    print("=" * 70)
    print("  TurkmenFST — Local Corpus Coverage Test")
    print("=" * 70)

    # 1. Sözlük yükle
    print("\n[1/4] Sözlük yükleniyor...")
    lexicon = Lexicon()
    dict_path = os.path.join(_FST_DIR, "data", "turkmence_sozluk.txt")
    if os.path.exists(dict_path):
        lexicon.load(dict_path)
        print(f"  Sözlük: {lexicon._word_count} giriş")
        _build_two_letter_whitelist(lexicon)
        print(f"  2-harfli beyaz liste: {len(_TWO_LETTER_WHITELIST)} kelime")
    else:
        print(f"  UYARI: Sözlük bulunamadı: {dict_path}")
    analyzer = MorphologicalAnalyzer(lexicon)

    # 2. Corpus oku
    print(f"\n[2/4] Corpus okunuyor: {corpus_path}")
    with open(corpus_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Makale başlıklarını temizle
    text = re.sub(r"=== ARTICLE \d+ ===", "", text)

    # 3. Tokenize
    print(f"\n[3/4] Tokenize ediliyor...")
    all_tokens = tokenize(text)
    print(f"  Toplam token: {len(all_tokens):,}")

    if sample_size > 0 and sample_size < len(all_tokens):
        import random
        random.seed(42)
        tokens = random.sample(all_tokens, sample_size)
        print(f"  Örnekleme: {sample_size:,} token")
    else:
        tokens = all_tokens
        print(f"  Tüm corpus kullanılıyor")

    type_counter = Counter(tokens)
    total_tokens = len(tokens)
    total_types = len(type_counter)
    print(f"  Benzersiz form (type): {total_types:,}")

    # 4. Analiz
    print(f"\n[4/4] Morfolojik analiz...")
    start_time = time.time()

    recognized_types = {}
    unrecognized_types = {}

    done = 0
    for word, count in type_counter.items():
        result = analyzer.parse(word)
        first = result.results[0] if result.results else None

        if first and first.word_type != "unknown":
            recognized_types[word] = {
                "count": count,
                "word_type": first.word_type,
                "stem": first.stem,
                "breakdown": first.breakdown,
            }
        else:
            unrecognized_types[word] = count

        done += 1
        if done % 1000 == 0:
            pct = done / total_types * 100
            print(f"  {done:,}/{total_types:,} type ({pct:.0f}%)...")

    elapsed = time.time() - start_time

    # Token-level
    rec_tokens = sum(info["count"] for info in recognized_types.values())
    unrec_tokens = sum(unrecognized_types.values())
    token_cov = rec_tokens / total_tokens * 100 if total_tokens > 0 else 0
    type_cov = len(recognized_types) / total_types * 100 if total_types > 0 else 0

    # ==================================================================
    #  Hata kategorileme
    # ==================================================================
    categories = defaultdict(list)
    cat_token_count = defaultdict(int)

    for word, count in sorted(unrecognized_types.items(), key=lambda x: -x[1]):
        cat = categorize_unrecognized(word)
        categories[cat].append((word, count))
        cat_token_count[cat] += count

    # ==================================================================
    #  POS dağılımı
    # ==================================================================
    pos_dist = Counter(info["word_type"] for info in recognized_types.values())

    # ==================================================================
    #  Rapor yazdır
    # ==================================================================
    print("\n" + "=" * 70)
    print("  SONUÇLAR")
    print("=" * 70)
    print(f"\n  Corpus: {os.path.basename(corpus_path)}")
    print(f"  Analiz süresi: {elapsed:.1f}s ({total_types / elapsed:.0f} type/s)")

    print(f"\n  TOKEN-LEVEL COVERAGE:")
    print(f"    Toplam:     {total_tokens:>10,}")
    print(f"    Tanınan:    {rec_tokens:>10,}  ({token_cov:.2f}%)")
    print(f"    Tanınmayan: {unrec_tokens:>10,}  ({100 - token_cov:.2f}%)")

    print(f"\n  TYPE-LEVEL COVERAGE:")
    print(f"    Toplam:     {total_types:>10,}")
    print(f"    Tanınan:    {len(recognized_types):>10,}  ({type_cov:.2f}%)")
    print(f"    Tanınmayan: {len(unrecognized_types):>10,}  ({100 - type_cov:.2f}%)")

    print(f"\n  POS DAĞILIMI (tanınan):")
    for pos, cnt in pos_dist.most_common():
        print(f"    {pos:12s}: {cnt:>6,} type")

    print(f"\n  TANINMAYAN KELİME KATEGORİLERİ:")
    print(f"  {'Kategori':25s} {'Type':>7s} {'Token':>8s} {'Token%':>7s}")
    print(f"  {'-'*25} {'-'*7} {'-'*8} {'-'*7}")
    for cat, items in sorted(cat_token_count.items(), key=lambda x: -x[1]):
        t_pct = cat_token_count[cat] / unrec_tokens * 100 if unrec_tokens > 0 else 0
        print(f"  {cat:25s} {len(categories[cat]):>7,} {cat_token_count[cat]:>8,} {t_pct:>6.1f}%")

    print(f"\n  KATEGORİ DETAYLARI (Her kategoriden top 10):")
    for cat in sorted(categories.keys(), key=lambda c: -cat_token_count[c]):
        cat_items = categories[cat]
        print(f"\n  [{cat}] ({len(cat_items)} type, {cat_token_count[cat]} token):")
        for w, c in cat_items[:10]:
            print(f"    {w:30s} × {c}")

    print(f"\n  EN SIK TANINMAYAN 50 KELİME:")
    top50 = sorted(unrecognized_types.items(), key=lambda x: -x[1])[:50]
    for i, (w, c) in enumerate(top50, 1):
        cat = categorize_unrecognized(w)
        print(f"    {i:3d}. {w:30s} × {c:>4d}  [{cat}]")

    # ==================================================================
    #  JSON kaydet
    # ==================================================================
    output = {
        "test_date": datetime.now().isoformat(),
        "corpus_file": os.path.basename(corpus_path),
        "total_corpus_words": len(all_tokens),
        "sample_size": len(tokens),
        "results": {
            "total_tokens": total_tokens,
            "total_types": total_types,
            "recognized_tokens": rec_tokens,
            "unrecognized_tokens": unrec_tokens,
            "recognized_types": len(recognized_types),
            "unrecognized_types": len(unrecognized_types),
            "token_coverage_pct": round(token_cov, 2),
            "type_coverage_pct": round(type_cov, 2),
            "pos_distribution": dict(pos_dist.most_common()),
        },
        "error_categories": {
            cat: {
                "type_count": len(categories[cat]),
                "token_count": cat_token_count[cat],
                "top_examples": categories[cat][:20],
            }
            for cat in sorted(categories.keys(), key=lambda c: -cat_token_count[c])
        },
        "top_unrecognized_100": top50[:100] if len(top50) >= 100 else sorted(
            unrecognized_types.items(), key=lambda x: -x[1]
        )[:100],
    }

    report_dir = os.path.join(os.path.dirname(_SCRIPT_DIR), "reports")
    os.makedirs(report_dir, exist_ok=True)
    out_path = os.path.join(report_dir, "corpus_coverage_local.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  JSON rapor: {out_path}")
    print("=" * 70)

    return output


if __name__ == "__main__":
    corpus_path = os.path.join(_SCRIPT_DIR, "..", "data", "metbugat_corpus.txt")

    sample = 0  # varsayılan: tamamı
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--sample" and i + 1 < len(sys.argv[1:]):
            sample = int(sys.argv[i + 2])
        elif arg == "--file" and i + 1 < len(sys.argv[1:]):
            corpus_path = sys.argv[i + 2]

    if not os.path.exists(corpus_path):
        print(f"HATA: Corpus dosyası bulunamadı: {corpus_path}")
        sys.exit(1)

    run_coverage(corpus_path, sample_size=sample)
