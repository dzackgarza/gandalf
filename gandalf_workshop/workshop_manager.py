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
from typing import Optional, Dict, Any # Added Optional, Dict, Any

# from datetime import datetime, timezone # No longer used in V1

# Import the LLMProviderManager
from gandalf_workshop.llm_provider_manager import LLMProviderManager

# Import the mock artisan crew and data models
from gandalf_workshop.artisan_guildhall.artisans import (
    initialize_live_planner_agent,
    initialize_live_coder_agent, # Changed from initialize_coder_agent_v1
    initialize_auditor_agent_v1,
    initialize_live_auditor_agent, # Added new live auditor
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
    It now also initializes and uses an LLMProviderManager to configure LLMs.
    """

    def __init__(self, preferred_llm_provider: Optional[str] = None):
        """
        Initializes the Workshop Manager for V1.
        It also initializes the LLMProviderManager to find a working LLM.
        Args:
            preferred_llm_provider (Optional[str]): The name of the preferred LLM provider.
        """
        logger.info("Workshop Manager (V1) initializing...")
        self.llm_provider_manager = LLMProviderManager()
        self.llm_config: Optional[Dict[str, Any]] = self.llm_provider_manager.get_llm_provider(
            preferred_provider=preferred_llm_provider
        )

        if not self.llm_config:
            logger.error("Workshop Manager: CRITICAL - No operational LLM provider found. Cannot proceed with commissions.")
            # This state should ideally prevent commission processing.
        else:
            logger.info(f"Workshop Manager: Successfully configured LLM provider: {self.llm_config.get('provider_name', 'Unknown')}")
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

        if not self.llm_config:
            logger.error(f"Workshop Manager: Cannot run commission '{commission_id}'. No LLM provider configured during initialization.")
            raise ConnectionError("LLM provider not available. Commission cannot be processed.")

        # 1. Call Planner Agent
        # Assuming Planner does not need LLM for V1. If it did, self.llm_config would be passed.
        logger.info(f"Workshop Manager: Invoking Planner Agent for '{commission_id}'.")
        plan_output = initialize_planner_agent_v1(user_prompt, commission_id)
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
            llm_config=self.llm_config # Pass the LLM configuration to the Coder
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
        # Assuming Auditor does not need LLM for V1.
        logger.info(f"Workshop Manager: Invoking Auditor Agent for '{commission_id}'.")
        audit_output = initialize_auditor_agent_v1(
            code_input=code_output, commission_id=commission_id
        )
        logger.info(
            f"Workshop Manager: Syntax Auditor Agent reported: {syntax_audit_output.status} - {syntax_audit_output.message}"
        )

        if syntax_audit_output.status == AuditStatus.FAILURE:
            logger.error(
                f"Workshop Manager: Commission '{commission_id}' failed syntax audit. Reason: {syntax_audit_output.message}"
            )
            raise Exception(
                f"Syntax audit failed for commission '{commission_id}': {syntax_audit_output.message}"
            )

        # If syntax check passes, proceed to Live LLM Auditor
        logger.info(f"Workshop Manager: Invoking Live Auditor Agent for '{commission_id}'.")

        # Read the generated code to pass as string
        try:
            with open(code_output.code_path, "r", encoding="utf-8") as f:
                generated_code_str = f.read()
        except Exception as e:
            logger.error(f"Workshop Manager: Failed to read generated code file {code_output.code_path}. Error: {e}")
            raise Exception(f"Failed to read generated code file for live audit: {e}")

        live_audit_output = initialize_live_auditor_agent(
            generated_code=generated_code_str,
            plan_input=plan_output, # Pass the plan_output from the planner
            commission_id=commission_id
        )
        logger.info(
            f"Workshop Manager: Live Auditor Agent reported: {live_audit_output.status} - {live_audit_output.message}"
        )

        if live_audit_output.status == AuditStatus.FAILURE:
            logger.error(
                f"Workshop Manager: Commission '{commission_id}' failed live semantic audit. Reason: {live_audit_output.message}"
            )
            raise Exception(
                f"Live semantic audit failed for commission '{commission_id}': {live_audit_output.message}"
            )

        logger.info(
            f"===== V1 Workflow for Commission: {commission_id} Completed Successfully ====="
        )
        return code_output.code_path

    # --- Methods from older, more complex workflow (commented out for V1 focus) ---
    # All legacy methods previously here have been removed.
