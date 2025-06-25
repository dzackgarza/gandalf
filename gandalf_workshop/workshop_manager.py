"""
workshop_manager.py - The Office of the Workshop Manager (Orchestrator)

This module houses the WorkshopManager class, the central intelligence of the
Gandalf Workshop. The Manager oversees all operations, from commissioning new
Blueprints to approving final Products for delivery. It's akin to the master
artisan or foreman who directs the workflow, assigns tasks to specialized
artisans (AI agents/crews), and ensures quality standards are met throughout
the creation process.
"""

# import json # No longer used in V1
# import yaml # No longer used in V1
from pathlib import Path

# from typing import Optional, Dict # No longer used in V1
# from datetime import datetime, timezone # No longer used in V1

# Import the mock artisan crew and data models
from gandalf_workshop.artisan_guildhall.artisans import initialize_planner_agent_v1

# from gandalf_workshop.specs.data_models import PMReview, PMReviewDecision # Not used in V1 simple loop
from gandalf_workshop.specs.data_models import (
    PlanOutput,
    CodeOutput,
    AuditOutput,
    AuditStatus,
)

# Placeholder for actual agent imports or direct function calls for V1
# from gandalf_workshop.artisan_guildhall.artisans import (
#     initialize_coder_agent_v1,
#     initialize_auditor_agent_v1
# )


class WorkshopManager:
    """
    The Workshop Manager directs the V1 workflow of the Gandalf workshop,
    sequentially invoking Planner, Coder, and Auditor agents.
    """

    def __init__(self):
        """
        Initializes the Workshop Manager for V1.
        """
        # For V1, initialization is simple.
        # Future versions might load configurations or connect to agent frameworks.
        print("Workshop Manager (V1) initialized.")

    def run_v1_commission(
        self, user_prompt: str, commission_id: str = "v1_commission"
    ) -> Path:
        """
        Orchestrates the V1 commission workflow: Planner -> Coder -> Auditor.
        Args:
            user_prompt: The initial request from the client.
            commission_id: A unique ID for this commission.
        Returns:
            Path to the final generated product if successful, otherwise raises an exception.
        """
        print(f"\n===== Starting V1 Workflow for Commission: {commission_id} =====")
        print(f"User Prompt: {user_prompt}")

        # 1. Call Planner Agent
        print(f"Workshop Manager: Invoking Planner Agent for '{commission_id}'.")
        plan_output = initialize_planner_agent_v1(user_prompt, commission_id)
        # Ensure the print statement below adheres to line length
        plan_tasks_str = str(plan_output.tasks)
        if len(plan_tasks_str) > 50:  # Arbitrary short length for log
            plan_tasks_str = plan_tasks_str[:47] + "..."
        print(f"Workshop Manager: Planner Agent returned plan: {plan_tasks_str}")

        # 2. Call Coder Agent
        # This will be replaced by actual agent call in later steps
        # coder_agent = initialize_coder_agent_v1() # Conceptual
        # code_output = coder_agent.generate_code(plan_output, commission_id)
        print(f"Workshop Manager: Invoking Coder Agent for '{commission_id}'.")
        # Mock Coder Output for now
        # Let's assume it creates a file in a temporary commission-specific directory
        commission_work_dir = Path("gandalf_workshop/commission_work") / commission_id
        commission_work_dir.mkdir(parents=True, exist_ok=True)

        if plan_output.tasks == ["Create a Python file that prints 'Hello, World!'"]:
            output_file = commission_work_dir / "hello.py"
            with open(output_file, "w") as f:
                f.write("print('Hello, World!')\n")
            code_output = CodeOutput(
                code_path=output_file, message="Python 'Hello, World!' generated."
            )
            print(
                f"Workshop Manager: Coder Agent generated code at: {code_output.code_path}"
            )
        else:
            # Generic placeholder file for other prompts
            output_file = commission_work_dir / "output.txt"
            with open(output_file, "w") as f:
                f.write(
                    f"Content for: {user_prompt}\nBased on plan: {plan_output.tasks}"
                )
            code_output = CodeOutput(
                code_path=output_file, message=f"Generated content for {user_prompt}."
            )
            print(
                f"Workshop Manager: Coder Agent generated code at: {code_output.code_path}"
            )
            # raise NotImplementedError(f"V1 Coder cannot handle plan: {plan_output.tasks}")

        # 3. Call Auditor Agent
        # This will be replaced by actual agent call in later steps
        # auditor_agent = initialize_auditor_agent_v1() # Conceptual
        # audit_output = auditor_agent.audit_code(code_output, commission_id)
        print(f"Workshop Manager: Invoking Auditor Agent for '{commission_id}'.")
        # Mock Auditor Output for now
        if code_output.code_path.name == "hello.py":
            audit_output = AuditOutput(
                status=AuditStatus.SUCCESS,
                message="Audit passed for 'Hello, World!'.",
                report_path=None,
            )
            print(
                f"Workshop Manager: Auditor Agent reported: {audit_output.status} - {audit_output.message}"
            )
        else:
            audit_output = AuditOutput(
                status=AuditStatus.SUCCESS,
                message="Audit passed for generic content.",
                report_path=None,
            )
            print(
                f"Workshop Manager: Auditor Agent reported: {audit_output.status} - {audit_output.message}"
            )
            # audit_output = AuditOutput(status=AuditStatus.FAILURE, message="Audit failed for unknown code.", report_path=None)
            # print(f"Workshop Manager: Auditor Agent reported: {audit_output.status} - {audit_output.message}")

        if audit_output.status == AuditStatus.FAILURE:
            print(
                f"Workshop Manager: Commission '{commission_id}' failed audit. Reason: {audit_output.message}"
            )
            # In a real V1, we might raise an exception or return a specific indicator of failure.
            # For now, we'll let it proceed but the message indicates failure.
            # Consider raising an exception for clearer failure handling:
            raise Exception(
                f"Audit failed for commission '{commission_id}': {audit_output.message}"
            )

        print(
            f"===== V1 Workflow for Commission: {commission_id} Completed Successfully ====="
        )
        return code_output.code_path

    # --- Methods from older, more complex workflow (commented out for V1 focus) ---
    # All legacy methods previously here have been removed.
