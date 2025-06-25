# Welcome to the Gandalf Workshop Documentation

This documentation provides a comprehensive overview of the Gandalf Workshop, an autonomous agentic system designed to produce high-quality software MVPs and verifiable research reports.

The goal of this documentation is to offer clarity for various stakeholders, from those seeking a high-level understanding of the Workshop's strategy and capabilities to developers looking for operational details and setup guides.

For information on how to contribute to the Gandalf Workshop, please see the [CONTRIBUTING.md](../CONTRIBUTING.md) file in the root of the repository.

## Navigating These Docs

The documentation is organized into the following main sections:

1.  **[Overall Version Roadmap (`VERSION_ROADMAP.md`)]**: Provides a high-level overview of the project's development phases and vision. For detailed, version-specific plans and branch-level tasks, see the roadmaps in the `roadmap/` directory:
    *   **[V1 Roadmap (`roadmap/V1.md`)]**: Focuses on the E2E testable basic application.
    *   **[V2 Roadmap (`roadmap/V2.md`)]**: Details plans for enhanced agent capabilities and collaboration.

2.  **[Strategic Overview (`1_strategic_overview/README.md`)]**: Delves into the foundational design and technological choices behind the Gandalf Workshop.
    *   `high_level_design.md`: Describes the core architecture, the validation-centric pipeline, quantitative process control, and autonomous intervention protocols.
    *   `technology_stack.md`: Details the agentic frameworks (e.g., CrewAI, AutoGen) and layering strategy used in the Workshop.

3.  **[Operational Framework (`2_operational_framework/README.md`)]**: Explains how the Gandalf Workshop functions on a day-to-day basis.
    *   `workshop_workflow.md`: Illustrates the end-to-end process of a commission, from initial request through planning, Product Manager review, iterative development, and automated auditing.
    *   `artisan_charters/`: Contains the "charters" for each specialized agent role within the workshop (Planner, Coder, Audit Agent, PM Agent), defining their responsibilities and guiding principles.
    *   `communication_protocols.md`: Specifies the data schemas and formats (e.g., Blueprints, Audit Receipts) used for communication between agents and the Workshop Manager.

4.  **[Guides and References (`3_guides_and_references/README.md`)]**: Provides practical information for setting up and interacting with the Gandalf Workshop.
    *   `workshop_setup.md`: Step-by-step instructions for setting up the development environment.
    *   `workshop_directory.md`: An overview of the Gandalf Workshop's directory structure and the purpose of each key location.

## Core Principles

The Gandalf Workshop is built upon principles of:

*   **Autonomy:** Minimizing human intervention in the generation and validation process.
*   **Verifiability:** Ensuring outputs are reliable and meet defined quality standards through rigorous automated auditing.
*   **Iterative Improvement:** Employing cyclical processes for progressive refinement of products.
*   **Strategic Alignment:** Ensuring that all development efforts are aligned with the overarching goals of a commission via mechanisms like the Product Manager Agent review.

We encourage you to explore these documents to gain a deeper understanding of the Gandalf Workshop's capabilities and design.
