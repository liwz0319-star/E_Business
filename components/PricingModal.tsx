
import React, { useState } from 'react';

interface PricingModalProps {
  onClose: () => void;
}

const PricingModal: React.FC<PricingModalProps> = ({ onClose }) => {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('yearly');

  const handlePlanSelection = (plan: string) => {
    alert(`Redirecting to payment for the ${plan} plan (${billingCycle})...`);
  };

  return (
    <div className="fixed inset-0 z-[100] bg-[#101918]/60 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-hidden font-manrope">
      {/* Backdrop for closing */}
      <div className="absolute inset-0" onClick={onClose}></div>

      {/* Modal Container */}
      <div className="relative w-full max-w-6xl bg-white dark:bg-[#1e2827] rounded-2xl shadow-2xl flex flex-col max-h-[95vh] overflow-y-auto sidebar-scroll animate-fade-in-up transition-all duration-300">
        
        {/* Close Button */}
        <div className="absolute top-4 right-4 z-30">
          <button 
            onClick={onClose}
            className="group flex h-10 w-10 cursor-pointer items-center justify-center rounded-full bg-white/40 hover:bg-white/60 dark:bg-black/20 dark:hover:bg-black/40 backdrop-blur-sm text-text-main transition-all duration-200 active:scale-90"
          >
            <span className="material-symbols-outlined text-gray-600 dark:text-white group-hover:scale-110 transition-transform">close</span>
          </button>
        </div>

        {/* Modal Header Section */}
        <div className="relative bg-gradient-to-br from-primary/10 to-primary/30 px-6 py-12 sm:px-10 sm:py-16 text-center shrink-0">
          {/* Decorative background elements */}
          <div className="absolute top-0 left-0 w-full h-full overflow-hidden opacity-30 pointer-events-none">
            <div className="absolute -top-24 -left-24 w-64 h-64 bg-primary rounded-full blur-3xl"></div>
            <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-primary rounded-full blur-3xl"></div>
          </div>
          
          <h2 className="relative text-[#101918] dark:text-white text-2xl sm:text-3xl md:text-5xl font-extrabold leading-tight tracking-tight mb-4 px-4">
            Unlock Your Creative Potential
          </h2>
          <p className="relative text-[#101918]/70 dark:text-white/70 text-sm sm:text-base md:text-xl max-w-2xl mx-auto font-medium px-4">
            Generate unlimited AI product photos, high-converting copy, and cinematic 4K videos. Scale your business faster.
          </p>

          {/* Toggle Switch */}
          <div className="relative mt-10 flex justify-center">
            <div className="bg-white/60 dark:bg-black/20 backdrop-blur-sm p-1.5 rounded-2xl border border-white/40 inline-flex shadow-sm">
              <label className="cursor-pointer">
                <input 
                  className="peer sr-only" 
                  name="billing" 
                  type="radio" 
                  checked={billingCycle === 'monthly'}
                  onChange={() => setBillingCycle('monthly')}
                />
                <span className="block px-6 sm:px-8 py-2.5 rounded-xl text-xs sm:text-sm font-black text-gray-500 transition-all peer-checked:bg-white peer-checked:text-[#101918] peer-checked:shadow-md dark:peer-checked:bg-[#2c3635] dark:peer-checked:text-primary">
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
                <span className="block px-6 sm:px-8 py-2.5 rounded-xl text-xs sm:text-sm font-black text-gray-500 transition-all peer-checked:bg-white peer-checked:text-[#101918] peer-checked:shadow-md dark:peer-checked:bg-[#2c3635] dark:peer-checked:text-primary">
                  Yearly <span className="text-green-600 text-[10px] ml-1 font-black uppercase tracking-wider">-20%</span>
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Pricing Cards Content */}
        <div className="px-5 py-10 sm:px-10 sm:py-16 bg-[#fbfdfd] dark:bg-[#1e2827]">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-8 items-stretch max-w-5xl mx-auto">
            
            {/* Free Plan */}
            <div className="flex flex-col gap-6 rounded-3xl border border-gray-200 bg-white dark:bg-[#252f2e] dark:border-gray-700 p-8 shadow-sm hover:shadow-xl transition-all duration-300">
              <div className="flex flex-col gap-1">
                <h3 className="text-[#101918] dark:text-white text-2xl font-black tracking-tight">Free</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Perfect for trying out our tools.</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-[#101918] dark:text-white text-4xl font-black tracking-tight">$0</span>
                  <span className="text-gray-500 dark:text-gray-400 font-bold">/mo</span>
                </div>
              </div>
              <button 
                onClick={() => alert("You are already on the Free plan.")}
                className="w-full h-14 rounded-2xl border border-gray-200 bg-gray-50 dark:bg-transparent dark:border-gray-600 dark:text-white text-[#101918] font-black text-sm transition-all cursor-default"
              >
                Current Plan
              </button>
              <div className="space-y-4 pt-4 border-t border-gray-50 dark:border-gray-800">
                {[
                  { text: '5 AI Generations/mo', included: true },
                  { text: 'Standard Quality (720p)', included: true },
                  { text: 'Community Support', included: true },
                  { text: 'No Watermark', included: false },
                ].map((feature, i) => (
                  <div key={i} className={`flex items-start gap-3 text-sm font-medium ${feature.included ? 'text-gray-600 dark:text-gray-300' : 'text-gray-300 dark:text-gray-600 line-through'}`}>
                    <span className={`material-symbols-outlined text-[20px] font-bold ${feature.included ? 'text-primary' : ''}`}>
                      {feature.included ? 'check_circle' : 'cancel'}
                    </span>
                    {feature.text}
                  </div>
                ))}
              </div>
            </div>

            {/* Pro Plan (Highlighted) */}
            <div className="relative flex flex-col gap-6 rounded-3xl border-[3px] border-primary bg-white dark:bg-[#252f2e] p-8 shadow-glow transition-all duration-300 hover:shadow-2xl lg:-translate-y-6 lg:scale-105 z-10">
              {/* Badge */}
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-[#101918] text-[10px] font-black px-5 py-2 rounded-full shadow-lg uppercase tracking-widest whitespace-nowrap">
                Most Popular
              </div>
              <div className="flex flex-col gap-1 pt-2">
                <h3 className="text-[#101918] dark:text-white text-2xl font-black tracking-tight flex items-center gap-2">
                  Pro
                  <span className="material-symbols-outlined text-primary text-[24px] font-fill-1">verified</span>
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">For growing brands & creators.</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-[#101918] dark:text-white text-5xl font-black tracking-tight">
                    ${billingCycle === 'yearly' ? '49' : '59'}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400 font-bold">/mo</span>
                </div>
                {billingCycle === 'yearly' && (
                  <p className="text-xs text-primary-dark font-black mt-2 bg-primary/10 inline-block self-start px-2 py-0.5 rounded">Billed $588 yearly</p>
                )}
              </div>
              <button 
                onClick={() => handlePlanSelection('Pro')}
                className="w-full h-14 rounded-2xl bg-primary hover:bg-teal-400 text-slate-900 font-black text-base shadow-xl shadow-primary/20 transition-all transform hover:-translate-y-0.5 active:translate-y-0 active:scale-95"
              >
                Upgrade Now
              </button>
              <div className="space-y-4 pt-4 border-t border-gray-50 dark:border-gray-800">
                {[
                  'Unlimited AI Generations',
                  '4K Video Export',
                  'Priority Processing (Fast)',
                  'No Watermark',
                  'Advanced Image Editing'
                ].map((feature, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm font-black text-[#101918] dark:text-white">
                    <span className="material-symbols-outlined text-primary text-[20px] font-bold">check_circle</span>
                    {feature}
                  </div>
                ))}
              </div>
            </div>

            {/* Enterprise Plan */}
            <div className="flex flex-col gap-6 rounded-3xl border border-gray-200 bg-white dark:bg-[#252f2e] dark:border-gray-700 p-8 shadow-sm hover:shadow-xl transition-all duration-300 md:col-span-2 lg:col-span-1">
              <div className="flex flex-col gap-1">
                <h3 className="text-[#101918] dark:text-white text-2xl font-black tracking-tight">Enterprise</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">For large teams & agencies.</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="text-[#101918] dark:text-white text-4xl font-black tracking-tight">Custom</span>
                </div>
              </div>
              <button 
                onClick={() => alert("Connecting to sales team...")}
                className="w-full h-14 rounded-2xl border-2 border-gray-100 bg-white hover:bg-gray-50 dark:bg-transparent dark:border-gray-700 dark:text-white dark:hover:bg-gray-800 text-[#101918] font-black text-sm transition-all hover:shadow-md active:scale-95"
              >
                Contact Sales
              </button>
              <div className="space-y-4 pt-4 border-t border-gray-50 dark:border-gray-800">
                {[
                  'Everything in Pro',
                  'API Access',
                  'Dedicated Success Manager',
                  'SSO & Advanced Security',
                  'Custom AI Models'
                ].map((feature, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm font-medium text-gray-600 dark:text-gray-300">
                    <span className="material-symbols-outlined text-primary text-[20px] font-bold">check_circle</span>
                    {feature}
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>

        {/* Footer Meta Text */}
        <div className="bg-gray-50 dark:bg-[#192221] px-6 py-8 sm:px-10 flex flex-col md:flex-row items-center justify-between gap-6 border-t border-gray-100 dark:border-gray-800 shrink-0">
          <div className="flex items-center gap-3 text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">
            <span className="material-symbols-outlined text-[20px]">lock</span>
            Secure SSL Payment
          </div>
          <p className="text-text-muted dark:text-gray-400 text-sm font-bold text-center">
            Cancel anytime. 14-day money-back guarantee.
          </p>
          <div className="flex items-center gap-4 opacity-40 grayscale group hover:grayscale-0 transition-all duration-500">
            <div className="h-8 w-12 bg-gray-300 dark:bg-gray-600 rounded-lg flex items-center justify-center font-black text-[10px] text-white">VISA</div>
            <div className="h-8 w-12 bg-gray-300 dark:bg-gray-600 rounded-lg flex items-center justify-center font-black text-[10px] text-white">MC</div>
            <div className="h-8 w-12 bg-gray-300 dark:bg-gray-600 rounded-lg flex items-center justify-center font-black text-[10px] text-white">APPLE</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingModal;
