"""
Gandalf Workshop - Specifications Submodule

This file makes the 'specs' directory a Python submodule.
This is the "Technical Archives" of the workshop, where the precise
definitions (schemas) for Blueprints and Inspection Reports are stored.
Making it a submodule allows these critical data model definitions
to be imported cleanly.
"""

# from .data_models import BlueprintModel, InspectionReportModel
# TODO: Restore these imports when AI agent execution populates data_models.py
# For the current refactoring verification, these are commented out as
# the `make develop` script uses placeholder content for data_models.py.

__all__: list[str] = []  # ["BlueprintModel", "InspectionReportModel"]
