import React, { useState } from 'react';
import authService from '../services/authService';
import { handleAuthError } from '../utils/errorHandler';

interface SignupProps {
    onSignIn: () => void;
    onSignUp?: () => void;
}

// 密码强度验证：至少8字符，包含大小写字母和数字
const validatePassword = (password: string): { valid: boolean; message: string } => {
    if (password.length < 8) {
        return { valid: false, message: '密码至少需要8个字符' };
    }
    if (!/[A-Z]/.test(password)) {
        return { valid: false, message: '密码需要包含至少一个大写字母' };
    }
    if (!/[a-z]/.test(password)) {
        return { valid: false, message: '密码需要包含至少一个小写字母' };
    }
    if (!/[0-9]/.test(password)) {
        return { valid: false, message: '密码需要包含至少一个数字' };
    }
    return { valid: true, message: '' };
};

const Signup: React.FC<SignupProps> = ({ onSignIn, onSignUp }) => {
    // CRITICAL-003: 移除未使用的fullName字段
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [termsAccepted, setTermsAccepted] = useState(false); // CRITICAL-002: 跟踪条款接受状态
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [passwordError, setPasswordError] = useState<string | null>(null);

    const handlePasswordChange = (value: string) => {
        setPassword(value);
        if (value) {
            const validation = validatePassword(value);
            setPasswordError(validation.valid ? null : validation.message);
        } else {
            setPasswordError(null);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrorMessage(null);

        // 密码验证
        const passwordValidation = validatePassword(password);
        if (!passwordValidation.valid) {
            setErrorMessage(passwordValidation.message);
            return;
        }

        // 确认密码匹配
        if (password !== confirmPassword) {
            setErrorMessage('两次输入的密码不一致');
            return;
        }

        // CRITICAL-002: 验证服务条款已接受
        if (!termsAccepted) {
            setErrorMessage('请同意服务条款和隐私政策');
            return;
        }

        setIsLoading(true);
        try {
            await authService.register(email, password);
            // 注册成功，导航到登录页面
            onSignIn();
        } catch (error: any) {
            // MEDIUM-003: 使用统一错误处理
            setErrorMessage(handleAuthError(error, 'signup'));
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen w-full flex-row bg-background-light dark:bg-background-dark font-display overflow-hidden text-[#101918] dark:text-white">
            {/* Visual/Hero Side */}
            <div
                className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-[#101918]"
            >
                <div
                    className="absolute inset-0 bg-cover bg-center opacity-80 mix-blend-overlay"
                    style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuA8gZnOiPR-iG_d3F28Yij1r0tLqcheHRKX2AP8yb1LCFUUITN_xEYrZZKO6gVdF2CkwA3zv2YxPAMHaNGlY9NNT7-dkfwuMGWGJbrNKijCI7Am3a2-ev5OPhMJhAXiRbm2Yo_hkLX87ln3Kg3zZ0oCB9eRZaNZZ5nUpid2H2JMdvknXWbqEclkU61NKCAlD08g136qGN_AjiFQ4voIr6wiJmkD6h3JtxVlSn8PmkOENkfDoM1J9srIjE3tYqdOBT3xJTBRdg_4k8FS')" }}
                >
                </div>
                <div className="absolute inset-0 bg-primary/20"></div>
                <div className="relative z-10 flex flex-col justify-between p-16 w-full h-full text-white">
                    <div className="flex items-center gap-3">
                        <div className="size-8 bg-primary rounded-lg flex items-center justify-center text-[#101918]">
                            <span className="material-symbols-outlined font-bold">sailing</span>
                        </div>
                    </div>
                    <div className="max-w-md">
                        <h1 className="text-5xl font-black leading-tight tracking-tight mb-6">
                            Chart Your Course to Success.
                        </h1>
                        <p className="text-lg text-white/80 leading-relaxed">
                            Join thousands of merchants using AI to navigate the complex waters of modern e-commerce. Scale faster, smarter, and with total clarity.
                        </p>
                    </div>
                    <div className="text-sm text-white/60">
                        © 2024 AI E-commerce SaaS. All rights reserved.
                    </div>
                </div>
            </div>

            {/* Form Side */}
            <div className="w-full lg:w-1/2 flex flex-col justify-center items-center bg-white dark:bg-background-dark px-8 py-12 md:px-24">
                <div className="w-full max-w-[440px]">
                    <div className="mb-10 text-center lg:text-left">
                        <h2 className="text-3xl font-black text-[#101918] dark:text-white mb-2">Create Account</h2>
                        <p className="text-[#5b8b86] dark:text-primary/70">Start your 14-day free trial today.</p>
                    </div>
                    <form className="space-y-5" onSubmit={handleSubmit}>
                        {/* CRITICAL-003: 移除fullName字段 */}
                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-semibold text-[#101918] dark:text-white/90">Email Address</label>
                            <div className="relative">
                                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#5b8b86] text-xl">mail</span>
                                <input
                                    className="w-full pl-10 pr-4 py-3 bg-background-light dark:bg-white/5 border border-[#d4e3e1] dark:border-white/10 rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all dark:text-white placeholder:text-[#5b8b86]/60"
                                    placeholder="name@company.com"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-semibold text-[#101918] dark:text-white/90">Password</label>
                                <input
                                    className={`w-full px-4 py-3 bg-background-light dark:bg-white/5 border ${passwordError ? 'border-red-500' : 'border-[#d4e3e1] dark:border-white/10'} rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all dark:text-white placeholder:text-[#5b8b86]/60`}
                                    placeholder="••••••••"
                                    type="password"
                                    value={password}
                                    onChange={(e) => handlePasswordChange(e.target.value)}
                                />
                                {passwordError && <p className="text-xs text-red-500 mt-1">{passwordError}</p>}
                            </div>
                            <div className="flex flex-col gap-2">
                                <label className="text-sm font-semibold text-[#101918] dark:text-white/90">Confirm Password</label>
                                <input
                                    className="w-full px-4 py-3 bg-background-light dark:bg-white/5 border border-[#d4e3e1] dark:border-white/10 rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary outline-none transition-all dark:text-white placeholder:text-[#5b8b86]/60"
                                    placeholder="••••••••"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                />
                            </div>
                        </div>
                        {errorMessage && (
                            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                                <p className="text-sm text-red-600 dark:text-red-400">{errorMessage}</p>
                            </div>
                        )}
                        <div className="flex items-start gap-3 py-2">
                            <input
                                className="mt-1 size-4 rounded border-[#d4e3e1] text-primary focus:ring-primary"
                                id="terms"
                                type="checkbox"
                                checked={termsAccepted}
                                onChange={(e) => setTermsAccepted(e.target.checked)}
                            />
                            <label className="text-sm text-[#5b8b86] dark:text-white/60 leading-tight" htmlFor="terms">
                                I agree to the <a className="text-[#101918] dark:text-primary font-semibold hover:underline" href="#">Terms of Service</a> and <a className="text-[#101918] dark:text-primary font-semibold hover:underline" href="#">Privacy Policy</a>.
                            </label>
                        </div>
                        <button
                            className="w-full bg-primary hover:bg-primary/90 text-[#101918] font-bold py-4 rounded-lg transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            type="submit"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <span className="animate-spin material-symbols-outlined">progress_activity</span>
                                    Creating...
                                </>
                            ) : (
                                <>
                                    Create Account
                                    <span className="material-symbols-outlined">arrow_forward</span>
                                </>
                            )}
                        </button>
                    </form>
                    <div className="flex items-center gap-4 my-8">
                        <div className="flex-1 h-px bg-[#d4e3e1] dark:bg-white/10"></div>
                        <span className="text-xs font-bold text-[#5b8b86] uppercase tracking-wider">Or sign up with</span>
                        <div className="flex-1 h-px bg-[#d4e3e1] dark:bg-white/10"></div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <button className="flex items-center justify-center gap-2 py-3 px-4 border border-[#d4e3e1] dark:border-white/10 rounded-lg hover:bg-background-light dark:hover:bg-white/5 transition-all">
                            <svg className="size-5" viewBox="0 0 24 24">
                                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"></path>
                                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                            </svg>
                            <span className="text-sm font-semibold">Google</span>
                        </button>
                        <button className="flex items-center justify-center gap-2 py-3 px-4 border border-[#d4e3e1] dark:border-white/10 rounded-lg hover:bg-background-light dark:hover:bg-white/5 transition-all">
                            <svg className="size-5" fill="#07C160" viewBox="0 0 24 24">
                                <path d="M12 2C6.477 2 2 6.477 2 12c0 1.891.524 3.662 1.435 5.176L2 22l4.966-1.391c1.474.84 3.193 1.328 5.034 1.328 5.523 0 10-4.477 10-10S17.523 2 12 2zm3.896 11.235c-.179-.1-.652-.322-.754-.358-.103-.036-.179-.054-.255.054-.076.107-.295.358-.362.434-.067.076-.134.085-.313-.013-.179-.1-.758-.279-1.444-.88-.533-.473-.893-1.057-1.01-1.25-.117-.193-.012-.297.083-.393.085-.087.179-.208.268-.313.089-.104.119-.176.179-.292.06-.117.03-.22-.015-.313-.045-.093-.402-.969-.554-1.336-.145-.353-.29-.304-.402-.313-.103-.005-.221-.005-.339-.005-.118 0-.311.044-.474.22-.163.176-.621.603-.621 1.471 0 .867.636 1.706.725 1.825.089.12 1.25 1.91 3.03 2.68.423.183.754.292 1.012.373.424.135.811.116 1.116.071.341-.05 1.046-.427 1.192-.839.146-.411.146-.763.102-.839-.044-.076-.16-.12-.339-.219z"></path>
                            </svg>
                            <span className="text-sm font-semibold">WeChat</span>
                        </button>
                    </div>
                    <div className="mt-10 text-center">
                        <p className="text-[#5b8b86] dark:text-white/60">
                            Already have an account?
                            <button onClick={onSignIn} className="text-primary font-bold hover:underline ml-1">Sign In</button>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Signup;
