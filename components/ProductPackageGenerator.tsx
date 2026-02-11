/**
 * Product Package Generator Component
 *
 * Form for initiating product package generation.
 */

import React, { useState } from 'react';
import { productPackageService, ProductPackageRequest } from '../services/productPackageService';

interface ProductPackageGeneratorProps {
  onGenerate: (workflowId: string, packageId: string) => void;
}

export const ProductPackageGenerator: React.FC<ProductPackageGeneratorProps> = ({ onGenerate }) => {
  const [imageUrl, setImageUrl] = useState('');
  const [background, setBackground] = useState('');
  const [copyVariants, setCopyVariants] = useState(2);
  const [imageVariants, setImageVariants] = useState(3);
  const [videoDuration, setVideoDuration] = useState(15);
  const [requireApproval, setRequireApproval] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsGenerating(true);

    try {
      const request: ProductPackageRequest = {
        image_url: imageUrl || undefined,
        background,
        options: {
          copy_variants: copyVariants,
          image_variants: imageVariants,
          video_duration_sec: videoDuration,
          require_approval,
          force_fallback_video: false,
        },
      };

      const response = await productPackageService.generate(request);
      onGenerate(response.workflow_id, response.package_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start generation');
      setIsGenerating(false);
    }
  };

  return (
    <div className="product-package-generator">
      <h2>Generate Product Package</h2>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="image-url">Product Image URL</label>
          <input
            id="image-url"
            type="url"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            placeholder="https://example.com/product.jpg"
            disabled={isGenerating}
          />
        </div>

        <div className="form-group">
          <label htmlFor="background">Product Background</label>
          <textarea
            id="background"
            value={background}
            onChange={(e) => setBackground(e.target.value)}
            placeholder="Describe your product, target audience, and key features..."
            rows={4}
            required
            disabled={isGenerating}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="copy-variants">Copy Variants</label>
            <input
              id="copy-variants"
              type="number"
              min="1"
              max="5"
              value={copyVariants}
              onChange={(e) => setCopyVariants(parseInt(e.target.value))}
              disabled={isGenerating}
            />
          </div>

          <div className="form-group">
            <label htmlFor="image-variants">Image Variants</label>
            <input
              id="image-variants"
              type="number"
              min="1"
              max="8"
              value={imageVariants}
              onChange={(e) => setImageVariants(parseInt(e.target.value))}
              disabled={isGenerating}
            />
          </div>

          <div className="form-group">
            <label htmlFor="video-duration">Video Duration (sec)</label>
            <input
              id="video-duration"
              type="number"
              min="6"
              max="60"
              value={videoDuration}
              onChange={(e) => setVideoDuration(parseInt(e.target.value))}
              disabled={isGenerating}
            />
          </div>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={requireApproval}
              onChange={(e) => setRequireApproval(e.target.checked)}
              disabled={isGenerating}
            />
            Require manual approval before completion
          </label>
        </div>

        <button type="submit" disabled={isGenerating || !background.trim()}>
          {isGenerating ? 'Starting...' : 'Generate Package'}
        </button>
      </form>
    </div>
  );
};
