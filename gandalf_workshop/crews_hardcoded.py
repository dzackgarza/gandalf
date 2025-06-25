import re
from pathlib import Path
from typing import Any
from datetime import datetime  # For planner blueprint date

from crewai import Agent, Task

# Assuming artifact_loader.py is in the same directory
from .artifact_loader import (
    load_planner_blueprint,
    load_planner_feature,
    load_coder_app_code,
    load_coder_test_code,
    load_coder_bdd_steps,
    load_coder_requirements,
)


# --- Helper Functions (copied from original crews.py, still needed) ---
def create_commission_id(prompt: str) -> str:
    s = prompt.lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s[:50]


def save_to_file(filepath: Path, content: str):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Saved output to: {filepath}")


# --- Planner Crew ---
class PlannerCrew:
    def __init__(self, commission_prompt: str, commission_id: str, llm_instance: Any):
        self.commission_prompt = commission_prompt
        self.commission_id = commission_id
        self.llm = (
            llm_instance  # Kept for structural compatibility, though not used by run()
        )
        self.workspace_path = (
            Path("workspace") / self.commission_id / "planning_outputs"
        )

        planner_goal = (
            f"Deconstruct the given software commission brief: '{self.commission_prompt}'.\n"
            "Then, produce two distinct artifacts:\n"
            "1. A comprehensive `blueprint.yaml` file, detailing the software's "
            "architecture, components, dependencies, and required unit tests. "
            "This blueprint must strictly adhere to the schema provided in the "
            "'Communication_Protocols.md'.\n"
            "2. A `commission_expectations.feature` file written in Gherkin, "
            "outlining user-facing behavioral expectations for BDD testing. "
            "This file must also adhere to its schema.\n\n"
            f"The `commission_id` for this task is: {self.commission_id}\n"
            "The `commission_title` should be derived from the prompt.\n"
            "The `commission_type` is 'software_mvp'.\n"
            "Focus on creating a plan for a simple, functional command-line application."
        )
        planner_backstory = (
            "You are a Planner Artisan from the Gandalf Workshop, renowned for your "
            "meticulous attention to detail and your ability to transform vague requests "
            "into actionable, crystal-clear technical plans. Your blueprints are "
            "legendary for their precision, and your expectation documents leave no room "
            "for ambiguity. You understand that the success of the entire commission "
            "hinges on the quality of your initial planning."
        )
        self.planner_agent = Agent(
            role="Master Draftsperson & Visionary Architect",
            goal=planner_goal,
            backstory=planner_backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )
        planning_task_description = (
            f"Analyze Commission Brief: '{self.commission_prompt}'\n\n"
            # Simplified for hardcoding context
            "Produce blueprint.yaml and commission_expectations.feature."
        )
        planning_task_expected_output = (
            "Content for blueprint.yaml and commission_expectations.feature."
        )
        self.planning_task = Task(
            description=planning_task_description,
            expected_output=planning_task_expected_output,
            agent=self.planner_agent,
        )

    def run(self) -> tuple[Path, Path]:
        print(
            f"\n--- Running Planner Crew (Hardcoded) for Commission ID: {self.commission_id} ---"
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        print("!!! USING HARDCODED OUTPUTS VIA ARTIFACT LOADER FOR PLANNER CREW !!!")

        blueprint_content = load_planner_blueprint(self.commission_id)
        feature_content = load_planner_feature()

        blueprint_path = self.workspace_path / "blueprint.yaml"
        feature_file_path = self.workspace_path / "commission_expectations.feature"

        save_to_file(blueprint_path, blueprint_content)
        save_to_file(feature_file_path, feature_content)

        print(
            f"Planner Crew generated (hardcoded): {blueprint_path}, {feature_file_path}"
        )
        return blueprint_path, feature_file_path


# --- Coder Crew ---
class CoderCrew:
    def __init__(
        self,
        commission_id: str,
        blueprint_path: Path,
        feature_file_path: Path,
        llm_instance: Any,
    ):
        self.commission_id = commission_id
        self.blueprint_path = blueprint_path
        self.feature_file_path = feature_file_path
        self.llm = llm_instance
        self.workspace_path = Path("workspace") / self.commission_id / "coding_outputs"
        self.app_name = "app"

        with open(self.blueprint_path, "r") as f:
            self.blueprint_content = f.read()
        with open(self.feature_file_path, "r") as f:
            self.feature_content = f.read()

        coder_goal = (
            f"Given the `blueprint.yaml` and `commission_expectations.feature` for "
            f"commission ID '{self.commission_id}', produce the specified code artifacts."
        )
        coder_backstory = "I am a master coder, translating plans into functional code."
        self.coder_agent = Agent(
            role="Master Crafter & Product Engineer",
            goal=coder_goal,
            backstory=coder_backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

        coding_task_description = (
            f"Commission ID: {self.commission_id}\n"
            "Inputs: blueprint.yaml, commission_expectations.feature.\n"
            "Task: Generate application code, unit tests, BDD steps, and requirements.txt."
        )
        self.coding_task = Task(
            description=coding_task_description,
            expected_output=("Python code files and requirements.txt."),
            agent=self.coder_agent,
        )

    def run(self) -> tuple[Path, Path, Path, Path | None]:
        print(
            f"\n--- Running Coder Crew (Hardcoded) for Commission ID: {self.commission_id} ---"
        )
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "features" / "steps").mkdir(parents=True, exist_ok=True)
        print("!!! USING HARDCODED OUTPUTS VIA ARTIFACT LOADER FOR CODER CREW !!!")

        app_code = load_coder_app_code(self.app_name)
        test_code = load_coder_test_code(self.app_name)
        bdd_steps_code = load_coder_bdd_steps(
            self.feature_file_path.name, self.app_name
        )
        requirements_content = load_coder_requirements()

        app_py_path = self.workspace_path / f"{self.app_name}.py"
        test_py_path = self.workspace_path / f"test_{self.app_name}.py"
        bdd_steps_py_path = self.workspace_path / "features" / "steps" / "app_steps.py"

        bdd_feature_target_path = (
            self.workspace_path / "features" / self.feature_file_path.name
        )
        save_to_file(bdd_feature_target_path, self.feature_content)
        print(f"Copied feature file for BDD to: {bdd_feature_target_path}")

        save_to_file(app_py_path, app_code)
        save_to_file(test_py_path, test_code)
        save_to_file(bdd_steps_py_path, bdd_steps_code)

        requirements_txt_path = None
        if (
            requirements_content and requirements_content.strip()
        ):  # Ensure content is not just whitespace
            requirements_txt_path = self.workspace_path / "requirements.txt"
            save_to_file(requirements_txt_path, requirements_content)
            print(
                f"CoderCrew generated (hardcoded): {app_py_path}, {test_py_path}, "
                f"{bdd_steps_py_path}, {requirements_txt_path}"
            )
        else:
            print(
                f"CoderCrew generated (hardcoded): {app_py_path}, {test_py_path}, "
                f"{bdd_steps_py_path}"
            )

        return app_py_path, test_py_path, bdd_steps_py_path, requirements_txt_path


# End of gandalf_workshop/crews_hardcoded.py
# Adding extra newlines to be safe.
