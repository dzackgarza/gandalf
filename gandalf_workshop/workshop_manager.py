"""
workshop_manager.py - The Office of the Workshop Manager (Orchestrator)

This module houses the WorkshopManager class, the central intelligence of the
Gandalf Workshop. The Manager oversees all operations, from commissioning new
Blueprints to approving final Products for delivery. It's akin to the master
artisan or foreman who directs the workflow, assigns tasks to specialized
artisans (AI agents/crews), and ensures quality standards are met throughout
the creation process.
"""

import json
import yaml  # For reading blueprint version
from pathlib import Path
from typing import Optional, Dict  # Tuple removed
from datetime import datetime, timezone

# Import the mock artisan crew and data models
from gandalf_workshop.artisan_guildhall.artisans import initialize_pm_review_crew
from gandalf_workshop.specs.data_models import PMReview, PMReviewDecision

# Metaphor: The WorkshopManager is the foreman of the artisan's workshop,
# directing the flow of work and ensuring quality.


class WorkshopManager:
    """
    The Workshop Manager directs the workflow of the Gandalf workshop,
    commissioning tasks to various artisan crews (AI agent configurations)
    and managing the lifecycle of a commission from initial request to
    final product delivery.
    """

    def __init__(self, max_pm_review_cycles=3):
        """
        Initializes the Workshop Manager.
        Metaphor: The Manager arrives at the workshop, ready to oversee the
        day's tasks. This might involve setting up connections to artisan
        crews or loading configurations.
        Args:
            max_pm_review_cycles (int): Max attempts for PM review approval.
        """
        # Placeholder for future initialization logic,
        # e.g., loading configurations, initializing connections to AI agent
        # frameworks (CrewAI, AutoGen, etc.)
        self.max_pm_review_cycles = max_pm_review_cycles
        print(
            (
                f"Workshop Manager initialized. Max PM review cycles: "
                f"{self.max_pm_review_cycles}. Ready to accept commissions."
            )
        )

    def _get_blueprint_version(self, blueprint_path: Path) -> str:
        """Helper to read version from blueprint YAML."""
        try:
            with open(blueprint_path, "r") as f:
                content = yaml.safe_load(f)
            # Assuming version is at top level or last in revisions
            if (
                "revisions" in content
                and isinstance(content["revisions"], list)
                and content["revisions"]
            ):
                return content["revisions"][-1].get("version", "unknown")
            return content.get("version", "unknown")
        except Exception:  # pylint: disable=broad-except
            return "unknown"

    def commission_new_blueprint(self, user_prompt: str, commission_id: str) -> Path:
        """
        Assigns a new Commission to a Planner Artisan to create a Blueprint.
        Metaphor: "Manager gives client's request to the Head Draftsman."
        Args:
            user_prompt: The initial request from the client.
            commission_id: A unique ID for this new commission.
        Returns:
            Path to the generated blueprint.yaml file in the /blueprints
            directory.
        """
        # In a real implementation, this would:
        # 1. Initialize a "Planner Crew" (e.g., using CrewAI).
        # 2. Pass the user_prompt and commission_id to the crew.
        # 3. The crew would generate the blueprint.yaml.
        # 4. The path to the blueprint would be saved and returned.
        print(
            (
                f"Workshop Manager: Commissioning new blueprint for "
                f"'{commission_id}' based on prompt: '{user_prompt[:50]}...'"
            )
        )

        # Placeholder: Create a dummy blueprint file for scaffolding purposes
        blueprint_dir = Path("gandalf_workshop/blueprints") / commission_id
        blueprint_dir.mkdir(parents=True, exist_ok=True)
        blueprint_path = blueprint_dir / "blueprint.yaml"

        # Placeholder: Create a dummy blueprint file for scaffolding purposes
        # For the mock PM agent to work, ensure project_summary is present.
        # Also adding a basic revision history as per schema expectations.
        initial_version = "1.0"  # Define initial_version here
        with open(blueprint_path, "w") as f:
            yaml.dump(
                {
                    "commission_id": commission_id,
                    "commission_title": f"Commission for {commission_id}",
                    "commission_type": "software_mvp",  # example
                    "project_summary": user_prompt,  # Used by mock PM agent
                    "key_objectives": ["Objective 1 based on prompt."],
                    "product_specifications": {
                        "type": "software",
                        "description": "Details to be filled by Planner.",
                    },
                    "quality_criteria": ["Criterion 1"],
                    "revisions": [
                        {
                            "version": initial_version,
                            "date": datetime.now(timezone.utc).isoformat(),
                            "notes": "Initial blueprint creation.",
                        }
                    ],
                },
                f,
                sort_keys=False,
            )

        print(
            (
                f"Workshop Manager: Placeholder blueprint generated at "
                f"{blueprint_path} (Version: {initial_version})"
            )
        )
        return blueprint_path

    def initiate_strategic_review(
        self, commission_id: str, blueprint_path: Path
    ) -> Path:
        """
        Assigns a Blueprint to the PM Agent for strategic review.
        Metaphor: "Manager asks Chief Strategist to validate Head Draftsman's plans."
        Args:
            commission_id: The ID of the commission.
            blueprint_path: Path to the blueprint.yaml for strategic review.
        Returns:
            Path to the generated PM_Review.json file.
        """
        print(
            (
                f"Workshop Manager: Initiating strategic review for blueprint "
                f"'{blueprint_path.name}' of commission '{commission_id}'."
            )
        )

        blueprint_version = self._get_blueprint_version(blueprint_path)

        # This calls the mock PM agent created in artisans.py
        pm_review_path = initialize_pm_review_crew(
            blueprint_path=blueprint_path,
            commission_id=commission_id,
            blueprint_version=blueprint_version,
        )
        print(
            (
                f"Workshop Manager: Strategic review completed. Report at {pm_review_path}"
            )
        )
        return pm_review_path

    def request_blueprint_strategic_revision(
        self,
        commission_id: str,
        original_blueprint_path: Path,
        pm_review: PMReview,  # noqa: E501
    ) -> Path:
        """
        Simulates sending a Blueprint back to Planner for PM-feedback-based
        revision.
        Metaphor: "Manager sends flawed design to Design Studio with Strategist's notes."
        Args:
            commission_id: The ID of the commission.
            original_blueprint_path: Path to the blueprint needing revision.
            pm_review: The PMReview object with feedback.
        Returns:
            Path to the revised blueprint.yaml.
        """
        rationale_summary = pm_review.rationale[:50]
        log_message = (  # noqa: E501
            f"Workshop Manager: Requesting strategic blueprint revision for "
            f"'{commission_id}' based on PM feedback: {rationale_summary}..."
        )
        print(log_message)

        # In a real system, this would invoke a Planner crew.
        # For this mock, create a new version of the blueprint file.
        try:
            with open(original_blueprint_path, "r") as f:
                blueprint_content = yaml.safe_load(f)
        except Exception as e:  # pylint: disable=broad-except
            print(
                f"Error reading original blueprint {original_blueprint_path}: {e}. "
                "Cannot revise."
            )
            raise

        current_revisions = blueprint_content.get("revisions", [])
        if not current_revisions or not isinstance(current_revisions, list):
            last_version_str = "1.0"  # Default if no revisions found
        else:
            last_version_str = current_revisions[-1].get("version", "1.0")

        try:
            major, minor = map(int, last_version_str.split("."))
            new_version_str = f"{major}.{minor + 1}"
        except ValueError:  # Handle versions like "1.0_revised" or non-numeric
            new_version_str = f"{last_version_str}_pm_rev"

        new_revision_note = (
            f"Revised based on PM Review. Feedback: {pm_review.rationale[:100]}..."
        )
        if pm_review.suggested_focus_areas_for_revision:
            new_revision_note += (
                f" Focus: {', '.join(pm_review.suggested_focus_areas_for_revision)}"
            )

        new_revision_entry = {
            "version": new_version_str,
            "date": datetime.now(timezone.utc).isoformat(),
            "notes": new_revision_note,
        }
        current_revisions.append(new_revision_entry)
        blueprint_content["revisions"] = current_revisions

        # Potentially modify project_summary for mock PM agent to pass next time
        if (
            "complex" in blueprint_content.get("project_summary", "")
            and "simplify" in pm_review.rationale.lower()
        ):
            blueprint_content["project_summary"] = (
                "Revised project summary: now simple and MVP focused."
            )

        revised_blueprint_filename = f"{original_blueprint_path.stem}_rev{new_version_str.replace('.', '_')}.yaml"
        revised_blueprint_path = (
            original_blueprint_path.parent / revised_blueprint_filename
        )

        with open(revised_blueprint_path, "w") as f:
            yaml.dump(blueprint_content, f, sort_keys=False)

        print(
            (
                f"Workshop Manager: Placeholder revised blueprint "
                f"(Version {new_version_str}) generated at {revised_blueprint_path}"
            )
        )
        return revised_blueprint_path

    def _execute_pm_review_cycle(
        self, commission_id: str, current_blueprint_path: Path
    ) -> Optional[Path]:
        """
        Manages the iterative PM review cycle for a blueprint.
        Returns the path to an approved blueprint, or None if approval fails.
        """
        for i in range(self.max_pm_review_cycles):
            cycle_msg = (  # noqa: E501
                f"PM Review Cycle {i+1}/{self.max_pm_review_cycles} "
                f"for {commission_id}"
            )
            print(cycle_msg)  # noqa: E501
            pm_review_report_path = self.initiate_strategic_review(
                commission_id=commission_id, blueprint_path=current_blueprint_path
            )
            with open(pm_review_report_path, "r") as f:
                pm_review_data = json.load(f)

            pm_review = PMReview(**pm_review_data)

            if pm_review.decision == PMReviewDecision.APPROVED:
                print(
                    (
                        f"Workshop Manager: Blueprint {current_blueprint_path.name} "
                        f"APPROVED by PM."
                    )
                )
                return current_blueprint_path
            elif pm_review.decision == PMReviewDecision.REVISION_REQUESTED:
                print(
                    (
                        f"Workshop Manager: Blueprint {current_blueprint_path.name} "
                        f"REVISION REQUESTED by PM."
                    )
                )
                if i < self.max_pm_review_cycles - 1:
                    current_blueprint_path = self.request_blueprint_strategic_revision(
                        commission_id=commission_id,
                        original_blueprint_path=current_blueprint_path,
                        pm_review=pm_review,
                    )
                else:
                    print(
                        (
                            f"Workshop Manager: Max PM review cycles reached for "
                            f"{commission_id}. Blueprint not approved."
                        )
                    )
                    return None
            else:
                print(
                    (
                        f"Workshop Manager: Unknown PM review decision: "
                        f"{pm_review.decision}. Halting."
                    )
                )
                return None
        return None  # Should be covered by loop logic, but as a fallback

    def execute_full_commission_workflow(
        self, user_prompt: str, commission_id: str
    ) -> bool:
        """
        Orchestrates the full commission workflow from blueprinting to
        (mocked) delivery.
        Args:
            user_prompt: The initial request from the client.
            commission_id: A unique ID for this new commission.
        Returns:
            True if the commission completes successfully, False otherwise.
        """
        print(f"\n===== Starting Full Workflow for Commission: {commission_id} =====")
        # 1. Commission and get initial blueprint
        initial_blueprint_path = self.commission_new_blueprint(
            user_prompt=user_prompt, commission_id=commission_id
        )

        # 2. PM Review Cycle
        approved_blueprint_path = self._execute_pm_review_cycle(
            commission_id, initial_blueprint_path
        )

        if not approved_blueprint_path:
            print(
                (
                    f"Workshop Manager: Commission '{commission_id}' halted due to "
                    f"failed PM review process."
                )
            )
            return False

        print(
            (
                f"Workshop Manager: PM review approved. Proceeding with blueprint: "
                f"{approved_blueprint_path.name}"
            )
        )

        # 3. Request product generation (using the PM-approved blueprint)
        # In a real flow, product_path would point to a directory or a set of files
        product_path_v1 = self.request_product_generation_or_revision(
            commission_id=commission_id, blueprint_path=approved_blueprint_path
        )

        # 4. Initiate quality inspection
        inspection_report_v1_path = self.initiate_quality_inspection(
            commission_id=commission_id,
            product_to_inspect_path=product_path_v1,
            blueprint_path=approved_blueprint_path,  # Use the approved blueprint
        )
        # TODO: Add logic to handle inspection report feedback (revisions, re-planning)

        # 5. Finalize and deliver (assuming inspection passes for this mock)
        print(f"Workshop Manager: Assuming QA passed for {commission_id} (mock).")
        self.finalize_commission_and_deliver(
            commission_id=commission_id,
            final_product_path=product_path_v1,
            final_inspection_report_path=inspection_report_v1_path,
        )
        print(
            (
                f"===== Full Workflow for Commission: {commission_id} "
                "Completed Successfully ====="
            )
        )
        return True

    def request_product_generation_or_revision(
        self,
        commission_id: str,
        blueprint_path: Path,
        current_product_path: Optional[Path] = None,
        previous_inspection_report_path: Optional[Path] = None,
    ) -> Path:
        """
        Assigns a Coder Artisan (or team) to build or revise a Product.
        Metaphor: "Manager gives Blueprint to Master Craftsman for construction."
        Args:
            commission_id: The ID of the commission.
            blueprint_path: Path to the relevant blueprint.yaml.
            current_product_path: Path to existing product if revising.
            previous_inspection_report_path: Path to last inspection report.
        Returns:
            Path to the newly generated or revised product version.
        """
        print(
            (
                f"Workshop Manager: Requesting product generation/revision for "
                f"'{commission_id}'."
            )
        )
        print(f"  Blueprint: {blueprint_path}")
        if current_product_path:
            print(f"  Revising existing product: {current_product_path}")
        if previous_inspection_report_path:
            print(f"  Using inspection report: {previous_inspection_report_path}")

        # Placeholder: Create a dummy product directory/file
        product_dir = (
            Path("gandalf_workshop/commissions_in_progress")
            / commission_id
            / "product_v_scaffold"
        )
        product_dir.mkdir(parents=True, exist_ok=True)
        product_file_path = product_dir / "product_content.txt"
        with open(product_file_path, "w") as f:
            f.write(f"Placeholder product for {commission_id}\n")
            if current_product_path:
                f.write(f"Based on revision of {current_product_path.name}\n")

        print(
            (
                f"Workshop Manager: Placeholder product generated at "
                f"{product_file_path}"
            )
        )
        # In reality, this would be a path to a directory or a main file
        return product_file_path

    def initiate_quality_inspection(
        self, commission_id: str, product_to_inspect_path: Path, blueprint_path: Path
    ) -> Path:
        """
        Assigns an Inspector Artisan (or Red Team) to conduct Quality Inspection.
        Metaphor: "Manager sends finished piece to Quality Control Guild."
        Args:
            commission_id: The ID of the commission.
            product_to_inspect_path: Path to product version to be inspected.
            blueprint_path: Path to blueprint for compliance checking.
        Returns:
            Path to the generated inspection_report.json.
        """
        print(
            (
                f"Workshop Manager: Initiating quality inspection for product "
                f"'{product_to_inspect_path.name}' of commission "
                f"'{commission_id}'."
            )
        )
        print(f"  Blueprint for reference: {blueprint_path}")

        # Placeholder: Create a dummy inspection report
        report_dir = Path("gandalf_workshop/quality_control_lab") / commission_id
        report_dir.mkdir(parents=True, exist_ok=True)
        # e.g. product_v1_inspection_report.json
        report_name = f"{product_to_inspect_path.parent.name}_inspection_report.json"
        report_path = report_dir / report_name

        with open(report_path, "w") as f:
            json.dump(
                {
                    "commission_id": commission_id,
                    "product_version_inspected": product_to_inspect_path.parent.name,
                    "status": "placeholder_inspection_report",
                    "summary": "Scaffold report - no actual inspection performed.",
                },
                f,
                indent=2,
            )

        print(
            (
                f"Workshop Manager: Placeholder inspection report generated at "
                f"{report_path}"
            )
        )
        return report_path

    def finalize_commission_and_deliver(
        self,
        commission_id: str,
        final_product_path: Path,
        final_inspection_report_path: Path,
    ) -> None:
        """
        Packages final Product and Inspection Report for delivery.
        Metaphor: "Manager approves Product, archives records, prepares for client."
        Args:
            commission_id: The ID of the commission.
            final_product_path: Path to the approved final product.
            final_inspection_report_path: Path to final inspection report.
        """
        print(f"Workshop Manager: Finalizing commission '{commission_id}'.")
        print(f"  Final Product: {final_product_path}")
        print(f"  Final Inspection Report: {final_inspection_report_path}")

        # Placeholder: Simulate moving to completed_commissions
        completed_dir = Path("gandalf_workshop/completed_commissions") / commission_id
        completed_dir.mkdir(parents=True, exist_ok=True)

        # Simulate copying product
        if final_product_path.is_file():
            dest_product_name = f"final_product_{final_product_path.name}"
            with open(completed_dir / dest_product_name, "w") as f:
                f.write(
                    f"Simulated copy of {final_product_path.name} for "
                    f"commission {commission_id}\n"
                )
        else:  # if it's a directory
            dest_info_name = f"final_product_info_for_{final_product_path.name}.txt"
            with open(completed_dir / dest_info_name, "w") as f:
                f.write(
                    f"Simulated copy of product directory {final_product_path} "
                    f"for commission {commission_id}\n"
                )

        # Simulate copying inspection report
        dest_report_name = (
            f"final_inspection_report_{final_inspection_report_path.name}"
        )
        with open(completed_dir / dest_report_name, "w") as f:
            f.write(
                f"Simulated copy of {final_inspection_report_path.name} "
                f"for commission {commission_id}\n"
            )

        print(
            (
                f"Workshop Manager: Commission '{commission_id}' finalized and "
                f"artifacts 'moved' to {completed_dir}."
            )
        )

    def request_blueprint_revision(
        self,
        commission_id: str,
        original_blueprint_path: Path,
        failure_history: Dict[str, any],
    ) -> Path:
        """
        Sends Blueprint to Planner for revision due to fundamental design issues.
        (Corresponds to Tier 2 Regression Protocol Re-Plan).
        Metaphor: "Manager sends flawed design to Design Studio with notes."
        Args:
            commission_id: The ID of the commission.
            original_blueprint_path: Path to blueprint needing revision.
            failure_history: Data about why current blueprint is failing.
        Returns:
            Path to the revised blueprint.yaml.
        """
        print(
            (
                f"Workshop Manager: Requesting blueprint revision for "
                f"'{commission_id}'."
            )
        )
        print(f"  Original Blueprint: {original_blueprint_path}")
        print(f"  Failure History: {failure_history}")

        # Placeholder: Create a dummy revised blueprint file
        revised_blueprint_name = f"{original_blueprint_path.stem}_revised.yaml"
        revised_blueprint_path = original_blueprint_path.parent / revised_blueprint_name
        with open(revised_blueprint_path, "w") as f:
            f.write(f"# Revised Blueprint for {commission_id}\n")
            f.write(f"commission_id: {commission_id}\n")
            f.write("status: placeholder_revised_blueprint\n")
            f.write(f"based_on_failures: {str(failure_history)}\n")

        print(
            (
                f"Workshop Manager: Placeholder revised blueprint generated at "
                f"{revised_blueprint_path}"
            )
        )
        return revised_blueprint_path


if __name__ == "__main__":
    # Example of how the manager might be used (for testing purposes)
    # This now demonstrates the full workflow including PM review.
    manager = WorkshopManager(
        max_pm_review_cycles=2
    )  # Test with 2 cycles for PM review

    # Test Case 1: Prompt to be rejected by PM, then revised and approved.
    test_commission_id_1 = "test_commission_pm_cycle_001"
    test_prompt_1 = (
        "Create a very complex AI-driven platform for advanced quantum "
        "particle simulation."
    )  # Mock PM rejects "complex"
    print(
        (
            f"\n--- Test Case 1: '{test_commission_id_1}' "
            "(expect PM revision then approval) ---"
        )
    )
    success_1 = manager.execute_full_commission_workflow(
        user_prompt=test_prompt_1, commission_id=test_commission_id_1
    )
    print(f"Test Case 1 completed. Success: {success_1}")
    if success_1:
        # Check if a revised blueprint was created
        expected_bp_name_part = "_rev1_1.yaml"
        bp_list = list(
            (Path("gandalf_workshop/blueprints") / test_commission_id_1).glob("*.yaml")
        )
        found_revised = any(
            expected_bp_name_part in bp.name
            for bp in bp_list
            if bp.name != "blueprint.yaml"
        )
        print(
            (
                f"Revised blueprint for Test Case 1 found: {found_revised} "
                "(expected True if PM revision occurred)"
            )
        )

    # Test Case 2: Prompt that should be approved by PM on first try.
    test_commission_id_2 = "test_commission_pm_direct_approval_002"
    test_prompt_2 = "Create a simple command-line calculator MVP."
    print(
        (
            f"\n--- Test Case 2: '{test_commission_id_2}' "
            "(expect direct PM approval) ---"
        )
    )
    success_2 = manager.execute_full_commission_workflow(
        user_prompt=test_prompt_2, commission_id=test_commission_id_2
    )
    print(f"Test Case 2 completed. Success: {success_2}")

    # Test Case 3: Prompt that might fail PM review cycles.
    manager_strict_pm = WorkshopManager(max_pm_review_cycles=1)
    test_commission_id_3 = "test_commission_pm_strict_fail_003"
    test_prompt_3 = (
        "Develop a highly intricate enterprise system with many legacy " "integrations."
    )
    print(
        (
            f"\n--- Test Case 3: '{test_commission_id_3}' "
            "(PM review with strict cycles) ---"
        )
    )
    # Mock strategic revision makes summary "simple", so it passes on 2nd attempt.
    # With max_pm_review_cycles=1, it means 1 attempt. If rejected, it stops.
    manager_one_shot_pm = WorkshopManager(max_pm_review_cycles=1)
    print("Testing with manager_one_shot_pm (max_pm_review_cycles=1)")
    success_3 = manager_one_shot_pm.execute_full_commission_workflow(
        user_prompt=test_prompt_3,  # This will be "complex"
        commission_id=test_commission_id_3,
    )
    print(
        (
            f"Test Case 3 completed. Success: {success_3} "
            "(expected False if initially complex and max_cycles=1)"
        )
    )

    # Example of old-style blueprint revision (technical, not strategic)
    print("\n--- Test original blueprint revision method (technical) ---")
    if success_2:
        bp_path_tech_rev = (
            Path("gandalf_workshop/blueprints")
            / test_commission_id_2
            / "blueprint.yaml"
        )
        if bp_path_tech_rev.exists():
            failure_data = {"reason": "Technical flaw found by QA", "attempts": 1}
            print("Calling legacy request_blueprint_revision (not PM flow)")
            try:
                manager.request_blueprint_revision(
                    commission_id=test_commission_id_2,
                    original_blueprint_path=bp_path_tech_rev,
                    failure_history=failure_data,
                )
                print(
                    (
                        "Legacy request_blueprint_revision called successfully for "
                        f"{test_commission_id_2}."
                    )
                )
            except Exception as e:
                print(f"Error calling legacy request_blueprint_revision: {e}")
        else:
            print(
                (
                    f"Skipping legacy request_blueprint_revision test, blueprint "
                    f"not found: {bp_path_tech_rev}"
                )
            )

    print("\nAll Workshop Manager __main__ tests completed.")
