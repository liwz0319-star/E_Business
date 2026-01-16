
import React from 'react';

const Hero: React.FC = () => {
  return (
    <div className="space-y-6 max-w-3xl mx-auto px-4">
      <div className="flex justify-center">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-primary to-secondary rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative w-20 h-20 rounded-2xl bg-white dark:bg-slate-800 shadow-xl border border-slate-100 dark:border-slate-700 flex items-center justify-center transform rotate-3 hover:rotate-0 transition-transform">
            <span className="material-icons-round text-5xl text-transparent bg-clip-text bg-gradient-to-br from-primary to-teal-500">auto_fix_high</span>
          </div>
        </div>
      </div>
      <div className="space-y-4">
        <h2 className="text-4xl md:text-6xl font-black text-slate-900 dark:text-white tracking-tight leading-[1.1]">
          The future of <br/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-teal-400 to-cyan-500">E-commerce Creative</span>
        </h2>
        <p className="text-xl text-slate-500 dark:text-slate-400 max-w-xl mx-auto font-medium">
          Generate stunning product photography, high-converting copy, and viral ad videos using the power of Gemini.
        </p>
      </div>
    </div>
  );
};

export default Hero;
