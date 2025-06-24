# Communication Protocols of the Gandalf Workshop

This document outlines the standardized "paperwork" (data schemas) and communication protocols used between the Workshop Manager and the Specialist Artisans. These protocols ensure that every Commission is handled consistently, information flows efficiently, and all work is meticulously documented according to the Workshop's standards.

## 1. Planner Artisan Outputs

The Planner Artisan produces two key artifacts at the start of a Commission:
*   **The Blueprint (`blueprint.yaml`):** The master technical plan.
*   **The Commission Expectations (`commission_expectations.feature`):** A Gherkin file defining user-facing behavior for BDD.

### 1.1. The Blueprint Schema (`blueprint.yaml`)

The "Blueprint" is the master technical plan created by a Planner Artisan. It serves as the single source of truth for the Coder Artisan regarding the internal structure and components of the Product. The Blueprint must be a YAML file (`blueprint.yaml`) and adhere to the following structure:

```yaml
# blueprint.yaml - Master Design Document for a Commission

commission_id: "unique_identifier_for_the_commission" # e.g., calc_gui_001, research_ai_ethics_002
commission_title: "Human-readable title of the commission"
commission_type: "software_mvp" | "research_report" # Specifies the nature of the final Product

# Section 1: Overview & Objectives
# Provided by the client, refined by the Planner Artisan
project_summary: |
  A concise description of the commission's goals and the Product to be created.
  What problem does it solve? Who is it for?
key_objectives:
  - "Objective 1..."
  _ - "Objective 2..."

# Section 2: Product Specifications (Metaphor: Detailed Technical Drawings)
# This section varies significantly based on commission_type

# Example for 'software_mvp'
product_specifications:
  type: "software"
  target_platform: "e.g., Desktop (Windows/macOS/Linux), Web, Mobile (iOS/Android)"
  primary_language_framework: "e.g., Python/Streamlit, JavaScript/React, Python/Django"
  modules:
    - module_name: "e.g., user_interface"
      description: "Handles the GUI and user interactions."
      components: # Or functions, classes, etc.
        - component_name: "e.g., main_window"
          description: "The primary application window."
          requirements:
            - "Must display input field."
            - "Must display buttons for numbers 0-9, operators (+, -, *, /), clear, and equals."
        - component_name: "e.g., calculation_logic"
          description: "Handles the arithmetic operations."
          requirements:
            - "Must correctly perform addition, subtraction, multiplication, division."
            - "Must handle division by zero gracefully."
  dependencies: # External libraries or services
    - "e.g., numpy"
    - "e.g., streamlit"
  unit_tests_required: # List of tests the Coder Artisan must ensure pass
    - "test_addition.py"
    - "test_division_by_zero.py"
  data_model: # If applicable
    # schema definitions

# Example for 'research_report'
product_specifications:
  type: "research"
  report_structure: # Outline of the report
    - section_title: "Introduction"
      key_questions_to_address:
        - "What is the scope of this research?"
        - "What are the main hypotheses?"
      required_subsections:
        - "Background"
        - "Problem Statement"
    - section_title: "Methodology"
      description: "How the research will be conducted."
      requirements:
        - "Detail data collection methods."
        - "Describe analytical approach."
    - section_title: "Findings for Hypothesis 1"
      # ... and so on for other sections and hypotheses
  key_sources_to_consult: # Optional initial list
    - "Source A (e.g., specific paper or database)"
  citation_style: "e.g., APA, MLA, IEEE"

# Section 3: Quality Standards & Acceptance Criteria
# Defines what a "well-crafted" Product looks like for this specific Commission
quality_criteria:
  - criterion: "All specified unit tests must pass." # For software
  - criterion: "Code must adhere to PEP8 standards (for Python)." # For software
  - criterion: "All claims must be supported by verifiable citations." # For research
  - criterion: "The Product must meet all functional requirements outlined in product_specifications."
  - criterion: "User interface must be intuitive and match descriptions." # For GUI software

# Section 4: Revision History (Metaphor: Blueprint Amendments)
# Automatically updated by the Workshop Manager after each significant revision cycle.
revisions:
  - version: "1.0"
    date: "YYYY-MM-DD"
    notes: "Initial Blueprint creation."
  # - version: "1.1"
  #   date: "YYYY-MM-DD"
  #   notes: "Revised module X based on early feedback."
```

### 1.2. The Commission Expectations Schema (`commission_expectations.feature`)

The "Commission Expectations" file is created by the Planner Artisan for software commissions. It defines the expected behavior of the Product from an end-user's perspective using Gherkin syntax. This file is used as input for Behavior-Driven Development (BDD) testing. It must be a plain text file with a `.feature` extension.

```gherkin
# commission_expectations.feature - User-facing behavioral specifications

Feature: [High-level feature name, e.g., User Login or Calculator Operations]
  As a [type of user]
  I want [an action or goal]
  So that [benefit or reason]

  Background: (Optional)
    Given [any preconditions that apply to all scenarios in this feature]
    # And [another precondition]

  Scenario: [Specific scenario name, e.g., Successful login with valid credentials]
    Given [context or precondition for this scenario]
    # And [another context item]
    When [event or action performed by the user]
    # And [another action]
    Then [expected outcome or system state]
    # And [another expected outcome]

  Scenario Outline: [Scenario with examples, e.g., Login attempts with different credentials]
    Given [context]
    When I attempt to log in with username "<username>" and password "<password>"
    Then the login result should be "<result>"

    Examples:
      | username    | password | result   |
      | "validuser" | "pass123"| "success"|
      | "invalid"   | "wrong"  | "failure"|

# More features or scenarios can be added.
# Comments can be added using '#'
# Tags (e.g., @smoke, @regression) can be used to organize scenarios.
```
**Key Guidelines for `.feature` files:**
*   **Declarative, Not Imperative:** Describe *what* the system should do, not *how* it does it.
*   **User Language:** Use terminology that the end-user or stakeholder would understand.
*   **One Scenario, One Behavior:** Each scenario should test a single, distinct piece of functionality or business rule.
*   **Independent Scenarios:** Scenarios should be runnable in any order and not depend on the state left by previous scenarios (unless using `Background`).

## 2. The Audit Receipt (`LATEST_AUDIT_RECEIPT.md`)

The "Quality Inspection Report" is now replaced by the "Audit Receipt." This Markdown file is automatically generated by the `run_full_audit.sh` script. It summarizes the results of all automated checks performed on the codebase, serving as the primary "Proof-of-Work" document.

**Location:** `auditing/LATEST_AUDIT_RECEIPT.md`

**Content Example:**
```markdown
# Audit Receipt

**Timestamp:** YYYY-MM-DDTHH:MM:SSZ
**Git Commit Hash:** abc123shortcommit

## Audit Summary

- **Code Quality & Style (black, flake8):** OK | FAILED
- **Type Safety (mypy):** OK | FAILED
- **Unit Test Coverage (pytest --cov --cov-fail-under=X):** OK (XX.XX%) | FAILED (Reason: Below threshold / Tests Failed)
- **Behavior-Driven Development Tests (pytest --bdd):** OK | FAILED (Reason: X scenarios failed)
- **Structural Integrity (audit_structure.py):** OK | FAILED

All core audit stages passed successfully according to their new definitions.
```
*(The actual content is generated by the `run_full_audit.sh` script based on the success or failure of each stage.)*

This receipt provides a quick overview of whether the codebase meets all the automated quality and correctness gates. A successful audit (all "OK") is required for a commission to be considered complete.
Detailed error logs from each tool (pytest, mypy, flake8) are available in the console output during the audit run for the Coder Artisan to debug any failures.

```json
{
  "commission_id": "unique_identifier_for_the_commission",
  "product_version_inspected": "e.g., v1, v2_revised_flaw_X",
  "inspection_date": "YYYY-MM-DDTHH:MM:SSZ",
  "lead_inspector_id": "identifier_of_the_primary_inspector_or_red_team_lead",
  "inspectors_involved": [
    "inspector_spec_compliance_id",
    "inspector_security_audit_id",
    "inspector_maintainability_id"
    // For research: "inspector_citation_validator_id", "inspector_source_reader_id", "inspector_skeptic_id"
  ],
  "quality_score": { // C(v) - Quantitative Quality Score
    "overall_score": 0.85, // Example: a value between 0.0 (low) and 1.0 (high), or other defined scale
    "metrics_details": [ // Breakdown of how the score was derived
      // For Software MVP
      { "metric_name": "passed_unit_tests", "value": 18, "max_value": 20, "weight": 0.4 },
      { "metric_name": "failed_unit_tests", "value": 2, "weight": -0.2 },
      { "metric_name": "linter_errors", "value": 5, "weight": -0.1 },
      { "metric_name": "spec_deviations_critical", "value": 0, "weight": -0.3 },
      { "metric_name": "spec_deviations_minor", "value": 1, "weight": -0.1 },
      // For Research Report
      // { "metric_name": "verified_claims", "value": 45, "weight": 0.5 },
      // { "metric_name": "unverified_claims", "value": 3, "weight": -0.2 },
      // { "metric_name": "contradicted_claims", "value": 1, "weight": -0.2 },
      // { "metric_name": "logical_fallacies_identified", "value": 1, "weight": -0.1 }
    ],
    "previous_score": 0.75 // Score of the prior version, if applicable
  },
  "identified_flaws": [ // List of issues discovered
    {
      "flaw_id": "unique_flaw_identifier_e.g., FLW001",
      "description": "Detailed description of the flaw.",
      "severity": "critical" | "high" | "medium" | "low" | "informational",
      "location_in_product": "e.g., module 'x', file 'y.py', line 'z' or section 'A', paragraph 'B'",
      "blueprint_requirement_violated": "ID or description of the Blueprint item not met",
      "suggested_remediation": "Optional: Inspector's suggestion for fixing the flaw",
      "status": "outstanding" | "addressed" | "deferred"
    }
    // ... more flaws
  ],
  "summary_assessment": "Overall qualitative assessment from the lead inspector. e.g., 'Significant improvements, but critical flaw X needs immediate attention.'",
  "recommendation": "approve_for_delivery" | "requires_revision" | "escalate_for_re_planning"
}
```

## 3. Workshop Manager-Artisan Interaction (Key Function Signatures)

The Workshop Manager (`workshop_manager.py` or `orchestrator.py`) directs the workflow by invoking Artisans (or crews of Artisans) for specific tasks. While the exact implementation will involve agent framework calls (CrewAI, AutoGen), these conceptual function signatures represent the core interactions:

```python
# Conceptual signatures within the Workshop Manager (Orchestrator)

class WorkshopManager:

    def commission_planning_artifacts(self, user_prompt: str, commission_id: str) -> tuple[Path, Path]:
        """
        Assigns a new Commission to a Planner Artisan to create a Blueprint and a .feature file.
        Metaphor: "Manager gives client's request to the Head Draftsman for technical plans and user stories."
        Args:
            user_prompt: The initial request from the client.
            commission_id: A unique ID for this new commission.
        Returns:
            Tuple: (Path to blueprint.yaml, Path to commission_expectations.feature)
        """
        pass

    def request_product_and_tests_generation_or_revision(
        self,
        commission_id: str,
        blueprint_path: Path,
        feature_file_path: Path,
        current_product_path: Optional[Path] = None, # Path to current version if revising
        audit_receipt_path: Optional[Path] = None # Path to previous audit receipt if revising
    ) -> Path: # Path to the product's root directory
        """
        Assigns a Coder Artisan (or team) to build or revise a Product, its unit tests, and BDD step definitions.
        Metaphor: "Manager gives Blueprint and User Stories to Master Craftsman for construction, unit testing, and behavior test implementation."
        Args:
            commission_id: The ID of the commission.
            blueprint_path: Path to the relevant blueprint.yaml.
            feature_file_path: Path to the commission_expectations.feature file.
            current_product_path: Path to the existing product's root directory if this is a revision.
            audit_receipt_path: Path to the last audit receipt detailing failures.
        Returns:
            Path to the root directory of the newly generated or revised product, which includes app code, unit tests, and BDD step defs.
        """
        pass

    def initiate_automated_audit(
        self,
        commission_id: str,
        product_to_audit_path: Path # Path to the product's root directory
    ) -> Path: # Path to the LATEST_AUDIT_RECEIPT.md
        """
        Triggers the automated audit script (run_full_audit.sh) for the specified product.
        Metaphor: "Manager submits the crafted Product and its tests to the automated 'Proving Grounds'."
        Args:
            commission_id: The ID of the commission.
            product_to_audit_path: Path to the product's root directory containing app code and all tests.
        Returns:
            Path to the generated LATEST_AUDIT_RECEIPT.md.
        """
        pass

    def finalize_commission_and_deliver(
        self,
        commission_id: str,
        final_product_path: Path, # Root directory of the final product
        final_audit_receipt_path: Path
    ) -> None:
        """
        Packages the final Product and its Audit Receipt for delivery (e.g., to /completed_commissions).
        Metaphor: "Manager approves the audited Product, archives records, and prepares it for the client."
        Args:
            commission_id: The ID of the commission.
            final_product_path: Path to the root directory of the approved final product.
            final_audit_receipt_path: Path to the final LATEST_AUDIT_RECEIPT.md.
        """
        pass

    def request_planning_artifacts_revision(
        self,
        commission_id: str,
        original_blueprint_path: Path,
        original_feature_file_path: Path,
        failure_feedback: dict # Contains audit results, persistent BDD failures etc.
    ) -> tuple[Path, Path]:
        """
        When a Commission is failing due to fundamental design or expectation issues, sends it back to a Planner Artisan
        to revise the original Blueprint and/or .feature file.
        Metaphor: "Manager sends flawed design and/or user stories back to the Design Studio with notes on what went wrong."
        Args:
            commission_id: The ID of the commission.
            original_blueprint_path: Path to the blueprint that needs revision.
            original_feature_file_path: Path to the .feature file that needs revision.
            failure_feedback: Data about why the current artifacts are leading to failure.
        Returns:
            Tuple: (Path to revised blueprint.yaml, Path to revised commission_expectations.feature)
        """
        pass

# Note: Actual implementation will use CrewAI/AutoGen agent execution calls
# within these conceptual methods. For example, `commission_planning_artifacts` might
# initialize and run a CrewAI "Planner Crew".
```

These standardized communication protocols are the bedrock of the Gandalf Workshop's efficiency and quality assurance, ensuring every Artisan understands their role and every Commission is managed with precision under the "Proof-of-Work" Constitution.
