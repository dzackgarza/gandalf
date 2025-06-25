# Jules Instructions

**Project:** Gandalf Workshop

**Your Current State & Context:**
*   You have just successfully completed a task to create detailed, versioned roadmaps for the Gandalf Workshop documentation.
*   This involved:
    *   Creating `docs/roadmap/V1.md` and `docs/roadmap/V2.md`.
    *   Revising `docs/VERSION_ROADMAP.md` to link to these new detailed roadmaps.
    *   Updating `docs/README.md` to reflect the new roadmap structure and link to `CONTRIBUTING.md`.
*   All these changes have been committed to the `docs/versioned-roadmaps` branch and submitted.
*   The repository now has a more structured and detailed approach to its development roadmap documentation.

**Next Steps & Focus Areas:**

The immediate next steps should focus on beginning the implementation of the V1 roadmap. Based on `docs/roadmap/V1.md`, the following are high-priority areas:

1.  **Establish `develop/V1` Branch:**
    *   If it doesn't exist, create a `develop/V1` integration branch from the current `main` or an appropriate base. This branch will be where `feature/V1-*` branches are merged.

2.  **Begin V1 Feature Implementation (Prioritize Core Workflow):**
    *   **`feature/V1-orchestrator-loop`**: This is fundamental. The Workshop Manager needs its basic sequential execution loop.
        *   Refer to `gandalf_workshop/workshop_manager.py`.
        *   Focus on the state management and transitions between placeholder agent tasks initially.
    *   **`feature/V1-communication-protocol`**: Define and implement the initial data structures or schemas for how the orchestrator will pass information to and receive information from the agents.
        *   Refer to `gandalf_workshop/specs/data_models.py` and `docs/2_operational_framework/communication_protocols.md` for existing ideas, but ensure V1 focuses on simplicity.
    *   **`feature/V1-planner-agent-basic`**: Develop a rudimentary Planner agent.
        *   Refer to `gandalf_workshop/artisan_guildhall/artisans.py` and relevant prompts in `gandalf_workshop/artisan_guildhall/prompts.py`.
        *   The V1 planner should be able to take a simple prompt and produce a basic, structured plan (e.g., a list of steps as a string or simple list in the defined communication protocol).

**General Guidance for Next Iteration:**

*   **Follow Test-Driven Development (TDD):** For any new Python code (orchestrator logic, agent functionality), write tests first.
    *   Look at existing tests in `gandalf_workshop/tests/` for examples.
    *   Ensure `Makefile` targets like `test` or `lint` are used and pass.
*   **Adhere to `CONTRIBUTING.md`:** This file now exists and should provide guidelines for development.
*   **Branching Strategy:**
    *   Create specific `feature/V1-*` branches for each component as outlined in `docs/roadmap/V1.md`.
    *   Merge completed features into `develop/V1`.
*   **Small, Atomic Commits:** Keep commits focused on a single logical change.
*   **Consult Documentation:** The `docs/` folder is now significantly improved. Use it as a reference for architecture, agent roles, and the V1 plan.
*   **AGENTS.md:** Always check for and adhere to instructions in any `AGENTS.md` files relevant to the files you are modifying. (As of now, there isn't one at the root, but this is a general reminder).

**If Ambiguity Arises:**
*   Refer to the detailed V1 roadmap (`docs/roadmap/V1.md`).
*   If the roadmap is unclear or a design decision is needed, use `request_user_input`.

Good luck with V1 implementation!Tool output for `create_file_with_block`:
