import os
import ast
import sys

# This script verifies that the AI-generated scaffold meets our design specifications.

print("  - Verifying directory and file layout...")

# Define the required project structure
REQUIRED_DIRS = [
    "gandalf_workshop/blueprints",
    "gandalf_workshop/artisan_guildhall/inspectors",
]
REQUIRED_FILES = [
    "main.py",
    "gandalf_workshop/workshop_manager.py",
    "gandalf_workshop/specs/data_models.py",
]

# Check if directories and files exist
for d in REQUIRED_DIRS:
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
