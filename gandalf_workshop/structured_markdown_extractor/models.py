from typing import List, Optional, Dict, Literal, Union
from pydantic import BaseModel, Field, field_validator, RootModel
import re
from datetime import datetime

class PaperSource(BaseModel):
    file_path: str = Field(..., description="REQUIRED: Source file")
    start_line: int = Field(..., description="REQUIRED: Exact start line")
    end_line: int = Field(..., description="REQUIRED: Exact end line")
    verbatim_content: str = Field(..., description="REQUIRED: Exact paper text\n[WORD-FOR-WORD content from paper - NEVER modify]")
    latex_labels: Optional[List[str]] = Field(default_factory=list, description="OPTIONAL: LaTeX labels in paper")
    paper_citations: Optional[List[str]] = Field(default_factory=list, description="OPTIONAL: Citations used in paper")

class NotationExplanations(BaseModel):
    latex_macros: Dict[str, str] = Field(..., description="REQUIRED: Undefined macro translations")
    mathematical_context: Dict[str, str] = Field(..., description="REQUIRED: Variable/symbol meanings")
    ambiguous_notation: Optional[Dict[str, str]] = Field(default_factory=dict, description="OPTIONAL: Unclear symbols needing verification")
    author_conventions: Optional[Dict[str, str]] = Field(default_factory=dict, description="OPTIONAL: Paper-specific conventions")

class ThesisContent(BaseModel):
    condensed_summary: str = Field(..., description="REQUIRED: Brief overview\n[1-2 paragraph summary of the logical unit]")
    detailed_analysis: str = Field(..., description="REQUIRED: Comprehensive explanation\n[Detailed exposition suitable for thesis - make implicit assumptions explicit]")
    expansion_notes: str = Field(..., description="REQUIRED: What needs expansion from paper\n[Specific areas where paper was brief due to space constraints]")

class LineByLineProofStep(BaseModel):
    step: int
    statement: str = Field(..., description="[Mathematical statement for this step]")
    justification: str = Field(..., description="[Complete justification with specific citations]")
    citations: List[str] = Field(default_factory=list, description="[Theorem X.Y in Paper1999, Stacks Tag 02AB, Mathlib theorem_name]")
    assumptions: str = Field(..., description="[Any assumptions used in this step]")

class ProofDevelopment(BaseModel):
    paper_proof_content: str = Field(..., description="REQUIRED: What paper provided\n[Exact proof from paper, often brief or sketched]")
    thesis_proof_outline: str = Field(..., description="REQUIRED: Structured proof plan\n[Step-by-step outline for complete thesis proof]")
    rigorous_proof: str = Field(..., description="REQUIRED: Complete proof for thesis\n[Fully detailed proof suitable for thesis examination]")
    line_by_line_proof: List[LineByLineProofStep] = Field(..., description="REQUIRED: Formalization-ready proof")
    proof_references: List[str] = Field(default_factory=list, description="REQUIRED: Sources needed for proof")

class SuspicionScores(BaseModel):
    source_fidelity: float = Field(..., ge=0.0, le=1.0, description="Paper extraction accuracy")
    mathematical_accuracy: float = Field(..., ge=0.0, le=1.0, description="Mathematical content correctness")
    citation_validity: float = Field(..., ge=0.0, le=1.0, description="Reference verification")
    proof_correctness: float = Field(..., ge=0.0, le=1.0, description="Mathematical proof validity")
    formalization_readiness: float = Field(..., ge=0.0, le=1.0, description="Line-by-line proof suitable for Lean")
    expansion_quality: float = Field(..., ge=0.0, le=1.0, description="Thesis expansion appropriateness")

class Audit(BaseModel):
    audit_id: str = Field(..., description="REQUIRED: Unique audit identifier")
    auditor_role: Literal["extractor", "auditor"] = Field(..., description="REQUIRED: extractor|auditor")
    audit_date: datetime = Field(..., description="REQUIRED: ISO timestamp")
    suspicion_scores: SuspicionScores
    audit_notes: str = Field(..., description="REQUIRED: Auditor comments\n[Comments about the extraction/verification process]")
    evidence_gathered: Optional[str] = Field(default="", description="OPTIONAL: Evidence for score changes\n[Details of verification work performed]")

class LogicalUnit(BaseModel):
    # === UNIT IDENTIFICATION ===
    unit_id: str = Field(..., description="REQUIRED: snake_case ID")
    unit_type: Literal["theorem", "lemma", "definition", "proposition", "example", "remark"] = Field(..., description="REQUIRED: theorem|lemma|definition|proposition|example|remark")
    thesis_title: str = Field(..., description="REQUIRED: Descriptive Title for Thesis Clear heading for thesis")
    dependencies: List[str] = Field(default_factory=list, description="REQUIRED: Prerequisites (empty array if none)")

    # === SOURCE TRACEABILITY ===
    paper_source: PaperSource

    # === NOTATION TRANSLATION ===
    notation_explanations: NotationExplanations

    # === THESIS EXPANSION ===
    thesis_content: ThesisContent

    # === PROOF OBJECTS (Required for theorem|lemma|proposition only) ===
    proof_development: Optional[ProofDevelopment] = None

    # === VERIFICATION TRAIL ===
    audits: List[Audit] = Field(..., min_length=1)

    @field_validator('unit_id')
    @classmethod
    def validate_unit_id_snake_case(cls, value: str) -> str:
        if not re.match(r'^[a-z0-9_]+$', value):
            raise ValueError('unit_id must be in snake_case')
        return value

    # Using model_validator for cross-field validation
    from pydantic import model_validator

    @model_validator(mode='after') # 'after' mode ensures individual fields are already validated
    def check_proof_development_logic(cls, model: 'LogicalUnit') -> 'LogicalUnit':
        if model.unit_type in ["theorem", "lemma", "proposition"] and model.proof_development is None:
            raise ValueError(f"proof_development is required for unit_type '{model.unit_type}'")

        # The original V1 validator had a check:
        # if unit_type not in ["theorem", "lemma", "proposition"] and v is not None:
        # This implies proof_development should NOT exist for other types.
        # However, the YAML structure and problem description say "Required for ... only",
        # which usually means it's optional overall but mandatory for those specific types.
        # The Pydantic field `Optional[ProofDevelopment]` already makes it optional.
        # So, we only need to enforce its presence for specific unit_types.
        # If it should be forbidden for other types, that's an additional check:
        # if model.unit_type not in ["theorem", "lemma", "proposition"] and model.proof_development is not None:
        #     raise ValueError(f"proof_development should only be present for theorem, lemma, or proposition, not for '{model.unit_type}'")
        # For now, sticking to "required for A, B, C" means it *must* be there for A, B, C, and can be there or not for others.
        return model


class LogicalUnitsFile(RootModel[List[LogicalUnit]]):
    root: List[LogicalUnit]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    @classmethod
    def model_validate_yaml(cls, yaml_str: str):
        import yaml
        data = yaml.safe_load(yaml_str)
        if 'logical_units' not in data:
            raise ValueError("YAML must have a top-level 'logical_units' key")
        # Ensure that the data passed to model_validate is a list
        if not isinstance(data['logical_units'], list):
            raise ValueError("'logical_units' must contain a list of units")
        return cls.model_validate(data['logical_units'])

    def model_dump_yaml(self, **kwargs) -> str:
        import yaml
        # Pydantic's model_dump can convert datetime to string automatically
        # based on model_fields schema.
        # We need to ensure it's ISO format for audit_date.
        # By default, Pydantic serializes datetime to ISO 8601 format.
        data = {"logical_units": self.model_dump(mode='python', **kwargs)} # self.model_dump() gives the list
        return yaml.dump(data, sort_keys=False, allow_unicode=True)

# New model for direct LLM response to simplify RootModel interaction with instructor
class ExtractionResult(BaseModel):
    logical_units: List[LogicalUnit] = Field(..., description="The list of extracted logical units.")

if __name__ == '__main__':
    # Example Usage and Validation Test
    sample_yaml_str = """
logical_units:
  - # === UNIT IDENTIFICATION ===
    unit_id: "unique_identifier"
    unit_type: "theorem"
    thesis_title: "Descriptive Title for Thesis"
    dependencies: ["unit_1", "unit_2"]

    # === SOURCE TRACEABILITY ===
    paper_source:
      file_path: "writing/sources/en.tex"
      start_line: 123
      end_line: 145
      verbatim_content: |
        [WORD-FOR-WORD content from paper - NEVER modify]
      latex_labels: ["thm:main", "eq:identity"]
      paper_citations: ["Author1999", "Smith2000"]

    # === NOTATION TRANSLATION ===
    notation_explanations:
      latex_macros:
        "\\\\cL": "\\\\mathcal{L} (script L - likely line bundle or sheaf)"
        "\\\\bZ": "\\\\mathbb{Z} (integers)"
        "\\\\sH": "\\\\mathscr{H} (script H - likely Hilbert scheme or family)"
      mathematical_context:
        "Z": "Scheme or variety being studied (from context in Section 2.1)"
        "S": "Parameter space or base scheme (introduced in Definition 2.3)"
        "\\\\Pic(Z)": "Picard group of the scheme Z (group of line bundles)"
        "deg": "Degree of polarization (numerical invariant)"
      ambiguous_notation:
        "H^2": "Could be cohomology or Hilbert scheme - verify in context"
        "\\\\chi": "Euler characteristic or other invariant - check definition"
      author_conventions:
        "polarization_notation": "Author uses (L,Z) for polarized pair, not standard (Z,L)"
        "moduli_convention": "M_d denotes moduli space, not M^d as in some literature"

    # === THESIS EXPANSION ===
    thesis_content:
      condensed_summary: |
        [1-2 paragraph summary of the logical unit]
      detailed_analysis: |
        [Detailed exposition suitable for thesis - make implicit assumptions explicit]
      expansion_notes: |
        [Specific areas where paper was brief due to space constraints]

    # === PROOF OBJECTS (Required for theorem|lemma|proposition only) ===
    proof_development:
      paper_proof_content: |
        [Exact proof from paper, often brief or sketched]
      thesis_proof_outline: |
        [Step-by-step outline for complete thesis proof]
      rigorous_proof: |
        [Fully detailed proof suitable for thesis examination]
      line_by_line_proof:
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
      proof_references: ["Source1", "Source2"]

    # === VERIFICATION TRAIL ===
    audits:
      - audit_id: "extractor_initial"
        auditor_role: "extractor"
        audit_date: "2025-01-06T10:30:00Z"
        suspicion_scores:
          source_fidelity: 1.0
          mathematical_accuracy: 1.0
          citation_validity: 1.0
          proof_correctness: 1.0
          formalization_readiness: 1.0
          expansion_quality: 1.0
        audit_notes: |
          [Comments about the extraction/verification process]
        evidence_gathered: |
          [Details of verification work performed]
  - unit_id: "another_unit"
    unit_type: "definition"
    thesis_title: "Another Definition"
    dependencies: []
    paper_source:
      file_path: "writing/sources/other.tex"
      start_line: 10
      end_line: 20
      verbatim_content: "This is another definition."
    notation_explanations:
      latex_macros: {}
      mathematical_context: {}
    thesis_content:
      condensed_summary: "Summary of definition."
      detailed_analysis: "Detailed analysis of definition."
      expansion_notes: "Needs more examples."
    # No proof_development for definition
    audits:
      - audit_id: "extractor_initial_def"
        auditor_role: "extractor"
        audit_date: "2025-01-07T11:00:00Z" # Different date
        suspicion_scores:
          source_fidelity: 1.0
          mathematical_accuracy: 1.0
          citation_validity: 1.0
          proof_correctness: 1.0 # This will be present but might be ignored by some logic if not a proof unit
          formalization_readiness: 1.0 # Same as above
          expansion_quality: 1.0
        audit_notes: "Initial extraction for definition."
"""
    try:
        parsed_data = LogicalUnitsFile.model_validate_yaml(sample_yaml_str)
        print("YAML Parsed Successfully!")
        # print(parsed_data.model_dump_json(indent=2))

        # Test dumping back to YAML
        output_yaml = parsed_data.model_dump_yaml()
        print("\nYAML Output:")
        print(output_yaml)

        # Test validation for proof_development requirement
        invalid_theorem_yaml = """
logical_units:
  - unit_id: "invalid_theorem"
    unit_type: "theorem"
    thesis_title: "Invalid Theorem without Proof Development"
    dependencies: []
    paper_source:
      file_path: "test.tex"
      start_line: 1
      end_line: 2
      verbatim_content: "Theorem statement."
    notation_explanations:
      latex_macros: {}
      mathematical_context: {}
    thesis_content:
      condensed_summary: "Summary."
      detailed_analysis: "Analysis."
      expansion_notes: "Notes."
    # Missing proof_development
    audits:
      - audit_id: "test_audit"
        auditor_role: "extractor"
        audit_date: "2025-01-01T00:00:00Z"
        suspicion_scores:
          source_fidelity: 1.0
          mathematical_accuracy: 1.0
          citation_validity: 1.0
          proof_correctness: 1.0
          formalization_readiness: 1.0
          expansion_quality: 1.0
        audit_notes: "Test."
"""
        try:
            LogicalUnitsFile.model_validate_yaml(invalid_theorem_yaml)
        except ValueError as e:
            print(f"\nSuccessfully caught expected error for missing proof_development: {e}")

        # Test validation for snake_case
        invalid_snake_case_yaml = """
logical_units:
  - unit_id: "InvalidID"
    unit_type: "definition"
    thesis_title: "Invalid ID"
    dependencies: []
    paper_source:
      file_path: "test.tex"
      start_line: 1
      end_line: 2
      verbatim_content: "Definition."
    notation_explanations:
      latex_macros: {}
      mathematical_context: {}
    thesis_content:
      condensed_summary: "Summary."
      detailed_analysis: "Analysis."
      expansion_notes: "Notes."
    audits:
      - audit_id: "test_audit_invalid_id"
        auditor_role: "extractor"
        audit_date: "2025-01-01T00:00:00Z"
        suspicion_scores:
          source_fidelity: 1.0
          mathematical_accuracy: 1.0
          citation_validity: 1.0
          proof_correctness: 1.0
          formalization_readiness: 1.0
          expansion_quality: 1.0
        audit_notes: "Test."
"""
        try:
            LogicalUnitsFile.model_validate_yaml(invalid_snake_case_yaml)
        except ValueError as e:
            print(f"\nSuccessfully caught expected error for invalid unit_id format: {e}")

    except Exception as e:
        print(f"Error parsing YAML: {e}")

    # Example of creating an instance programmatically
    example_audit = Audit(
        audit_id="prog_audit_001",
        auditor_role="extractor",
        audit_date=datetime.now(),
        suspicion_scores=SuspicionScores(
            source_fidelity=1.0,
            mathematical_accuracy=1.0,
            citation_validity=1.0,
            proof_correctness=1.0,
            formalization_readiness=1.0,
            expansion_quality=1.0
        ),
        audit_notes="Programmatically created audit."
    )

    example_logical_unit = LogicalUnit(
        unit_id="programmatic_example",
        unit_type="remark",
        thesis_title="A Programmatically Created Remark",
        dependencies=[],
        paper_source=PaperSource(
            file_path="source.md",
            start_line=1,
            end_line=5,
            verbatim_content="This is a remark created via Pydantic models."
        ),
        notation_explanations=NotationExplanations(
            latex_macros={"\\myMacro": "\\mathcal{M}"},
            mathematical_context={"X": "A variable X"}
        ),
        thesis_content=ThesisContent(
            condensed_summary="This is a short summary.",
            detailed_analysis="This is a more detailed analysis of the remark.",
            expansion_notes="Consider adding examples for this remark."
        ),
        audits=[example_audit]
    )

    logical_units_file_instance = LogicalUnitsFile.model_validate([example_logical_unit])
    print("\nProgrammatically created instance YAML:")
    print(logical_units_file_instance.model_dump_yaml())

    # Test datetime serialization
    dt_audit = Audit(
        audit_id="dt_test",
        auditor_role="extractor",
        audit_date=datetime(2024, 7, 26, 12, 30, 55),
         suspicion_scores=SuspicionScores(
            source_fidelity=1.0,
            mathematical_accuracy=1.0,
            citation_validity=1.0,
            proof_correctness=1.0,
            formalization_readiness=1.0,
            expansion_quality=1.0
        ),
        audit_notes="Testing datetime"
    )
    # Pydantic v2 serializes datetime to ISO format by default
    # print(dt_audit.model_dump_json()) # "audit_date": "2024-07-26T12:30:55"

    # Test RootModel
    lu_list = [example_logical_unit]
    root_model_instance = LogicalUnitsFile(root=lu_list) # or LogicalUnitsFile(lu_list)
    assert root_model_instance[0].unit_id == "programmatic_example"
    print("\nRootModel test successful.")
    yaml_from_root = root_model_instance.model_dump_yaml()
    # print(yaml_from_root)
    assert "programmatic_example" in yaml_from_root

    # Test min_length for audits
    try:
        LogicalUnit(
            unit_id="no_audit_test",
            unit_type="remark",
            thesis_title="Test No Audits",
            dependencies=[],
            paper_source=PaperSource(file_path="s.t", start_line=1, end_line=1, verbatim_content="vc"),
            notation_explanations=NotationExplanations(latex_macros={}, mathematical_context={}),
            thesis_content=ThesisContent(condensed_summary="cs", detailed_analysis="da", expansion_notes="en"),
            audits=[] # Empty list, should fail
        )
    except ValueError as e:
        print(f"\nSuccessfully caught error for empty audits list: {e}")

    print("\nAll inline tests completed.")
