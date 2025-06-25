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
    initialize_planner_agent_v1,
    initialize_coder_agent_v1,
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
        # The Coder agent (initialize_coder_agent_v1) is responsible for creating
        # this directory if it doesn't exist.
        code_output = initialize_coder_agent_v1(
            plan_input=plan_output,
            commission_id=commission_id,
            output_target_dir=commission_specific_work_dir,
            llm_config=self.llm_config # Pass the LLM configuration to the Coder
        )
        logger.info(
            f"Workshop Manager: Coder Agent completed. Code path: {code_output.code_path}, Message: {code_output.message}"
        )
        if not code_output.code_path.exists():
            # This case should ideally be handled by the Coder agent returning an error CodeOutput
            # or raising an exception that WorkshopManager catches.
            # For now, an explicit check.
            logger.error(f"Coder Agent failed to create file at {code_output.code_path}")
            raise FileNotFoundError(
                f"Coder Agent was supposed to create a file at {code_output.code_path} but it was not found."
            )

        # 3. Call Auditor Agent
        # Assuming Auditor does not need LLM for V1.
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
