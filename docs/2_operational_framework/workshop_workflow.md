# Workshop Workflow: A Commission's Journey

This document walks through the Gandalf Workshop's typical process for handling a commission. It includes the crucial **Product Manager (PM) Agent Review** step and the iterative **Development and Audit Cycle**, demonstrating how the Workshop Manager, Specialist Artisans (Planner, PM Agent, Coder, Audit Agent), Blueprints, PM Reviews, Products, and Audit Receipts interact to deliver a high-quality, strategically aligned result.

While the example used is a software MVP, similar principles apply to other commission types like research reports.

## Illustrative Commission Brief (Example: GUI Calculator)

"We need a simple graphical calculator application for desktop users. It should perform basic arithmetic operations: addition, subtraction, multiplication, and division. It needs a clear display and standard number buttons (0-9) and operator buttons. We want a functional Minimum Viable Product (MVP) first."

## The Commission Journey

The workflow is managed by the **Workshop Manager** and involves several key stages:

1.  **Commission Intake & Initial Blueprinting:**
    *   The **Workshop Manager** receives the commission brief (e.g., the GUI calculator request).
    *   A unique `commission_id` is assigned.
    *   The Manager assigns the task to a **Planner Artisan** (see `planner_charter.md`).
    *   The Planner Artisan drafts the initial `blueprint.yaml` (Version 1.0). This includes:
        *   `commission_title`, `commission_type`
        *   `project_summary` (derived from the brief)
        *   `key_objectives`
        *   `product_specifications` (modules, components, features, etc.)
        *   `unit_tests_required` (for software)
        *   `quality_criteria`
        *   The Planner might also draft an initial `commission_expectations.feature` file for BDD.
    *   *Self-correction Example:* Initially, the Planner might include features beyond MVP scope (e.g., scientific functions for the basic calculator).

2.  **Strategic PM Review Cycle:**
    *   The **Workshop Manager** sends the `blueprint.yaml` (v1.0) to the **Product Manager (PM) Agent** (see `pm_agent_charter.md`).
    *   The PM Agent analyzes the blueprint for strategic alignment with the commission's intent, especially MVP principles.
    *   The PM Agent generates a `PM_Review.json` with a `decision` (`APPROVED` or `REVISION_REQUESTED`) and `rationale`.
        *   *If REVISION_REQUESTED (e.g., due to over-scoping for an MVP):* The `rationale` would specify issues like "Over-engineered for an MVP," and `suggested_focus_areas_for_revision` would guide the Planner.
    *   The **Workshop Manager** processes the PM review.

3.  **Blueprint Revision (If Necessary):**
    *   If the PM review requested revisions, the **Workshop Manager** sends the blueprint and the PM review back to the **Planner Artisan**.
    *   The Planner revises the blueprint to address the PM's feedback (e.g., removing non-MVP features, clarifying objectives).
    *   The revised blueprint (e.g., v1.1) is submitted.
    *   This loop (PM Review -> Blueprint Revision) continues until the PM Agent `APPROVES` the blueprint.

4.  **Product Generation & Iteration Cycle (Post PM Approval):**
    *   Once the blueprint is PM-approved, the **Workshop Manager** assigns it to a **Coder Artisan** (see `coder_charter.md`).
    *   The Coder Artisan takes the approved `blueprint.yaml` and the `commission_expectations.feature` file (if applicable) to build/revise the product. This includes:
        *   Writing the application code.
        *   Writing unit test code as specified or needed.
        *   Writing BDD step definition code to match the `.feature` file.
    *   The Coder produces an initial version of the product (e.g., `product_v1`).

5.  **Automated Audit Cycle:**
    *   The **Workshop Manager** takes the generated `product_v1` and initiates an automated audit using the **Audit Agent** (see `audit_agent_charter.md`). This typically involves running `run_full_audit.sh`.
    *   The Audit Agent performs various checks: linting, type checking, unit test execution, BDD test execution, etc.
    *   The Audit Agent generates an `LATEST_AUDIT_RECEIPT.md` detailing pass/fail for each stage and contributing to a `quality_score` (C(v)).
    *   *If Audit Fails (e.g., unit tests fail, linting errors):* The receipt will indicate failures.

6.  **Revision Based on Audit (If Necessary):**
    *   The **Workshop Manager** reviews the `LATEST_AUDIT_RECEIPT.md`.
    *   If the audit is not successful or the quality score is below target, the Manager sends the product and the audit receipt back to the **Coder Artisan**.
    *   The Coder Artisan works on a new version (e.g., `product_v2`), fixing issues identified in the audit.
    *   This loop (Product Generation/Revision -> Automated Audit) continues until the audit is successful and the quality score meets the target. This aligns with the Generate <-> Critique loop and `ΔC` concepts from the `high_level_design.md`.

7.  **Commission Completion & Archival:**
    *   Once a product version passes all automated audits and meets quality criteria, the **Workshop Manager** declares the commission complete.
    *   The final product version and its final `LATEST_AUDIT_RECEIPT.md` are archived (e.g., in a `completed_commissions/` directory).

## Benefits of this Workflow:

*   **Upfront Strategic Alignment:** The PM Agent ensures the Blueprint is strategically sound *before* extensive development, preventing work on misaligned features.
*   **Iterative Blueprint Refinement:** The Planner-PM loop allows for early strategic corrections.
*   **Focused Development:** Coder Artisans work on PM-approved, well-defined Blueprints.
*   **Continuous Quality Assurance:** The automated audit cycle provides consistent, objective feedback, driving product quality.
*   **Efficiency:** Reduces late-stage rework by catching strategic and quality issues earlier in the process.

This structured, iterative workflow with integrated strategic review and automated auditing is key to the Gandalf Workshop's goal of autonomously delivering high-quality, validated products.
