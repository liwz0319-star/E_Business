/**
 * Package Result Display Component
 *
 * Displays the final generated product package.
 */

import React, { useEffect, useState } from 'react';
import {
  productPackageService,
  ProductPackageResponse,
  ApproveRequest
} from '../services/productPackageService';

interface PackageResultDisplayProps {
  packageId: string;
}

export const PackageResultDisplay: React.FC<PackageResultDisplayProps> = ({ packageId }) => {
  const [pkg, setPkg] = useState<ProductPackageResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    fetchPackage();
  }, [packageId]);

  const fetchPackage = async () => {
    try {
      const response = await productPackageService.getPackage(packageId);
      setPkg(response);
    } catch (err: any) {
      setError(err.message || 'Failed to load package');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (decision: 'approve' | 'reject') => {
    setApproving(true);
    try {
      const request: ApproveRequest = {
        decision,
        comment: '', // Could add comment dialog
      };
      await productPackageService.approve(packageId, request);
      await fetchPackage(); // Refresh
    } catch (err: any) {
      setError(err.message || 'Failed to process approval');
    } finally {
      setApproving(false);
    }
  };

  if (loading) {
    return <div className="result-display loading">Loading package...</div>;
  }

  if (error || !pkg) {
    return <div className="result-display error">{error || 'Package not found'}</div>;
  }

  return (
    <div className="result-display">
      <div className="package-header">
        <h2>Product Package</h2>
        <div className="package-meta">
          <span className={`status status-${pkg.status}`}>{pkg.status}</span>
          <span className="stage">{pkg.stage}</span>
        </div>
      </div>

      {/* Analysis Section */}
      {pkg.analysis && (
        <section className="package-section">
          <h3>Product Analysis</h3>
          <div className="analysis-content">
            <div><strong>Category:</strong> {pkg.analysis.category}</div>
            <div><strong>Style:</strong> {pkg.analysis.style}</div>
            <div><strong>Target Audience:</strong> {pkg.analysis.target_audience}</div>
            <div><strong>Key Features:</strong></div>
            <ul>
              {pkg.analysis.key_features?.map((feature: string, i: number) => (
                <li key={i}>{feature}</li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* Copywriting Section */}
      {pkg.copywriting_versions && pkg.copywriting_versions.length > 0 && (
        <section className="package-section">
          <h3>Copywriting</h3>
          {pkg.copywriting_versions.map((version, index) => (
            <div key={index} className="copywriting-item">
              <h4>{version.channel}</h4>
              <pre className="copywriting-content">{version.content || 'Content not available'}</pre>
            </div>
          ))}
        </section>
      )}

      {/* Images Section */}
      {pkg.images && pkg.images.length > 0 && (
        <section className="package-section">
          <h3>Images</h3>
          <div className="images-grid">
            {pkg.images.map((image, index) => (
              <div key={index} className="image-item">
                <img src={image.url} alt={image.label} />
                <div className="image-label">{image.label}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Video Section */}
      {pkg.video && (
        <section className="package-section">
          <h3>
            Video
            {pkg.video.is_fallback && <span className="fallback-badge">Slideshow Fallback</span>}
          </h3>
          <div className="video-container">
            <video src={pkg.video.url} controls />
            {pkg.video.duration && (
              <div className="video-meta">Duration: {pkg.video.duration}s</div>
            )}
          </div>
        </section>
      )}

      {/* QA Report Section */}
      {pkg.qa_report && (
        <section className="package-section">
          <h3>Quality Report</h3>
          <div className="qa-report">
            <div className="qa-score">
              Score: <strong>{(pkg.qa_report.score * 100).toFixed(0)}%</strong>
            </div>
            {pkg.qa_report.issues && pkg.qa_report.issues.length > 0 && (
              <div className="qa-issues">
                <strong>Issues:</strong>
                <ul>
                  {pkg.qa_report.issues.map((issue: string, i: number) => (
                    <li key={i}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}
            {pkg.qa_report.suggestions && pkg.qa_report.suggestions.length > 0 && (
              <div className="qa-suggestions">
                <strong>Suggestions:</strong>
                <ul>
                  {pkg.qa_report.suggestions.map((suggestion: string, i: number) => (
                    <li key={i}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Approval Actions */}
      {pkg.status === 'approval_required' && (
        <section className="package-section approval-actions">
          <h3>Approval Required</h3>
          <p>Please review and approve or reject this package.</p>
          <div className="approval-buttons">
            <button
              onClick={() => handleApprove('approve')}
              disabled={approving}
              className="btn-approve"
            >
              {approving ? 'Processing...' : 'Approve'}
            </button>
            <button
              onClick={() => handleApprove('reject')}
              disabled={approving}
              className="btn-reject"
            >
              {approving ? 'Processing...' : 'Reject'}
            </button>
          </div>
        </section>
      )}
    </div>
  );
};
