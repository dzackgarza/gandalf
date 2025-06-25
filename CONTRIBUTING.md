# Contributing to the Gandalf Workshop

Thank you for your interest in contributing to the Gandalf Workshop! This document provides guidelines to ensure a smooth and effective development process.

## Finding Your Tasks and Branches

The core of our development is organized into versions (V1, V2, etc.). Each version has a detailed plan, including specific tasks and their corresponding development branches.

1.  **Primary Task Source:** All development tasks, branch names, and progress tracking are located in version-specific Markdown files within the `docs/roadmap/` directory.
    *   For Version 1 tasks, refer to `docs/roadmap/V1.md`.
    *   For Version 2 tasks, refer to `docs/roadmap/V2.md`.
    *   And so on for subsequent versions.

2.  **Roadmap Overview:** For a higher-level understanding of how these versions fit together, you can consult `docs/VERSION_ROADMAP.md`.

## Development Workflow

1.  **Identify Your Task:** Go to the relevant `docs/roadmap/Vn.md` file for the current development version. Find an unassigned task (an unchecked item in the checklist) that you will be working on.
2.  **Branch Naming Convention:** Create your development branch using the exact name specified in the `Vn.md` file. Our standard format is:
    `feature/V<version>-<component>-<short-description>`
    *   Example: `feature/V1-orchestrator-loop`
    *   Example: `feature/V2-coder-llm-integration`
    Adhering to this naming convention is crucial for tracking and integration.
3.  **Develop Your Feature:** Implement the required functionality for your assigned task on your branch. Ensure your code is clean, well-commented, and adheres to any project-specific coding standards (to be detailed elsewhere as the project evolves).
4.  **Test Your Changes:** (Specific testing guidelines will be added as the project matures. For V1, ensure your component integrates into the end-to-end test.)
5.  **Update Progress in `Vn.md`:** **Before pushing your changes and creating a Pull Request**, you **MUST** update the relevant `docs/roadmap/Vn.md` file:
    *   Locate your assigned task/branch in the checklist.
    *   Mark it as complete by changing `[ ]` to `[x]`.
    *   Commit this change to your feature branch. This acts as a clear signal that the work for that branch is considered done by you.
    *   Example commit message for this update: `docs: Mark feature/V1-orchestrator-loop as complete in V1.md`
6.  **Push and Create Pull Request:**
    *   Push your feature branch (including the `Vn.md` update) to the repository.
    *   Create a Pull Request (PR) against the main development branch (e.g., `main` or a version-specific integration branch, to be defined).
    *   Ensure your PR description clearly outlines the changes made and references the task from `Vn.md`.

## Code Style and Quality

*   Our Python code is formatted with Black and linted with Flake8. Please ensure your contributions pass these checks (e.g., by running `make audit`).
*   **Line Length:** While Flake8 is configured with a specific line length, very long lines (e.g., up to 200 characters) are generally acceptable if they improve readability, especially for comments or string literals. The Flake8 configuration has been updated to reflect this.
*   **F401 - Unused Imports for Type Hinting:** If an import is flagged by Flake8 with an F401 error (module imported but unused) but the import is necessary for type hinting, you can suppress this specific error by adding a `# noqa: F401` comment to the import line. Please verify that the import is indeed only used for type hinting before suppressing.

## Questions?

*   (To be defined - e.g., preferred communication channels for questions)

By following these guidelines, we can maintain a clear, organized, and efficient development process. Welcome to the team!
