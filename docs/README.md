# Welcome to the Gandalf Workshop Documentation

This documentation provides a comprehensive overview of the Gandalf Workshop, an autonomous agentic system designed to produce high-quality software MVPs and verifiable research reports.

The goal of this documentation is to offer clarity for various stakeholders, from those seeking a high-level understanding of the Workshop's strategy and capabilities to developers looking for operational details and setup guides.

## Navigating These Docs

The documentation is organized into the following main sections:

1.  **[Version Roadmap (`VERSION_ROADMAP.md`)]**: Outlines the phased development plan for the Gandalf Workshop, detailing current priorities (MVP, Viability) and future aspirations. Start here to understand the project's trajectory.

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
