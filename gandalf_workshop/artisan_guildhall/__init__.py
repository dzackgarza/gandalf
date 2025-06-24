"""
Gandalf Workshop - Artisan Guildhall Submodule

This file makes the 'artisan_guildhall' directory a Python submodule.
This is the "Artisan's Guildhall" itself, containing the charters (prompts)
that guide the Artisans and the means to assemble (initialize) them for work.
Making it a submodule allows for organized access to these core agent-related
components.
"""

from .prompts import (
    PLANNER_CHARTER_PROMPT,
    CODER_CHARTER_PROMPT,
    GENERAL_INSPECTOR_CHARTER_PROMPT,
)
from .artisans import (
    initialize_planning_crew,
    initialize_coding_crew,
    initialize_inspection_crew,
)

__all__ = [
    "PLANNER_CHARTER_PROMPT",
    "CODER_CHARTER_PROMPT",
    "GENERAL_INSPECTOR_CHARTER_PROMPT",
    "initialize_planning_crew",
    "initialize_coding_crew",
    "initialize_inspection_crew",
]
