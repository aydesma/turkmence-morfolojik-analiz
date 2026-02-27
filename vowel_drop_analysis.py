# -*- coding: utf-8 -*-
"""Ünlü düşmesi fonotaktik analizi — rapor dosyaya yazılır"""

ALL_VOWELS = set("aouyeäöiü")
CONSONANTS = set("bcçdfghjklmnňprsştuwýz")
DROPPABLE = set("yiuü")

DUSME_ADAYLARI = {
    "burun", "alyn", "agyz", "gobek", "ogul", "erin",
    "bagyr", "sabyr", "kömür", "sygyr", "deňiz",
    "goýun", "boýun", "howuz", "tomus", "tizir",
    "köwüş", "orun", "garyn", "gelin"
}
DUSME_ISTISNALARI = {"asyl", "pasyl", "nesil", "ylym", "mähir"}
ALL_CURRENT = DUSME_ADAYLARI | DUSME_ISTISNALARI

def count_syl(w):
    return sum(1 for c in w if c in ALL_VOWELS)

def matches_pattern(w):
    if len(w) < 4: return False
    if count_syl(w) < 2: return False
    if w[-1] not in CONSONANTS: return False
    if w[-2] not in DROPPABLE: return False
    if len(w) >= 3 and w[-3] in ALL_VOWELS: return False
    return True

nouns = []
with open("resources/turkmence_sozluk.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split("\t")
        word = parts[0].lower()
        pos = parts[1] if len(parts) > 1 else ""
        features = parts[2] if len(parts) > 2 else ""
        if "%<n%>" in pos:
            nouns.append((word, features))

pm = [(w, f) for w, f in nouns if matches_pattern(w)]
in_list = [(w, f) for w, f in pm if w in ALL_CURRENT]
not_in = [(w, f) for w, f in pm if w not in ALL_CURRENT]

simplex = []
derived_lyk = []
derived_ysh = []
derived_other = []

for w, f in not_in:
    if any(w.endswith(s) for s in ["lyk", "lik", "luk", "lük"]):
        derived_lyk.append((w, f))
    elif any(w.endswith(s) for s in ["yş", "iş", "uş", "üş"]):
        derived_ysh.append((w, f))
    elif len(w) <= 6 and count_syl(w) == 2:
        simplex.append((w, f))
    else:
        derived_other.append((w, f))

with open("vowel_drop_report.txt", "w", encoding="utf-8") as out:
    out.write("=" * 70 + "\n")
    out.write("UNLU DUSMESI FONOTAKTIK ANALIZ RAPORU\n")
    out.write("=" * 70 + "\n\n")
    out.write(f"Toplam isim (sozluk): {len(nouns)}\n")
    out.write(f"Pattern (C+dar_unlu+C, 2+ hece): {len(pm)} kelime eslesti\n")
    out.write(f"  - Zaten listede olan: {len(in_list)} / {len(ALL_CURRENT)}\n")
    out.write(f"  - Listede olmayan: {len(not_in)}\n\n")
    out.write("KURAL: Son hece CVC (C=unsuz, V=dar unlu y/i/u/u)\n")
    out.write("Bu kural cok genis - her -lyk turetmesi de eslesiyor.\n")
    out.write("Gercek unlu dusmesi sadece basit koklerde olur.\n\n")

    out.write("-" * 70 + "\n")
    out.write(f"1. ZATEN LISTEDE OLANLAR ({len(in_list)} kelime)\n")
    out.write("-" * 70 + "\n")
    for w, f in sorted(in_list):
        tag = "[+]" if "vowel_drop" in f or "exception_drop" in f else "[-]"
        out.write(f"  {w:15s}  {tag} {f}\n")

    out.write(f"\n{'-'*70}\n")
    out.write(f"2. BASIT KOKLER - LISTEDE OLMAYANLAR ({len(simplex)} kelime)\n")
    out.write(f"   (2 hece, <=6 harf, turetme eki yok - MANUEL KONTROL GEREKLI)\n")
    out.write("-" * 70 + "\n")
    for w, f in sorted(simplex):
        d = w[:-2] + w[-1]
        out.write(f"  {w:15s}  ->  {d:12s}  [{f}]\n")

    out.write(f"\n{'-'*70}\n")
    out.write(f"3. TURETILMIS KELIMELER -lyk/-lik ({len(derived_lyk)} kelime)\n")
    out.write(f"   (Bu kelimeler unlu dusmesine ugramaz - turetme soneki)\n")
    out.write("-" * 70 + "\n")
    for w, f in sorted(derived_lyk)[:30]:
        out.write(f"  {w}\n")
    if len(derived_lyk) > 30:
        out.write(f"  ... ve {len(derived_lyk)-30} kelime daha\n")

    out.write(f"\n{'-'*70}\n")
    out.write(f"4. TURETILMIS KELIMELER -ys/-is ({len(derived_ysh)} kelime)\n")
    out.write("-" * 70 + "\n")
    for w, f in sorted(derived_ysh)[:30]:
        out.write(f"  {w}\n")
    if len(derived_ysh) > 30:
        out.write(f"  ... ve {len(derived_ysh)-30} kelime daha\n")

    out.write(f"\n{'-'*70}\n")
    out.write(f"5. DIGER TURETILMIS/UZUN KELIMELER ({len(derived_other)} kelime)\n")
    out.write("-" * 70 + "\n")
    for w, f in sorted(derived_other)[:30]:
        out.write(f"  {w}\n")
    if len(derived_other) > 30:
        out.write(f"  ... ve {len(derived_other)-30} kelime daha\n")

    out.write(f"\n{'-'*70}\n")
    out.write("6. LISTEDE OLUP PATTERN ESLESMEYENLER\n")
    out.write("-" * 70 + "\n")
    pw = {w for w, f in pm}
    missing = 0
    for w in sorted(ALL_CURRENT):
        if w not in pw:
            out.write(f"  {w:15s} (hece:{count_syl(w)}, son-2:'{w[-2]}', son:'{w[-1]}')\n")
            missing += 1
    if missing == 0:
        out.write("  (Hepsi eslesti)\n")

    out.write(f"\n{'='*70}\n")
    out.write("SONUC\n")
    out.write(f"Kural tabanli yaklasim {len(not_in)} false-positive uretir.\n")
    out.write(f"Manuel kontrol gereken basit kokler: {len(simplex)} kelime.\n")
    out.write("Mevcut liste tabanli yaklasim dogru strateji.\n")

print(f"Rapor yazildi: vowel_drop_report.txt")
print(f"Toplam isim: {len(nouns)}, Pattern eslesen: {len(pm)}")
print(f"Listede olan: {len(in_list)}, Listede olmayan: {len(not_in)}")
print(f"  Basit kokler (manuel kontrol): {len(simplex)}")
print(f"  Turetilmis -lyk: {len(derived_lyk)}")
print(f"  Turetilmis -ysh: {len(derived_ysh)}")
print(f"  Diger turetilmis: {len(derived_other)}")
