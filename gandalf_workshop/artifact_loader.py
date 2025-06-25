from pathlib import Path
from datetime import datetime

ARTIFACT_BASE_PATH = Path(__file__).parent / "hardcoded_artifacts"


def _read_template(template_path: Path) -> str:
    try:
        with open(template_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: Template file not found at {template_path}")
        raise


def load_planner_blueprint(commission_id: str) -> str:
    template_path = ARTIFACT_BASE_PATH / "planner/blueprint_template.yaml"
    template_content = _read_template(template_path)
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    return template_content.format(
        commission_id=commission_id, current_date=current_date_str
    )


def load_planner_feature() -> str:
    template_path = ARTIFACT_BASE_PATH / "planner/feature_template.feature"
    return _read_template(template_path)  # No formatting needed for this one


def load_coder_app_code(app_name: str) -> str:
    # app_name is not used in template, but kept for consistency if needed later
    template_path = ARTIFACT_BASE_PATH / "coder/app_code_template.py"
    template_content = _read_template(template_path)
    # If app_code_template.py used {app_name}, it would be:
    # return template_content.format(app_name=app_name)
    return template_content  # No formatting needed for current template


def load_coder_test_code(app_name: str) -> str:
    template_path = ARTIFACT_BASE_PATH / "coder/test_code_template.py"
    template_content = _read_template(template_path)
    return template_content.format(app_name_placeholder=app_name)


def load_coder_bdd_steps(feature_file_name: str, app_name: str) -> str:
    template_path = ARTIFACT_BASE_PATH / "coder/bdd_steps_template.py"
    template_content = _read_template(template_path)
    return template_content.format(
        feature_file_name_placeholder=feature_file_name, app_name_placeholder=app_name
    )


def load_coder_requirements() -> str:
    template_path = ARTIFACT_BASE_PATH / "coder/requirements_template.txt"
    return _read_template(template_path)  # No formatting needed
