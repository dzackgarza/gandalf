from textwrap import dedent

# It's a good practice to have the canonical YAML structure and guidelines available
# to the prompt, or at least the parts the LLM needs to generate the output.

# For complex models and large contexts, you can include more of the original spec.
# For smaller context windows, you might need to be more selective.

# Let's define the core parts of the YAML structure as a string to be included in the prompt.
# This should be kept in sync with your Pydantic models.

CANONICAL_YAML_STRUCTURE_SNIPPET = """
The output MUST be a YAML object with a single top-level key `logical_units`.
`logical_units` is a list of objects, each representing a single logical unit.
ALL REQUIRED fields MUST be present and contain meaningful, non-empty content unless the schema explicitly allows them to be empty (e.g., an empty list `[]` for `dependencies` if none). Do not use placeholder text like "[Summary]" for required multi-line string fields; generate actual content.

Each logical unit object MUST have the following structure:

  - # === UNIT IDENTIFICATION ===
    unit_id: "unique_snake_case_identifier"        # REQUIRED: snake_case ID (e.g., "enriques_surface_definition")
    unit_type: "theorem"                           # REQUIRED: one of [theorem, lemma, definition, proposition, example, remark]
    thesis_title: "Descriptive Title for Thesis"   # REQUIRED: Clear heading for thesis. Must be a non-empty string.
    dependencies: ["unit_id_1", "unit_id_2"]       # REQUIRED: List of unit_ids this unit depends on (empty list `[]` if none)

    # === SOURCE TRACEABILITY ===
    paper_source:
      file_path: "source_markdown_filename.md"     # REQUIRED: The filename of the input document.
      start_line: 123                              # REQUIRED: Estimated start line in the (potentially converted) markdown.
      end_line: 145                                # REQUIRED: Estimated end line in the (potentially converted) markdown.
      verbatim_content: |                          # REQUIRED: Exact markdown text for this logical unit. Must be non-empty.
        This is an example of verbatim content that would be extracted for a logical unit.
        It should be copied word-for-word from the (potentially converted) input.
      latex_labels: ["label1", "label2"]           # OPTIONAL: Any LaTeX labels found within this verbatim content (e.g. ["thm:main", "eq:identity"])
      paper_citations: ["CiteKey1999"]             # OPTIONAL: Any citation keys (e.g. BibTeX keys like ["Author2021"]) found

    # === NOTATION TRANSLATION ===
    notation_explanations:                        # REQUIRED: Document all paper notation relevant to THIS unit.
      latex_macros:                               # REQUIRED: (can be empty dict `{}` if none relevant)
        "\\\\mathcal{F}_b": "Represents a Foo Bar structure."
        "\\\\mathbb{K}": "Represents a field."
      mathematical_context:                       # REQUIRED: (can be empty dict `{}` if none relevant)
        "S": "The non-empty set component of a Foo Bar, as used in this unit's verbatim_content."
        "lambda_0": "The base foo element in a Foo Bar."
      ambiguous_notation:                         # OPTIONAL (empty dict `{}` if none)
        "phi": "A canonical map, its specific definition needs to be clarified from context."
      author_conventions:                         # OPTIONAL (empty dict `{}` if none)
        "foo_bar_tuple_order": "The paper uses (S, op1, op2, base) for Foo Bar tuples."

    # === THESIS EXPANSION ===
    thesis_content:                               # REQUIRED: All sub-fields must be non-empty, well-developed textual content.
      condensed_summary: |                        # REQUIRED: Brief overview (1-2 paragraphs) of this logical unit.
        Example: This unit defines the Foo Bar, a mathematical structure consisting of a set, two operations (foo-addition and bar-multiplication over a field K), and a base foo element. These components must satisfy specific axioms.
      detailed_analysis: |                        # REQUIRED: Comprehensive explanation suitable for a thesis.
        Example: The Foo Bar, denoted as $\mathcal{F}_b$, is formally defined as a tuple $(\mathcal{S}, \oplus, \otimes, \lambda_0)$. The set $\mathcal{S}$ provides the domain for the structure. Foo-addition, $\oplus$, is an internal binary operation on $\mathcal{S}$, required to be associative. Bar-multiplication, $\otimes$, defines a scalar multiplication action of the field $\mathbb{K}$ on the set $\mathcal{S}$. The element $\lambda_0 \in \mathcal{S}$ serves as a foundational point or origin for constructions within the Foo Bar. The interplay of these components under Axioms F1-F3 gives rise to the unique characteristics of Foo Bars, distinguishing them from other algebraic structures like groups or vector spaces by their specific operational semantics and the role of the base foo.
      expansion_notes: |                          # REQUIRED: What needs expansion from the paper's version of this unit for a thesis.
        Example: For a thesis, Axioms F1-F3 must be explicitly stated and their implications discussed. The relationship between Foo Bars and existing algebraic structures (e.g., modules, algebras) should be elaborated. Provide concrete examples of Foo Bars over different fields (e.g., $\mathbb{R}$, $\mathbb{C}$, $\mathbb{F}_p$) to illustrate varying properties. Discuss the motivation behind the 'base foo' concept.

    # === PROOF OBJECTS (Required for unit_type: theorem|lemma|proposition only. Otherwise, this whole `proof_development` key should be null or absent) ===
    proof_development:                            # Null or absent if not a proof-bearing unit type.
      paper_proof_content: |                      # REQUIRED if proof_development is present. Non-empty.
        Example: The paper states: "The proof relies on Zorn's Lemma and the Bar Homomorphism Lemma."
      thesis_proof_outline: |                     # REQUIRED if proof_development is present. Non-empty.
        Example:
        1. Define the set of proto-Baz Foos and establish a partial ordering.
        2. Apply Zorn's Lemma to show existence of a maximal element.
        3. Prove this maximal element is a Baz Foo, $\beta_c$.
        4. For uniqueness, assume two Baz Foos $\beta_1^*$ and $\beta_2^*$.
        5. Define Bar Homomorphisms and state the Bar Homomorphism Lemma.
        6. Apply the lemma to show $\beta_1^* = \beta_2^*$.
      rigorous_proof: |                           # REQUIRED if proof_development is present. Non-empty detailed proof.
        Example: Let $P$ be the set of all proto-Baz Foos in $\mathcal{S}$, ordered by inclusion. $P$ is non-empty as... [continues for several paragraphs with full mathematical rigor] ...thus establishing $\beta_1^* = \beta_2^*$. Q.E.D.
      line_by_line_proof:                         # REQUIRED if proof_development is present. Non-empty list.
        - step: 1
          statement: "Define $P = \{x \in \mathcal{S} \mid x \text{ is a proto-Baz Foo}\}$. Order $P$ by foo-inclusion $\preceq$."
          justification: "Standard construction for applying Zorn's Lemma to existence proofs in algebraic structures."
          citations: ["Abstract Algebra, Dummit and Foote, Ch. 7.4", "Internal Paper Definition 2.5 for proto-Baz Foo"]
          assumptions: "The set $\mathcal{S}$ and its operations satisfy Foo Bar axioms F1-F3. Field $\mathbb{K}$ is algebraically closed, char 0."
        - step: 2
          statement: "Show every chain in $(P, \preceq)$ has an upper bound in $P$."
          justification: "The union of a chain of proto-Baz Foos can be shown to be a proto-Baz Foo itself."
          citations: [] # If justification is self-contained for this step based on prior definitions
          assumptions: "Standard properties of set unions and defined properties of proto-Baz Foos."
        # ... more steps for existence and uniqueness
      proof_references: ["DummitAndFoote2004", "AppendixA_BarHomomorphisms"]     # REQUIRED if proof_development is present. List of key biblio references.

    # === VERIFICATION TRAIL ===
    audits:                                       # REQUIRED: Must contain at least one audit entry.
      - audit_id: "extractor_initial_YYYYMMDDHHMMSS_xyz" # REQUIRED: Unique ID (e.g., 'extractor_initial_' + timestamp + 3 random chars).
        auditor_role: "extractor"                  # REQUIRED: Must be "extractor".
        audit_date: "YYYY-MM-DDTHH:MM:SSZ"         # REQUIRED: Current ISO 8601 timestamp of extraction (e.g., "2024-07-28T12:30:00Z").
        suspicion_scores:                          # REQUIRED. All scores must be 1.0 for initial extraction.
          source_fidelity: 1.0
          mathematical_accuracy: 1.0
          citation_validity: 1.0
          proof_correctness: 1.0
          formalization_readiness: 1.0
          expansion_quality: 1.0
        audit_notes: |                             # REQUIRED. Non-empty.
          Initial extraction by LLM. All content generated based on the input document and system instructions. All fields require human verification and subsequent audit.
        evidence_gathered: ""                      # OPTIONAL: (leave empty string "" for initial extraction)
"""

GRANULARITY_GUIDELINES_SNIPPET = """
GRANULARITY GUIDELINES:
- PREFER OVER-EXTRACTION TO UNDER-EXTRACTION.
- Each logical unit should represent ONE specific mathematical concept, technique, or result.
- Aim for units developable into a solid paragraph to half a page (0.2-0.5 thesis pages).
- CREATE SEPARATE UNITS for:
    - Different mathematical objects (surfaces vs. moduli spaces).
    - Different properties of the same object (numerical invariants vs. geometric properties).
    - Different techniques or methods.
    - Different types of results (existence vs. uniqueness).
    - Supporting lemmas vs. main theorems.
    - Definitions, examples, remarks should typically be their own units.
- EXTRACTION TARGETS (approximate per source paper section, adjust for markdown):
    - Introduction: 15-25 units
    - Technical sections: 20-35 units
    - Proof sections: 25-40 units
- DENSITY: Aim for 5-8 units per "page" of content (approx. 45 lines or 187 words of dense academic text).
  A typical markdown section of a few hundred words should yield multiple units.
  For example, a 600-word section might yield 15-25 units.

NOTATION HANDLING:
- For each unit, identify relevant notation.
- `latex_macros`: Explain any non-standard LaTeX macros used in the `verbatim_content` of THIS unit.
- `mathematical_context`: Explain variables/symbols specific to THIS unit's `verbatim_content`.
- If `verbatim_content` for a unit is e.g. "Define Enriques surfaces", the notation section should explain symbols used in that definition.

PROOF DEVELOPMENT:
- If a unit is a theorem, lemma, or proposition, the `proof_development` section is MANDATORY.
- `paper_proof_content`: Extract any proof sketch or argument from the source markdown for THIS unit. If none, state "No proof provided in source for this unit."
- `thesis_proof_outline`: Provide a detailed step-by-step outline for a rigorous thesis proof.
- `rigorous_proof`: Write out the full, detailed proof.
- `line_by_line_proof`: Formalize the proof with explicit steps, justifications, citations (use placeholder citations if exact ones are not in source, e.g., "Standard result from [Field]", but be specific if possible), and assumptions. Each step MUST have a statement, justification, and assumptions. Citations list can be empty if justification is self-contained for that step.
- `proof_references`: List key external references needed for the proof.

AUDIT TRAIL:
- For each logical unit, you MUST generate one initial audit entry.
- `audit_id`: Create a unique ID, e.g., "extractor_initial_" + current timestamp + random string.
- `auditor_role`: Set to "extractor".
- `audit_date`: Current ISO 8601 timestamp (e.g., "2025-01-06T10:30:00Z").
- `suspicion_scores`: All scores MUST be initialized to 1.0.
- `audit_notes`: Use a standard note like "Initial extraction by LLM. All content generated based on input document and instructions. All fields require human verification."
"""

def get_system_prompt() -> str:
    return dedent(f"""
        You are an expert in mathematical document analysis and structured data extraction.
        Your task is to process a given mathematics markdown document and extract "logical units" according to very specific guidelines and a strict YAML output format.
        You must adhere to the granularity guidelines, ensuring that each unit is focused and appropriately sized.
        Pay extremely close attention to all REQUIRED fields in the YAML structure. Do not omit any.
        If a list can be empty (e.g., dependencies, latex_labels), use an empty list `[]` rather than omitting the key.
        If a section like `proof_development` is not applicable for a `unit_type` (e.g., 'remark', 'definition'), it should be `null` or omitted if the schema allows (the provided schema implies it can be null).

        **CRITICAL YAML STRUCTURE TO FOLLOW:**
        {CANONICAL_YAML_STRUCTURE_SNIPPET}

        **CRITICAL EXTRACTION GUIDELINES:**
        {GRANULARITY_GUIDELINES_SNIPPET}

        Process the entire input document. Identify all logical units.
        For each unit, meticulously fill in all required fields.
        The `verbatim_content` for each unit must be an exact segment from the source markdown. Try to infer reasonable start/end lines.
        The `unit_id` must be unique for each unit and in snake_case. Generate it from the unit's content or title.
        The `thesis_title` should be descriptive and suitable for a thesis chapter.
        `dependencies` should list `unit_id`s of other units that are prerequisites for understanding this unit. If a unit defines a term used in another, the latter depends on the former.

        You will be provided with the full markdown content and its filename.
        Ensure the `paper_source.file_path` correctly reflects the provided filename.
        Generate `audit_date` and `audit_id` dynamically for each unit's initial audit record.

        You will be provided with the textual content to process (which will be in Markdown format, possibly converted from another source like LaTeX) and the original source filename.
        The `paper_source.file_path` field in your YAML output MUST always refer to this original source filename.
        The `verbatim_content`, `start_line`, and `end_line` fields under `paper_source` should refer to the processed Markdown content that you are directly analyzing.
        If the original source was TeX, these line numbers will refer to the converted Markdown representation, not the original TeX file.
    """).strip()

def get_user_prompt(markdown_content: str, source_filename: str) -> str: # markdown_content here is the content for LLM (already converted if original was TeX)
    return dedent(f"""
        Please process the following textual content from original source file '{source_filename}'.
        The content below is in Markdown format (it may have been converted from another format like TeX).
        Extract all logical units according to the system instructions and guidelines.
        Output the result as a single YAML object adhering strictly to the specified format.

        Markdown Filename: {source_filename}

        Markdown Content:
        ```markdown
        {markdown_content}
        ```

        Remember to:
        1.  Identify granular logical units.
        2.  For each unit, extract/generate all REQUIRED fields as per the YAML structure.
        3.  Pay special attention to `proof_development` for theorems, lemmas, propositions.
        4.  Generate a unique `unit_id` (snake_case) for each unit.
        5.  Populate the initial `audits` record for each unit with all scores at 1.0.
        6.  Ensure `paper_source.file_path` is "{source_filename}".
        7.  `verbatim_content` must be copied exactly from the markdown for that unit.
        8.  Estimate `start_line` and `end_line` for each unit within the source markdown.
    """).strip()

if __name__ == '__main__':
    system_prompt = get_system_prompt()
    print("----- SYSTEM PROMPT -----")
    print(system_prompt)

    sample_markdown = """
# Chapter 1: Introduction to Frobnitz Theory

This chapter introduces the fundamental concepts of Frobnitz theory.

## 1.1 Definition of a Frobnitz

A **Frobnitz** is defined as a widget that exhibits schmangaroo properties.
Let $F$ be a Frobnitz. We denote its schmangaroo by $\\mathcal{S}(F)$.
This concept was first introduced in [Author2021].

## 1.2 Theorem: Frobnitz Existence

**Theorem 1.2.1.** Under conditions $C_1$ and $C_2$, a Frobnitz exists.

*Proof Sketch.*
The proof relies on constructing a Schmangaroo manifold and showing it's non-empty.
Details can be found in [Author2021, Theorem 3.4].
QED.

## 1.3 Example: The Trivial Frobnitz

Consider a widget where $\\mathcal{S}(F) = 0$. This is the trivial Frobnitz.
It is not very interesting.

"""
    user_prompt = get_user_prompt(sample_markdown, "sample_chapter.md")
    print("\n----- USER PROMPT -----")
    print(user_prompt)

    # Test that snippets are included
    assert "unit_id: \"unique_snake_case_identifier\"" in system_prompt
    assert "PREFER OVER-EXTRACTION TO UNDER-EXTRACTION" in system_prompt
    assert "Markdown Filename: sample_chapter.md" in user_prompt
    assert "Frobnitz is defined as a widget" in user_prompt
    print("\nPrompts generated and basic checks passed.")
