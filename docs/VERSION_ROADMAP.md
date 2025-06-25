# Gandalf Workshop Version Roadmap

This document outlines the phased development roadmap for the Gandalf Workshop. Our primary goal is to achieve a Minimum Viable Product (MVP) that demonstrates the core viability of the autonomous agentic system, followed by iterative enhancements.

## Phase 1: Core Orchestration & Planning MVP (Viability Focus)

**Goal:** Demonstrate a minimal, verifiable end-to-end flow from commission intake to a placeholder product output, including strategic review and basic audit. This phase prioritizes proving the viability of the core control loop and inter-agent communication.

**Core Components & Functionality:**

1.  **Basic Workshop Manager Orchestration:**
    *   Implement the main control loop in `workshop_manager.py`.
    *   Ability to receive a simple commission (e.g., user prompt as a string).
    *   Sequential execution of Planner, PM Agent, Coder, and Audit Agent stages.
    *   Basic logging of stage transitions and outcomes.

2.  **Planner Artisan - MVP Implementation:**
    *   Receives a commission prompt.
    *   Generates a syntactically correct `blueprint.yaml` with predefined, minimal content.
        *   Example: Fixed structure for a simple "hello world" type application or a single-section research outline.
    *   Generates a syntactically correct `commission_expectations.feature` file (if software_mvp type) with one or two predefined Gherkin scenarios.
    *   Focus is on schema adherence, not sophisticated planning logic.

3.  **Product Manager (PM) Agent - MVP Review:**
    *   Receives the `blueprint.yaml` from the Planner.
    *   Performs a basic, potentially rule-based, review.
        *   Example: Checks if `project_summary` and `key_objectives` are non-empty.
    *   Outputs a `PM_Review.json` with a decision (`APPROVED` or `REVISION_REQUESTED`) and minimal rationale.
    *   For MVP, the PM Agent will likely approve most well-formed (even if trivial) blueprints to allow the flow to continue.

4.  **Coder Artisan - Placeholder Product:**
    *   Receives the PM-approved `blueprint.yaml`.
    *   Generates a placeholder product.
        *   Example: A simple text file saying "Product for commission [ID] based on blueprint [version]" or a single Python file with a print statement.
    *   Generates placeholder unit test files (e.g., empty test files or tests that trivially pass).
    *   Generates placeholder BDD step definition files (if applicable).
    *   Focus is on demonstrating the Coder Artisan can be invoked and produce *some* output, not functional code.

5.  **Audit Agent - Placeholder Audit:**
    *   Receives the placeholder product from the Coder.
    *   Simulates an audit process.
    *   Generates a `LATEST_AUDIT_RECEIPT.md` indicating placeholder success (e.g., all checks "OK" by default).
    *   Focus is on integrating the audit step and producing a receipt.

**Viability Metrics for Phase 1:**

*   **Successful End-to-End Flow:** The Workshop Manager can orchestrate all MVP agent stages sequentially without crashing.
*   **Correct Artifact Generation:** Each agent produces its designated output file(s) adhering to basic schema requirements (e.g., valid YAML/JSON/Markdown).
*   **Data Persistence:** Artifacts from each stage are correctly saved to the designated workshop layout directories.
*   **Basic PM Review Logic:** The PM Agent can make a decision and record it.
*   **Completion of a "Commission":** The system can take a mock commission from start to finish, resulting in a final (placeholder) product and audit receipt.

## Phase 2: Enhanced Functionality & Iteration

**Goal:** Build upon the MVP by integrating more sophisticated agent logic, initial code generation capabilities, and meaningful audit checks.

**Core Components & Functionality:**

1.  **Planner Artisan - Enhanced Planning:**
    *   Integrate LLM capabilities for generating more realistic `blueprint.yaml` content based on user prompts.
    *   Ability to define a basic but plausible module structure and component requirements for simple software.
    *   Improved Gherkin scenario generation for `commission_expectations.feature`.

2.  **Coder Artisan - Basic Code Generation:**
    *   Integrate LLM capabilities to generate simple, runnable code based on the `blueprint.yaml` (e.g., a Python script that performs a basic calculation or a simple Streamlit app).
    *   Generate actual unit tests for the generated code (e.g., simple function input/output tests).
    *   Implement basic BDD step definitions that can execute against the generated code.

3.  **Audit Agent - Initial Automated Checks:**
    *   Integrate basic linting (e.g., `flake8` for Python) into the audit process.
    *   Execute actual unit tests (e.g., `pytest`) and report pass/fail status in `LATEST_AUDIT_RECEIPT.md`.
    *   Execute BDD tests (e.g., `pytest-bdd`) and report pass/fail.
    *   The `quality_score` concept from `Design-Doc-High-Level.md` can be introduced with simple metrics (e.g., % unit tests passed, linter errors).

4.  **Workshop Manager - Basic Iteration Logic:**
    *   Implement a simple retry mechanism if a stage fails (e.g., Coder fails to produce code that passes linting, then retry once).
    *   Begin incorporating the `ΔC` (change in quality score) concept for deciding if a revision loop is productive, initially based on unit test pass rates or linting results.

**Viability Metrics for Phase 2:**

*   **Generation of Functional Code:** The Coder Artisan can produce simple applications that run and perform tasks as per the blueprint.
*   **Meaningful Unit Testing:** Generated unit tests verify basic code functionality.
*   **Automated Audit Feedback:** The Audit Agent provides actionable feedback (linting errors, test failures) that can be used for revisions.
*   **Demonstration of Basic Self-Correction:** The system can attempt a revision based on audit feedback (e.g., Coder tries to fix a linting error identified by the Audit Agent).

## Subsequent Phases (High-Level Vision)

Drawing from the `Design-Doc-High-Level.md`, future phases will focus on increasing autonomy, sophistication, and reliability:

*   **Full QA Integration (Adversarial Critique):**
    *   Implement specialized "Breaker" agents (Security Auditor, Spec Compliance, Maintainability) as described in `Design-Doc-High-Level.md` and `Artisan_Charters.md`.
    *   Develop a comprehensive `C(v)` (Quantitative Quality Score) based on multiple metrics.
*   **Advanced Research Report Generation:**
    *   For `research_report` commission types, implement sophisticated search, drafting, and citation validation agents (e.g., Source-Reader Agent with RAG).
*   **Autonomous Intervention Protocols:**
    *   Fully implement Tier 1 (Stagnation) and Tier 2 (Regression) protocols, including state reversion and strategy changes for agents.
*   **Self-Correction & Learning:**
    *   Enable the system to learn from failures and improve its planning and generation strategies over time.
    *   Refine the re-planning loop where failures are sent back to the Planner Artisan.
*   **User Interface & Experience:**
    *   Develop a user-friendly interface for submitting commissions and viewing progress/results (if deemed necessary beyond programmatic interaction).
*   **Tool Integration & Expansion:**
    *   Integrate more development tools, testing frameworks, and knowledge sources.

This roadmap provides a structured approach to developing the Gandalf Workshop, prioritizing early viability and progressively building towards a highly autonomous and capable system.
