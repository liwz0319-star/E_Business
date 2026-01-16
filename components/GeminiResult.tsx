
import React from 'react';
import { GenerationType } from '../services/geminiService';

interface GeminiResultProps {
  isGenerating: boolean;
  result: { type: GenerationType; content: string | string[] } | null;
  onReset: () => void;
  onImageClick?: (content: string) => void;
}

const GeminiResult: React.FC<GeminiResultProps> = ({ isGenerating, result, onReset, onImageClick }) => {
  if (isGenerating) {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-6 animate-pulse">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xl font-medium text-slate-600 dark:text-slate-300">CommerceAI is thinking...</p>
      </div>
    );
  }

  if (!result) return null;

  return (
    <div className="w-full max-w-4xl bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-slate-100 dark:border-slate-700 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="material-icons-round text-primary">auto_awesome</span>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">Generated {result.type}</h3>
        </div>
        <button 
          onClick={onReset}
          className="text-sm text-slate-500 hover:text-primary transition-colors flex items-center gap-1"
        >
          <span className="material-icons-round text-base">refresh</span>
          Start Over
        </button>
      </div>

      <div className="overflow-auto max-h-[60vh] sidebar-scroll pr-2">
        {result.type === GenerationType.IMAGE && typeof result.content === 'string' ? (
          <img 
            src={result.content} 
            alt="Generated Asset" 
            className="w-full rounded-xl shadow-lg cursor-pointer hover:opacity-90 transition-opacity" 
            onClick={() => onImageClick?.(result.content as string)}
          />
        ) : result.type === GenerationType.VIDEO && typeof result.content === 'string' ? (
          <video src={result.content} controls className="w-full rounded-xl shadow-lg" />
        ) : (
          <div className="prose dark:prose-invert max-w-none text-left leading-relaxed">
            {typeof result.content === 'string' ? (
                result.content.split('\n').map((line, i) => <p key={i}>{line}</p>)
            ) : (
                <ul className="list-disc pl-5">
                    {result.content.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
            )}
          </div>
        )}
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t border-slate-100 dark:border-slate-700">
         <button className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
            Copy
         </button>
         <button className="px-4 py-2 bg-primary hover:bg-secondary text-white text-sm font-bold rounded-lg shadow-lg shadow-primary/20 transition-all">
            Save to Assets
         </button>
      </div>
    </div>
  );
};

export default GeminiResult;
