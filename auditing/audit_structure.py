import os
import ast
import sys

# This script verifies that the AI-generated scaffold meets our design specifications.

print("  - Verifying directory and file layout...")

# Define the required project structure
REQUIRED_DIRS = [
    "gandalf_workshop/blueprints",
    "gandalf_workshop/artisan_guildhall/inspectors",
    "gandalf_workshop/tests/features", # For BDD .feature files
    "gandalf_workshop/tests/step_definitions", # For BDD step definition .py files
]
REQUIRED_FILES = [
    "main.py",
    "gandalf_workshop/workshop_manager.py",
    "gandalf_workshop/specs/data_models.py",
    "gandalf_workshop/tests/__init__.py", # Ensure tests module is treated as a package
    "gandalf_workshop/tests/step_definitions/__init__.py", # Ensure step_definitions is a package
]

# Check if directories and files exist
# Allow 'gandalf_workshop/tests/features' and 'gandalf_workshop/tests/step_definitions'
# to be initially empty or missing, as they are created during the commission.
# The BDD test run itself will fail if they are not correctly populated later.
OPTIONAL_DIRS_UNTIL_COMMISSION = [
    "gandalf_workshop/tests/features",
    "gandalf_workshop/tests/step_definitions"
]

for d in REQUIRED_DIRS:
    if d in OPTIONAL_DIRS_UNTIL_COMMISSION and not os.path.exists(d):
        print(f"    ℹ️ Optional directory (expected after commission): {d} - Not found, but this is acceptable at initial audit.")
        # Create them so subsequent steps don't fail if they expect the path
        try:
            os.makedirs(d, exist_ok=True)
            # Create __init__.py for step_definitions if it's that directory
            if d == "gandalf_workshop/tests/step_definitions":
                with open(os.path.join(d, "__init__.py"), "w") as f:
                    f.write("# Required for pytest-bdd to find step definitions\n")
        except OSError as e:
            print(f"❌ Structural Integrity Error: Could not create optional directory {d}: {e}")
            sys.exit(1)
        continue # Skip the isdir check for these optional dirs if they didn't exist

    if not os.path.isdir(d):
        print(f"❌ Structural Integrity Error: Missing required directory: {d}")
        sys.exit(1)

for f in REQUIRED_FILES:
    # Allow __init__.py in step_definitions to be missing if the dir itself was optional and not yet created
    if f == "gandalf_workshop/tests/step_definitions/__init__.py" and \
       "gandalf_workshop/tests/step_definitions" in OPTIONAL_DIRS_UNTIL_COMMISSION and \
       not os.path.exists(os.path.dirname(f)):
        print(f"    ℹ️ Optional file (expected after commission): {f} - Not found, but this is acceptable at initial audit.")
        continue

    if not os.path.isfile(f):
    if not os.path.isdir(d):
        print(f"❌ Structural Integrity Error: Missing required directory: {d}")
        sys.exit(1)
for f in REQUIRED_FILES:
    if not os.path.isfile(f):
        print(f"❌ Structural Integrity Error: Missing required file: {f}")
        sys.exit(1)

print("    ✅ Directory and file layout is correct.")

print("  - Verifying code structure (classes and methods)...")

# Load the manager's source code and parse it
try:
    with open("gandalf_workshop/workshop_manager.py", "r") as f:
        tree = ast.parse(f.read())
except FileNotFoundError:
    print("❌ Structural Integrity Error: workshop_manager.py not found.")
    sys.exit(1)

class_found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "WorkshopManager":
        class_found = True
        defined_methods = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}

        REQUIRED_METHODS = [
            "commission_new_blueprint",
            "request_product_generation_or_revision",
            "initiate_quality_inspection",
            "finalize_commission_and_deliver",
            "request_blueprint_revision",
        ]

        for method in REQUIRED_METHODS:
            if method not in defined_methods:
                print(f"❌ WorkshopManager class is missing required method: {method}")
                sys.exit(1)

        print("    ✅ WorkshopManager class and all required methods are defined.")
        break

if not class_found:
    print("❌ Could not find class 'WorkshopManager' in workshop_manager.py")
    sys.exit(1)

print("  - Code structure verification complete.")
