
import React, { useState, useEffect } from 'react';
import { GenerationType } from '../services/geminiService';

interface GeminiResultProps {
  isGenerating: boolean;
  pendingType: GenerationType | null;
  result: { type: GenerationType; content: string | string[]; title?: string } | null;
  userMessage: string | null;
  onReset: () => void;
  onImageClick?: (content: string) => void;
}

const reassuringMessages = [
  "Sarah is crafting your cinematic product reveal...",
  "Applying high-end visual effects and transitions...",
  "Optimizing the render for vertical social platforms...",
  "Finalizing the lighting and color grading...",
  "Almost there! Preparing your ad for download...",
  "Adding the finishing touches to your video..."
];

const GeminiResult: React.FC<GeminiResultProps> = ({ isGenerating, pendingType, result, userMessage, onReset, onImageClick }) => {
  const currentType = result?.type || pendingType || GenerationType.TEXT;
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    let interval: any;
    if (isGenerating && currentType === GenerationType.VIDEO) {
      interval = setInterval(() => {
        setMessageIndex((prev) => (prev + 1) % reassuringMessages.length);
      }, 5000);
    } else {
      setMessageIndex(0);
    }
    return () => clearInterval(interval);
  }, [isGenerating, currentType]);

  return (
    <div className="w-full max-w-3xl flex flex-col gap-6 animate-fade-in-up mt-8">
      {/* User Message Bubble */}
      {userMessage && (
        <div className="flex justify-end">
          <div className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm text-sm font-medium max-w-[85%] border border-slate-200/50 dark:border-slate-700/50">
            {userMessage}
          </div>
        </div>
      )}

      {/* AI Response Area */}
      <div className="flex gap-4">
        {/* AI Avatar */}
        <div className="relative shrink-0 mt-1">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-slate-900 shadow-lg shadow-primary/20 border border-white dark:border-slate-800">
            <span className="material-symbols-outlined text-[24px]">auto_awesome</span>
          </div>
          {isGenerating && (
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 border-2 border-white dark:border-slate-900 rounded-full animate-pulse"></div>
          )}
        </div>

        {/* AI Content / Loading */}
        <div className="flex-1 min-w-0">
          {isGenerating ? (
            <div className="pt-2">
              <div className="flex items-center gap-3 text-primary font-bold text-sm tracking-tight">
                <span>{currentType === GenerationType.VIDEO ? reassuringMessages[messageIndex] : `Sarah is generating your ${currentType}...`}</span>
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
              <div className="mt-4 space-y-3 bg-white dark:bg-surface-dark border border-slate-100 dark:border-slate-700 rounded-2xl rounded-tl-sm shadow-soft p-6">
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded w-3/4 animate-pulse"></div>
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded w-1/2 animate-pulse"></div>
                <div className="h-48 bg-slate-50 dark:bg-slate-800/50 rounded-xl w-full animate-pulse mt-4 flex items-center justify-center">
                   <span className="material-icons-round text-slate-200 dark:text-slate-700 text-6xl">
                      {currentType === GenerationType.IMAGE ? 'image' : currentType === GenerationType.VIDEO ? 'videocam' : 'description'}
                   </span>
                </div>
                {currentType === GenerationType.VIDEO && (
                  <p className="text-[10px] text-center text-slate-400 font-bold uppercase tracking-widest mt-2">Video generation takes about 1-2 minutes</p>
                )}
              </div>
            </div>
          ) : result ? (
            <div className="bg-white dark:bg-surface-dark border border-slate-100 dark:border-slate-700 rounded-2xl rounded-tl-sm shadow-soft p-6 transition-all group/card">
              <div className="flex justify-between items-start mb-4 pb-4 border-b border-slate-50 dark:border-slate-700/50">
                <div>
                  <h3 className="font-bold text-lg text-slate-900 dark:text-white mb-1">
                    {result.title || (result.type === GenerationType.IMAGE ? "Product Visual" : result.type === GenerationType.VIDEO ? "Marketing Ad" : "Copy Draft")}
                  </h3>
                  <div className="flex gap-2">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-teal-50 text-teal-700 dark:bg-teal-900/20 dark:text-teal-300">
                      <span className="w-1 h-1 rounded-full bg-teal-500 mr-1.5"></span>
                      {result.type} Generated
                    </span>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                      {result.type === GenerationType.IMAGE ? 'Photorealistic' : result.type === GenerationType.VIDEO ? 'Cinematic' : 'Concise Style'}
                    </span>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button className="p-1.5 text-slate-400 hover:text-primary hover:bg-slate-50 dark:hover:bg-slate-800 rounded transition-colors" title="Copy" onClick={() => alert("Link copied!")}>
                    <span className="material-icons-round text-sm">content_copy</span>
                  </button>
                  <button className="p-1.5 text-slate-400 hover:text-primary hover:bg-slate-50 dark:hover:bg-slate-800 rounded transition-colors" title="Regenerate" onClick={onReset}>
                    <span className="material-icons-round text-sm">refresh</span>
                  </button>
                </div>
              </div>

              <div className="overflow-auto max-h-[70vh] sidebar-scroll pr-2">
                {result.type === GenerationType.IMAGE && typeof result.content === 'string' ? (
                  <div className="flex flex-col gap-6">
                    <div className="relative rounded-xl overflow-hidden shadow-lg border border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 flex items-center justify-center min-h-[300px]">
                      <img 
                        src={result.content} 
                        alt="Generated Asset" 
                        className="max-w-full h-auto cursor-pointer hover:scale-[1.02] transition-transform duration-500" 
                        onClick={() => onImageClick?.(result.content as string)}
                      />
                      <div className="absolute top-3 left-3 bg-black/50 backdrop-blur-md text-white text-[10px] px-2 py-1 rounded font-bold">AI Rendered</div>
                    </div>
                  </div>
                ) : result.type === GenerationType.VIDEO && typeof result.content === 'string' ? (
                  <div className="flex flex-col gap-6">
                    <div className="relative rounded-xl overflow-hidden shadow-2xl bg-black border border-slate-100 dark:border-slate-700 aspect-video flex items-center justify-center">
                      <video src={result.content} controls className="w-full h-full" />
                    </div>
                  </div>
                ) : (
                  <div className="prose prose-sm prose-slate dark:prose-invert max-w-none text-slate-600 dark:text-slate-300 leading-relaxed">
                    {/* Render content appropriately if it's text or array */}
                    {typeof result.content === 'string' ? (
                        result.content.split('\n').map((line, i) => <p key={i} className="mb-4">{line}</p>)
                    ) : (
                        <ul className="list-disc pl-5">
                            {result.content.map((item, i) => <li key={i}>{item}</li>)}
                        </ul>
                    )}
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-700/50 flex items-center justify-between text-xs text-slate-400">
                <p>Generated by CommerceAI specialized {result.type.toLowerCase()} engine.</p>
                <div className="flex gap-2">
                  <button className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 hover:border-primary hover:text-primary transition-colors active:scale-95 font-bold" onClick={onReset}>
                    {result.type === GenerationType.TEXT ? 'Shorten' : 'Regenerate'}
                  </button>
                  <button className="px-3 py-1.5 rounded-lg bg-slate-900 dark:bg-slate-700 text-white hover:bg-primary hover:text-slate-900 transition-all active:scale-95 font-bold shadow-md" onClick={() => alert("Asset saved to gallery.")}>Save to Assets</button>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default GeminiResult;
