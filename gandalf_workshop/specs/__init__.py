"""
Gandalf Workshop - Specifications Submodule

This file makes the 'specs' directory a Python submodule.
This is the "Technical Archives" of the workshop, where the precise
definitions (schemas) for Blueprints and Inspection Reports are stored.
Making it a submodule allows these critical data model definitions
to be imported cleanly.
"""

from .data_models import BlueprintModel, InspectionReportModel

__all__ = ["BlueprintModel", "InspectionReportModel"]
