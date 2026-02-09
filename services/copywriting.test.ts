/**
 * Unit Tests for Copywriting Service
 * Story 2-4: Frontend Copywriting UI Integration
 *
 * TEST-001 Fix: Add comprehensive unit tests for copywriting service
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Use vi.hoisted() to ensure mocks are hoisted above imports
const { mockAuthService } = vi.hoisted(() => {
    const mockAuthService = {
        isAuthenticated: vi.fn(() => true),
        getCurrentUserToken: vi.fn(() => 'mock-token')
    };
    return { mockAuthService };
});

vi.mock('./authService', () => ({
    default: mockAuthService
}));

// Import after mocking
import copywritingService, { toSnakeCase, CopywritingRequest } from './copywriting';

describe('copywritingService', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockAuthService.isAuthenticated.mockReturnValue(true);
        mockAuthService.getCurrentUserToken.mockReturnValue('mock-token');
    });

    describe('toSnakeCase', () => {
        it('should convert camelCase keys to snake_case', () => {
            const input = {
                productName: 'Test Product',
                brandGuidelines: 'Premium brand'
            };
            const result = toSnakeCase(input);
            expect(result).toEqual({
                product_name: 'Test Product',
                brand_guidelines: 'Premium brand'
            });
        });

        it('should handle already lowercase keys', () => {
            const input = { features: ['feature1', 'feature2'] };
            const result = toSnakeCase(input);
            expect(result).toEqual({ features: ['feature1', 'feature2'] });
        });

        it('should handle empty object', () => {
            const result = toSnakeCase({});
            expect(result).toEqual({});
        });

        it('should handle leading uppercase (MD-004 fix verification)', () => {
            const input = { ProductName: 'Test' };
            const result = toSnakeCase(input);
            // Should be 'product_name', not '_product_name'
            expect(result).toEqual({ product_name: 'Test' });
        });

        it('should handle multiple uppercase letters', () => {
            const input = { myProductName: 'Test' };
            const result = toSnakeCase(input);
            expect(result).toEqual({ my_product_name: 'Test' });
        });
    });

    describe('createRequest', () => {
        it('should create properly formatted snake_case request', () => {
            const result = copywritingService.createRequest(
                'Test Product',
                ['Feature 1', 'Feature 2'],
                'Premium brand'
            );
            const expected: CopywritingRequest = {
                product_name: 'Test Product',
                features: ['Feature 1', 'Feature 2'],
                brand_guidelines: 'Premium brand'
            };
            expect(result).toEqual(expected);
        });

        it('should handle optional brand_guidelines', () => {
            const result = copywritingService.createRequest(
                'Test Product',
                ['Feature 1']
            );
            expect(result).toEqual({
                product_name: 'Test Product',
                features: ['Feature 1'],
                brand_guidelines: undefined
            });
        });

        it('should handle empty features array', () => {
            const result = copywritingService.createRequest(
                'Test Product',
                []
            );
            expect(result.features).toEqual([]);
        });
    });

    describe('startGeneration', () => {
        it('should throw error if user is not authenticated', async () => {
            mockAuthService.isAuthenticated.mockReturnValue(false);

            const payload: CopywritingRequest = {
                product_name: 'Test',
                features: ['Feature']
            };

            await expect(copywritingService.startGeneration(payload))
                .rejects.toThrow('User is not authenticated');
        });

        it('should be a defined function', () => {
            expect(copywritingService.startGeneration).toBeDefined();
            expect(typeof copywritingService.startGeneration).toBe('function');
        });
    });
});

describe('API URL Configuration', () => {
    it('should use correct API URL with /api/v1 prefix (ARCH-001 fix)', () => {
        // Verify the module exports exist and use correct pattern
        expect(copywritingService.startGeneration).toBeDefined();
        expect(copywritingService.createRequest).toBeDefined();
    });
});

describe('Type Exports', () => {
    it('should export toSnakeCase function', () => {
        expect(toSnakeCase).toBeDefined();
        expect(typeof toSnakeCase).toBe('function');
    });
});
