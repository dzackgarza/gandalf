# This file is for development and testing purposes.
# It provides a hardcoded, simulated LLM response for specific inputs,
# allowing testing of the end-to-end pipeline without making actual LLM calls
# (useful when API keys are unavailable or to save costs during UI/logic testing).

from .models import (
    ExtractionResult, LogicalUnit, PaperSource, NotationExplanations, ThesisContent,
    Audit, SuspicionScores, ProofDevelopment, LineByLineProofStep
)
from datetime import datetime, timezone, timedelta # Added timedelta for unique audit dates

def get_simulated_llm_response_for_md_sample() -> ExtractionResult:
    """
    Returns a crafted ExtractionResult object simulating a high-quality LLM
    output for the 'sample_math_article.md' document.
    """
    now = datetime.now(timezone.utc)
    simulated_logical_units = [
        LogicalUnit(
            unit_id="foo_bar_definition",
            unit_type="definition",
            thesis_title="Formal Definition of a Foo Bar",
            dependencies=[],
            paper_source=PaperSource(
                file_path="sample_math_article.md",
                start_line=10,
                end_line=18,
                verbatim_content="A *Foo Bar* over a field $\\mathbb{K}$ is a tuple $(\\mathcal{S}, \\oplus, \\otimes, \\lambda_0)$ where:\n1.  $\\mathcal{S}$ is a non-empty set.\n2.  $\\oplus: \\mathcal{S} \\times \\mathcal{S} \\to \\mathcal{S}$ is a binary operation called 'foo-addition'.\n3.  $\\otimes: \\mathbb{K} \\times \\mathcal{S} \\to \\mathcal{S}$ is an operation called 'bar-multiplication'.\n4.  $\\lambda_0 \\in \\mathcal{S}$ is a distinguished element known as the 'base foo'.\n\nThese components must satisfy Axioms F1-F3 (detailed elsewhere). For example, foo-addition $\\oplus$ must be associative.",
                latex_labels=[],
                paper_citations=[]
            ),
            notation_explanations=NotationExplanations(
                latex_macros={
                    "\\mathbb{K}": "Represents a generic field.",
                    "\\mathcal{S}": "Represents the non-empty set in a Foo Bar.",
                    "\\oplus": "Represents the 'foo-addition' binary operation.",
                    "\\otimes": "Represents the 'bar-multiplication' operation.",
                    "\\lambda_0": "Represents the 'base foo' distinguished element."
                },
                mathematical_context={
                    "field": "A set with addition and multiplication satisfying certain axioms, denoted K.",
                    "tuple": "An ordered collection of elements."
                },
                ambiguous_notation={},
                author_conventions={}
            ),
            thesis_content=ThesisContent(
                condensed_summary="This unit formally defines a Foo Bar over a field K as a tuple comprising a set S, two operations (foo-addition and bar-multiplication), and a special 'base foo' element. These must adhere to specified axioms.",
                detailed_analysis="The definition of a Foo Bar establishes its fundamental components. The set S forms the underlying space. Foo-addition provides an internal composition rule, while bar-multiplication defines how elements of the field K interact with S. The base foo, lambda_0, likely serves as an origin or fundamental building block. The requirement for these to satisfy Axioms F1-F3 (which should be detailed in a full thesis) constrains the structure, ensuring it has well-defined mathematical properties. The associativity of foo-addition is given as an example axiom, typical for algebraic structures.",
                expansion_notes="For a thesis: Explicitly list and explain Axioms F1-F3. Discuss the choice of a field K and implications of its properties. Provide simple, illustrative examples of S, operations, and lambda_0. Compare and contrast with known algebraic structures like vector spaces or monoids to highlight unique aspects of Foo Bars."
            ),
            proof_development=None,
            audits=[Audit(
                audit_id=f"extractor_initial_{(now - timedelta(seconds=10)).strftime('%Y%m%d%H%M%S%f')[:-3]}_sim_def",
                auditor_role="extractor",
                audit_date=(now - timedelta(seconds=10)),
                suspicion_scores=SuspicionScores(source_fidelity=1.0, mathematical_accuracy=1.0, citation_validity=1.0, proof_correctness=1.0, formalization_readiness=1.0, expansion_quality=1.0),
                audit_notes="Initial extraction by LLM (simulated). All content generated based on input document and system instructions. All fields require human verification.",
                evidence_gathered=""
            )]
        ),
        LogicalUnit(
            unit_id="existence_unique_baz_foo_theorem",
            unit_type="theorem",
            thesis_title="Existence and Uniqueness of the Baz Foo",
            dependencies=["foo_bar_definition"],
            paper_source=PaperSource(
                file_path="sample_math_article.md",
                start_line=25,
                end_line=30,
                verbatim_content="Every Foo Bar $(\\mathcal{S}, \\oplus, \\otimes, \\lambda_0)$ over an algebraically closed field $\\mathbb{K}$ of characteristic zero contains a unique non-trivial 'Baz Foo', denoted $\\beta^*$, such that $\\phi(\\beta^*) = \\lambda_0$ for a specific canonical map $\\phi$.",
                latex_labels=[],
                paper_citations=[]
            ),
            notation_explanations=NotationExplanations(
                latex_macros={
                    "\\beta^*": "Denotes the unique non-trivial Baz Foo.",
                    "\\phi": "Represents a specific canonical map related to Baz Foos."
                },
                mathematical_context={
                    "algebraically closed field": "A field K where every non-constant polynomial with coefficients in K has a root in K.",
                    "characteristic zero": "A field where repeated addition of the multiplicative identity 1 never sums to 0."
                },
                ambiguous_notation={},
                author_conventions={}
            ),
            thesis_content=ThesisContent(
                condensed_summary="This theorem asserts that under specific conditions on the underlying field (algebraically closed, characteristic zero), any Foo Bar is guaranteed to possess exactly one non-trivial Baz Foo. This Baz Foo has a defined relationship with the base foo via a canonical map.",
                detailed_analysis="Theorem 3.1 is a cornerstone result, establishing both the existence and uniqueness of a special element called the Baz Foo ($\\beta^*$) within a Foo Bar. The conditions on the field $\\mathbb{K}$ (algebraically closed and characteristic zero) are significant and common in deep algebraic theorems, often simplifying arguments or enabling powerful tools. The relationship $\\phi(\\beta^*) = \\lambda_0$ links the Baz Foo back to the fundamental base foo, suggesting $\\beta^*$ might be a derived or canonical representation. The non-triviality condition implies $\\beta^*$ is distinct from simpler or identity-like elements.",
                expansion_notes="For a thesis: Define 'Baz Foo' formally if not already done. Explain the significance of 'non-trivial'. Detail the 'specific canonical map' $\\phi$. Discuss why algebraically closed fields of characteristic zero are necessary conditions – provide counter-examples or explain limitations if these conditions are relaxed. Explore the implications of this unique element for the structure of Foo Bars."
            ),
            proof_development=ProofDevelopment(
                paper_proof_content="*Proof Sketch*.\nThe proof proceeds in two parts:\n1.  **Existence**: We construct an element $\\beta_c$ using a sequence of foo-operations derived from the Zorn's Lemma applied to a partially ordered set of proto-Baz Foos. We then show $\\beta_c$ satisfies the conditions for a Baz Foo.\n2.  **Uniqueness**: Assume $\\beta_1^*$ and $\\beta_2^*$ are two distinct non-trivial Baz Foos. We apply the Bar Homomorphism Lemma (Lemma 3.0, not shown here) to demonstrate that $\\beta_1^* = \\beta_2^*$, leading to a contradiction.\n\nThe full proof requires developing the theory of Bar Homomorphisms and is deferred to Appendix A.",
                thesis_proof_outline="1. Define Proto-Baz Foo and establish a relevant poset.\n2. Verify Zorn's Lemma conditions (non-empty, every chain has upper bound).\n3. Apply Zorn's Lemma for existence of $\\beta_c$.\n4. Prove $\\beta_c$ is a Baz Foo and non-trivial.\n5. For uniqueness, assume $\\beta_1^*, \\beta_2^*$ are distinct Baz Foos.\n6. State and prove/cite the Bar Homomorphism Lemma.\n7. Apply Bar Homomorphism Lemma to show $\\beta_1^* = \\beta_2^*$.\n8. Conclude uniqueness.",
                rigorous_proof="[To be developed in full for thesis. Start with defining the set of proto-Baz Foos $P = \\{x \\in \\mathcal{S} \\mid \\text{x satisfies proto-Baz conditions}\\}$. Define a partial order $\\preceq$ on $P$. Show $(P, \\preceq)$ is non-empty (e.g., $\\lambda_0$ related elements). Let $C$ be a chain in $P$. Construct an upper bound $u_C \\in P$. By Zorn's Lemma, there exists a maximal element $\\beta_c$. Prove $\\beta_c$ is indeed a Baz Foo. Then, for uniqueness, assume $\\beta_1^*, \\beta_2^*$ exist... (This would be many paragraphs)]",
                line_by_line_proof=[
                    LineByLineProofStep(step=1, statement="Let $P$ be the set of all proto-Baz Foos. Define a partial order $\\preceq$ on $P$.", justification="Standard approach for Zorn's Lemma application.", citations=["Folland, Real Analysis, Appendix A"], assumptions="Foo Bar axioms hold."),
                    LineByLineProofStep(step=2, statement="Show $P$ is non-empty.", justification="The base foo $\\lambda_0$ or a simple derivative might serve as a trivial proto-Baz Foo.", citations=[], assumptions="Definition of proto-Baz Foo allows for a base case."),
                ],
                proof_references=["Folland_RealAnalysis_AppendixA", "Hypothetical_AppendixA_BarHomomorphisms"]
            ),
            audits=[Audit(
                audit_id=f"extractor_initial_{now.strftime('%Y%m%d%H%M%S%f')[:-3]}_sim_thm", # Ensure unique audit_id
                auditor_role="extractor",
                audit_date=now,
                suspicion_scores=SuspicionScores(source_fidelity=1.0, mathematical_accuracy=1.0, citation_validity=1.0, proof_correctness=1.0, formalization_readiness=1.0, expansion_quality=1.0),
                audit_notes="Initial extraction by LLM (simulated). All content generated based on input document and system instructions. All fields require human verification.",
                evidence_gathered=""
            )]
        )
    ]
    return ExtractionResult(logical_units=simulated_logical_units)

if __name__ == '__main__':
    # Test the simulated response
    sim_response = get_simulated_llm_response_for_md_sample()
    print(f"Generated {len(sim_response.logical_units)} simulated logical units.")
    if sim_response.logical_units:
        print(f"First unit ID: {sim_response.logical_units[0].unit_id}")
        print(f"Second unit ID: {sim_response.logical_units[1].unit_id}")

        from .models import LogicalUnitsFile
        import yaml

        lu_file = LogicalUnitsFile(root=sim_response.logical_units)
        yaml_output = lu_file.model_dump_yaml()
        print("\nSimulated YAML Output:")
        print(yaml_output)
