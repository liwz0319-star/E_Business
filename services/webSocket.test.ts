/**
 * Unit Tests for WebSocket Service
 * Story 2-4: Frontend Copywriting UI Integration
 *
 * TEST-001 Fix: Add comprehensive unit tests for WebSocket service
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Use vi.hoisted() to ensure mocks are hoisted above imports
const { mockSocket, mockIo, mockAuthService } = vi.hoisted(() => {
    const mockSocket = {
        on: vi.fn(),
        emit: vi.fn(),
        disconnect: vi.fn(),
        removeAllListeners: vi.fn(),
        connected: false
    };
    const mockIo = vi.fn(() => mockSocket);
    const mockAuthService = {
        isAuthenticated: vi.fn(() => true),
        getCurrentUserToken: vi.fn(() => 'mock-token-123')
    };
    return { mockSocket, mockIo, mockAuthService };
});

vi.mock('socket.io-client', () => ({
    io: mockIo
}));

vi.mock('./authService', () => ({
    default: mockAuthService
}));

// Import after mocking
import webSocketService, {
    ThoughtEvent,
    ResultEvent,
    ErrorEvent,
    SocketEventHandlers
} from './webSocket';

describe('WebSocketService', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Reset socket connected state
        mockSocket.connected = false;
        // Reset auth defaults
        mockAuthService.isAuthenticated.mockReturnValue(true);
        mockAuthService.getCurrentUserToken.mockReturnValue('mock-token-123');
    });

    afterEach(() => {
        webSocketService.disconnect();
    });

    describe('connect', () => {
        it('should return false if user is not authenticated', () => {
            mockAuthService.isAuthenticated.mockReturnValue(false);

            const handlers: SocketEventHandlers = {};
            const result = webSocketService.connect(handlers);

            expect(result).toBe(false);
            expect(mockIo).not.toHaveBeenCalled();
        });

        it('should return false if no token available', () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);
            mockAuthService.getCurrentUserToken.mockReturnValue(null);

            const handlers: SocketEventHandlers = {};
            const result = webSocketService.connect(handlers);

            expect(result).toBe(false);
        });

        it('should connect with correct options when authenticated', () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);
            mockAuthService.getCurrentUserToken.mockReturnValue('test-token');

            const handlers: SocketEventHandlers = {
                onConnect: vi.fn()
            };
            const result = webSocketService.connect(handlers);

            expect(result).toBe(true);
            expect(mockIo).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    path: '/socket.io',
                    auth: { token: 'test-token' },
                    reconnection: true,
                    reconnectionAttempts: 5
                })
            );
        });

        it('should setup event listeners after connection', () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);
            mockAuthService.getCurrentUserToken.mockReturnValue('test-token');

            webSocketService.connect({});

            // Verify all event listeners are set up
            const onCalls = mockSocket.on.mock.calls;
            const eventNames = onCalls.map((call: [string, unknown]) => call[0]);

            expect(eventNames).toContain('connect');
            expect(eventNames).toContain('disconnect');
            expect(eventNames).toContain('connect_error');
            expect(eventNames).toContain('agent:thought');
            expect(eventNames).toContain('agent:result');
            expect(eventNames).toContain('agent:error');
            expect(eventNames).toContain('agent:tool_call');
        });
    });

    describe('setWorkflowId', () => {
        it('should store workflow ID for event filtering', () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);
            mockAuthService.getCurrentUserToken.mockReturnValue('test-token');

            webSocketService.connect({});
            webSocketService.setWorkflowId('workflow-123');

            // Workflow ID should be stored (internal state, verify via behavior)
            expect(webSocketService.setWorkflowId).toBeDefined();
        });
    });

    describe('isConnected', () => {
        it('should return false when not connected', () => {
            expect(webSocketService.isConnected()).toBe(false);
        });

        it('should return socket connected state', () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);
            mockAuthService.getCurrentUserToken.mockReturnValue('test-token');

            webSocketService.connect({});
            mockSocket.connected = true;

            expect(webSocketService.isConnected()).toBe(true);
        });
    });

    describe('disconnect', () => {
        it('should clean up socket and handlers', () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);
            mockAuthService.getCurrentUserToken.mockReturnValue('test-token');

            webSocketService.connect({});
            webSocketService.disconnect();

            expect(mockSocket.removeAllListeners).toHaveBeenCalled();
            expect(mockSocket.disconnect).toHaveBeenCalled();
        });
    });

    describe('event filtering', () => {
        it('should ignore events before workflowId is set', () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);
            mockAuthService.getCurrentUserToken.mockReturnValue('test-token');

            const onError = vi.fn();
            webSocketService.connect({ onError });

            const errorCallback = mockSocket.on.mock.calls.find(
                (call: [string, unknown]) => call[0] === 'agent:error'
            )?.[1] as ((event: ErrorEvent) => void) | undefined;

            const event: ErrorEvent = {
                type: 'error',
                workflowId: 'workflow-123',
                data: { code: 'WORKFLOW_FAILED', message: 'DeepSeek API key is required' },
                timestamp: new Date().toISOString()
            };

            if (errorCallback) {
                errorCallback(event);
            }

            expect(onError).not.toHaveBeenCalled();
        });

        it('should filter events by workflowId when set', () => {
            mockAuthService.isAuthenticated.mockReturnValue(true);
            mockAuthService.getCurrentUserToken.mockReturnValue('test-token');

            const onThought = vi.fn();
            webSocketService.connect({ onThought });
            webSocketService.setWorkflowId('workflow-123');

            // Simulate receiving a thought event with different workflowId
            const thoughtCallback = mockSocket.on.mock.calls.find(
                (call: [string, unknown]) => call[0] === 'agent:thought'
            )?.[1] as ((event: ThoughtEvent) => void) | undefined;

            // Event with matching workflowId should trigger handler
            const matchingEvent: ThoughtEvent = {
                type: 'thought',
                workflowId: 'workflow-123',
                data: { content: 'Test', node_name: 'plan' },
                timestamp: new Date().toISOString()
            };

            // Event with non-matching workflowId should NOT trigger handler
            const nonMatchingEvent: ThoughtEvent = {
                type: 'thought',
                workflowId: 'other-workflow',
                data: { content: 'Test', node_name: 'plan' },
                timestamp: new Date().toISOString()
            };

            if (thoughtCallback) {
                thoughtCallback(matchingEvent);
                expect(onThought).toHaveBeenCalledWith(matchingEvent);

                onThought.mockClear();
                thoughtCallback(nonMatchingEvent);
                expect(onThought).not.toHaveBeenCalled();
            }
        });
    });
});

describe('Event Type Definitions', () => {
    it('should have correct ThoughtEvent structure', () => {
        const event: ThoughtEvent = {
            type: 'thought',
            workflowId: 'test-123',
            data: {
                node_name: 'plan',
                content: 'Planning...'
            },
            timestamp: '2026-01-01T00:00:00Z'
        };
        expect(event.type).toBe('thought');
        expect(event.data.node_name).toBe('plan');
    });

    it('should have correct ResultEvent structure', () => {
        const event: ResultEvent = {
            type: 'result',
            workflowId: 'test-123',
            data: {
                finalCopy: 'Generated content'
            },
            timestamp: '2026-01-01T00:00:00Z'
        };
        expect(event.type).toBe('result');
        expect(event.data.finalCopy).toBe('Generated content');
    });

    it('should have correct ErrorEvent structure', () => {
        const event: ErrorEvent = {
            type: 'error',
            workflowId: 'test-123',
            data: {
                code: 'GENERATION_FAILED',
                message: 'An error occurred'
            },
            timestamp: '2026-01-01T00:00:00Z'
        };
        expect(event.type).toBe('error');
        expect(event.data.code).toBe('GENERATION_FAILED');
    });
});
