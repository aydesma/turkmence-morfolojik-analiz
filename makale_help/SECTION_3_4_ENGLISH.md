# Improved Sections 3 & 4 — English (Paste-Ready)

> **Usage:** Replace the current §3 and §4 in the paper with the text below.
> Directive notes in **[DIRECTIVE: ...]** indicate where a table, figure, or
> template example should be inserted during final formatting.
>
> **Commentary on the current draft** is collected at the end of this file (§ A).

---

## 3. Morphological Structure of Turkmen

Turkmen is an agglutinative Turkic language of the Oghuz branch. Word formation follows a strictly linear pattern in which suffixes attach to the right of the stem in a fixed order. This section describes the phonological processes and inflectional paradigms that TurkmenFST formally models. All rules are defined over the 30-letter Turkmen Latin alphabet.

### 3.1. Vowel System

Turkmen has nine vowel phonemes classified along two axes: backness (back vs. front) and rounding (rounded vs. unrounded). These two dimensions determine vowel harmony in all suffixation.

**[DIRECTIVE: Insert Table 1 — 2×2 vowel grid (back/front × rounded/unrounded) with the nine vowels: {a, o, u, y} (back), {e, ä, ö, i, ü} (front); rounded {o, ö, u, ü}, unrounded {a, e, ä, y, i}. Keep it compact, one small table.]**

The **last vowel** of a stem governs the vowel quality of all subsequent suffixes. This is the single most important phonological fact for the inflectional engine: every suffix lookup begins with a call to *get_vowel_quality(stem)*.

### 3.2. Phonological Processes

TurkmenFST implements four phonological processes that transform stems and suffixes during concatenation.

#### 3.2.1. Vowel Harmony

Suffix vowels agree in backness with the last vowel of the stem. If the last vowel belongs to the **back** set {a, o, u, y}, a back variant is selected; otherwise a front variant is chosen:

```
kitap  → kitap + lar   (last vowel a ∈ back → -lar)
mekdep → mekdep + ler  (last vowel e ∈ front → -ler)
```

An additional **rounding harmony** layer applies in possessive and genitive contexts: when the stem contains a rounded vowel (o, ö, u, ü), certain suffix vowels surface in their rounded form:

```
okuw  → okuw + um   (rounded → -um, not -ym)
göz   → göz + üm    (rounded → -üm, not -im)
kitap → kitab + ym   (unrounded → -ym)
```

#### 3.2.2. Consonant Softening

When a vowel-initial suffix attaches to a stem ending in a voiceless stop, that stop voices according to the mapping **p→b, ç→j, t→d, k→g**:

```
kitap + ym  → kitab + ym  → kitabym   (my book)
agaç  + yň  → agaj + yň   → agajyň   (of the tree)
ýürek + im  → ýüreg + im  → ýüregim  (my heart)
```

Softening applies **only** to stems tagged with `softening` in the lexicon (6,997 nouns). This prevents incorrect application to loanwords. Furthermore, homonymous stems may differ in softening behaviour; for example, *at* meaning "name" softens (*adym* "my name") whereas *at* meaning "horse" does not (*atym* "my horse"). Six such pairs are explicitly modelled.

In verb conjugation, consonant softening also occurs in specific tenses (see §3.4).

#### 3.2.3. Vowel Elision

In 20 stems, the vowel of the final syllable drops when a vowel-initial suffix is added:

```
burun + um → burn + um → burnum   (my nose)
ogul  + y  → ogl  + y  → ogly     (his son)
```

Five additional stems follow an **irregular** elision pattern in which a different vowel position is affected (e.g., *asyl→asl, nesil→nesl, ylym→ylm*). Both groups are listed in the phonology module and tagged in the lexicon (`vowel_drop` / `exception_drop`). Crucially, elision triggers **only** before vowel-initial suffixes; consonant-initial suffixes leave the stem intact (*burunda*, not *\*burnda*).

#### 3.2.4. Rounding Alternation

A handful of stems whose final vowel is *y* or *i* undergo rounding (*y→u, i→ü*) before the plural suffix and the 3rd-person possessive:

```
guzy  → guzular  (lambs)
süri  → sürüler  (herds)
```

**[DIRECTIVE: Insert Table 2 — A compact summary table listing each phonological process, the number of affected stems, the relevant lexicon tag, and one example each. Four rows.]**

### 3.3. Noun Inflection

A Turkmen noun inflects according to the fixed slot order:

```
STEM + [PLURAL] + [POSSESSIVE] + [CASE]
```

Any violation of this order (e.g., case before possessive) produces an ungrammatical form; the morphotactic state machine described in §4.3 enforces this constraint.

#### 3.3.1. Case Suffixes

Turkmen has six cases. Each case suffix has allomorphs conditioned by (i) vowel harmony, (ii) whether the stem ends in a vowel or consonant, and (iii) the presence of a possessive suffix (which introduces a buffer consonant *n*):

**[DIRECTIVE: Insert Table 3 — Case suffixes. Columns: Case | Function | Post-Consonant | Post-Vowel | Post-Possessive. Six rows: Nominative ∅, Genitive -(n)yň/-(n)iň, Dative -a/-e (special rule: final vowel → a/ä), Accusative -(n)y/-(n)i, Locative -(n)da/-(n)de, Ablative -(n)dan/-(n)den. Mention the dative special rule in a footnote.]**

The dative (A3) deserves special mention: when the stem ends in a vowel, no suffix is added; instead, the final vowel changes directly to *a* (back) or *ä* (front). This is the only case in which suffixation alters the stem-final segment rather than appending material.

#### 3.3.2. Possessive Suffixes

Three singular and two plural possessive persons are distinguished (3rd plural is identical to 3rd singular). Allomorph selection depends on stem-final sound (vowel/consonant), vowel harmony, and rounding:

**[DIRECTIVE: Insert Table 4 — Possessive suffixes. Columns: Person | Post-Consonant (plain) | Post-Consonant (rounded) | Post-Vowel. Five rows: 1sg -ym/-im/-um/-üm, 2sg -yň/-iň/-uň/-üň, 3sg -y/-i/-sy/-si, 1pl -ymyz/-imiz/-umyz/-ümiz, 2pl -yňyz/-iňiz/-uňyz/-üňiz. Keep compact.]**

When a possessive suffix is added, consonant softening and vowel elision apply in sequence before the suffix vowel:

```
kitap + ym  → kitab + ym → kitabym      (softening only)
burun + um  → burn + um  → burnum       (elision only)
```

#### 3.3.3. Plural

The plural marker is *-lar* (back) / *-ler* (front), governed by vowel harmony. It always precedes possessive and case slots:

```
kitap + lar + ym + da  → kitaplarymda   (in my books)
```

#### 3.3.4. Copular Negation (*däl*)

Predicate negation for nouns is analytic: the particle *däl* ("not," cognate of Turkish *değil*) is placed after the fully inflected form. It does not interact with the phonology of the preceding noun:

```
kitap         → kitap däl          (is not a book)
kitabym       → kitabym däl        (is not my book)
kitaplarda    → kitaplarda däl     (not in the books)
```

Note that the **privative derivational** suffix *-syz/-siz* (≈ "without," e.g. *kitapsyz* "bookless") creates a new adjective and therefore belongs to derivational morphology. Since TurkmenFST currently covers only inflectional morphology, *-syz/-siz* is outside the scope of the present system and is listed as future work (§8).

### 3.4. Verb Conjugation

Turkmen verbs inflect in the order **STEM + [NEGATION] + TENSE/MOOD + [PERSON]**. TurkmenFST models seven conjugated tenses, five non-finite forms, two voice transformations, and four special moods, producing inflected forms across six persons (3 singular + 3 plural) in both affirmative and negative polarity.

#### 3.4.1. Tense and Mood System

**[DIRECTIVE: Insert Table 5 — Seven tenses. Columns: Code | Tense | Turkmen Name | Suffix Pattern (affirmative) | Example (gel- "to come"). Rows: Ö1 Definite Past -dy/-di, Ö2 Indefinite Past -ypdy/-ipdi, Ö3 Continuous Past -ýardy/-ýärdi, H1 General Present -ýar/-ýär, H2 Definite Present (special), G1 Definite Future -jak/-jek + copula, G2 Indefinite Future -ar/-er/-r. Compact; examples only for A1.]**

In addition, the system generates conditional (Ş1), imperative (B1K), necessitative (HK), evidential (NÖ), and optative-regret (AÖ) moods, as well as converbs (FH), and past/present/future participles (FÖ/FÄ/FG). Causative (ETT) and passive (EDL) voice derivations are also supported.

#### 3.4.2. Person Suffixes

Two paradigms of person markers are used; which paradigm applies depends on the tense:

**[DIRECTIVE: Insert Table 6 — Two-column person paradigms. Columns: Person | Standard Paradigm (Ö1, Ö2, Ö3, Ş1, AÖ) | Extended Paradigm (H1, G2, NÖ). Six rows for A1–B3. Keep short — show only back-vowel allomorphs, note VH applies.]**

#### 3.4.3. Negation Strategies

Unlike Turkish, where verbal negation is almost uniformly expressed by the suffix *-ma/-me*, Turkmen employs **three distinct negation strategies** according to tense/mood:

**Strategy 1 — Synthetic negation (-ma/-me).** The negation morpheme inserts between stem and tense suffix. Used in definite past (Ö1), general present (H1), and conditional (Ş1):

```
gel + me + di + m → gelmedim        (I did not come)
gel + me + ýär + in → gelmeýärin    (I do not come)
```

**Strategy 2 — Fused negation.** Negation and tense merge into a single portmanteau morpheme. Used in indefinite past (Ö2), indefinite future (G2), and evidential (NÖ):

```
gel + mändi + m → gelmändim         (I had not come — Ö2 neg.)
gel + mez → gelmez                  (he will not come — G2 neg.)
```

**Strategy 3 — Analytic (periphrastic) negation.** Negation is expressed by the separate word *däl* (= değil). Used in continuous past (Ö3), definite future (G1), and necessitative (HK):

```
gel + ýän däldi + m → gelýän däldim  (I was not coming — Ö3 neg.)
gel + jek däl → geljek däl           (will not come — G1 neg.)
```

**[DIRECTIVE: Insert Table 7 — Negation strategies mapped to tenses. Three rows (Synthetic / Fused / Analytic), each row listing the applicable tense codes and a single example. Small table.]**

The coexistence of these three strategies in a single language is typologically noteworthy and has practical engineering consequences: the generator's negation logic is not a simple prefix/suffix toggle but a tense-dependent decision tree.

#### 3.4.4. Definite Present — Special Construction (H2)

The definite present (*Anyk Häzirki*) is structurally unique. Only four auxiliary verbs (*otyr-, dur-, ýatyr-, ýör-*) conjugate in this tense, each taking a tense-specific person paradigm. This tense expresses the "right now" aspect:

```
otyr + yn → otyryn   (I am sitting — right now)
dur  + un → durun    (I am standing — right now)
```

#### 3.4.5. Stem-Level Sound Changes in Verbs

In the general present (H1) and indefinite future (G2), two additional stem changes occur before the vowel-initial tense suffix:

1. **k/t softening:** In polysyllabic stems and in four special monosyllabic stems (*aýt-, gaýt-, et-, git-*), stem-final k→g, t→d.
2. **e→ä raising (G2 only):** The last stem vowel *e* becomes *ä* in indefinite future.

```
aýt + ýar → aýdýar    (softening: t→d)
gel + er   → gäler     (raising: e→ä)
```

---

## 4. System Architecture

TurkmenFST is implemented as a modular Python package (`turkmen_fst`) comprising five core modules: phonology rules (`phonology.py`), lexicon management (`lexicon.py`), morphotactic state machine (`morphotactics.py`), generation engine (`generator.py`), and analysis engine (`analyzer.py`). Each module has a single responsibility and communicates with others through well-defined function interfaces.

**[DIRECTIVE: Insert Figure 1 — System architecture diagram (use the Mermaid source from MERMAID_SEKIL_2_3_4.md, rendered as a proper vector figure). Show the five modules with dependency arrows: phonology and lexicon feed into generator; morphotactics validates each step inside generator; analyzer calls generator for reverse-generation verification. Also show the Flask web / REST API layer on top.]**

### 4.1. Phonology Module (`phonology.py`)

The phonology module encodes every sound rule described in §3.2 as a stateless static method. It holds no mutable state; each function takes a stem (and optionally a suffix) as input and returns a transformed string. This stateless design permits independent unit testing — 36 of the system's 105 unit tests target this module alone.

The module's principal data structures and methods are summarised below:

**[DIRECTIVE: Insert Table 8 — Phonology module components. Columns: Component | Content | Size. Rows: VowelSystem (vowel sets — 3 sets, 9 vowels), SOFTENING_TABLE (voiceless→voiced mapping — 4 pairs), VOWEL_DROP_CANDIDATES (regular elision list — 20 stems), VOWEL_DROP_EXCEPTIONS (irregular elision — 5 stems), ROUNDING_LIST (rounding alternation — 3 stems). Small table.]**

Key methods include `get_vowel_quality(word)`, which returns `"yogyn"` (back) or `"ince"` (front); `apply_consonant_softening(stem)` and its inverse `reverse_consonant_softening(stem)` (used in analysis); `apply_vowel_drop(stem, suffix)` and `reverse_vowel_drop(stem)`. A pipeline function `apply_pre_suffix_rules(stem, suffix, ...)` chains elision and softening in the correct order before suffix attachment.

### 4.2. Lexicon Module (`lexicon.py`)

The lexicon loads a plain-text dictionary file (32,015 entries) at startup. Each entry carries a lemma, a part-of-speech tag, and zero or more morphological feature tags:

```
kitap    %<n%>    softening
burun    %<n%>    vowel_drop
at       %<n%>    softening;homonym:1=AT_(Ad)|yes;2=AT_(At)|no
```

Feature tags govern the phonological rules applied during generation: `softening` permits consonant voicing; `vowel_drop` / `exception_drop` triggers elision; `homonym` enumerates meaning-specific softening permissions. The lexicon is detailed further in §5.

### 4.3. Morphotactic State Machine (`morphotactics.py`)

Suffix ordering constraints are formalised as finite-state automata inspired by the model of Beesley and Karttunen (2003). Separate automata are defined for nouns and verbs:

```
Noun FST:   STEM → [PLURAL] → [POSSESSIVE] → [CASE] → FINAL
Verb FST:   STEM → [NEGATION] → TENSE → [PERSON] → FINAL
```

Each state transition is labelled with a morphological category (`MorphCategory`). A state's `is_final` flag indicates whether generation may terminate there (e.g., the verb stem state is non-final — a bare stem without a tense suffix is not a valid conjugated form). The machine rejects any invalid suffix sequence — such as plural after case, or case after case — before the generator performs any phonological computation, thereby guaranteeing that only grammatically valid paths reach the surface.

### 4.4. Generation Engine (`generator.py`)

The generation engine transforms *(stem, feature-set) → surface form*. Two main classes are defined:

**NounGenerator** performs noun inflection in the following pipeline:

1. Look up the stem in the lexicon; retrieve morphological features.
2. Validate the suffix sequence against the noun FST (§4.3).
3. If plural: attach *-lar/-ler* per vowel harmony.
4. If possessive: apply vowel elision and consonant softening, then attach the possessive allomorph.
5. If case: determine buffer consonant *n* (post-possessive) or direct attachment; apply the case allomorph.
6. If negation: append the copular particle *däl*.
7. Return the inflected surface form, a morpheme breakdown string, and the ordered morpheme list.

**VerbGenerator** handles verb conjugation, implementing tense-specific suffix selection, the three negation strategies (§3.4.3), person paradigm selection, and stem-level sound changes. Each tense–person–polarity combination has been cross-validated against the conjugation tables of enedilim.com (§7.4).

Both generators return a `GenerationResult` data class containing the surface word, breakdown path, stem, and morpheme list.

### 4.5. Analysis Engine (`analyzer.py`)

The analyser decomposes an inflected surface form into its constituent root and suffix chain. It uses a **generate-and-verify** strategy:

1. Enumerate candidate roots from the lexicon that could plausibly underlie the input form.
2. For each candidate, generate all combinatorially possible inflected forms via the generation engine.
3. If a generated form matches the input, the corresponding feature-set is reported as a valid parse.

This design has two key advantages. First, no phonological rules need to be reimplemented separately for analysis; the generator's rules are reused implicitly, guaranteeing **100% round-trip consistency** between generation and analysis (verified on 1,192 test pairs — see §7). Second, the approach naturally handles homonyms: for a word like *ady*, both parses "at (name) + 3sg-poss" (with softening: at→ad+y) and "at (horse) + 3sg-poss" (without: at+y→aty) are generated and compared, and all matching analyses are returned.

Cross-deduplication removes identical surface-level analyses that arise from different homonym branches, so the user receives only semantically distinct results.

---

## § A — Commentary on the Current Draft (remove before submission)

### Shortcomings of the current §3

1. **Too brief.** The current §3 is roughly half a page. For a morphology-focused paper, the linguistic section should be the most detailed; readers need to understand the phenomena before the engineering solution.
2. **No vowel system table.** The nine-vowel inventory and its two-axis classification are never presented in tabular form.
3. **No complete case table.** Only a partial table is given — allomorphs conditioned by post-vowel and post-possessive positions are missing.
4. **Three negation strategies not covered.** This is arguably the most interesting typological feature. The current draft mentions "periphrastic negation" in passing but does not delineate the three strategies or map them to tenses.
5. **Vowel elision understated.** Only two examples and no mention of the regular/irregular distinction.
6. **Rounding harmony absent.** Not mentioned at all in the current §3.
7. **No step-by-step derivation.** A conference paper should include at least one full derivation example so readers can follow the pipeline.
8. **Verb tense table lacks suffix patterns.** The table lists tenses and examples but not the actual suffix morphemes; readers cannot verify the system from the table alone.
9. **H2 (Definite Present) special construction not explained.** This is unique to Turkmen and should be highlighted.
10. **No mention of copular negation (däl) for nouns.** Predicate negation for nouns is not covered at all.

### Shortcomings of the current §4

1. **ASCII-art diagram.** Should be replaced with a proper vector figure (Mermaid → SVG, TikZ, or draw.io).
2. **Descriptions lack depth.** Each subsection is ~5 sentences. The generation pipeline (six-step sequence) is not shown. The morphotactic FST is not formalized beyond a one-line schema.
3. **No mention of `GenerationResult` or the morpheme list.** These are critical for API consumers and for the analysis engine.
4. **Analysis engine's generate-and-verify strategy deserves more emphasis.** This is an architecturally novel choice (compared to traditional two-level analysis) and a selling point of the paper.
5. **Homonym handling not discussed in §4.** The dual-parse mechanism for *at*, *ot*, etc., is an engineering contribution worth highlighting.
6. **Missing quantitative summary of module sizes.** A short table (module, LOC, #unit tests) would add substance.

### Note on -syz/-siz

The suffix **-syz/-siz** (≈ Turkish *-sız/-siz*, "without, -less") is a **derivational** suffix that derives adjectives from nouns (*kitap→kitapsyz* "bookless", *suw→suwsyz* "waterless"). It is **not** part of noun inflection (çekim); it belongs to word formation (yapım).

For **predicate negation** of noun sentences, the correct mechanism is the copular particle **däl**:
- *Bu kitap.* → *Bu kitap däl.* (This is not a book.)
- *Kitabym.* → *Kitabym däl.* (Not my book.)

So what we implemented ("adding *däl* after the inflected noun form") is correct for noun inflection negation. The -syz/-siz suffix would be relevant only if the system supported derivational morphology, which is noted as future work (§8.2 already lists it).
