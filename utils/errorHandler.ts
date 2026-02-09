// utils/errorHandler.ts
// MEDIUM-003: 统一错误处理函数

export interface AuthErrorMessages {
    [key: number]: string;
}

const defaultMessages: AuthErrorMessages = {
    400: '请求格式错误或数据已存在',
    401: '邮箱或密码错误',
    422: '密码强度不足或数据验证失败',
    500: '服务器错误，请稍后重试'
};

export const handleAuthError = (error: any, context: 'login' | 'signup' = 'login'): string => {
    if (!error.response) {
        return '网络错误，请检查网络连接';
    }

    const status = error.response.status;

    // 根据上下文提供更具体的错误消息
    if (context === 'signup') {
        if (status === 400) return '该邮箱已注册';
        if (status === 422) return '密码强度不足';
    } else if (context === 'login') {
        if (status === 401) return '邮箱或密码错误';
        if (status === 422) return '请求格式错误';
    }

    return defaultMessages[status] || error.response.data?.detail || '操作失败，请重试';
};
