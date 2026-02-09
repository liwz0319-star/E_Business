/**
 * Copywriting Service
 * Story 2-4: Frontend Copywriting UI Integration
 * 
 * Follows the same pattern as authService.ts for API client configuration
 */
import axios, { AxiosError } from 'axios';
import authService from './authService';

// Use environment variable with fallback (same pattern as authService)
// ARCH-001 Fix: Unified URL pattern - always include /api/v1 prefix
const API_URL = import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api/v1/copywriting`
    : 'http://localhost:8000/api/v1/copywriting';

// Create axios instance with base URL
const apiClient = axios.create({
    baseURL: API_URL
});

// Request interceptor to add Bearer token (same pattern as authService)
apiClient.interceptors.request.use((config) => {
    const token = authService.getCurrentUserToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// =====================
// Type Definitions
// =====================

/**
 * Request payload for copywriting generation
 * CRITICAL: Must use snake_case to match backend DTO
 */
export interface CopywritingRequest {
    product_name: string;         // NOT productName
    features: string[];           // Array of product features
    brand_guidelines?: string;    // NOT brandGuidelines
}

/**
 * Raw API response. Backend may return either camelCase or snake_case.
 */
interface CopywritingApiResponse {
    workflowId?: string;
    workflow_id?: string;
    status: string;
    message: string;
}

/**
 * Normalized response used by frontend code.
 */
export interface CopywritingResponse {
    workflowId: string;
    status: string;
    message: string;
}

/**
 * Error response structure
 */
export interface CopywritingError {
    code: string;
    message: string;
    details?: unknown;
}

// =====================
// Helper Functions
// =====================

/**
 * Convert camelCase object keys to snake_case
 * Ensures frontend objects match backend DTO format
 * MD-004: Fixed leading uppercase bug (ProductName -> product_name, not _product_name)
 */
export const toSnakeCase = (obj: Record<string, unknown>): Record<string, unknown> => {
    return Object.keys(obj).reduce((acc, key) => {
        // Fix: Skip leading underscores for first character uppercase
        let snakeKey = key.charAt(0).toLowerCase() + key.slice(1);
        snakeKey = snakeKey.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
        acc[snakeKey] = obj[key];
        return acc;
    }, {} as Record<string, unknown>);
};

// =====================
// Service Methods
// =====================

const copywritingService = {
    /**
     * Start copywriting generation workflow
     * Calls POST /api/v1/copywriting/generate
     * 
     * @param payload - The copywriting request payload (already in snake_case)
     * @returns Promise with workflowId for tracking
     */
    async startGeneration(payload: CopywritingRequest): Promise<CopywritingResponse> {
        // Verify user is authenticated before making request
        if (!authService.isAuthenticated()) {
            throw new Error('User is not authenticated. Please login first.');
        }

        try {
            const response = await apiClient.post<CopywritingApiResponse>('/generate', payload);
            const workflowId = response.data.workflowId || response.data.workflow_id;
            if (!workflowId) {
                throw new Error('Invalid backend response: missing workflowId');
            }

            return {
                workflowId,
                status: response.data.status,
                message: response.data.message,
            };
        } catch (error) {
            if (error instanceof AxiosError) {
                const errorData = error.response?.data as CopywritingError | undefined;
                throw new Error(
                    errorData?.message ||
                    `Failed to start generation: ${error.message}`
                );
            }
            throw error;
        }
    },

    /**
     * Helper to create a properly formatted request from frontend form data
     * Converts camelCase form fields to snake_case API format
     */
    createRequest(
        productName: string,
        features: string[],
        brandGuidelines?: string
    ): CopywritingRequest {
        return {
            product_name: productName,
            features: features,
            brand_guidelines: brandGuidelines
        };
    }
};

export default copywritingService;
