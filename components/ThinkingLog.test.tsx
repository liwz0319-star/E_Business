/**
 * Unit Tests for ThinkingLog Component
 * Story 2-4: Frontend Copywriting UI Integration
 *
 * TEST-001 Fix: Add comprehensive unit tests for ThinkingLog component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ThinkingLog, {
    ThinkingStep,
    ConnectionStatus,
    eventToStep
} from './ThinkingLog';
import { ThoughtEvent } from '../services/webSocket';

describe('ThinkingLog Component', () => {
    const mockSteps: ThinkingStep[] = [
        {
            id: 'step-1',
            nodeName: 'plan',
            content: 'Planning the content structure...',
            timestamp: '2026-01-01T00:00:00Z',
            status: 'completed'
        },
        {
            id: 'step-2',
            nodeName: 'draft',
            content: 'Drafting initial content...',
            timestamp: '2026-01-01T00:01:00Z',
            status: 'active'
        }
    ];

    describe('Rendering', () => {
        it('should render header with AI thinking title', () => {
            render(
                <ThinkingLog
                    steps={[]}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            expect(screen.getByText('AI 思考过程')).toBeInTheDocument();
        });

        it('should render connection status indicator', () => {
            render(
                <ThinkingLog
                    steps={[]}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            expect(screen.getByText('已连接')).toBeInTheDocument();
        });

        it('should render connecting status with pulse animation', () => {
            render(
                <ThinkingLog
                    steps={[]}
                    connectionStatus="connecting"
                    isComplete={false}
                />
            );

            expect(screen.getByText('连接中...')).toBeInTheDocument();
        });

        it('should render error status', () => {
            render(
                <ThinkingLog
                    steps={[]}
                    connectionStatus="error"
                    isComplete={false}
                />
            );

            expect(screen.getByText('连接错误')).toBeInTheDocument();
        });
    });

    describe('Steps Display', () => {
        it('should render thinking steps', () => {
            render(
                <ThinkingLog
                    steps={mockSteps}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            expect(screen.getByText('Planning the content structure...')).toBeInTheDocument();
            expect(screen.getByText('Drafting initial content...')).toBeInTheDocument();
        });

        it('should display node labels correctly', () => {
            render(
                <ThinkingLog
                    steps={mockSteps}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            expect(screen.getByText('规划')).toBeInTheDocument();
            expect(screen.getByText('起草')).toBeInTheDocument();
        });

        it('should show original node_name for visible distinction (AC-001)', () => {
            render(
                <ThinkingLog
                    steps={mockSteps}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            // AC-001 Fix: Should display original node_name values
            expect(screen.getByText('plan')).toBeInTheDocument();
            expect(screen.getByText('draft')).toBeInTheDocument();
        });

        it('should show active status indicator for active steps', () => {
            render(
                <ThinkingLog
                    steps={mockSteps}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            expect(screen.getByText('进行中')).toBeInTheDocument();
        });

        it('should display waiting message when connected but no steps', () => {
            render(
                <ThinkingLog
                    steps={[]}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            expect(screen.getByText('等待 AI 响应...')).toBeInTheDocument();
        });
    });

    describe('Completion Indicator', () => {
        it('should show completion indicator when isComplete is true', () => {
            render(
                <ThinkingLog
                    steps={mockSteps}
                    connectionStatus="connected"
                    isComplete={true}
                />
            );

            expect(screen.getByText('生成完成')).toBeInTheDocument();
        });

        it('should not show completion indicator when isComplete is false', () => {
            render(
                <ThinkingLog
                    steps={mockSteps}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            expect(screen.queryByText('生成完成')).not.toBeInTheDocument();
        });
    });

    describe('Error Handling', () => {
        it('should display error message when provided', () => {
            render(
                <ThinkingLog
                    steps={[]}
                    connectionStatus="error"
                    isComplete={false}
                    errorMessage="Connection failed"
                />
            );

            expect(screen.getByText('Connection failed')).toBeInTheDocument();
        });

        it('should show retry button when onRetry is provided (ERROR-001)', () => {
            const onRetry = vi.fn();
            render(
                <ThinkingLog
                    steps={[]}
                    connectionStatus="error"
                    isComplete={false}
                    errorMessage="Generation failed"
                    onRetry={onRetry}
                />
            );

            const retryButton = screen.getByText('重试');
            expect(retryButton).toBeInTheDocument();

            fireEvent.click(retryButton);
            expect(onRetry).toHaveBeenCalledTimes(1);
        });

        it('should not show retry button when onRetry is not provided', () => {
            render(
                <ThinkingLog
                    steps={[]}
                    connectionStatus="error"
                    isComplete={false}
                    errorMessage="Generation failed"
                />
            );

            expect(screen.queryByText('重试')).not.toBeInTheDocument();
        });
    });

    describe('Node Configuration', () => {
        it('should use default config for unknown node names', () => {
            const steps: ThinkingStep[] = [{
                id: 'step-1',
                nodeName: 'unknown_node',
                content: 'Unknown step',
                timestamp: '2026-01-01T00:00:00Z',
                status: 'active'
            }];

            render(
                <ThinkingLog
                    steps={steps}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            // Should fall back to default label
            expect(screen.getByText('思考中')).toBeInTheDocument();
        });

        it('should handle case-insensitive node name matching (HI-003)', () => {
            const steps: ThinkingStep[] = [{
                id: 'step-1',
                nodeName: 'PLAN', // uppercase
                content: 'Planning...',
                timestamp: '2026-01-01T00:00:00Z',
                status: 'completed'
            }];

            render(
                <ThinkingLog
                    steps={steps}
                    connectionStatus="connected"
                    isComplete={false}
                />
            );

            // Should match 'plan' config despite uppercase input
            expect(screen.getByText('规划')).toBeInTheDocument();
        });
    });
});

describe('eventToStep Helper', () => {
    it('should convert ThoughtEvent to ThinkingStep', () => {
        const event: ThoughtEvent = {
            type: 'thought',
            workflowId: 'workflow-123',
            data: {
                node_name: 'plan',
                content: 'Planning content...'
            },
            timestamp: '2026-01-01T00:00:00Z'
        };

        const step = eventToStep(event, 'active');

        expect(step.id).toBe('workflow-123-2026-01-01T00:00:00Z');
        expect(step.nodeName).toBe('plan');
        expect(step.content).toBe('Planning content...');
        expect(step.status).toBe('active');
    });

    it('should use default node name when not provided', () => {
        const event: ThoughtEvent = {
            type: 'thought',
            workflowId: 'workflow-123',
            data: {
                content: 'Thinking...'
            },
            timestamp: '2026-01-01T00:00:00Z'
        };

        const step = eventToStep(event, 'active');

        expect(step.nodeName).toBe('default');
    });

    it('should default to active status', () => {
        const event: ThoughtEvent = {
            type: 'thought',
            workflowId: 'workflow-123',
            data: {
                content: 'Thinking...'
            },
            timestamp: '2026-01-01T00:00:00Z'
        };

        const step = eventToStep(event);

        expect(step.status).toBe('active');
    });
});
