# PM_Review.json Schema Definition

This document defines the structure and fields for the `PM_Review.json` file. This file is the output of the Product Manager (PM) Agent after it reviews a `blueprint.yaml`.

## File Format

JSON

## Location

The `PM_Review.json` file will be stored in a location accessible to the WorkshopManager, typically within a structured directory related to the specific commission and review cycle. For example: `reviews/<commission_id>/pm_review_YYYYMMDD_HHMMSS.json` or alongside the blueprint it reviewed. The exact path will be returned by the `initiate_strategic_review` method of the WorkshopManager.

## Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PM Review",
  "description": "Output of the Product Manager Agent's strategic review of a Blueprint.",
  "type": "object",
  "properties": {
    "commission_id": {
      "description": "Unique identifier for the commission, matching the one in blueprint.yaml.",
      "type": "string",
      "examples": ["calc_gui_001", "research_ai_ethics_002"]
    },
    "blueprint_path": {
      "description": "The full path to the blueprint.yaml file that was reviewed.",
      "type": "string",
      "examples": ["blueprints/gui_calc_001/blueprint.yaml"]
    },
    "blueprint_version_reviewed": {
      "description": "The version of the Blueprint that was reviewed (e.g., from the 'revisions' section of the Blueprint).",
      "type": "string",
      "examples": ["1.0", "1.1_revised"]
    },
    "review_timestamp": {
      "description": "Timestamp of when the review was completed, in ISO 8601 format.",
      "type": "string",
      "format": "date-time",
      "examples": ["2023-10-26T10:30:00Z"]
    },
    "pm_agent_id": {
      "description": "Identifier of the PM Agent instance or version performing the review.",
      "type": "string",
      "examples": ["PM_Agent_v1.2"]
    },
    "decision": {
      "description": "The outcome of the PM Agent's review.",
      "type": "string",
      "enum": ["APPROVED", "REVISION_REQUESTED"],
      "examples": ["APPROVED"]
    },
    "rationale": {
      "description": "A detailed natural language explanation for the decision. If REVISION_REQUESTED, this must clearly state the issues found and reference the specific decision criteria from the PM_Agent_Charter.md that were triggered.",
      "type": "string",
      "examples": [
        "The Blueprint is APPROVED. The key_objectives and product_specifications align well with the project_summary, presenting a clear and strategically sound plan for an MVP.",
        "REVISION_REQUESTED: The product_specifications for the 'software_mvp' detail features beyond a minimal viable scope (Criterion: 'Over-engineered for an MVP'). Specifically, module 'reporting_suite' and its components seem premature for an initial version based on the project_summary. Recommend deferring this module to a later iteration."
      ]
    },
    "suggested_focus_areas_for_revision": {
      "description": "Optional: A list of specific sections or aspects of the Blueprint that the Planner Artisan should focus on during revision. This is only present if decision is REVISION_REQUESTED.",
      "type": "array",
      "items": {
        "type": "string"
      },
      "examples": [
        ["product_specifications.modules[1].description", "key_objectives[2]"]
      ],
      "minItems": 1,
      "uniqueItems": true
    }
  },
  "required": [
    "commission_id",
    "blueprint_path",
    "blueprint_version_reviewed",
    "review_timestamp",
    "pm_agent_id",
    "decision",
    "rationale"
  ],
  "if": {
    "properties": { "decision": { "const": "REVISION_REQUESTED" } }
  },
  "then": {
    "required": ["suggested_focus_areas_for_revision"]
  }
}
```

## Field Descriptions

*   **`commission_id` (string, required):**
    Unique identifier for the commission. Must match the `commission_id` in the reviewed `blueprint.yaml`.
*   **`blueprint_path` (string, required):**
    The full path to the `blueprint.yaml` file that this review pertains to. This helps in unambiguously linking the review to the specific blueprint version, especially if multiple blueprint files exist for a commission over time (though the `revisions` array within the blueprint should be the primary versioning mechanism).
*   **`blueprint_version_reviewed` (string, required):**
    The version number of the Blueprint that was analyzed. This should correspond to the latest version entry in the `revisions` section of the `blueprint.yaml`.
*   **`review_timestamp` (string, format: date-time, required):**
    The ISO 8601 timestamp indicating when the PM Agent completed this review.
*   **`pm_agent_id` (string, required):**
    An identifier for the PM Agent that performed the review (e.g., its name, version). This is useful for logging and traceability.
*   **`decision` (enum, required):**
    The PM Agent's final decision.
    *   `APPROVED`: The Blueprint is strategically sound and aligns with the user's commission.
    *   `REVISION_REQUESTED`: The Blueprint has strategic issues and needs to be revised by the Planner Artisan.
*   **`rationale` (string, required):**
    A comprehensive, human-readable explanation for the `decision`.
    *   If `APPROVED`, this should briefly confirm the alignment.
    *   If `REVISION_REQUESTED`, this must detail the strategic misalignments, referencing the specific criteria from `PM_Agent_Charter.md` that were triggered. It should provide enough information for the Planner Artisan to understand the issues and revise the Blueprint effectively.
*   **`suggested_focus_areas_for_revision` (array of strings, conditionally required):**
    This field is **required if and only if `decision` is `REVISION_REQUESTED`**.
    It provides a list of specific pointers or paths within the `blueprint.yaml` (e.g., using dot notation like `product_specifications.modules[0].description`, or descriptive text like "Key Objective 3") that the Planner Artisan should pay particular attention to when making revisions. This helps to quickly guide the revision process.

This schema ensures that the PM Agent's feedback is structured, consistent, and provides all necessary information for the WorkshopManager and Planner Artisans to act upon.
