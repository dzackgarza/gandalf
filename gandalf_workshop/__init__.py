"""
Gandalf Workshop Package Root

This file makes the 'gandalf_workshop' directory a Python package.
It's like placing a sign on the main workshop building, identifying it
and allowing its various departments (submodules) to be recognized
and accessed systematically.
"""

# You can make key components available at the package level if desired, e.g.:
# from .workshop_manager import WorkshopManager
# from .specs.data_models import BlueprintModel, InspectionReportModel

__version__ = "0.1.0"  # Workshop's current "model year" or "version"
PROJECT_NAME = "Gandalf Workshop"

print(f"Welcome to {PROJECT_NAME} v{__version__}. The workshop is now open.")
