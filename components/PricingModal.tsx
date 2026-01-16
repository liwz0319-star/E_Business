
import React, { useState } from 'react';

interface PricingModalProps {
  onClose: () => void;
}

const PricingModal: React.FC<PricingModalProps> = ({ onClose }) => {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('yearly');

  return (
    <div className="fixed inset-0 z-[100] bg-[#101918]/60 glass-blur flex items-center justify-center p-4 sm:p-6 overflow-y-auto font-manrope">
      {/* Modal Container */}
      <div className="relative w-full max-w-5xl bg-white dark:bg-[#1e2827] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-fade-in-up">
        
        {/* Close Button */}
        <div className="absolute top-4 right-4 z-20">
          <button 
            onClick={onClose}
            className="group flex h-10 w-10 cursor-pointer items-center justify-center rounded-full bg-white/20 hover:bg-white/40 backdrop-blur-sm text-text-main transition-colors duration-200"
          >
            <span className="material-symbols-outlined text-gray-600 dark:text-white group-hover:scale-110 transition-transform">close</span>
          </button>
        </div>

        {/* Modal Header Section */}
        <div className="relative bg-gradient-to-br from-primary/10 to-primary/30 px-6 py-10 sm:px-10 text-center">
          {/* Decorative background elements */}
          <div className="absolute top-0 left-0 w-full h-full overflow-hidden opacity-30 pointer-events-none">
            <div className="absolute -top-24 -left-24 w-64 h-64 bg-primary rounded-full blur-3xl"></div>
            <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-primary rounded-full blur-3xl"></div>
          </div>
          <h2 className="relative text-[#101918] dark:text-white text-3xl sm:text-4xl font-extrabold leading-tight tracking-tight mb-3">
            Unlock Your Creative Potential
          </h2>
          <p className="relative text-[#101918]/70 dark:text-white/70 text-base sm:text-lg max-w-2xl mx-auto font-medium">
            Generate unlimited AI product photos, copy, and 4K videos. Scale your e-commerce business faster.
          </p>

          {/* Toggle Switch */}
          <div className="relative mt-8 flex justify-center">
            <div className="bg-white/50 dark:bg-black/20 backdrop-blur-sm p-1.5 rounded-xl border border-white/40 inline-flex">
              <label className="cursor-pointer">
                <input 
                  className="peer sr-only" 
                  name="billing" 
                  type="radio" 
                  checked={billingCycle === 'monthly'}
                  onChange={() => setBillingCycle('monthly')}
                />
                <span className="block px-6 py-2 rounded-lg text-sm font-bold text-gray-500 transition-all peer-checked:bg-white peer-checked:text-[#101918] peer-checked:shadow-sm dark:peer-checked:bg-[#2c3635] dark:peer-checked:text-primary">
                  Monthly
                </span>
              </label>
              <label className="cursor-pointer">
                <input 
                  className="peer sr-only" 
                  name="billing" 
                  type="radio" 
                  checked={billingCycle === 'yearly'}
                  onChange={() => setBillingCycle('yearly')}
                />
                <span className="block px-6 py-2 rounded-lg text-sm font-bold text-gray-500 transition-all peer-checked:bg-white peer-checked:text-[#101918] peer-checked:shadow-sm dark:peer-checked:bg-[#2c3635] dark:peer-checked:text-primary">
                  Yearly <span className="text-green-600 text-xs ml-1 font-extrabold">-20%</span>
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Pricing Cards Content */}
        <div className="px-6 py-8 sm:px-10 bg-[#fbfdfd] dark:bg-[#1e2827]">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 items-start">
            {/* Free Plan */}
            <div className="flex flex-col gap-5 rounded-2xl border border-gray-200 bg-white dark:bg-[#252f2e] dark:border-gray-700 p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex flex-col gap-1">
                <h3 className="text-[#101918] dark:text-white text-xl font-bold">Free</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Perfect for trying out our tools.</p>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-[#101918] dark:text-white text-4xl font-black tracking-tight">$0</span>
                  <span className="text-gray-500 dark:text-gray-400 font-medium">/mo</span>
                </div>
              </div>
              <button className="w-full h-12 rounded-xl border border-gray-200 bg-gray-50 hover:bg-gray-100 dark:bg-transparent dark:border-gray-600 dark:text-white dark:hover:bg-gray-800 text-[#101918] font-bold text-sm transition-colors">
                Current Plan
              </button>
              <div className="space-y-3 pt-2">
                <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <span className="material-symbols-outlined text-gray-400 text-[20px]">check</span>
                  5 AI Generations/mo
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <span className="material-symbols-outlined text-gray-400 text-[20px]">check</span>
                  Standard Quality (720p)
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <span className="material-symbols-outlined text-gray-400 text-[20px]">check</span>
                  Community Support
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-400 dark:text-gray-600 line-through decoration-gray-400">
                  <span className="material-symbols-outlined text-[20px]">close</span>
                  No Watermark
                </div>
              </div>
            </div>

            {/* Pro Plan (Highlighted) */}
            <div className="relative flex flex-col gap-6 rounded-2xl border-[3px] border-primary bg-white dark:bg-[#252f2e] p-6 shadow-glow transform md:-translate-y-4 z-10">
              {/* Badge */}
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-[#101918] text-xs font-bold px-4 py-1.5 rounded-full shadow-sm uppercase tracking-wider">
                Most Popular
              </div>
              <div className="flex flex-col gap-1 pt-2">
                <h3 className="text-[#101918] dark:text-white text-xl font-bold flex items-center gap-2">
                  Pro
                  <span className="material-symbols-outlined text-primary text-[24px] font-fill-1">verified</span>
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">For growing brands & creators.</p>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-[#101918] dark:text-white text-5xl font-black tracking-tight">
                    ${billingCycle === 'yearly' ? '49' : '59'}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400 font-medium">/mo</span>
                </div>
                {billingCycle === 'yearly' && (
                  <p className="text-xs text-primary-dark font-medium mt-1">Billed $588 yearly</p>
                )}
              </div>
              <button className="w-full h-12 rounded-xl bg-primary hover:bg-primary-dark text-[#101918] font-bold text-base shadow-md hover:shadow-lg transition-all transform hover:-translate-y-0.5">
                Upgrade Now
              </button>
              <div className="space-y-3 pt-2">
                <div className="flex items-start gap-3 text-sm font-medium text-[#101918] dark:text-white">
                  <span className="material-symbols-outlined text-primary text-[20px] font-bold">check_circle</span>
                  Unlimited AI Generations
                </div>
                <div className="flex items-start gap-3 text-sm font-medium text-[#101918] dark:text-white">
                  <span className="material-symbols-outlined text-primary text-[20px] font-bold">check_circle</span>
                  4K Video Export
                </div>
                <div className="flex items-start gap-3 text-sm font-medium text-[#101918] dark:text-white">
                  <span className="material-symbols-outlined text-primary text-[20px] font-bold">check_circle</span>
                  Priority Processing (Fast)
                </div>
                <div className="flex items-start gap-3 text-sm font-medium text-[#101918] dark:text-white">
                  <span className="material-symbols-outlined text-primary text-[20px] font-bold">check_circle</span>
                  No Watermark
                </div>
                <div className="flex items-start gap-3 text-sm font-medium text-[#101918] dark:text-white">
                  <span className="material-symbols-outlined text-primary text-[20px] font-bold">check_circle</span>
                  Advanced Image Editing
                </div>
              </div>
            </div>

            {/* Enterprise Plan */}
            <div className="flex flex-col gap-5 rounded-2xl border border-gray-200 bg-white dark:bg-[#252f2e] dark:border-gray-700 p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex flex-col gap-1">
                <h3 className="text-[#101918] dark:text-white text-xl font-bold">Enterprise</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">For large teams & agencies.</p>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-[#101918] dark:text-white text-4xl font-black tracking-tight">Custom</span>
                </div>
              </div>
              <button className="w-full h-12 rounded-xl border border-gray-200 bg-gray-50 hover:bg-gray-100 dark:bg-transparent dark:border-gray-600 dark:text-white dark:hover:bg-gray-800 text-[#101918] font-bold text-sm transition-colors">
                Contact Sales
              </button>
              <div className="space-y-3 pt-2">
                <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <span className="material-symbols-outlined text-primary text-[20px]">check</span>
                  Everything in Pro
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <span className="material-symbols-outlined text-primary text-[20px]">check</span>
                  API Access
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <span className="material-symbols-outlined text-primary text-[20px]">check</span>
                  Dedicated Success Manager
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <span className="material-symbols-outlined text-primary text-[20px]">check</span>
                  SSO & Advanced Security
                </div>
                <div className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-300">
                  <span className="material-symbols-outlined text-primary text-[20px]">check</span>
                  Custom AI Models
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Meta Text */}
        <div className="bg-gray-50 dark:bg-[#192221] px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4 border-t border-gray-100 dark:border-gray-800">
          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <span className="material-symbols-outlined text-[16px]">lock</span>
            Secure SSL Payment
          </div>
          <p className="text-text-muted text-sm font-medium text-center">
            Cancel anytime. 14-day money-back guarantee.
          </p>
          <div className="flex items-center gap-3 opacity-60 grayscale">
            <div className="h-6 w-10 bg-gray-300 dark:bg-gray-600 rounded"></div>
            <div className="h-6 w-10 bg-gray-300 dark:bg-gray-600 rounded"></div>
            <div className="h-6 w-10 bg-gray-300 dark:bg-gray-600 rounded"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingModal;
