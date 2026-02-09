/**
 * WebSocket Service for Agent Communication
 * Story 2-4: Frontend Copywriting UI Integration
 * 
 * Handles Socket.io connection and agent event subscriptions
 */
import { io, Socket } from 'socket.io-client';
import authService from './authService';

// Socket.io connection URL (base URL, not /ws)
const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// =====================
// Type Definitions
// =====================

export interface ThoughtEvent {
    type: 'thought';
    workflowId: string;
    data: {
        node_name?: string;
        content: string;
    };
    timestamp: string;
}

export interface ResultEvent {
    type: 'result';
    workflowId: string;
    data: {
        finalCopy: string;  // Backend sends camelCase
        stage?: string;
        [key: string]: unknown;
    };
    timestamp: string;
}

export interface ErrorEvent {
    type: 'error';
    workflowId: string;
    data: {
        code: string;
        message: string;
        details?: unknown;
    };
    timestamp: string;
}

export interface ToolCallEvent {
    type: 'tool_call';
    workflowId: string;
    data: {
        tool_name: string;
        status: 'in_progress' | 'completed' | 'error';
        message: string;
    };
    timestamp: string;
}

export type AgentEvent = ThoughtEvent | ResultEvent | ErrorEvent | ToolCallEvent;

export interface SocketEventHandlers {
    onThought?: (event: ThoughtEvent) => void;
    onResult?: (event: ResultEvent) => void;
    onError?: (event: ErrorEvent) => void;
    onToolCall?: (event: ToolCallEvent) => void;
    onConnect?: () => void;
    onDisconnect?: (reason: string) => void;
    onConnectError?: (error: Error) => void;
}

// =====================
// Socket Manager
// =====================

class WebSocketService {
    private socket: Socket | null = null;
    private handlers: SocketEventHandlers = {};
    private workflowId: string | null = null;

    /**
     * Connect to Socket.io server with authentication
     */
    connect(handlers: SocketEventHandlers): boolean {
        // Verify authentication before connecting
        if (!authService.isAuthenticated()) {
            console.error('[WebSocket] User not authenticated');
            return false;
        }

        const token = authService.getCurrentUserToken();
        if (!token) {
            console.error('[WebSocket] No auth token available');
            return false;
        }

        // Store handlers
        this.handlers = handlers;

        // Create socket connection
        // Path: '/socket.io' (default path used by backend python-socketio)
        this.socket = io(SOCKET_URL, {
            path: '/socket.io',
            auth: { token },
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5,
            transports: ['websocket', 'polling']
        });

        // Setup event listeners
        this.setupListeners();

        return true;
    }

    /**
     * Set the active workflow ID for filtering events
     */
    setWorkflowId(workflowId: string): void {
        this.workflowId = workflowId;
    }

    /**
     * Get current connection status
     */
    isConnected(): boolean {
        return this.socket?.connected ?? false;
    }

    /**
     * Setup all socket event listeners
     */
    private setupListeners(): void {
        if (!this.socket) return;

        // Connection events
        this.socket.on('connect', () => {
            console.log('[WebSocket] Connected');
            this.handlers.onConnect?.();
        });

        this.socket.on('disconnect', (reason) => {
            console.log('[WebSocket] Disconnected:', reason);
            this.handlers.onDisconnect?.(reason);
        });

        this.socket.on('connect_error', (error) => {
            console.error('[WebSocket] Connection error:', error);
            this.handlers.onConnectError?.(error);
        });

        // Agent events
        this.socket.on('agent:thought', (event: ThoughtEvent) => {
            console.log('[WebSocket] Thought:', event);
            // Ignore all agent events until the current workflowId is known.
            if (!this.workflowId) return;
            if (event.workflowId === this.workflowId) {
                this.handlers.onThought?.(event);
            }
        });

        this.socket.on('agent:result', (event: ResultEvent) => {
            console.log('[WebSocket] Result:', event);
            if (!this.workflowId) return;
            if (event.workflowId === this.workflowId) {
                this.handlers.onResult?.(event);
            }
        });

        this.socket.on('agent:error', (event: ErrorEvent) => {
            console.error('[WebSocket] Error:', event);
            if (!this.workflowId) return;
            if (event.workflowId === this.workflowId) {
                this.handlers.onError?.(event);
            }
        });

        this.socket.on('agent:tool_call', (event: ToolCallEvent) => {
            console.log('[WebSocket] Tool call:', event);
            if (!this.workflowId) return;
            if (event.workflowId === this.workflowId) {
                this.handlers.onToolCall?.(event);
            }
        });
    }

    /**
     * Disconnect from socket server
     */
    disconnect(): void {
        if (this.socket) {
            this.socket.removeAllListeners();
            this.socket.disconnect();
            this.socket = null;
        }
        this.handlers = {};
        this.workflowId = null;
        console.log('[WebSocket] Cleaned up');
    }

    /**
     * Update event handlers
     */
    updateHandlers(handlers: Partial<SocketEventHandlers>): void {
        this.handlers = { ...this.handlers, ...handlers };
    }
}

// Export singleton instance
const webSocketService = new WebSocketService();
export default webSocketService;
