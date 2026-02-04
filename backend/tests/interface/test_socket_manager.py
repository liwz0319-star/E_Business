"""
Tests for SocketManager emit_thought with node_name parameter.

Story 2-3: Thinking Stream Integration
"""
import pytest
from unittest.mock import AsyncMock, patch


class TestEmitThoughtWithNodeName:
    """Tests for emit_thought method with node_name parameter."""
    
    @pytest.mark.asyncio
    async def test_emit_thought_with_node_name(self):
        """Test emit_thought includes node_name in payload when provided."""
        from app.interface.ws.socket_manager import SocketManager
        
        manager = SocketManager()
        
        with patch.object(manager.sio, 'emit', new_callable=AsyncMock) as mock_emit:
            await manager.emit_thought(
                workflow_id="test-wf-id",
                content="Test thought content",
                node_name="plan"
            )
            
            # Verify emit was called once
            mock_emit.assert_called_once()
            
            # Get the call arguments
            call_args = mock_emit.call_args
            event_name = call_args[0][0]  # First positional arg is event name
            payload = call_args[0][1]     # Second positional arg is payload
            
            # Verify event name
            assert event_name == "agent:thought"
            
            # Verify payload structure
            assert payload["type"] == "thought"
            assert payload["workflowId"] == "test-wf-id"
            assert payload["data"]["content"] == "Test thought content"
            assert payload["data"]["node_name"] == "plan"
            assert "timestamp" in payload
    
    @pytest.mark.asyncio
    async def test_emit_thought_without_node_name(self):
        """Test emit_thought works when node_name is None (edge case)."""
        from app.interface.ws.socket_manager import SocketManager
        
        manager = SocketManager()
        
        with patch.object(manager.sio, 'emit', new_callable=AsyncMock) as mock_emit:
            await manager.emit_thought(
                workflow_id="test-wf-id",
                content="Test without node_name"
                # node_name defaults to None
            )
            
            call_args = mock_emit.call_args
            payload = call_args[0][1]
            
            # node_name should NOT be in payload when None
            assert "node_name" not in payload["data"]
            assert payload["data"]["content"] == "Test without node_name"
    
    @pytest.mark.asyncio
    async def test_emit_thought_with_all_node_names(self):
        """Test emit_thought with all valid node_name values."""
        from app.interface.ws.socket_manager import SocketManager
        
        valid_node_names = ["plan", "draft", "critique", "finalize"]
        
        for node_name in valid_node_names:
            manager = SocketManager()
            
            with patch.object(manager.sio, 'emit', new_callable=AsyncMock) as mock_emit:
                await manager.emit_thought(
                    workflow_id="test-wf-id",
                    content=f"Testing {node_name}",
                    node_name=node_name
                )
                
                payload = mock_emit.call_args[0][1]
                assert payload["data"]["node_name"] == node_name
    
    @pytest.mark.asyncio
    async def test_emit_thought_with_sid(self):
        """Test emit_thought with specific socket ID."""
        from app.interface.ws.socket_manager import SocketManager
        
        manager = SocketManager()
        
        with patch.object(manager.sio, 'emit', new_callable=AsyncMock) as mock_emit:
            await manager.emit_thought(
                workflow_id="test-wf-id",
                content="Test thought",
                node_name="plan",
                sid="socket-123"
            )
            
            # Verify room parameter is set correctly
            call_kwargs = mock_emit.call_args[1]  # keyword arguments
            assert call_kwargs["room"] == "socket-123"
    
    @pytest.mark.asyncio
    async def test_emit_thought_handles_emit_failure(self):
        """Test emit_thought handles exceptions gracefully."""
        from app.interface.ws.socket_manager import SocketManager
        
        manager = SocketManager()
        
        with patch.object(manager.sio, 'emit', new_callable=AsyncMock) as mock_emit:
            mock_emit.side_effect = Exception("Connection error")
            
            # Should not raise, just log error
            await manager.emit_thought(
                workflow_id="test-wf-id",
                content="Test thought",
                node_name="plan"
            )
            
            # Verify emit was attempted
            mock_emit.assert_called_once()


class TestEmitThoughtPayloadStructure:
    """Tests to verify emit_thought payload structure matches frontend expectations."""
    
    @pytest.mark.asyncio
    async def test_payload_structure_matches_api_contract(self):
        """Test that payload structure matches the API contract."""
        from app.interface.ws.socket_manager import SocketManager
        
        manager = SocketManager()
        
        with patch.object(manager.sio, 'emit', new_callable=AsyncMock) as mock_emit:
            await manager.emit_thought(
                workflow_id="workflow-uuid-123",
                content="Analyzing target audience...",
                node_name="plan"
            )
            
            payload = mock_emit.call_args[0][1]
            
            # Verify all required fields are present
            assert "type" in payload
            assert "workflowId" in payload
            assert "data" in payload
            assert "timestamp" in payload
            
            # Verify data structure
            assert "content" in payload["data"]
            assert "node_name" in payload["data"]
            
            # Verify timestamp format (ISO 8601 with Z suffix)
            timestamp = payload["timestamp"]
            assert timestamp.endswith("Z")
    
    @pytest.mark.asyncio
    async def test_workflow_id_is_camel_case_in_payload(self):
        """Test that workflow_id is converted to camelCase in payload."""
        from app.interface.ws.socket_manager import SocketManager
        
        manager = SocketManager()
        
        with patch.object(manager.sio, 'emit', new_callable=AsyncMock) as mock_emit:
            await manager.emit_thought(
                workflow_id="test-id",
                content="Test",
                node_name="plan"
            )
            
            payload = mock_emit.call_args[0][1]
            
            # Should be camelCase
            assert "workflowId" in payload
            # Should not be snake_case
            assert "workflow_id" not in payload
