/**
 * ThinkingLog Component
 * Story 2-4: Frontend Copywriting UI Integration
 * 
 * Visualizes the AI thinking stream with node progress indicators
 */
import React from 'react';
import { ThoughtEvent, ResultEvent, ErrorEvent } from '../services/webSocket';

// =====================
// Type Definitions
// =====================

export interface ThinkingStep {
    id: string;
    nodeName: string;
    content: string;
    timestamp: string;
    status: 'active' | 'completed' | 'error';
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

interface ThinkingLogProps {
    steps: ThinkingStep[];
    connectionStatus: ConnectionStatus;
    isComplete: boolean;
    errorMessage?: string;
    // ERROR-001 Fix: Add optional retry callback
    onRetry?: () => void;
}

// Node display names and icons
// HI-003: Use lowercase keys for case-insensitive matching
// Story 3-3: Added image generation nodes
const NODE_CONFIG: Record<string, { label: string; icon: string; color: string }> = {
    // Copywriting nodes
    'plan': { label: '规划', icon: 'psychology', color: 'text-blue-500' },
    'draft': { label: '起草', icon: 'edit_note', color: 'text-green-500' },
    'critique': { label: '评审', icon: 'rate_review', color: 'text-amber-500' },
    'finalize': { label: '定稿', icon: 'check_circle', color: 'text-purple-500' },
    // Image generation nodes (Story 3-3)
    'optimize_prompt': { label: '优化提示词', icon: 'auto_fix_high', color: 'text-cyan-500' },
    'generate_image': { label: '生成图像', icon: 'image', color: 'text-pink-500' },
    'persist_artifact': { label: '保存资源', icon: 'cloud_upload', color: 'text-emerald-500' },
    'image_agent': { label: '图像代理', icon: 'auto_awesome', color: 'text-violet-500' },
    // Default
    'default': { label: '思考中', icon: 'auto_awesome', color: 'text-slate-500' }
};

// =====================
// Component
// =====================

const ThinkingLog: React.FC<ThinkingLogProps> = ({
    steps,
    connectionStatus,
    isComplete,
    errorMessage,
    onRetry
}) => {
    // HI-003: Case-insensitive node name lookup
    const getNodeConfig = (nodeName: string) => {
        const key = nodeName?.toLowerCase() || 'default';
        return NODE_CONFIG[key] || NODE_CONFIG['default'];
    };

    const getConnectionStatusDisplay = () => {
        switch (connectionStatus) {
            case 'connecting':
                return { label: '连接中...', color: 'bg-yellow-500', pulse: true };
            case 'connected':
                return { label: '已连接', color: 'bg-green-500', pulse: false };
            case 'disconnected':
                return { label: '已断开', color: 'bg-slate-400', pulse: false };
            case 'error':
                return { label: '连接错误', color: 'bg-red-500', pulse: false };
        }
    };

    const statusDisplay = getConnectionStatusDisplay();

    return (
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <span className="material-icons-round text-primary text-lg">psychology</span>
                    <span className="font-bold text-sm text-slate-700 dark:text-slate-200">AI 思考过程</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${statusDisplay.color} ${statusDisplay.pulse ? 'animate-pulse' : ''}`}></span>
                    <span className="text-xs text-slate-500">{statusDisplay.label}</span>
                </div>
            </div>

            {/* Error Message with Retry Button (ERROR-001 Fix) */}
            {errorMessage && (
                <div className="mb-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                            <span className="material-icons-round text-sm">error</span>
                            <span className="text-sm font-medium">{errorMessage}</span>
                        </div>
                        {onRetry && (
                            <button
                                onClick={onRetry}
                                className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
                            >
                                <span className="material-icons-round text-sm">refresh</span>
                                重试
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* Steps */}
            <div className="space-y-3">
                {steps.length === 0 && connectionStatus === 'connected' && (
                    <div className="flex items-center gap-3 text-slate-400 py-2">
                        <span className="material-icons-round animate-spin text-lg">refresh</span>
                        <span className="text-sm">等待 AI 响应...</span>
                    </div>
                )}

                {steps.map((step, index) => {
                    const config = getNodeConfig(step.nodeName);
                    const isLast = index === steps.length - 1;

                    return (
                        <div key={step.id} className="relative">
                            {/* Connector line */}
                            {!isLast && (
                                <div className="absolute left-[11px] top-8 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700"></div>
                            )}

                            <div className="flex gap-3">
                                {/* Icon */}
                                <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${step.status === 'active'
                                    ? 'bg-primary/20 animate-pulse'
                                    : step.status === 'error'
                                        ? 'bg-red-100 dark:bg-red-900/30'
                                        : 'bg-slate-100 dark:bg-slate-700'
                                    }`}>
                                    <span className={`material-icons-round text-sm ${step.status === 'error' ? 'text-red-500' : config.color
                                        }`}>
                                        {step.status === 'error' ? 'error' : config.icon}
                                    </span>
                                </div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="font-semibold text-sm text-slate-700 dark:text-slate-200">
                                            {config.label}
                                        </span>
                                        {/* AC-001 Fix: Show original node_name for visible distinction (AC5) */}
                                        {step.nodeName && step.nodeName !== 'default' && (
                                            <span className="text-[10px] px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 rounded font-mono">
                                                {step.nodeName}
                                            </span>
                                        )}
                                        {step.status === 'active' && (
                                            <span className="text-[10px] px-1.5 py-0.5 bg-primary/10 text-primary rounded font-medium">
                                                进行中
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed break-words">
                                        {step.content}
                                    </p>
                                </div>
                            </div>
                        </div>
                    );
                })}

                {/* Completion indicator */}
                {isComplete && (
                    <div className="flex items-center gap-3 pt-2 border-t border-slate-200 dark:border-slate-700 mt-3">
                        <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                            <span className="material-icons-round text-sm text-green-500">check</span>
                        </div>
                        <span className="text-sm font-medium text-green-600 dark:text-green-400">
                            生成完成
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ThinkingLog;

// =====================
// Helper Hooks
// =====================

/**
 * Convert ThoughtEvent to ThinkingStep
 */
export function eventToStep(event: ThoughtEvent, status: ThinkingStep['status'] = 'active'): ThinkingStep {
    return {
        id: `${event.workflowId}-${event.timestamp}`,
        nodeName: event.data.node_name || 'default',
        content: event.data.content,
        timestamp: event.timestamp,
        status
    };
}
