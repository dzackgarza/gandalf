"""
workshop_manager.py - The Office of the Workshop Manager (Orchestrator)

This module houses the WorkshopManager class, the central intelligence of the
Gandalf Workshop. The Manager oversees all operations, from commissioning new
Blueprints to approving final Products for delivery. It's akin to the master
artisan or foreman who directs the workflow, assigns tasks to specialized
artisans (AI agents/crews), and ensures quality standards are met throughout
the creation process.
"""

import logging
from pathlib import Path

# from typing import Optional, Dict # No longer used in V1
# from datetime import datetime, timezone # No longer used in V1

# Import the mock artisan crew and data models
from gandalf_workshop.artisan_guildhall.artisans import (
    initialize_live_planner_agent,
    initialize_live_coder_agent, # Changed from initialize_coder_agent_v1
    initialize_auditor_agent_v1,
)

# from gandalf_workshop.specs.data_models import PMReview, PMReviewDecision # Not used in V1 simple loop
from gandalf_workshop.specs.data_models import (
    PlanOutput,
    CodeOutput,
    AuditOutput,
    AuditStatus,
)

logger = logging.getLogger(__name__)


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
        logger.info("Workshop Manager (V1) initialized.")

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
        logger.info(f"===== Starting V1 Workflow for Commission: {commission_id} =====")
        logger.info(f"User Prompt: {user_prompt}")

        # 1. Call Planner Agent
        logger.info(f"Workshop Manager: Invoking Live Planner Agent for '{commission_id}'.") # Log message updated
        plan_output = initialize_live_planner_agent(user_prompt, commission_id) # Function call updated
        # Ensure the log statement below adheres to line length
        plan_tasks_str = str(plan_output.tasks)
        if len(plan_tasks_str) > 50:  # Arbitrary short length for log
            plan_tasks_str = plan_tasks_str[:47] + "..."
        logger.info(f"Workshop Manager: Planner Agent returned plan: {plan_tasks_str}")

        # 2. Call Coder Agent
        logger.info(f"Workshop Manager: Invoking Coder Agent for '{commission_id}'.")
        commission_specific_work_dir = (
            Path("outputs") / commission_id
        )
        # The Coder agent will create this directory if it doesn't exist.
        code_output = initialize_live_coder_agent( # Function call updated
            plan_input=plan_output,
            commission_id=commission_id,
            output_target_dir=commission_specific_work_dir,
        )
        logger.info(
            f"Workshop Manager: Live Coder Agent completed. Code path: {code_output.code_path}, Message: {code_output.message}" # Log updated
        )
        # It's possible the live agent returns the directory path on certain errors,
        # so check if the path is a file and exists.
        if not code_output.code_path.is_file() or not code_output.code_path.exists():
            logger.error(f"Live Coder Agent failed to create a valid code file at {code_output.code_path}. Message: {code_output.message}")
            # Consider the message from CodeOutput to make the error more informative
            error_message = code_output.message or f"Live Coder Agent was supposed to create a file at {code_output.code_path} but it was not found or is not a file."
            raise FileNotFoundError(error_message)

        # 3. Call Auditor Agent
        logger.info(f"Workshop Manager: Invoking Auditor Agent for '{commission_id}'.")
        audit_output = initialize_auditor_agent_v1(
            code_input=code_output, commission_id=commission_id
        )
        logger.info(
            f"Workshop Manager: Auditor Agent reported: {audit_output.status} - {audit_output.message}"
        )

        if audit_output.status == AuditStatus.FAILURE:
            logger.error(
                f"Workshop Manager: Commission '{commission_id}' failed audit. Reason: {audit_output.message}"
            )
            # In a real V1, we might raise an exception or return a specific indicator of failure.
            # For now, we'll let it proceed but the message indicates failure.
            # Consider raising an exception for clearer failure handling:
            raise Exception(
                f"Audit failed for commission '{commission_id}': {audit_output.message}"
            )

        logger.info(
            f"===== V1 Workflow for Commission: {commission_id} Completed Successfully ====="
        )
        return code_output.code_path

    # --- Methods from older, more complex workflow (commented out for V1 focus) ---
    # All legacy methods previously here have been removed.
