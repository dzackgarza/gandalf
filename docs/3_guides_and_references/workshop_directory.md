# Workshop Layout

This document outlines the physical and logical layout of the Gandalf Workshop. Each area (directory) has a specific purpose, ensuring that all tools, materials, and ongoing Commissions are well-organized and easily accessible to the Workshop Manager and the Specialist Artisans.

## 1. Workshop Blueprint (Directory Structure)

The following diagram illustrates the main areas of the Gandalf Workshop:

```
gandalf_workshop/
├── .venv/                      # The dedicated toolset and machinery for the workshop
├── .env                        # Secure storage for the workshop's keys
├── requirements.txt            # The master list of all tools required
├── workshop_manager.py         # The office of the Workshop Manager (Orchestrator)
│
├── blueprints/                 # Design Studio: Where Blueprints for Commissions are stored
│   └── commission_id_123/
│       └── blueprint.yaml      # The detailed plan for a specific Commission
│
├── commissions_in_progress/    # Main Workbench: Active workspace for ongoing Commissions
│   └── commission_id_123/      # Each Commission gets its own bench
│       ├── product_v1/         # Version 1 of the artifact being built
│       ├── product_v2/         # Version 2, after revisions
│       └── ...                 # Further iterations
│
├── completed_commissions/      # Finished Goods Storage: Where completed Products are stored
│   └── commission_id_123/
│       ├── final_product/      # The final, approved artifact
│       └── inspection_report.json # The final Quality Inspection Report
│
├── artisan_guildhall/          # Artisan's Quarters & Guild Library
│   ├── planners/               # Charters and tools for Planner Artisans
│   │   └── software_architect_charter.md
│   │   └── lead_researcher_charter.md
│   ├── coders/                 # Charters and tools for Coder Artisans
│   │   └── python_coder_charter.md
│   └── inspectors/             # Charters and tools for Inspector Artisans
│       ├── general_inspector_charter.md
│       └── specialized_inspectors/
│           ├── spec_compliance_inspector_charter.md
│           └── security_auditor_inspector_charter.md
│           └── ...
│
├── quality_control_lab/        # Inspection Area: Where Products undergo Quality Inspection
│   └── commission_id_123/
│       ├── product_v1_inspection_report.json
│       └── product_v2_inspection_report.json
│
└── workshop_logs/              # Record Room: Logs of all workshop activities
    └── manager.log             # Workshop Manager's operational logs
    └── commission_id_123.log   # Specific log for a Commission
```

## 2. Area Descriptions

*   **`gandalf_workshop/` (The Workshop Entrance)**: The main entrance and overview of the entire Gandalf Workshop.
    *   **`.venv/` (The Tool Store & Maintenance Bay)**: This area houses the specific set of tools and machinery (Python virtual environment) required for the workshop's operations. It's kept separate to ensure tools are always in top condition and correctly configured for our specialized work.
    *   **`.env` (The Key Safe)**: A secure location where essential keys (API keys, access tokens) to various resources and restricted areas of the digital world are stored. Access is strictly controlled.
    *   **`requirements.txt` (The Tool Inventory Ledger)**: An official list detailing every standard tool (Python library) that must be available in the workshop. Used for initial setup and periodic checks.
    *   **`workshop_manager.py` (The Workshop Manager's Office)**: The central control room where the Workshop Manager (Orchestrator script) oversees all operations, assigns tasks to Artisans, tracks the progress of Commissions, and makes executive decisions based on Quality Inspection Reports.

*   **`/blueprints/` (The Design Studio)**: This is where the initial designs and plans for each Commission are drafted and stored.
    *   `commission_id_123/blueprint.yaml`: For each Commission, a detailed Blueprint (specification file) is created here by a Planner Artisan. This Blueprint guides all subsequent work.

*   **`/commissions_in_progress/` (The Main Workbench)**: The primary area where Specialist Artisans actively work on crafting the Products for each Commission.
    *   `commission_id_123/`: Each Commission receives its own dedicated space on the workbench.
    *   `product_vX/`: Iterative versions of the Product are stored here as they are developed and refined by the Coder Artisans, allowing for review and rollback if needed.

*   **`/completed_commissions/` (The Finished Goods Storage)**: This secure area is where the final, approved Products are stored after passing all Quality Inspections, along with their final Inspection Reports.
    *   `commission_id_123/final_product/`: The actual deliverable artifact.
    *   `commission_id_123/inspection_report.json`: The comprehensive report detailing the final quality assessment.

*   **`/artisan_guildhall/` (The Artisan's Quarters & Guild Library)**: This area houses the official Charters that define the roles, responsibilities, and guiding principles for each type of Specialist Artisan. It also serves as a library for their specialized tools and knowledge.
    *   `/planners/`, `/coders/`, `/inspectors/`: Specific sections for each guild, containing their respective charters and operational guidelines.

*   **`/quality_control_lab/` (The Inspection Area)**: A dedicated laboratory where Inspector Artisans meticulously examine the Products created on the Main Workbench.
    *   `commission_id_123/product_vX_inspection_report.json`: Each version of a Product undergoes a thorough Quality Inspection, and the findings (Quality Score, identified flaws) are documented in an Inspection Report here. These reports inform the next cycle of revisions.

*   **`/workshop_logs/` (The Record Room)**: This archive stores detailed logs of all activities within the workshop.
    *   `manager.log`: The Workshop Manager's log, detailing high-level operations and decisions.
    *   `commission_id_123.log`: A specific log file for each Commission, tracking its journey through the workshop from start to finish.

This structured layout ensures that every Commission is handled with clarity, precision, and accountability, reflecting the high standards of the Gandalf Workshop.
