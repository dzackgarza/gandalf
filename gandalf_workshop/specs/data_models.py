from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class PMReviewDecision(str, Enum):
    APPROVED = "APPROVED"
    REVISION_REQUESTED = "REVISION_REQUESTED"


class PMReview(BaseModel):
    """
    Output of the Product Manager Agent's strategic review of a Blueprint.
    Adheres to the schema defined in PM_Review_Schema.md.
    """

    commission_id: str = Field(
        ...,
        examples=["calc_gui_001", "research_ai_ethics_002"],
        description=(
            "Unique identifier for the commission, matching the one in "
            "blueprint.yaml."
        ),
    )
    blueprint_path: str = Field(
        ...,
        examples=["blueprints/gui_calc_001/blueprint.yaml"],
        description=("The full path to the blueprint.yaml file that was reviewed."),
    )
    blueprint_version_reviewed: str = Field(
        ...,
        examples=["1.0", "1.1_revised"],
        description="The version of the Blueprint that was reviewed.",
    )
    review_timestamp: datetime = Field(
        ...,
        examples=["2023-10-26T10:30:00Z"],
        description=("Timestamp of when the review was completed, in ISO 8601 format."),
    )
    pm_agent_id: str = Field(
        ...,
        examples=["PM_Agent_v1.2"],
        description=(
            "Identifier of the PM Agent instance or version performing the " "review."
        ),
    )
    decision: PMReviewDecision = Field(
        ..., examples=["APPROVED"], description="The outcome of the PM Agent's review."
    )
    rationale: str = Field(
        ...,
        examples=[
            (
                "The Blueprint is APPROVED. The key_objectives and "
                "product_specifications align well with the project_summary, "
                "presenting a clear and strategically sound plan for an MVP."
            ),
            (
                "REVISION_REQUESTED: The product_specifications for the "
                "'software_mvp' detail features beyond a minimal viable scope "
                "(Criterion: 'Over-engineered for an MVP'). Specifically, "
                "module 'reporting_suite' and its components seem premature "
                "for an initial version based on the project_summary. "
                "Recommend deferring this module to a later iteration."
            ),
        ],
        description="A detailed natural language explanation for the decision.",
    )
    suggested_focus_areas_for_revision: Optional[List[str]] = Field(
        None,
        examples=[
            [
                "product_specifications.modules[1].description",
                "key_objectives[2]",
            ]
        ],
        min_length=1,
        description=(
            "Optional: List of Blueprint sections for Planner to focus on "
            "during revision. Required if decision is REVISION_REQUESTED."
        ),
    )

    @validator("suggested_focus_areas_for_revision", always=True)
    def check_suggested_focus_areas(cls, v, values):
        decision = values.get("decision")
        if decision == PMReviewDecision.REVISION_REQUESTED and not v:
            raise ValueError(
                "suggested_focus_areas_for_revision is required for "
                "REVISION_REQUESTED decision."
            )
        if decision == PMReviewDecision.APPROVED and v:
            # While not strictly disallowed by schema, it's good practice for
            # it to be None if approved. We allow it here.
            pass
        return v

    class Config:
        use_enum_values = True  # Ensures that enum values are used in serialization
        extra = "forbid"  # Disallow extra fields during parsing
