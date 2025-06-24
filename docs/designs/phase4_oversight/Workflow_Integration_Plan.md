# Workflow Integration Plan: PM Agent Review

This document details the necessary modifications to the Gandalf WorkshopManager's workflow to incorporate the new "PM Review" step, performed by the Product Manager (PM) Agent.

## 1. Objective

To integrate a strategic review phase into the commission lifecycle immediately after a Blueprint is generated (or revised) and before any product development or detailed work commences. This ensures that the Blueprint aligns with the user's strategic intent, preventing wasted effort on misaligned plans.

## 2. Proposed Changes to WorkshopManager Logic

The `WorkshopManager` class, as outlined in `Communication_Protocols.md`, will require a new conceptual method to manage the PM Agent's review process.

### New Conceptual Method: `initiate_strategic_review`

```python
# Conceptual signature within the WorkshopManager (Orchestrator)

class WorkshopManager:
    # ... existing methods ...

    def initiate_strategic_review(
        self,
        commission_id: str,
        blueprint_path: Path # Path to the blueprint.yaml to be reviewed
    ) -> Path:
        """
        Assigns a Blueprint to the Product Manager (PM) Agent for strategic review.
        Metaphor: "Manager asks the Chief Strategist to validate the Head Draftsman's plans against the client's vision."
        Args:
            commission_id: The ID of the commission.
            blueprint_path: Path to the blueprint.yaml that requires strategic review.
        Returns:
            Path to the generated PM_Review.json file, which contains the PM Agent's decision and rationale.
            This file will be stored in a designated review directory (e.g., /reviews/{commission_id}/).
        """
        # Actual implementation would:
        # 1. Instantiate or invoke the PM Agent.
        # 2. Provide the blueprint_path as input to the PM Agent.
        # 3. The PM Agent analyzes the blueprint and produces PM_Review.json
        #    according to the schema in PM_Review_Schema.md.
        # 4. Return the path to this PM_Review.json.
        pass

    # ... other methods ...
```

### Modification to Existing Workflow Logic

The `WorkshopManager`'s main control loop or state machine will be updated as follows:

1.  After `commission_new_blueprint()` successfully returns a `blueprint_path`:
    *   The `WorkshopManager` will now call `initiate_strategic_review(commission_id, blueprint_path)`.
    *   It will then inspect the `decision` field in the returned `PM_Review.json`.

2.  **If `PM_Review.json` -> `decision` is `APPROVED`:**
    *   The workflow proceeds as before: The `WorkshopManager` calls `request_product_generation_or_revision()` using the approved Blueprint.

3.  **If `PM_Review.json` -> `decision` is `REVISION_REQUESTED`:**
    *   The `WorkshopManager` must **not** proceed to product generation.
    *   Instead, it should invoke a process similar to `request_blueprint_revision()`, but specifically using the feedback from `PM_Review.json`.
    *   A new conceptual method or an overloaded `request_blueprint_revision` might be suitable:

    ```python
    # Option A: New specific method
    def request_blueprint_strategic_revision(
        self,
        commission_id: str,
        original_blueprint_path: Path,
        pm_review_path: Path # Path to the PM_Review.json with REVISION_REQUESTED
    ) -> Path:
        """
        Sends a Blueprint back to a Planner Artisan for revision based on strategic feedback from the PM Agent.
        Metaphor: "Manager sends flawed design back to Design Studio with Chief Strategist's notes."
        Args:
            commission_id: The ID of the commission.
            original_blueprint_path: Path to the blueprint that needs revision.
            pm_review_path: Path to the PM_Review.json detailing required strategic changes.
        Returns:
            Path to the revised blueprint.yaml.
        """
        # 1. The Planner Artisan is invoked.
        # 2. The Planner Artisan receives the original blueprint and the PM_Review.json.
        # 3. The Planner Artisan revises the blueprint, updating its version and notes.
        # 4. The revised blueprint is saved, and its path is returned.
        pass
    ```
    *   After the Planner Artisan submits a revised Blueprint, this new Blueprint **must undergo another PM review** by calling `initiate_strategic_review()` again. This loop continues until a Blueprint version is `APPROVED` by the PM Agent.

## 3. Updated End-to-End Workflow

This updated workflow explicitly incorporates the "PM Review" step, referencing and expanding upon the sequence from `First_Commission_Walkthrough.md`.

**Commission Brief (Client Request):** (Same as original walkthrough)

---

**UPDATED Commission Journey**

1.  **Commission Acceptance & Initial Blueprinting:**
    *   The **Workshop Manager** receives the Commission.
    *   A unique `commission_id` is assigned.
    *   The Manager assigns the task to a **Planner Artisan** via `commission_new_blueprint()`.
    *   The Planner Artisan drafts `blueprints/<commission_id>/blueprint.yaml` (e.g., `blueprint_v1.0.yaml`).

2.  **NEW: Strategic PM Review (Phase 1):**
    *   The **Workshop Manager** takes the newly created `blueprint_v1.0.yaml`.
    *   The Manager calls `initiate_strategic_review(commission_id, path_to_blueprint_v1.0.yaml)`.
    *   The **PM Agent** analyzes `blueprint_v1.0.yaml` based on its Charter.
    *   The PM Agent generates `reviews/<commission_id>/pm_review_for_v1.0.json`.
    *   **Scenario A: `decision: "REVISION_REQUESTED"`**
        *   `rationale` might be: "The key_objectives are not fully aligned with the project_summary. Objective 3 seems to introduce scope creep for an MVP."
        *   `suggested_focus_areas_for_revision` points to specific objectives.
        *   The **Workshop Manager** calls `request_blueprint_strategic_revision(commission_id, path_to_blueprint_v1.0.yaml, path_to_pm_review_for_v1.0.json)`.
        *   The **Planner Artisan** revises the Blueprint based on `pm_review_for_v1.0.json`, creating `blueprint_v1.1.yaml` (version updated in the YAML).
        *   **The workflow returns to the beginning of Step 2 (Strategic PM Review) with `blueprint_v1.1.yaml`**. This loop continues until a blueprint is `APPROVED`.
    *   **Scenario B: `decision: "APPROVED"`**
        *   `rationale` confirms strategic alignment.
        *   The workflow proceeds to Step 3. Let's assume `blueprint_v1.0.yaml` (or a revised `blueprint_v1.x.yaml`) is now `APPROVED`.

3.  **First Product Iteration (The First Draft):**
    *   The **Workshop Manager**, having an `APPROVED` Blueprint (e.g., `blueprint_approved.yaml`), assigns it to a **Coder Artisan** via `request_product_generation_or_revision()`.
    *   The Coder Artisan crafts `product_v1` based on `blueprint_approved.yaml`.

4.  **First Quality Inspection:**
    *   The **Workshop Manager** assigns `product_v1` to **Inspector Artisans** via `initiate_quality_inspection()`.
    *   Inspectors generate `inspection_report_v1.json`.
    *   `recommendation` might be `"requires_revision"` or `"escalate_for_re_planning"`.

5.  **Revision Cycle(s) / Re-Planning:**
    *   **If `requires_revision` (Product Flaws):**
        *   The **Workshop Manager** sends `product_v1` and `inspection_report_v1.json` back to the **Coder Artisan** via `request_product_generation_or_revision()`.
        *   Coder produces `product_v2`.
        *   Workflow returns to Step 4 (Quality Inspection) for `product_v2`.
    *   **If `escalate_for_re_planning` (Fundamental Blueprint Flaws discovered during implementation/inspection):**
        *   This implies the initial PM Review might have missed something subtle, or the act of building revealed deeper issues not apparent at the pure planning stage.
        *   The **Workshop Manager** calls `request_blueprint_revision()` (the existing one for deep technical re-planning, potentially including the problematic inspection report as part of `failure_history`).
        *   The **Planner Artisan** revises the Blueprint (e.g., creating `blueprint_approved_v2.0.yaml`).
        *   **Crucially, this revised Blueprint MUST loop back to Step 2: Strategic PM Review** to ensure the re-plan is still strategically sound before more coding work is done.

6.  **Further Quality Inspections & Revisions:**
    *   Continue iterating between product revisions (Step 3, then 4, then 5) until an inspection report recommends `"approve_for_delivery"`.

7.  **Final Approval & Commission Completion:**
    *   The **Workshop Manager** reviews the final `inspection_report.json` with `recommendation: "approve_for_delivery"`.
    *   The Manager finalizes the commission via `finalize_commission_and_deliver()`.

---

## 4. Diagram of Modified Workflow Snippet

```
+---------------------------------+
| Planner Artisan creates/revises |
| Blueprint (e.g., v1.0)          |
+---------------------------------+
          |
          v
+---------------------------------+
| WorkshopManager calls           |
| initiate_strategic_review()     |
+---------------------------------+
          |
          v
+---------------------------------+      +---------------------------------+
| PM Agent reviews Blueprint      |----->| PM_Review.json generated        |
| Generates PM_Review.json        |      | (path returned to WorkshopMgr)  |
+---------------------------------+      +---------------------------------+
          |
          v
+--------------------------------------------+
| WorkshopManager checks PM_Review.decision  |
+--------------------------------------------+
          |
          +---------------------+----------------------+
          | (REVISION_REQUESTED)|                      | (APPROVED)
          v                     v                      v
+-------------------------+   +--------------------------+   +-------------------------+
| WorkshopManager calls   |   | Planner Artisan revises  |   | WorkshopManager calls   |
| request_blueprint_      |   | Blueprint based on PM    |   | request_product_        |
| strategic_revision()    |   | Review (e.g., v1.1)      |   | generation_or_revision()|
| (passing PM_Review.json)|   +--------------------------+   +-------------------------+
+-------------------------+               |                            |
          ^                             |                            v
          |                             |                      (Proceed to
          +-----------------------------+                       Product Dev
                                                              & QA Cycles)
```

## 5. Implications

*   **Upfront Strategic Validation:** Reduces risk of building the wrong product.
*   **Iterative Blueprint Refinement:** Allows for strategic adjustments before costly development.
*   **Clearer Guidance for Planners:** `PM_Review.json` provides specific, actionable feedback.
*   **Potential for Increased Initial Latency:** The added review step will take time. However, this is expected to be offset by reduced rework later.
*   **WorkshopManager Complexity:** The manager's logic becomes more sophisticated to handle the review and revision loop at the blueprinting stage.

This integration plan provides a clear path for incorporating the PM Agent and its strategic review process into the existing Gandalf Workshop workflow.
