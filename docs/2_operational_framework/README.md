# Operational Framework

This section details the operational mechanics of the Gandalf Workshop, explaining how commissions are processed and how different agentic components collaborate to produce and validate artifacts.

Understanding these documents will clarify the step-by-step workflow, the roles and responsibilities of various automated "Artisans," and the data formats they use to communicate.

## Key Documents

*   **[Workshop Workflow (`workshop_workflow.md`)]**: This document provides a comprehensive walkthrough of a typical commission's lifecycle within the Gandalf Workshop. It illustrates the flow from initial planning and strategic review by the Product Manager (PM) Agent, through iterative development by Coder Artisans, to the final automated auditing stages. (This will be developed from the existing `First_Commission_Walkthrough.md`).

*   **[Artisan Charters (`artisan_charters/README.md`)]**: This subdirectory contains the detailed "charters" for each specialized agent role within the workshop. These charters define their core responsibilities, guiding principles, inputs, and outputs.
    *   `planner_charter.md`
    *   `coder_charter.md`
    *   `audit_agent_charter.md`
    *   `pm_agent_charter.md`

*   **[Communication Protocols (`communication_protocols.md`)]**: This crucial document specifies the standardized data schemas (e.g., YAML for Blueprints, JSON for PM Reviews, Markdown for Audit Receipts, Gherkin for BDD tests) and conceptual interaction patterns used between the Workshop Manager and the various Artisans. It is the definitive guide to the "paperwork" of the Workshop.

These documents collectively describe the engine of the Gandalf Workshop and how its parts interact to achieve its goals.
