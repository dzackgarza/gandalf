from textwrap import dedent

# It's a good practice to have the canonical YAML structure and guidelines available
# to the prompt, or at least the parts the LLM needs to generate the output.

# For complex models and large contexts, you can include more of the original spec.
# For smaller context windows, you might need to be more selective.

# Let's define the core parts of the YAML structure as a string to be included in the prompt.
# This should be kept in sync with your Pydantic models.
# Note: In a real-world scenario with very large schemas, you might provide a URL
# or a summarized version. For this task, including it directly is feasible.

CANONICAL_YAML_STRUCTURE_SNIPPET = """
The output MUST be a YAML object with a single top-level key `logical_units`.
`logical_units` is a list of objects, each representing a single logical unit.

Each logical unit object MUST have the following structure:

  - # === UNIT IDENTIFICATION ===
    unit_id: "unique_snake_case_identifier"        # REQUIRED: snake_case ID (e.g., "enriques_surface_definition")
    unit_type: "theorem"                           # REQUIRED: one of [theorem, lemma, definition, proposition, example, remark]
    thesis_title: "Descriptive Title for Thesis"   # REQUIRED: Clear heading for thesis
    dependencies: ["unit_id_1", "unit_id_2"]       # REQUIRED: List of unit_ids this unit depends on (empty list if none)

    # === SOURCE TRACEABILITY ===
    paper_source:
      file_path: "source_markdown_filename.md"     # REQUIRED: The filename of the input markdown document
      start_line: 123                              # REQUIRED: Exact start line in the source markdown (estimate if not precise)
      end_line: 145                                # REQUIRED: Exact end line in the source markdown (estimate if not precise)
      verbatim_content: |                          # REQUIRED: Exact markdown text for this logical unit
        [WORD-FOR-WORD content from the markdown segment corresponding to this unit - NEVER modify]
      latex_labels: ["label1", "label2"]           # OPTIONAL: Any LaTeX labels found within this verbatim content
      paper_citations: ["CiteKey1999"]             # OPTIONAL: Any citation keys (e.g., BibTeX keys) found

    # === NOTATION TRANSLATION ===
    notation_explanations:                         # REQUIRED: Document all paper notation relevant to this unit
      latex_macros:                                # REQUIRED: (can be empty if none relevant to this specific unit)
        "\\\\cL": "\\\\mathcal{L} (script L - likely line bundle or sheaf)"
      mathematical_context:                        # REQUIRED: (can be empty if none relevant to this specific unit)
        "Z": "Scheme or variety (as used in this unit's context)"
      ambiguous_notation:                          # OPTIONAL
        "H^2": "Could be cohomology or Hilbert scheme - verify"
      author_conventions:                          # OPTIONAL
        "convention_name": "Description of convention"

    # === THESIS EXPANSION ===
    thesis_content:
      condensed_summary: |                         # REQUIRED: Brief overview (1-2 paragraphs) of this logical unit
        [Summary]
      detailed_analysis: |                         # REQUIRED: Comprehensive explanation for a thesis
        [Detailed analysis]
      expansion_notes: |                           # REQUIRED: What needs expansion from the paper's version of this unit
        [Expansion notes]

    # === PROOF OBJECTS (Required for unit_type: theorem|lemma|proposition only) ===
    proof_development:                             # Null if not theorem, lemma, or proposition
      paper_proof_content: |                       # REQUIRED if proof_development is present
        [Exact proof from paper, if any, for this unit]
      thesis_proof_outline: |                      # REQUIRED if proof_development is present
        [Step-by-step outline for complete thesis proof]
      rigorous_proof: |                            # REQUIRED if proof_development is present
        [Fully detailed proof suitable for thesis examination]
      line_by_line_proof:                          # REQUIRED if proof_development is present
        - step: 1
          statement: "[Mathematical statement for this step]"
          justification: "[Complete justification with specific citations]"
          citations: ["Theorem X.Y in Paper1999", "Stacks Tag 02AB"]
          assumptions: "[Any assumptions used in this step]"
        # ... more steps
      proof_references: ["Source1", "Source2"]     # REQUIRED if proof_development is present

    # === VERIFICATION TRAIL ===
    audits:                                        # REQUIRED: Must contain at least one audit entry
      - audit_id: "extractor_initial_YYYYMMDDHHMMSS_randomsuffix" # REQUIRED: Unique audit identifier (append timestamp and random chars)
        auditor_role: "extractor"                  # REQUIRED: "extractor"
        audit_date: "YYYY-MM-DDTHH:MM:SSZ"         # REQUIRED: ISO timestamp of extraction
        suspicion_scores:                          # REQUIRED
          source_fidelity: 1.0
          mathematical_accuracy: 1.0
          citation_validity: 1.0
          proof_correctness: 1.0
          formalization_readiness: 1.0
          expansion_quality: 1.0
        audit_notes: |                            # REQUIRED
          Initial extraction by LLM. All content generated based on the input document and instructions.
          All fields require human verification.
        evidence_gathered: ""                     # OPTIONAL: (leave empty for initial extraction)
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
