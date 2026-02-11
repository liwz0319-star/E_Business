/**
 * Product Package Service
 *
 * API client for product package generation and management.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

export interface ProductPackageOptions {
  copy_variants: number;
  image_variants: number;
  video_duration_sec: number;
  require_approval: boolean;
  force_fallback_video: boolean;
}

export interface ProductPackageRequest {
  image_url?: string;
  image_asset_id?: string;
  background: string;
  options?: ProductPackageOptions;
}

export interface ProductPackageGenerateResponse {
  package_id: string;
  workflow_id: string;
  status: string;
  stage: string;
}

export interface ProductPackageStatusResponse {
  package_id: string;
  workflow_id: string;
  status: 'pending' | 'running' | 'approval_required' | 'completed' | 'failed' | 'cancelled';
  stage: 'init' | 'analysis' | 'copywriting' | 'image_generation' | 'video_generation' | 'qa_review' | 'approval' | 'done';
  progress_percentage: number;
  current_step: string;
  artifacts: Record<string, any>;
  error?: string;
}

export interface ArtifactDetail {
  asset_id: string;
  url?: string;
  label?: string;
}

export interface CopywritingArtifact extends ArtifactDetail {
  channel: string;
  content?: string;
}

export interface ImageArtifact extends ArtifactDetail {
  scene: string;
}

export interface VideoArtifact extends ArtifactDetail {
  is_fallback: boolean;
  duration?: number;
}

export interface ProductPackageResponse {
  package_id: string;
  workflow_id: string;
  status: string;
  stage: string;
  analysis?: Record<string, any>;
  copywriting_versions: CopywritingArtifact[];
  images: ImageArtifact[];
  video?: VideoArtifact;
  qa_report?: Record<string, any>;
}

export interface RegenerateRequest {
  target: 'copywriting' | 'images' | 'video' | 'all';
  reason?: string;
}

export interface RegenerateResponse {
  package_id: string;
  workflow_id: string;
  target: string;
  status: string;
}

export interface ApproveRequest {
  decision: 'approve' | 'reject';
  comment?: string;
}

export interface ApproveResponse {
  package_id: string;
  decision: string;
  status: string;
  comment?: string;
}

/**
 * Product Package Service Class
 */
class ProductPackageService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE}/product-packages`;
  }

  /**
   * Get auth token from localStorage
   */
  private getAuthToken(): string {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No authentication token found');
    }
    return token;
  }

  /**
   * Get axios config with auth headers
   */
  private getConfig() {
    const token = this.getAuthToken();
    return {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    };
  }

  /**
   * Generate a new product package
   */
  async generate(request: ProductPackageRequest): Promise<ProductPackageGenerateResponse> {
    try {
      const response = await axios.post<ProductPackageGenerateResponse>(
        `${this.baseUrl}/generate`,
        request,
        this.getConfig()
      );
      return response.data;
    } catch (error: any) {
      console.error('Failed to generate product package:', error);
      throw new Error(error.response?.data?.detail || 'Failed to generate product package');
    }
  }

  /**
   * Get package status by workflow ID
   */
  async getStatus(workflowId: string): Promise<ProductPackageStatusResponse> {
    try {
      const response = await axios.get<ProductPackageStatusResponse>(
        `${this.baseUrl}/status/${workflowId}`,
        this.getConfig()
      );
      return response.data;
    } catch (error: any) {
      console.error('Failed to get package status:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get package status');
    }
  }

  /**
   * Get package details by package ID
   */
  async getPackage(packageId: string): Promise<ProductPackageResponse> {
    try {
      const response = await axios.get<ProductPackageResponse>(
        `${this.baseUrl}/${packageId}`,
        this.getConfig()
      );
      return response.data;
    } catch (error: any) {
      console.error('Failed to get package details:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get package details');
    }
  }

  /**
   * Regenerate part or all of a package
   */
  async regenerate(packageId: string, request: RegenerateRequest): Promise<RegenerateResponse> {
    try {
      const response = await axios.post<RegenerateResponse>(
        `${this.baseUrl}/${packageId}/regenerate`,
        request,
        this.getConfig()
      );
      return response.data;
    } catch (error: any) {
      console.error('Failed to regenerate package:', error);
      throw new Error(error.response?.data?.detail || 'Failed to regenerate package');
    }
  }

  /**
   * Approve or reject a package
   */
  async approve(packageId: string, request: ApproveRequest): Promise<ApproveResponse> {
    try {
      const response = await axios.post<ApproveResponse>(
        `${this.baseUrl}/${packageId}/approve`,
        request,
        this.getConfig()
      );
      return response.data;
    } catch (error: any) {
      console.error('Failed to process approval:', error);
      throw new Error(error.response?.data?.detail || 'Failed to process approval');
    }
  }
}

// Export singleton instance
export const productPackageService = new ProductPackageService();
