
import React, { useState } from 'react';

interface ImageDetailProps {
  image: any;
  onClose: () => void;
}

const ImageDetail: React.FC<ImageDetailProps> = ({ image, onClose }) => {
  const [zoom, setZoom] = useState(100);
  const [isLiked, setIsLiked] = useState(false);

  const handleAction = (label: string) => {
    alert(`Image Action: ${label}`);
  };

  const copyPrompt = () => {
    const promptText = "Studio lighting, minimalist perfume bottle on a white marble podium, soft shadows, 8k resolution, photorealistic, luxury aesthetic, clean composition, beige and cream tones, depth of field.";
    navigator.clipboard.writeText(promptText);
    alert("Prompt copied to clipboard!");
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/10 backdrop-blur-md flex items-center justify-center p-4 md:p-8 font-display transition-colors">
      <div className="bg-white dark:bg-slate-900 w-full max-w-[1280px] h-[90vh] md:h-[85vh] rounded-xl shadow-2xl overflow-hidden flex flex-col lg:flex-row border border-slate-200 dark:border-slate-800 relative ring-1 ring-black/5">
        
        {/* Left: Image Preview Section */}
        <div className="flex-1 lg:w-7/12 xl:w-8/12 bg-[#f8f9fa] dark:bg-slate-950 relative group overflow-hidden flex items-center justify-center p-8 lg:p-12 transition-colors">
          <div className="absolute inset-0 opacity-40 dark:opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#d1d5db 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
          
          <div className="relative z-10 w-full h-full flex items-center justify-center">
             <img 
               alt={image?.title || "AI Generated Preview"} 
               className="max-w-full max-h-full object-contain rounded-sm shadow-xl transition-all duration-500 cursor-zoom-in" 
               style={{ transform: `scale(${zoom / 100})` }}
               src={image?.url || "https://lh3.googleusercontent.com/aida-public/AB6AXuCpSlHIN1IKvTeY0mdkVRYVCoTOjXPDgQOK8XlWMRcSCL3nS1mle71siP_jAKAWG5uypzOWxP1R3yaTWXO4DRPWe5GiazkUobAJlHXuAdMm64W6GQWgShc4QRlpBZJigcRpOt_8MhqSqwiJENt3GWVkFIj73azd8IpcHoscdcr1l4Pv4Q7G85KD2ZMoIGD_bi_FkH8bSSThxFSQ4naIr3ELXD0SS_hv5sGLzam0geA_lYQup95v_tCeNvlZ8ttpCQugs60NQB9vIfs"}
             />
          </div>

          {/* Floating Controls */}
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-white/90 dark:bg-slate-800/90 backdrop-blur border border-slate-200 dark:border-slate-700 rounded-full px-4 py-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-20 shadow-lg text-slate-600 dark:text-slate-300">
            <button 
              onClick={() => setZoom(Math.max(50, zoom - 25))} 
              className="hover:text-primary transition-colors p-1"
            >
              <span className="material-symbols-outlined text-[20px]">remove</span>
            </button>
            <span className="text-xs font-bold w-12 text-center">{zoom}%</span>
            <button 
              onClick={() => setZoom(Math.min(200, zoom + 25))} 
              className="hover:text-primary transition-colors p-1"
            >
              <span className="material-symbols-outlined text-[20px]">add</span>
            </button>
            <div className="w-px h-4 bg-slate-300 dark:bg-slate-600 mx-1"></div>
            <button onClick={() => handleAction('Compare Original')} className="hover:text-primary transition-colors p-1">
              <span className="material-symbols-outlined text-[20px]">compare</span>
            </button>
            <button onClick={() => handleAction('Fullscreen')} className="hover:text-primary transition-colors p-1">
              <span className="material-symbols-outlined text-[20px]">fullscreen</span>
            </button>
          </div>
        </div>

        {/* Right: Info Sidebar */}
        <div className="lg:w-5/12 xl:w-4/12 flex flex-col bg-white dark:bg-slate-900 border-t lg:border-t-0 lg:border-l border-slate-200 dark:border-slate-800 relative transition-colors">
          
          {/* Header */}
          <div className="flex items-start justify-between p-6 pb-2 shrink-0">
            <div className="pr-8">
              <h2 className="text-slate-900 dark:text-white text-2xl font-bold leading-tight tracking-tight">{image?.title || "Perfume Bottle - Variation 04"}</h2>
              <p className="text-slate-500 dark:text-slate-400 text-sm mt-1 flex items-center gap-1">
                Generated 2 mins ago <span className="w-1 h-1 rounded-full bg-slate-300"></span> Public
              </p>
            </div>
            <button 
              onClick={onClose}
              className="text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full p-2 flex items-center justify-center shrink-0"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto sidebar-scroll p-6 pt-2 space-y-8">
            {/* Prompt Section */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-slate-900 dark:text-white text-sm font-black uppercase tracking-wider">Prompt</h3>
                <button 
                  onClick={copyPrompt}
                  className="text-xs text-primary hover:text-teal-500 transition-colors flex items-center gap-1 font-bold"
                >
                  <span className="material-symbols-outlined text-[14px]">content_copy</span> Copy
                </button>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-slate-200 dark:border-slate-800 relative group">
                <p className="text-slate-700 dark:text-slate-300 text-sm font-medium leading-relaxed">
                  Studio lighting, minimalist perfume bottle on a white marble podium, soft shadows, 8k resolution, photorealistic, luxury aesthetic, clean composition, beige and cream tones, depth of field.
                </p>
                <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
                  <span className="text-xs text-slate-400 font-mono">--negative: low quality, blurry, text, watermark</span>
                </div>
              </div>
            </div>

            {/* Generation Details Grid */}
            <div>
              <h3 className="text-slate-900 dark:text-white text-sm font-black uppercase tracking-wider mb-4">Generation Details</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Model Version</span>
                  <div className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1">
                    E-com Diffusion v2.1
                    <span className="material-symbols-outlined text-[14px] text-primary" title="Verified Model">verified</span>
                  </div>
                </div>
                <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Resolution</span>
                  <span className="text-sm font-bold text-slate-900 dark:text-white">2048 x 2048 px</span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Aspect Ratio</span>
                  <span className="text-sm font-bold text-slate-900 dark:text-white">1:1 Square</span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Seed</span>
                  <span className="text-sm font-bold text-slate-900 dark:text-white font-mono">3948210492</span>
                </div>
                <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-200 dark:border-slate-800 col-span-2">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-1">Guidance Scale</span>
                  <div className="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full mt-3 relative overflow-hidden">
                    <div className="bg-primary h-full rounded-full transition-all duration-1000" style={{ width: '70%' }}></div>
                  </div>
                  <span className="text-xs text-slate-400 mt-2 block text-right font-bold">7.0</span>
                </div>
              </div>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="p-6 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0">
            <button 
              onClick={() => handleAction('Download Image')}
              className="w-full bg-primary hover:bg-teal-400 text-slate-900 font-black text-base py-4 px-6 rounded-xl mb-3 flex items-center justify-center gap-2 transition-all shadow-xl shadow-primary/20 transform hover:-translate-y-0.5 active:scale-95"
            >
              <span className="material-symbols-outlined font-bold">download</span>
              Download (HD)
            </button>
            <div className="flex gap-3">
              <button 
                onClick={() => handleAction('Edit in Workspace')}
                className="flex-1 bg-transparent hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-bold text-sm py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all active:scale-95"
              >
                <span className="material-symbols-outlined text-[18px]">edit_square</span>
                Edit
              </button>
              <button 
                onClick={() => handleAction('Share Image')}
                aria-label="Share" 
                className="bg-transparent hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 p-3 rounded-xl flex items-center justify-center transition-all active:scale-95"
              >
                <span className="material-symbols-outlined text-[20px]">share</span>
              </button>
              <button 
                onClick={() => setIsLiked(!isLiked)}
                aria-label="Like" 
                className={`p-3 rounded-xl border flex items-center justify-center transition-all active:scale-95 ${isLiked ? 'bg-pink-50 border-pink-200 text-pink-500 shadow-sm' : 'bg-transparent border-slate-200 dark:border-slate-700 text-slate-400'}`}
              >
                <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: isLiked ? "'FILL' 1" : "" }}>favorite</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageDetail;
