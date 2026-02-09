
import axios from 'axios';

// MEDIUM-001: 使用环境变量配置API URL
const API_URL = import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/auth`
    : 'http://localhost:8000/api/v1/auth';

// MEDIUM-002: 创建带拦截器的axios实例
const apiClient = axios.create({
    baseURL: API_URL
});

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export interface User {
    id: string;
    email: string;
    isActive: boolean;
}

export interface AuthResponse {
    accessToken: string;
    tokenType: string;
}

export interface RegisterResponse {
    message: string;
    user: User;
}

const authService = {
    async login(email: string, password: string): Promise<AuthResponse> {
        const response = await apiClient.post<AuthResponse>('/login', {
            email,
            password,
        });
        if (response.data.accessToken) {
            localStorage.setItem('token', response.data.accessToken);
        }
        return response.data;
    },

    async register(email: string, password: string): Promise<RegisterResponse> {
        const response = await apiClient.post<RegisterResponse>('/signup', {
            email,
            password,
        });
        return response.data;
    },

    logout() {
        localStorage.removeItem('token');
    },

    getCurrentUserToken(): string | null {
        return localStorage.getItem('token');
    },

    // CRITICAL-001: 添加JWT过期验证
    isAuthenticated(): boolean {
        const token = localStorage.getItem('token');
        if (!token) return false;

        try {
            // 解析JWT并检查exp时间戳
            const payload = JSON.parse(atob(token.split('.')[1]));
            const now = Date.now() / 1000;
            return payload.exp > now;
        } catch {
            return false;
        }
    },

    async getCurrentUser(): Promise<User> {
        if (!this.isAuthenticated()) {
            throw new Error('No valid token found');
        }
        // 使用apiClient会自动添加Authorization header
        const response = await apiClient.get<User>('/me');
        return response.data;
    }
};

export default authService;
