# CHAPTER 3: PAPER-TO-THESIS EXPANSION INSTRUCTIONS

**Date**: 2025-01-06
**Purpose**: Extract and expand content from research paper into rigorous thesis chapter
**Source**: `writing/sources/en.tex` (original research paper, 3267 lines)
**Output**: Verified logical units ready for thesis integration

---

## 🎯 MISSION OVERVIEW

Transform dense research paper content into comprehensive thesis exposition through a two-stage process:
1. **EXTRACTORS**: Generate expansion suggestions with source traceability
2. **AUDITORS**: Verify accuracy and mathematical correctness

**Key Goals**:
- Maintain absolute fidelity to original paper sources
- Expand brief paper content into thesis-level detail
- Provide rigorous mathematical proofs and explanations
- Create verified content ready for thesis integration

---

## 🔬 GRANULARITY GUIDELINES FOR LOGICAL UNITS

**⚠️ CRITICAL PRINCIPLE: PREFER OVER-EXTRACTION TO UNDER-EXTRACTION**

### **Unit Size Philosophy**
- **Each logical unit should represent ONE specific mathematical concept, technique, or result**
- **Err on the side of too many units rather than too few**
- **Better to have 20 focused units than 5 overly broad ones**
- **Each unit should be developable into a solid paragraph to half a page** (0.2-0.5 thesis pages)

### **When to CREATE SEPARATE UNITS**

✅ **Always separate these into distinct units**:
- Different mathematical objects (surfaces vs. moduli spaces vs. compactifications)
- Different properties of the same object (numerical invariants vs. geometric properties)
- Different techniques or methods (construction methods vs. classification results)
- Different types of results (existence vs. uniqueness vs. explicit description)
- Different theoretical frameworks (algebraic vs. geometric vs. combinatorial approaches)
- Supporting lemmas vs. main theorems
- General theory vs. specific applications
- Classical results vs. new contributions

✅ **Granularity Examples**:
```
INSTEAD OF: "Enriques surfaces and their moduli"
CREATE SEPARATE UNITS FOR:
- Enriques surface definition and basic properties
- Numerical invariants (2K ∼ 0, q = 0)
- Quotient construction from K3 surfaces
- Classification of involutions
- Moduli space definition
- Polarization theory
- Comparison with K3 moduli
```

### **When to COMBINE into single units**

❌ **Only combine when concepts are inseparable**:
- Equivalent formulations of the same definition
- Steps of a single proof that cannot stand alone
- Immediate corollaries that follow trivially

### **EXTRACTION TARGET NUMBERS**

**Per paper section, aim for**:
- **Introduction**: 15-25 units (comprehensive background development)
- **Technical sections**: 20-35 units (detailed mathematics)
- **Proof sections**: 25-40 units (step-by-step development)

**Better to extract 30 units and use 20 than to extract 10 and realize you need 25**

### **📊 DENSITY GUIDELINES WITH MULTIPLE UNIT TYPES**

**Source**: Section 1 (Introduction) empirical analysis

#### **🔢 CONVERSION RATES (Empirically Determined)**

| **Metric** | **Conversion Rate** | **Source Data** |
|------------|---------------------|-----------------|
| **LaTeX lines → Pages** | **45 lines = 1 page** | 162 lines = 3.6 pages |
| **Words → Pages** | **187 words = 1 page** | 674 words = 3.6 pages |
| **Units → Words** | **35 words = 1 unit** | 674 words = 19 units |
| **Units → Lines** | **8.5 lines = 1 unit** | 162 lines = 19 units |

#### **📈 DENSITY TARGETS BY UNIT TYPE**

| **Quality Level** | **Units/Page** | **Units/45 Lines** | **Units/187 Words** | **Lines/Unit** | **Words/Unit** |
|-------------------|----------------|-------------------|-------------------|---------------|----------------|
| ❌ **Too sparse** | 1-3 | 1-3 | 1-3 | 15-45 | 62-187 |
| ⚠️ **Minimum acceptable** | 4-5 | 4-5 | 4-5 | 9-11 | 37-47 |
| ✅ **Good target** | 5-8 | 5-8 | 5-8 | 6-9 | 23-37 |
| 🎯 **Excellent** | 8-15 | 8-15 | 8-15 | 3-6 | 12-23 |
| ⚡ **Maximum useful** | 15-20 | 15-20 | 15-20 | 2-3 | 9-12 |

#### **🧮 MULTIPLE CALCULATION FORMULAS**

**Choose the most convenient input metric:**

**📄 FROM PAGE COUNT:**
```
Target Units = Pages × (5-8 units/page)
Example: 3.6 pages × 5-8 = 18-29 units
```

**📝 FROM LINE COUNT:**
```
Target Units = Lines ÷ (6-9 lines/unit)
Example: 162 lines ÷ 6-9 = 18-27 units
```

**📊 FROM WORD COUNT:**
```
Target Units = Words ÷ (23-37 words/unit)
Example: 674 words ÷ 23-37 = 18-29 units
```

**⚡ QUICK ESTIMATION:**
```
Units ≈ Lines ÷ 8    (use 8 lines per unit as rule of thumb)
Units ≈ Words ÷ 30   (use 30 words per unit as rule of thumb)
```

#### **📋 PRACTICAL WORKFLOW BY INPUT TYPE**

**If you have LINE COUNT:**
1. Count LaTeX lines in section: `end_line - start_line + 1`
2. Quick estimate: `lines ÷ 8 = target units`
3. Range check: `lines ÷ 6` to `lines ÷ 9` for min-max range

**If you have WORD COUNT:**
1. Count words in markdown/LaTeX: `wc -w filename`
2. Quick estimate: `words ÷ 30 = target units`
3. Range check: `words ÷ 23` to `words ÷ 37` for min-max range

**If you have PAGE ESTIMATE:**
1. Estimate pages: `lines ÷ 45` or `words ÷ 187`
2. Quick estimate: `pages × 6 = target units`
3. Range check: `pages × 5` to `pages × 8` for min-max range

#### **✅ VALIDATION EXAMPLES**

| **Section** | **Lines** | **Words** | **Pages** | **Target Units** | **Actual Units** | **Assessment** |
|-------------|-----------|-----------|-----------|------------------|------------------|----------------|
| **Section 1** | 162 | 674 | 3.6 | 18-29 | 19 (TODO) | ✅ Perfect |
| **Section 1** | 162 | 674 | 3.6 | 18-29 | 5 (my orig) | ❌ Too sparse |
| **Section 4** | 400+ | 3800 | 8.9 | 45-71 | 100 | ✅ Excellent |
| **Section 5** | 350+ | 3365 | 7.8 | 39-62 | 100 | ✅ Excellent |

### **CONCRETE SPLITTING EXAMPLE**

**❌ TOO COARSE (my original approach)**:
```yaml
unit_id: "enriques_surfaces_definition"
thesis_title: "Enriques Surfaces: Basic Properties and Moduli Theory"
# Covers: definition, invariants, classification position, moduli finiteness
```

**✅ PROPER GRANULARITY (recommended approach)**:
```yaml
- unit_id: "enriques_surface_definition"
  thesis_title: "Definition of Enriques Surfaces as K3 Quotients"

- unit_id: "basepoint_free_involution_conditions"
  thesis_title: "Conditions for Basepoint-Free Involutions on K3 Surfaces"

- unit_id: "enriques_numerical_invariants"
  thesis_title: "Fundamental Invariants: 2K ∼ 0 and q = 0"

- unit_id: "enriques_classification_position"
  thesis_title: "Position in Enriques-Kodaira Classification"

- unit_id: "enriques_vs_k3_comparison"
  thesis_title: "Geometric Comparison with K3 Surfaces"

- unit_id: "polarized_enriques_moduli_finiteness"
  thesis_title: "Finiteness of Polarized Enriques Moduli Spaces"
```

**Result**: 6 focused units instead of 1 overly broad unit, each developing a solid paragraph to half a page (0.2-0.5 thesis pages) of specific mathematical content.

---

## 🔤 NOTATION HANDLING REQUIREMENTS

### **PAPER-SPECIFIC NOTATION CHALLENGES**

Research papers often contain notation issues that must be resolved for thesis clarity:

1. **Undefined LaTeX Macros**: Paper uses `\cL`, `\sH`, `\bZ` without definitions
2. **Context-Dependent Variables**: `$\Pic(Z)$` without explaining what $Z$ represents
3. **Author Conventions**: Implicit notational systems specific to the paper/author
4. **Mathematical Context**: Symbols that mean different things in different contexts

### **EXTRACTOR NOTATION RESPONSIBILITIES**

#### **Step 1: Identify All Notation Issues**
- Document every undefined macro: `\cL`, `\sH`, `\bZ`, etc.
- Note context-dependent variables: `Z`, `X`, `S`, etc.
- Flag ambiguous mathematical symbols

#### **Step 2: Research and Document**
- **LaTeX Macros**: Check paper preamble, standard conventions, or make educated guesses
  - `\cL` likely means `\mathcal{L}` (script L)
  - `\bZ` likely means `\mathbb{Z}` (blackboard bold Z)
  - `\sH` likely means `\mathscr{H}` (script H)
- **Mathematical Context**: Use surrounding text to determine variable meanings
  - In algebraic geometry: `Z` often means a scheme/variety
  - In moduli theory: `S` often means parameter space
  - In lattice theory: `L` often means a lattice

#### **Step 3: Document Everything**
Create comprehensive notation explanations for thesis readers unfamiliar with paper conventions.

---

## 📊 CANONICAL YAML STRUCTURE

**⚠️ THIS IS THE DEFINITIVE FORMAT - ALL IMPLEMENTATIONS MUST USE THIS EXACT STRUCTURE**

```yaml
logical_units:
  - # === UNIT IDENTIFICATION ===
    unit_id: "unique_identifier"                    # REQUIRED: snake_case ID
    unit_type: "theorem"                           # REQUIRED: theorem|lemma|definition|proposition|example|remark
    thesis_title: "Descriptive Title for Thesis"  # REQUIRED: Clear heading for thesis
    dependencies: ["unit_1", "unit_2"]            # REQUIRED: Prerequisites (empty array if none)

    # === SOURCE TRACEABILITY ===
    paper_source:
      file_path: "writing/sources/en.tex"         # REQUIRED: Source file
      start_line: 123                             # REQUIRED: Exact start line
      end_line: 145                               # REQUIRED: Exact end line
      verbatim_content: |                         # REQUIRED: Exact paper text
        [WORD-FOR-WORD content from paper - NEVER modify]
      latex_labels: ["thm:main", "eq:identity"]   # OPTIONAL: LaTeX labels in paper
      paper_citations: ["Author1999", "Smith2000"] # OPTIONAL: Citations used in paper

    # === NOTATION TRANSLATION ===
    notation_explanations:                        # REQUIRED: Document all paper notation
      latex_macros:                               # REQUIRED: Undefined macro translations
        "\\cL": "\\mathcal{L} (script L - likely line bundle or sheaf)"
        "\\bZ": "\\mathbb{Z} (integers)"
        "\\sH": "\\mathscr{H} (script H - likely Hilbert scheme or family)"
      mathematical_context:                       # REQUIRED: Variable/symbol meanings
        "Z": "Scheme or variety being studied (from context in Section 2.1)"
        "S": "Parameter space or base scheme (introduced in Definition 2.3)"
        "\\Pic(Z)": "Picard group of the scheme Z (group of line bundles)"
        "deg": "Degree of polarization (numerical invariant)"
      ambiguous_notation:                         # OPTIONAL: Unclear symbols needing verification
        "H^2": "Could be cohomology or Hilbert scheme - verify in context"
        "\\chi": "Euler characteristic or other invariant - check definition"
      author_conventions:                         # OPTIONAL: Paper-specific conventions
        "polarization_notation": "Author uses (L,Z) for polarized pair, not standard (Z,L)"
        "moduli_convention": "M_d denotes moduli space, not M^d as in some literature"

    # === THESIS EXPANSION ===
    thesis_content:
      condensed_summary: |                        # REQUIRED: Brief overview
        [1-2 paragraph summary of the logical unit]
      detailed_analysis: |                        # REQUIRED: Comprehensive explanation
        [Detailed exposition suitable for thesis - make implicit assumptions explicit]
      expansion_notes: |                          # REQUIRED: What needs expansion from paper
        [Specific areas where paper was brief due to space constraints]

    # === PROOF OBJECTS (Required for theorem|lemma|proposition only) ===
    proof_development:
      paper_proof_content: |                      # REQUIRED: What paper provided
        [Exact proof from paper, often brief or sketched]
      thesis_proof_outline: |                     # REQUIRED: Structured proof plan
        [Step-by-step outline for complete thesis proof]
      rigorous_proof: |                          # REQUIRED: Complete proof for thesis
        [Fully detailed proof suitable for thesis examination]
      line_by_line_proof:                        # REQUIRED: Formalization-ready proof
        - step: 1
          statement: "[Mathematical statement for this step]"
          justification: "[Complete justification with specific citations]"
          citations: ["Theorem X.Y in Paper1999", "Stacks Tag 02AB", "Mathlib theorem_name"]
          assumptions: "[Any assumptions used in this step]"
        - step: 2
          statement: "[Next mathematical statement]"
          justification: "[Complete justification - no gaps allowed]"
          citations: ["Specific theorem/lemma with exact reference"]
          assumptions: "[Explicit assumptions]"
      proof_references: ["Source1", "Source2"]   # REQUIRED: Sources needed for proof

    # === VERIFICATION TRAIL ===
    audits:
      - audit_id: "extractor_initial"             # REQUIRED: Unique audit identifier
        auditor_role: "extractor"                 # REQUIRED: extractor|auditor
        audit_date: "2025-01-06T10:30:00Z"       # REQUIRED: ISO timestamp

        # Initial suspicion scores (extractors set all to 1.0)
        suspicion_scores:
          source_fidelity: 1.0                   # Paper extraction accuracy
          mathematical_accuracy: 1.0             # Mathematical content correctness
          citation_validity: 1.0                 # Reference verification
          proof_correctness: 1.0                 # Mathematical proof validity
          formalization_readiness: 1.0           # Line-by-line proof suitable for Lean
          expansion_quality: 1.0                 # Thesis expansion appropriateness

        audit_notes: |                           # REQUIRED: Auditor comments
          [Comments about the extraction/verification process]

        evidence_gathered: |                     # OPTIONAL: Evidence for score changes
          [Details of verification work performed]
```

---

## 🔧 STAGE 1: EXTRACTOR ROLE

### **PRIMARY MISSION**
Generate rich expansion suggestions from paper content while maintaining absolute source traceability.

### **EXTRACTOR RESPONSIBILITIES**
1. **Source Extraction**: Copy exact content from paper with precise line numbers
2. **Expansion Planning**: Suggest how brief paper content should be expanded for thesis
3. **Proof Development**: Create complete proofs from paper sketches
4. **⚠️ CRITICAL: Line-by-Line Formalization**: Generate step-by-step proofs with explicit citations ready for Lean formalization
5. **Initial Documentation**: Record extraction with maximum suspicion scores
6. **Dependency Mapping**: Identify logical prerequisites

### **EXTRACTOR WORKFLOW**

#### **STEP 1: Locate Paper Content & Calculate Density Target**
```bash
# Find exact location in source paper
grep -n "\\section" writing/sources/en.tex
# Note exact line numbers for traceability

# Calculate density target - CHOOSE MOST CONVENIENT METHOD:

# METHOD A - From line count (most common):
# Lines: end_line - start_line + 1
# Quick target: lines ÷ 8
# Example: Section 1 = 233-72+1 = 162 lines → 162÷8 = 20 units

# METHOD B - From word count (if available):
# wc -w section_file.md
# Quick target: words ÷ 30
# Example: 674 words → 674÷30 = 22 units

# METHOD C - From page estimate:
# Pages: lines ÷ 45 or words ÷ 187
# Quick target: pages × 6
# Example: 162÷45 = 3.6 pages → 3.6×6 = 22 units

# All methods should give similar results!
```

#### **STEP 2: Identify All Granular Units**
- **Read each paragraph sentence-by-sentence**
- **Identify every distinct mathematical concept, technique, or claim**
- **Create separate units for each major mathematical object or property**
- **Don't group concepts just because they appear in the same paragraph**

**Granular Unit Identification Checklist**:
- [ ] Each theorem, lemma, proposition, definition gets its own unit
- [ ] Each technique or method gets its own unit
- [ ] Each numerical/geometric property gets its own unit
- [ ] Each classification result gets its own unit
- [ ] Each connection between theories gets its own unit
- [ ] Each historical/motivational context gets its own unit

#### **STEP 3: Extract with Perfect Fidelity**
- Copy paper text **EXACTLY** - no modifications
- Record precise line numbers for EACH unit
- Identify all LaTeX labels and citations
- Note surrounding mathematical context

#### **STEP 4: Document All Notation Issues**
- **Scan for undefined LaTeX macros**: `\cL`, `\bZ`, `\sH`, etc.
- **Identify context-dependent variables**: What does `Z`, `S`, `X` represent?
- **Research macro meanings**: Check paper preamble, math conventions, educated guesses
- **Document mathematical context**: Use surrounding text to determine variable meanings
- **Note author conventions**: Any paper-specific notational systems

#### **STEP 5: Plan Thesis Expansion**
- Identify what paper omitted due to space
- Suggest detailed explanations needed
- Plan complete proof development
- Outline pedagogical improvements

#### **STEP 5.5: ⚠️ CRITICAL - Create Line-by-Line Formalization-Ready Proof**
- **REQUIREMENT**: Every mathematical step must have explicit justification
- **CITATIONS**: Each step must cite specific theorems, Stacks tags, Mathlib proofs, or textbook sections
- **NO GAPS**: Proof must be complete enough for seasoned Lean programmer to formalize
- **ASSUMPTIONS**: All assumptions must be explicitly stated
- **REJECTION**: Entire logical unit will be rejected if proof has gaps or incorrect steps

#### **STEP 6: Create Initial YAML for ALL Units**
```yaml
logical_units:
  - unit_id: "k3_lattice_involutions"
    unit_type: "theorem"
    thesis_title: "Classification of K3 Lattice Involutions"
    dependencies: ["lattice_basics", "nikulin_theory"]

    paper_source:
      file_path: "writing/sources/en.tex"
      start_line: 520
      end_line: 540
      verbatim_content: |
        \begin{theorem}\label{thm:k3_involutions}
        The K3 lattice $\Lambda$ admits exactly three types of involutions...
        \end{theorem}
      latex_labels: ["thm:k3_involutions"]
      paper_citations: ["Nikulin1980"]

    notation_explanations:
      latex_macros:
        "\\Lambda": "\\Lambda (K3 lattice - standard notation from paper introduction)"
        "\\cL": "\\mathcal{L} (script L - line bundle from paper Section 1.2)"
        "\\bZ": "\\mathbb{Z} (integers - blackboard bold)"
      mathematical_context:
        "Lambda": "The K3 lattice with signature (3,19) as defined in Section 1.1"
        "involution": "Isometry sigma: Lambda -> Lambda with sigma^2 = id"
        "type": "Classification by fixed sublattice structure (from Nikulin theory)"
      ambiguous_notation: {}
      author_conventions:
        "lattice_notation": "Author uses Lambda for K3 lattice throughout, not standard H notation"

    thesis_content:
      condensed_summary: |
        This theorem classifies all possible involutions on the K3 lattice,
        building on Nikulin's classification theory for even lattices.
      detailed_analysis: |
        The paper provides only the classification statement. For the thesis,
        we need complete background on lattice theory, detailed construction
        of each involution type, and geometric interpretation.
      expansion_notes: |
        Paper omitted: (1) Nikulin theory background, (2) explicit constructions,
        (3) geometric realizability proofs, (4) examples and computations.

    proof_development:
      paper_proof_content: |
        "The result follows from Nikulin's classification [Nik80]."
      thesis_proof_outline: |
        1. Review Nikulin classification for even lattices
        2. Apply to K3 lattice specifically
        3. Construct each involution type explicitly
        4. Verify geometric realizability
      rigorous_proof: |
        [Complete proof would be developed here with all details]
      line_by_line_proof:
        - step: 1
          statement: "Let Λ be the K3 lattice with signature (3,19)"
          justification: "K3 lattice is standard lattice for K3 surfaces with signature (3,19)"
          citations: ["Barth-Hulek-Peters-Van de Ven Section VIII.3", "Dolgachev-Kondō Theorem 1.2.1"]
          assumptions: ["Standard definition of K3 lattice"]
        - step: 2
          statement: "Λ is an even, indefinite lattice of rank 22"
          justification: "Direct from definition and signature computation"
          citations: ["Milnor-Husemoller Chapter I.4", "Stacks Tag 0DXX"]
          assumptions: ["Basic lattice theory"]
        - step: 3
          statement: "Apply Nikulin classification for even lattices with involutions"
          justification: "Nikulin 1980 classifies all possible involutions on even indefinite lattices"
          citations: ["Nikulin 1980 Theorem 4.2", "Dolgachev-Kondō Section 4.1"]
          assumptions: ["Λ satisfies conditions for Nikulin classification"]
      proof_references: ["Nikulin1980", "Dolgachev-Kondo2016"]

    audits:
      - audit_id: "initial_extraction"
        auditor_role: "extractor"
        audit_date: "2025-01-06T10:30:00Z"
        suspicion_scores:
          source_fidelity: 1.0
          mathematical_accuracy: 1.0
          citation_validity: 1.0
          proof_correctness: 1.0
          expansion_quality: 1.0
        audit_notes: |
          Initial extraction completed. All content requires verification.
          Particular attention needed for Nikulin classification claims.
```

---

## 🔍 STAGE 2: AUDITOR ROLE

### **PRIMARY MISSION**
Serve as gatekeepers against false information through independent verification of all extractor claims.

### **AUDITOR RESPONSIBILITIES**
1. **Source Verification**: Independently confirm paper extraction accuracy
2. **Mathematical Validation**: Verify all mathematical claims and proofs
3. **⚠️ CRITICAL: Line-by-Line Proof Verification**: Validate every step, citation, and assumption in formalization-ready proofs
4. **Citation Checking**: Confirm all references exist and support claims
5. **Quality Assessment**: Evaluate thesis expansion appropriateness
6. **Evidence Documentation**: Record verification work and update suspicion scores

### **AUDITOR WORKFLOW**

#### **PHASE 1: Source Document Verification**
1. Retrieve `writing/sources/en.tex`
2. Navigate to claimed line numbers
3. Compare character-by-character with verbatim content
4. Verify LaTeX labels exist and are correct
5. Check surrounding context for consistency

#### **PHASE 2: Mathematical Content Validation**
1. Verify mathematical objects are well-defined
2. Check proof logic step-by-step
3. Confirm claims against standard references
4. Validate computational statements
5. Cross-check with multiple authoritative sources

#### **PHASE 2.5: Notation Verification**
1. **Verify macro translations**: Check if `\cL = \mathcal{L}` interpretations are reasonable
2. **Validate mathematical context**: Confirm variable meanings align with mathematical context
3. **Cross-check author conventions**: Look for consistency in notation usage throughout paper
4. **Flag notation gaps**: Identify any undefined notation that extractor missed
5. **Verify disambiguation**: Check that ambiguous notation has been properly clarified

#### **PHASE 3: Citation and Reference Verification**
1. Search MathSciNet/zbMATH for each citation
2. Retrieve papers where possible
3. Verify citations support the claims made
4. Check bibliographic accuracy
5. Cross-reference with Google Scholar

#### **PHASE 3.5: ⚠️ CRITICAL - Line-by-Line Proof Validation**
1. **Step-by-Step Verification**: Check every statement and justification
2. **Citation Validation**: Verify each cited theorem/lemma actually exists and supports the step
3. **Assumption Tracking**: Confirm all assumptions are explicit and valid
4. **Gap Detection**: Identify any logical gaps that would prevent Lean formalization
5. **Formalization Readiness Test**: Assess if proof is detailed enough for formal verification

#### **PHASE 4: Evidence-Based Suspicion Update**
Update suspicion scores ONLY with substantial evidence:

```yaml
# Auditor appends new audit record - NEVER modifies extractor content
audits:
  - audit_id: "independent_verification_001"
    auditor_role: "auditor"
    audit_date: "2025-01-07T14:22:00Z"

    suspicion_scores:
      source_fidelity: 0.05     # REDUCED after character-by-character verification
      mathematical_accuracy: 0.15  # REDUCED after reference checking
      citation_validity: 0.08   # REDUCED after MathSciNet verification
      proof_correctness: 0.60   # REMAINS HIGH - proof sketch needs work
      formalization_readiness: 0.15  # REDUCED after line-by-line verification
      expansion_quality: 0.25   # REDUCED after pedagogical review

    audit_notes: |
      VERIFICATION COMPLETED:
      - Source extraction verified character-by-character ✓
      - Mathematical claims cross-checked with Dolgachev-Kondō ✓
      - Nikulin 1980 citation verified in MathSciNet ✓
      - Line-by-line proof citations validated for steps 1-3 ✓
      - Each proof step has explicit justification ✓
      - Proof development plan assessed as appropriate ✓

      REMAINING CONCERNS:
      - Paper proof is minimal sketch requiring substantial development
      - Geometric realizability claims need expert mathematical review
      - Line-by-line proof needs completion for all steps of full theorem

    evidence_gathered: |
      SOURCE VERIFICATION:
      Retrieved en.tex and compared lines 520-540 with claimed verbatim content.
      Found exact match except minor LaTeX spacing differences.

      MATHEMATICAL VERIFICATION:
      Cross-checked K3 lattice signature (3,19) in Barth-Hulek-Peters-Van de Ven.
      Verified Nikulin classification applies to indefinite even lattices.

      CITATION VERIFICATION:
      Confirmed Nikulin 1980 "Finite groups of automorphisms..." exists.
      Verified it contains lattice involution classification in Section 4.

      LINE-BY-LINE PROOF VERIFICATION:
      Validated citations for proof steps 1-3:
      - Step 1: Barth-Hulek-Peters-Van de Ven Section VIII.3 confirmed ✓
      - Step 2: Milnor-Husemoller Chapter I.4 verified ✓
      - Step 3: Nikulin 1980 Theorem 4.2 exists and applicable ✓
      Each step has explicit statement, justification, and assumptions.
```

### **SUSPICION SCORING GUIDELINES**

**Philosophy**: Start at maximum suspicion (1.0), reduce only with substantial evidence.

- **1.0 → 0.3**: Basic verification completed
- **0.3 → 0.1**: Thorough cross-checking with multiple sources
- **0.1 → 0.05**: Expert review confirms accuracy

**Score Meanings**:
- **0.90-1.0**: Unverified, assume incorrect
- **0.50-0.89**: Partially verified, significant concerns remain
- **0.10-0.49**: Well-verified, minor concerns only
- **0.01-0.09**: Thoroughly verified, high confidence
- **0.00**: Perfect verification (rarely achievable)

---

## 📋 QUALITY CONTROL STANDARDS

### **EXTRACTOR SUCCESS CRITERIA**
- ✅ Perfect source traceability (exact line numbers)
- ✅ Verbatim paper content (zero modifications)
- ✅ **Granular extraction (15-25 units for Introduction section)**
- ✅ **Each unit represents single mathematical concept/technique/result**
- ✅ **Complete notation documentation (all macros and variables explained)**
- ✅ Comprehensive expansion planning
- ✅ Complete YAML structure conformance
- ✅ All suspicion scores initialized to 1.0

### **GRANULARITY SUCCESS INDICATORS**
- ✅ **Volume**: Introduction should yield 15-25 units, not 3-8
- ✅ **Density**: Target 5-8 units per source page (use formula: page count × 5-8)
- ✅ **Specificity**: Each unit title describes one specific concept
- ✅ **SeparATION**: Different mathematical objects/properties in separate units
- ✅ **Completeness**: Every sentence with mathematical content gets a unit
- ✅ **Thesis-ready**: Each unit can be developed into a solid paragraph to half a page (0.2-0.5 thesis pages)

### **DENSITY VALIDATION CHECKLIST**

**Choose your input metric and calculate target:**

**Option A - FROM LINES:**
- [ ] **Count LaTeX lines**: `end_line - start_line + 1`
- [ ] **Quick target**: Lines ÷ 8 ≈ target units
- [ ] **Range check**: Lines ÷ 6 to lines ÷ 9

**Option B - FROM WORDS:**
- [ ] **Count words**: `wc -w filename` or visual estimate
- [ ] **Quick target**: Words ÷ 30 ≈ target units
- [ ] **Range check**: Words ÷ 23 to words ÷ 37

**Option C - FROM PAGES:**
- [ ] **Estimate pages**: Lines ÷ 45 or words ÷ 187
- [ ] **Quick target**: Pages × 6 ≈ target units
- [ ] **Range check**: Pages × 5 to pages × 8

**Final validation:**
- [ ] **Verify minimum**: At least 4 units per source page
- [ ] **Check maximum**: No more than 20 units per source page
- [ ] **Quality check**: Each unit represents distinct mathematical concept
- [ ] **Granularity check**: No unit covers more than 45 lines or 187 words

### **AUDITOR SUCCESS CRITERIA**
- ✅ Independent verification of all claims
- ✅ Substantial evidence for any suspicion reduction
- ✅ Mathematical accuracy confirmed through multiple sources
- ✅ Citation verification with primary sources
- ✅ Detailed evidence documentation

### **REJECTION CRITERIA**
Immediately reject logical units with:
- ❌ Source extraction errors (content doesn't match paper)
- ❌ Mathematical errors discovered in verification
- ❌ Invalid citations or unsupported claims
- ❌ Incomplete YAML structure
- ❌ Insufficient verification evidence
- ❌ **CRITICAL: Undefined notation without explanations**
- ❌ **CRITICAL: Incorrect macro translations or variable interpretations**
- ❌ **CRITICAL: Gaps or logical errors in line-by-line proof**
- ❌ **CRITICAL: Missing citations for any step in line-by-line proof**
- ❌ **CRITICAL: Line-by-line proof not detailed enough for Lean formalization**

---

## ⚠️ FORMALIZATION REQUIREMENTS FOR LINE-BY-LINE PROOFS

### **LEAN-READY PROOF STANDARDS**
Every line-by-line proof MUST meet these criteria or face immediate rejection:

#### **1. COMPLETE JUSTIFICATION**
- Every mathematical step has explicit reasoning
- No "it follows that..." or "clearly..." without proof
- Every implication must be justified with specific citations

#### **2. EXPLICIT CITATIONS**
- **Theorems**: "Theorem X.Y in AuthorYear" or "Paper Title Theorem X.Y"
- **Stacks Project**: "Stacks Tag XXXX" with specific tag number
- **Mathlib**: "Mathlib.Category.Theory.theorem_name" with exact path
- **Textbooks**: "Author Book Name Chapter X.Y Theorem Z"

#### **3. ASSUMPTION TRACKING**
- List all assumptions used in each step
- Distinguish between given hypotheses and intermediate results
- Make implicit mathematical assumptions explicit

#### **4. FORMALIZATION TEST**
Each proof must pass this test:
> "Could a seasoned Lean programmer take this line-by-line proof and formalize it in Lean without needing to fill in mathematical gaps?"

If the answer is NO, the entire logical unit is REJECTED.

#### **5. EXAMPLE CITATION FORMATS**
```yaml
citations:
  - "Hartshorne Algebraic Geometry Chapter II Proposition 5.17"
  - "Vakil Foundations of Algebraic Geometry Theorem 12.2.1"
  - "Stacks Tag 02V1"
  - "Mathlib.RingTheory.Ideal.Quotient.is_prime_iff_prime_of_surjective"
  - "Nikulin 1980 Finite Groups of Automorphisms Theorem 4.2"
  - "Dolgachev-Kondō Mirror Symmetry Section 4.1 Lemma 4.1.3"
```

---

## 🚀 COMPLETE WORKFLOW SUMMARY

```
1. EXTRACTOR locates paper content at specific lines
   ↓
2. ⚠️ EXTRACTOR calculates density target (pages × 5-8 units/page)
   ↓
3. ⚠️ EXTRACTOR identifies ALL granular units (meet density target)
   ↓
4. ⚠️ EXTRACTOR documents ALL notation issues (macros, variables, conventions)
   ↓
5. EXTRACTOR creates YAML with verbatim extraction + notation explanations + expansion plan
   ↓
6. ⚠️ EXTRACTOR creates line-by-line formalization-ready proof with citations
   ↓
7. EXTRACTOR sets all suspicion scores to 1.0 (maximum suspicion)
   ↓
8. AUDITOR independently verifies paper source accuracy
   ↓
9. AUDITOR validates mathematical content against references
   ↓
10. ⚠️ AUDITOR verifies all notation translations and variable interpretations
    ↓
11. ⚠️ AUDITOR validates every step in line-by-line proof
    ↓
12. AUDITOR checks all citations and claims
    ↓
13. AUDITOR updates suspicion scores with evidence
    ↓
14. VERIFIED LOGICAL UNITS ready for thesis integration
```

**RESULT**: High-confidence, verified content ready for thesis with complete source traceability and mathematical accuracy. 🎯

---

## 🎓 IMPLEMENTATION NOTES

### **File Naming Convention**
- Extractor output: `CH3_EXTRACTED_[date].yaml`
- Auditor output: `CH3_VERIFIED_[date].yaml`
- Final verified: `CH3_LOGICAL_UNITS.yaml`

### **Dependencies Management**
- Map dependencies to specific sections/theorems in paper
- Verify dependency chain is acyclic
- Document external dependencies (other chapters, literature)

### **Version Control**
- Commit each extraction phase separately
- Tag verified milestones
- Maintain audit trail in git history

**CRITICAL**: Follow this canonical format exactly. Any deviation will compromise the verification system and thesis quality control.

---

## 📋 QUICK REFERENCE: DENSITY TARGETS

### **⚡ INSTANT FORMULAS**
- **Lines → Units**: `lines ÷ 8` (rule of thumb)
- **Words → Units**: `words ÷ 30` (rule of thumb)
- **Pages → Units**: `pages × 6` (rule of thumb)

### **📊 QUALITY BENCHMARKS**
- **❌ Too sparse**: >45 lines/unit OR >187 words/unit
- **⚠️ Minimum**: 9-11 lines/unit OR 37-47 words/unit
- **✅ Good**: 6-9 lines/unit OR 23-37 words/unit
- **🎯 Excellent**: 3-6 lines/unit OR 12-23 words/unit

### **🔢 EMPIRICAL CONVERSION RATES**
- **45 LaTeX lines = 1 source page**
- **187 words = 1 source page**
- **8.5 lines = 1 logical unit** (good quality)
- **35 words = 1 logical unit** (good quality)

### **📈 TARGET RANGES BY SECTION TYPE**
- **Introduction sections**: 18-29 units per ~3.6 pages
- **Setup sections**: 30-50 units per ~6-8 pages
- **Technical sections**: 50-80 units per ~8-12 pages
- **Proof sections**: 80-120 units per ~10-15 pages
