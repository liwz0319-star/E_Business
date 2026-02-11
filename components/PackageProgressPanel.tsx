/**
 * Package Progress Panel Component
 *
 * Displays real-time progress of product package generation.
 */

import React, { useEffect, useState } from 'react';
import { productPackageService, ProductPackageStatusResponse } from '../services/productPackageService';
import { webSocketService } from '../services/webSocket';

interface PackageProgressPanelProps {
  workflowId: string;
  onComplete?: () => void;
  onError?: (error: string) => void;
}

export const PackageProgressPanel: React.FC<PackageProgressPanelProps> = ({
  workflowId,
  onComplete,
  onError,
}) => {
  const [status, setStatus] = useState<ProductPackageStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Initial status fetch
    fetchStatus();

    // Set up polling for status updates
    const interval = setInterval(fetchStatus, 2000);
    setPollInterval(interval);

    // Subscribe to WebSocket events
    const unsubscribeProgress = webSocketService.subscribe('agent:progress', handleProgressEvent);
    const unsubscribeArtifact = webSocketService.subscribe('agent:artifact', handleArtifactEvent);
    const unsubscribeApproval = webSocketService.subscribe('agent:approval_required', handleApprovalEvent);
    const unsubscribeError = webSocketService.subscribe('agent:error', handleErrorEvent);

    return () => {
      clearInterval(interval);
      unsubscribeProgress();
      unsubscribeArtifact();
      unsubscribeApproval();
      unsubscribeError();
    };
  }, [workflowId]);

  const fetchStatus = async () => {
    try {
      const response = await productPackageService.getStatus(workflowId);
      setStatus(response);

      if (response.status === 'completed') {
        onComplete?.();
      } else if (response.status === 'failed') {
        const errorMsg = response.error || 'Generation failed';
        setError(errorMsg);
        onError?.(errorMsg);
      }
    } catch (err: any) {
      console.error('Failed to fetch status:', err);
    }
  };

  const handleProgressEvent = (data: any) => {
    if (data.workflowId === workflowId && status) {
      setStatus({
        ...status,
        stage: data.data.stage,
        progress_percentage: data.data.percentage,
        current_step: data.data.current_step,
      });
    }
  };

  const handleArtifactEvent = (data: any) => {
    console.log('Artifact generated:', data);
    // Could update local artifacts state here
  };

  const handleApprovalEvent = (data: any) => {
    if (data.workflowId === workflowId) {
      console.log('Approval required:', data);
    }
  };

  const handleErrorEvent = (data: any) => {
    if (data.workflowId === workflowId) {
      const errorMsg = data.data.message || 'An error occurred';
      setError(errorMsg);
      onError?.(errorMsg);
    }
  };

  if (!status) {
    return <div className="progress-panel loading">Loading status...</div>;
  }

  const stages = [
    { key: 'init', label: 'Initializing' },
    { key: 'analysis', label: 'Analyzing Product' },
    { key: 'copywriting', label: 'Generating Copywriting' },
    { key: 'image_generation', label: 'Generating Images' },
    { key: 'video_generation', label: 'Generating Video' },
    { key: 'qa_review', label: 'Quality Review' },
    { key: 'approval', label: 'Awaiting Approval' },
    { key: 'done', label: 'Complete' },
  ];

  const currentStageIndex = stages.findIndex(s => s.key === status.stage);

  return (
    <div className="progress-panel">
      <h3>Generation Progress</h3>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="progress-overview">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${status.progress_percentage}%` }}
          />
        </div>
        <div className="progress-text">
          {status.progress_percentage}% - {status.current_step}
        </div>
      </div>

      <div className="stage-list">
        {stages.map((stage, index) => (
          <div
            key={stage.key}
            className={`stage-item ${
              index === currentStageIndex ? 'current' :
              index < currentStageIndex ? 'completed' :
              'pending'
            }`}
          >
            <div className="stage-indicator">
              {index < currentStageIndex ? '✓' : index + 1}
            </div>
            <div className="stage-label">{stage.label}</div>
          </div>
        ))}
      </div>

      {status.artifacts && Object.keys(status.artifacts).length > 0 && (
        <div className="artifacts-summary">
          <h4>Generated Artifacts</h4>
          {Object.entries(status.artifacts).map(([type, items]) => (
            <div key={type} className="artifact-type">
              <strong>{type}:</strong> {Array.isArray(items) ? items.length : 1}
            </div>
          ))}
        </div>
      )}

      {status.status === 'approval_required' && (
        <div className="approval-notice">
          <strong>⚠️ Approval Required</strong>
          <p>This package requires manual approval before completion.</p>
        </div>
      )}
    </div>
  );
};
