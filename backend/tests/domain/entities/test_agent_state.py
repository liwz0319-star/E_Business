"""
Tests for agent state entities.
"""
import pytest

from app.domain.entities.agent_state import (
    CopywritingState,
    CopywritingStage,
    InvalidStageTransitionError,
    VALID_TRANSITIONS,
)


class TestCopywritingState:
    """Tests for CopywritingState dataclass."""
    
    def test_create_state_with_required_fields(self):
        """Test creating state with only required fields."""
        state = CopywritingState(
            product_name="Test Product",
            features=["Feature 1", "Feature 2"],
        )
        
        assert state.product_name == "Test Product"
        assert state.features == ["Feature 1", "Feature 2"]
        assert state.workflow_id == ""
        assert state.current_stage is None
        assert state.plan is None
        assert state.draft is None
        assert state.critique is None
        assert state.final_copy is None
        assert state.brand_guidelines is None
    
    def test_create_state_with_all_fields(self):
        """Test creating state with all fields."""
        state = CopywritingState(
            product_name="Smart Watch Pro",
            features=["Heart rate", "GPS"],
            workflow_id="test-workflow-123",
            current_stage=CopywritingStage.DRAFT,
            plan="Marketing outline...",
            draft="Initial copy...",
            critique=None,
            final_copy=None,
            brand_guidelines="Professional tone",
        )
        
        assert state.product_name == "Smart Watch Pro"
        assert state.features == ["Heart rate", "GPS"]
        assert state.workflow_id == "test-workflow-123"
        assert state.current_stage == CopywritingStage.DRAFT
        assert state.plan == "Marketing outline..."
        assert state.draft == "Initial copy..."
        assert state.brand_guidelines == "Professional tone"


class TestCopywritingStage:
    """Tests for CopywritingStage enum."""
    
    def test_stage_values(self):
        """Test all stage values exist."""
        assert CopywritingStage.PLAN.value == "plan"
        assert CopywritingStage.DRAFT.value == "draft"
        assert CopywritingStage.CRITIQUE.value == "critique"
        assert CopywritingStage.FINALIZE.value == "finalize"
        assert CopywritingStage.COMPLETED.value == "completed"
    
    def test_stage_from_string(self):
        """Test creating stage from string."""
        assert CopywritingStage("plan") == CopywritingStage.PLAN
        assert CopywritingStage("finalize") == CopywritingStage.FINALIZE


class TestValidTransitions:
    """Tests for VALID_TRANSITIONS mapping."""
    
    def test_initial_can_only_go_to_plan(self):
        """Test that initial state (None) can only transition to PLAN."""
        assert VALID_TRANSITIONS[None] == [CopywritingStage.PLAN]
    
    def test_plan_can_only_go_to_draft(self):
        """Test that PLAN can only transition to DRAFT."""
        assert VALID_TRANSITIONS[CopywritingStage.PLAN] == [CopywritingStage.DRAFT]
    
    def test_draft_can_only_go_to_critique(self):
        """Test that DRAFT can only transition to CRITIQUE."""
        assert VALID_TRANSITIONS[CopywritingStage.DRAFT] == [CopywritingStage.CRITIQUE]
    
    def test_critique_can_only_go_to_finalize(self):
        """Test that CRITIQUE can only transition to FINALIZE."""
        assert VALID_TRANSITIONS[CopywritingStage.CRITIQUE] == [CopywritingStage.FINALIZE]
    
    def test_finalize_can_only_go_to_completed(self):
        """Test that FINALIZE can only transition to COMPLETED."""
        assert VALID_TRANSITIONS[CopywritingStage.FINALIZE] == [CopywritingStage.COMPLETED]
    
    def test_completed_is_terminal(self):
        """Test that COMPLETED is a terminal state."""
        assert VALID_TRANSITIONS[CopywritingStage.COMPLETED] == []


class TestStateTransitionValidation:
    """Tests for state transition validation logic."""
    
    def test_valid_transition_from_none_to_plan(self):
        """Test valid transition from initial to PLAN."""
        state = CopywritingState(product_name="Test", features=[])
        assert state.validate_transition(CopywritingStage.PLAN) is True
    
    def test_valid_transition_from_plan_to_draft(self):
        """Test valid transition from PLAN to DRAFT."""
        state = CopywritingState(
            product_name="Test",
            features=[],
            current_stage=CopywritingStage.PLAN,
        )
        assert state.validate_transition(CopywritingStage.DRAFT) is True
    
    def test_valid_transition_from_draft_to_critique(self):
        """Test valid transition from DRAFT to CRITIQUE."""
        state = CopywritingState(
            product_name="Test",
            features=[],
            current_stage=CopywritingStage.DRAFT,
        )
        assert state.validate_transition(CopywritingStage.CRITIQUE) is True
    
    def test_valid_transition_from_critique_to_finalize(self):
        """Test valid transition from CRITIQUE to FINALIZE."""
        state = CopywritingState(
            product_name="Test",
            features=[],
            current_stage=CopywritingStage.CRITIQUE,
        )
        assert state.validate_transition(CopywritingStage.FINALIZE) is True
    
    def test_valid_transition_from_finalize_to_completed(self):
        """Test valid transition from FINALIZE to COMPLETED."""
        state = CopywritingState(
            product_name="Test",
            features=[],
            current_stage=CopywritingStage.FINALIZE,
        )
        assert state.validate_transition(CopywritingStage.COMPLETED) is True
    
    def test_invalid_transition_from_none_to_draft(self):
        """Test invalid transition from initial to DRAFT."""
        state = CopywritingState(product_name="Test", features=[])
        with pytest.raises(InvalidStageTransitionError) as exc_info:
            state.validate_transition(CopywritingStage.DRAFT)
        assert "Cannot transition from None to" in str(exc_info.value)
    
    def test_invalid_transition_skipping_stage(self):
        """Test invalid transition skipping a stage."""
        state = CopywritingState(
            product_name="Test",
            features=[],
            current_stage=CopywritingStage.PLAN,
        )
        with pytest.raises(InvalidStageTransitionError):
            state.validate_transition(CopywritingStage.FINALIZE)
    
    def test_invalid_transition_from_completed(self):
        """Test that no transitions are allowed from COMPLETED."""
        state = CopywritingState(
            product_name="Test",
            features=[],
            current_stage=CopywritingStage.COMPLETED,
        )
        with pytest.raises(InvalidStageTransitionError):
            state.validate_transition(CopywritingStage.PLAN)


class TestStateTransitionTo:
    """Tests for transition_to method."""
    
    def test_transition_to_updates_stage(self):
        """Test that transition_to updates current_stage."""
        state = CopywritingState(product_name="Test", features=[])
        result = state.transition_to(CopywritingStage.PLAN)
        
        assert result.current_stage == CopywritingStage.PLAN
        assert result is state  # Returns self
    
    def test_transition_to_raises_on_invalid(self):
        """Test that transition_to raises on invalid transition."""
        state = CopywritingState(product_name="Test", features=[])
        with pytest.raises(InvalidStageTransitionError):
            state.transition_to(CopywritingStage.FINALIZE)


class TestStateSerialization:
    """Tests for state serialization methods."""
    
    def test_to_dict(self):
        """Test converting state to dictionary."""
        state = CopywritingState(
            product_name="Test Product",
            features=["F1", "F2"],
            workflow_id="wf-123",
            current_stage=CopywritingStage.DRAFT,
            plan="Outline",
            draft="Copy draft",
        )
        
        result = state.to_dict()
        
        assert result["product_name"] == "Test Product"
        assert result["features"] == ["F1", "F2"]
        assert result["workflow_id"] == "wf-123"
        assert result["current_stage"] == "draft"
        assert result["plan"] == "Outline"
        assert result["draft"] == "Copy draft"
        assert result["critique"] is None
        assert result["final_copy"] is None
    
    def test_to_dict_with_none_stage(self):
        """Test to_dict with None current_stage."""
        state = CopywritingState(product_name="Test", features=[])
        result = state.to_dict()
        assert result["current_stage"] is None
    
    def test_from_dict(self):
        """Test creating state from dictionary."""
        data = {
            "product_name": "Test Product",
            "features": ["F1", "F2"],
            "workflow_id": "wf-123",
            "current_stage": "draft",
            "plan": "Outline",
            "draft": "Copy draft",
            "critique": None,
            "final_copy": None,
            "brand_guidelines": "Professional",
        }
        
        state = CopywritingState.from_dict(data)
        
        assert state.product_name == "Test Product"
        assert state.features == ["F1", "F2"]
        assert state.workflow_id == "wf-123"
        assert state.current_stage == CopywritingStage.DRAFT
        assert state.plan == "Outline"
        assert state.draft == "Copy draft"
        assert state.brand_guidelines == "Professional"
    
    def test_from_dict_with_none_stage(self):
        """Test from_dict with None current_stage."""
        data = {
            "product_name": "Test",
            "features": [],
            "current_stage": None,
        }
        
        state = CopywritingState.from_dict(data)
        assert state.current_stage is None
    
    def test_from_dict_missing_optional_fields(self):
        """Test from_dict with missing optional fields."""
        data = {
            "product_name": "Test",
            "features": ["F1"],
        }
        
        state = CopywritingState.from_dict(data)
        assert state.product_name == "Test"
        assert state.features == ["F1"]
        assert state.workflow_id == ""
        assert state.current_stage is None
    
    def test_round_trip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = CopywritingState(
            product_name="Round Trip Test",
            features=["A", "B", "C"],
            workflow_id="rt-456",
            current_stage=CopywritingStage.CRITIQUE,
            plan="Plan text",
            draft="Draft text",
            critique="Critique text",
            brand_guidelines="Casual tone",
        )
        
        data = original.to_dict()
        restored = CopywritingState.from_dict(data)
        
        assert restored.product_name == original.product_name
        assert restored.features == original.features
        assert restored.workflow_id == original.workflow_id
        assert restored.current_stage == original.current_stage
        assert restored.plan == original.plan
        assert restored.draft == original.draft
        assert restored.critique == original.critique
        assert restored.brand_guidelines == original.brand_guidelines
