"""
Agent State Entities.

Domain entities for agent workflow state management.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class CopywritingStage(str, Enum):
    """Stages of the copywriting agent workflow."""
    PLAN = "plan"
    DRAFT = "draft"
    CRITIQUE = "critique"
    FINALIZE = "finalize"
    COMPLETED = "completed"


# Valid stage transitions
VALID_TRANSITIONS = {
    None: [CopywritingStage.PLAN],
    CopywritingStage.PLAN: [CopywritingStage.DRAFT],
    CopywritingStage.DRAFT: [CopywritingStage.CRITIQUE],
    CopywritingStage.CRITIQUE: [CopywritingStage.FINALIZE],
    CopywritingStage.FINALIZE: [CopywritingStage.COMPLETED],
    CopywritingStage.COMPLETED: [],  # Terminal state
}


class InvalidStageTransitionError(Exception):
    """Raised when an invalid stage transition is attempted."""
    pass


@dataclass
class CopywritingState:
    """
    State for the copywriting agent workflow.
    
    Tracks the product information, workflow progress, and generated content
    through the Plan -> Draft -> Critique -> Finalize stages.
    
    Attributes:
        product_name: Name of the product to write copy for
        features: List of product features to highlight
        workflow_id: Unique identifier for this workflow execution
        current_stage: Current stage of the workflow
        plan: Generated marketing outline/plan
        draft: Initial copy draft
        critique: Self-critique and improvement suggestions
        final_copy: Polished final marketing copy
        brand_guidelines: Optional brand voice instructions
    """
    product_name: str
    features: List[str]
    workflow_id: str = ""
    current_stage: Optional[CopywritingStage] = None
    plan: Optional[str] = None
    draft: Optional[str] = None
    critique: Optional[str] = None
    final_copy: Optional[str] = None
    brand_guidelines: Optional[str] = None
    
    def validate_transition(self, to_stage: CopywritingStage) -> bool:
        """
        Validate if transition to the given stage is allowed.
        
        Args:
            to_stage: Target stage to transition to
            
        Returns:
            True if transition is valid
            
        Raises:
            InvalidStageTransitionError: If transition is not allowed
        """
        allowed = VALID_TRANSITIONS.get(self.current_stage, [])
        if to_stage not in allowed:
            raise InvalidStageTransitionError(
                f"Cannot transition from {self.current_stage} to {to_stage}. "
                f"Allowed transitions: {allowed}"
            )
        return True
    
    def transition_to(self, stage: CopywritingStage) -> "CopywritingState":
        """
        Transition to a new stage after validation.
        
        Args:
            stage: Target stage
            
        Returns:
            Self with updated current_stage
            
        Raises:
            InvalidStageTransitionError: If transition is not allowed
        """
        self.validate_transition(stage)
        self.current_stage = stage
        return self
    
    def to_dict(self) -> dict:
        """Convert state to dictionary for LangGraph compatibility."""
        return {
            "product_name": self.product_name,
            "features": self.features,
            "workflow_id": self.workflow_id,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "plan": self.plan,
            "draft": self.draft,
            "critique": self.critique,
            "final_copy": self.final_copy,
            "brand_guidelines": self.brand_guidelines,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CopywritingState":
        """Create state from dictionary."""
        stage = data.get("current_stage")
        if stage and isinstance(stage, str):
            stage = CopywritingStage(stage)
        
        return cls(
            product_name=data.get("product_name", ""),
            features=data.get("features", []),
            workflow_id=data.get("workflow_id", ""),
            current_stage=stage,
            plan=data.get("plan"),
            draft=data.get("draft"),
            critique=data.get("critique"),
            final_copy=data.get("final_copy"),
            brand_guidelines=data.get("brand_guidelines"),
        )
